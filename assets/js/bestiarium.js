(function () {
    const selectionKey = "ffxiv_bestiarium_state_v2";
    const progressKey = "ffxiv_bestiarium_progress_v2";
    const app = document.getElementById("bestiariumApp");
    if (!app) return;

    const ui = {
        loading: document.getElementById("bestiariumLoading"),
        error: document.getElementById("bestiariumError"),
        content: document.getElementById("bestiariumContent"),
        categoryGrid: document.getElementById("bestiariumCategoryGrid"),
        rankList: document.getElementById("bestiariumRankList"),
        title: document.getElementById("bestiariumTitle"),
        classIcon: document.getElementById("bestiariumClassIcon"),
        completedTotal: document.getElementById("bestiariumCompletedTotal"),
        rankTitle: document.getElementById("bestiariumRankTitle"),
        rankStatus: document.getElementById("bestiariumRankStatus"),
        rankReward: document.getElementById("bestiariumRankReward"),
        showAll: document.getElementById("bestiariumShowAll"),
        completeRank: document.getElementById("bestiariumCompleteRank"),
        resetProgress: document.getElementById("bestiariumResetProgress"),
        toolbarHint: document.getElementById("bestiariumToolbarHint"),
        notes: document.getElementById("bestiariumNotes")
    };

    const config = {
        gameAssetsUrl: (app.dataset.gameAssetsUrl || "").replace(/\/$/, "")
    };

    const state = {
        categories: [],
        selectedCategory: null,
        selectedRank: 1,
        progress: {}
    };

    function createElement(tag, className, text) {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (text !== undefined) element.textContent = text;
        return element;
    }

    function toIconUrl(path) {
        const normalizedPath = String(path || "").replace(/^\/+/, "");
        return normalizedPath ? `${config.gameAssetsUrl}/${normalizedPath}` : "";
    }

    function loadState() {
        try {
            const selection = JSON.parse(localStorage.getItem(selectionKey) || "{}");
            const progress = JSON.parse(localStorage.getItem(progressKey) || "{}");
            state.selectedCategory = selection.selectedCategory || null;
            state.selectedRank = selection.selectedRank === null ? null : (selection.selectedRank || 1);
            state.progress = progress && typeof progress === "object" ? progress : {};
        } catch (error) {
            console.warn("Bestiarium state could not be restored", error);
        }
    }

    function saveSelection() {
        localStorage.setItem(selectionKey, JSON.stringify({
            selectedCategory: state.selectedCategory,
            selectedRank: state.selectedRank
        }));
    }

    function saveProgress() {
        localStorage.setItem(progressKey, JSON.stringify(state.progress));
    }

    function getCategory() {
        return state.categories.find(category => category.name === state.selectedCategory) || state.categories[0];
    }

    function targetKey(category, entry, target) {
        return `${category.name}:${entry.id}:${target.id}`;
    }

    function getTargetProgress(category, entry, target) {
        const stored = Number(state.progress[targetKey(category, entry, target)] || 0);
        return Math.max(0, Math.min(target.count, stored));
    }

    function setTargetProgress(category, entry, target, value) {
        const next = Math.max(0, Math.min(target.count, Number(value) || 0));
        const key = targetKey(category, entry, target);
        if (next === 0) delete state.progress[key];
        else state.progress[key] = next;
        saveProgress();
    }

    function isTargetComplete(category, entry, target) {
        return getTargetProgress(category, entry, target) >= target.count;
    }

    function isEntryComplete(category, entry) {
        return entry.targets.length > 0 && entry.targets.every(target => isTargetComplete(category, entry, target));
    }

    function rankEntries(category, rank) {
        return category.entries.filter(entry => entry.rank === rank);
    }

    function completedEntries(category, entries) {
        return entries.filter(entry => isEntryComplete(category, entry)).length;
    }

    function rankReward(category, rank) {
        return rankEntries(category, rank).reduce((sum, entry) => sum + Number(entry.reward || 0), 0);
    }

    function renderCategories() {
        const category = getCategory();
        ui.categoryGrid.innerHTML = "";

        state.categories.forEach(item => {
            const button = createElement("button", "bestiarium-category-button");
            button.type = "button";
            button.title = item.label || item.name;
            button.setAttribute("aria-label", item.label || item.name);
            button.classList.toggle("is-active", item.name === category.name);

            const image = document.createElement("img");
            image.loading = "lazy";
            image.src = toIconUrl(item.icon);
            image.alt = "";
            button.appendChild(image);

            button.addEventListener("click", () => {
                state.selectedCategory = item.name;
                state.selectedRank = item.ranks.length ? item.ranks[0].rank : null;
                saveSelection();
                render();
            });

            ui.categoryGrid.appendChild(button);
        });
    }

    function renderRanks(category) {
        ui.rankList.innerHTML = "";

        category.ranks.forEach(rankInfo => {
            const entries = rankEntries(category, rankInfo.rank);
            const completed = completedEntries(category, entries);
            const button = createElement("button", "bestiarium-rank-button");
            button.type = "button";
            button.classList.toggle("is-active", rankInfo.rank === state.selectedRank);
            button.classList.toggle("is-complete", entries.length > 0 && completed === entries.length);

            const rankNumber = createElement("span", "bestiarium-rank-button__number", String(rankInfo.rank));
            const rankProgress = createElement("span", "bestiarium-rank-button__progress", `${completed}/${entries.length}`);
            const check = createElement("span", "bestiarium-rank-button__check", entries.length > 0 && completed === entries.length ? "✓" : "");

            button.append(rankNumber, check, rankProgress);
            button.addEventListener("click", () => {
                state.selectedRank = rankInfo.rank;
                saveSelection();
                render();
            });
            ui.rankList.appendChild(button);
        });
    }

    function renderHeader(category) {
        const allCompleted = completedEntries(category, category.entries);
        ui.title.textContent = category.label || category.name;
        ui.classIcon.src = toIconUrl(category.icon);
        ui.classIcon.alt = category.label || category.name;
        ui.completedTotal.textContent = `${allCompleted}/${category.entries.length}`;

        if (state.selectedRank === null) {
            ui.rankTitle.textContent = "Alle Ränge";
            ui.rankReward.textContent = Number(category.total_reward || category.entries.reduce((s, e) => s + Number(e.reward || 0), 0)).toLocaleString("de-DE");
            ui.rankStatus.textContent = `${allCompleted}/${category.entries.length}`;
            ui.toolbarHint.textContent = "Alle Einträge dieser Klasse";
            ui.completeRank.disabled = true;
        } else {
            const entries = rankEntries(category, state.selectedRank);
            const completed = completedEntries(category, entries);
            ui.rankTitle.textContent = `Rang ${state.selectedRank}`;
            ui.rankReward.textContent = rankReward(category, state.selectedRank).toLocaleString("de-DE");
            ui.rankStatus.textContent = `${completed}/${entries.length}`;
            ui.toolbarHint.textContent = `Rang ${state.selectedRank} · ${entries.length} Einträge`;
            ui.completeRank.disabled = false;
        }

        ui.showAll.classList.toggle("is-active", state.selectedRank === null);
    }

    function renderTarget(category, entry, target) {
        const current = getTargetProgress(category, entry, target);
        const complete = current >= target.count;
        const row = createElement("div", "bestiarium-target");
        row.classList.toggle("is-complete", complete);

        const check = createElement("button", "bestiarium-target__check", complete ? "✓" : "");
        check.type = "button";
        check.title = complete ? "Fortschritt zurücksetzen" : "Als abgeschlossen markieren";
        check.setAttribute("aria-label", check.title);
        check.addEventListener("click", () => {
            setTargetProgress(category, entry, target, complete ? 0 : target.count);
            render();
        });

        const icon = document.createElement("img");
        icon.className = "bestiarium-target__icon";
        icon.loading = "lazy";
        icon.alt = target.name;
        icon.src = toIconUrl(target.icon || "/000000/000000_hr1.webp");

        const text = createElement("div", "bestiarium-target__text");
        text.appendChild(createElement("div", "bestiarium-target__name", target.name));
        const locationParts = [target.zone, target.location, target.town_name].filter(Boolean);
        text.appendChild(createElement("div", "bestiarium-target__location", locationParts.join(" / ")));

        const progress = createElement("div", "bestiarium-target__progress");
        const countLine = createElement("div", "bestiarium-target__count-line");
        const minus = createElement("button", "bestiarium-target__step", "−");
        minus.type = "button";
        minus.disabled = current <= 0;
        minus.addEventListener("click", () => {
            setTargetProgress(category, entry, target, current - 1);
            render();
        });
        const count = createElement("strong", "bestiarium-target__count", `${current}/${target.count}`);
        const plus = createElement("button", "bestiarium-target__step", "+");
        plus.type = "button";
        plus.disabled = current >= target.count;
        plus.addEventListener("click", () => {
            setTargetProgress(category, entry, target, current + 1);
            render();
        });
        countLine.append(minus, count, plus);

        const bar = createElement("div", "bestiarium-target__bar");
        const fill = createElement("span", "bestiarium-target__bar-fill");
        fill.style.width = `${target.count ? (current / target.count) * 100 : 0}%`;
        bar.appendChild(fill);
        progress.append(countLine, bar);

        row.append(check, icon, text, progress);
        return row;
    }

    function renderEntry(category, entry) {
        const complete = isEntryComplete(category, entry);
        const card = createElement("article", "bestiarium-note");
        card.classList.toggle("is-complete", complete);

        const head = createElement("header", "bestiarium-note__head");
        const title = createElement("strong", "bestiarium-note__title", entry.name);
        const status = createElement("span", "bestiarium-note__status", complete ? "ERLEDIGT!" : "");
        head.append(title, status);
        card.appendChild(head);

        const body = createElement("div", "bestiarium-note__body");
        entry.targets.forEach(target => body.appendChild(renderTarget(category, entry, target)));
        card.appendChild(body);

        const footer = createElement("footer", "bestiarium-note__footer");
        footer.appendChild(createElement("span", "bestiarium-note__footer-label", "Vergütung"));
        footer.appendChild(createElement("strong", "bestiarium-note__reward", Number(entry.reward || 0).toLocaleString("de-DE")));
        card.appendChild(footer);

        return card;
    }

    function renderNotes(category) {
        ui.notes.innerHTML = "";
        const ranks = state.selectedRank === null ? category.ranks.map(r => r.rank) : [state.selectedRank];

        ranks.forEach(rank => {
            const entries = rankEntries(category, rank);
            if (!entries.length) return;

            if (state.selectedRank === null) {
                const group = createElement("section", "bestiarium-rank-group");
                const head = createElement("div", "bestiarium-rank-group__header");
                head.appendChild(createElement("strong", "", `Rang ${rank}`));
                head.appendChild(createElement("span", "", `${completedEntries(category, entries)}/${entries.length}`));
                group.appendChild(head);
                const list = createElement("div", "bestiarium-rank-group__entries");
                entries.forEach(entry => list.appendChild(renderEntry(category, entry)));
                group.appendChild(list);
                ui.notes.appendChild(group);
            } else {
                entries.forEach(entry => ui.notes.appendChild(renderEntry(category, entry)));
            }
        });
    }

    function render() {
        const category = getCategory();
        if (!category) return;
        renderCategories();
        renderRanks(category);
        renderHeader(category);
        renderNotes(category);
        ui.loading.hidden = true;
        ui.error.hidden = true;
        ui.content.hidden = false;
    }

    function completeSelectedRank() {
        const category = getCategory();
        if (!category || state.selectedRank === null) return;
        rankEntries(category, state.selectedRank).forEach(entry => {
            entry.targets.forEach(target => setTargetProgress(category, entry, target, target.count));
        });
        render();
    }

    ui.showAll.addEventListener("click", () => {
        state.selectedRank = null;
        saveSelection();
        render();
    });

    ui.completeRank.addEventListener("click", completeSelectedRank);

    ui.resetProgress.addEventListener("click", () => {
        if (!window.confirm("Bestiarium-Fortschritt wirklich zurücksetzen?")) return;
        state.progress = {};
        saveProgress();
        render();
    });

    function init() {
        ui.loading.hidden = false;
        ui.error.hidden = true;
        ui.content.hidden = true;
        loadState();

        try {
            const dataElement = document.getElementById("bestiariumData");
            if (!dataElement) throw new Error("Bestiary data element is missing.");
            const categories = JSON.parse(dataElement.textContent || "[]");
            if (!categories.length) throw new Error("No bestiary categories found.");

            state.categories = categories.sort((a, b) => (a.order || 0) - (b.order || 0));
            if (!state.selectedCategory || !state.categories.some(c => c.name === state.selectedCategory)) {
                state.selectedCategory = state.categories[0].name;
            }

            const category = getCategory();
            if (state.selectedRank !== null && !category.ranks.some(r => r.rank === state.selectedRank)) {
                state.selectedRank = category.ranks.length ? category.ranks[0].rank : null;
            }

            render();
        } catch (error) {
            console.error(error);
            ui.loading.hidden = true;
            ui.error.hidden = false;
        }
    }

    init();
}());
