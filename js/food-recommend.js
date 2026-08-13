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
        { id: "meal", kinds: { meal: 6 }, tags: { hearty: 1 } },
        { id: "dessert", kinds: { dessert: 6 }, tags: { sweet: 1 } },
        {
          id: "quick",
          kinds: { quick: 5 },
          tags: { quickbite: 2, portable: 1, combo: 1 },
        },
      ],
    },
    {
      id: "spicy",
      when: function (a) {
        return a.craving === "meal" || a.craving === "quick";
      },
      options: [
        { id: "love", tags: { spicy: 4 } },
        { id: "mild", tags: { mild: 3, spicy: 1 } },
        { id: "no", tags: { mild: 3, nonspicy: 2 } },
      ],
    },
    {
      id: "dessertVibe",
      when: function (a) {
        return a.craving === "dessert";
      },
      options: [
        { id: "icy", tags: { icy: 5, cold: 2 } },
        { id: "bakery", tags: { bakery: 5 } },
        { id: "coffee", tags: { coffee: 5 } },
      ],
    },
    {
      id: "soup",
      when: function (a) {
        return a.craving === "meal";
      },
      options: [
        { id: "yes", tags: { soup: 4, warm: 1 } },
        { id: "no", tags: { nosoup: 3, grill: 1 } },
      ],
    },
    {
      id: "protein",
      when: function (a) {
        return a.craving === "meal";
      },
      options: [
        { id: "meat", tags: { meat: 4, pork: 1, grill: 1 } },
        { id: "chicken", tags: { chicken: 4 } },
        { id: "light", tags: { light: 3, veggie: 2 } },
      ],
    },
    {
      id: "mood",
      when: function (a) {
        return a.craving === "meal" || a.craving === "dessert";
      },
      options: [
        { id: "hot", tags: { cold: 4, icy: 1 } },
        { id: "cold", tags: { warm: 4, soup: 1 } },
        { id: "rain", tags: { soup: 2, warm: 2, spicy: 1 } },
        { id: "any", tags: { balanced: 1 } },
      ],
    },
    {
      id: "quickStyle",
      when: function (a) {
        return a.craving === "quick";
      },
      options: [
        { id: "combo", tags: { combo: 5 }, kinds: { quick: 2 } },
        { id: "noodles", tags: { noodles: 5, quickbite: 1 } },
        { id: "roll", tags: { roll: 5, portable: 2 } },
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

  function catalog() {
    var list = window.FOOD_RECOMMEND_CATALOG;
    return Array.isArray(list) ? list : [];
  }

  function t(key, fallback) {
    try {
      var lang =
        (window.GuideI18n &&
          window.GuideI18n.getLang &&
          window.GuideI18n.getLang()) ||
        "ko";
      var pack =
        (window.__I18N_MESSAGES__ && window.__I18N_MESSAGES__[lang]) || null;
      if (pack) {
        var cur = pack;
        var parts = key.split(".");
        for (var i = 0; i < parts.length; i++) {
          if (!cur || typeof cur !== "object" || !(parts[i] in cur)) {
            cur = undefined;
            break;
          }
          cur = cur[parts[i]];
        }
        if (typeof cur === "string" && cur) return cur;
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

    var prompt = t(
      "foodLife.quiz.questions." + q.id + ".prompt",
      q.id
    );

    var optsHtml = q.options
      .map(function (opt) {
        var label = t(
          "foodLife.quiz.questions." + q.id + ".options." + opt.id,
          opt.id
        );
        return (
          '<button type="button" class="food-quiz-option" data-food-quiz-option="' +
          opt.id +
          '">' +
          '<span class="food-quiz-option__label">' +
          escapeHtml(label) +
          "</span></button>"
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
      '<div class="food-quiz-options" role="group" aria-label="' +
      escapeAttr(prompt) +
      '">' +
      optsHtml +
      "</div></div>";

    panel.querySelectorAll("[data-food-quiz-option]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        chooseOption(btn.getAttribute("data-food-quiz-option"));
      });
    });
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

  function startQuiz(keepOpen) {
    answers = {};
    historyStack = [];
    resetScores();
    rebuildActiveFromAnswers();
    stepIndex = 0;
    setOpen(true);
    renderQuestion();
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
