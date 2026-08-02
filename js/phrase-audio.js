/**
 * Play Korean phrase audio from audio/korean/{id}.mp3
 */
(function () {
  var current = null;

  function audioBase() {
    var scripts = document.getElementsByTagName("script");
    for (var i = scripts.length - 1; i >= 0; i--) {
      var src = scripts[i].src || "";
      if (src.indexOf("phrase-audio.js") !== -1) {
        return src.replace(/\/js\/[^/]*$/, "/audio/korean/");
      }
    }
    return "../../audio/korean/";
  }

  function play(id, btn) {
    if (current) {
      current.pause();
      current = null;
      document.querySelectorAll(".phrase-audio-btn.is-playing").forEach(function (b) {
        b.classList.remove("is-playing");
        b.textContent = "▶";
      });
    }

    var audio = new Audio(audioBase() + id + ".mp3");
    current = audio;
    btn.classList.add("is-playing");
    btn.textContent = "■";

    audio.addEventListener("ended", function () {
      btn.classList.remove("is-playing");
      btn.textContent = "▶";
      if (current === audio) current = null;
    });
    audio.addEventListener("error", function () {
      btn.classList.remove("is-playing");
      btn.textContent = "▶";
      if (current === audio) current = null;
    });
    audio.play().catch(function () {
      btn.classList.remove("is-playing");
      btn.textContent = "▶";
    });
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-phrase-audio]");
    if (!btn) return;
    var id = btn.getAttribute("data-phrase-audio");
    if (!id) return;
    if (btn.classList.contains("is-playing") && current) {
      current.pause();
      current = null;
      btn.classList.remove("is-playing");
      btn.textContent = "▶";
      return;
    }
    play(id, btn);
  });
})();
