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

  var parsed = JSON.parse(script.textContent);
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

  driver({ steps: steps, skipMissingElement: true }).drive();
})();
