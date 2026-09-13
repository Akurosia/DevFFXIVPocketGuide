(function () {
  function norm(value) {
    return String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }

  function initCopyButtons(root) {
    root.querySelectorAll("[data-copy-value]").forEach((button) => {
      button.addEventListener("click", async () => {
        const value = button.dataset.copyValue || "";
        if (!value) return;
        try {
          await navigator.clipboard.writeText(value);
          const original = button.textContent;
          button.textContent = "Kopiert";
          setTimeout(() => button.textContent = original, 1200);
        } catch (error) {
          console.error(error);
        }
      });
    });
  }

  function initDalamud(root) {
    const items = Array.from(root.querySelectorAll("[data-resource-item]"));
    const search = root.querySelector("[data-resource-search]");
    const status = root.querySelector("[data-dalamud-status]");
    const sort = root.querySelector("[data-resource-sort]");
    const reset = root.querySelector("[data-resource-reset]");
    const grid = root.querySelector("[data-resource-grid]");
    const empty = root.querySelector("[data-resource-empty]");
    const visibleEl = root.querySelector("[data-resource-visible]");
    const totalEl = root.querySelector("[data-resource-total]");
    const context = root.querySelector("[data-resource-context]");

    if (totalEl) totalEl.textContent = items.length;

    function apply() {
      const q = norm(search?.value);
      const statusValue = status?.value || "";
      let visible = 0;

      items.forEach((item) => {
        const matchesSearch = !q || norm(item.dataset.resourceSearch).includes(q);
        let matchesStatus = true;

        if (statusValue === "official") matchesStatus = item.dataset.official === "true" && item.dataset.outdated !== "true";
        if (statusValue === "community") matchesStatus = item.dataset.official !== "true" && item.dataset.outdated !== "true";
        if (statusValue === "outdated") matchesStatus = item.dataset.outdated === "true";

        const show = matchesSearch && matchesStatus;
        item.hidden = !show;
        if (show) visible++;
      });

      const visibleItems = items.filter(item => !item.hidden);
      const sortMode = sort?.value || "name";
      visibleItems.sort((a, b) => {
        if (sortMode === "api-desc") return (+b.dataset.apiLevel || 0) - (+a.dataset.apiLevel || 0);
        if (sortMode === "api-asc") return (+a.dataset.apiLevel || 0) - (+b.dataset.apiLevel || 0);
        return (a.dataset.resourceName || "").localeCompare(b.dataset.resourceName || "", undefined, { sensitivity: "base" });
      }).forEach(item => grid.appendChild(item));

      if (visibleEl) visibleEl.textContent = visible;
      if (empty) empty.hidden = visible !== 0;

      if (context) {
        const labels = [];
        if (statusValue) labels.push(status?.selectedOptions[0]?.textContent || statusValue);
        if (q) labels.push(`Suche: "${search.value.trim()}"`);
        context.textContent = labels.length ? labels.join(" · ") : "Alle Plugins";
      }
    }

    search?.addEventListener("input", apply);
    status?.addEventListener("change", apply);
    sort?.addEventListener("change", apply);

    root.querySelectorAll("[data-resource-tag]").forEach(tag => {
      tag.addEventListener("click", () => {
        if (search) search.value = tag.dataset.resourceTag || "";
        apply();
      });
    });

    reset?.addEventListener("click", () => {
      if (search) search.value = "";
      if (status) status.value = "";
      if (sort) sort.value = "name";
      apply();
    });

    initCopyButtons(root);
    apply();
  }

  function initLinks(root) {
    const items = Array.from(root.querySelectorAll("[data-resource-item]"));
    const sections = Array.from(root.querySelectorAll("[data-link-section]"));
    const categories = Array.from(root.querySelectorAll("[data-link-category]"));
    const search = root.querySelector("[data-resource-search]");
    const sort = root.querySelector("[data-resource-sort]");
    const reset = root.querySelector("[data-resource-reset]");
    const empty = root.querySelector("[data-resource-empty]");
    const visibleEl = root.querySelector("[data-resource-visible]");
    const totalEl = root.querySelector("[data-resource-total]");
    const sidebarTotal = root.querySelector("[data-link-total]");
    const context = root.querySelector("[data-resource-context]");

    let activeCategory = "";
    if (totalEl) totalEl.textContent = items.length;
    if (sidebarTotal) sidebarTotal.textContent = items.length;

    function apply() {
      const q = norm(search?.value);
      let visible = 0;

      items.forEach((item) => {
        const cat = item.dataset.linkCategoryValue || "";
        const show = (!activeCategory || cat === activeCategory) &&
                     (!q || norm(item.dataset.resourceSearch).includes(q));
        item.hidden = !show;
        if (show) visible++;
      });

      sections.forEach(section => {
        const visibleCards = Array.from(section.querySelectorAll("[data-resource-item]")).filter(item => !item.hidden);
        section.hidden = visibleCards.length === 0;

        if (sort?.value === "name") {
          const grid = section.querySelector(".links-grid");
          visibleCards.sort((a, b) =>
            (a.dataset.resourceName || "").localeCompare(b.dataset.resourceName || "", undefined, { sensitivity: "base" })
          ).forEach(item => grid.appendChild(item));
        }
      });

      if (visibleEl) visibleEl.textContent = visible;
      if (empty) empty.hidden = visible !== 0;
      if (context) {
        const labels = [];
        if (activeCategory) labels.push(activeCategory);
        if (q) labels.push(`Suche: "${search.value.trim()}"`);
        context.textContent = labels.length ? labels.join(" · ") : "Alle Kategorien";
      }

      categories.forEach(button => {
        button.classList.toggle("is-active", (button.dataset.linkCategory || "") === activeCategory);
      });
    }

    categories.forEach(button => {
      button.addEventListener("click", () => {
        activeCategory = button.dataset.linkCategory || "";
        apply();
      });
    });

    search?.addEventListener("input", apply);
    sort?.addEventListener("change", apply);

    reset?.addEventListener("click", () => {
      activeCategory = "";
      if (search) search.value = "";
      if (sort) sort.value = "default";
      apply();
    });

    apply();
  }

  document.querySelectorAll("[data-resource-browser]").forEach(root => {
    if (root.dataset.resourceBrowser === "dalamud") initDalamud(root);
    if (root.dataset.resourceBrowser === "links") initLinks(root);
  });
})();
