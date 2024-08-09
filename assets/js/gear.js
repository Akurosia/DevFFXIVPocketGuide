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
    console.log(text)
  if (!navigator.clipboard) {
    fallbackCopyTextToClipboard(text);
    return;
  }
  navigator.clipboard.writeText(text).then(function() {
    console.log('Async: Copying to clipboard was successful!');
  }, function(err) {
    console.error('Async: Could not copy text: ', err);
  });
}

function remove_gearlist(){
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
    sum_fields = {}
    classjob_select = document.getElementById("classjob")
    classjob = classjob_select.options[classjob_select.selectedIndex].value;
    lvl_from = document.getElementById("lvl_from").value
    lvl_to = document.getElementById("lvl_to").value
    ilvl_from = document.getElementById("ilvl_from").value
    ilvl_to = document.getElementById("ilvl_to").value
    include_hq = document.getElementById("include_hq").checked
    limit_to_hq = document.getElementById("limit_to_hq").checked

    var rarity = []
    var x = null
    x = ((document.getElementById("rarity_0").checked) ? rarity.push("1") : null);
    x = ((document.getElementById("rarity_7").checked) ? rarity.push("7") : null);
    x = ((document.getElementById("rarity_2").checked) ? rarity.push("2") : null);
    x = ((document.getElementById("rarity_3").checked) ? rarity.push("3") : null);
    x = ((document.getElementById("rarity_4").checked) ? rarity.push("4") : null);

    set_localstorage()
    remove_gearlist()
    promisses = []
    lists.forEach(category => {
        table_name = category
        if (category == "Mainhand"){
            table_name = weapon_dict[classjob]
        } else if (category == "Offhand"){
            table_name = tools_dict[classjob]
            if (table_name === undefined){
                table_name = category
            }
        }
        url_params2 = "?classjob=" + classjob +
                     "&classjobadd=" + class_additions[classjob] +
                     "&category=" + String(table_name).replaceAll(" (", "_").replaceAll(")", "").replaceAll("-", "_").replaceAll(" ", "_") +
                     "&lvl_from=" + lvl_from +
                     "&lvl_to=" + lvl_to +
                     "&ilvl_from=" + ilvl_from +
                     "&ilvl_to=" + ilvl_to +
                     "&rarity=" + String(rarity)
        if (include_hq && limit_to_hq) {
            url_params2 += "&hq=1"
        } else if (include_hq && !limit_to_hq) {
                url_params2 += "&hq=0,1"
        } else {
            url_params2 += "&hq=0"
        }
        jsondata = load_data(url_params2, table_name, category, classjob)
        promisses.push(jsondata)
    })
    await Promise.allSettled(promisses).then((xxx) => {
        console.log("Done")
        // this is from handleLanguages.js
        executeHandelingLanguages();
        setTimeout(() => {  executeHandelingLanguages(); }, 700);
    })
}

async function load_data(params, table_name, category, classJob){
    //load treasure map json
    url = 'https://ffxiv.akurosiakamo.de/queryFFXIVequipmentDB.php' + params
    console.log(url)
    //fetch(url,{mode: 'cors'})
    return fetch(url)
        .then(r => r.json())
        .then(data => {
            create_table(data, table_name, category, classJob)
        })
        .catch(e => console.log(e))
}

function get(object, key, default_value) {
    if (typeof object === "undefined"){
        return default_value
    }
    var result = object[key];
    return (typeof result !== "undefined") ? result : default_value;
}

var ringcounter = 1
async function create_table(data, table_name, category, classJob){
    //console.log(table_name)
    // handle mainhand case
    if (category == "Mainhand"){
        _div = document.getElementById("weapon_left")
    }
    // handle offhand case
    else if (category == "Offhand"){
        _div = document.getElementById("weapon_right")
    //handle ring cases
    }else if (category == "Ring"){
        if (ringcounter == 1){
            ringcounter++
            category = "Ring_links"
            _div = document.getElementById("ring_links")
        }else if (ringcounter == 2){
            ringcounter--
            category = "Ring_rechts"
            _div = document.getElementById("ring_rechts")
        }
    //handle all other cases
    }else {
        _div = document.getElementById(table_name.toLowerCase())
    }
    _div.innerHTML = ""
    _table = await createTemplateTable(category, data, classJob)
    _div.appendChild(_table)
}

async function createTemplateTable(name, json, classJob){
    var _table = document.createElement('table');
    _thead = await createTemplateTableHead(name, json, classJob)
    _tbody = await createTemplateTableBody(name, json, classJob)
    createSummaryTable(sum_fields)
    _table.appendChild(_thead);
    _table.appendChild(_tbody);

    //_table.className = "table table-bordered table-striped table-dark table-hover table-striped bg-charcoal text-light border-gold-metallic";
    _table.className = "table table-bordered table-dark table-striped text-light patch_table";
    _table.setAttribute("id", "table_"+name);
    //_table.style.width = "1641px";
    return _table;
}

async function createTHorTD(field, _type, classname){
    var _th = document.createElement(_type);
    if (_type == "th" && field) {
        _th.setAttribute("data-translate", `Gear_${field}`)
    }
    _th.innerHTML = field;
    if (classname !== undefined){
        _th.className = classname
    }
    return _th
}

function get_stats_for_class(classJob, removeshy=false){
    x = []
    if (["BSW","SMA","RMA","BMA", "PKT"].includes(classJob)){
        x = ["Mag. Basiswert", "Magieabwehr", "Intelligenz", "Kritischer Treffer", "Direkter Treffer", "Entschlossenheit","Zaubertempo","Konstitution"]
    }
    if (["WMA","GLT","AST", "WEI"].includes(classJob)){
        x = ["Mag. Basiswert", "Magieabwehr", "Willenskraft", "Frömmigkeit", "Kritischer Treffer", "Direkter Treffer", "Entschlossenheit","Zaubertempo","Konstitution"]
    }
    if (["ZMR","GRS","PLA","GLD","GER","WEB","ALC","GRM"].includes(classJob)){
        x = ["Kunstfertigkeit", "Kontrolle", "HP","Konstitution"]
    }
    if (["MIN","GÄR","FIS"].includes(classJob)){
        x = ["Sammelgeschick", "Expertise", "SP","Konstitution"]
    }
    if (["PLD","KRG","DKR","REV"].includes(classJob)){
        x = ["Phys. Basiswert", "Verteidigung", "Stärke", "Kritischer Treffer", "Direkter Treffer", "Entschlossenheit", "Schnelligkeit", "Unbeugsamkeit", "Konstitution"]
    }
    if (["NIN","BRD","MCH","TÄN"].includes(classJob)){
        x = ["Phys. Basiswert", "Verteidigung", "Geschick", "Kritischer Treffer", "Direkter Treffer", "Entschlossenheit", "Schnelligkeit","Konstitution"]
    }
    if (["MÖN","DRG","SAM", "SNT", "VPR"].includes(classJob)){
        x = ["Phys. Basiswert", "Verteidigung", "Stärke", "Kritischer Treffer", "Direkter Treffer", "Entschlossenheit", "Schnelligkeit","Konstitution"]
    }
    if (removeshy){
        for (e in x){
            x[e] = x[e].replace("&shy;", "")
        }
    }
    return x
}

races = [
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
]

function get_race_select(){
    select = document.createElement("select")
    for (var race in races) {
        option = document.createElement("option")
        option.setAttribute("data-translate", `Gear_Race_${races[race]}`)
        option.value = races[race]
        option.innerHTML = races[race]
        select.appendChild(option)
    }
    select.setAttribute("onchange", "updateValues()")
    select.setAttribute("id", "races_select")
    return select
}

// this creates the footer table
async function createSummaryTable(fields){
    var table = document.getElementById("table_stats_overview")
    table.innerHTML = ""
    var _head = document.createElement('thead');
    _head.id = "thead_stats_overview"
    var _tr = document.createElement('tr');
    _tr.appendChild(await createTHorTD("Race", "th", "race"));
    //_tr.appendChild(await createTHorTD("lvl", "th", "lvl"));
    _tr.appendChild(await createTHorTD("ilvl", "th", "ilvl"));
    //_tr.appendChild(await createTHorTD("Materia", "th", "materia"));
    for (var field in fields){
        _tr.appendChild(await createTHorTD(field, "th", "stat"));
    }
    //place holder to allign get from column
    //_tr.appendChild(await createTHorTD("", "th", "stat "));
    _head.appendChild(_tr);
    table.appendChild(_head);

    var _body = document.createElement('tbody');
    _body.id = "tbody_stats_overview"
    var _tr = document.createElement('tr');
    _tr.appendChild(get_race_select());
    //_tr.appendChild(await createTHorTD("", "td", "lvl"));
    _tr.appendChild(await createTHorTD("0", "td", "ilvl"));
    //_tr.appendChild(await createTHorTD("", "td", "materia"));
    for (var field in fields){
        _tr.appendChild(await createTHorTD(fields[field], "td", "stat " + field));
    }
    //place holder to allign get from column
    //_tr.appendChild(await createTHorTD("", "td", "stat "));
    _body.appendChild(_tr);
    table.className = "table-bordered table-dark bg-charcoal text-light"
    table.appendChild(_body);
    document.getElementById("races_select").onchange()
}

async function createTemplateTableHead(name, json, classJob){
    var _head = document.createElement('thead');
    _head.setAttribute("id", "thead_"+name);
    var _tr = document.createElement('tr');
    _tr.appendChild(await createTHorTD("", "th",  "radio"));
    _tr.appendChild(await createTHorTD("", "th",  "icon"));
    _tr.appendChild(await createTHorTD(name, "th"));
    _tr.appendChild(await createTHorTD("lvl", "th", "lvl"));
    _tr.appendChild(await createTHorTD("ilvl", "th", "ilvl"));
    _tr.appendChild(await createTHorTD("patch", "th", "patch"));
    _tr.appendChild(await createTHorTD("Materia", "th", "materia"));

    fields = get_stats_for_class(classJob)
    for (var field in fields){
        if (["Blockeffekt", "Blockrate"].includes(fields[field])){
        } else if (fields[field] == []){
        } else {
            _tr.appendChild(await createTHorTD(fields[field], "th", "stat"));
            xfield = fields[field].replace("&shy;", "")
            //xfield = fields[field].replace(" ", "_").replace("&shy;", "")
            sum_fields[xfield] = 0
        }
    }
    //_tr.appendChild(await createTHorTD("Get From", "th", "loc"));
    _head.appendChild(_tr);
    return _head;
}

function getMaxMeld(item) {
    meldstats = 0
    for (var field in substats){
        // jor api itself add item['Stats'][substats[field]]
        if (meldstats < item[substats[field]]) {
            meldstats = item[substats[field]];
        }
    }
    return meldstats
}

cleartext = {
    1: "Ja",
    0: "Nein",
    true: "Ja",
    false: "Nein"
}
async function createTemplateTableBody(name, json, classJob){
    var _body = document.createElement('tbody');
    _body.setAttribute("id", "tbody_"+name);
    for (var key in json){
        max_meld = getMaxMeld(json[key])
        var _tr = document.createElement('tr');
        _tr.appendChild(await createTHorTD("<input onclick='updateValues()' type='radio' id='" + json[key]["Name_de"] + "' name='" + name + "' value=''>", "td"));
        _tr.appendChild(await createTHorTD("<a target='_blank' href='http://garlandtools.org/db/#item/" + json[key]["ID"] + "'><img loading='lazy' src='https://xivapi.com/i/" + json[key]['Icon'].replace("ui/icon/", "") + "'></img>" + "</a>", "td", "icon"));
        _name = '<div class="mytooltip"  id="' + json[key]["ID"] + '">'
        _name += '<span class="lang-toggle lang-toogle-de" onclick="copy2clipboard(\'' + json[key]["Name_de"] + '\')">' + json[key]["Name_de"] + '</span>'
        _name += '<span class="lang-toggle lang-toogle-en" onclick="copy2clipboard(\'' + json[key]["Name_en"] + '\')">' + json[key]["Name_en"] + '</span>'
        _name += '<span class="lang-toggle lang-toogle-fr" onclick="copy2clipboard(\'' + json[key]["Name_fr"] + '\')">' + json[key]["Name_fr"] + '</span>'
        _name += '<span class="lang-toggle lang-toogle-ja" onclick="copy2clipboard(\'' + json[key]["Name_ja"] + '\')">' + json[key]["Name_ja"] + '</span>'
        _name += '<span class="lang-toggle lang-toogle-cn" onclick="copy2clipboard(\'' + json[key]["Name_cn"] + '\')">' + json[key]["Name_cn"] + '</span>'
        _name += '<span class="lang-toggle lang-toogle-ko" onclick="copy2clipboard(\'' + json[key]["Name_ko"] + '\')">' + json[key]["Name_ko"] + '</span>'
        _name += '<span class="tooltiptext">'
        _name += 'Färbbar: ' + cleartext[parseInt(json[key]["IsDyeable"])] + '</br>'
        _name += 'Einzigartig: ' + cleartext[parseInt(json[key]["IsUnique"])] + '</br>'
        _name += 'Handelbar: ' + cleartext[!parseInt(json[key]["IsUntradable"])] + '</br>'
        _name += 'Verkauf am MB: ' + cleartext[parseInt(json[key]["ItemSearchCategory"])] + '</br>'
        _name += 'Pentameld: ' + cleartext[parseInt(json[key]["IsAdvancedMeldingPermitted"])] + '</span></div>'
        _tr.appendChild(await createTHorTD(_name, "td"));
        _tr.appendChild(await createTHorTD(json[key]["Level_Equip"], "td", "lvl"));
        _tr.appendChild(await createTHorTD(json[key]["Level_Item"], "td", "ilvl"));
        _tr.appendChild(await createTHorTD(json[key]["Patch"], "td", "patch"));
        _tr.appendChild(await createTHorTD(json[key]["MateriaSlotCount"], "td", "materia"));
        fields = get_stats_for_class(classJob, true)
        for (var field in fields){
            xfield = fields[field].replace("&shy;", "")
            if (["Blockeffekt", "Blockrate"].includes(field)){
            } else {
                _td = await createTHorTD(get(json[key], xfield, 0), "td", "stat " + xfield)
                if (substats.includes(xfield)){
                    _span = document.createElement("span")
                    _span.innerHTML = " (" + max_meld + ")"
                    _td.appendChild(_span);
                }
                _tr.appendChild(_td);
            }
        }
        //_tr.appendChild(await createTHorTD("", "td", "loc"));
        _body.appendChild(_tr);
    }
    return _body;
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
    new_sum_fields = JSON.parse(JSON.stringify(sum_fields))
    for (category in lists){
        //get correct ring table
        tablename = lists[category]
        if (tablename == "Ring"){
            if (ringcounter == 1){
                ringcounter++
                tablename = "Ring_links"
            }else {
                ringcounter--
                tablename = "Ring_rechts"
            }
        }
        // getAll items per table
        var cbs_main = document.getElementsByName(tablename)
        for (var cb in cbs_main) {
            // get only for items that are checked
            if(cbs_main[cb].checked){
                statElements = cbs_main[cb].parentElement.parentElement.getElementsByClassName("stat")
                // each stat for the checked item
                for (var stat in statElements) {
                    if (statElements[stat].className !== undefined){
                        nstat = statElements[stat].className.substring(5).replace("&shy;", "")
                        new_sum_fields[nstat] += parseInt(statElements[stat].innerHTML, 10)
                    }
                }
                // set ilvl to 0 if not defined
                if (new_sum_fields["ilvl"] == undefined) {
                    new_sum_fields["ilvl"] = 0
                }
                // if no entry for shield is available, count weapon 2 times
                if (document.getElementsByName("Offhand").length == 0 && tablename == "Mainhand"){
                    new_sum_fields["ilvl"] += 2* parseInt(cbs_main[cb].parentElement.parentElement.getElementsByClassName("ilvl")[0].innerHTML)
                }else{
                    new_sum_fields["ilvl"] += parseInt(cbs_main[cb].parentElement.parentElement.getElementsByClassName("ilvl")[0].innerHTML)
                }
            }
        }
    }

    tbody = document.getElementById("tbody_stats_overview")
    race = document.getElementById("races_select").value
    for (var field in new_sum_fields){
        if (field == "ilvl"){
            element = tbody.getElementsByClassName(field)[0]
            element.innerHTML = parseInt(new_sum_fields[field] / 12)
        }else {
            element = tbody.getElementsByClassName(field)[0]
            gear_value = parseInt(new_sum_fields[field], 10)
            stat_value = (parseInt(defaultSatst[field], 10) || 0)
            modify_value = (parseInt(baseStatModifier[field][races.indexOf(race)], 10) || 0)
            element.innerHTML = ( gear_value + stat_value + modify_value).toString() + " (+" + gear_value + ")"
        }
    }
}

get_localstorage()
call_api_data()
