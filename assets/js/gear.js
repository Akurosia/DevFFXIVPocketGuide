const minilvl = 650
const maxilvl = 800
const minlvl = 90
const maxlvl = 100

weapon_dict = {
    "PLD": ["Hauptwaffe der Gladiatoren"],
    "KRG": ["Hauptwaffe der Marodeure"],
    "DKR": ["Hauptwaffe der Dunkelritter"],
    "REV": ["Hauptwaffe der Revolverklingen"],
    "WMA": ["Druiden-Waffe", "Druiden-Zweihandwaffe"],
    "GLT": ["Hauptwaffe der Gelehrten"],
    "AST": ["Hauptwaffe der Astrologen"],
    "WEI": ["Hauptwaffe der Weisen"],
    "MÖN": ["Hauptwaffe der Faustk\u00e4mpfer"],
    "DRG": ["Hauptwaffe der Pikeniere"],
    "NIN": ["Hauptwaffe der Schurken"],
    "SAM": ["Hauptwaffe der Samurai"],
    "SNT": ["Hauptwaffe der Schnitter"],
    "VPR": ["Hauptwaffe der Vipern"],
    "BRD": ["Hauptwaffe der Waldl\u00e4ufer"],
    "MCH": ["Hauptwaffe der Maschinisten"],
    "TÄN": ["Hauptwaffe der T\u00e4nzer"],
    "BSW": ["Grimoire"],
    "SMA": ["Thaumaturgen-Waffe", "Thaumaturgen-Zweihandwaffe"],
    "RMA": ["Hauptwaffe der Rotmagier"],
    "BMA": ["Blaumagier-Waffe"],
    "PKT": ["Hauptwaffe der Piktomanten"],
    "ZMR": ["Zimmermannszeug"],
    "GRS": ["Schmiedezeug"],
    "PLA": ["Plattnerzeug"],
    "GLD": ["Goldschmiedezeug"],
    "GER": ["Gerberzeug"],
    "WEB": ["Weberzeug"],
    "ALC": ["Alchemistenzeug"],
    "GRM": ["Gourmetzeug"],
    "MIN": ["Minenarbeiterzeug"],
    "GÄR": ["Gärtnerzeug"],
    "FIS": ["Fischerzeug"]
}

class_additions = {
    "PLD": "Krieger",
    "KRG": "Krieger",
    "DKR": "Krieger",
    "REV": "Krieger",
    "WMA": "Magier",
    "GLT": "Magier",
    "AST": "Magier",
    "WEI": "Magier",
    "MÖN": "Krieger",
    "DRG": "Krieger",
    "NIN": "Krieger",
    "SAM": "Krieger",
    "SNT": "Krieger",
    "VPR": "Krieger",
    "BRD": "Krieger",
    "MCH": "Krieger",
    "TÄN": "Krieger",
    "BSW": "Magier",
    "SMA": "Magier",
    "RMA": "Magier",
    "BMA": "Magier",
    "PKT": "Magier",
    "ZMR": "Handwerker",
    "GRS": "Handwerker",
    "PLA": "Handwerker",
    "GLD": "Handwerker",
    "GER": "Handwerker",
    "WEB": "Handwerker",
    "ALC": "Handwerker",
    "GRM": "Handwerker",
    "MIN": "Sammler",
    "GÄR": "Sammler",
    "FIS": "Sammler",
}

tools_dict = {
    "PLD": "Schild",
    "ZMR": "Zimmermannszeug (sekund\u00e4r)",
    "GRS": "Schmiedezeug (sekund\u00e4r)",
    "PLA": "Plattnerzeug (sekund\u00e4r)",
    "GLD": "Goldschmiedezeug (sekund\u00e4r)",
    "GER": "Gerberzeug (sekund\u00e4r)",
    "WEB": "Weberzeug (sekund\u00e4r)",
    "ALC": "Alchemistenzeug (sekund\u00e4r)",
    "GRM": "Gourmetzeug (sekund\u00e4r)",
    "MIN": "Minenarbeiterzeug (sekund\u00e4r)",
    "GÄR": "Gärtnerzeug (sekund\u00e4r)",
    "FIS": "Fischerzeug (sekund\u00e4r)"
}

mainstats = [
    "Phys. Basiswert",
    "Mag. Basiswert",
    "Verteidigung",
    "Magieabwehr",
    "Stärke",
    "Intelligenz",
    "Willenskraft",
    "Geschick",
    "Konstitution",
    "Unbeugsamkeit"
]

substats = [
    "Direkter Treffer",
    "Kritischer Treffer",
    "Entschlossenheit",
    "Schnelligkeit",
    "Frömmigkeit",
    "Zaubertempo",
    "Kunstfertigkeit",
    "Kontrolle",
    "HP",
    "Sammelgeschick",
    "Expertise",
    "SP"
]

sum_fields = {}

lists = ["Mainhand", "Offhand", "Kopf", "Rumpf", "Hände", "Beine", "Füße", "Ohrring", "Halskette", "Armreif", "Ring", "Ring"]

function copy2clipboard(text) {
    if (!navigator.clipboard) {
        fallbackCopyTextToClipboard(text);
        return;
    }
    navigator.clipboard.writeText(text).then(function() {
    }, function(err) {
        console.error('Async: Could not copy text: ', err);
    });
}

function remove_gearlist(){
    const summary = document.getElementById("gear-result-summary");
    if (summary) summary.textContent = "Lade …";

    document.getElementById("weapon_left").innerHTML = "";
    document.getElementById("weapon_right").innerHTML = "";
    document.getElementById("kopf").innerHTML = "";
    document.getElementById("rumpf").innerHTML = "";
    document.getElementById("hände").innerHTML = "";
    document.getElementById("beine").innerHTML = "";
    document.getElementById("füße").innerHTML = "";
    document.getElementById("ohrring").innerHTML = "";
    document.getElementById("halskette").innerHTML = "";
    document.getElementById("armreif").innerHTML = "";
    document.getElementById("ring_links").innerHTML = "";
    document.getElementById("ring_rechts").innerHTML = "";
}

async function call_api_data(){
    sum_fields = {};
    ringcounter = 1;

    const classjob_select = document.getElementById("classjob");
    const classjob = classjob_select.options[classjob_select.selectedIndex].value;
    const lvl_from = document.getElementById("lvl_from").value;
    const lvl_to = document.getElementById("lvl_to").value;
    const ilvl_from = document.getElementById("ilvl_from").value;
    const ilvl_to = document.getElementById("ilvl_to").value;
    const include_hq = document.getElementById("include_hq").checked;
    const limit_to_hq = document.getElementById("limit_to_hq").checked;

    const rarity = [];
    if (document.getElementById("rarity_0").checked) rarity.push("1");
    if (document.getElementById("rarity_7").checked) rarity.push("7");
    if (document.getElementById("rarity_2").checked) rarity.push("2");
    if (document.getElementById("rarity_3").checked) rarity.push("3");
    if (document.getElementById("rarity_4").checked) rarity.push("4");

    const fields = get_stats_for_class(classjob);

    fields.forEach(field => {
        sum_fields[field] = 0;
    });

    await createSummaryTable(fields);

    set_localstorage();
    remove_gearlist();

    const requests = [];

    lists.forEach(category => {
        let table_name = category;

        if (category === "Mainhand"){
            table_name = weapon_dict[classjob];
        } else if (category === "Offhand"){
            table_name = tools_dict[classjob];

            // Jobs such as Dancer, Bard, etc. do not have an offhand slot.
            // Do not query the backend with category=Offhand because that endpoint
            // responds with HTTP 500 for unsupported categories.
            if (table_name === undefined){
                const target = document.getElementById("weapon_right");
                if (target) target.innerHTML = "";
                return;
            }
        }

        const params = new URLSearchParams();
        params.set("classjob", classjob);
        params.set("classjobadd", class_additions[classjob] || "");
        params.set(
            "category",
            String(table_name)
                .replaceAll(" (", "_")
                .replaceAll(")", "")
                .replaceAll("-", "_")
                .replaceAll(" ", "_")
        );
        params.set("lvl_from", lvl_from);
        params.set("lvl_to", lvl_to);
        params.set("ilvl_from", ilvl_from);
        params.set("ilvl_to", ilvl_to);
        params.set("rarity", rarity.join(","));

        if (include_hq && limit_to_hq){
            params.set("hq", "1");
        } else if (include_hq){
            params.set("hq", "0,1");
        } else {
            params.set("hq", "0");
        }

        requests.push(
            load_data("?" + params.toString(), table_name, category, classjob, fields)
        );
    });

    await Promise.allSettled(requests);

    updateGearResultSummary();

    if (typeof executeHandelingLanguages === "function"){
        executeHandelingLanguages();
        setTimeout(() => executeHandelingLanguages(), 700);
    }
}

async function load_data(params, table_name, category, classJob, fields){
    const url = "https://ffxiv.akurosiakamo.de/queryFFXIVequipmentDB.php" + params;

    try {
        const response = await fetch(url);
        const body = await response.text();

        if (!response.ok){
            throw new Error(
                `Gear API ${response.status} for ${category}: ${body.slice(0, 180)}`
            );
        }

        let data;
        try {
            data = JSON.parse(body);
        } catch (error) {
            throw new Error(
                `Gear API returned invalid JSON for ${category}: ${body.slice(0, 180)}`
            );
        }

        if (data === null || typeof data !== "object"){
            data = [];
        }

        await create_table(data, table_name, category, classJob, fields);
    } catch (error) {
        console.error(error);
        renderGearSlotError(category, error);
    }
}

function renderGearSlotError(category, error){
    let target = null;

    if (category === "Mainhand"){
        target = document.getElementById("weapon_left");
    } else if (category === "Offhand"){
        target = document.getElementById("weapon_right");
    } else if (category === "Ring"){
        // Ring requests are duplicated; don't guess which one failed.
        return;
    } else {
        target = document.getElementById(String(category).toLowerCase());
    }

    if (!target) return;

    target.innerHTML = "";

    const panel = document.createElement("div");
    panel.className = "xiv-notice xiv-notice--warning gear-slot__error";

    const title = document.createElement("strong");
    title.textContent = `${gearDisplayName(category)} konnte nicht geladen werden`;

    const detail = document.createElement("span");
    detail.textContent = error?.message || "Unbekannter Fehler";

    panel.append(title, detail);
    target.appendChild(panel);
}

function get(object, key, default_value) {
    if (typeof object === "undefined"){
        return default_value
    }
    var result = object[key];
    return (typeof result !== "undefined") ? result : default_value;
}


function get_stats_for_class(classJob, removeshy=true){
    let stats = [];

    if (["BSW","SMA","RMA","BMA","PKT"].includes(classJob)){
        stats = [
            "Mag. Basiswert",
            "Magieabwehr",
            "Intelligenz",
            "Kritischer Treffer",
            "Direkter Treffer",
            "Entschlossenheit",
            "Zaubertempo",
            "Konstitution"
        ];
    } else if (["WMA","GLT","AST","WEI"].includes(classJob)){
        stats = [
            "Mag. Basiswert",
            "Magieabwehr",
            "Willenskraft",
            "Frömmigkeit",
            "Kritischer Treffer",
            "Direkter Treffer",
            "Entschlossenheit",
            "Zaubertempo",
            "Konstitution"
        ];
    } else if (["ZMR","GRS","PLA","GLD","GER","WEB","ALC","GRM"].includes(classJob)){
        stats = ["Kunstfertigkeit", "Kontrolle", "HP", "Konstitution"];
    } else if (["MIN","GÄR","FIS"].includes(classJob)){
        stats = ["Sammelgeschick", "Expertise", "SP", "Konstitution"];
    } else if (["PLD","KRG","DKR","REV"].includes(classJob)){
        stats = [
            "Phys. Basiswert",
            "Verteidigung",
            "Stärke",
            "Kritischer Treffer",
            "Direkter Treffer",
            "Entschlossenheit",
            "Schnelligkeit",
            "Unbeugsamkeit",
            "Konstitution"
        ];
    } else if (["NIN","BRD","MCH","TÄN"].includes(classJob)){
        stats = [
            "Phys. Basiswert",
            "Verteidigung",
            "Geschick",
            "Kritischer Treffer",
            "Direkter Treffer",
            "Entschlossenheit",
            "Schnelligkeit",
            "Konstitution"
        ];
    } else if (["MÖN","DRG","SAM","SNT","VPR"].includes(classJob)){
        stats = [
            "Phys. Basiswert",
            "Verteidigung",
            "Stärke",
            "Kritischer Treffer",
            "Direkter Treffer",
            "Entschlossenheit",
            "Schnelligkeit",
            "Konstitution"
        ];
    } else {
        console.error("Gear: unsupported class/job", classJob);
    }

    if (removeshy){
        stats = stats.map(field => field.replace("&shy;", ""));
    }

    return stats;
}

const races = [
    "Hyuran - Wiesländer",
    "Hyuran - Hochländer",
    "Miqo'te - Goldtatze",
    "Miqo'te - Mondstreuner",
    "Lalafell - Halmling",
    "Lalafell - Sandling",
    "Elezen - Erlschatten",
    "Elezen - Dunkelalb",
    "Roegadyn - Seewolf",
    "Roegadyn - Lohengarde",
    "Au Ra - Raen",
    "Au Ra - Xaela",
    "Viera - Rava",
    "Viera - Veena",
    "Hrothgar - Helion",
    "Hrothgar - Losgesagter"
];

function get_race_select(){
    const td = document.createElement("td");
    const select = document.createElement("select");
    select.id = "races_select";
    select.className = "xiv-select";

    races.forEach(race => {
        const option = document.createElement("option");
        option.setAttribute("data-translate", `Gear_Race_${race}`);
        option.value = race;
        option.textContent = race;
        select.appendChild(option);
    });

    select.addEventListener("change", updateValues);
    td.appendChild(select);
    return td;
}

async function createTHorTD(field, type, classname){
    const cell = document.createElement(type);

    if (type === "th" && field){
        cell.setAttribute("data-translate", `Gear_${field}`);
    }

    cell.innerHTML = field ?? "";

    if (classname !== undefined){
        cell.className = classname;
    }

    return cell;
}

function getMaxMeld(item){
    let meldstats = 0;

    substats.forEach(field => {
        const value = Number(item?.[field] ?? 0);
        if (value > meldstats){
            meldstats = value;
        }
    });

    return meldstats;
}

var ringcounter = 1
async function create_table(data, table_name, category, classJob, fields){
    let target;

    if (category === "Mainhand"){
        target = document.getElementById("weapon_left");
    } else if (category === "Offhand"){
        target = document.getElementById("weapon_right");
    } else if (category === "Ring"){
        if (ringcounter === 1){
            ringcounter++;
            category = "Ring_links";
            target = document.getElementById("ring_links");
        } else {
            ringcounter--;
            category = "Ring_rechts";
            target = document.getElementById("ring_rechts");
        }
    } else {
        target = document.getElementById(String(table_name).toLowerCase());
    }

    if (!target) return;

    target.innerHTML = "";
    target.appendChild(await createGearSlot(category, data, classJob, fields));
    updateGearResultSummary();
}

function gearDisplayName(name){
    const names = {
        "Mainhand": "Hauptwaffe",
        "Offhand": "Nebenhand",
        "Kopf": "Kopf",
        "Rumpf": "Rumpf",
        "Hände": "Hände",
        "Beine": "Beine",
        "Füße": "Füße",
        "Ohrring": "Ohrring",
        "Halskette": "Halskette",
        "Armreif": "Armreif",
        "Ring_links": "Ring 1",
        "Ring_rechts": "Ring 2",
        "Ring": "Ring"
    };
    return names[name] || name;
}

function createGearMeta(label, value, className=""){
    const item = document.createElement("span");
    item.className = "gear-item__meta " + className;

    const labelEl = document.createElement("span");
    labelEl.className = "gear-item__meta-label";
    labelEl.textContent = label;

    const valueEl = document.createElement("strong");
    valueEl.className = "gear-item__meta-value";
    valueEl.textContent = value;

    item.append(labelEl, valueEl);
    return item;
}

function createGearStat(field, value, maxMeld){
    const stat = document.createElement("span");
    stat.className = "gear-item__stat";
    stat.dataset.statName = field;
    stat.dataset.statValue = String(value || 0);

    const name = document.createElement("span");
    name.className = "gear-item__stat-name";
    name.textContent = field;

    const val = document.createElement("strong");
    val.className = "gear-item__stat-value";
    val.textContent = String(value || 0);

    if (substats.includes(field) && maxMeld > 0){
        const meld = document.createElement("small");
        meld.className = "gear-item__stat-cap";
        meld.textContent = `max ${maxMeld}`;
        val.appendChild(meld);
    }

    stat.append(name, val);
    return stat;
}

async function createGearSlot(name, json, classJob, fields){
    const slot = document.createElement("div");
    slot.className = "gear-slot";

    const header = document.createElement("header");
    header.className = "gear-slot__header";

    const title = document.createElement("h3");
    title.className = "gear-slot__title";
    title.textContent = gearDisplayName(name);

    const count = document.createElement("span");
    count.className = "xiv-badge gear-slot__count";
    count.textContent = `${json.length || Object.keys(json).length} Treffer`;

    header.append(title, count);

    const list = document.createElement("div");
    list.className = "gear-item-list";

    const values = Array.isArray(json) ? json : Object.values(json);
    if (!values.length){
        const empty = document.createElement("div");
        empty.className = "gear-slot__empty";
        empty.textContent = "Keine passenden Gegenstände gefunden.";
        list.appendChild(empty);
    }

    values.forEach(item => {
        list.appendChild(createGearItem(name, item, fields));
    });

    slot.append(header, list);
    return slot;
}

function createGearItem(slotName, item, fields){
    const maxMeld = getMaxMeld(item);
    const row = document.createElement("label");
    row.className = "gear-item";
    row.dataset.itemId = item["ID"];

    const selectWrap = document.createElement("span");
    selectWrap.className = "gear-item__select";
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = slotName;
    radio.value = item["ID"];
    radio.addEventListener("change", updateValues);
    selectWrap.appendChild(radio);

    const iconLink = document.createElement("a");
    iconLink.className = "gear-item__icon-link";
    iconLink.target = "_blank";
    iconLink.href = `https://garlandtools.org/db/#item/${item["ID"]}`;
    iconLink.addEventListener("click", event => event.stopPropagation());

    const icon = document.createElement("img");
    icon.className = "gear-item__icon";
    const iconPath = String(item["Icon"] || "")
        .replace("ui/icon/", "")
        .replace(".png", ".webp")
        .replace(".webp", "_hr1.webp");

    if (iconPath){
        icon.src = `https://ff14.akurosiakamo.de/extras/images/ui/icon/${iconPath}`;
    } else {
        icon.style.display = "none";
    }
    icon.loading = "lazy";
    icon.alt = "";
    iconLink.appendChild(icon);

    const identity = document.createElement("span");
    identity.className = "gear-item__identity";

    const name = document.createElement("strong");
    name.className = "gear-item__name";
    name.textContent = item["Name_de"];
    name.title = item["Name_en"] || item["Name_de"];
    name.addEventListener("click", event => {
        event.preventDefault();
        event.stopPropagation();
        copy2clipboard(item["Name_de"]);
    });

    const flags = document.createElement("span");
    flags.className = "gear-item__flags";
    if (parseInt(item["IsUnique"])) flags.appendChild(makeGearFlag("Einzigartig"));
    if (parseInt(item["IsDyeable"])) flags.appendChild(makeGearFlag("Färbbar"));
    if (parseInt(item["IsAdvancedMeldingPermitted"])) flags.appendChild(makeGearFlag("Pentameld"));
    if (parseInt(item["ItemSearchCategory"])) flags.appendChild(makeGearFlag("Marktbrett"));

    identity.append(name, flags);

    const meta = document.createElement("span");
    meta.className = "gear-item__metadata";
    meta.append(
        createGearMeta("Lv", item["Level_Equip"], "lvl"),
        createGearMeta("iLv", item["Level_Item"], "ilvl"),
        createGearMeta("Patch", item["Patch"], "patch"),
        createGearMeta("Materia", item["MateriaSlotCount"], "materia")
    );

    const stats = document.createElement("span");
    stats.className = "gear-item__stats";

    fields.forEach(field => {
        const xfield = field.replace("&shy;", "");
        if (["Blockeffekt", "Blockrate"].includes(xfield)) return;
        if (!(xfield in sum_fields)) sum_fields[xfield] = 0;
        stats.appendChild(createGearStat(xfield, get(item, xfield, 0), maxMeld));
    });

    row.append(selectWrap, iconLink, identity, meta, stats);
    return row;
}

function makeGearFlag(text){
    const flag = document.createElement("span");
    flag.className = "xiv-badge gear-item__flag";
    flag.textContent = text;
    return flag;
}

function updateGearResultSummary(){
    const summary = document.getElementById("gear-result-summary");
    if (!summary) return;

    const sections = Array.from(document.querySelectorAll("#gearlist .gear-slot"));
    const items = sections.reduce((total, section) => total + section.querySelectorAll(".gear-item").length, 0);
    summary.textContent = `${items} Gegenstände · ${sections.length} Slots`;
}

/* The footer/summary table remains compact, but item selection no longer relies
   on the old table-row DOM. */
async function createSummaryTable(fields){
    const table = document.getElementById("table_stats_overview");
    if (!table) return;

    table.innerHTML = "";

    const head = document.createElement("thead");
    const headRow = document.createElement("tr");

    headRow.appendChild(await createTHorTD("Race", "th", "race"));
    headRow.appendChild(await createTHorTD("ilvl", "th", "ilvl"));

    fields.forEach(field => {
        headRow.appendChild(createSummaryCellSync(field, "th", "stat"));
    });

    head.appendChild(headRow);

    const body = document.createElement("tbody");
    body.id = "tbody_stats_overview";

    const row = document.createElement("tr");
    row.appendChild(get_race_select());
    row.appendChild(createSummaryCellSync("0", "td", "ilvl"));

    fields.forEach(field => {
        row.appendChild(createSummaryCellSync("0", "td", "stat " + field));
    });

    body.appendChild(row);

    table.className = "xiv-table xiv-stat-table";
    table.append(head, body);

    updateValues();
}

function createSummaryCellSync(value, type, className){
    const cell = document.createElement(type);
    cell.innerHTML = value;
    if (className) cell.className = className;
    return cell;
}

function set_localstorage() {
    localStorage.setItem('gear_class',   document.getElementById("classjob").selectedIndex);
    localStorage.setItem('gear_minlvl',  document.getElementById("lvl_from").value);
    localStorage.setItem('gear_maxlvl',  document.getElementById("lvl_to").value);
    localStorage.setItem('gear_minilvl', document.getElementById("ilvl_from").value);
    localStorage.setItem('gear_maxilvl', document.getElementById("ilvl_to").value);
    localStorage.setItem('gear_whiteitems', document.getElementById("rarity_0").checked);
    localStorage.setItem('gear_reditems', document.getElementById("rarity_7").checked);
    localStorage.setItem('gear_greenitems', document.getElementById("rarity_2").checked);
    localStorage.setItem('gear_blueitems', document.getElementById("rarity_3").checked);
    localStorage.setItem('gear_purpleitems', document.getElementById("rarity_4").checked);
    localStorage.setItem('gear_include_hq', document.getElementById("include_hq").checked);
    localStorage.setItem('gear_limit_to_hq', document.getElementById("limit_to_hq").checked);
}

function get_localstorage() {
    document.getElementById("classjob").selectedIndex = localStorage.getItem('gear_class') || 16
    document.getElementById("lvl_from").value = localStorage.getItem('gear_minlvl') || minlvl
    document.getElementById("lvl_to").value = localStorage.getItem('gear_maxlvl') || maxlvl
    document.getElementById("ilvl_from").value = localStorage.getItem('gear_minilvl') || minilvl
    document.getElementById("ilvl_to").value = localStorage.getItem('gear_maxilvl') || maxilvl
    if (localStorage.getItem('gear_whiteitems') == "true"){
        document.getElementById("rarity_0").checked = true;
    }
    if (localStorage.getItem('gear_reditems') == "true"){
        document.getElementById("rarity_7").checked = true;
    }
    if (localStorage.getItem('gear_greenitems') == "true"){
        document.getElementById("rarity_2").checked = true;
    }
    if (localStorage.getItem('gear_blueitems') == "true"){
        document.getElementById("rarity_3").checked = true;
    }
    if (localStorage.getItem('gear_purpleitems') == "true"){
        document.getElementById("rarity_4").checked = true;
    }
    if ((document.getElementById("rarity_0").checked || document.getElementById("rarity_7").checked || document.getElementById("rarity_2").checked || document.getElementById("rarity_3").checked || document.getElementById("rarity_4").checked) === false) {
        document.getElementById("rarity_2").checked = true;
        document.getElementById("rarity_3").checked = true;
        document.getElementById("rarity_4").checked = true;
    }
    if (localStorage.getItem('gear_include_hq') == "true"){
        document.getElementById("include_hq").checked = true;
    } else {
        document.getElementById("include_hq").checked = true;
    }
    if (localStorage.getItem('gear_limit_to_hq') == "true"){
        document.getElementById("limit_to_hq").checked = true;
    } else {
        document.getElementById("limit_to_hq").checked = false;
    }
}

defaultSatst = {
    "Phys. Basiswert":       0,
    "Mag. Basiswert":        0,
    "Verteidigung":          0,
    "Magieabwehr":          0,
    "Stärke":              422,
    "Intelligenz":         439,
    "Willenskraft":        437,
    "Geschick":            439,
    "Direkter Treffer":    380,
    "Kritischer Treffer":  380,
    "Entschlossenheit":    340,
    "Schnelligkeit":       380,
    "Zaubertempo":         380,
    "Frömmigkeit":         340,
    "Konstitution":        340,
    "Unbeugsamkeit":       380
}

// following list is ordered by the above races list
baseStatModifier= {
    "Phys. Basiswert":     [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    "Mag. Basiswert":      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    "Verteidigung":        [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    "Magieabwehr":         [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    "Stärke":              [ 2,  3,  2, -1, -1, -1,  0,  0,  0,  2,  3, -1,  0, -1,  3,  3],
    "Intelligenz":         [ 3, -2, -1,  1,  2,  2,  2,  3,  0, -2,  0,  0,  1,  3, -3, -3],
    "Willenskraft":        [-1,  0, -1,  3,  0,  3, -1,  1,  2,  1, -2,  3,  1,  2,  3,  3],
    "Geschick":            [-1,  0,  3,  2,  3,  1,  3,  0, -2, -1,  0,  2,  3,  0, -3, -3],
    "Frömmigkeit":         [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    "Konstitution":        [ 0,  2,  0, -2, -1, -2, -1, -1,  3,  3,  2, -1, -2, -1,  3,  3],
    "Direkter Treffer":    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    "Kritischer Treffer":  [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    "Entschlossenheit":    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    "Schnelligkeit":       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    "Zaubertempo":         [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    "Unbeugsamkeit":       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0]
}

function updateValues(){
    const new_sum_fields = JSON.parse(JSON.stringify(sum_fields));
    new_sum_fields["ilvl"] = 0;

    const selected = Array.from(document.querySelectorAll("#gearlist .gear-item input[type='radio']:checked"));

    selected.forEach(radio => {
        const item = radio.closest(".gear-item");
        if (!item) return;

        item.querySelectorAll(".gear-item__stat").forEach(stat => {
            const name = stat.dataset.statName;
            const value = parseInt(stat.dataset.statValue || "0", 10);
            if (!(name in new_sum_fields)) new_sum_fields[name] = 0;
            new_sum_fields[name] += value;
        });

        const ilvl = parseInt(item.querySelector(".gear-item__meta.ilvl .gear-item__meta-value")?.textContent || "0", 10);
        const slotName = radio.name;
        new_sum_fields["ilvl"] += (slotName === "Mainhand" && document.getElementsByName("Offhand").length === 0) ? ilvl * 2 : ilvl;
    });

    const tbody = document.getElementById("tbody_stats_overview");
    const raceSelect = document.getElementById("races_select");
    if (!tbody || !raceSelect) return;

    const race = raceSelect.value;

    Object.keys(new_sum_fields).forEach(field => {
        if (field === "ilvl"){
            const element = tbody.getElementsByClassName("ilvl")[0];
            if (element) element.textContent = selected.length ? Math.round(new_sum_fields[field] / 12) : "0";
            return;
        }

        const element = tbody.getElementsByClassName(field)[0];
        if (!element) return;

        const gear_value = parseInt(new_sum_fields[field], 10) || 0;
        const stat_value = parseInt(defaultSatst[field], 10) || 0;
        const modifierList = baseStatModifier[field] || [];
        const modify_value = parseInt(modifierList[races.indexOf(race)], 10) || 0;
        element.textContent = `${gear_value + stat_value + modify_value} (+${gear_value})`;
    });
}

function initGearPage(){
    get_localstorage();
    call_api_data();
}

if (document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", initGearPage, { once: true });
} else {
    initGearPage();
}
