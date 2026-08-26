/**
 * Food-life hub: short “스무고개” style recommendation quiz.
 * Questions score tags/kinds; winners come from window.FOOD_RECOMMEND_CATALOG
 * (built by tool/build-food-recommend-catalog.py).
 */
(function () {
  var ROOT_SEL = "[data-food-quiz]";
  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /**
   * Question bank. `when` filters by prior answers.
   * Option `tags` / `kinds` accumulate weights for catalog matching.
   */
  var QUESTIONS = [
    {
      id: "craving",
      options: [
        {
          id: "meal",
          kinds: { meal: 6 },
          tags: { hearty: 1 },
          image: "Images/places/food-baekban.jpg",
        },
        {
          id: "dessert",
          kinds: { dessert: 6 },
          tags: { sweet: 1 },
          image: "pages/foods/desserts/cafe/media/cover.jpg",
        },
        {
          id: "quick",
          kinds: { quick: 5 },
          tags: { quickbite: 2, portable: 1, combo: 1 },
          image: "pages/foods/meals/kimbap/media/cover.jpg",
        },
      ],
    },
    {
      id: "spicy",
      when: function (a) {
        return a.craving === "meal" || a.craving === "quick";
      },
      options: [
        { id: "love", tags: { spicy: 4 }, image: "Images/places/food-budae.jpg" },
        { id: "mild", tags: { mild: 3, spicy: 1 }, image: "pages/foods/meals/kalguksu/media/cover.jpg" },
        { id: "no", tags: { mild: 3, nonspicy: 2 }, image: "pages/foods/meals/kimbap/media/cover.jpg" },
      ],
    },
    {
      id: "dessertVibe",
      when: function (a) {
        return a.craving === "dessert";
      },
      options: [
        {
          id: "icy",
          tags: { icy: 5, cold: 2 },
          image: "pages/foods/desserts/bingsu/media/cover.jpg",
        },
        {
          id: "bakery",
          tags: { bakery: 5 },
          image: "pages/foods/desserts/bread/media/cover.jpg",
        },
        {
          id: "coffee",
          tags: { coffee: 5 },
          image: "pages/foods/desserts/cafe/media/cover.jpg",
        },
      ],
    },
    {
      id: "soup",
      when: function (a) {
        return a.craving === "meal";
      },
      options: [
        { id: "yes", tags: { soup: 4, warm: 1 }, image: "pages/foods/meals/gukbap/media/cover.jpg" },
        { id: "no", tags: { nosoup: 3, grill: 1 }, image: "Images/places/food-samgyeopsal.jpg" },
      ],
    },
    {
      id: "protein",
      when: function (a) {
        return a.craving === "meal";
      },
      options: [
        {
          id: "meat",
          tags: { meat: 4, pork: 1, grill: 1 },
          image: "Images/places/food-samgyeopsal.jpg",
        },
        { id: "chicken", tags: { chicken: 4 }, image: "pages/foods/meals/yangnyeom-chicken/media/cover.jpg" },
        {
          id: "light",
          tags: { light: 3, veggie: 2 },
          image: "pages/foods/meals/bibimbap/media/cover.jpg",
        },
      ],
    },
    {
      id: "mood",
      when: function (a) {
        return a.craving === "meal" || a.craving === "dessert";
      },
      options: [
        {
          id: "hot",
          tags: { cold: 4, icy: 1 },
          image: "pages/foods/meals/naengmyeon/media/cover.jpg",
        },
        { id: "cold", tags: { warm: 4, soup: 1 }, image: "pages/foods/meals/gukbap/media/cover.jpg" },
        { id: "rain", tags: { soup: 2, warm: 2, spicy: 1 }, image: "Images/places/food-budae.jpg" },
        { id: "any", tags: { balanced: 1 }, image: "Images/places/food-baekban.jpg" },
      ],
    },
    {
      id: "quickStyle",
      when: function (a) {
        return a.craving === "quick";
      },
      options: [
        {
          id: "combo",
          tags: { combo: 5 },
          kinds: { quick: 2 },
          image: "pages/convenience-store/kim-hyeja-dosirak/media/cover.jpg",
        },
        {
          id: "noodles",
          tags: { noodles: 5, quickbite: 1 },
          image: "pages/convenience-store/buldak-bokkeum-myeon/media/cover.jpg",
        },
        { id: "roll", tags: { roll: 5, portable: 2 }, image: "pages/foods/meals/kimbap/media/cover.jpg" },
      ],
    },
  ];

  var root = null;
  var dialog = null;
  var answers = {};
  var historyStack = [];
  var activeQuestionIds = [];
  var stepIndex = 0;
  var tagScores = {};
  var kindScores = {};
  var lastFocus = null;
  var pendingChoice = null;

  function catalog() {
    var list = window.FOOD_RECOMMEND_CATALOG;
    return Array.isArray(list) ? list : [];
  }

  function t(key, fallback) {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.t === "function") {
        return window.GuideI18n.t(key, fallback || key);
      }
      if (window.GuideI18n && typeof window.GuideI18n.lookupWithFallback === "function") {
        var via = window.GuideI18n.lookupWithFallback(
          key,
          window.GuideI18n.getLang && window.GuideI18n.getLang()
        );
        if (via != null && via !== "") return String(via);
      }
    } catch (e) {
      /* ignore */
    }
    return fallback || key;
  }

  function questionById(id) {
    for (var i = 0; i < QUESTIONS.length; i++) {
      if (QUESTIONS[i].id === id) return QUESTIONS[i];
    }
    return null;
  }

  function visibleQuestions(ans) {
    return QUESTIONS.filter(function (q) {
      return !q.when || q.when(ans);
    });
  }

  function estimateTotal(ans) {
    if (ans && ans.craving) return visibleQuestions(ans).length;
    return 5;
  }

  function resetScores() {
    tagScores = {};
    kindScores = {};
  }

  function applyScores(option) {
    if (!option) return;
    if (option.tags) {
      Object.keys(option.tags).forEach(function (tag) {
        tagScores[tag] = (tagScores[tag] || 0) + option.tags[tag];
      });
    }
    if (option.kinds) {
      Object.keys(option.kinds).forEach(function (kind) {
        kindScores[kind] = (kindScores[kind] || 0) + option.kinds[kind];
      });
    }
  }

  function scoreItem(item) {
    var s = kindScores[item.kind] || 0;
    var tags = item.tags || [];
    for (var i = 0; i < tags.length; i++) {
      s += tagScores[tags[i]] || 0;
    }
    return s;
  }

  function pickWinner() {
    var items = catalog();
    if (!items.length) {
      return {
        id: "kimbap",
        href: "../foods/meals/kimbap/index.html",
        kind: "meal",
        tags: [],
        titleKey: "dishes.kimbap.title",
      };
    }

    var best = -1;
    var tops = [];
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      var s = scoreItem(item);
      if (s > best) {
        best = s;
        tops = [item];
      } else if (s === best) {
        tops.push(item);
      }
    }

    /* Prefer convenience hub on quick+combo when tied-ish with products */
    if (answers.craving === "quick" && answers.quickStyle === "combo") {
      var hub = null;
      var hubScore = -1;
      for (var h = 0; h < items.length; h++) {
        if (items[h].id === "convenience") {
          hub = items[h];
          hubScore = scoreItem(hub);
          break;
        }
      }
      if (hub && hubScore >= best - 1) return hub;
    }

    if (tops.length === 1) return tops[0];
    return tops[Math.floor(Math.random() * tops.length)];
  }

  function resultName(item) {
    if (item.titleKey) {
      var fromTitle = t(item.titleKey, "");
      if (fromTitle && fromTitle !== item.titleKey) return fromTitle;
    }
    var quizName = t("foodLife.quiz.results." + item.id + ".name", "");
    if (quizName && quizName !== "foodLife.quiz.results." + item.id + ".name") {
      return quizName;
    }
    var dishTitle = t("dishes." + item.id + ".title", "");
    if (dishTitle && dishTitle !== "dishes." + item.id + ".title") {
      return dishTitle;
    }
    return item.id;
  }

  function resultReason(item) {
    if (item.reasonKey) {
      var keyed = t(item.reasonKey, "");
      if (keyed && keyed !== item.reasonKey) return keyed;
    }
    var quizReason = t("foodLife.quiz.results." + item.id + ".reason", "");
    if (
      quizReason &&
      quizReason !== "foodLife.quiz.results." + item.id + ".reason"
    ) {
      return quizReason;
    }
    var desc = t("dishes." + item.id + ".desc", "");
    if (desc && desc !== "dishes." + item.id + ".desc") return desc;
    return t(
      "foodLife.quiz.defaultReason",
      "취향에 잘 맞는 메뉴예요. 자세히 보기로 확인해 보세요."
    );
  }

  function setOpen(open) {
    if (!dialog || !root) return;
    dialog.hidden = !open;
    root.classList.toggle("is-quiz-open", open);
    document.body.classList.toggle("food-quiz-lock", open);
    if (open) {
      lastFocus = document.activeElement;
      var closeBtn = dialog.querySelector("[data-food-quiz-close]");
      if (closeBtn) closeBtn.focus();
    } else if (lastFocus && lastFocus.focus) {
      lastFocus.focus();
    }
  }

  function renderProgress(current, total) {
    var el = dialog.querySelector("[data-food-quiz-progress]");
    if (!el) return;
    var tmpl = t("foodLife.quiz.progress", "{current} / {total}");
    el.textContent = tmpl
      .replace("{current}", String(current))
      .replace("{total}", String(total));
    el.setAttribute("aria-valuenow", String(current));
    el.setAttribute("aria-valuemax", String(total));
    var bar = dialog.querySelector("[data-food-quiz-bar]");
    if (bar) {
      var pct = total > 0 ? Math.round((current / total) * 100) : 0;
      bar.style.width = pct + "%";
    }
  }

  function optionThumbSrc(opt) {
    if (opt && opt.image) {
      return "../../" + String(opt.image).replace(/^\.\//, "");
    }
    return "../../Images/menu/foods.png";
  }

  function optionThumbFallback() {
    return "../../Images/menu/foods.png";
  }

  function setPendingChoice(optionId) {
    pendingChoice = optionId;
    if (!dialog) return;
    dialog.querySelectorAll("[data-food-quiz-option]").forEach(function (btn) {
      var on = btn.getAttribute("data-food-quiz-option") === optionId;
      btn.classList.toggle("is-selected", on);
      btn.setAttribute("aria-checked", on ? "true" : "false");
    });
    var nextBtn = dialog.querySelector("[data-food-quiz-next]");
    if (nextBtn) nextBtn.disabled = !optionId;
  }

  function renderQuestion() {
    var panel = dialog.querySelector("[data-food-quiz-panel]");
    if (!panel) return;

    var qid = activeQuestionIds[stepIndex];
    var q = questionById(qid);
    if (!q) {
      renderResult();
      return;
    }

    var total = Math.max(activeQuestionIds.length, estimateTotal(answers));
    renderProgress(stepIndex + 1, total);

    var backBtn = dialog.querySelector("[data-food-quiz-back]");
    if (backBtn) {
      backBtn.hidden = historyStack.length === 0;
    }

    var title = dialog.querySelector("[data-food-quiz-heading]");
    if (title) title.textContent = t("foodLife.quiz.title", "먹거리 추천");

    var prompt = t("foodLife.quiz.questions." + q.id + ".prompt", q.id);
    var lead = t("foodLife.quiz.questions." + q.id + ".lead", "");
    if (lead === "foodLife.quiz.questions." + q.id + ".lead") lead = "";
    var nextLbl = t("foodLife.quiz.next", "다음");
    var fallbackImg = optionThumbFallback();
    pendingChoice = answers[qid] || null;

    var optsHtml = q.options
      .map(function (opt) {
        var selected = pendingChoice === opt.id;
        var label = t(
          "foodLife.quiz.questions." + q.id + ".options." + opt.id,
          opt.id
        );
        var hint = t(
          "foodLife.quiz.questions." + q.id + ".hints." + opt.id,
          ""
        );
        if (hint === "foodLife.quiz.questions." + q.id + ".hints." + opt.id) {
          hint = "";
        }
        var src = optionThumbSrc(opt);
        return (
          '<button type="button" class="food-quiz-option' +
          (selected ? " is-selected" : "") +
          '" data-food-quiz-option="' +
          opt.id +
          '" role="radio" aria-checked="' +
          (selected ? "true" : "false") +
          '">' +
          '<img class="food-quiz-option__thumb" src="' +
          escapeAttr(src) +
          '" alt="" loading="lazy" decoding="async" onerror="this.onerror=null;this.src=\'' +
          escapeAttr(fallbackImg) +
          '\'">' +
          '<span class="food-quiz-option__copy">' +
          '<span class="food-quiz-option__label">' +
          escapeHtml(label) +
          "</span>" +
          (hint
            ? '<span class="food-quiz-option__hint">' +
              escapeHtml(hint) +
              "</span>"
            : "") +
          "</span>" +
          '<span class="food-quiz-option__radio" aria-hidden="true"></span>' +
          "</button>"
        );
      })
      .join("");

    panel.innerHTML =
      '<div class="food-quiz-step"' +
      (reduceMotion ? "" : ' data-anim="in"') +
      ">" +
      '<p class="food-quiz-prompt">' +
      escapeHtml(prompt) +
      "</p>" +
      (lead
        ? '<p class="food-quiz-lead">' + escapeHtml(lead) + "</p>"
        : "") +
      '<div class="food-quiz-options" role="radiogroup" aria-label="' +
      escapeAttr(prompt) +
      '">' +
      optsHtml +
      "</div>" +
      '<button type="button" class="food-quiz-next" data-food-quiz-next' +
      (pendingChoice ? "" : " disabled") +
      ">" +
      escapeHtml(nextLbl) +
      "</button></div>";

    panel.querySelectorAll("[data-food-quiz-option]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setPendingChoice(btn.getAttribute("data-food-quiz-option"));
      });
    });
    var nextBtn = panel.querySelector("[data-food-quiz-next]");
    if (nextBtn) {
      nextBtn.addEventListener("click", function () {
        if (pendingChoice) chooseOption(pendingChoice);
      });
    }
  }

  function renderResult() {
    var panel = dialog.querySelector("[data-food-quiz-panel]");
    if (!panel) return;

    var backBtn = dialog.querySelector("[data-food-quiz-back]");
    if (backBtn) backBtn.hidden = true;

    var winner = pickWinner();
    var name = resultName(winner);
    var reason = resultReason(winner);
    var eyebrow = t("foodLife.quiz.resultEyebrow", "오늘의 추천");
    var cta = t("foodLife.quiz.viewMore", t("common.viewMore", "자세히 보기 →"));
    var again = t("foodLife.quiz.restart", "다시 하기");
    analyticsEvent("quiz_complete", {
      quiz_id: "food",
      item_id: winner && winner.id ? winner.id : "",
      item_category: (winner && winner.kind) || "",
      craving: (answers && answers.craving) || "",
      spicy: (answers && answers.spicy) || "",
    });

    var bar = dialog.querySelector("[data-food-quiz-bar]");
    if (bar) bar.style.width = "100%";
    var prog = dialog.querySelector("[data-food-quiz-progress]");
    if (prog) {
      prog.textContent = t("foodLife.quiz.resultLabel", "결과");
    }

    panel.innerHTML =
      '<div class="food-quiz-result"' +
      (reduceMotion ? "" : ' data-anim="in"') +
      ">" +
      '<p class="food-quiz-result__eyebrow">' +
      escapeHtml(eyebrow) +
      "</p>" +
      '<h3 class="food-quiz-result__name">' +
      escapeHtml(name) +
      "</h3>" +
      '<p class="food-quiz-result__reason">' +
      escapeHtml(reason) +
      "</p>" +
      '<div class="food-quiz-result__actions">' +
      '<a class="food-quiz-cta" href="' +
      escapeAttr(winner.href) +
      '">' +
      escapeHtml(cta) +
      "</a>" +
      '<button type="button" class="food-quiz-restart" data-food-quiz-restart>' +
      escapeHtml(again) +
      "</button>" +
      "</div></div>";

    var restart = panel.querySelector("[data-food-quiz-restart]");
    if (restart) {
      restart.addEventListener("click", function () {
        startQuiz(true);
      });
    }
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  function rebuildActiveFromAnswers() {
    activeQuestionIds = visibleQuestions(answers).map(function (q) {
      return q.id;
    });
  }

  function chooseOption(optionId) {
    var qid = activeQuestionIds[stepIndex];
    var q = questionById(qid);
    if (!q) return;
    var opt = null;
    for (var i = 0; i < q.options.length; i++) {
      if (q.options[i].id === optionId) {
        opt = q.options[i];
        break;
      }
    }
    if (!opt) return;

    historyStack.push({
      answers: Object.assign({}, answers),
      tagScores: Object.assign({}, tagScores),
      kindScores: Object.assign({}, kindScores),
      activeQuestionIds: activeQuestionIds.slice(),
      stepIndex: stepIndex,
    });

    answers[qid] = optionId;
    applyScores(opt);
    rebuildActiveFromAnswers();

    var nextIdx = activeQuestionIds.indexOf(qid) + 1;
    if (nextIdx >= activeQuestionIds.length) {
      stepIndex = activeQuestionIds.length;
      renderResult();
      return;
    }
    stepIndex = nextIdx;
    renderQuestion();
  }

  function goBack() {
    var prev = historyStack.pop();
    if (!prev) return;
    answers = prev.answers;
    tagScores = prev.tagScores;
    kindScores = prev.kindScores;
    activeQuestionIds = prev.activeQuestionIds;
    stepIndex = prev.stepIndex;
    renderQuestion();
  }

  function analyticsEvent(name, params) {
    try {
      if (window.GuideAnalytics && typeof window.GuideAnalytics.event === "function") {
        window.GuideAnalytics.event(name, params);
      }
    } catch (e) {}
  }

  function startQuiz(keepOpen) {
    answers = {};
    historyStack = [];
    pendingChoice = null;
    resetScores();
    rebuildActiveFromAnswers();
    stepIndex = 0;
    setOpen(true);
    renderQuestion();
    analyticsEvent("quiz_start", { quiz_id: "food" });
  }

  function refreshBannerCopy() {
    if (!root) return;
    var title = root.querySelector("[data-food-quiz-banner-title]");
    var cta = root.querySelector("[data-food-quiz-banner-cta]");
    if (title) {
      title.textContent = t(
        "foodLife.quiz.bannerTitle",
        "뭐 먹을지 모르겠다면 추천받아보세요."
      );
    }
    if (cta) {
      cta.textContent = t("foodLife.quiz.bannerCta", "추천받기");
    }
    var closeBtn = dialog && dialog.querySelector("[data-food-quiz-close]");
    if (closeBtn) {
      closeBtn.setAttribute("aria-label", t("foodLife.quiz.close", "닫기"));
    }
    var backBtn = dialog && dialog.querySelector("[data-food-quiz-back]");
    if (backBtn) {
      backBtn.textContent = t("foodLife.quiz.back", "이전");
    }
    if (dialog && !dialog.hidden) {
      if (stepIndex >= activeQuestionIds.length && Object.keys(answers).length) {
        renderResult();
      } else if (activeQuestionIds.length) {
        renderQuestion();
      }
    }
  }

  function onKeydown(e) {
    if (!dialog || dialog.hidden) return;
    if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false);
    }
  }

  function init() {
    root = document.querySelector(ROOT_SEL);
    if (!root) return;
    dialog = root.querySelector("[data-food-quiz-dialog]");
    if (!dialog) return;

    var openers = root.querySelectorAll("[data-food-quiz-open]");
    openers.forEach(function (el) {
      el.addEventListener("click", function () {
        startQuiz(false);
      });
    });

    var closeBtn = dialog.querySelector("[data-food-quiz-close]");
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        setOpen(false);
      });
    }

    var backdrop = dialog.querySelector("[data-food-quiz-backdrop]");
    if (backdrop) {
      backdrop.addEventListener("click", function () {
        setOpen(false);
      });
    }

    var backBtn = dialog.querySelector("[data-food-quiz-back]");
    if (backBtn) {
      backBtn.addEventListener("click", goBack);
    }

    document.addEventListener("keydown", onKeydown);
    document.addEventListener("guide:langchange", refreshBannerCopy);
    refreshBannerCopy();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
