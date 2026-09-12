(() => {
    "use strict";
    const list = document.getElementById("beastmaster-list");
    if (!list) return;
    const search = document.getElementById("beastmaster-search");
    const missing = document.getElementById("beastmaster-missing");
    const count = document.getElementById("beastmaster-count");
    const storageMessage = document.getElementById("beastmaster-storage");
    const entries = Array.from(list.querySelectorAll(".beastmaster-entry"));
    const key = "ffxiv-pocketguide-beastmaster-caught-v1";
    let caught = new Set();
    try {
        const saved = JSON.parse(localStorage.getItem(key) || "[]");
        if (Array.isArray(saved)) caught = new Set(saved.map(String));
    } catch (_) { storageMessage.hidden = false; }
    const normalize = value => value.normalize("NFKC").toLocaleLowerCase("de");
    const searchable = new Map(entries.map(entry => [entry, normalize(
        Array.from(entry.querySelectorAll("[data-beast-search], .beastmaster-abilities .Names")).map(part => part.textContent).join(" ")
    )]));
    function filter() {
        const terms = normalize(search.value).trim().split(/\s+/).filter(Boolean);
        let visible = 0;
        entries.forEach(entry => {
            entry.hidden = (missing.checked && caught.has(entry.dataset.beastNumber)) ||
                !terms.every(term => searchable.get(entry).includes(term));
            if (!entry.hidden) visible++;
        });
        const totalCaught = entries.filter(entry => caught.has(entry.dataset.beastNumber)).length;
        count.textContent = `${visible} von ${entries.length} Bestien · ${totalCaught} gefangen`;
        document.getElementById("beastmaster-empty").hidden = visible !== 0;
    }
    entries.forEach(entry => {
        const checkbox = entry.querySelector("[data-beast-caught]");
        checkbox.checked = caught.has(entry.dataset.beastNumber);
        checkbox.addEventListener("change", () => {
            if (checkbox.checked) caught.add(entry.dataset.beastNumber);
            else caught.delete(entry.dataset.beastNumber);
            try { localStorage.setItem(key, JSON.stringify([...caught])); }
            catch (_) { storageMessage.hidden = false; }
            filter();
        });
    });
    search.addEventListener("input", filter);
    missing.addEventListener("change", filter);
    filter();
})();
