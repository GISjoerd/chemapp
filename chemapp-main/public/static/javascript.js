'use strict';
document.addEventListener('DOMContentLoaded', () => {
    const nav = document.querySelector('.nav');
    const hamburger = document.querySelector('.hamburger');
    if (!nav || !hamburger) return;
    hamburger.addEventListener('click', () => {
        const open = nav.classList.toggle('nav--open');
        hamburger.classList.toggle('hamburger--open', open);
        hamburger.setAttribute('aria-expanded', String(open));
        const height = open ? nav.offsetHeight + 'px' : '0';
        document.querySelectorAll('.carousel-inner img, .list_box, .map_box').forEach(el => {
            el.style.marginTop = height;
        });
        if (window.chemappMap) window.chemappMap.invalidateSize();
    });
});
