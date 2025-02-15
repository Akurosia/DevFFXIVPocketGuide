let quests = {};
// Load saved quest from localStorage
if (localStorage.getItem('savedQuest')) {
    document.getElementById("questSearch").value = localStorage.getItem('savedQuest').trim();
}
// Load JSON file and filter relevant quests
fetch('/assets/quests_aku.json')
    .then(response => response.json())
    .then(data => {
        quests = Object.fromEntries(
            Object.entries(data).filter(([_, quest]) =>
                quest.JournalGenre?.Icon === "ui/icon/071000/071201_hr1.webp"
            )
        );
        sortQuests();
        searchQuest();
    })
    .catch(error => console.error('Fehler beim Laden der Quest-Daten:', error));

function sortQuests() {
    let orderedQuests = [];
    let questMap = new Map(Object.entries(quests));
    let startQuestId = "65575";
    let startQuest = questMap.get(startQuestId);

    if (!startQuest) {
        console.error('Start-Quest nicht gefunden.');
        return;
    }

    let visited = new Set();
    let queue = [startQuestId];

    while (queue.length > 0) {
        let currentId = queue.shift();
        let currentQuest = questMap.get(currentId);
        if (!currentQuest || visited.has(currentId)) continue;

        visited.add(currentId);
        orderedQuests.push(currentQuest);

        if (currentQuest.NextQuest) {
            queue.push(...currentQuest.NextQuest.filter(id => questMap.has(id)));
        }
    }

    quests = orderedQuests;

    const selectElement = document.getElementById("test");
    quests.forEach(item => {
        let option = document.createElement("option");
        option.textContent = item.Name;
        option.value = item.Name;
        selectElement.appendChild(option);
    });
}

function searchQuest() {
    const query = document.getElementById('questSearch').value.trim();
    const progressDiv = document.getElementById('progress');
    progressDiv.innerHTML = '';

    if (!query) {
        progressDiv.innerHTML = '<p>Bitte eine Quest-ID oder einen Namen eingeben.</p>';
        return;
    }

    let questIndex = quests.findIndex(q => q.Name === query || query in quests);
    if (questIndex === -1) {
        progressDiv.innerHTML = '<p>Quest nicht gefunden.</p>';
        return;
    }

    let completedQuests = questIndex + 1;
    let remainingQuests = quests.length - completedQuests;

    let progressPercentage = Math.max(0, Math.min(100, (completedQuests / quests.length) * 100));
    progressDiv.innerHTML = `<p>Gefundene Quest: <strong>${quests[questIndex].Name}</strong></p>`;
    progressDiv.innerHTML += `
            <div class="progress-container">
                <div class="progress-section-container">
                    <span class="progress-label">Overview (${completedQuests}/${quests.length})</span>
                    <div class="progress-bar-container">
                        <div class="progress-bar">
                            <div class="progress-fill arealmreborn" style="width: ${progressPercentage}%;"></div>
                        </div>
                    </div>
                </div>
            </div>
    `
    //progressDiv.innerHTML += `<p>Abgeschlossene Quests: ${completedQuests}</p>`;
    //progressDiv.innerHTML += `<p>Verbleibende Quests: ${remainingQuests}</p>`;

    localStorage.setItem('savedQuest', quests[questIndex].Name);
    renderProgressBar(completedQuests, quests.length);
}

function renderProgressBar(completed, total) {
    const progressDiv = document.getElementById('progress');
    const searchInput = document.getElementById('search-input');
    const breakpoin1 = {
        "2.0 A Realm Reborn":                   "Zu neuen Ufern",
        "2.1 A Realm Awoken":                   "Ein neuer Morgen",
        "2.2 Through the Maelstrom":            "Das Leid der Heimatlosen",
        "2.3 Defenders of Eorzea":              "Im Netz des Webers",
        "2.4 Dreams of Ice":                    "Drei mächtige Säulen",
        "2.5 Before the Fall":                  "Zu neuem Glanz",
        "3.0 Heavensward":                      "Wahrheit tut weh",
        "3.1 As Goes Light, So Goes Darkness":  "Fast wie früher",
        "3.2 The Gears of Change":              "Zwei Seelen in einem Körper",
        "3.3 Revenge of the Horde":             "Eine wohlverdiente Mahlzeit",
        "3.4 Soul Surrender":                   "Nachricht aus Gyr Abania",
        "3.5 The Far Edge of Fate":             "Über den Wall",
        "4.0 Stormblood":                       "Ein neues Abenteuer",
        "4.1 The Legend Returns":               "Eilmeldung aus Kugane",
        "4.2 Rise of a new Sun":                "Sinneswandel",
        "4.3 Under the Moonlight":              "Eine erste Spur",
        "4.4 Prelude in Violet":                "Den Seelen auf der Spur",
        "4.5 A Requiem for Heroes":             "Von Sendern und Sendungen",
        "5.0 Shadowbringers":                   "Ein Flackern in der Seele",
        "5.1 Vows of Virtue, Deeds of Cruelty": "Eine Warnung für die Allianz",
        "5.2 Echoes of a fallen Star":          "Sage der Krieger des Lichts",
        "5.3 Reflections in Crystal":           "Hohe Ziele",
        "5.4 Futures Rewritten":                "Silberharnisch",
        "5.5 Death Unto Dawn":                  "Aufbruch zu neuen Horizonten",
        "6.0 Endwalker":                        "Neu entdecktes Abenteuer",
        "6.1 Newfound Adventure":               "Auf den Spuren von Azdaja",
        "6.2 Buried Memory":                    "Ruf aus dem Nichts",
        "6.3 Gods Revel, Lands Tremble":        "Die Würze Radz-at-Hans",
        "6.4 The Dark Throne":                  "Das Licht im Dunkel",
        "6.5 Growing Light":                    "Unbegrenzte Möglichkeiten",
        "7.0 Dawntrail":                        "Auf Geheiß Alexandrias",
        "7.1 Crossroads":                       quests[quests.findIndex(q => q.Name === "Auf Geheiß Alexandrias") + 1]?.Name || ""
    };
    const breakpoint2 = {
        "2.0 A Realm Reborn":                   "Zu neuem Glanz",
        "3.0 Heavensward":                      "Über den Wall",
        "4.0 Stormblood":                       "Von Sendern und Sendungen",
        "5.0 Shadowbringers":                   "Aufbruch zu neuen Horizonten",
        "6.0 Endwalker":                        "Unbegrenzte Möglichkeiten",
        "7.0 Dawntrail":                        quests[quests.findIndex(q => q.Name === "Auf Geheiß Alexandrias") + 1]?.Name || ""
    };
    const breakpoints = breakpoin1

    let sections = [];
    let lastIndex = 0;
    Object.entries(breakpoints).forEach(([label, questName], i, arr) => {
        let currentIndex = quests.findIndex(q => q.Name === questName);
        if (currentIndex === -1) return;

        let totalInSection = (i === arr.length - 1) ? (total - lastIndex) : (currentIndex - lastIndex);
        let doneInSection = Math.max(0, Math.min(completed, currentIndex) - lastIndex);
        let progressPercentage = Math.max(0, Math.min(100, (doneInSection / totalInSection) * 100));

        let sectionQuests = quests.slice(lastIndex, currentIndex).map(q => `<option value="${q.Name}">${q.Name}</option>`).join('');

        sections.push(`
            <div class="progress-section-container">
                <span class="progress-label">${label} (${doneInSection}/${totalInSection})</span>
                <div class="progress-bar-container">
                    <div class="progress-bar">
                        <div class="progress-fill ${label.replaceAll(" ", "").slice(3).toLowerCase()}" style="width: ${progressPercentage}%;"></div>
                    </div>
                </div>
                <select class="quest-dropdown" onchange="document.getElementById('questSearch').value = this.value;">
                    <option value="">Wähle eine Quest</option>
                    ${sectionQuests}
                </select>
            </div>
        `);

        lastIndex = currentIndex;
    });

    progressDiv.innerHTML += `<div class="progress-container">${sections.join('')}</div>`;
}
