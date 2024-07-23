
var result = {}
var player_list = [];
if (localStorage.getItem('fflogs_isAku')){
    player_list = [
         ["Akurosia Kamo", "Shiva", "EU"],
         ["---", "", ""],
         ["Nana Mejyna", "Odin", "EU"],
         ["Ieni Telara", "Odin", "EU"],
         ["Loucid Dreaming", "Odin", "EU"],
         ["Aegir Ragnaroek", "Raiden", "EU"],
         ["Dragomir Xertuz", "Shiva", "EU"],
         ["Shira Noyuki", "Shiva", "EU"],
         ["Rhotgeim Igarashi", "Odin", "EU"],
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


         //["Miyuki Mizu", "Twintania", "EU"],
         //["Filianore Void", "Shiva", "EU"],
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
    ]
}
// fix also in python_module > __init__.getFFLOGSapiPlayerData
figths = {
    1060: ["UCoB"],
    1061: ["UWU"],
    1062: ["TEA"],
    1065: ["DSU"],
    1068: ["TOP"],

    93: ["R1N"],
    94: ["R2N"],
    95: ["R3N"],
    96: ["R4N"],
    //92: ["P12S_P2"],

    //3008: ["Thordan"],
    1071: ["Valigarmanda"],
    1072: ["Zoraal Ja"],
}

fight_ids = [1060,1061,1062,1065,1068,93,94,95,96,1071,1072]

function fixIDs(_id) {
    if (["1039", "1047", "1060", "1073"].includes(_id)) { // 1039=SB 1047=SHB 1060=EW   FIX OLD UCoB
        _id = "1060"
    }
    if (["1042", "1048", "1061", "1074"].includes(_id)) { // 1042=SB 1048=SHB 1061=EW   FIX OLD UWU
        _id = "1061"
    }
    if (["1050", "1062", "1075"].includes(_id)) { // 1050=SHB 1062=EW FIX OLD TEA
        _id = "1062"
    }
    if (["1065", "1076"].includes(_id)) { // 1065=EW FIX OLD DSU
        _id = "1065"
    }
    if (["1068", "1077"].includes(_id)) { // 1068=EW FIX OLD TOP
        _id = "1068"
    }
    return _id
}

const currentDate = new Date();
function gSFZ_getDataViaFetch(user, state){
    //url = "https://ffxivapi.akurosia.de/ffxiv/fflogsapi/getPlayer?player=" + user
    //console.log(url)
    //fetch(url)
    //  .then(response => response.json())
    //  .then(data => JSON.parse(data))
    //  .then(data => printTable(data))

    // state is only set if the button was pressed manually in the frontend
    if (localStorage.getItem('player_data') && currentDate.getTime() < localStorage.getItem('last_access') && !state) {
        remaining = (localStorage.getItem('last_access') - currentDate.getTime()) / 60000
        console.log(`Get Cached Data (${remaining})`)
        printTable(JSON.parse(localStorage.getItem('player_data')))
    } else {
        console.log("Get New Data")
        prom = getFFLOGSapiPlayerData(player = user, customTextblock = "", includeName = false)
        Promise.all([prom]).then((values) => {
            next5min = new Date(currentDate.getTime() + 5 * 60000).getTime()
            localStorage.setItem('player_data', JSON.stringify(values[0]))
            localStorage.setItem('last_access', next5min)
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
    a.style = "color: blue !important"
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
    td.style = "color: blue !important; font-size: 20px; text-shadow: black 0px 0px;"
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
    table.className = "table table-striped table-dark table-hover bg-slate text-light border-gold-metallic";
    table.setAttribute("id", "table_fflogs");
    head = addThead(result)
    table.appendChild(head)
    table.appendChild(addTbody(result))
    //table.appendChild(head)
    x.appendChild(table)
}

// normal job icons
jobs = {
    "Paladin":     "062119_hr1.png",
    "Warrior":     "062121_hr1.png",
    "DarkKnight":  "062132_hr1.png",
    "Gunbreaker":  "062137_hr1.png",
    "WhiteMage":   "062124_hr1.png",
    "Scholar":     "062128_hr1.png",
    "Astrologian": "062133_hr1.png",
    "Sage":        "062140_hr1.png",
    "Monk":        "062120_hr1.png",
    "Dragoon":     "062122_hr1.png",
    "Ninja":       "062130_hr1.png",
    "Samurai":     "062134_hr1.png",
    "Reaper":      "062139_hr1.png",
    "Viper":       "062141_hr1.png",
    "Bard":        "062123_hr1.png",
    "Machinist":   "062131_hr1.png",
    "Dancer":      "062138_hr1.png",
    "BlackMage":   "062125_hr1.png",
    "Summoner":    "062127_hr1.png",
    "RedMage":     "062135_hr1.png",
    "Pictomancer": "062142_hr1.png"
}
//golden icons
jobs = {
    "Paladin":     "062019_hr1.png",
    "Warrior":     "062021_hr1.png",
    "DarkKnight":  "062032_hr1.png",
    "Gunbreaker":  "062037_hr1.png",
    "WhiteMage":   "062024_hr1.png",
    "Scholar":     "062028_hr1.png",
    "Astrologian": "062033_hr1.png",
    "Sage":        "062040_hr1.png",
    "Monk":        "062020_hr1.png",
    "Dragoon":     "062022_hr1.png",
    "Ninja":       "062030_hr1.png",
    "Samurai":     "062034_hr1.png",
    "Reaper":      "062039_hr1.png",
    "Viper":       "062041_hr1.png",
    "Bard":        "062023_hr1.png",
    "Machinist":   "062031_hr1.png",
    "Dancer":      "062038_hr1.png",
    "BlackMage":   "062025_hr1.png",
    "Summoner":    "062027_hr1.png",
    "RedMage":     "062035_hr1.png",
    "Pictomancer": "062042_hr1.png"
}
function addJobImage(job){
    return '<img loading="lazy" src="https://xivapi.com/i/062000/' + jobs[job] + '" style="height: 30px; padding-right: 5px;">'
}

function addRow(tr, result, name, encounterID){
    td = document.createElement("td")
    console.log(result[name][encounterID])
    console.log(encounterID)
    if (parseInt(result[name][encounterID]['historical']) !== -1) {
        td.innerHTML = addJobImage(result[name][encounterID]['job']) + parseInt(result[name][encounterID]['historical'])
    }
    td = colorize(td, parseInt(result[name][encounterID]['historical']))
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
        td.style.color = "purple"
    //blue
    }else if ( 75 > value && value >= 50 ){
        td.style.color = "blue"
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
      latestRaid = "62";
    }
    if (unrealId === null) {
      unrealId = "46";
    }
    if (latestPrimal === null) {
      latestPrimal = "58";
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
            textblock += `LATEST_RAID: zoneRankings(zoneID: ${latestRaid}, metric: rdps, difficulty: 100),`
            //textblock += `UNREAL_Primals: zoneRankings(zoneID: ${unrealId}, metric: rdps),`
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
    console.log(payload)

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
                    if (player_result[player_data['name']][_id] == undefined) {
                        player_result[player_data['name']][_id] = {'historical': entry['rankPercent'], 'job': entry['spec']}
                    }
                    if (player_result[player_data['name']][_id]['historical'] < entry['rankPercent']) {
                        player_result[player_data['name']][_id] = {'historical': entry['rankPercent'], 'job': entry['spec']}
                    }
                    if (includeName) {
                        player_result[player_data['name']][_id]['name'] = entry['encounter']['name']
                    }
                }
            }
        } catch(err) {
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
