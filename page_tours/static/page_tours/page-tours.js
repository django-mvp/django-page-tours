(function () {
  "use strict";

  // Plays every guide the page renders: a tour, hints and a checklist, each from
  // a <script id="page-tours-<kind>" type="application/json"> element. Each
  // guide's `config` is already the object Driver.js takes. What this script adds
  // is what a Python declaration cannot hold: elements found when they are shown,
  // the classes each part carries, and what the browser remembers.

  // ---------------------------------------------------------------- shared

  function visibleElement(selector) {
    try {
      var el = document.querySelector(selector);
      if (el && el.checkVisibility({ visibilityProperty: true, opacityProperty: true })) {
        return el;
      }
    } catch (error) {
      // An invalid selector counts as an element that is not there.
    }
    return undefined;
  }

  // What the browser remembers about a guide: a list of ids, kept under the
  // guide's name for its version. A new version starts from nothing.
  function memory(kind, payload) {
    var key = "page-tours:" + kind + ":" + payload.id;
    return {
      get: function () {
        try {
          var stored = JSON.parse(window.localStorage.getItem(key));
          return stored && stored.version === payload.version ? stored.ids : [];
        } catch (error) {
          return [];
        }
      },
      set: function (ids) {
        try {
          window.localStorage.setItem(
            key,
            JSON.stringify({ version: payload.version, ids: ids })
          );
        } catch (error) {
          // Storage that cannot be written means nothing is remembered.
        }
      },
      clear: function () {
        try {
          window.localStorage.removeItem(key);
        } catch (error) {
          // Nothing to forget.
        }
      },
    };
  }

  function addClasses(parts, element, part) {
    var tokens = parts && parts[part];
    if (element && tokens && tokens.length) {
      element.classList.add.apply(element.classList, tokens);
    }
  }

  // A popover is a popover, in a tour or a hint: each part carries its classes.
  function popoverParts(parts) {
    return function (popover, opts) {
      addClasses(parts, popover.wrapper, "box");
      addClasses(parts, popover.title, "title");
      addClasses(parts, popover.description, "text");
      addClasses(parts, popover.progress, "progress");
      addClasses(parts, popover.previousButton, "previous");
      var last = opts && opts.driver && opts.driver.isLastStep && opts.driver.isLastStep();
      addClasses(parts, popover.nextButton, last ? "done" : "next");
      addClasses(parts, popover.closeButton, "close");
    };
  }

  // Driver.js writes the overlay's fill and opacity as inline styles, which no
  // site rule can beat. As attributes of the svg they look the same and give way.
  function nameOverlay(parts) {
    var overlay = document.querySelector("svg.driver-overlay");
    if (!overlay) {
      return;
    }
    addClasses(parts, overlay, "highlight");
    var path = overlay.querySelector("path");
    [
      ["fill", "fill"],
      ["opacity", "fill-opacity"],
    ].forEach(function (pair) {
      var value = path && path.style.getPropertyValue(pair[0]);
      if (value) {
        overlay.setAttribute(pair[1], value);
        path.style.removeProperty(pair[0]);
      }
    });
  }

  // ---------------------------------------------------------------- tours

  // Builds the Driver.js tour for a tour's payload. A page's own tour and a tour
  // a checklist item starts are built here alike, so both find their elements,
  // name their parts, clean up after themselves and count as seen.
  function buildTour(payload) {
    var create = window.driver.js.driver;
    var seen = memory("seen", payload);
    var returnFocusTo;
    var overlayWatcher;
    var instance;

    function stopWatching() {
      if (overlayWatcher) {
        overlayWatcher.disconnect();
        overlayWatcher = undefined;
      }
      window.removeEventListener("error", fail);
    }

    function restoreFocus() {
      var target = returnFocusTo;
      returnFocusTo = undefined;
      if (target && target.isConnected && typeof target.focus === "function") {
        target.focus();
      }
    }

    // A Driver.js error mid-tour must never leave the page dimmed and dead.
    function fail() {
      try {
        instance.destroy();
      } catch (error) {
        // Removing by hand below covers whatever destroy() could not.
      }
      stopWatching();
      document
        .querySelectorAll(".driver-overlay, .driver-popover, #driver-dummy-element")
        .forEach(function (el) {
          el.remove();
        });
      ["driver-active", "driver-fade", "driver-simple", "driver-no-scroll"].forEach(
        function (name) {
          document.body.classList.remove(name);
        }
      );
      restoreFocus();
    }

    var steps = payload.config.steps.map(function (step) {
      var driverStep = Object.assign({}, step);
      if (step.element) {
        driverStep.element = function () {
          return visibleElement(step.element);
        };
      }
      return driverStep;
    });

    instance = create(
      Object.assign({}, payload.config, {
        steps: steps,
        skipMissingElement: true,
        onPopoverRender: popoverParts(payload.parts),
        onDestroyed: function () {
          stopWatching();
          restoreFocus();
        },
      })
    );

    instance.showable = function () {
      return payload.config.steps.some(function (step) {
        return !step.element || visibleElement(step.element);
      });
    };
    instance.isSeen = function () {
      return seen.get().length > 0;
    };

    // Whoever starts the tour, the page or a checklist, starts it through here.
    var drive = instance.drive;
    instance.drive = function (index) {
      returnFocusTo = document.activeElement;
      window.addEventListener("error", fail);
      overlayWatcher = new MutationObserver(function () {
        nameOverlay(payload.parts);
      });
      overlayWatcher.observe(document.body, { childList: true });
      try {
        drive(index);
        seen.set(["seen"]);
      } catch (error) {
        fail();
      }
    };
    return instance;
  }

  function playTour(payload) {
    var tour = buildTour(payload);

    function start() {
      if (!tour.showable()) {
        return;
      }
      if (tour.isActive()) {
        tour.destroy();
      }
      tour.drive();
    }

    // A replay control is the developer's own element. One written with `hidden`
    // shows only on a page with a tour, with JavaScript on.
    document.querySelectorAll("[data-page-tour-replay]").forEach(function (control) {
      control.addEventListener("click", start);
      control.hidden = false;
    });

    if (payload.autoplay && !tour.isSeen()) {
      start();
    }
  }

  // ---------------------------------------------------------------- hints

  function playHints(payload) {
    var create = window.driverHints && window.driverHints.hints;
    if (!create) {
      return;
    }
    var dismissed = memory("dismissed", payload);
    var parts = payload.parts;
    var namePopover = popoverParts(parts);

    function keyOf(hint) {
      return hint.id || hint.element;
    }

    function hintsToShow() {
      var gone = dismissed.get();
      return payload.config.hints
        .filter(function (hint) {
          return gone.indexOf(keyOf(hint)) === -1;
        })
        .map(function (hint) {
          // The beacon carries the classes configured for it, then its own.
          var beacon = Object.assign({}, hint.beacon);
          beacon.className = [(parts.beacon || []).join(" "), beacon.className || ""]
            .join(" ")
            .trim();
          return Object.assign({}, hint, {
            id: keyOf(hint),
            beacon: beacon,
            popover: Object.assign({}, hint.popover, { onPopoverRender: namePopover }),
          });
        });
    }

    var instance = create(
      Object.assign({}, payload.config, {
        hints: hintsToShow(),
        onDismiss: function (element, hint) {
          var gone = dismissed.get();
          if (gone.indexOf(hint.id) === -1) {
            gone.push(hint.id);
          }
          dismissed.set(gone);
        },
      })
    );
    instance.show();

    // A control that brings dismissed hints back.
    document.querySelectorAll("[data-page-hints-restore]").forEach(function (control) {
      control.addEventListener("click", function () {
        dismissed.clear();
        instance.setHints(hintsToShow());
        instance.show();
      });
      control.hidden = false;
    });
  }

  // ---------------------------------------------------------------- checklists

  function playChecklist(payload) {
    var create = window.driverChecklist && window.driverChecklist.checklist;
    if (!create) {
      return;
    }
    var ticked = memory("done", payload);
    var parts = payload.parts;
    var instance;

    // The checklist's parts are named after the matching parts of a tour step:
    // its panel is a box with a title, text and progress, and a close control.
    function nameParts() {
      var root = document.querySelector(".driver-checklist");
      if (!root) {
        return;
      }
      [
        [".driver-checklist-panel", "box"],
        [".driver-checklist-title", "title"],
        [".driver-checklist-description", "text"],
        [".driver-checklist-progress", "progress"],
        [".driver-checklist-close-btn", "close"],
        [".driver-checklist-launcher", "launcher"],
        [".driver-checklist-item", "item"],
      ].forEach(function (pair) {
        root.querySelectorAll(pair[0]).forEach(function (el) {
          addClasses(parts, el, pair[1]);
        });
      });
    }

    var done = payload.config.completed.slice();
    ticked.get().forEach(function (id) {
      if (done.indexOf(id) === -1) {
        done.push(id);
      }
    });

    instance = create(
      Object.assign({}, payload.config, {
        id: payload.id,
        completed: done,
        items: payload.config.items.map(function (item) {
          return item.tour ? Object.assign({}, item, { tour: buildTour(item.tour) }) : item;
        }),
        onProgress: function (progress) {
          ticked.set(progress.completed);
        },
        onEvent: function () {
          queueMicrotask(nameParts);
        },
      })
    );
    instance.show();
    nameParts();

    // A control of the developer's own that opens and closes the checklist, for
    // a checklist declared with `launcher=False`.
    document.querySelectorAll("[data-page-checklist-toggle]").forEach(function (control) {
      control.addEventListener("click", function () {
        instance.toggle();
      });
      control.hidden = false;
    });
  }

  // ---------------------------------------------------------------- start

  var players = { tour: playTour, hints: playHints, checklist: playChecklist };

  function play() {
    if (!(window.driver && window.driver.js)) {
      return;
    }
    // Declared first, the page-tours cascade layer is the lowest of the page's.
    var stylesheet = document.querySelector(
      'link[rel~="stylesheet"][href*="page_tours/page-tours."]'
    );
    if (stylesheet && document.head.firstElementChild !== stylesheet) {
      document.head.prepend(stylesheet);
    }
    // Hints and the checklist go first, so a tour step can point at them.
    ["hints", "checklist", "tour"].forEach(function (kind) {
      var script = document.getElementById("page-tours-" + kind);
      if (script) {
        players[kind](JSON.parse(script.textContent));
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", play);
  } else {
    play();
  }
})();
