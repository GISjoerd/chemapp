document.addEventListener("DOMContentLoaded", function() {
  const navE1 = document.querySelector(".nav");
  const hamburgerE1 = document.querySelector('.hamburger');
  const imageE1 = document.querySelector('.carousel-inner img');
  const listBoxE1 = document.querySelector('.list_box');
  const mapBoxE1 = document.querySelector('.map_box');

  hamburgerE1.addEventListener("click", () => {
      navE1.classList.toggle("nav--open");
      hamburgerE1.classList.toggle("hamburger--open");
      
      // Dynamically calculate navbar height
      const navHeight = navE1.offsetHeight;
      
      // Check if the image element exists before manipulating it
      if (imageE1) {
          // Toggle a class to adjust elements' position
          if (navE1.classList.contains("nav--open")) {
              imageE1.style.marginTop = navHeight + 'px';
          } else {
              imageE1.style.marginTop = '0';
          }
      }
      
      // Toggle a class to adjust elements' position
      if (navE1.classList.contains("nav--open")) {
          listBoxE1.style.marginTop = navHeight + 'px';
          mapBoxE1.style.marginTop = navHeight + 'px';
      } else {
          listBoxE1.style.marginTop = '0';
          mapBoxE1.style.marginTop = '0';
      }
  });
});


document.addEventListener("DOMContentLoaded", function() {
    const showItems = document.querySelectorAll('.show-item');
    const today = new Date();

    showItems.forEach(item => {
        const dateString = item.getAttribute('data-date');
        const dateParts = dateString.split('-');
        const year = dateParts[0];
        const month = dateParts[1].padStart(2, '0'); // Ensure two digits for month
        const day = dateParts[2].padStart(2, '0'); // Ensure two digits for day

        const formattedDate = `${day}-${month}-${year}`;
        item.querySelector('.date-display').textContent = `${formattedDate}`;

        const itemDate = new Date(year, month - 1, day); // JavaScript months are 0-based
        if (itemDate < today) {
            item.querySelector('.date-display').classList.add('due-date');
        }
    });
});


document.addEventListener("DOMContentLoaded", function() {
    const image = document.getElementById('carousel-image');

    function updateImageSource() {
        if (window.innerWidth <= 767) {
            image.src = imageUrls.small;
        } else {
            image.src = imageUrls.large;
        }
    }

    // Initial check
    updateImageSource();

    // Update image source on window resize
    window.addEventListener('resize', updateImageSource);
});









