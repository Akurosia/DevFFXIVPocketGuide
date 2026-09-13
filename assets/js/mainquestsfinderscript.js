let quests = [];

const MAINQUEST_BREAKPOINTS = [
    ["2.0 A Realm Reborn", "Willkommen in Gridania"],
    ["2.1 A Realm Awoken", "Zu neuen Ufern"],
    ["2.2 Through the Maelstrom", "Ein neuer Morgen"],
    ["2.3 Defenders of Eorzea", "Das Leid der Heimatlosen"],
    ["2.4 Dreams of Ice", "Im Netz des Webers"],
    ["2.5 Before the Fall", "Drei mächtige Säulen"],
    ["3.0 Heavensward", "Zu neuem Glanz"],
    ["3.1 As Goes Light, So Goes Darkness", "Wahrheit tut weh"],
    ["3.2 The Gears of Change", "Fast wie früher"],
    ["3.3 Revenge of the Horde", "Zwei Seelen in einem Körper"],
    ["3.4 Soul Surrender", "Eine wohlverdiente Mahlzeit"],
    ["3.5 The Far Edge of Fate", "Nachricht aus Gyr Abania"],
    ["4.0 Stormblood", "Über den Wall"],
    ["4.1 The Legend Returns", "Ein neues Abenteuer"],
    ["4.2 Rise of a new Sun", "Eilmeldung aus Kugane"],
    ["4.3 Under the Moonlight", "Sinneswandel"],
    ["4.4 Prelude in Violet", "Eine erste Spur"],
    ["4.5 A Requiem for Heroes", "Den Seelen auf der Spur"],
    ["5.0 Shadowbringers", "Von Sendern und Sendungen"],
    ["5.1 Vows of Virtue, Deeds of Cruelty", "Ein Flackern in der Seele"],
    ["5.2 Echoes of a fallen Star", "Eine Warnung für die Allianz"],
    ["5.3 Reflections in Crystal", "Sage der Krieger des Lichts"],
    ["5.4 Futures Rewritten", "Hohe Ziele"],
    ["5.5 Death Unto Dawn", "Silberharnisch"],
    ["6.0 Endwalker", "Aufbruch zu neuen Horizonten"],
    ["6.1 Newfound Adventure", "Neu entdecktes Abenteuer"],
    ["6.2 Buried Memory", "Auf den Spuren von Azdaja"],
    ["6.3 Gods Revel, Lands Tremble", "Ruf aus dem Nichts"],
    ["6.4 The Dark Throne", "Die Würze Radz-at-Hans"],
    ["6.5 Growing Light", "Das Licht im Dunkel"],
    ["7.0 Dawntrail", "Unbegrenzte Möglichkeiten"],
    ["7.1 Crossroads", "Auf Geheiß Alexandrias"],
    ["7.2 Seekers of Eternity", "Glanz der Vergangenheit"],
    ["7.3 The Promose of Tomorrow", "Endlose Dunkelheit"],
    ["7.4 Into the Mist", "Der Kompassnadel nach"],
    ["7.5 Trail to the Heavens", "Auf den Spuren des Schicksals"]
];

const EXPANSION_ACCENT_MAP = {
    '2': '#c16b5a',
    '3': '#7cb2de',
    '4': '#c95858',
    '5': '#8a63c3',
    '6': '#b5c48a',
    '7': '#d7b566'
};

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function getQuestInput() {
    return document.getElementById('questSearch');
}

function getProgressRoot() {
    return document.getElementById('progress');
}

function findQuestIndex(query) {
    const trimmedQuery = String(query || '').trim();
    if (!trimmedQuery) {
        return -1;
    }

    const numericQuery = Number(trimmedQuery);
    if (Number.isInteger(numericQuery) && numericQuery >= 0 && numericQuery < quests.length) {
        return numericQuery;
    }

    const lowerQuery = trimmedQuery.toLowerCase();

    let exactIndex = quests.findIndex(q => String(q.Name || '').toLowerCase() === lowerQuery);
    if (exactIndex !== -1) {
        return exactIndex;
    }

    return quests.findIndex(q => String(q.Name || '').toLowerCase().includes(lowerQuery));
}

function getExpansionAccent(label) {
    return EXPANSION_ACCENT_MAP[String(label).trim().charAt(0)] || '#d6ad59';
}

function renderState(message, type = 'info') {
    const progressDiv = getProgressRoot();
    progressDiv.innerHTML = `
        <div class="mainquest-state mainquest-state--${type}">
            <p class="mainquest-state__text">${escapeHtml(message)}</p>
        </div>
    `;
}

function buildSectionOptions(sectionQuests, baseIndex) {
    return sectionQuests
        .map((quest, index) => `
            <option value="${escapeHtml(quest.Name)}">
                ${index + 1}. ${escapeHtml(quest.Name)} (#${baseIndex + index})
            </option>
        `)
        .join('');
}

function getSectionStatus(done, total) {
    if (done <= 0) {
        return 'Noch nicht begonnen';
    }
    if (done >= total) {
        return 'Abgeschlossen';
    }
    return 'Aktiver Fortschritt';
}

function getSectionStatusClass(done, total, active) {
    if (active) {
        return 'is-active';
    }
    if (done >= total) {
        return 'is-complete';
    }
    if (done > 0) {
        return 'is-progress';
    }
    return 'is-empty';
}

function applySectionQuest(selectId) {
    const select = document.getElementById(selectId);
    const input = getQuestInput();
    if (!select || !input || !select.value) {
        return;
    }

    input.value = select.value;
    searchQuest();
}
window.applySectionQuest = applySectionQuest;

function renderOverview(questIndex) {
    const completedQuests = questIndex + 1;
    const totalQuests = quests.length;
    const remainingQuests = Math.max(0, totalQuests - completedQuests);
    const progressPercentage = Math.max(0, Math.min(100, (completedQuests / totalQuests) * 100));

    const currentSectionIndex = MAINQUEST_BREAKPOINTS.reduce((lastIndex, [, questName], index) => {
        const breakpointQuestIndex = quests.findIndex(q => q.Name === questName);
        if (breakpointQuestIndex !== -1 && breakpointQuestIndex <= questIndex) {
            return index;
        }
        return lastIndex;
    }, 0);

    const currentSectionLabel = MAINQUEST_BREAKPOINTS[currentSectionIndex]?.[0] || 'Unbekannter Abschnitt';

    return `
        <section class="mainquest-overview xiv-card-body">
            <div class="mainquest-overview__header">
                <div class="mainquest-overview__copy">
                    <p class="mainquest-overview__eyebrow">Gefundene Quest</p>
                    <h3 class="mainquest-overview__title">${escapeHtml(quests[questIndex].Name)}</h3>
                    <p class="mainquest-overview__subtitle">Aktueller Abschnitt: <strong>${escapeHtml(currentSectionLabel)}</strong></p>
                </div>
                <div class="mainquest-overview__badge">${completedQuests} / ${totalQuests}</div>
            </div>

            <div class="mainquest-overview__stats">
                <article class="mainquest-stat xiv-card-body">
                    <span class="mainquest-stat__label">Abgeschlossen</span>
                    <strong class="mainquest-stat__value">${completedQuests}</strong>
                </article>
                <article class="mainquest-stat xiv-card-body">
                    <span class="mainquest-stat__label">Verbleibend</span>
                    <strong class="mainquest-stat__value">${remainingQuests}</strong>
                </article>
                <article class="mainquest-stat xiv-card-body">
                    <span class="mainquest-stat__label">Fortschritt</span>
                    <strong class="mainquest-stat__value">${progressPercentage.toFixed(1)}%</strong>
                </article>
            </div>

            <div class="progress-bar-container progress-bar-container--overview">
                <div class="progress-bar mainquest-progress-bar">
                    <div class="progress-fill" style="width:${progressPercentage}%; background:${getExpansionAccent(currentSectionLabel)};"></div>
                </div>
            </div>
        </section>
    `;
}

function renderProgressSections(questIndex) {
    const totalQuests = quests.length;
    const sections = [];

    MAINQUEST_BREAKPOINTS.forEach(([label, questName], index) => {
        const currentIndex = quests.findIndex(q => q.Name === questName);
        const nextBreakpoint = MAINQUEST_BREAKPOINTS[index + 1];
        const nextIndex = nextBreakpoint
            ? quests.findIndex(q => q.Name === nextBreakpoint[1])
            : totalQuests;

        if (currentIndex === -1 || nextIndex === -1 || nextIndex <= currentIndex) {
            return;
        }

        const totalInSection = nextIndex - currentIndex;
        const doneInSection = Math.max(0, Math.min(questIndex + 1, nextIndex) - currentIndex);
        const progressPercentage = Math.max(0, Math.min(100, (doneInSection / totalInSection) * 100));
        const sectionQuests = quests.slice(currentIndex, nextIndex);
        const selectId = `mqf-section-${index}`;
        const active = questIndex >= currentIndex && questIndex < nextIndex;
        const accent = getExpansionAccent(label);
        const statusClass = getSectionStatusClass(doneInSection, totalInSection, active);
        const statusLabel = getSectionStatus(doneInSection, totalInSection);
        const startQuest = sectionQuests[0]?.Name || questName;
        const endQuest = sectionQuests[sectionQuests.length - 1]?.Name || questName;

        sections.push(`
            <article class="mainquest-journey-step ${statusClass}" style="--mq-accent:${accent}; --mq-step:${index + 1};">
                <div class="mainquest-journey-step__rail" aria-hidden="true">
                    <span class="mainquest-journey-step__dot"></span>
                </div>

                <div class="mainquest-journey-step__body xiv-card-body">
                    <div class="mainquest-journey-step__top">
                        <div class="mainquest-section__copy">
                            <p class="mainquest-section__eyebrow">Main Scenario</p>
                            <h4 class="mainquest-section__title">${escapeHtml(label)}</h4>
                            <p class="mainquest-journey-step__range">${escapeHtml(startQuest)} → ${escapeHtml(endQuest)}</p>
                        </div>
                        <div class="mainquest-section__meta">
                            <span class="mainquest-section__status">${statusLabel}</span>
                            <strong class="mainquest-section__count">${doneInSection} / ${totalInSection}</strong>
                        </div>
                    </div>

                    <div class="progress-bar-container">
                        <div class="progress-bar mainquest-progress-bar">
                            <div class="progress-fill" style="width:${progressPercentage}%; background:${accent};"></div>
                        </div>
                    </div>

                    <div class="mainquest-journey-step__footer">
                        <div class="mainquest-journey-step__summary">
                            <span class="mainquest-journey-step__summary-label">Aktuelle Auswahl</span>
                            <strong class="mainquest-journey-step__summary-value">${active ? escapeHtml(quests[questIndex].Name) : (doneInSection > 0 ? escapeHtml(endQuest) : 'Noch keine Quest gewählt')}</strong>
                        </div>
                        <div class="mainquest-section__footer">
                            <label class="mainquest-section__label" for="${selectId}">Questliste</label>
                            <div class="mainquest-section__controls">
                                <select id="${selectId}" class="quest-dropdown xiv-select">
                                    <option value="">Quest auswählen</option>
                                    ${buildSectionOptions(sectionQuests, currentIndex + 1)}
                                </select>
                                <button type="button" class="xiv-button xiv-button--small" onclick="applySectionQuest('${selectId}')">Übernehmen</button>
                            </div>
                        </div>
                    </div>
                </div>
            </article>
        `);
    });

    return `
        <section class="mainquest-sections-block">
            <div class="mainquest-sections-block__header">
                <div>
                    <p class="mainquest-search-panel__eyebrow">Abschnitte</p>
                    <h3 class="mainquest-sections-block__title">Fortschritt nach Patch und Erweiterung</h3>
                    <p class="mainquest-search-panel__text">Die Abschnitte sind jetzt als durchgehender Quest-Pfad angeordnet, damit der Fortschritt klarer von oben nach unten lesbar ist.</p>
                </div>
            </div>
            <div class="mainquest-journey">
                ${sections.join('')}
            </div>
        </section>
    `;
}

function searchQuest() {
    const query = getQuestInput()?.value.trim() || '';

    if (!Array.isArray(quests) || quests.length === 0) {
        renderState('Quest-Daten werden noch geladen …');
        return;
    }

    if (!query) {
        renderState('Bitte eine Quest-ID oder einen Namen eingeben.', 'warning');
        return;
    }

    const questIndex = findQuestIndex(query);
    if (questIndex === -1) {
        renderState('Quest nicht gefunden.', 'warning');
        return;
    }

    localStorage.setItem('savedQuest', quests[questIndex].Name);
    getProgressRoot().innerHTML = `${renderOverview(questIndex)}${renderProgressSections(questIndex)}`;
}
window.searchQuest = searchQuest;

function initialiseMainquestFinder() {
    const savedQuest = localStorage.getItem('savedQuest');
    if (savedQuest && getQuestInput()) {
        getQuestInput().value = savedQuest.trim();
    }

    renderState('Quest-Daten werden geladen …');

    fetch('/assets/sorted_quests_aku.json')
        .then(response => response.json())
        .then(data => {
            quests = Array.isArray(data) ? data : [];
            searchQuest();
        })
        .catch(error => {
            console.error('Fehler beim Laden der Quest-Daten:', error);
            renderState('Quest-Daten konnten nicht geladen werden.', 'error');
        });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialiseMainquestFinder);
} else {
    initialiseMainquestFinder();
}
