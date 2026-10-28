<!DOCTYPE html>
<html lang="en">
<head>
  <title><?= e($title) ?> | Chemical Clouds</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css"> 
  <link rel="stylesheet" href="<?= e(asset('style.css')) ?>">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.3.1/dist/leaflet.css" integrity="sha512-Rksm5RenBEKSKFjgI3a41vrjkw4EVPlJ3+OiI65vTjIdo9brlAacEuKOiQ5OFh7cOI1bkDwLqdLw3Zg0cRJAAQ==" crossorigin="" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.3.0/dist/MarkerCluster.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.3.0/dist/MarkerCluster.Default.css" />

  <script src="https://unpkg.com/leaflet@1.3.1/dist/leaflet.js" integrity="sha512-/Nsx9X4HebavoBvEBuyp3I7od5tA0UzAxs+j83KgC8PU0kgB4XiK4Lfe4y4cgBtaRJQEIFCW+oC506aPT2L1zw==" crossorigin=""></script>
  <script src="https://unpkg.com/leaflet.markercluster@1.3.0/dist/leaflet.markercluster.js"></script>
  
  <script src="<?= e(asset('javascript.js')) ?>"></script>

</head>

<body>

<!--Nav bar-->
<header class="header">
<div class="header__content">
  <a href="<?= e(page_url('home')) ?>" class="logo">Chemical Clouds</a>
  <nav class="nav" id="site-nav">
    <ul class="nav__list">
      <li class="nav__item">
        <a href="<?= e(page_url('map')) ?>" class="nav__link <?= $page === 'map' ? 'active' : '' ?>">Tour Dates</a>
        </li>
      <li class="nav__item">
        <a href="<?= e(page_url('music')) ?>" class="nav__link <?= $page === 'music' ? 'active' : '' ?>">Music</a>
        </li>
      <li class="nav__item">
        <a href="<?= e(page_url('about')) ?>" class="nav__link <?= $page === 'about' ? 'active' : '' ?>">About</a>
        </li>
      <li class="nav__item">
        <a href="<?= e(page_url('mail')) ?>" class="nav__link <?= $page === 'mail' ? 'active' : '' ?>">Contact</a>
        </li>
      <li class="nav_item2">
        <a href="https://mailchi.mp/bec19833a031/chemical-community" class="nav__link2"> <ion-icon name="person-circle-outline" class="member-icon"></ion-icon> Become Chemical</a>
      </li>
      <!-- <li class="nav_item2">
        <a href="#"class="nav__link2">Shop</a>
      </li>  -->
    </ul>
  </nav>
  <button type="button" class="hamburger" aria-label="Toggle navigation" aria-expanded="false" aria-controls="site-nav">
    <span class="bar"></span>
    <span class="bar"></span>
    <span class="bar"></span>
  </button>
</div>
</header>
<main>
<?php require __DIR__ . '/' . $view . '.php'; ?>
</main>
<script type="module" src="https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.esm.js"></script>
<script nomodule src="https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.js"></script>
</body>
</html>
