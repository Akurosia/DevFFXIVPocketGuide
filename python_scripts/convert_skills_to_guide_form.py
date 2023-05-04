#!/usr/bin/env python3
# coding: utf8
import os
import sys
from ffxiv_aku import *
from collections import OrderedDict
from operator import getitem
import math
import traceback

skills = None
pvpskills = None
logdata = None
cj = None
cjs = None
actions = None
actionss = None
action_trans = None
aozaction_trans = None
lo_actions = None
bo_actions = None
craftactions = None
statuss = None
status = None
traits = None
traitss = None
traitstransient = None
aozactions = None
aozactiontransient = None
quests = None
questss = None
levels = None
maps = None
leves = None
trans_leves = None
craftleves = None
chocoboskills = None
chocoboitems = None
chocobochallange = None
buddyskill = None

disable_print = True
status_ncj = None


def load_global_data():
    global skills
    global pvpskills
    global logdata
    global cj
    global cjs
    global actions
    global actionss
    global action_trans
    global aozaction_trans
    global lo_actions
    global bo_actions
    global craftactions
    global statuss
    global status
    global traits
    global traitss
    global traitstransient
    global aozactions
    global aozactiontransient
    global quests
    global questss
    global levels
    global maps
    global leves
    global trans_leves
    global craftleves

    global chocoboskills
    global chocoboitems
    global chocobochallange
    global buddyskill
    storeFilesInTmp(True)
    skills = get_skills_for_player()
    pvpskills = get_skills_for_player(True)
    logdata = get_any_Logdata()
    cj = loadDataTheQuickestWay("classjob", translate=True)
    cjs = loadDataTheQuickestWay("ClassJob")
    actions = loadDataTheQuickestWay("action")
    actionss = loadDataTheQuickestWay("action", translate=True)
    action_trans = loadDataTheQuickestWay("actiontransient", translate=True)
    aozaction_trans = loadDataTheQuickestWay("aozactiontransient", translate=True)
    lo_actions = loadDataTheQuickestWay("eurekamagiaaction.json")
    bo_actions = loadDataTheQuickestWay("MYCTemporaryItem.json")
    craftactions = loadDataTheQuickestWay("craftaction", translate=True)
    statuss = loadDataTheQuickestWay("status", translate=True)
    status = loadDataTheQuickestWay("Status")
    traits = loadDataTheQuickestWay("Trait")
    traitss = loadDataTheQuickestWay("trait", translate=True)
    traitstransient = loadDataTheQuickestWay("TraitTransient", translate=True)
    aozactions = loadDataTheQuickestWay("aozaction", translate=True)
    aozactiontransient = loadDataTheQuickestWay("AozActionTransient")
    quests = loadDataTheQuickestWay("Quest")
    questss = loadDataTheQuickestWay("quest", translate=True)
    levels = loadDataTheQuickestWay("Level.json")
    maps = loadDataTheQuickestWay("Map.json")
    leves = loadDataTheQuickestWay("leve")
    trans_leves = loadDataTheQuickestWay("leve", translate=True)
    craftleves = loadDataTheQuickestWay("craftleve.json")
    chocoboskills = loadDataTheQuickestWay("chocoboraceability", translate=True)
    chocoboitems = loadDataTheQuickestWay("chocoboraceitem", translate=True)
    chocobochallange = loadDataTheQuickestWay("chocoboracechallenge", translate=True)
    buddyskill = loadDataTheQuickestWay("buddyskill.json", exd="raw-exd-all")


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
            if not enemy_name or type(enemy_data) == list:
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
            #print_color_green(n)
            return file.split("\\")[0].replace("_new", "") + "/" + n.replace("_", "-") + ".html"
    #print_color_red(n)
    return None


def addBlueAttackDetails(job_data):
    global actionss
    global aozactions
    global aozactiontransient
    result = ""
    result += "    attacks:\n"
    # get special aoz action data from correct files e.g. number in blu spell book and description
    for x, y in job_data.items():
        for key, value in aozactions.items():
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
        locations = []
        if skill_data.get('Location', None):
            locations.append(skill_data['Location'])
        en_name = actionss.get(skill_data['id'], {}).get("Name_en", "").title()
        fr_name = actionss.get(skill_data['id'], {}).get("Name_fr", "").title()
        ja_name = actionss.get(skill_data['id'], {}).get("Name_ja", "").title()
        cn_name = actionss.get(skill_data['id'], {}).get("Name_cn", "").title()
        ko_name = actionss.get(skill_data['id'], {}).get("Name_ko", "").title()
        if en_name == "":
            en_name = craftactions[skill_data['id'] + ".0"]["Name_en"]
        level = skill_data['Level']
        #
        locations = getBLULocationsFromLogdata(skill_data["Name"], locations)
        locations = sorted(locations, key=lambda x: x['Ort'])

        desc = ""
        if not locations == []:
            desc += "\n\n<br/>#########################################<br/>\n\nLOCATIONS:\n"
            #desc += "&emsp;Zone".ljust(max_zone_length) + " -> " + "Gegnername".ljust(max_enemyname_length) + ":"
            desc += "<table class='table-striped table-dark table-hover bg-charcoal text-light border-gold-metallic'><thead><td>Zone</td><td>Gegnername</td></thead><tbody>"

        for location in locations:
            zone_name = location["Ort"]
            enemy_name = location["Gegner"]
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
            result += f'          de: "{level}. {skill_data["Name"]}"\n'
            result += f'          en: "{level}. {en_name}"\n'
            result += f'          fr: "{level}. {fr_name}"\n'
            result += f'          ja: "{level}. {ja_name}"\n'
            result += f'          cn: "{level}. {cn_name}"\n'
            result += f'          ko: "{level}. {ko_name}"\n'
        else:
            result += f'      - title:\n'
            result += f'          de: "{skill_data["Name"]}"\n'
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
    return result


def convertJobToAbrev(job):
    global cj
    global cjs
    job_abbr = None
    class_abbr = None
    for key, value in cj.items():
        if value['Name_de'] == job:
            job_abbr = value['Abbreviation_de']
    _class = [v['ClassJob']['Parent'] for k, v in cjs.items() if v["Name"]['Value'] == job][0]
    for key2, value2 in cj.items():
        if value2['Name_de'] == _class:
            class_abbr = value2['Abbreviation_de']

    if not job_abbr == "" or not class_abbr == "":
        return job_abbr, class_abbr
    raise NotImplementedError


def addAttackDetails(job_data, pvp=False):
    global actionss
    global craftactions
    result = ""
    # only print for normal attacks
    if not pvp:
        result += "    attacks:\n"

    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, skill_data in job_data.items():
        #print_color_red(pretty_json(skill_data) + "\n")
        en_name = actionss.get(skill_data['id'], {}).get("Name_en", "").title()
        fr_name = actionss.get(skill_data['id'], {}).get("Name_fr", "").title()
        ja_name = actionss.get(skill_data['id'], {}).get("Name_ja", "").title()
        cn_name = actionss.get(skill_data['id'], {}).get("Name_cn", "").title()
        ko_name = actionss.get(skill_data['id'], {}).get("Name_ko", "").title()
        if en_name == "":
            en_name = craftactions[skill_data['id']]["Name_en"].title()
            fr_name = craftactions[skill_data['id']]["Name_fr"].title()
            ja_name = craftactions[skill_data['id']]["Name_ja"].title()
            cn_name = craftactions[skill_data['id']]["Name_cn"].title()
            ko_name = craftactions[skill_data['id']]["Name_ko"].title()
        level = "0" if skill_data['Level'] == "99999" else skill_data['Level']
        desc = action_trans.get(skill_data["id"].split(".")[0], None)
        if not desc:
            desc = craftactions[skill_data["id"].split(".")[0]]
        result += f'      - title:\n'
        result += f'          de: "{skill_data["Name"]}"\n'
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
        result += f'        description:\n'
        result += f'          de: "' + desc["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          en: "' + desc["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          fr: "' + desc["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ja: "' + desc["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          cn: "' + desc["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ko: "' + desc["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'        phases:\n'
        if pvp:
            result += f'          - phase: "04"\n'
        else:
            result += f'          - phase: "01"\n'
    return result


def addStatusDetails(job, job_abb):
    global logdata
    global statuss
    global status_ncj
    result = ""
    #jobstatusdata = logdata["Klassen"].get(job, {}).get("status", {})
    jobstatusdata = {}
    for key, value in status_ncj[job_abb].items():
        if not key in jobstatusdata:
            jobstatusdata[key] = value
    if not jobstatusdata == {}:
        jobstatusdata = OrderedDict(sorted(jobstatusdata.items(), key=lambda x: getitem(x[1], 'name')))
        result += "    debuffs:\n"
        for key, s in jobstatusdata.items():
            # skip known buffs
            #if key in ["30", "438", "43C", "437", "32", "53E", "31", "C2A", "C2C", "C2D", "BCF", "BEE", "436", "CAA", "541", "CA9", "D92", "C82", "", "", "", "", "", "", "", "", ""]:
            #    continue
            _id = str(int(key, 16))
            result += f'      - title:\n'
            result += f'          de: "{s["name"].title()}"\n'
            result += f'          en: "{statuss[_id]["Name_en"].title()}"\n'
            result += f'          fr: "{statuss[_id]["Name_fr"].title()}"\n'
            result += f'          ja: "{statuss[_id]["Name_ja"].title()}"\n'
            result += f'          cn: "{statuss[_id]["Name_cn"].title()}"\n'
            result += f'          ko: "{statuss[_id]["Name_ko"].title()}"\n'
            result += f'        title_id: "{key}"\n'
            result += f'        icon: "{getImage(s["icon"])}"\n'
            result += f'        description:\n'
            result += f'          de: "{statuss[_id]["Description_de"]}"\n'
            result += f'          en: "{statuss[_id]["Description_en"]}"\n'
            result += f'          fr: "{statuss[_id]["Description_fr"]}"\n'
            result += f'          ja: "{statuss[_id]["Description_ja"]}"\n'
            result += f'          cn: "{statuss[_id]["Description_cn"]}"\n'
            result += f'          ko: "{statuss[_id]["Description_ko"]}"\n'
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
    traitsss = {k: v for k, v in traits.items() if v["ClassJob"] in ([job] + _class)}
    job_trait_data = OrderedDict(sorted(traitsss.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, trait_data in job_trait_data.items():
        if not trait_data.get("Icon", None):
            continue
        en_name = traitss[_id]["Name_en"].title()
        fr_name = traitss[_id]["Name_fr"].title()
        ja_name = traitss[_id]["Name_ja"].title()
        cn_name = traitss[_id]["Name_cn"].title()
        ko_name = traitss[_id]["Name_ko"].title()
        level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        result += f'      - title:\n'
        result += f'          de: "{trait_data["Name"].title()}"\n'
        result += f'          en: "{en_name}"\n'
        result += f'          fr: "{fr_name}"\n'
        result += f'          ja: "{ja_name}"\n'
        result += f'          cn: "{cn_name}"\n'
        result += f'          ko: "{ko_name}"\n'
        result += f'        title_id: "{_id.split(".")[0]}"\n'
        result += f'        level: "{level}"\n'
        result += f'        icon: "{getImage(trait_data["Icon"].replace(".tex", "_hr1.png"))}"\n'
        result += f'        description:\n'
        result += f'          de: "' + traitstransient[_id]["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          en: "' + traitstransient[_id]["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          fr: "' + traitstransient[_id]["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ja: "' + traitstransient[_id]["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          cn: "' + traitstransient[_id]["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ko: "' + traitstransient[_id]["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'        phases:\n'
        result += f'          - phase: "03"\n'
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
                            "de": actionss[k]['Name_de'],
                            "en": actionss[k]['Name_en'],
                            "fr": actionss[k]['Name_fr'],
                            "ja": actionss[k]['Name_ja'],
                            "cn": actionss[k]['Name_cn'],
                            "ko": actionss[k]['Name_ko']
                        },
                        "icon": i["Icon"].replace(".png", "_hr1.png"),
                        "type": i["ActionCategory"],
                        "cj": i["ClassJobCategory"],
                        "uses": lo["MaxUses"],
                        "status": {
                            "de": statuss[status_key]['Name_de'],
                            "en": statuss[status_key]['Name_en'],
                            "fr": statuss[status_key]['Name_fr'],
                            "ja": statuss[status_key]['Name_ja'],
                            "cn": statuss[status_key]['Name_cn'],
                            "ko": statuss[status_key]['Name_ko']
                        },
                        "status_icon": statuss[status_key]['Icon'].replace(".tex", "_hr1.png").replace(".png", "_hr1.png"),
                        "description": {
                            "de": action_trans[k]["Description_de"].replace("\n", "</br>"),
                            "en": action_trans[k]["Description_en"].replace("\n", "</br>"),
                            "fr": action_trans[k]["Description_fr"].replace("\n", "</br>"),
                            "ja": action_trans[k]["Description_ja"].replace("\n", "</br>"),
                            "cn": action_trans[k]["Description_cn"].replace("\n", "</br>"),
                            "ko": action_trans[k]["Description_ko"].replace("\n", "</br>")
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
                "de": actionss[b]['Name_de'],
                "en": actionss[b]['Name_en'],
                "fr": actionss[b]['Name_fr'],
                "ja": actionss[b]['Name_ja'],
                "cn": actionss[b]['Name_cn'],
                "ko": actionss[b]['Name_ko']
            },
            "icon": icon,
            "cj": a["ClassJobCategory"],
            "frontsplitter": getFrontsplitterEntry(action['Action'], result),
            "description": {
                "de": action_trans[b]["Description_de"].replace("\n", "<br>"),
                "en": action_trans[b]["Description_en"].replace("\n", "<br>"),
                "fr": action_trans[b]["Description_fr"].replace("\n", "<br>"),
                "ja": action_trans[b]["Description_ja"].replace("\n", "<br>"),
                "cn": action_trans[b]["Description_cn"].replace("\n", "<br>"),
                "ko": action_trans[b]["Description_ko"].replace("\n", "<br>")
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
            result_text += f'      - title:\n'
            result_text += f'          de: "{value["name"]["de"]}"\n'
            result_text += f'          en: "{value["name"]["en"]}"\n'
            result_text += f'          fr: "{value["name"]["fr"]}"\n'
            result_text += f'          ja: "{value["name"]["ja"]}"\n'
            result_text += f'          cn: "{value["name"]["cn"]}"\n'
            result_text += f'          ko: "{value["name"]["ko"]}"\n'
            result_text += f'        status:\n'
            result_text += f'          de: "{value["name"]["de"]}"\n'
            result_text += f'          en: "{value["name"]["en"]}"\n'
            result_text += f'          fr: "{value["name"]["fr"]}"\n'
            result_text += f'          ja: "{value["name"]["ja"]}"\n'
            result_text += f'          cn: "{value["name"]["cn"]}"\n'
            result_text += f'          ko: "{value["name"]["ko"]}"\n'
            result_text += f'        status_icon: "{getImage(value["status_icon"])}"\n'
            result_text += f'        title_id: "{k}"\n'
            result_text += f'        level: "70"\n'
            result_text += f'        icon: "{getImage(value["icon"])}"\n'
            result_text += f'        description:\n'
            result_text += f'          de: "' + value["description"]['de'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += f'          en: "' + value["description"]['en'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += f'          fr: "' + value["description"]['fr'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += f'          ja: "' + value["description"]['ja'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += f'          cn: "' + value["description"]['cn'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += f'          ko: "' + value["description"]['ko'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
            result_text += f'        type: "{value["type"]}"\n'
            result_text += f'        phases:\n'
            result_text += f'          - phase: "06"\n'
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
                result_text += f'      - title:\n'
                result_text += f'          de: "{value["name"]["de"]}"\n'
                result_text += f'          en: "{value["name"]["en"]}"\n'
                result_text += f'          fr: "{value["name"]["fr"]}"\n'
                result_text += f'          ja: "{value["name"]["ja"]}"\n'
                result_text += f'          cn: "{value["name"]["cn"]}"\n'
                result_text += f'          ko: "{value["name"]["ko"]}"\n'
                result_text += f'        title_id: "{k}"\n'
                result_text += f'        level: "80"\n'
                result_text += f'        icon: "{getImage(value["icon"])}"\n'
                result_text += f'        description:\n'
                result_text += f'          de: "' + value["description"]['de'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += f'          en: "' + value["description"]['en'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += f'          fr: "' + value["description"]['fr'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += f'          ja: "' + value["description"]['ja'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += f'          cn: "' + value["description"]['cn'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += f'          ko: "' + value["description"]['ko'].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
                result_text += f'        frontsplitter: "{value["frontsplitter"]}"\n'
                result_text += f'        phases:\n'
                result_text += f'          - phase: "07"\n'
    return result, result_text


def translatename(name, lang="en"):
    global trans_leves
    for y, x in trans_leves.items():
        if x["Name_de"] == name:
            return x[f"Name_{lang}"].title()


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
            result += f'      - title:\n'
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
            result += f'        phases:\n'
            result += f'          - phase: "04"\n'
        return True, result
    return False, result


def addQuestkDetails(job, pvp):
    global quests
    global questss
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
        en_name = questss.get(quest['id'], {}).get("Name_en", "").replace(" ", "").replace(" ", "").title()
        fr_name = questss.get(quest['id'], {}).get("Name_fr", "").replace(" ", "").replace(" ", "").title()
        ja_name = questss.get(quest['id'], {}).get("Name_ja", "").replace(" ", "").replace(" ", "").title()
        cn_name = questss.get(quest['id'], {}).get("Name_cn", "").replace(" ", "").replace(" ", "").title()
        ko_name = questss.get(quest['id'], {}).get("Name_ko", "").replace(" ", "").replace(" ", "").title()
        level = "0" if quest['level'] == "99999" else quest['level']
        # desc = skill_data["Description"].replace("\n", "</br>")
        result += f'      - title:\n'
        result += f'          de: "{quest["name"].title().replace(" ", "").replace(" ", "")}"\n'
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
        result += f'        phases:\n'
        if pvp:
            result += f'          - phase: "05"\n'
        else:
            result += f'          - phase: "04"\n'
    return result


classDetails = {
    "Ninja": {
        "date": "2014.10.28", "patchNumber": "2.4", "patchName": "Dreams of Ice"
    },
    "Maschinist": {
        "date": "2015.06.23", "patchNumber": "3.0", "patchName": "Heavensward"
    },
    "Dunkelritter": {
        "date": "2015.06.23", "patchNumber": "3.0", "patchName": "Heavensward"
    },
    "Astrologe": {
        "date": "2015.06.23", "patchNumber": "3.0", "patchName": "Heavensward"
    },
    "Samurai": {
        "date": "2017.06.20", "patchNumber": "4.0", "patchName": "Stormblood"
    },
    "Rotmagier": {
        "date": "2017.06.20", "patchNumber": "4.0", "patchName": "Stormblood"
    },
    "Blaumagier": {
        "date": "2019.01.08", "patchNumber": "4.5", "patchName": "A Requiem for Heroes"
    },
    "Revolverklinge": {
        "date": "2019.06.28", "patchNumber": "5.0", "patchName": "Shadowbringers"
    },
    "Tänzer": {
        "date": "2019.06.28", "patchNumber": "5.0", "patchName": "Shadowbringers"
    },
    "Schnitter": {
        "date": "2021.12.07", "patchNumber": "6.0", "patchName": "Endwalker"
    },
    "Weiser": {
        "date": "2021.12.07", "patchNumber": "6.0", "patchName": "Endwalker"
    },
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
    global cj
    global status_ncj
    # for job, job_data in skills.items():
    all_crafter_leves = getCrafterLeves()
    all_gatherer_leves = getGathererLeves()
    eureka_actions = getEurekaActionDetails()
    bozja_actions = getBozjaActionDetails()
    #print_color_yellow(pretty_json(bozja_actions))

    ncj = sorted(cj.items(), key=lambda item: int(item[0].split(".")[0]))
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
        if not job_data:
            continue
        counter += 1
        #if not job == "Rotmagier":
        #    continue
        print_color_red(job)

        tmpmaxlvl = str(max([int(data["Level"]) for key, data in job_data.items() if int(data['Level']) < 99999]))
        if job == "Blaumagier":
            maxlvl = "70"
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
        filecontent += 'categories: "klassenjobs"\n'
        filecontent += 'difficulty: "Normal"\n'
        filecontent += 'instanceType: "klassenjobs"\n'

        if classDetails.get(job, {}):
            filecontent += f'date: "{classDetails[job]["date"]}"\n'
            filecontent += f'patchNumber: "{classDetails[job]["patchNumber"]}"\n'
            filecontent += f'patchName: "{classDetails[job]["patchName"]}"\n'
        else:
            filecontent += 'date: "2013.01.01"\n'
            filecontent += 'patchNumber: "2.0"\n'
            filecontent += 'patchName: "A Realm Reborn"\n'

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
    global actionss
    global action_trans

    global buddyskill
    test = [ [ x['Attacker'], x['Defender'], x['Healer'] ] for key, x in buddyskill.items() if x['IsActive'] == "True" and not key == "0" ]
    chocobo_skills = []
    for x in test:
        chocobo_skills += x
    chocobo_skillss = { key:actions[key] for key in chocobo_skills }
    #print(chocobo_skillss)
    ordered = OrderedDict(sorted(chocobo_skillss.items(), key=lambda x: int(x[0])))
    result = ""
    result += "    attacks:\n"
    for key, _ in ordered.items():
        t = actionss[key]
        result += f'      - title:\n'
        result += f'          de: "{t["Name_de"]}"\n'
        result += f'          en: "{t["Name_en"]}"\n'
        result += f'          fr: "{t["Name_fr"]}"\n'
        result += f'          ja: "{t["Name_ja"]}"\n'
        result += f'          cn: "{t["Name_cn"]}"\n'
        result += f'          ko: "{t["Name_ko"]}"\n'
        result += f'        icon: "{getImage(t["Icon"])}"\n'
        #result += f'        level: "{actions[key]["Level"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += f'        description:\n'
        result += f'          de: "' + action_trans[key]["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          en: "' + action_trans[key]["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          fr: "' + action_trans[key]["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ja: "' + action_trans[key]["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          cn: "' + action_trans[key]["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ko: "' + action_trans[key]["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'        phases:\n'
        result += f'          - phase: "01"\n'
    return result


def addRennChocoboSkills():
    global chocoboskills
    ordered = OrderedDict(sorted(chocoboskills.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["Name_de"] == "":
            continue
        # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        result += f'      - title:\n'
        result += f'          de: "{value["Name_de"]}"\n'
        result += f'          en: "{value["Name_en"]}"\n'
        result += f'          fr: "{value["Name_fr"]}"\n'
        result += f'          ja: "{value["Name_ja"]}"\n'
        result += f'          cn: "{value["Name_cn"]}"\n'
        result += f'          ko: "{value["Name_ko"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += f'        icon: "{getImage(value["Icon"])}"\n'
        result += f'        description:\n'
        result += f'          de: "' + value["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          en: "' + value["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          fr: "' + value["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ja: "' + value["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          cn: "' + value["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ko: "' + value["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'        phases:\n'
        result += f'          - phase: "03"\n'
    return result


def addChocoboPartnerTraits():
    global traits
    global traitss
    global traitstransient
    global buddyskill
    test = [ [x['Attacker'], x['Defender'], x['Healer']] for key, x in buddyskill.items() if x['IsActive'] == "False" and not key == "0"]
    chocobo_traits = []
    for x in test:
        chocobo_traits += x
    chocobo_traits = sorted(chocobo_traits)
    chocobo_traitss = { key:traits[key] for key in chocobo_traits }
    ordered = OrderedDict(sorted(chocobo_traitss.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    result = ""
    result += "    traits:\n"
    for key, _ in ordered.items():
        t = traitss[key]
        result += f'      - title:\n'
        result += f'          de: "{t["Name_de"]}"\n'
        result += f'          en: "{t["Name_en"]}"\n'
        result += f'          fr: "{t["Name_fr"]}"\n'
        result += f'          ja: "{t["Name_ja"]}"\n'
        result += f'          cn: "{t["Name_cn"]}"\n'
        result += f'          ko: "{t["Name_ko"]}"\n'
        result += f'        icon: "{getImage(t["Icon"])}"\n'
        result += f'        level: "{traits[key]["Level"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += f'        description:\n'
        result += f'          de: "' + traitstransient[key]["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          en: "' + traitstransient[key]["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          fr: "' + traitstransient[key]["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ja: "' + traitstransient[key]["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          cn: "' + traitstransient[key]["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ko: "' + traitstransient[key]["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'        phases:\n'
        result += f'          - phase: "02"\n'
    return result


def addRennChocoboItems():
    global chocoboitems
    ordered = OrderedDict(sorted(chocoboitems.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["Name_de"] == "":
            continue
        # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        result += f'      - title:\n'
        result += f'          de: "{value["Name_de"]}"\n'
        result += f'          en: "{value["Name_en"]}"\n'
        result += f'          fr: "{value["Name_fr"]}"\n'
        result += f'          ja: "{value["Name_ja"]}"\n'
        result += f'          cn: "{value["Name_cn"]}"\n'
        result += f'          ko: "{value["Name_ko"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += f'        icon: "{getImage(value["Icon"])}"\n'
        result += f'        description:\n'
        result += f'          de: "' + value["Description_de"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          en: "' + value["Description_en"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          fr: "' + value["Description_fr"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ja: "' + value["Description_ja"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          cn: "' + value["Description_cn"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'          ko: "' + value["Description_ko"].replace("\n", "</br>").replace("</br></br>", "</br>") + '"\n'
        result += f'        phases:\n'
        result += f'          - phase: "04"\n'
    return result


def addRennChocoboMissions():
    global chocobochallange
    ordered = OrderedDict(sorted(chocobochallange.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["col_0_de"] == "":
            continue
        result += f'      - title:\n'
        result += f'          de: "{value["col_0_de"]}"\n'
        result += f'          en: "{value["col_0_en"]}"\n'
        result += f'          fr: "{value["col_0_fr"]}"\n'
        result += f'          ja: "{value["col_0_ja"]}"\n'
        result += f'          cn: "{value["col_0_cn"]}"\n'
        result += f'          ko: "{value["col_0_ko"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += f'        phases:\n'
        result += f'          - phase: "05"\n'
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
    filecontent += f'  de: "{job_d["Name_de"].title()}"\n'
    filecontent += f'  en: "{job_d["Name_en"].title()}"\n'
    filecontent += f'  fr: "{job_d["Name_fr"].title()}"\n'
    filecontent += f'  ja: "{job_d["Name_ja"].title()}"\n'
    filecontent += f'  cn: "{job_d["Name_cn"].title()}"\n'
    filecontent += f'  ko: "{job_d["Name_ko"].title()}"\n'
    filecontent += 'layout: klassen\n'
    filecontent += 'page_type: guide\n'
    filecontent += 'categories: "klassenjobs"\n'
    filecontent += 'difficulty: "Normal"\n'
    filecontent += 'instanceType: "klassenjobs"\n'
    filecontent += 'date: "2013.01.01"\n'
    filecontent += 'patchNumber: "2.0"\n'
    filecontent += 'patchName: "A Realm Reborn"\n'
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
    filecontent += f'    - term: "{job_d["Name_de"].title()}"\n'
    filecontent += f'    - term: "{job_d["Name_en"].title()}"\n'
    filecontent += f'    - term: "{job_d["Name_fr"].title()}"\n'
    filecontent += f'    - term: "{job_d["Name_ja"].title()}"\n'
    filecontent += f'    - term: "{job_d["Name_cn"].title()}"\n'
    filecontent += f'    - term: "{job_d["Name_ko"].title()}"\n'
    filecontent += f'sortid: 0\n'
    filecontent += f'order: 0\n'
    filecontent += f'plvl: 50\n'
    filecontent += "bosses:\n"
    filecontent += "  - title:\n"
    filecontent += f'      de: "{job_d["Name_de"].title()}"\n'
    filecontent += f'      en: "{job_d["Name_en"].title()}"\n'
    filecontent += f'      fr: "{job_d["Name_fr"].title()}"\n'
    filecontent += f'      ja: "{job_d["Name_ja"].title()}"\n'
    filecontent += f'      cn: "{job_d["Name_cn"].title()}"\n'
    filecontent += f'      ko: "{job_d["Name_ko"].title()}"\n'
    filecontent += "    id: \"" + "boss0\"\n"
    #todo add chocobo stuff
    filecontent += addChocoboPartnerSkills()
    filecontent += addRennChocoboSkills()
    #addRennChocoboStatus()
    filecontent += addRennChocoboItems()
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
    addKlassJobs()
    addChocobo()


if __name__ == "__main__":
    os.chdir("../_posts")
    run()
