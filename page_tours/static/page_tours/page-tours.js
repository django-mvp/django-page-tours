(function () {
  "use strict";

  var script = document.getElementById("page-tour-steps");
  var driver = window.driver && window.driver.js && window.driver.js.driver;
  if (!script || !driver) {
    return;
  }

  var steps = JSON.parse(script.textContent).map(function (step) {
    var driverStep = { popover: { title: step.title, description: step.text } };
    if (step.element) {
      driverStep.element = function () {
        try {
          return document.querySelector(step.element) || undefined;
        } catch (error) {
          return undefined;
        }
      };
    }
    return driverStep;
  });

  driver({ steps: steps, skipMissingElement: true }).drive();
})();
