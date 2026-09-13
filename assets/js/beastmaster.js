(() => {
    "use strict";

    const list = document.getElementById("beastmaster-list");
    if (!list) return;

    const root = list.closest(".beastmaster-captures");
    const search = document.getElementById("beastmaster-search");
    const missing = document.getElementById("beastmaster-missing");
    const count = document.getElementById("beastmaster-count");
    const storageMessage = document.getElementById("beastmaster-storage");
    const empty = document.getElementById("beastmaster-empty");
    const entries = Array.from(list.querySelectorAll(".beastmaster-entry"));

    const key = "ffxiv-pocketguide-beastmaster-caught-v1";
    let caught = new Set();

    try {
        const saved = JSON.parse(localStorage.getItem(key) || "[]");
        if (Array.isArray(saved)) caught = new Set(saved.map(String));
    } catch (_) {
        if (storageMessage) storageMessage.hidden = false;
    }

    const normalize = value =>
        String(value || "").normalize("NFKC").toLocaleLowerCase("de");

    const searchable = new Map(
        entries.map(entry => [
            entry,
            normalize(
                Array.from(
                    entry.querySelectorAll(
                        "[data-beast-search], .beastmaster-abilities .Names"
                    )
                )
                    .map(part => part.textContent)
                    .join(" ")
            )
        ])
    );

    function setAccordionState(trigger, content, open) {
        if (!trigger || !content) return;

        trigger.setAttribute("aria-expanded", open ? "true" : "false");
        trigger.classList.toggle("active", open);
        content.hidden = !open;
        content.classList.toggle("active", open);
    }

    function bindAccordion(trigger, content) {
        if (!trigger || !content || trigger.dataset.beastAccordionBound === "true") {
            return;
        }

        trigger.dataset.beastAccordionBound = "true";

        if (!trigger.hasAttribute("role")) trigger.setAttribute("role", "button");
        if (!trigger.hasAttribute("tabindex")) trigger.setAttribute("tabindex", "0");

        // Respect the markup's initial state.
        const initiallyOpen =
            trigger.getAttribute("aria-expanded") === "true" ||
            trigger.classList.contains("active") ||
            content.classList.contains("active");

        setAccordionState(trigger, content, initiallyOpen);

        const toggle = event => {
            // A click on a control inside a trigger should not toggle the row.
            if (
                event.target.closest(
                    "a, button:not(.guide__entry-trigger--beast), input, select, textarea, label"
                ) &&
                event.target !== trigger
            ) {
                return;
            }

            const open = trigger.getAttribute("aria-expanded") === "true";
            setAccordionState(trigger, content, !open);
        };

        trigger.addEventListener("click", toggle);
        trigger.addEventListener("keydown", event => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                toggle(event);
            }
        });
    }

    // Whole "Bestien zum Fangen" section.
    if (root) {
        const sectionTrigger = root.querySelector(
            ":scope > .guide__accordion-trigger--01-grid"
        );
        const sectionContent = root.querySelector(
            ":scope > .beastmaster-captures__content"
        );

        if (sectionTrigger && sectionContent) {
            sectionTrigger.setAttribute("aria-expanded", "true");
            bindAccordion(sectionTrigger, sectionContent);
        }
    }

    // Individual beasts.
    entries.forEach(entry => {
        const trigger = entry.querySelector(
            ":scope > .guide__entry-trigger--beast"
        );
        const content = entry.querySelector(
            ":scope > .guide__entry-content--beast"
        );

        if (trigger && content) {
            trigger.setAttribute("aria-expanded", "false");
            trigger.classList.remove("active");
            content.classList.remove("active");
            content.hidden = true;
            bindAccordion(trigger, content);
        }

        const checkbox = entry.querySelector("[data-beast-caught]");
        if (!checkbox) return;

        checkbox.checked = caught.has(entry.dataset.beastNumber);

        checkbox.addEventListener("change", () => {
            if (checkbox.checked) caught.add(entry.dataset.beastNumber);
            else caught.delete(entry.dataset.beastNumber);

            try {
                localStorage.setItem(key, JSON.stringify([...caught]));
            } catch (_) {
                if (storageMessage) storageMessage.hidden = false;
            }

            filter();
        });
    });

    function filter() {
        const terms = normalize(search?.value)
            .trim()
            .split(/\s+/)
            .filter(Boolean);

        let visible = 0;

        entries.forEach(entry => {
            const isCaught = caught.has(entry.dataset.beastNumber);
            const matchesSearch = terms.every(term =>
                searchable.get(entry).includes(term)
            );

            entry.hidden =
                (!!missing?.checked && isCaught) || !matchesSearch;

            if (!entry.hidden) visible++;
        });

        const totalCaught = entries.filter(entry =>
            caught.has(entry.dataset.beastNumber)
        ).length;

        if (count) {
            count.textContent =
                `${visible} von ${entries.length} Bestien · ${totalCaught} gefangen`;
        }

        if (empty) empty.hidden = visible !== 0;
    }

    search?.addEventListener("input", filter);
    missing?.addEventListener("change", filter);

    filter();
})();
