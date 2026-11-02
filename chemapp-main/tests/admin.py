"""Exercise admin sessions and real MySQL writes in an isolated application copy."""
import contextlib
import http.cookiejar
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor, HTTPRedirectHandler, Request

APP = Path(__file__).resolve().parents[1]
PHP = os.environ.get('PHP_BINARY', 'php')
if os.environ.get('CHEMAPP_TEST_DATABASE') != '1':
    raise SystemExit('Set CHEMAPP_TEST_DATABASE=1 only for a disposable test database.')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def browser(simulated_https=False):
    # The HTTPS fixture below simulates trusted TLS termination at the web server.
    # Permit Secure cookies over its loopback HTTP transport only in that fixture.
    policy = http.cookiejar.DefaultCookiePolicy(secure_protocols=('https', 'http') if simulated_https else ('https', 'wss'))
    jar = http.cookiejar.CookieJar(policy)
    return build_opener(HTTPCookieProcessor(jar), NoRedirect()), jar


def request(client, base, path='/index.php?page=manage', fields=None, expected=200, headers=None, method=None):
    data = urlencode(fields, doseq=True).encode() if fields is not None else None
    req = Request(base + path, data=data, headers=headers or {}, method=method)
    try:
        response = client.open(req, timeout=10)
    except HTTPError as error:
        response = error
    with response:
        text = response.read().decode()
        assert response.status == expected, (response.status, expected, text)
        if 'page=manage' in path:
            assert response.headers['Cache-Control'] == 'no-store'
            assert response.headers['X-Frame-Options'] == 'DENY'
        return text, response.headers


def csrf(html):
    return re.search(r'name="csrf" value="([a-f0-9]+)"', html).group(1)


@contextlib.contextmanager
def server(app, env, subfolder=False, trusted_https=False):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    if subfolder:
        root = app / 'webroot'
        root.mkdir(exist_ok=True)
        (root / 'band').symlink_to(app / 'public', target_is_directory=True)
        cmd = [PHP, '-S', f'127.0.0.1:{port}', '-t', str(root)]
    else:
        cmd = [PHP, '-S', f'127.0.0.1:{port}', '-t', str(app / 'public'), str(app / 'public/router.php')]
    if trusted_https:
        router = app / 'trusted-https-router.php'
        router.write_text("<?php $_SERVER['HTTPS'] = 'on'; $_SERVER['SCRIPT_NAME'] = '/index.php'; require __DIR__ . '/public/index.php';")
        cmd[-1] = str(router)
    sessions = app / 'sessions'
    sessions.mkdir(exist_ok=True)
    cmd[1:1] = ['-d', 'session.save_path=' + str(sessions)]
    base = f'http://127.0.0.1:{port}'
    with tempfile.TemporaryFile() as log:
        proc = subprocess.Popen(cmd, cwd=app, env=env, stdout=log, stderr=log)
        try:
            for _ in range(100):
                try:
                    with socket.create_connection(('127.0.0.1', port), .1):
                        break
                except OSError:
                    if proc.poll() is not None:
                        log.seek(0)
                        raise AssertionError(log.read().decode())
                    time.sleep(.05)
            yield base + ('/band' if subfolder else '')
        finally:
            proc.terminate()
            proc.wait(timeout=5)


with tempfile.TemporaryDirectory() as directory:
    app = Path(directory) / 'app'
    shutil.copytree(APP, app, ignore=shutil.ignore_patterns('storage', 'static', 'config.php', '__pycache__'))
    (app / 'public/static').symlink_to(APP / 'public/static', target_is_directory=True)
    env = dict(os.environ, CHEMAPP_CONFIG=str(app / 'absent-config.php'), CHEMAPP_BASE_PATH='')
    password = 'disposable-admin-passphrase'
    client, cookies = browser()
    guest, _ = browser()
    with server(app, env) as base:
        html, _ = request(client, base, headers={'Host': 'public.example', 'X-Forwarded-For': '127.0.0.1'})
        assert 'Admin setup required' in html and 'name="password"' not in html, html
        html, _ = request(client, base)
        assert 'Choose your admin password' in html
        token = csrf(html)
        request(client, base, fields={'action': 'setup', 'password': password, 'password_confirm': password}, expected=403)
        request(client, base, fields={'csrf': token, 'action': 'setup', 'password': 'short', 'password_confirm': 'short'}, expected=400)
        _, headers = request(client, base, fields={'csrf': token, 'action': 'setup', 'password': password, 'password_confirm': password}, expected=303)
        assert headers['Location'] == '/index.php?page=manage'
        state = json.loads((app / 'storage/admin.json').read_text())
        assert password not in json.dumps(state) and state['password_hash'].startswith('$2y$')
        html, headers = request(client, base)
        assert 'Add a show' in html and 'Choose your admin password' not in html
        assert all(cookie.has_nonstandard_attr('HttpOnly') and cookie.get_nonstandard_attr('SameSite') == 'Strict' for cookie in cookies)
        token = csrf(html)
        original = json.loads(request(client, base, '/index.php?page=api%2Fshows')[0])
        guest_html, _ = request(guest, base)
        guest_token = csrf(guest_html)
        show = {'action': 'save', 'csrf': token, 'id': '', 'name': 'Admin test 🎸 <script>alert(1)</script>', 'date': '2028-05-17', 'latitude': '52.02', 'longitude': '6.42', 'link_ticket': 'https://example.com/tickets?x=1&y=2', 'link_img': ''}
        request(guest, base, fields=show | {'csrf': guest_token}, expected=403)
        request(client, base, fields=show | {'csrf': 'wrong'}, expected=403)
        html, _ = request(client, base, fields=show | {'date': '2027-02-29'}, expected=400)
        assert 'Admin test 🎸 &lt;script&gt;' in html
        request(client, base, fields=show | {'latitude': '91'}, expected=400)
        request(client, base, fields=show | {'link_ticket': 'javascript:alert(1)'}, expected=400)
        request(client, base, fields=show | {'id': '999999999999'}, expected=400)
        request(client, base, fields=show | {'id[]': '1'}, expected=400)
        assert json.loads(request(client, base, '/index.php?page=api%2Fshows')[0]) == original
        _, headers = request(client, base, fields=show, expected=303)
        edit_path = headers['Location']
        show_id = int(re.search(r'id=(\d+)', edit_path).group(1))
        html, _ = request(client, base, edit_path)
        assert 'Show added.' in html and '&lt;script&gt;' in html and '<script>alert(1)</script>' not in html
        public = json.loads(request(client, base, '/index.php?page=api%2Fshows')[0])
        created = next(row for row in public if row['id'] == show_id)
        assert created['geometry']['coordinates'] == [6.42, 52.02]
        updated = show | {'id': str(show_id), 'name': 'Changed tour date', 'date': '2029-06-18', 'latitude': '', 'longitude': ''}
        request(client, base, fields=updated, expected=303)
        # Saving an unchanged row is successful too (MySQL may report zero affected rows).
        request(client, base, fields=updated, expected=303)
        public = json.loads(request(client, base, '/index.php?page=api%2Fshows')[0])
        row = next(row for row in public if row['id'] == show_id)
        assert row['name'] == 'Changed tour date' and row['date'] == '2029-06-18' and row['geometry'] is None
        assert len(public) == len(original) + 1
        assert [r for r in public if r['id'] != show_id] == original
        request(client, base, fields=updated | {'id': '4294967295'}, expected=404)
        request(client, base, '/index.php?page=manage&id[]=1', expected=404)
        deletion = {'action': 'delete', 'csrf': token, 'id': str(show_id), 'confirm_delete': str(show_id)}
        request(guest, base, fields=deletion | {'csrf': guest_token}, expected=403)
        request(client, base, fields=deletion | {'csrf': 'wrong'}, expected=403)
        request(client, base, fields=deletion | {'confirm_delete': ''}, expected=400)
        request(client, base, fields=deletion | {'confirm_delete': str(show_id + 1)}, expected=400)
        for invalid_id in ['', '0', '-1', '1 OR 1=1', '999999999999']:
            request(client, base, fields=deletion | {'id': invalid_id}, expected=400)
        request(client, base, fields=deletion | {'id[]': '1'}, expected=400)
        before_delete = json.loads(request(client, base, '/index.php?page=api%2Fshows')[0])
        assert before_delete == public
        # Opening a confirmation page, a forged GET action, or Cancel never deletes data.
        confirm_path = edit_path + '&delete=1'
        html, _ = request(client, base, confirm_path)
        assert 'Delete this show?' in html and 'Changed tour date' in html and '2029-06-18' in html
        assert 'name="confirm_delete"' in html and 'Cancel' in html
        request(client, base, edit_path + '&action=delete&confirm_delete=' + str(show_id))
        html, _ = request(client, base, edit_path)
        assert 'Delete show…' in html
        assert json.loads(request(client, base, '/index.php?page=api%2Fshows')[0]) == public
        _, headers = request(client, base, fields=deletion, expected=303)
        assert headers['Location'] == '/index.php?page=manage'
        html, _ = request(client, base)
        assert 'Show deleted.' in html
        assert json.loads(request(client, base, '/index.php?page=api%2Fshows')[0]) == original
        request(client, base, '/index.php?page=info&id=' + str(show_id), expected=404)
        request(client, base, fields=deletion, expected=404)
        request(client, base, fields={'csrf': token, 'action': 'logout'}, expected=303)
        html, _ = request(client, base)
        assert 'name="password"' in html and 'show-form' not in html
        token = csrf(html)
        request(client, base, fields={'csrf': token, 'action': 'login', 'password': 'wrong-password'}, expected=401)
        request(client, base, fields={'csrf': token, 'action': 'login', 'password': password}, expected=303)
        html, _ = request(client, base)
        assert 'show-form' in html
        # A password reset must revoke existing authenticated sessions.
        result = subprocess.run([PHP, 'bin/set-admin-password.php'], input='replacement-admin-passphrase\nreplacement-admin-passphrase\n', text=True, capture_output=True, cwd=app, env=env)
        assert result.returncode == 0, result.stderr
        html, _ = request(client, base)
        assert 'name="password"' in html and 'show-form' not in html
        token = csrf(html)
        for _ in range(10):
            request(client, base, fields={'csrf': token, 'action': 'login', 'password': 'wrong-password'}, expected=401)
        request(client, base, fields={'csrf': token, 'action': 'login', 'password': 'replacement-admin-passphrase'}, expected=429)
        request(client, base, method='DELETE', expected=405)

    # Reset the isolated admin password and verify cookie/redirect paths in a subfolder.
    subprocess.run([PHP, 'bin/set-admin-password.php'], input=password + '\n' + password + '\n', text=True, capture_output=True, cwd=app, env=env, check=True)
    with server(app, dict(env, CHEMAPP_BASE_PATH='/band'), subfolder=True) as base:
        client, cookies = browser()
        html, _ = request(client, base)
        _, headers = request(client, base, fields={'csrf': csrf(html), 'action': 'login', 'password': password}, expected=303)
        assert headers['Location'] == '/band/index.php?page=manage'
        html, _ = request(client, base)
        assert '/band/static/admin-map.js' in html and '/band/index.php?page=manage' in html
        assert all(cookie.path == '/band/' for cookie in cookies)
    no_db = {key: value for key, value in env.items() if not key.startswith('CHEMAPP_DB_')}
    with server(app, no_db) as base:
        client, _ = browser()
        html, _ = request(client, base)
        request(client, base, fields={'csrf': csrf(html), 'action': 'login', 'password': password}, expected=303)
        html, _ = request(client, base, expected=503)
        assert 'show manager is unavailable' in html and 'PDOException' not in html

# Public first-time setup using the actual Plesk private-directory layout.
with tempfile.TemporaryDirectory() as directory:
    app = Path(directory) / 'app'
    shutil.copytree(APP, app, ignore=shutil.ignore_patterns('storage', 'static', 'config.php', '__pycache__'))
    (app / 'public/static').symlink_to(APP / 'public/static', target_is_directory=True)
    private = app / 'chemapp-private'
    private.mkdir()
    for name in ['src', 'views', 'bin']:
        shutil.move(str(app / name), private / name)
    index = app / 'public/index.php'
    index.write_text(index.read_text().replace('$appRoot = dirname(__DIR__);', "$appRoot = dirname(__DIR__) . '/chemapp-private';"))
    config = private / 'config.php'
    env = dict(os.environ, CHEMAPP_CONFIG=str(config), CHEMAPP_BASE_PATH='')
    env.pop('CHEMAPP_ADMIN_SETUP_KEY', None)
    setup_key = 'disposable-private-setup-key-' + 'a' * 36
    password = 'online-disposable-admin-password'
    public_headers = {'Host': 'public.example', 'X-Forwarded-Proto': 'https', 'X-Forwarded-For': '127.0.0.1'}
    config.write_text("<?php return ['admin_setup_key' => '" + setup_key + "'];")
    with server(app, env) as base:
        client, _ = browser()
        html, _ = request(client, base, headers=public_headers)
        assert 'Admin setup required' in html and 'name="setup_key"' not in html
        local_html, _ = request(client, base)
        request(client, base, fields={'csrf': csrf(local_html), 'action': 'setup', 'setup_key': setup_key, 'password': password, 'password_confirm': password}, headers=public_headers, expected=403)
    with server(app, env, trusted_https=True) as base:
        client, cookies = browser(simulated_https=True)
        guest, _ = browser(simulated_https=True)
        for key in ['', 'too-short', 'bad key with spaces' + 'x' * 32, 'x' * 129]:
            config.write_text("<?php return ['admin_setup_key' => '" + key + "'];")
            html, _ = request(client, base, headers=public_headers)
            assert 'Admin setup required' in html and 'name="password"' not in html
        config.write_text("<?php return ['admin_setup_key' => '" + setup_key + "'];")
        html, _ = request(client, base, headers=public_headers)
        assert 'Choose your admin password' in html and 'name="setup_key"' in html
        assert setup_key not in html
        token = csrf(html)
        setup = {'csrf': token, 'action': 'setup', 'setup_key': setup_key, 'password': password, 'password_confirm': password}
        request(client, base, fields=setup | {'csrf': 'wrong'}, headers=public_headers, expected=403)
        request(client, base, fields=setup | {'password_confirm': 'mismatch'}, headers=public_headers, expected=400)
        request(client, base, fields=setup | {'password': 'short', 'password_confirm': 'short'}, headers=public_headers, expected=400)
        for key in [None, '', 'incorrect', ['bad']]:
            fields = setup | {'setup_key': key}
            if key is None:
                fields.pop('setup_key')
            elif isinstance(key, list):
                fields.pop('setup_key')
                fields['setup_key[]'] = key
            html, _ = request(client, base, fields=fields, headers=public_headers, expected=403)
            assert setup_key not in html and password not in html
        # Brute-force protection persists across requests and rejects even the right key at the limit.
        for _ in range(6):
            request(client, base, fields=setup | {'setup_key': 'wrong'}, headers=public_headers, expected=403)
        request(client, base, fields=setup, headers=public_headers, expected=429)
        state_path = private / 'storage/admin.json'
        state = json.loads(state_path.read_text())
        assert state.get('password_hash', '') == '' and state['failures'] == 10
        state['window_start'] = 0  # Expire the fixture's five-minute lockout without sleeping.
        state_path.write_text(json.dumps(state))
        _, headers = request(client, base, fields=setup, headers=public_headers, expected=303)
        assert headers['Location'] == '/index.php?page=manage'
        state = json.loads(state_path.read_text())
        assert password not in json.dumps(state) and setup_key not in json.dumps(state)
        assert state['password_hash'].startswith('$2y$')
        assert all(cookie.secure for cookie in cookies)
        html, _ = request(client, base, headers=public_headers)
        assert 'show-form' in html and 'name="setup_key"' not in html
        assert 'Admin login created.' in html and 'Remove admin_setup_key' in html
        token = csrf(html)
        # The key cannot repeat setup or reset an existing password, even before removal.
        guest_html, _ = request(guest, base, headers=public_headers)
        assert 'Log in' in guest_html and 'name="setup_key"' not in guest_html
        request(guest, base, fields=setup | {'csrf': csrf(guest_html)}, headers=public_headers, expected=403)
        original = json.loads(request(client, base, '/index.php?page=api%2Fshows', headers=public_headers)[0])
        show = {'action': 'save', 'csrf': token, 'id': '', 'name': 'Online setup show', 'date': '2030-05-17', 'latitude': '0', 'longitude': '0'}
        request(guest, base, fields=show | {'csrf': csrf(guest_html)}, headers=public_headers, expected=403)
        _, headers = request(client, base, fields=show, headers=public_headers, expected=303)
        show_id = int(re.search(r'id=(\d+)', headers['Location']).group(1))
        request(client, base, fields=show | {'id': str(show_id), 'name': 'Online edited show'}, headers=public_headers, expected=303)
        request(client, base, fields={'csrf': token, 'action': 'delete', 'id': str(show_id), 'confirm_delete': str(show_id)}, headers=public_headers, expected=303)
        assert json.loads(request(client, base, '/index.php?page=api%2Fshows', headers=public_headers)[0]) == original
        config.write_text("<?php return ['admin_setup_key' => ''];")
        request(client, base, fields={'csrf': token, 'action': 'logout'}, headers=public_headers, expected=303)
        html, _ = request(client, base, headers=public_headers)
        request(client, base, fields={'csrf': csrf(html), 'action': 'login', 'password': password}, headers=public_headers, expected=303)
        assert 'show-form' in request(client, base, headers=public_headers)[0]

print('Admin local/online setup, HTTPS and private-key gates, setup throttling, one-time setup, login, logout, CSRF, authorization, MySQL add/edit/delete, password reset and subfolder tests passed.')
