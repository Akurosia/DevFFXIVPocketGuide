  (() => {
    const STORAGE_KEY = "guideAccordionState:v1";
    const IDS = ["guideBosse", "guideAdds", "guideMap"]; // add more ids here later

    const readState = () => {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return {};
        const obj = JSON.parse(raw);
        return obj && typeof obj === "object" ? obj : {};
      } catch {
        return {};
      }
    };
    const findContentForTrigger = (triggerEl) => {
      // expects the content to be the next element sibling (as in your markup)
      let el = triggerEl.nextElementSibling;
      while (el && !(el.classList && el.classList.contains("guide__accordion-content--01-grid"))) el = el.nextElementSibling;
      return el || null;
    };
    const writeState = (state) => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      } catch {}
    };

    const init = () => {
      const stored = readState();

      for (const id of IDS) {
        const triggerEl = document.getElementById(id);
        if (!triggerEl) continue;
        const contentEl = findContentForTrigger(triggerEl);

        if (stored[id] !== undefined){
            if (stored[id]) {
              triggerEl.classList.add("active");
              if (contentEl) contentEl.classList.add("active");
            } else {
              triggerEl.classList.remove("active");
              if (contentEl) contentEl.classList.remove("active");
            }
        }
        // keep storage in sync with user interaction
        triggerEl.addEventListener("click", () => {
          const next = triggerEl.classList.contains("active");

          const nextState = readState();
          nextState[id] = next; // true/false
          writeState(nextState);
        });
      }
    };

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
  })();
