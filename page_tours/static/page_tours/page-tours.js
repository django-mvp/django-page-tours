(function () {
  "use strict";

  var script = document.getElementById("page-tour-steps");
  var driver = window.driver && window.driver.js && window.driver.js.driver;
  if (!script || !driver) {
    return;
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
  var steps = payload.steps.map(function (step) {
    var driverStep = { popover: { title: step.title, description: step.text } };
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
      return window.localStorage.getItem(seenKey) !== null;
    } catch (error) {
      return false;
    }
  }

  function markSeen() {
    try {
      window.localStorage.setItem(seenKey, "1");
    } catch (error) {
      // Storage that cannot be written means the tour plays on every visit.
    }
  }

  var tour;

  function endTour() {
    try {
      if (tour) {
        tour.destroy();
      }
    } catch (error) {
      // Cleaning up by hand below covers whatever destroy() could not.
    }
    window.removeEventListener("error", endTour);
    document
      .querySelectorAll(".driver-overlay, .driver-popover, #driver-dummy-element")
      .forEach(function (el) {
        el.remove();
      });
    [
      "driver-active",
      "driver-fade",
      "driver-simple",
      "driver-active-element",
      "driver-active-element-parent",
      "driver-active-element-parent-no-scroll",
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
  }

  function start() {
    if (!showable()) {
      return;
    }
    try {
      if (tour && tour.isActive()) {
        tour.destroy();
      }
      tour = driver({
        steps: steps,
        skipMissingElement: true,
        onDestroyed: function () {
          window.removeEventListener("error", endTour);
        },
      });
      window.addEventListener("error", endTour);
      tour.drive();
      markSeen();
    } catch (error) {
      endTour();
    }
  }

  var holders = document.querySelectorAll("template[data-page-tour-replay]");
  holders.forEach(function (holder) {
    var control = holder.content.firstElementChild;
    if (control) {
      var button = control.cloneNode(true);
      button.addEventListener("click", start);
      holder.before(button);
    }
    holder.remove();
  });

  if (payload.autoplay && !isSeen()) {
    start();
  }
})();
