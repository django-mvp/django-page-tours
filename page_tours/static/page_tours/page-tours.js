(function () {
  "use strict";

  // The element of the selector, when it is there and can be seen.
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

  // What a visitor did under a declaration's name: a list of ids kept in the
  // browser for the version that is playing. An entry of another version, of
  // another shape or that cannot be read counts as nothing done.
  function memory(kind, payload) {
    var key = "page-tours:" + kind + ":" + payload.id;
    return {
      get: function () {
        try {
          var entry = JSON.parse(window.localStorage.getItem(key));
          if (entry && entry.version === payload.version && Array.isArray(entry.ids)) {
            return entry.ids;
          }
        } catch (error) {
          // Storage that cannot be read holds nothing.
        }
        return [];
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
          // Storage that cannot be written means nothing is remembered.
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

  // Gives every part of the shown popover its documented name and the classes
  // the site configured for it, and nothing else: no attribute, text or role.
  // Where there is no driver to ask, the popover is not a step of a tour and
  // its button is the next one.
  function popoverParts(parts) {
    return function (popover, opts) {
      var last = opts && opts.driver && opts.driver.isLastStep();
      addClasses(parts, popover.wrapper, "box");
      addClasses(parts, popover.title, "title");
      addClasses(parts, popover.description, "text");
      addClasses(parts, popover.progress, "progress");
      addClasses(parts, popover.previousButton, "previous");
      addClasses(parts, popover.nextButton, last ? "done" : "next");
      addClasses(parts, popover.closeButton, "close");
    };
  }

  // Builds the tour a payload describes. `instance()` is the Driver.js instance,
  // made on its first call, whose `drive` is the package's start; `start()` does
  // nothing for a tour with nothing to show and otherwise drives that instance,
  // after ending a run that is still going.
  function buildTour(payload, driver) {
    var seen = memory("seen", payload);
    var nameParts = popoverParts(payload.parts);
    var steps = payload.config.steps.map(function (step) {
      var driverStep = Object.assign({}, step);
      if (step.element) {
        driverStep.element = function () {
          return visibleElement(step.element);
        };
      } else {
        delete driverStep.element;
      }
      return driverStep;
    });

    function showable() {
      return payload.config.steps.some(function (step) {
        return !step.element || visibleElement(step.element);
      });
    }

    var tour;
    var returnFocusTo;

    // Driver.js writes the overlay's fill and opacity as inline styles, which no
    // site rule can beat. As attributes of the svg they look the same and give way.
    // The opacity becomes fill-opacity: the svg's own opacity is what the fade-in
    // animates, and the dimming has to multiply into that rather than replace it.
    function nameOverlay() {
      var overlay = document.querySelector("svg.driver-overlay");
      if (!overlay) {
        return;
      }
      addClasses(payload.parts, overlay, "highlight");
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

    // Driver.js creates the overlay after the first step's box and a moment before
    // that step is highlighted, so the overlay is named when it is added.
    var overlayWatcher;

    function stopWatchingOverlay() {
      if (overlayWatcher) {
        overlayWatcher.disconnect();
        overlayWatcher = undefined;
      }
    }

    // Ending the tour waits until Driver.js has finished the call that raised,
    // so what it adds afterwards is removed too.
    function guarded(work) {
      return function (a, b) {
        try {
          work(a, b);
        } catch (error) {
          queueMicrotask(endTour);
        }
      };
    }

    // Driver.js 1.11.0 puts focus back on whatever had it when the current step
    // opened, which after the first step is a button of a popover it has removed.
    // Focus is put back here instead, on what had it before the tour started.
    function restoreFocus() {
      var target = returnFocusTo;
      returnFocusTo = undefined;
      if (target && target.isConnected && typeof target.focus === "function") {
        target.focus();
      }
    }

    // Runs once Driver.js has finished ending the tour, so the focus it moves
    // on the way out is moved back. A replay that has already started the next
    // tour keeps everything that tour set up.
    function finished() {
      if (tour.isActive()) {
        return;
      }
      window.removeEventListener("error", endTour);
      stopWatchingOverlay();
      restoreFocus();
    }

    function endTour() {
      try {
        if (tour) {
          tour.destroy();
        }
      } catch (error) {
        // Cleaning up by hand below covers whatever destroy() could not.
      }
      window.removeEventListener("error", endTour);
      stopWatchingOverlay();
      document
        .querySelectorAll(
          ".driver-overlay, .driver-popover, .driver-live-region, #driver-dummy-element"
        )
        .forEach(function (el) {
          el.remove();
        });
      [
        "driver-active",
        "driver-fade",
        "driver-simple",
        "driver-no-scroll",
        "driver-active-element",
        "driver-active-element-parent",
        "driver-active-element-parent-no-scroll",
        "driver-allowed-element",
        "driver-no-interaction",
      ].forEach(function (name) {
        document.querySelectorAll("." + name).forEach(function (el) {
          el.classList.remove(name);
        });
      });
      document
        .querySelectorAll('[aria-controls="driver-popover-content"]')
        .forEach(function (el) {
          el.removeAttribute("aria-haspopup");
          el.removeAttribute("aria-expanded");
          el.removeAttribute("aria-controls");
        });
      document.body.style.removeProperty("--driver-animation-duration");
      restoreFocus();
    }

    // The package's start, which the instance's `drive` runs whoever calls it.
    function run(driveOwn, args) {
      if (!showable()) {
        return;
      }
      try {
        returnFocusTo = document.activeElement;
        window.addEventListener("error", endTour);
        stopWatchingOverlay();
        // A tour closed while a step is still opening never reaches onDestroyed,
        // so the watcher also notices the overlay going.
        overlayWatcher = new MutationObserver(
          guarded(function () {
            nameOverlay();
            finished();
          })
        );
        overlayWatcher.observe(document.body, { childList: true });
        driveOwn.apply(tour, args);
        seen.set([payload.id]);
      } catch (error) {
        endTour();
      }
    }

    function instance() {
      if (!tour) {
        // The tour's own options go first, so the settings the package
        // depends on below replace any of the same name.
        tour = driver(Object.assign({}, payload.config, {
          steps: steps,
          skipMissingElement: true,
          onPopoverRender: guarded(nameParts),
          onDestroyed: function () {
            queueMicrotask(finished);
          },
        }));
        var driveOwn = tour.drive;
        tour.drive = function () {
          run(driveOwn, arguments);
        };
      }
      return tour;
    }

    function start() {
      if (!showable()) {
        return;
      }
      var tour = instance();
      if (tour.isActive()) {
        tour.destroy();
      }
      tour.drive();
    }

    return { start: start, instance: instance };
  }

  // Plays the tour a payload describes.
  function playTour(payload, driver) {
    var seen = memory("seen", payload);
    var start = buildTour(payload, driver).start;

    // A replay control is the developer's own element. One written with `hidden`,
    // as in a shared template, shows only where this point is reached: on a page
    // with a tour, with JavaScript on. This comes before autoplay, so a step can
    // point at it.
    document.querySelectorAll("[data-page-tour-replay]").forEach(function (control) {
      control.addEventListener("click", start);
      control.hidden = false;
    });

    if (payload.autoplay && seen.get().length === 0) {
      start();
    }
  }

  // Shows the hints a payload describes. A hint's key is worked out in the
  // script only, so the build's own `id` stays as declared.
  function playHints(payload, hintsDriver) {
    var config = payload.config;
    var shared = config.beacon || {};
    var dismissed = memory("dismissed", payload);

    function keyOf(hint) {
      return hint.id || hint.element;
    }

    var hints = config.hints.map(function (hint) {
      var own = hint.beacon || {};
      var beacon = Object.assign({}, own);
      var classes = ((payload.parts && payload.parts.beacon) || []).concat(
        own.className || shared.className || []
      );
      if (classes.length) {
        beacon.className = classes.join(" ");
      }
      return Object.assign({}, hint, {
        beacon: beacon,
        popover: Object.assign({}, hint.popover, {
          onPopoverRender: popoverParts(payload.parts),
        }),
      });
    });

    function undismissed() {
      var keys = dismissed.get();
      return hints.filter(function (hint) {
        return keys.indexOf(keyOf(hint)) === -1;
      });
    }

    // Where nothing can be remembered, Driver.js still keeps a dismissed hint
    // hidden until the page is left.
    var instance = hintsDriver(
      Object.assign({}, config, {
        hints: undismissed(),
        onDismiss: function (element, hint) {
          var keys = dismissed.get();
          if (keys.indexOf(keyOf(hint)) === -1) {
            dismissed.set(keys.concat(keyOf(hint)));
          }
        },
      })
    );
    instance.show();

    // A restore control is the developer's own element, written with `hidden`.
    document.querySelectorAll("[data-page-hints-restore]").forEach(function (control) {
      control.addEventListener("click", function () {
        dismissed.clear();
        instance.setHints(hints);
        instance.show();
      });
      control.hidden = false;
    });
  }

  // Shows the checklist a payload describes. An item that names a tour starts
  // it through the tour's Driver.js instance, which Driver.js drives as it is.
  function playChecklist(payload, checklistDriver, tourDriver) {
    var config = payload.config;
    var instance = checklistDriver(
      Object.assign({}, config, {
        id: payload.id,
        completed: config.completed,
        items: config.items.map(function (item) {
          if (!item.tour) {
            return item;
          }
          return Object.assign({}, item, {
            tour: buildTour(item.tour, tourDriver).instance(),
          });
        }),
      })
    );
    instance.show();

    [
      ["box", ".driver-checklist-panel"],
      ["title", ".driver-checklist-title"],
      ["text", ".driver-checklist-description"],
      ["progress", ".driver-checklist-progress"],
      ["close", ".driver-checklist-close-btn"],
      ["launcher", ".driver-checklist-launcher"],
      ["item", ".driver-checklist-item"],
    ].forEach(function (pair) {
      document.querySelectorAll(pair[1]).forEach(function (element) {
        addClasses(payload.parts, element, pair[0]);
      });
    });
  }

  // Plays every kind of declaration the page carries, each from its own element
  // and each in its own try, so one that fails neither stops the other nor
  // raises on the page. Hints and the checklist come first, so they are on the
  // page before a tour starts and one of its steps can point at them. The page
  // is looked at only once it is parsed, so an element may sit anywhere in it and
  // the scripts may load in any way. A page has one of each kind: should an
  // element appear twice, the first is played and the other is left alone.
  function play() {
    var tourDriver = window.driver && window.driver.js && window.driver.js.driver;
    var hintsDriver = window.driverHints && window.driverHints.hints;
    var checklistDriver = window.driverChecklist && window.driverChecklist.checklist;
    var kinds = [
      ["hints", playHints, hintsDriver],
      ["checklist", playChecklist, checklistDriver],
      ["tour", playTour, tourDriver],
    ];
    var present = kinds.filter(function (kind) {
      return kind[2] && document.getElementById("page-tours-" + kind[0]);
    });
    if (present.length === 0) {
      return;
    }

    // Declared first, the page-tours cascade layer is the lowest of the page's.
    // The link is found by the file it loads, which a hashed name still contains.
    var stylesheet = document.querySelector(
      'link[rel~="stylesheet"][href*="page_tours/page-tours."]'
    );
    if (stylesheet && document.head.firstElementChild !== stylesheet) {
      document.head.prepend(stylesheet);
    }

    present.forEach(function (kind) {
      try {
        var script = document.getElementById("page-tours-" + kind[0]);
        kind[1](JSON.parse(script.textContent), kind[2], tourDriver);
      } catch (error) {
        // A declaration that cannot be played leaves the page as it was.
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", play);
  } else {
    play();
  }
})();
