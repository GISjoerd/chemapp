<article class="show-detail">
<?php if ($show === null): ?>
  <h1>Show information</h1>
  <p>Select a show from the <a href="<?= e(page_url('map')) ?>">tour dates</a> to see its details.</p>
<?php else: ?>
  <h1><?= e($show['name']) ?></h1>
  <p><time datetime="<?= e($show['date']) ?>"><?= e(date('d-m-Y', strtotime($show['date']))) ?></time></p>
  <?php if (http_url($show['link_img']) !== ''): ?>
    <img src="<?= e(http_url($show['link_img'])) ?>" alt="<?= e($show['name']) ?>" loading="lazy">
  <?php endif; ?>
  <?php if (http_url($show['link_ticket']) !== ''): ?>
    <p><a class="btn btn-primary" href="<?= e(http_url($show['link_ticket'])) ?>" target="_blank" rel="noopener noreferrer">Buy tickets</a></p>
  <?php endif; ?>
  <p><a href="<?= e(page_url('map')) ?>">Back to tour dates</a></p>
<?php endif; ?>
</article>
