/* Mark hub category cards as entered so hover transforms are free. */
(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    document.querySelectorAll(".food-life-card, .prep-card").forEach(function (card) {
      card.classList.add("is-entered");
    });
    return;
  }

  document.querySelectorAll(".food-life-card, .prep-card").forEach(function (card) {
    var done = false;
    function finish() {
      if (done) return;
      done = true;
      card.classList.add("is-entered");
    }
    card.addEventListener("animationend", function (event) {
      if (event.target === card) finish();
    });
    window.setTimeout(finish, 1400);
  });
})();
