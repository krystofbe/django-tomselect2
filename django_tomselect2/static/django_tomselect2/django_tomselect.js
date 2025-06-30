document.addEventListener("DOMContentLoaded", () =>
  initializeTomSelectElements(document),
);

document.addEventListener("formset:added", handleFormsetAdded);

/* -------------------------------------------------------------------------
 * HTMX integration
 *   • initialise TomSelect for fragments swapped into the DOM
 *   • fire an htmx change-trigger whenever the select value changes
 * ----------------------------------------------------------------------  */
if (window.htmx) {
  /* When HTMX swaps content in (`htmx:load` = alias for `htmx:afterSwap`)
     we only have to look at the fragment that was just added (event.target). */
  document.body.addEventListener("htmx:load", (event) => {
    initializeTomSelectElements(event.target);
  });
}

/**
 * Initializes all Tom Select elements inside a given root node.
 * @param {ParentNode} root - The node inside which we look for [data-tom-select] elements.
 */
function initializeTomSelectElements(root = document) {
  const tomSelectElements = root.querySelectorAll("[data-tom-select]");
  tomSelectElements.forEach(initializeTomSelectElement);
}

/**
 * Handles newly added formsets by initializing Tom Select elements within them.
 * @param {Event} event - The formset:added event.
 */
function handleFormsetAdded(event) {
  initializeTomSelectElements(event.target);
}

/**
 * Processes plugin callbacks by converting htmlTemplate strings into html callback functions.
 * @param {Object} config - The Tom Select configuration object.
 * @returns {Object} - The updated Tom Select configuration with processed plugin callbacks.
 */
function processPluginCallbacks(config) {
  const plugins = config.plugins;

  // Iterate over each plugin in the configuration
  Object.keys(plugins).forEach((pluginName) => {
    const pluginConfig = plugins[pluginName];

    // Check if the plugin has an htmlTemplate
    if (pluginConfig.htmlTemplate) {
      // Create an html callback function from the htmlTemplate string
      plugins[pluginName].html = new Function(
        "data",
        `return \`${pluginConfig.htmlTemplate}\`;`,
      );

      // Remove the htmlTemplate property as it's no longer needed
      delete plugins[pluginName].htmlTemplate;
    }
  });

  return config;
}

/**
 * Initializes a single Tom Select element, determining if it's heavy or not.
 * @param {HTMLElement} element - The select element to initialize.
 */
function initializeTomSelectElement(element) {
  /* Do nothing if this element is already wired-up. Prevents double init
     when both htmx and formset listeners hit the same node. */
  if (element.tomselect) {
    return;
  }

  // Parse the data-tom-select attribute if it exists
  let tomSelectConfig = {};
  if (element.dataset.tomSelect) {
    try {
      tomSelectConfig = JSON.parse(element.dataset.tomSelect);
    } catch (error) {
      console.error("Invalid JSON in data-tom-select:", error);
    }
  }

  // Initialize with plugins if any
  const isHeavy =
    element.hasAttribute("data-widget-type") &&
    element.getAttribute("data-widget-type") === "heavy";

  let settings = {};

  if (isHeavy) {
    settings = getHeavyTomSelectSettings(element, tomSelectConfig);
  } else {
    settings = getLightTomSelectSettings(element, tomSelectConfig);
  }

  // Process plugin callbacks to convert htmlTemplate to html functions
  if (settings.plugins) {
    settings = processPluginCallbacks(settings);
  }

  // Initialize Tom Select with the settings
  const tom = new TomSelect(element, settings);
  element.tomselect = tom;

  // Add event listeners for selection changes
  element.addEventListener("change", handleSelectionChange);

  // Add event listener to auto-select when only one option is available
  tom.on("load", function (data) {
    autoSelectSingleOption(tom, data);
  });

  // Also handle the 'load' event for initial load
  tom.on("initialize", function () {
    const currentOptions = tom.options;
    if (Object.keys(currentOptions).length === 1) {
      const singleOption = Object.values(currentOptions)[0];
      tom.setValue(singleOption[tom.settings.valueField], true);
    }
  });
}

/**
 * Automatically selects the first option if there's only one available.
 * @param {TomSelect} tom - The Tom Select instance.
 * @param {Object} data - The data returned from the AJAX load.
 */
function autoSelectSingleOption(tom, data) {
  if (data.results && data.results.length === 1) {
    const singleOption = data.results[0];
    tom.setValue(singleOption[tom.settings.valueField], true);
  }
}

/**
 * Handles the change event for Tom Select elements, managing dependent fields
 * and notifying HTMX (if present) that the value changed.
 * @param {Event} event - The change event.
 */
function handleSelectionChange(event) {
  /* ---------------------------------------------------------------------
   * 1. HTMX trigger
   * ------------------------------------------------------------------  */
  if (window.htmx) {
    window.htmx.trigger(event.target, "change");
  }

  /* ---------------------------------------------------------------------
   * 2. Dependent field logic
   * ------------------------------------------------------------------  */
  const selectedFieldName = event.target.name;
  const dependentSelectors = document.querySelectorAll(
    `[data-dependent-fields~="${selectedFieldName}"]`,
  );

  dependentSelectors.forEach((dependentElement) => {
    dependentElement.value = "";
    const tomSelectInstance = dependentElement.tomselect;
    if (tomSelectInstance) {
      tomSelectInstance.clearOptions();
      tomSelectInstance.clear();

      const params = new URLSearchParams();
      // Set an empty string for the search query
      params.append("q", "");
      params.append("field_id", dependentElement.getAttribute("data-field_id"));

      const dependentFields = dependentElement
        .getAttribute("data-dependent-fields")
        .trim()
        .split(/\s+/)
        .filter(Boolean);

      dependentFields.forEach((fieldName) => {
        const fieldValue = document.querySelector(
          `[name="${fieldName}"]`,
        ).value;
        params.append(fieldName, fieldValue);
      });

      fetch(
        `${dependentElement.getAttribute("data-url")}?${params.toString()}`,
        {
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        },
      )
        .then((response) => response.json())
        .then((data) => {
          // Add the options to the select
          if (data.results) {
            tomSelectInstance.addOptions(data.results);
            // Auto-select if only one option
            if (data.results.length === 1) {
              const singleOption = data.results[0];
              tomSelectInstance.setValue(
                singleOption[tomSelectInstance.settings.valueField],
                true,
              );
            }
          }
        })
        .catch((error) => {
          console.error("Error loading options:", error);
        });
    }
  });
}

/**
 * Initialize a standard (light) Tom Select instance.
 * @param {HTMLElement} element - The select element to initialize.
 */
function getLightTomSelectSettings(element, tomSelectConfig) {
  // Base config with defaults
  const baseConfig = {
    openOnFocus: true,
    placeholder: element.getAttribute("placeholder") || "",
    plugins: [],
  };

  // Merge in this order:
  // 1. Base config
  // 2. User provided tomSelectConfig
  return {
    ...baseConfig,
    ...tomSelectConfig,
  };
}

/**
 * Initialize a heavy Tom Select instance with AJAX loading and dependent fields.
 * @param {HTMLElement} element - The select element to initialize.
 */
function getHeavyTomSelectSettings(element, tomSelectConfig) {
  const fieldId = element.getAttribute("data-field_id");
  const loadUrl = element.getAttribute("data-url");
  const dependentFields = (element.getAttribute("data-dependent-fields") || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  const heavyConfig = {
    valueField: element.getAttribute("data-value-field") || "id",
    labelField: element.getAttribute("data-label-field") || "text",
    searchField: (element.getAttribute("data-search-field") || "text")
      .split(",")
      .map((field) => field.trim()),
    load: function (query, callback) {
      const params = new URLSearchParams();
      params.append("q", query);
      params.append("field_id", fieldId);

      dependentFields.forEach((fieldName) => {
        const dependentElement = document.querySelector(
          `[name="${fieldName}"]`,
        );
        if (dependentElement) {
          params.append(fieldName, dependentElement.value);
        }
      });

      fetch(`${loadUrl}?${params.toString()}`, {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          callback(data);
          // Auto-select if only one option and trigger change event
          if (data.results && data.results.length === 1) {
            const singleOption = data.results[0];
            this.setValue(singleOption[this.settings.valueField], true);
            element.dispatchEvent(new Event("change", { bubbles: true }));
          }
        })
        .catch(() => {
          callback();
        });
    },
    placeholder: element.getAttribute("placeholder") || "",
    plugins: [],
  };

  return {
    ...heavyConfig,
    ...tomSelectConfig,
    load: heavyConfig.load,
  };
}
