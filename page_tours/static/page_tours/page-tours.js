(function () {
  "use strict";

  // The page's tour, from the element `{{ tour }}` renders. The page is looked
  // at only once it is parsed, so the element may sit anywhere in it and the
  // scripts may load in any way. A page has one tour: should the element appear
  // twice, the first is played and the other is left alone.
  function play() {
    var script = document.getElementById("page-tour-steps");
    var driver = window.driver && window.driver.js && window.driver.js.driver;
    if (!script || !driver) {
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

    var payload = JSON.parse(script.textContent);
    var seenKey = "page-tours:seen:" + payload.id;
    // The entry holds the version that played. A browser that saw the tour before
    // tours had versions holds "1", which is the version a tour has by default.
    var seenVersion = String(payload.version);
    var steps = payload.steps.map(function (step) {
      var driverStep = Object.assign({}, step);
      if (step.element) {
        driverStep.element = function () {
          return visibleElement(step.element);
        };
      }
      return driverStep;
    });

    function showable() {
      return payload.steps.some(function (step) {
        return !step.element || visibleElement(step.element);
      });
    }

    function isSeen() {
      try {
        return window.localStorage.getItem(seenKey) === seenVersion;
      } catch (error) {
        return false;
      }
    }

    function markSeen() {
      try {
        window.localStorage.setItem(seenKey, seenVersion);
      } catch (error) {
        // Storage that cannot be written means the tour plays on every visit.
      }
    }

    var tour;
    var returnFocusTo;

    function addClasses(element, part) {
      var tokens = payload.parts && payload.parts[part];
      if (element && tokens && tokens.length) {
        element.classList.add.apply(element.classList, tokens);
      }
    }

    // Gives every part of the shown step its documented name and the classes the
    // site configured for it, and nothing else: no attribute, text or role.
    function nameParts(popover, opts) {
      addClasses(popover.wrapper, "box");
      addClasses(popover.title, "title");
      addClasses(popover.description, "text");
      addClasses(popover.progress, "progress");
      addClasses(popover.previousButton, "previous");
      addClasses(popover.nextButton, opts.driver.isLastStep() ? "done" : "next");
      addClasses(popover.closeButton, "close");
    }

    // Driver.js writes the overlay's fill and opacity as inline styles, which no
    // site rule can beat. As attributes of the svg they look the same and give way.
    // The opacity becomes fill-opacity: the svg's own opacity is what the fade-in
    // animates, and the dimming has to multiply into that rather than replace it.
    function nameOverlay() {
      var overlay = document.querySelector("svg.driver-overlay");
      if (!overlay) {
        return;
      }
      addClasses(overlay, "highlight");
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

    function start() {
      if (!showable()) {
        return;
      }
      try {
        if (tour && tour.isActive()) {
          tour.destroy();
        }
        returnFocusTo = document.activeElement;
        // The tour's own options go first, so the settings the package
        // depends on below replace any of the same name.
        tour = driver(Object.assign({}, payload.options, {
          steps: steps,
          skipMissingElement: true,
          onPopoverRender: guarded(nameParts),
          onDestroyed: function () {
            queueMicrotask(finished);
          },
        }));
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
        tour.drive();
        markSeen();
      } catch (error) {
        endTour();
      }
    }

    // A replay control is the developer's own element. One written with `hidden`,
    // as in a shared template, shows only where this point is reached: on a page
    // with a tour, with JavaScript on. This comes before autoplay, so a step can
    // point at it.
    document.querySelectorAll("[data-page-tour-replay]").forEach(function (control) {
      control.addEventListener("click", start);
      control.hidden = false;
    });

    if (payload.autoplay && !isSeen()) {
      start();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", play);
  } else {
    play();
  }
})();
