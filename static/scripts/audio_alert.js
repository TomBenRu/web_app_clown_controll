function playAudio() {
    let audio = document.querySelector('audio');
    audio.play();
  }
  
  document.addEventListener('htmx:load', (event) => {
  
    // Prüfen ob geladenes Element die ID "alerts" hat
    if (event.target.id === "alert") {
      playAudio();
    }
  
  });