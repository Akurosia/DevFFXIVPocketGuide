
var result = {}
var player_list = [];
if (localStorage.getItem('fflogs_isAku')){
    player_list = [
        ["Akurosia Kamo", "Shiva", "EU"],
        ["---", "", ""],
        ["Nana Mejyna", "Odin", "EU"],
        ["Ieni Telara", "Odin", "EU"],
        ["Loucid Dreaming", "Odin", "EU"],
        ["Rhago Ashina", "Raiden", "EU"],
        ["Dragomir Xertuz", "Shiva", "EU"],
        ["Shira Noyuki", "Shiva", "EU"],
        ["Robin Black", "Shiva", "EU"],
        ["Kelly Orphis'black", "Raiden", "EU"],
        //["Rhotgeim Igarashi", "Odin", "EU"],
        ["---", "", ""],
        ["Kamo Akurosia", "Shiva", "EU"],
        ["Kuroyuki Hiragi", "Shiva", "EU"],
        ["Patrobo Rendan", "Shiva", "EU"],
        ["Nanami Bladefield", "Odin", "EU"],
        ["Koko Hirai", "Shiva", "EU"],
        ["Myosotis Black", "Shiva", "EU"],
        ["Archangel Scarlett", "Phoenix", "EU"],
        ["Shade Kazumori", "Shiva", "EU"],
        ["---", "", ""],
        ["Hans Yolo", "Shiva", "EU"],
        ["Calis Asterion", "Lich", "EU"],
        ["Nanoha Bladefield", "Odin", "EU"],
        ["Asuna Bladefield", "Odin", "EU"],

        ["Miyuki Mizu", "Zodiark", "EU"],
        ["Filianore Void", "Shiva", "EU"],
         //["---", "", ""],
         //["Celia Edenfall", "Twintania", "EU"],
         //["Emi Apyrha", "Odin", "EU"],
         //["Lesunia Antiqua", "Shiva", "EU"],
         //["Dogina Wok", "Zodiark", "EU"],
         //["Kyleigh Alyz", "Shiva", "EU"],
         //["Yuqi Minami", "Twintania", "EU"],
         //["Tama Worry", "Twintania", "EU"],
         //["Cola Bottle", "Raiden", "EU"],
         //["Kaynehril Everdusk", "Zodiark", "EU"],
         //["Vanille Croissant", "Shiva", "EU"],
         //["Gora Saurus", "Phoenix", "EU"],
         //["Mimiko Moeka", "Zodiark", "EU"],
         //["Simha'ze Lerdai", "Shiva", "EU"]

        //FRU 100% ["Couchgirl Neviutz", "Odin", "EU"],
    ]
    if (localStorage.getItem('fflogs_isAku_debug')) {
        player_list = [
            ["Akurosia Kamo", "Shiva", "EU"]
        ]
    }
}
// fix also in python_module > __init__.getFFLOGSapiPlayerData

figthsArray = [
    [1060, ["UCoB"]],
    [1061, ["UWU"]],
    [1062, ["TEA"]],
    [1065, ["DSU"]],
    [1068, ["TOP"]],
    [1079, ["FRU"]],

    [97,  ["R5S"]],
    [98,  ["R6S"]],
    [99,  ["R7S"]],
    [100, ["R8S"]],
    // [92, ["P12S_P2"]],

    [3010, ["Suzaku"]],
    // [1071, ["Valigarmanda"]],
    // [1072, ["Zoraal Ja"]],
    [1080, ["Zelenia"]],
];

// Extract fight IDs while preserving order
fight_ids = figthsArray.map(entry => entry[0]);
// Convert figthsArray back to the original json object used before
figths = Object.fromEntries(figthsArray);


function fixIDs(_id) {
    if (["1039", "1047", "1060", "1073"].includes(_id)) { // 1039=SB 1047=SHB 1060=EW 1073=DT FIX OLD UCoB
        _id = "1060"
    }
    if (["1042", "1048", "1061", "1074"].includes(_id)) { // 1042=SB 1048=SHB 1061=EW 1074=DT  FIX OLD UWU
        _id = "1061"
    }
    if (["1050", "1062", "1075"].includes(_id)) { // 1050=SHB 1062=EW 1075=DT FIX OLD TEA
        _id = "1062"
    }
    if (["1065", "1076"].includes(_id)) { // 1065=EW 1076=DT FIX OLD DSU
        _id = "1065"
    }
    if (["1068", "1077"].includes(_id)) { // 1068=EW 1077=DT FIX OLD TOP
        _id = "1068"
    }
    if (["1079"].includes(_id)) { // 1079=DT FIX OLD FRU
        _id = "1079"
    }
    return _id
}

const currentDate = new Date();
function gSFZ_getDataViaFetch(user, state){
    // state is only set if the button was pressed manually in the frontend    console.log("STATE: " + localStorage.getItem('fflogs_player_data')=== undefined)
    if (localStorage.getItem('fflogs_player_data') !== "undefined" && currentDate.getTime() < localStorage.getItem('fflogs_last_access') && !state) {
        remaining = (localStorage.getItem('fflogs_last_access') - currentDate.getTime()) / 60000
        console.log(`Get Cached Data (${remaining})`)
        printTable(JSON.parse(localStorage.getItem('fflogs_player_data')))
    } else {
        console.log("Get New Data")
        prom = getFFLOGSapiPlayerData(player = user, customTextblock = "", includeName = false)
        Promise.all([prom]).then((values) => {
            next5min = new Date(currentDate.getTime() + 5 * 60000).getTime()
            localStorage.setItem('fflogs_player_data', JSON.stringify(values[0]))
            localStorage.setItem('fflogs_last_access', next5min)
            printTable(values[0])
        });
    }
}


function addThead(result){
    thead = document.createElement("thead")
    for (var i in result) {
        tr = document.createElement("tr")
        th = document.createElement("th")
        th.innerText = "name"
        tr.appendChild(th)
        for (var j of fight_ids){
            if (figths[j] != undefined) {
                th = document.createElement("th")
                th.innerHTML = figths[j][0]
                tr.appendChild(th)
            }
        }
        thead.style = "position: sticky; top: -1px;"
        thead.appendChild(tr)
        break
    }
    return thead
}

function addLodestoneID(lodeston_id){
    img = document.createElement("img")
    img.src = "https://img.finalfantasyxiv.com/lds/pc/global/images/favicon.ico?1490749553"
    img.style.height = "20px"
    img.style.width = "20px"
    a = document.createElement("a")
    a.href = "https://de.finalfantasyxiv.com/lodestone/character/" + lodeston_id
    a.target = "_blank"
    a.style.paddingRight = "5px"
    a.rel = "noopener noreferrer"
    a.appendChild(img)
    return a
}
function addTomestoneID(lodeston_id, name){
    img = document.createElement("img")
    img.src = "https://assets.rpglogs.com/img/ff/tomestone-icon.png"
    img.style.height = "20px"
    img.style.width = "20px"
    a = document.createElement("a")
    a.href = "https://tomestone.gg/character/" + lodeston_id + "/" + name.toLowerCase().replace(" ", "-")
    a.target = "_blank"
    a.style.paddingRight = "5px"
    a.rel = "noopener noreferrer"
    a.appendChild(img)
    return a
}
function addFFLOGSID(fflogs_id, name){
    img = document.createElement("img")
    img.src = "https://assets.rpglogs.com/img/ff/favicon.png?v=2"
    img.style.height = "20px"
    img.style.width = "20px"
    //img.style.paddingRight = "5px"
    a = document.createElement("a")
    a.href = "https://de.fflogs.com/character/id/" + fflogs_id
    a.target = "_blank"
    a.style.paddingRight = "5px"
    a.rel = "noopener noreferrer"
    a.appendChild(img)
    return a
}

function addLink(link, name){
    a = document.createElement("a")
    if (link != undefined) {
        a.href = link
    } else {
        a.href = ""
    }
    a.target = "_blank"
    a.innerHTML = name
    a.style = "color: #2d59db !important"
    a.rel = "noopener noreferrer"
    return a
}

// todo add tomestone and fflogs icon and change alignment
function addUserNameStuff(iresult, name){
    td = document.createElement("td")
    //console.log(iresult);
    if (iresult["lodestone_id"] != undefined){
        td.appendChild(addLodestoneID(iresult["lodestone_id"]))
        td.appendChild(addTomestoneID(iresult["lodestone_id"], name))
        td.appendChild(addFFLOGSID(iresult["fflogs_id"]))
    }
    td.appendChild(addLink(iresult["link"], name))
    td.style = "color: #2d59db !important; font-size: 20px; text-shadow: black 0px 0px;"
    return td
}

function addTbody(result){
    tbody = document.createElement("tbody")
    for (var x in player_list) {
        i = player_list[x][0]
        if (result[i] !== undefined){
        if (i == "---"){
            continue
        }
        tr = document.createElement("tr")
        tr.appendChild(addUserNameStuff(result[i], i))
        for (var j of fight_ids){
            if (figths[j] != undefined) {
                console.log("[addTbody] Result:")
                console.log(result)
                tr = addRow(tr, result, i, j)
            }
        }
        tbody.appendChild(tr)
        }
    }
    return tbody
}

function printTable(data){
    result = Object.assign({}, data, result);
    x = document.getElementById("table")
    x.innerHTML = "";
    table = document.createElement("table")
    table.className = "table table-bordered table-dark table-striped text-light table-hover";
    table.setAttribute("id", "table_fflogs");
    head = addThead(result)
    table.appendChild(head)
    table.appendChild(addTbody(result))
    //table.appendChild(head)
    x.appendChild(table)
}

// normal job icons
jobs = {
    "Paladin":     "062119_hr1",
    "Warrior":     "062121_hr1",
    "DarkKnight":  "062132_hr1",
    "Gunbreaker":  "062137_hr1",
    "WhiteMage":   "062124_hr1",
    "Scholar":     "062128_hr1",
    "Astrologian": "062133_hr1",
    "Sage":        "062140_hr1",
    "Monk":        "062120_hr1",
    "Dragoon":     "062122_hr1",
    "Ninja":       "062130_hr1",
    "Samurai":     "062134_hr1",
    "Reaper":      "062139_hr1",
    "Viper":       "062141_hr1",
    "Bard":        "062123_hr1",
    "Machinist":   "062131_hr1",
    "Dancer":      "062138_hr1",
    "BlackMage":   "062125_hr1",
    "Summoner":    "062127_hr1",
    "RedMage":     "062135_hr1",
    "Pictomancer": "062142_hr1"
}
//golden icons
jobs = {
    "Paladin":     "062019_hr1",
    "Warrior":     "062021_hr1",
    "DarkKnight":  "062032_hr1",
    "Gunbreaker":  "062037_hr1",
    "WhiteMage":   "062024_hr1",
    "Scholar":     "062028_hr1",
    "Astrologian": "062033_hr1",
    "Sage":        "062040_hr1",
    "Monk":        "062020_hr1",
    "Dragoon":     "062022_hr1",
    "Ninja":       "062030_hr1",
    "Samurai":     "062034_hr1",
    "Reaper":      "062039_hr1",
    "Viper":       "062041_hr1",
    "Bard":        "062023_hr1",
    "Machinist":   "062031_hr1",
    "Dancer":      "062038_hr1",
    "BlackMage":   "062025_hr1",
    "Summoner":    "062027_hr1",
    "RedMage":     "062035_hr1",
    "Pictomancer": "062042_hr1"
}
function addJobImage(job){
    //return '<img loading="lazy" src="https://xivapi.com/i/062000/' + jobs[job] + '" style="height: 30px; padding-right: 5px;">'
    return '<img loading="lazy" src="https://v2.xivapi.com/api/asset/ui/icon/062000/' + jobs[job] + '.tex?format=webp" style="height: 30px; padding-right: 5px;">'
}

function addRow(tr, result, name, encounterID){
    td = document.createElement("td")
    console.log("[addRow] result[name][encounterID]:")
    console.log(result[name][encounterID])
    console.log(encounterID)
    if (result[name][encounterID] === undefined) {
        result[name][encounterID] = { 'historical': -1 }
    }
    if (parseInt(result[name][encounterID]['historical']) !== -1) {
        td.innerHTML = addJobImage(result[name][encounterID]['job']) + parseInt(result[name][encounterID]['historical']) + " <span style=\"color:white\">(" + parseInt(result[name][encounterID]['kills']) + ")</span>"
    }
    td = colorize(td, parseInt(result[name][encounterID]['historical']))
    td.title = parseInt(result[name][encounterID]['kills']) + " Kills"
    tr.appendChild(td)
    return tr
}

function colorize(td, value){
    //gold
    if (value == 100){
        td.style.color = "gold"
    //pink
    }else if ( 99 == value ){
        td.style.color = "darksalmon"
    //orange
    }else if ( 99 > value && value >= 95 ){
        td.style.color = "orange"
    //purple
    }else if ( 95 > value && value >= 75 ){
        td.style.color = "#d72dd7"
    //blue
    }else if ( 75 > value && value >= 50 ){
        td.style.color = "#2d59db"
    //green
    }else if ( 50 > value && value >= 25 ){
        td.style.color = "lightgreen"
    //grey
    }else if ( 25 > value && value >=  0){
        td.style.color = "white"
    }
    td.style.fontSize = "20"
    td.style.textShadow = "0 0 black"
    return td
}

function addEntryToTable(state){
    name = document.getElementById("Name").value
    server = document.getElementById("Server").value
    region = document.getElementById("Region").options[document.getElementById("Region").selectedIndex].value
    user = [name, server, region]
    player_list.push([name, server, region])
    //userarray = JSON.stringify([user])
    gSFZ_getDataViaFetch(player_list, state)
}


async function getFFLOGSapiPlayerData(player = "", customTextblock = "", includeName = false, latestRaid = null, unrealId = null, latestPrimal = null, rerun = false) {
    access_key = localStorage.getItem('fflogs_token')
    if (access_key === undefined) {
        access_key = getNewAccessKey();
    }
    // get ids by api https://www.fflogs.com:443/v1/zones?api_key={KEY} and looking for bossid e.g. 1071
    if (latestRaid === null) {
        latestRaid = "68";
    }
    if (unrealId === null) {
        unrealId = "64";
    }
    if (latestPrimal === null) {
        latestPrimal = "67";
    }

    let query_player = "";
    for (const p of player) {
        //console.log(p)
        const [name, server, region] = p;
        if (["-", "--", "---"].includes(name)) {
            continue;
        }
        const name1 = name.replace(/\s/g, '').replace(/'/g, '');
        let textblock = "";
        if (customTextblock === '') {
            textblock += `${name1}_${server}_${region}: character(name: \\"${name}\\", serverSlug: \\"${server}\\", serverRegion: \\"${region}\\")`
            textblock += `{ canonicalID, lodestoneID, name, server { name, region { compactName } },`
            textblock += `UCoB_4: zoneRankings(zoneID: 19, metric: rdps),`
            textblock += `UWU_4: zoneRankings(zoneID: 23, metric: rdps),`
            textblock += `Ultimates_SHB_5: zoneRankings(zoneID: 30, metric: rdps),`
            textblock += `Ultimates_5: zoneRankings(zoneID: 32, metric: rdps),`
            textblock += `Ultimates_Legacy_6: zoneRankings(zoneID: 43, metric: rdps),`
            textblock += `DSU_6: zoneRankings(zoneID: 45, metric: rdps),`
            textblock += `TOP_6: zoneRankings(zoneID: 53, metric: rdps),`
            textblock += `Ultimates_Legacy_7: zoneRankings(zoneID: 59, metric: rdps),`
            textblock += `FRU_7: zoneRankings(zoneID: 65, metric: rdps),`
            textblock += `LATEST_RAID: zoneRankings(zoneID: ${latestRaid}, metric: rdps, difficulty: 101),`
            textblock += `UNREAL_Primals: zoneRankings(zoneID: ${unrealId}, metric: rdps),`
            textblock += `LATEST_Primals: zoneRankings(zoneID: ${latestPrimal}, metric: rdps)`
            textblock += `},`;
        } else {
            textblock = customTextblock;
        }
        query_player += textblock;
    }
    let payload = `{"query":"query char_to_id { characterData { ${query_player} } }","variables":{} }`;
    payload = payload.replace(/\s+/, " ")
    payload = `${payload}`;
    console.log("[getFFLOGSapiPlayerData] Query:")
    console.log(payload.replace("\\", ""))

    const headers = {
        'Authorization': `Bearer ${access_key}`,
        "Origin": "*",
        "Access-Control-Allow-Origin": "no-cors",
        'Content-Type': 'application/json'
    };
    const url = "https://www.fflogs.com/api/v2/client";


    const response = await fetch(url, {
        method: "POST",
        headers: headers,
        body: payload
    })
    let jsonData;
    try {
        jsonData = (await response.json()).data.characterData;
    } catch(err) {
        console.log("[getFFLOGSapiPlayerData] Error:")
        console.log(err)
        if (!rerun){
            setNewAccessToken()
            getFFLOGSapiPlayerData(player, customTextblock, includeName, latestRaid, unrealId, latestPrimal, rerun=true)
        }
        return
    }
    const player_result = {};

    for (player_key in jsonData) {
        player_data = jsonData[player_key]
        try {
            player_server = player_data['server']
            player_result[player_data['name']] = {
                'lodestone_id': player_data['lodestoneID'],
                'fflogs_id': player_data['canonicalID'],
                'link': `https://de.fflogs.com/character/${player_server["region"]["compactName"]}/${player_server["name"]}/${player_data["name"]}`
            }
            for (fight_category in player_data) {
                category_data = player_data[fight_category]
                if (typeof category_data != "object") {
                    continue
                }
                if (category_data['name'] != undefined) {
                    continue
                }
                for (entry_key in category_data['rankings']){
                    entry = category_data['rankings'][entry_key]
                    _id = String(entry['encounter']['id'])
                    _id = fixIDs(_id)
                    if (entry['rankPercent'] == null) {
                        entry['rankPercent'] = -1
                    }
                    console.log(entry['totalKills'])
                    if (includeName) {
                        player_result[player_data['name']][_id]['name'] = entry['encounter']['name']
                    }

                    // add template if fight is not already added
                    if (player_result[player_data['name']][_id] == undefined) {
                        player_result[player_data['name']][_id] = {'historical': entry['rankPercent'], 'job': entry['spec'], 'kills': entry['totalKills']}
                        continue
                    }
                    // if fight was already added, but new entry has a higher percent, we update it, for kills we add them together
                    if (player_result[player_data['name']][_id]['historical'] < entry['rankPercent']) {
                        player_result[player_data['name']][_id] = {'historical': entry['rankPercent'], 'job': entry['spec'], 'kills': player_result[player_data['name']][_id]['kills']}
                    }

                    if (entry['totalKills'] > 0) [
                        player_result[player_data['name']][_id]['kills'] += entry['totalKills']
                    ]


                }
            }
        } catch(err) {
            console.log("[getFFLOGSapiPlayerData] Error:")
            console.log(err)
            console.log(`Error when loading user ${player_key}`)
        }
    }
    return player_result
}

async function getNewAccessKey(bearer) {
    const url = "https://www.fflogs.com/oauth/token";

    const payload = 'grant_type=client_credentials';
    const headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + bearer
    };

    return await fetch(url, {
        method: 'POST',
        headers: headers,
        body: payload
    })
    .then(response => response.json())
    .then(data => data.access_token);
}

function setNewAccessToken() {
    bearer = localStorage.getItem('fflogs_bearer') || document.getElementById('bearer').value
    localStorage.setItem('fflogs_bearer', bearer)
    Promise.all([getNewAccessKey(bearer)]).then((values) => {
        localStorage.setItem('fflogs_token', values[0])
        document.getElementById('token').value = values[0]
    });
}

document.getElementById('bearer').value = localStorage.getItem('fflogs_bearer')
document.getElementById('token').value = localStorage.getItem('fflogs_token')
gSFZ_getDataViaFetch(player_list, false)
