#!/usr/bin/env python3
# coding: utf8
import os
import sys
from ffxiv_aku import *
from ffxiv_aku import storeFilesInTmp, get_skills_for_player, loadDataTheQuickestWay, get_any_Logdata
from collections import OrderedDict
from operator import getitem
import traceback

skills = None
pvpskills = None
logdata = None
cj = None
cjs = None
actions = None
actions_trans = None
action_trans = None
aozaction_trans = None
lo_actions = None
bo_actions = None
craftactions_trans = None
status_trans = None
status = None
traits = None
traits_trans = None
traitstransient_trans = None
aozactions_trans = None
aozactiontransient = None
quests = None
quests_trans = None
levels = None
maps = None
leves = None
trans_leves = None
craftleves = None
chocoboskills_trans = None
chocoboitems_trans = None
chocobochallange_trans = None
buddyskill_raw = None
addon_trans = None
items_trans = None

disable_print = True
status_ncj = None


def load_global_data():
    global skills
    global pvpskills
    global logdata
    global addon_trans
    global cjs_trans
    global cjs
    global actions
    global actions_trans
    global actiontransient_trans
    global aozaction_trans
    global lo_actions
    global bo_actions
    global craftactions_trans
    global status_trans
    global status
    global traits
    global traits_trans
    global traitstransient_trans
    global aozactions_trans
    global aozactiontransient
    global quests
    global quests_trans
    global levels
    global maps
    global leves
    global trans_leves
    global craftleves
    global items_trans

    global chocoboskills_trans
    global chocoboitems_trans
    global chocobochallange_trans
    global buddyskill_raw
    storeFilesInTmp(True)
    skills = get_skills_for_player()
    pvpskills = get_skills_for_player(True)
    logdata = get_any_Logdata()
    cjs_trans = loadDataTheQuickestWay("classjob", translate=True)
    cjs = loadDataTheQuickestWay("ClassJob")
    actions = loadDataTheQuickestWay("action")
    addon_trans = loadDataTheQuickestWay("addon", translate=True)
    actions_trans = loadDataTheQuickestWay("action", translate=True)
    actiontransient_trans = loadDataTheQuickestWay("actiontransient", translate=True)
    aozaction_trans = loadDataTheQuickestWay("aozactiontransient", translate=True)
    lo_actions = loadDataTheQuickestWay("eurekamagiaaction.json")
    bo_actions = loadDataTheQuickestWay("MYCTemporaryItem.json")
    craftactions_trans = loadDataTheQuickestWay("craftaction", translate=True)
    status_trans = loadDataTheQuickestWay("status", translate=True)
    status = loadDataTheQuickestWay("Status")
    traits = loadDataTheQuickestWay("Trait")
    traits_trans = loadDataTheQuickestWay("trait", translate=True)
    traitstransient_trans = loadDataTheQuickestWay("TraitTransient", translate=True)
    aozactions_trans = loadDataTheQuickestWay("aozaction", translate=True)
    aozactiontransient = loadDataTheQuickestWay("AozActionTransient")
    quests = loadDataTheQuickestWay("Quest")
    quests_trans = loadDataTheQuickestWay("quest", translate=True)
    items_trans = loadDataTheQuickestWay("item", translate=True)
    levels = loadDataTheQuickestWay("Level.json")
    maps = loadDataTheQuickestWay("Map.json")
    leves = loadDataTheQuickestWay("leve")
    trans_leves = loadDataTheQuickestWay("leve", translate=True)
    craftleves = loadDataTheQuickestWay("craftleve.json")
    chocoboskills_trans = loadDataTheQuickestWay("chocoboraceability", translate=True)
    chocoboitems_trans = loadDataTheQuickestWay("chocoboraceitem", translate=True)
    chocobochallange_trans = loadDataTheQuickestWay("chocoboracechallenge", translate=True)
    buddyskill_raw = loadDataTheQuickestWay("buddyskill.json", exd="raw-exd-all")


def getImage(image: str) -> str:
    image = image.replace(".tex", "_hr1.png")
    image = image.replace("ui/icon/", "")
    return image


def getBLULocationsFromLogdata(name, locations):
    global logdata
    if not name:
        return locations
    nresult = locations
    for location_name, location_data in logdata.items():
        if not location_name:
            continue
        for enemy_name, enemy_data in location_data.items():
            if not enemy_name or isinstance(enemy_data, list):
                continue
            for skill_id, skill_data in enemy_data.get("skill", {}).items():
                if not skill_id or not skill_data:
                    continue
                if name.lower() == skill_data["name"].lower():
                    tmp = {"Ort": location_name, "Gegner": enemy_name}
                    if tmp not in nresult:
                        nresult.append(tmp)
    return nresult


def fix_slug(name):
    return (
        name.lower()
            .replace("ö", "oe")
            .replace("ä", "ae")
            .replace("ü", "ue")
            .replace("ß", "ss")
            .replace(" ", "_")
            .replace(")(", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "_")
            .replace("'", "")
            .replace(":", "_")
            .replace("__", "_")
            .replace("__", "_")
    )


def get_propper_zone_name(zone_name, files):
    n = fix_slug(zone_name)
    for file in files:
        if n in file:
            return file.split("\\")[0].replace("_new", "") + "/" + n.replace("_", "-") + ".html"
    return None


def get_blue_totem_skills():
    global items_trans
    result = ["Wasserkanone"]
    for key, value in items_trans.items():
        if "Totem der Blaumagie:" in value['Name_de']:
            result.append(value['Name_de'].replace("Totem der Blaumagie: ", ""))
    return result


def get_play_in_locations(locations):
    cfc = loadDataTheQuickestWay("ContentFindercondition")
    cmt = loadDataTheQuickestWay("ContentMemberType.json")
    new_locations = []
    for key, value in cfc.items():
        player = 0
        for loc in locations:
            if value['Name'].lower() == loc['Ort'].lower():
                if value['TerritoryType'] == "w1tz":
                    loc["player"] = 1
                    loc["type"] = "Große Maskerade Masked Carnivale Himmlische Arena"
                else:
                    x = cmt[value['ContentMemberType'].split('#')[1]]
                    player = int(x['HealersPerParty']) + int(x['MeleesPerParty']) + int(x['RangedPerParty']) + int(x['TanksPerParty'])
                    loc["player"] = 1 if player == 0 else player
                    loc["type"] = value['ContentType']
                    new_locations.append(loc)
                #print(value)
    for loc in locations:
        found = False
        for loc2 in new_locations:
            if loc['Ort'] == loc2['Ort']:
                found = True
        if not found:
            new_locations.append(loc)
    return sorted(new_locations, key=lambda x: x['Ort'])


def addBlueAttackDetails(job_data):
    global actions_trans
    global aozactions_trans
    global aozactiontransient
    result = ""
    result += "    attacks:\n"
    # get special aoz action data from correct files e.g. number in blu spell book and description
    blueTotemSpells = get_blue_totem_skills()
    blueTotemCondition = {
        "Wasserkanone": "Blaumagier freischalten",
        "Weißer Wind": "10 Zauber gelernt",
        "Einschüchtern": "5 Zauber gelernt",
        "Assimilation": "20 Zauber gelernt",
        "Totalabwehr": "10 Zauber gelernt",
        "Mondflöte": "10 Mission der Himmlichen Arena abgeschlossen",
        "Verhängnis": "20 Mission der Himmlichen Arena abgeschlossen",
        "Rachestoß": "50 Zauber gelernt",
        "Engelsflüstern": "30 Mission der Himmlichen Arena abgeschlossen",
        "Engelspeise": "Level 70 mit dem Blaumagier erreicht",
        "Drachenkraft": "100 Zauber gelernt",
        "Matra-Magie": "100 Zauber gelernt",
        "Zauberatem": "Level 80 mit dem Blaumagier erreicht",
        "Kraftfeld": "120 Zauber gelernt"
    }
    for x, y in job_data.items():
        for key, value in aozactions_trans.items():
            if y['Name'] == value['Name_de']:
                if not aozactiontransient[key]['Location'] == "":
                    job_data[x]["Location"] = {"Ort": aozactiontransient[key]['Location'], "Gegner": "(InGame Hinweis)"}
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = aozactiontransient[key]['Number']

                job_data[x]["Description_de"] += "\n\n<br/>#########################################<br/>\n\n" + aozaction_trans[key]['Description_de']
                job_data[x]["Description_en"] += "\n\n<br/>#########################################<br/>\n\n" + aozaction_trans[key]['Description_en']
                job_data[x]["Description_fr"] += "\n\n<br/>#########################################<br/>\n\n" + aozaction_trans[key]['Description_fr']
                job_data[x]["Description_ja"] += "\n\n<br/>#########################################<br/>\n\n" + aozaction_trans[key]['Description_ja']
                job_data[x]["Description_cn"] += "\n\n<br/>#########################################<br/>\n\n" + aozaction_trans[key]['Description_cn']
                job_data[x]["Description_ko"] += "\n\n<br/>#########################################<br/>\n\n" + aozaction_trans[key]['Description_ko']
            elif y['Name'] == "Weißer Tod":
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = "84"
            elif y['Name'] == "Göttlicher Katarakt":
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = "89"

        if not y.get("Number", None):
            job_data[x]["Number"] = job_data[x]["Level"]
            job_data[x]["Level"] = "90" + job_data[x]["Level"]

    files = glob("**/**/*.md")

    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, skill_data in job_data.items():
        try:
            locations = []
            if skill_data.get('Location', None):
                locations.append(skill_data['Location'])
            de_name = actions_trans.get(skill_data["id"], {}).get("Name_de", "")
            en_name = actions_trans.get(skill_data["id"], {}).get("Name_en", "")
            fr_name = actions_trans.get(skill_data["id"], {}).get("Name_fr", "")
            ja_name = actions_trans.get(skill_data["id"], {}).get("Name_ja", "")
            cn_name = actions_trans.get(skill_data["id"], {}).get("Name_cn", "")
            ko_name = actions_trans.get(skill_data["id"], {}).get("Name_ko", "")
            if en_name == "":
                en_name = craftactions_trans[skill_data["id"] + ".0"]["Name_en"]
            level = skill_data['Level']
            #
            locations = getBLULocationsFromLogdata(skill_data["Name"], locations)
            locations = sorted(locations, key=lambda x: x['Ort'])
            # somehow original locations got updated, just dont touch it
            n_locations = get_play_in_locations(locations)
            desc = ""
            terms = []

            if not locations == [] or de_name in blueTotemSpells:
                desc += "\n\n<br/>#########################################<br/>\n\nLOCATIONS:\n"
                # special case to add totem entries
                if de_name in blueTotemSpells:
                    desc += "<table class='table-striped table-dark table-hover bg-charcoal text-light border-gold-metallic'><thead><td>Zone</td><td>Gegnername</td><td>Bedinnung</td></thead><tbody>"
                    desc += f"<tr><td>Ul'dah - Thal-Kreuzgang (X:12.5 Y:12.9)</td><td> Wayward Gaheel Ja (Totem der Blaumagie: {de_name})</td><td> {blueTotemCondition[de_name]} </td></tr>"
                    terms.append("Totems")
                else:
                    desc += "<table class='table-striped table-dark table-hover bg-charcoal text-light border-gold-metallic'><thead><td>Zone</td><td>Gegnername</td></thead><tbody>"
                    for location in locations:
                        zone_name = location["Ort"]
                        enemy_name = location["Gegner"]
                        if location.get('player', None):
                            if f"{location['player']}man" not in terms:
                                terms.append(f"{location['player']}man")
                        if location.get('type', None):
                            if location['type'] not in terms:
                                terms.append(location['type'])
                        p_zone_name = get_propper_zone_name(zone_name, files)
                        tmp = f"<tr><td>{zone_name} </td><td> {enemy_name}</td></tr>"
                        #tmp = "\n&emsp;" + f"{zone_name} -> {enemy_name}"
                        if p_zone_name:
                            tmp = f"<tr><td><a href='/DevFFXIVPocketGuide/{p_zone_name}' target='_blank'>{zone_name} </a></td><td> {enemy_name}</td></tr>"
                            #tmp = "\n&emsp;" + f"<a href='{p_zone_name}' target='_blank'>{zone_name}</a> -> {enemy_name}"
                        desc += tmp
            desc += "</tbody></table>"

            desc = desc.replace("\n", "</br>").replace("</br></br>", "</br>")
            if skill_data.get("Number", None) and int(level) < 901:
                result += f'      - title:\n'
                result += f'          de: "{level}. {de_name}"\n'
                result += f'          en: "{level}. {en_name}"\n'
                result += f'          fr: "{level}. {fr_name}"\n'
                result += f'          ja: "{level}. {ja_name}"\n'
                result += f'          cn: "{level}. {cn_name}"\n'
                result += f'          ko: "{level}. {ko_name}"\n'
            else:
                result += f'      - title:\n'
                result += f'          de: "{de_name}"\n'
                result += f'          en: "{en_name}"\n'
                result += f'          fr: "{fr_name}"\n'
                result += f'          ja: "{ja_name}"\n'
                result += f'          cn: "{cn_name}"\n'
                result += f'          ko: "{ko_name}"\n'
            result += f'        title_id: "{skill_data["id"].split(".")[0]}"\n'
            if skill_data.get("Number", None):
                result += f'        level: "{skill_data["Number"]}"\n'
            else:
                result += f'        level: "{level}"\n'

            result += f'        terms:\n'
            for term in terms:
                result += f'          - term: "{term}"\n'
            result += f'        icon: "{getImage(skill_data["Icon"])}"\n'
            result += f'        range: "{skill_data["Range"]}"\n'
            result += f'        effectrange: "{skill_data["EffectRange"]}"\n'
            result += f'        cast: "{skill_data["Cast"]}"\n'
            result += f'        recast: "{skill_data["Recast"]}"\n'
            result += f'        kategorie: "{skill_data["Kategorie"]}"\n'
            result += f'        description:\n'
            result += f'          de: "' + skill_data["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>").replace('"', '\\"') + f'{desc}"\n'
            result += f'          en: "' + skill_data["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>").replace('"', '\\"') + f'{desc}"\n'
            result += f'          fr: "' + skill_data["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>").replace('"', '\\"') + f'{desc}"\n'
            result += f'          ja: "' + skill_data["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>").replace('"', '\\"') + f'{desc}"\n'
            result += f'          cn: "' + skill_data["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>").replace('"', '\\"') + f'{desc}"\n'
            result += f'          ko: "' + skill_data["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>").replace('"', '\\"') + f'{desc}"\n'
            result += f'        phases:\n'
            result += f'          - phase: "01"\n'
        except:
            traceback.print_exc()
    return result


def convertJobToAbrev(job):
    global cjs_trans
    global cjs
    job_abbr = None
    class_abbr = None
    for key, value in cjs_trans.items():
        if value['Name_de'] == job:
            job_abbr = value['Abbreviation_de']
    _class = [v['ClassJob']['Parent'] for k, v in cjs.items() if v["Name"]['Value'] == job][0]
    for key2, value2 in cjs_trans.items():
        if value2['Name_de'] == _class:
            class_abbr = value2['Abbreviation_de']

    if not job_abbr == "" or not class_abbr == "":
        return job_abbr, class_abbr
    raise NotImplementedError


def addAttackDetails(job_data, pvp=False):
    global actions_trans
    global craftactions_trans
    result = ""
    # only print for normal attacks
    if not pvp:
        result += "    attacks:\n"

    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, skill_data in job_data.items():
        #print_color_red(pretty_json(skill_data) + "\n")
        de_name = actions_trans.get(skill_data["id"], {}).get("Name_de", "").replace("\n", "</br>").replace("</br></br>", "</br>")
        en_name = actions_trans.get(skill_data["id"], {}).get("Name_en", "").replace("\n", "</br>").replace("</br></br>", "</br>")
        fr_name = actions_trans.get(skill_data["id"], {}).get("Name_fr", "").replace("\n", "</br>").replace("</br></br>", "</br>")
        ja_name = actions_trans.get(skill_data["id"], {}).get("Name_ja", "").replace("\n", "</br>").replace("</br></br>", "</br>")
        cn_name = actions_trans.get(skill_data["id"], {}).get("Name_cn", "").replace("\n", "</br>").replace("</br></br>", "</br>")
        ko_name = actions_trans.get(skill_data["id"], {}).get("Name_ko", "").replace("\n", "</br>").replace("</br></br>", "</br>")
        if en_name == "":
            de_name = craftactions_trans[skill_data["id"]]["Name_de"].replace("\n", "</br>").replace("</br></br>", "</br>")
            en_name = craftactions_trans[skill_data["id"]]["Name_en"].replace("\n", "</br>").replace("</br></br>", "</br>")
            fr_name = craftactions_trans[skill_data["id"]]["Name_fr"].replace("\n", "</br>").replace("</br></br>", "</br>")
            ja_name = craftactions_trans[skill_data["id"]]["Name_ja"].replace("\n", "</br>").replace("</br></br>", "</br>")
            cn_name = craftactions_trans[skill_data["id"]]["Name_cn"].replace("\n", "</br>").replace("</br></br>", "</br>")
            ko_name = craftactions_trans[skill_data["id"]]["Name_ko"].replace("\n", "</br>").replace("</br></br>", "</br>")
        level = "0" if skill_data['Level'] == "99999" else skill_data['Level']
        desc = actiontransient_trans.get(skill_data["id"].split(".")[0], None)
        if not desc:
            desc = craftactions_trans[skill_data["id"].split(".")[0]]
        de_desc = desc["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>")
        en_desc = desc["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>")
        fr_desc = desc["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>")
        ja_desc = desc["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>")
        cn_desc = desc["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>")
        ko_desc = desc["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>")
        result += '      - title:\n'
        result += f'          de: "{de_name}"\n'
        result += f'          en: "{en_name}"\n'
        result += f'          fr: "{fr_name}"\n'
        result += f'          ja: "{ja_name}"\n'
        result += f'          cn: "{cn_name}"\n'
        result += f'          ko: "{ko_name}"\n'
        result += f'        title_id: "{skill_data["id"].split(".")[0]}"\n'
        result += f'        level: "{level}"\n'
        result += f'        type: "{skill_data["Type"]}"\n'
        result += f'        icon: "{getImage(skill_data["Icon"])}"\n'
        result += f'        range: "{skill_data["Range"]}"\n'
        result += f'        effectrange: "{skill_data["EffectRange"]}"\n'
        result += f'        cast: "{skill_data["Cast"]}"\n'
        result += f'        recast: "{skill_data["Recast"]}"\n'
        result += f'        kategorie: "{skill_data["Kategorie"]}"\n'
        result += '        description:\n'
        result += '          de: "' + de_desc + '"\n'
        result += '          en: "' + en_desc + '"\n'
        result += '          fr: "' + fr_desc + '"\n'
        result += '          ja: "' + ja_desc + '"\n'
        result += '          cn: "' + cn_desc + '"\n'
        result += '          ko: "' + ko_desc + '"\n'
        #if "Reduces damage" in desc["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>"):
        #    print(en_name)
        result += '        phases:\n'
        if pvp:
            result += '          - phase: "04"\n'
        else:
            result += '          - phase: "01"\n'
    return result


def addStatusDetails(job, job_abb):
    global logdata
    global status_trans
    global status_ncj
    result = ""
    jobstatusdata = logdata["Klassen"].get(job, {}).get("status", {})
    for key, value in status_ncj[job_abb].items():
        if key not in jobstatusdata:
            jobstatusdata[key] = value
    if not jobstatusdata == {}:
        jobstatusdata = OrderedDict(sorted(jobstatusdata.items(), key=lambda x: getitem(x[1], 'name')))
        result += "    debuffs:\n"
        for key, s in jobstatusdata.items():
            _id = str(int(key, 16))
            result += '      - title:\n'
            result += '          de: "' + status_trans[_id]["Name_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += '          en: "' + status_trans[_id]["Name_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += '          fr: "' + status_trans[_id]["Name_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += '          ja: "' + status_trans[_id]["Name_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += '          cn: "' + status_trans[_id]["Name_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += '          ko: "' + status_trans[_id]["Name_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += f'        title_id: "{key}"\n'
            if "_hr1" in getImage(s["icon"]):
                result += f'        icon: "{getImage(s["icon"])}"\n'
            else:
                result += f'        icon: "{getImage(s["icon"]).replace(".png", "_hr1.png")}"\n'
            result += '        description:\n'
            result += '          de: "' + status_trans[_id]["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += '          en: "' + status_trans[_id]["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += '          fr: "' + status_trans[_id]["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += '          ja: "' + status_trans[_id]["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += '          cn: "' + status_trans[_id]["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result += '          ko: "' + status_trans[_id]["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            if s['duration']:
                result += f'        durations: {s["duration"]}\n'
            result += '        phases:\n'
            result += '          - phase: "02"\n'
    return result


def addTraitDetails(job):
    global traits
    # TODO get traits by class
    result = ""
    result += "    traits:\n"
    _class = [v['ClassJob']['Parent'] for k, v in cjs.items() if v["Name"]['Value'] == job]
    traits_transs = {k: v for k, v in traits.items() if v["ClassJob"] in ([job] + _class)}
    job_trait_data = OrderedDict(sorted(traits_transs.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, trait_data in job_trait_data.items():
        if not trait_data.get("Icon", None):
            continue
        level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        result += '      - title:\n'
        result += '          de: "' + traits_trans[_id]["Name_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          en: "' + traits_trans[_id]["Name_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          fr: "' + traits_trans[_id]["Name_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ja: "' + traits_trans[_id]["Name_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          cn: "' + traits_trans[_id]["Name_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ko: "' + traits_trans[_id]["Name_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'        title_id: "{_id.split(".")[0]}"\n'
        result += f'        level: "{level}"\n'
        result += f'        icon: "{getImage(trait_data["Icon"].replace(".tex", "_hr1.png"))}"\n'
        result += '        description:\n'
        result += '          de: "' + traitstransient_trans[_id]["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          en: "' + traitstransient_trans[_id]["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          fr: "' + traitstransient_trans[_id]["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ja: "' + traitstransient_trans[_id]["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          cn: "' + traitstransient_trans[_id]["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ko: "' + traitstransient_trans[_id]["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '        phases:\n'
        result += '          - phase: "03"\n'
    return result


def getStatusKey(stat):
    for k, v in status.items():
        if v["Name"] == stat:
            return k
    return "0"


def getEurekaActionDetails():
    results = {}
    new_lo_actions = {}
    # get all eurekamagiaaction
    for x, v in lo_actions.items():
        _id = int(x.split(".")[0])
        new_lo_actions[_id] = v

    for k, i in actions.items():
        for k2, lo in new_lo_actions.items():
            if i["Name"] == lo["Action"] and not i["Name"] == "":
                if k2 not in results:
                    status_key = getStatusKey(i["Status"]['GainSelf'])
                    results[k] = {
                        "name": {
                            "de": actions_trans[k]['Name_de'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "en": actions_trans[k]['Name_en'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "fr": actions_trans[k]['Name_fr'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "ja": actions_trans[k]['Name_ja'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "cn": actions_trans[k]['Name_cn'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "ko": actions_trans[k]['Name_ko'].replace("\n", "</br>").replace("</br></br>", "</br>")
                        },
                        "icon": i["Icon"].replace(".png", "_hr1.png"),
                        "type": i["ActionCategory"],
                        "cj": i["ClassJobCategory"],
                        "uses": lo["MaxUses"],
                        "status": {
                            "de": status_trans[status_key]['Name_de'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "en": status_trans[status_key]['Name_en'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "fr": status_trans[status_key]['Name_fr'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "ja": status_trans[status_key]['Name_ja'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "cn": status_trans[status_key]['Name_cn'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "ko": status_trans[status_key]['Name_ko'].replace("\n", "</br>").replace("</br></br>", "</br>")
                        },
                        "status_icon": status_trans[status_key]['Icon'].replace(".tex", "_hr1.png").replace(".png", "_hr1.png"),
                        "description": {
                            "de": actiontransient_trans[k]["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "en": actiontransient_trans[k]["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "fr": actiontransient_trans[k]["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "ja": actiontransient_trans[k]["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "cn": actiontransient_trans[k]["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>"),
                            "ko": actiontransient_trans[k]["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>")
                        },
                    }
                    break
                else:
                    print("Douplicate for " + str(k2))
                    continue
    return results


def getActionDataSet(name):
    for _ida, action in actions.items():
        if action["Name"] == name:
            return _ida, action


def getFrontsplitterEntry(name, result):
    if not name.startswith("Verschollen") and not name.startswith("Gemüt") or not name.startswith("Würfel "):
        return name
    if name.startswith("Gemüt") or name.startswith("Würfel "):
        return "Frontsplitter des " + name
    if name.startswith("Verschollen"):
        new_name = re.split("Verschollen(?:e|es|er) (.*)", name)[1]
        for x, x_data in result["Splitter"].items():
            for y in x_data["Frontsplitter"]:
                if new_name in y:
                    return y
    return ""


def getBozjaActionDetails():
    result = {}
    for _id, action in bo_actions.items():
        if action['Category'] == "":
            continue
        if action['Category'] == "Gegenstände":
            action['Category'] = "ZGegenstände"
        if not result.get(action['Category']):
            result[action['Category']] = {}
        b, a = getActionDataSet(action['Action'])
        icon = a["Icon"].replace(".tex", "_hr1.png")
        if action['Action'] == "Würfel des Schicksals":
            icon = "ui/icon/064000/064690_hr1.png"
        tmp = {
            "name": {
                "de": actions_trans[b]['Name_de'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                "en": actions_trans[b]['Name_en'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                "fr": actions_trans[b]['Name_fr'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                "ja": actions_trans[b]['Name_ja'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                "cn": actions_trans[b]['Name_cn'].replace("\n", "</br>").replace("</br></br>", "</br>"),
                "ko": actions_trans[b]['Name_ko'].replace("\n", "</br>").replace("</br></br>", "</br>")
            },
            "icon": icon,
            "cj": a["ClassJobCategory"],
            "frontsplitter": getFrontsplitterEntry(action['Action'], result),
            "description": {
                "de": actiontransient_trans[b]["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>"),
                "en": actiontransient_trans[b]["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>"),
                "fr": actiontransient_trans[b]["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>"),
                "ja": actiontransient_trans[b]["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>"),
                "cn": actiontransient_trans[b]["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>"),
                "ko": actiontransient_trans[b]["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>")
            },
        }
        result[action['Category']][b] = tmp
    return json.loads(json.dumps(result, indent=4, sort_keys=true, ensure_ascii=false))


def addEurekaActions(job, eureka_actions):
    result = False
    result_text = ""
    result_text += "    eureka:\n"
    _class = [v['Abbreviation'] for k, v in cjs.items() if v["Name"]['Value'] == job]
    for k, value in eureka_actions.items():
        if _class[0] in value['cj']:
            result = True
            # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
            result_text += '      - title:\n'
            result_text += '          de: "' + value["name"]["de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          en: "' + value["name"]["en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          fr: "' + value["name"]["fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          ja: "' + value["name"]["ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          cn: "' + value["name"]["cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          ko: "' + value["name"]["ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '        status:\n'
            result_text += '          de: "' + value["name"]["de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          en: "' + value["name"]["en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          fr: "' + value["name"]["fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          ja: "' + value["name"]["ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          cn: "' + value["name"]["cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          ko: "' + value["name"]["ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += f'        status_icon: "{getImage(value["status_icon"])}"\n'
            result_text += f'        title_id: "{k}"\n'
            result_text += '        level: "70"\n'
            result_text += f'        icon: "{getImage(value["icon"])}"\n'
            result_text += '        description:\n'
            result_text += '          de: "' + value["description"]['de'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          en: "' + value["description"]['en'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          fr: "' + value["description"]['fr'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          ja: "' + value["description"]['ja'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          cn: "' + value["description"]['cn'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += '          ko: "' + value["description"]['ko'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += f'        type: "{value["type"]}"\n'
            result_text += '        phases:\n'
            result_text += '          - phase: "06"\n'
    return result, result_text


def addBozjaActions(job, bozja_actions):
    result = False
    result_text = ""
    result_text += "    bozja:\n"
    _class = [v['Abbreviation'] for k, v in cjs.items() if v["Name"]['Value'] == job]
    for categorie, data in bozja_actions.items():
        for k, value in data.items():
            if _class[0] in value['cj']:
                result = True
                # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
                result_text += '      - title:\n'
                result_text += '          de: "' + value["name"]["de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += '          en: "' + value["name"]["en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += '          fr: "' + value["name"]["fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += '          ja: "' + value["name"]["ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += '          cn: "' + value["name"]["cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += '          ko: "' + value["name"]["ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += f'        title_id: "{k}"\n'
                result_text += '        level: "80"\n'
                result_text += f'        icon: "{getImage(value["icon"])}"\n'
                result_text += '        description:\n'
                result_text += '          de: "' + value["description"]['de'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += '          en: "' + value["description"]['en'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += '          fr: "' + value["description"]['fr'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += '          ja: "' + value["description"]['ja'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += '          cn: "' + value["description"]['cn'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += '          ko: "' + value["description"]['ko'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += f'        frontsplitter: "{value["frontsplitter"]}"\n'
                result_text += '        phases:\n'
                result_text += '          - phase: "07"\n'
    return result, result_text


def translatename(name, lang="en"):
    global trans_leves
    for y, x in trans_leves.items():
        if x["Name_de"] == name:
            return x[f"Name_{lang}"]


def getCrafterLeves():
    global leves
    global craftleves
    final_results = {}
    for leve_id, leve in leves.items():
        new_leve_id = int(leve_id)

        if "Fertigungserlasse" not in leve["JournalGenre"]:
            continue
        for cleve_id, cleve in craftleves.items():
            if leve["Name"] == cleve["Leve"]:
                if not final_results.get(leve["JournalGenre"], None):
                    final_results[leve["JournalGenre"]] = {}
                final_results[leve["JournalGenre"]][new_leve_id] = {
                    "Name_DE": leve["Name"],
                    "Name_EN": translatename(leve["Name"], "en"),
                    "Name_FR": translatename(leve["Name"], "fr"),
                    "Name_JA": translatename(leve["Name"], "ja"),
                    "Name_CN": translatename(leve["Name"], "cn"),
                    "Name_KO": translatename(leve["Name"], "ko"),
                    "0xID": hex(new_leve_id)[2:].upper(),
                    "ID": str(new_leve_id),
                    "item": cleve['Item']["0"],
                    "item_amount": int(cleve['ItemCount']["0"]) + int(cleve['ItemCount']["1"]) + int(cleve['ItemCount']["2"]),
                    "level": leve['ClassJobLevel'],
                    "Start_Leve_Zone": leve['PlaceName']['Issued'],
                    "Start_Leve_NPC": leve['LeveClient'],
                    "Freibriefanzahl": leve["AllowanceCost"],
                    "Wiederholbar": (int(cleve["Repeats"]) + 1) if cleve["Repeats"] != "0" else 1,
                    "EXP_per_full_hq_leve": (int(cleve['Repeats']) + 1) * int(leve['ExpReward']) * 2,
                    "Gil_per_full_hq_leve": (int(cleve['Repeats']) + 1) * int(leve['GilReward']) * 2,
                    "Gil_per_100_hq_leve": (int(cleve['Repeats']) + 1) * int(leve['GilReward']) * 100 * 2,
                }
    return final_results


def getGathererLeves():
    global leves
    final_results = {}
    for leve_id, leve in leves.items():
        new_leve_id = int(str(int(leve_id.split(".")[0])))

        if "Sammelerlasse" not in leve["JournalGenre"]:
            continue
        if not final_results.get(leve["JournalGenre"], None):
            final_results[leve["JournalGenre"]] = {}
        final_results[leve["JournalGenre"]][new_leve_id] = {
            "Name_DE": leve["Name"],
            "Name_EN": translatename(leve["Name"], "en"),
            "Name_FR": translatename(leve["Name"], "fr"),
            "Name_JA": translatename(leve["Name"], "ja"),
            "Name_CN": translatename(leve["Name"], "cn"),
            "Name_KO": translatename(leve["Name"], "ko"),
            "0xID": hex(new_leve_id)[2:].upper(),
            "ID": str(new_leve_id),
            "item": "",
            "item_amount": "",
            #"item": cleve['Item[0]'],
            #"item_amount": cleve['ItemCount[0]'],
            "level": leve['ClassJobLevel'],
            "Start_Leve_Zone": leve['PlaceName']['Issued'],
            "Start_Leve_NPC": leve['LeveClient'],
            "Freibriefanzahl": leve["AllowanceCost"],
            #"Wiederholbar": True if cleve["Repeats"] != "0" else False,
            "EXP_per_full_hq_leve": int(leve['ExpReward']),
            "Gil_per_full_hq_leve": int(leve['GilReward']),
            "Gil_per_100_hq_leve": int(leve['GilReward']) * 100,
        }
    return final_results


def addCrafterLeve(job, all_crafter_leves):
    result = ""
    for key, value in all_crafter_leves.items():
        if job not in key:
            continue
        result += "    leves:\n"
        job_leve_data = OrderedDict(sorted(value.items(), key=lambda x: int(getitem(x[1], 'level'))))
        for _id, leve_data in job_leve_data.items():
            level = "0" if leve_data['level'] == "99999" else leve_data['level']
            result += '      - title:\n'
            result += f'          de: "{leve_data["Name_DE"]}"\n'
            result += f'          en: "{leve_data["Name_EN"]}"\n'
            result += f'          fr: "{leve_data["Name_FR"]}"\n'
            result += f'          ja: "{leve_data["Name_JA"]}"\n'
            result += f'          cn: "{leve_data["Name_CN"]}"\n'
            result += f'          ko: "{leve_data["Name_KO"]}"\n'
            result += f'        title_id: "{leve_data["0xID"]}"\n'
            result += f'        level: "{level}"\n'
            result += f'        leveamount: "{leve_data["Freibriefanzahl"]}"\n'
            if leve_data.get('item', None):
                result += f'        item: "{leve_data["item"]}"\n'
                result += f'        itemamount: "{leve_data["item_amount"]}"\n'
                result += f'        repeat: "{leve_data["Wiederholbar"]}"\n'
            result += f'        exphq: "{leve_data["EXP_per_full_hq_leve"]}"\n'
            result += f'        gilhq: "{leve_data["Gil_per_full_hq_leve"]}"\n'
            result += '        phases:\n'
            result += '          - phase: "04"\n'
        return True, result
    return False, result


def addQuestkDetails(job, pvp):
    global quests
    global quests_trans
    newjob, newclass = convertJobToAbrev(job)
    klassenquests = {}
    for key, quest in quests.items():
        if "Restaurierung der Reliktwaffen" in quest['Name']:
            continue
        if quest['ClassJobCategory']["0"] in [newjob, newclass] or quest['ClassJobCategory']["1"] in [newjob, newclass]:
            # print(" \t" + quest['Name'])
            if quest['Issuer']['Location'] == "":
                continue
            level_data = {}
            try:
                level_data = getLevel(quest['Issuer']['Location'])
                if level_data is None:
                    continue
            except Exception as e:
                print(f"Error in addQuestkDetails: {e}")
                pass
            place = f"{level_data['region']} > {quest['PlaceName']}"
            if not level_data['placename'] in place:
                place + f" > {level_data['placename']}"
            newquest = {
                "name": quest['Name'],
                "id": key,
                "expansion": quest['Expansion'],
                "level": int(quest['ClassJobLevel']["0"]),
                "Icon": quest['Icon']['Value'].replace('.tex', "_hr1.png"),
                "place": place,
                "previousquest": [quest['PreviousQuest']["0"], quest['PreviousQuest']["1"], quest['PreviousQuest']["2"]],
                "journalgenre": quest['JournalGenre'],
                "issuer_location_": f"X: {level_data['x']} / Y: {level_data['y']}",
                "issuer_start_": quest['Issuer']['Start']
            }
            if klassenquests.get(newquest['level'], None):
                klassenquests[newquest['level'] + 0.1] = newquest
            else:
                klassenquests[newquest['level']] = newquest
    result = ""
    result += "    quests:\n"
    for _level in sorted(klassenquests):
        quest = klassenquests[_level]
        de_name = quests_trans.get(quest["id"], {}).get("Name_de", "").replace(" ", "").replace(" ", "")
        en_name = quests_trans.get(quest["id"], {}).get("Name_en", "").replace(" ", "").replace(" ", "")
        fr_name = quests_trans.get(quest["id"], {}).get("Name_fr", "").replace(" ", "").replace(" ", "")
        ja_name = quests_trans.get(quest["id"], {}).get("Name_ja", "").replace(" ", "").replace(" ", "")
        cn_name = quests_trans.get(quest["id"], {}).get("Name_cn", "").replace(" ", "").replace(" ", "")
        ko_name = quests_trans.get(quest["id"], {}).get("Name_ko", "").replace(" ", "").replace(" ", "")
        level = "0" if quest['level'] == "99999" else quest['level']
        # desc = skill_data["Description"].replace("\n", "</br>")
        result += '      - title:\n'
        result += f'          de: "{de_name}"\n'
        result += f'          en: "{en_name}"\n'
        result += f'          fr: "{fr_name}"\n'
        result += f'          ja: "{ja_name}"\n'
        result += f'          cn: "{cn_name}"\n'
        result += f'          ko: "{ko_name}"\n'
        result += f'        title_id: "{quest["id"].split(".")[0]}"\n'
        result += f'        level: "{level}"\n'
        result += f'        expansion: "{quest["expansion"]}"\n'
        result += f'        journalgenre: "{quest["journalgenre"]}"\n'
        result += f'        issuer_location: "{quest["issuer_location_"]}"\n'
        result += f'        issuer_start: "{quest["issuer_start_"]}"\n'
        result += f'        place: "{quest["place"]}"\n'
        result += '        phases:\n'
        if pvp:
            result += '          - phase: "05"\n'
        else:
            result += '          - phase: "04"\n'
    return result


classDetails = {
    "Ninja": {          "date": "2014.10.28", "patchNumber": "2.4", "patchName": "Dreams of Ice", "patchShort": "arr"},
    "Maschinist": {     "date": "2015.06.23", "patchNumber": "3.0", "patchName": "Heavensward", "patchShort": "hw"},
    "Dunkelritter": {   "date": "2015.06.23", "patchNumber": "3.0", "patchName": "Heavensward", "patchShort": "hw"},
    "Astrologe": {      "date": "2015.06.23", "patchNumber": "3.0", "patchName": "Heavensward", "patchShort": "hw"},
    "Samurai": {        "date": "2017.06.20", "patchNumber": "4.0", "patchName": "Stormblood", "patchShort": "sb"},
    "Rotmagier": {      "date": "2017.06.20", "patchNumber": "4.0", "patchName": "Stormblood", "patchShort": "sb"},
    "Blaumagier": {     "date": "2019.01.08", "patchNumber": "4.5", "patchName": "A Requiem for Heroes", "patchShort": "sb"},
    "Revolverklinge": { "date": "2019.06.28", "patchNumber": "5.0", "patchName": "Shadowbringers", "patchShort": "shb"},
    "Tänzer": {         "date": "2019.06.28", "patchNumber": "5.0", "patchName": "Shadowbringers", "patchShort": "shb"},
    "Schnitter": {      "date": "2021.12.07", "patchNumber": "6.0", "patchName": "Endwalker", "patchShort": "ew"},
    "Weiser": {         "date": "2021.12.07", "patchNumber": "6.0", "patchName": "Endwalker", "patchShort": "ew"},
    "Viper": {          "date": "2024.07.02", "patchNumber": "7.0", "patchName": "Dawntrail", "patchShort": "dt"},
    "Piktomant": {      "date": "2024.07.02", "patchNumber": "7.0", "patchName": "Dawntrail", "patchShort": "dt"},
}


def getQuestName(job):
    for key, value in cjs.items():
        if job == value['Name']['Value']:
            if not value['UnlockQuest'] == "0":
                return value['UnlockQuest']
            return ""
    return ""


def getStatusFromFile(ncj):
    klc = [x["Abbreviation_de"] for key, x in ncj]
    default_status = {}
    for k in klc:
        default_status[k] = {}
    for key, s in status.items():
        if s['ClassJobCategory'] in klc:
            default_status[s['ClassJobCategory']][str(hex(int(key)))[2:].upper()] = {
                "name": s['Name'],
                "icon": s['Icon'],
                "duration": None
            }
        elif s['ClassJobCategory'] == "Handwerker":
            for crafter in ['ZMR', 'GRS', 'PLA', 'GLD', 'GER', 'WEB', 'ALC', 'GRM']:
                default_status[crafter][str(hex(int(key)))[2:].upper()] = {
                    "name": s['Name'],
                    "icon": s['Icon'],
                    "duration": None
                }
    return default_status


def addKlassJobs():
    global cjs_trans
    global cjs
    global addon_trans
    global status_ncj
    partybonus = {
        "0": "",
        "1": "1082",
        "2": "1083",
        "3": "1084",
        "4": "1085",
        "5": "1086",
        "6": "1295",
        "7": "1294",
    }
    # for job, job_data in skills.items():
    all_crafter_leves = getCrafterLeves()
    all_gatherer_leves = getGathererLeves()
    eureka_actions = getEurekaActionDetails()
    bozja_actions = getBozjaActionDetails()
    #print_color_yellow(pretty_json(bozja_actions))

    ncj = sorted(cjs_trans.items(), key=lambda item: int(item[0].split(".")[0]))
    status_ncj = getStatusFromFile(ncj)

    counter = 0
    # print_color_red(pretty_json(ncj))
    maxlvl = ""
    for k in ncj:
        job_d = k[1]
        job = job_d['Name_de']
        job_abb = job_d['Abbreviation_de']
        job_data = skills.get(job, None)
        job_data_pvp = pvpskills.get(job, None)
        job_party_bonus = str(cjs[k[0]]['PartyBonus'])
        if job == "Ninja":
            job_party_bonus = "3"
        if not job_data:
            continue
        counter += 1
        #if not job == "Blaumagier":
        #    continue
        print_color_red(job)

        tmpmaxlvl = str(max([int(data["Level"]) for key, data in job_data.items() if int(data['Level']) < 99999]))
        if job == "Blaumagier":
            maxlvl = "80"
        else:
            maxlvl = tmpmaxlvl if tmpmaxlvl > maxlvl else maxlvl

        gear = gear_get(lvl_from=1, lvl_to=int(maxlvl), ilvl_from=1, ilvl_to=999999, rarity=[1, 7, 2, 3, 4], classjob=job_d['Abbreviation_de'], category="Rumpf")
        maxilvl = str(max([int(e["Level_Item"]) for e in gear]))

        filecontent = ""
        filecontent += '---\n'
        filecontent += 'wip: "True"\n'
        filecontent += 'title:\n'
        filecontent += f'  de: "{job_d["Name_de"].title()}"\n'
        filecontent += f'  en: "{job_d["Name_en"].title()}"\n'
        filecontent += f'  fr: "{job_d["Name_fr"].title()}"\n'
        filecontent += f'  ja: "{job_d["Name_ja"].title()}"\n'
        filecontent += f'  cn: "{job_d["Name_cn"].title()}"\n'
        filecontent += f'  ko: "{job_d["Name_ko"].title()}"\n'
        filecontent += 'layout: klassen\n'
        filecontent += 'page_type: guide\n'
        filecontent += 'roletypeinparty:\n'
        filecontent += f'  de: "{addon_trans[partybonus[job_party_bonus]]["Text_de"].title()}"\n'
        filecontent += f'  en: "{addon_trans[partybonus[job_party_bonus]]["Text_en"].title()}"\n'
        filecontent += f'  fr: "{addon_trans[partybonus[job_party_bonus]]["Text_fr"].title()}"\n'
        filecontent += f'  ja: "{addon_trans[partybonus[job_party_bonus]]["Text_ja"].title()}"\n'
        filecontent += f'  cn: "{addon_trans[partybonus[job_party_bonus]]["Text_cn"].title()}"\n'
        filecontent += f'  ko: "{addon_trans[partybonus[job_party_bonus]]["Text_ko"].title()}"\n'
        filecontent += 'categories: "klassenjobs"\n'

        filecontent += 'difficulty: "Normal"\n'
        filecontent += 'instanceType: "klassenjobs"\n'

        if classDetails.get(job, {}):
            filecontent += f'date: "{classDetails[job]["date"]}"\n'
            filecontent += f'patchNumber: "{classDetails[job]["patchNumber"]}"\n'
            filecontent += f'patchName: "{classDetails[job]["patchName"]}"\n'
            filecontent += f'expac: "{classDetails[job]["patchShort"]}"\n'
        else:
            filecontent += 'date: "2013.01.01"\n'
            filecontent += 'patchNumber: "2.0"\n'
            filecontent += 'patchName: "A Realm Reborn"\n'
            filecontent += 'expac: "arr"\n'

        # this will be empty for non jobs (crafter/gatherer are clases so we know if they have pvp spells)
        pvp = getQuestName(job)

        filecontent += 'slug: "klassen_und_jobs_' + job.lower() + '"\n'
        if os.path.exists(f"{os.getcwd()}/../assets/img/content/klassen/{job}.png"):
            filecontent += 'image:\n'
            filecontent += f'    - url: "/assets/img/content/klassen/{job}.png"\n'
        else:
            print(f"Missing img: {job}.png")
        filecontent += 'terms:\n'
        filecontent += '    - term: "Klassen"\n'
        filecontent += '    - term: "Jobs"\n'
        filecontent += '    - term: "Skills"\n'
        filecontent += '    - term: "Status"\n'
        filecontent += '    - term: "Traits"\n'
        if classDetails.get(job, {}):
            filecontent += f'    - term: "{classDetails[job]["patchNumber"]}"\n'
            filecontent += f'    - term: "{classDetails[job]["patchName"]}"\n'
        else:
            filecontent += '    - term: "2.0"\n'
            filecontent += '    - term: "A Realm Reborn"\n'
        filecontent += f'    - term: "{job_d["Name_de"].title()}"\n'
        filecontent += f'    - term: "{job_d["Name_en"].title()}"\n'
        filecontent += f'    - term: "{job_d["Name_fr"].title()}"\n'
        filecontent += f'    - term: "{job_d["Name_ja"].title()}"\n'
        filecontent += f'    - term: "{job_d["Name_cn"].title()}"\n'
        filecontent += f'    - term: "{job_d["Name_ko"].title()}"\n'
        filecontent += f'sortid: {counter}\n'
        filecontent += f'order: {counter}\n'
        filecontent += f'plvl: {maxlvl}\n'
        filecontent += f'ilvl: {maxilvl}\n'
        filecontent += "bosses:\n"
        filecontent += "  - title:\n"
        filecontent += f'      de: "{job_d["Name_de"].title()}"\n'
        filecontent += f'      en: "{job_d["Name_en"].title()}"\n'
        filecontent += f'      fr: "{job_d["Name_fr"].title()}"\n'
        filecontent += f'      ja: "{job_d["Name_ja"].title()}"\n'
        filecontent += f'      cn: "{job_d["Name_cn"].title()}"\n'
        filecontent += f'      ko: "{job_d["Name_ko"].title()}"\n'
        filecontent += "    id: \"" + "boss" + str(counter) + "\"\n"
        if job == "Blaumagier":
            filecontent += addBlueAttackDetails(job_data)
        else:
            filecontent += addAttackDetails(job_data)
            filecontent += addAttackDetails(job_data_pvp, True)
        filecontent += addStatusDetails(job, job_abb)
        filecontent += addTraitDetails(job)

        ea, ea_text = addEurekaActions(job, eureka_actions)
        filecontent += ea_text
        bz, bz_text = addBozjaActions(job, bozja_actions)
        filecontent += bz_text
        cleves, cleves_text = addCrafterLeve(job, all_crafter_leves)
        filecontent += cleves_text
        gleves, gleves_text = addCrafterLeve(job, all_gatherer_leves)
        filecontent += gleves_text
        filecontent += addQuestkDetails(job, pvp or leves)
        filecontent += "    sequence:" + "\n"
        filecontent += "      - phase: \"01\"\n"
        filecontent += "        name: \"Skills\"\n"
        filecontent += "      - phase: \"02\"\n"
        filecontent += "        name: \"Status\"\n"
        filecontent += "      - phase: \"03\"\n"
        filecontent += "        name: \"Traits\"\n"
        filecontent += "      - phase: \"04\"\n"
        if pvp:
            filecontent += "        name: \"PvP\"\n"
            filecontent += "      - phase: \"05\"\n"
        if cleves or gleves:
            filecontent += "        name: \"Freibriefe\"\n"
            filecontent += "      - phase: \"05\"\n"
        filecontent += "        name: \"Quests\"\n"
        if ea:
            filecontent += "      - phase: \"06\"\n"
            filecontent += "        name: \"Eureka Skills\"\n"
        if bz:
            filecontent += "      - phase: \"07\"\n"
            filecontent += "        name: \"Bozja Skills\"\n"
        filecontent += '---\n'
        filename = f"klassen_und_jobs/2013-01-01--2.0--{counter}--{job}.md"
        with open(filename, encoding="utf8") as f:
            doc = f.read()
        if not doc == filecontent:
            with open(filename, "w", encoding="utf8") as f:
                f.write(filecontent)
    return counter


def addChocoboPartnerSkills():
    global actions
    global actions_trans
    global actiontransient_trans

    global buddyskill_raw
    test = [ [ x['Attacker'], x['Defender'], x['Healer'] ] for key, x in buddyskill_raw.items() if x['IsActive'] == "True" and not key == "0" ]
    chocobo_skills = []
    for x in test:
        chocobo_skills += x
    chocobo_skillss = { key:actions[key] for key in chocobo_skills }
    #print(chocobo_skillss)
    ordered = OrderedDict(sorted(chocobo_skillss.items(), key=lambda x: int(x[0])))
    result = ""
    result += "    attacks:\n"
    for key, _ in ordered.items():
        t = actions_trans[key]
        result += '      - title:\n'
        result += f'          de: "{t["Name_de"]}"\n'
        result += f'          en: "{t["Name_en"]}"\n'
        result += f'          fr: "{t["Name_fr"]}"\n'
        result += f'          ja: "{t["Name_ja"]}"\n'
        result += f'          cn: "{t["Name_cn"]}"\n'
        result += f'          ko: "{t["Name_ko"]}"\n'
        result += f'        icon: "{getImage(t["Icon"])}"\n'
        #result += f'        level: "{actions[key]["Level"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += '        description:\n'
        result += '          de: "' + actiontransient_trans[key]["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          en: "' + actiontransient_trans[key]["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          fr: "' + actiontransient_trans[key]["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ja: "' + actiontransient_trans[key]["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          cn: "' + actiontransient_trans[key]["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ko: "' + actiontransient_trans[key]["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '        phases:\n'
        result += '          - phase: "01"\n'
    return result


def addRennChocoboSkills_trans():
    global chocoboskills_trans
    ordered = OrderedDict(sorted(chocoboskills_trans.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["Name_de"] == "":
            continue
        # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        result += '      - title:\n'
        result += f'          de: "{value["Name_de"]}"\n'
        result += f'          en: "{value["Name_en"]}"\n'
        result += f'          fr: "{value["Name_fr"]}"\n'
        result += f'          ja: "{value["Name_ja"]}"\n'
        result += f'          cn: "{value["Name_cn"]}"\n'
        result += f'          ko: "{value["Name_ko"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += f'        icon: "{getImage(value["Icon"])}"\n'
        result += '        description:\n'
        result += '          de: "' + value["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          en: "' + value["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          fr: "' + value["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ja: "' + value["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          cn: "' + value["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ko: "' + value["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '        phases:\n'
        result += '          - phase: "03"\n'
    return result


def addChocoboPartnerTraits():
    global traits
    global traits_trans
    global traitstransient_trans
    global buddyskill_raw
    test = [ [x['Attacker'], x['Defender'], x['Healer']] for key, x in buddyskill_raw.items() if x['IsActive'] == "False" and not key == "0"]
    chocobo_traits = []
    for x in test:
        chocobo_traits += x
    chocobo_traits = sorted(chocobo_traits)
    chocobo_traits_trans = { key:traits[key] for key in chocobo_traits }
    ordered = OrderedDict(sorted(chocobo_traits_trans.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    result = ""
    result += "    traits:\n"
    for key, _ in ordered.items():
        t = traits_trans[key]
        result += '      - title:\n'
        result += f'          de: "{t["Name_de"]}"\n'
        result += f'          en: "{t["Name_en"]}"\n'
        result += f'          fr: "{t["Name_fr"]}"\n'
        result += f'          ja: "{t["Name_ja"]}"\n'
        result += f'          cn: "{t["Name_cn"]}"\n'
        result += f'          ko: "{t["Name_ko"]}"\n'
        result += f'        icon: "{getImage(t["Icon"])}"\n'
        result += f'        level: "{traits[key]["Level"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += '        description:\n'
        result += '          de: "' + traitstransient_trans[key]["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          en: "' + traitstransient_trans[key]["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          fr: "' + traitstransient_trans[key]["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ja: "' + traitstransient_trans[key]["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          cn: "' + traitstransient_trans[key]["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ko: "' + traitstransient_trans[key]["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '        phases:\n'
        result += '          - phase: "02"\n'
    return result


def addRennChocoboItems_trans():
    global chocoboitems_trans
    ordered = OrderedDict(sorted(chocoboitems_trans.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["Name_de"] == "":
            continue
        # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        result += '      - title:\n'
        result += f'          de: "{value["Name_de"]}"\n'
        result += f'          en: "{value["Name_en"]}"\n'
        result += f'          fr: "{value["Name_fr"]}"\n'
        result += f'          ja: "{value["Name_ja"]}"\n'
        result += f'          cn: "{value["Name_cn"]}"\n'
        result += f'          ko: "{value["Name_ko"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += f'        icon: "{getImage(value["Icon"])}"\n'
        result += '        description:\n'
        result += '          de: "' + value["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          en: "' + value["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          fr: "' + value["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ja: "' + value["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          cn: "' + value["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '          ko: "' + value["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += '        phases:\n'
        result += '          - phase: "04"\n'
    return result


def addRennChocoboMissions():
    global chocobochallange_trans
    ordered = OrderedDict(sorted(chocobochallange_trans.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["col_0_de"] == "":
            continue
        result += '      - title:\n'
        result += f'          de: "{value["col_0_de"]}"\n'
        result += f'          en: "{value["col_0_en"]}"\n'
        result += f'          fr: "{value["col_0_fr"]}"\n'
        result += f'          ja: "{value["col_0_ja"]}"\n'
        result += f'          cn: "{value["col_0_cn"]}"\n'
        result += f'          ko: "{value["col_0_ko"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += '        phases:\n'
        result += '          - phase: "05"\n'
    return result


def addChocobo():
    job = "Chocobo"
    job_d = {
        "Name_de": "Chocobo",
        "Name_en": "chocobo",
        "Name_fr": "chocobo",
        "Name_ja": "チョコボ",
        "Name_cn": "チョコボ",
        "Name_ko": "초코보"
    }
    filecontent = ""
    filecontent += '---\n'
    filecontent += 'wip: "True"\n'
    filecontent += 'title:\n'
    filecontent += f'  de: "{job_d["Name_de"]}"\n'
    filecontent += f'  en: "{job_d["Name_en"]}"\n'
    filecontent += f'  fr: "{job_d["Name_fr"]}"\n'
    filecontent += f'  ja: "{job_d["Name_ja"]}"\n'
    filecontent += f'  cn: "{job_d["Name_cn"]}"\n'
    filecontent += f'  ko: "{job_d["Name_ko"]}"\n'
    filecontent += 'layout: klassen\n'
    filecontent += 'page_type: guide\n'
    filecontent += 'roletypeinparty:\n'
    filecontent += f'  de: "{job_d["Name_de"]}"\n'
    filecontent += f'  en: "{job_d["Name_en"]}"\n'
    filecontent += f'  fr: "{job_d["Name_fr"]}"\n'
    filecontent += f'  ja: "{job_d["Name_ja"]}"\n'
    filecontent += f'  cn: "{job_d["Name_cn"]}"\n'
    filecontent += f'  ko: "{job_d["Name_ko"]}"\n'
    filecontent += 'categories: "klassenjobs"\n'
    filecontent += 'difficulty: "Normal"\n'
    filecontent += 'instanceType: "klassenjobs"\n'
    filecontent += 'date: "2013.01.01"\n'
    filecontent += 'patchNumber: "2.0"\n'
    filecontent += 'patchName: "A Realm Reborn"\n'
    filecontent += 'expac: "arr"\n'
    filecontent += 'slug: "klassen_und_jobs_' + job.lower() + '"\n'
    if os.path.exists(f"{os.getcwd()}/../assets/img/content/klassen/{job}.png"):
        filecontent += 'image:\n'
        filecontent += f'    - url: "/assets/img/content/klassen/{job}.png"\n'
    else:
        print(f"Missing img: {job}.png")
    filecontent += 'terms:\n'
    filecontent += '    - term: "Klassen"\n'
    filecontent += '    - term: "Jobs"\n'
    filecontent += '    - term: "Skills"\n'
    filecontent += '    - term: "Status"\n'
    filecontent += '    - term: "Traits"\n'
    filecontent += f'    - term: "{job_d["Name_de"]}"\n'
    filecontent += f'    - term: "{job_d["Name_en"]}"\n'
    filecontent += f'    - term: "{job_d["Name_fr"]}"\n'
    filecontent += f'    - term: "{job_d["Name_ja"]}"\n'
    filecontent += f'    - term: "{job_d["Name_cn"]}"\n'
    filecontent += f'    - term: "{job_d["Name_ko"]}"\n'
    filecontent += 'sortid: 0\n'
    filecontent += 'order: 0\n'
    filecontent += 'plvl: 50\n'
    filecontent += "bosses:\n"
    filecontent += "  - title:\n"
    filecontent += f'      de: "{job_d["Name_de"]}"\n'
    filecontent += f'      en: "{job_d["Name_en"]}"\n'
    filecontent += f'      fr: "{job_d["Name_fr"]}"\n'
    filecontent += f'      ja: "{job_d["Name_ja"]}"\n'
    filecontent += f'      cn: "{job_d["Name_cn"]}"\n'
    filecontent += f'      ko: "{job_d["Name_ko"]}"\n'
    filecontent += "    id: \"" + "boss0\"\n"
    #todo add chocobo stuff
    filecontent += addChocoboPartnerSkills()
    filecontent += addRennChocoboSkills_trans()
    #addRennChocoboStatus()
    filecontent += addRennChocoboItems_trans()
    filecontent += addRennChocoboMissions()
    filecontent += addChocoboPartnerTraits()
    filecontent += "    sequence:" + "\n"
    filecontent += "      - phase: \"01\"\n"
    filecontent += "        name: \"Chocobo-Partner-Skills\"\n"
    filecontent += "      - phase: \"02\"\n"
    filecontent += "        name: \"Chocobo-Partner-Traits\"\n"
    filecontent += "      - phase: \"03\"\n"
    filecontent += "        name: \"Renn-Chocobo-Skills\"\n"
    #filecontent += "      - phase: \"04\"\n"
    #filecontent += "        name: \"Renn-Chocobo-Status\"\n"
    filecontent += "      - phase: \"04\"\n"
    filecontent += "        name: \"Renn-Chocobo-Items\"\n"
    filecontent += "      - phase: \"05\"\n"
    filecontent += "        name: \"Renn-Chocobo-Missions\"\n"
    filecontent += '---\n'

    filename = f"klassen_und_jobs/2013-01-01--2.0--0--{job}.md"
    with open(filename, encoding="utf8") as f:
        doc = f.read()
    if not doc == filecontent:
        with open(filename, "w", encoding="utf8") as f:
            f.write(filecontent)


def run():
    load_global_data()
    os.chdir("../_posts")
    addKlassJobs()
    addChocobo()


if __name__ == "__main__":
    run()
    #test([{'Ort': 'Abyssos - Fünfter Kreis', 'Gegner': 'Proto-Karfunkel'}, {'Ort': 'Abyssos - Fünfter Kreis (episch)', 'Gegner': 'Proto-Karfunkel'}, {'Ort': 'Das Fenn', 'Gegner': 'Mahisha'}, {'Ort': 'Die Nichts-Arche', 'Gegner': 'Cuchulainn'}, {'Ort': 'Die Welt der Dunkelheit', 'Gegner': 'Cerberus'}, {'Ort': 'Himmelssäule (Ebenen 61-70)', 'Gegner': 'Kenko'}, {'Ort': 'Himmelssäule (Ebenen 81-90)', 'Gegner': 'Himmelssäulen-Gozu'}, {'Ort': 'Historisches Amdapor', 'Gegner': 'Verrottender Gourmet'}, {'Ort': 'Sankt Mocianne-Arboretum (schwer)', 'Gegner': 'Nullchu'}, {'Ort': 'Thavnair', 'Gegner': 'Yilan'}, {'Ort': 'Verschlungene Schatten 1', 'Gegner': '(InGame Hinweis)'}, {'Ort': 'Verschlungene Schatten 2 - 1', 'Gegner': 'Rafflesia'}, {'Ort': 'Verschlungene Schatten 3 - 4', 'Gegner': 'Schmerz Von Meracydia'}])
