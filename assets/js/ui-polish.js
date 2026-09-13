(() => {
  "use strict";

  const mobileMedia = window.matchMedia("(max-width: 63.999rem)");

  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === "function") {
      return window.CSS.escape(String(value));
    }
    return String(value).replace(/["\\]/g, "\\$&");
  }

  /* -----------------------------------------------------------------------
     Expansion toggles
     ----------------------------------------------------------------------- */

  function getExpansionButtons(expansion) {
    return Array.from(
      document.querySelectorAll(
        `.expansion-toggle[data-expansion="${cssEscape(expansion)}"]`
      )
    );
  }

  function forceHideExpansionHeaders(expansion) {
    document
      .querySelectorAll(
        `.index-divider[data-expansion="${cssEscape(expansion)}"]`
      )
      .forEach(header => {
        header.dataset.expansionForcedHidden = "true";
        header.style.setProperty("display", "none", "important");
      });
  }

  function releaseExpansionHeaders(expansion) {
    document
      .querySelectorAll(
        `.index-divider[data-expansion="${cssEscape(expansion)}"]`
      )
      .forEach(header => {
        if (header.dataset.expansionForcedHidden === "true") {
          delete header.dataset.expansionForcedHidden;
          header.style.removeProperty("display");
        }
      });
  }

  function syncExpansion(expansion) {
    if (!expansion) return;

    const buttons = getExpansionButtons(expansion);
    if (!buttons.length) return;

    const disabled = buttons.some(button =>
      button.classList.contains("inactive")
    );

    buttons.forEach(button => {
      button.classList.toggle("inactive", disabled);
      button.classList.toggle("active", !disabled);
      button.setAttribute("aria-pressed", String(!disabled));
      button.setAttribute(
        "title",
        `${button.getAttribute("aria-label") || expansion}: ${
          disabled ? "ausgeblendet" : "angezeigt"
        }`
      );
    });

    if (disabled) {
      forceHideExpansionHeaders(expansion);
    } else {
      releaseExpansionHeaders(expansion);

      // Let the normal guide filter decide which re-enabled headers actually
      // have visible results.
      if (typeof window.runGuideFilter === "function") {
        window.runGuideFilter();
      }
    }
  }

  function syncAllExpansions() {
    const seen = new Set();

    document.querySelectorAll(".expansion-toggle[data-expansion]").forEach(button => {
      const expansion = button.dataset.expansion;
      if (!expansion || seen.has(expansion)) return;
      seen.add(expansion);
      syncExpansion(expansion);
    });
  }

  document.addEventListener("click", event => {
    const button = event.target.closest(".expansion-toggle[data-expansion]");
    if (!button) return;

    /*
     * app.js owns the actual enabled/disabled toggle. Wait until its bubbling
     * handler has finished, then synchronize visuals and header visibility.
     */
    requestAnimationFrame(() => syncExpansion(button.dataset.expansion));
  });

  /* -----------------------------------------------------------------------
     Mobile sidebar
     ----------------------------------------------------------------------- */

  const trigger = document.querySelector(".sidebar__trigger");
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.querySelector(".site-grid__sidebar-overlay");

  function syncMenuState() {
    if (!trigger || !sidebar) return;

    const open = sidebar.classList.contains("active");

    trigger.classList.toggle("active", open);
    trigger.setAttribute("aria-expanded", String(open));

    if (overlay) {
      overlay.classList.toggle("active", open);
      overlay.setAttribute("aria-hidden", String(!open));
    }

    if (mobileMedia.matches) {
      document.body.classList.toggle("mobile-nav-open", open);
    } else {
      document.body.classList.remove("mobile-nav-open");
    }
  }

  function closeMobileMenu() {
    if (!trigger || !sidebar) return;

    trigger.classList.remove("active");
    sidebar.classList.remove("active");

    if (overlay) {
      overlay.classList.remove("active");
      overlay.setAttribute("aria-hidden", "true");
    }

    trigger.setAttribute("aria-expanded", "false");
    document.body.classList.remove("mobile-nav-open");

    // app.js uses inline overflow while opening the menu.
    document.body.style.removeProperty("overflow-y");
  }

  if (trigger) {
    trigger.addEventListener("click", () => {
      requestAnimationFrame(syncMenuState);
    });
  }

  if (overlay) {
    overlay.addEventListener("click", () => {
      requestAnimationFrame(syncMenuState);
    });
  }

  document.addEventListener("keydown", event => {
    if (
      event.key === "Escape" &&
      mobileMedia.matches &&
      sidebar?.classList.contains("active")
    ) {
      closeMobileMenu();
      trigger?.focus();
    }
  });

  /*
   * On mobile, selecting an actual destination should behave like a native
   * navigation drawer: close immediately and reveal the destination.
   * Disclosure buttons remain open.
   */
  document.addEventListener("click", event => {
    if (!mobileMedia.matches) return;

    const link = event.target.closest(
      ".sidebar a.xiv-nav-item, .sidebar__title a"
    );

    if (link) {
      closeMobileMenu();
    }
  });

  const handleMediaChange = () => {
    if (!mobileMedia.matches) {
      closeMobileMenu();
    } else {
      syncMenuState();
    }
  };

  if (typeof mobileMedia.addEventListener === "function") {
    mobileMedia.addEventListener("change", handleMediaChange);
  } else {
    mobileMedia.addListener(handleMediaChange);
  }

  /* Initial state after all legacy scripts have loaded. */
  syncAllExpansions();
  syncMenuState();
})();
