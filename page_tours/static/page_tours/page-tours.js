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

  var parsed = JSON.parse(script.textContent).steps;
  var steps = parsed.map(function (step) {
    var driverStep = { popover: { title: step.title, description: step.text } };
    if (step.element) {
      driverStep.element = function () {
        return visibleElement(step.element);
      };
    }
    return driverStep;
  });

  var showable = parsed.some(function (step) {
    return !step.element || visibleElement(step.element);
  });
  if (!showable) {
    return;
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

  try {
    tour = driver({
      steps: steps,
      skipMissingElement: true,
      onDestroyed: function () {
        window.removeEventListener("error", endTour);
      },
    });
    window.addEventListener("error", endTour);
    tour.drive();
  } catch (error) {
    endTour();
  }
})();
