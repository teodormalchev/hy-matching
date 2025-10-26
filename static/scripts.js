document.addEventListener('DOMContentLoaded', function() {
    window.addEventListener('scroll', handleScroll);
    window.addEventListener('scroll', userScroll);
  });
  
  function handleScroll() {
    const boxes = document.querySelectorAll('.box');
    const halfViewportHeight = window.innerHeight / 4;
  
    boxes.forEach(box => {
      const boxTop = box.getBoundingClientRect().top;
  
      // Check if the box is at least halfway visible
      if (boxTop < window.innerHeight - halfViewportHeight) {
        box.style.opacity = 1;
      } else {
        box.style.opacity = 0;
      }
    });
  }
  

  // FOR THE WORDS TO COME INTO SHOW

  function userScroll() {
    const fadeInOnScroll = document.querySelector('.fadeInOnScroll');
    const fadeInOffset = fadeInOnScroll.getBoundingClientRect().top;
    const screenHeight = window.innerHeight;
  
    if (fadeInOffset < screenHeight * 0.2) {
      fadeInOnScroll.classList.add('show');
    }
  }


  // Countdown to the game

  const targetDate = new Date('November 15, 2024 9:0:0').getTime();

// Update the countdown every 1 second
const countdownInterval = setInterval(function() {
    const currentDate = new Date().getTime();
    const timeDifference = targetDate - currentDate;

    // Calculate days, hours, minutes, and seconds
    const days = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeDifference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);

    // Display the countdown
    document.getElementById('countdown').innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;

    // Check if the countdown has reached zero
    if (timeDifference <= 0) {
        clearInterval(countdownInterval); // Stop the countdown when it reaches zero
        document.getElementById('countdown').innerHTML = 'Countdown expired!';
    }
}, 1000);