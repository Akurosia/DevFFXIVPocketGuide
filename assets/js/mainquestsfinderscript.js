let quests = {};
// Load saved quest from localStorage
if (localStorage.getItem('savedQuest')) {
    document.getElementById("questSearch").value = localStorage.getItem('savedQuest').trim();
}
// Load JSON file and filter relevant quests
fetch('/assets/sorted_quests_aku.json')
    .then(response => response.json())
    .then(data => {
        quests = data;
        searchQuest();
    })
    .catch(error => console.error('Fehler beim Laden der Quest-Daten:', error));

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
    const breakpoin1 = {
        // current patch                        patches first quest
        "2.0 A Realm Reborn":                   "Willkommen in Gridania",
        "2.1 A Realm Awoken":                   "Zu neuen Ufern",
        "2.2 Through the Maelstrom":            "Ein neuer Morgen",
        "2.3 Defenders of Eorzea":              "Das Leid der Heimatlosen",
        "2.4 Dreams of Ice":                    "Im Netz des Webers",
        "2.5 Before the Fall":                  "Drei mächtige Säulen",
        "3.0 Heavensward":                      "Zu neuem Glanz",
        "3.1 As Goes Light, So Goes Darkness":  "Wahrheit tut weh",
        "3.2 The Gears of Change":              "Fast wie früher",
        "3.3 Revenge of the Horde":             "Zwei Seelen in einem Körper",
        "3.4 Soul Surrender":                   "Eine wohlverdiente Mahlzeit",
        "3.5 The Far Edge of Fate":             "Nachricht aus Gyr Abania",
        "4.0 Stormblood":                       "Über den Wall",
        "4.1 The Legend Returns":               "Ein neues Abenteuer",
        "4.2 Rise of a new Sun":                "Eilmeldung aus Kugane",
        "4.3 Under the Moonlight":              "Sinneswandel",
        "4.4 Prelude in Violet":                "Eine erste Spur",
        "4.5 A Requiem for Heroes":             "Den Seelen auf der Spur",
        "5.0 Shadowbringers":                   "Von Sendern und Sendungen",
        "5.1 Vows of Virtue, Deeds of Cruelty": "Ein Flackern in der Seele",
        "5.2 Echoes of a fallen Star":          "Eine Warnung für die Allianz",
        "5.3 Reflections in Crystal":           "Sage der Krieger des Lichts",
        "5.4 Futures Rewritten":                "Hohe Ziele",
        "5.5 Death Unto Dawn":                  "Silberharnisch",
        "6.0 Endwalker":                        "Aufbruch zu neuen Horizonten",
        "6.1 Newfound Adventure":               "Neu entdecktes Abenteuer",
        "6.2 Buried Memory":                    "Auf den Spuren von Azdaja",
        "6.3 Gods Revel, Lands Tremble":        "Ruf aus dem Nichts",
        "6.4 The Dark Throne":                  "Die Würze Radz-at-Hans",
        "6.5 Growing Light":                    "Das Licht im Dunkel",
        "7.0 Dawntrail":                        "Unbegrenzte Möglichkeiten",
        "7.1 Crossroads":                       "Auf Geheiß Alexandrias",
        "7.2 Seekers of Eternity":              "Glanz der Vergangenheit"
    };
    const breakpoint2 = {
        "2.0 A Realm Reborn":                   "Willkommen in Gridania",
        "3.0 Heavensward":                      "Zu neuem Glanz",
        "4.0 Stormblood":                       "Über den Wall",
        "5.0 Shadowbringers":                   "Von Sendern und Sendungen",
        "6.0 Endwalker":                        "Aufbruch zu neuen Horizonten",
        "7.0 Dawntrail":                        "Unbegrenzte Möglichkeiten"
    };
    const breakpoints = breakpoin1

    let sections = [];
    let lastIndex = 0;
    Object.entries(breakpoints).forEach(([label, questName], i, arr) => {
        let currentIndex = quests.findIndex(q => q.Name === questName);
        let nextEntry = arr[i + 1];
        let nextIndex = nextEntry ? quests.findIndex(q => q.Name === nextEntry[1]) : total;

        if (currentIndex === -1 || (nextEntry && nextIndex === -1)) return;

        let totalInSection = nextIndex - currentIndex;
        let doneInSection = Math.max(0, Math.min(completed, nextIndex) - currentIndex);
        let progressPercentage = Math.max(0, Math.min(100, (doneInSection / totalInSection) * 100));

        let sectionQuests = quests.slice(currentIndex, nextIndex)
            .map((q, index) =>
                `<option value="${q.Name}">${index + 1}. ${q.Name} (${index + currentIndex + 1})</option>`
            )
            .join('');

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
    });


    progressDiv.innerHTML += `<div class="progress-container">${sections.join('')}</div>`;
}
