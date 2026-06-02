(function () {
    const stateKey = "ffxiv_bestiarium_state";
    const app = document.getElementById("bestiariumApp");
    if (!app) {
        return;
    }

    const ui = {
        loading: document.getElementById("bestiariumLoading"),
        error: document.getElementById("bestiariumError"),
        content: document.getElementById("bestiariumContent"),
        categoryGrid: document.getElementById("bestiariumCategoryGrid"),
        rankList: document.getElementById("bestiariumRankList"),
        title: document.getElementById("bestiariumTitle"),
        entryCount: document.getElementById("bestiariumEntryCount"),
        targetCount: document.getElementById("bestiariumTargetCount"),
        rewardTotal: document.getElementById("bestiariumRewardTotal"),
        showAll: document.getElementById("bestiariumShowAll"),
        toolbarHint: document.getElementById("bestiariumToolbarHint"),
        notes: document.getElementById("bestiariumNotes")
    };

    const config = {
        gameAssetsUrl: (app.dataset.gameAssetsUrl || "").replace(/\/$/, "")
    };

    const state = {
        categories: [],
        selectedCategory: null,
        selectedRank: null
    };

    function saveState() {
        localStorage.setItem(stateKey, JSON.stringify({
            selectedCategory: state.selectedCategory,
            selectedRank: state.selectedRank
        }));
    }

    function restoreState() {
        try {
            const raw = localStorage.getItem(stateKey);
            if (!raw) {
                return;
            }
            const parsed = JSON.parse(raw);
            state.selectedCategory = parsed.selectedCategory || null;
            state.selectedRank = parsed.selectedRank || null;
        } catch (error) {
            console.error(error);
        }
    }

    function createElement(tag, className, text) {
        const element = document.createElement(tag);
        if (className) {
            element.className = className;
        }
        if (text !== undefined) {
            element.textContent = text;
        }
        return element;
    }

    function toIconUrl(path) {
        const normalizedPath = String(path || "").replace(/^\/+/, "");
        if (!normalizedPath) {
            return "";
        }
        return `${config.gameAssetsUrl}/${normalizedPath}`;
    }

    function getSelectedCategory() {
        return state.categories.find((category) => category.name === state.selectedCategory) || state.categories[0];
    }

    function getVisibleEntries(category) {
        if (!category) {
            return [];
        }
        if (!state.selectedRank) {
            return category.entries;
        }
        return category.entries.filter((entry) => entry.rank === state.selectedRank);
    }

    function renderCategories() {
        ui.categoryGrid.innerHTML = "";

        state.categories.forEach((category) => {
            const button = createElement("button", "bestiarium-category-button");
            button.type = "button";
            button.title = category.name;
            if (category.name === state.selectedCategory) {
                button.classList.add("is-active");
            }

            const image = document.createElement("img");
            image.loading = "lazy";
            image.src = toIconUrl(category.icon);
            image.alt = category.name;
            button.appendChild(image);

            button.appendChild(createElement("span", "", category.label || category.name));
            button.addEventListener("click", () => {
                state.selectedCategory = category.name;
                state.selectedRank = 1;
                saveState();
                render();
            });

            ui.categoryGrid.appendChild(button);
        });
    }

    function renderRanks(category) {
        ui.rankList.innerHTML = "";

        category.ranks.forEach((rankInfo) => {
            const button = createElement("button", "bestiarium-rank-button");
            button.type = "button";
            if (rankInfo.rank === state.selectedRank) {
                button.classList.add("is-active");
            }

            button.appendChild(createElement("span", "", `Rang ${rankInfo.rank}`));
            button.appendChild(createElement("small", "", `${rankInfo.count} Einträge`));
            button.addEventListener("click", () => {
                state.selectedRank = rankInfo.rank === state.selectedRank ? null : rankInfo.rank;
                saveState();
                render();
            });
            ui.rankList.appendChild(button);
        });
    }

    function renderHeader(category, visibleEntries) {
        ui.title.textContent = category.name;
        ui.entryCount.textContent = `${visibleEntries.length}/${category.entries.length}`;
        ui.targetCount.textContent = `${visibleEntries.reduce((sum, entry) => sum + entry.targets.length, 0)}/${category.total_targets}`;
        ui.rewardTotal.textContent = visibleEntries.reduce((sum, entry) => sum + entry.reward, 0).toLocaleString("de-DE");
        ui.toolbarHint.textContent = state.selectedRank
            ? `Gefiltert auf Rang ${state.selectedRank}`
            : "Alle verfügbaren Einträge dieser Kategorie";
        ui.showAll.classList.toggle("is-active", !state.selectedRank);
    }

    function renderNotes(entries) {
        ui.notes.innerHTML = "";

        entries.forEach((entry) => {
            const card = createElement("article", "bestiarium-note");

            const head = createElement("div", "bestiarium-note__head");
            head.appendChild(createElement("div", "bestiarium-note__title", entry.name));
            head.appendChild(createElement("div", "bestiarium-note__reward", `Vergütung ${entry.reward.toLocaleString("de-DE")}`));
            card.appendChild(head);

            const body = createElement("div", "bestiarium-note__body");
            entry.targets.forEach((target) => {
                const targetRow = createElement("div", "bestiarium-target");

                const targetIcon = document.createElement("img");
                targetIcon.className = "bestiarium-target__icon";
                targetIcon.loading = "lazy";
                targetIcon.alt = target.name;
                targetIcon.src = toIconUrl(target.icon || "/000000/000000_hr1.webp");
                targetRow.appendChild(targetIcon);

                const text = createElement("div", "bestiarium-target__text");
                text.appendChild(createElement("div", "bestiarium-target__name", target.name));
                const locationParts = [target.zone, target.location, target.town_name].filter(Boolean);
                text.appendChild(createElement("div", "bestiarium-target__location", locationParts.join(" | ")));
                targetRow.appendChild(text);

                const count = createElement("div", "bestiarium-target__count");
                count.appendChild(createElement("strong", "", `${target.count}/${target.count}`));
                count.appendChild(createElement("span", "", "Benötigt"));
                targetRow.appendChild(count);

                body.appendChild(targetRow);
            });

            const footer = createElement("div", "bestiarium-note__footer");
            footer.appendChild(createElement("div", "", `Rang ${entry.rank}`));
            footer.appendChild(createElement("div", "", `${entry.target_total} Abschüsse insgesamt`));
            body.appendChild(footer);

            card.appendChild(body);
            ui.notes.appendChild(card);
        });
    }

    function render() {
        const category = getSelectedCategory();
        if (!category) {
            return;
        }

        renderCategories();
        renderRanks(category);

        const visibleEntries = getVisibleEntries(category);
        renderHeader(category, visibleEntries);
        renderNotes(visibleEntries);

        ui.loading.hidden = true;
        ui.error.hidden = true;
        ui.content.hidden = false;
    }

    function setLoadingState() {
        ui.loading.hidden = false;
        ui.error.hidden = true;
        ui.content.hidden = true;
    }

    function setErrorState() {
        ui.loading.hidden = true;
        ui.error.hidden = false;
        ui.content.hidden = true;
    }

    ui.showAll.addEventListener("click", () => {
        state.selectedRank = null;
        saveState();
        render();
    });

    function init() {
        setLoadingState();
        restoreState();

        try {
            const dataElement = document.getElementById("bestiariumData");
            if (!dataElement) {
                throw new Error("Bestiary data element is missing.");
            }

            const categories = JSON.parse(dataElement.textContent || "[]");
            if (!categories.length) {
                throw new Error("No bestiary categories found.");
            }

            state.categories = categories.sort((left, right) => (left.order || 0) - (right.order || 0));
            if (!state.selectedCategory || !state.categories.some((category) => category.name === state.selectedCategory)) {
                state.selectedCategory = state.categories[0].name;
            }

            const selectedCategory = getSelectedCategory();
            if (!state.selectedRank) {
                state.selectedRank = 1;
            }
            if (!selectedCategory.ranks.some((rankInfo) => rankInfo.rank === state.selectedRank)) {
                state.selectedRank = selectedCategory.ranks.length ? selectedCategory.ranks[0].rank : 1;
            }

            render();
        } catch (error) {
            console.error(error);
            setErrorState();
        }
    }

    init();
}());
