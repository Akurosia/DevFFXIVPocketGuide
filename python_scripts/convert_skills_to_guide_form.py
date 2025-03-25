#!/usr/bin/env python3
# coding: utf8
import os
from collections import OrderedDict
from operator import getitem
from typing import Any, Literal
from ffxiv_aku import print_color_red, gear_get, getLevel, deal_with_extras_in_text, readJsonFile, print_pretty_json, writeJsonFile
from ffxiv_aku import storeFilesInTmp, get_skills_for_player, loadDataTheQuickestWay, get_any_Logdata, print_color_green

try:
    from .convert_skills_to_guide_form_helper.chocobo import addChocobo
except:
    from convert_skills_to_guide_form_helper.chocobo import addChocobo
try:
    from .convert_skills_to_guide_form_helper.helper import getImage, deal_with_extras_in_text, LANGUAGES, LANGUAGES_MAPPING
except:
    from convert_skills_to_guide_form_helper.helper import getImage, deal_with_extras_in_text, LANGUAGES, LANGUAGES_MAPPING
try:
    from .convert_skills_to_guide_form_helper.blaumagier import addBlueAttackDetails
except:
    from convert_skills_to_guide_form_helper.blaumagier import addBlueAttackDetails
try:
    from .convert_skills_to_guide_form_helper.eureka_bozja import prepare_eureka_bozja_data, addEurekaActions, addBozjaActions, getBozjaActionDetails, getEurekaActionDetails
except:
    from convert_skills_to_guide_form_helper.eureka_bozja import prepare_eureka_bozja_data, addEurekaActions, addBozjaActions, getBozjaActionDetails, getEurekaActionDetails

allPartyMittigation = {}
skills = None
pvpskills = None
logdata = None
cj = None
cjs = None
actions = None
action_trans = None
actions_trans = None
craftactions_trans = None
status_trans = None
status = None
traits = None
traits_trans = None
traitstransient_trans = None
quests = None
quests_trans = None
levels = None
maps = None
leves = None
trans_leves = None
craftleves = None
addon_trans = None
items_trans = None
bannertimeline = None

disable_print = True
status_ncj = None

klass_translations = None
job_translations = None

def get_class_translation_data() -> None:
    global klass_translations
    klass_translations = {}
    for lang in LANGUAGES:
        #klass_translations[lang] = readJsonFile(f'assets/translations/klassen/{LANGUAGES_MAPPING[lang]}.json')
        klass_translations[lang] = {}


def write_class_translation_data(data: dict) -> None:
    origin: str = os.getcwd()
    os.chdir("..")
    for lang in LANGUAGES:
        writeJsonFile(f'assets/translations/klassen/{LANGUAGES_MAPPING[lang]}.json', data[lang])
    os.chdir(origin)


def load_global_data() -> None:
    global skills
    global pvpskills
    global logdata
    global addon_trans
    global cjs_trans
    global cjs
    global actions
    global actions_trans
    global actiontransient_trans
    global craftactions_trans
    global status_trans
    global status
    global traits
    global traits_trans
    global traitstransient_trans
    global quests
    global quests_trans
    global levels
    global maps
    global leves
    global trans_leves
    global craftleves
    global items_trans
    global bannertimeline

    storeFilesInTmp(False)
    logdata = get_any_Logdata()
    storeFilesInTmp(True)
    skills = get_skills_for_player()
    pvpskills = get_skills_for_player(True)
    cjs_trans = loadDataTheQuickestWay("classjob", translate=True)
    cjs = loadDataTheQuickestWay("ClassJob")
    actions = loadDataTheQuickestWay("action")
    addon_trans = loadDataTheQuickestWay("addon", translate=True)
    actions_trans = loadDataTheQuickestWay("action", translate=True)
    actiontransient_trans = loadDataTheQuickestWay("actiontransient", translate=True)
    craftactions_trans = loadDataTheQuickestWay("craftaction", translate=True)
    status_trans = loadDataTheQuickestWay("status", translate=True)
    status = loadDataTheQuickestWay("Status")
    traits = loadDataTheQuickestWay("Trait")
    traits_trans = loadDataTheQuickestWay("trait", translate=True)
    traitstransient_trans = loadDataTheQuickestWay("TraitTransient", translate=True)
    quests = loadDataTheQuickestWay("Quest")
    quests_trans = loadDataTheQuickestWay("quest", translate=True)
    items_trans = loadDataTheQuickestWay("item", translate=True)
    levels = loadDataTheQuickestWay("Level.json")
    maps = loadDataTheQuickestWay("Map.json")
    leves = loadDataTheQuickestWay("leve")
    trans_leves = loadDataTheQuickestWay("leve", translate=True)
    craftleves = loadDataTheQuickestWay("craftleve.json")
    bannertimeline = loadDataTheQuickestWay("BannerTimeline")


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


def addAttackDetails(job_data, pvp: bool=False):
    global actions_trans
    global craftactions_trans
    global job_translations
    result = ""
    attack_skills = []
    pvp_text_field = ""
    # only print for normal attacks
    if not pvp:
        result += "    attacks:\n"
    else:
        pvp_text_field = "PVP_"

    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, skill_data in job_data.items():
        name = {}
        for lang in LANGUAGES:
            name[lang] = deal_with_extras_in_text(actions_trans.get(skill_data["Id"], {}).get(f"Name_{lang}", "").replace("\n", "</br>").replace("</br></br>", "</br>"))
        if name["en"] == "":
            for lang in LANGUAGES:
                name[lang] = deal_with_extras_in_text(craftactions_trans[skill_data["Id"]][f"Name_{lang}"].replace("\n", "</br>").replace("</br></br>", "</br>"))
        level: str | Literal['0'] = "0" if skill_data['Level'] == "99999" else skill_data['Level']

        tpye_damage: None | Literal['Schaden'] = "Schaden" if skill_data["IsDamageSkill"] else None
        tpye_heilung: None | Literal['Heilung'] = "Heilung" if skill_data["IsHealingSkill"] else None
        type_shield: None | Literal['P-Schild-Mitigation'] = "P-Schild-Mitigation" if skill_data["IsShieldSkill"] else None
        mtype  = skill_data["MitigationType"]
        mvalue = skill_data["MitigationValue"]

        if type_shield and not pvp:
            if "all party" in skill_data["Description"]["en"] or "nearby party" in skill_data["Description"]["en"]:
                type_shield = "G-Schild-Mitigation"
        result += '      - title:\n'

        attack_skills.append(name['de'])
        for lang in LANGUAGES:
            result += f'          {lang}: "{name[lang]}"\n'
            job_translations[lang][f'Class_Skill_Name_{pvp_text_field}{name["en"]}'] = name[lang]
        result += f'        title_id: "{skill_data["Id"].split(".")[0]}"\n'
        result += f'        level: "{level}"\n'
        result += f'        type: "{skill_data["Type"]}"\n'
        result += f'        icon: "/assets/img/game_assets{getImage(skill_data["Icon"])}"\n'
        result += f'        range: "{skill_data["Range"]}"\n'
        result += f'        effectrange: "{skill_data["EffectRange"]}"\n'
        result += f'        cast: "{skill_data["Cast"]}"\n'
        result += f'        cost: "{skill_data["Cost"]}"\n'
        result += f'        recast: "{skill_data["Recast"]}"\n'
        result += f'        secondarycost: "{skill_data.get("SecondaryCostType", 0)}"\n'
        result += f'        kategorie: "{skill_data["Kategorie"]['de']}"\n'
        if tpye_damage:
            result += f'        damage: "{tpye_damage}"\n'
        if tpye_heilung:
            result += f'        heal: "{tpye_heilung}"\n'
        if type_shield:
            result += f'        shield: "{type_shield}"\n'
        if mtype == "personal":
            result += '        pmitigation: "P-Mitigation"\n'
            result += f'        pmitigation_value: "M:{mvalue['magic']}/P:{mvalue['physical']}"\n'
        if mtype == "group":
            result += '        gmitigation: "G-Mitigation"\n'
            result += f'        gmitigation_value: "M:{mvalue['magic']}/P:{mvalue['physical']}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "' + skill_data["Description"][lang] + '"\n'
            job_translations[lang][f'Class_Skill_Desc_{pvp_text_field}{name["en"]}'] = deal_with_extras_in_text(skill_data["Description"][lang])
        result += '        phases:\n'
        if pvp:
            result += '          - phase: "04"\n'
        else:
            result += '          - phase: "01"\n'
    return result, attack_skills


def addOldStatusDetails(job, job_abb) -> str:
    global logdata
    global status_trans
    global status_ncj
    global status
    result: str = ""
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
            for lang in LANGUAGES:
                result += f'          {lang}: "' + deal_with_extras_in_text(status_trans[_id][f"Name_{lang}"]) + '"\n'
            result += f'        title_id: "{key}"\n'
            if "_hr1" in getImage(s["icon"]):
                result += f'        icon: "/assets/img/game_assets{getImage(s["icon"])}"\n'
            else:
                result += f'        icon: "/assets/img/game_assets{getImage(s["icon"]).replace(".webp", "_hr1.webp")}"\n'
            result += '        description:\n'
            for lang in LANGUAGES:
                result += f'          {lang}: "' + deal_with_extras_in_text(status_trans[_id][f"Description_{lang}"]) + '"\n'
            if s.get('buff', None):
                result += f'        buff: {s["buff"]}\n'
            else:
                buff = "buff" if str(status[str(int(key,16))]['StatusCategory']) == "1" else "debuff"
                result += f'        buff: {buff}\n'
            if s['duration']:
                result += f'        durations: {s["duration"]}\n'

            if s.get('was_added_by_action', None):
                result += '        added_by:\n'
                result += '          icon: "' + getImage(actions_trans[str(int(s['was_added_by_action'], 16))]['Icon'].replace("ui/icon/", "")) + '"\n'
                for lang in LANGUAGES:
                    result += f'          {lang}: "' + getImage(actions_trans[str(int(s['was_added_by_action'], 16))][f'Name_{lang}']) + '"\n'
            result += '        phases:\n'
            result += '          - phase: "02"\n'
    return result


def addStatusDetails(job, job_abb, attack_skills, pvp_skills, eureka_skills, bozja_skills):
    global status
    global job_translations
    result = ""
    result += "    debuffs:\n"
    for key, value in status.items():
        if job_abb not in value['ClassJobCategory']:
            continue
        con = False
        # validate if skill is either a pvp skill or a normal skill
        if value['Name'] in attack_skills:
            con = True
        if value['Name'] in pvp_skills:
            con = True
        if not con:
            #print(value['Name'])
            continue
        result += '      - title:\n'
        for lang in LANGUAGES:
            tmp_name = deal_with_extras_in_text(status_trans[key][f"Name_{lang}"])
            result += f'          {lang}: "' + tmp_name + '"\n'
            job_translations[lang][f'Class_Status_Name_{deal_with_extras_in_text(status_trans[key]["Name_en"])}'] = tmp_name
        result += f'        title_id: "{status_trans[key]['0xID']}"\n'
        image = getImage(status_trans[key]["Icon"])
        if "_hr1" in image:
            result += f'        icon: "/assets/img/game_assets{image}"\n'
        else:
            result += f'        icon: "/assets/img/game_assets{image.replace(".webp", "_hr1.webp")}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            tmp_desc = deal_with_extras_in_text(status_trans[key][f"Description_{lang}"])
            result += f'          {lang}: "' + tmp_desc + '"\n'
            job_translations[lang][f'Class_Status_Desc_{deal_with_extras_in_text(status_trans[key]["Name_en"])}'] = tmp_desc
        buff = "buff" if str(status[str(key)]['StatusCategory']) == "1" else "debuff"
        result += f'        buff: {buff}\n'
        result += '        phases:\n'
        result += '          - phase: "02"\n'
    return result


def addTraitDetails(job):
    global traits
    global job_translations

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
        for lang in LANGUAGES:
            tmp_trait = deal_with_extras_in_text(traits_trans[_id][f"Name_{lang}"])
            result += f'          {lang}: "' + tmp_trait + '"\n'
            job_translations[lang][f'Class_Trait_Name_{deal_with_extras_in_text(traits_trans[_id]["Name_en"]) }'] = tmp_trait
        result += f'        title_id: "{_id.split(".")[0]}"\n'
        result += f'        level: "{level}"\n'
        result += f'        icon: "/assets/img/game_assets{getImage(trait_data["Icon"].replace(".tex", "_hr1.webp"))}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            tmp_trait = deal_with_extras_in_text(traitstransient_trans[_id][f"Description_{lang}"])
            result += f'          {lang}: "' + tmp_trait + '"\n'
            job_translations[lang][f'Class_Trait_Desc_{deal_with_extras_in_text(traits_trans[_id]["Name_en"]) }'] = tmp_trait

        result += '        phases:\n'
        result += '          - phase: "03"\n'
    return result


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
    global job_translations
    result = ""
    for key, value in all_crafter_leves.items():
        if job not in key:
            continue
        result += "    leves:\n"
        job_leve_data = OrderedDict(sorted(value.items(), key=lambda x: int(getitem(x[1], 'level'))))
        for _id, leve_data in job_leve_data.items():
            level = "0" if leve_data['level'] == "99999" else leve_data['level']
            result += '      - title:\n'
            for lang in LANGUAGES:
                job_translations[lang][f'Class_Leve_Name_{leve_data["Name_EN"]}'] = leve_data[f"Name_{lang.upper()}"]
                result += f'          {lang}: "{leve_data[f"Name_{lang.upper()}"]}"\n'
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
    global job_translations

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
                if level_data is None or level_data == "{}":
                    continue
            except Exception as e:
                print(f"Error in addQuestkDetails: {e}")
                pass
            place = f"{level_data['region']} > {quest['PlaceName']}"
            if level_data['placename'] not in place:
                place + f" > {level_data['placename']}"
            newquest = {
                "name": quest['Name'],
                "id": key,
                "expansion": quest['Expansion'],
                "level": int(quest['ClassJobLevel']["0"]),
                "Icon": quest['Icon']['Value'].replace('.tex', "_hr1.webp"),
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
        for lang in LANGUAGES:
            name = {
                "de": quests_trans.get(quest["id"], {}).get("Name_de", "").replace(" ", "").replace(" ", ""),
                "en": quests_trans.get(quest["id"], {}).get("Name_en", "").replace(" ", "").replace(" ", ""),
                "fr": quests_trans.get(quest["id"], {}).get("Name_fr", "").replace(" ", "").replace(" ", ""),
                "ja": quests_trans.get(quest["id"], {}).get("Name_ja", "").replace(" ", "").replace(" ", ""),
                "cn": quests_trans.get(quest["id"], {}).get("Name_cn", "").replace(" ", "").replace(" ", ""),
                "ko": quests_trans.get(quest["id"], {}).get("Name_ko", "").replace(" ", "").replace(" ", "")
            }
        level = "0" if quest['level'] == "99999" else quest['level']
        # desc = skill_data["Description"].replace("\n", "</br>")
        result += '      - title:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{name[lang]}"\n'
            job_translations[lang][f'Class_Quest_Name_{name["en"]}'] = name[lang]

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

ExtraIconsCategory: list[str] = ["MarketBoard", "classjob", "normal", "glow", "gearset", "grey", "black", "gold", "orange", "red", "purple", "blue", "green"]
ExtraIcons: dict[str, list[str]] = {
                    # [MarketBoard, classjob, normal,   glow,     gearset,  grey,     black,    gold,     orange,   red,      purple,   blue,     green
    "Zimmerer":       ["060112",    "062008", "062108", "062310", "062808", "091031", "091531", "092031", "092531", "093031", "093531", "094031", "094531"],
    "Grobschmied":    ["060113",    "062009", "062109", "062311", "062809", "091032", "091532", "092032", "092532", "093032", "093532", "094032", "094532"],
    "Plattner":       ["060114",    "062010", "062110", "062312", "062810", "091033", "091533", "092033", "092533", "093033", "093533", "094033", "094533"],
    "Goldschmied":    ["060115",    "062011", "062111", "062313", "062811", "091034", "091534", "092034", "092534", "093034", "093534", "094034", "094534"],
    "Gerber":         ["060116",    "062012", "062112", "062314", "062812", "091035", "091535", "092035", "092535", "093035", "093535", "094035", "094535"],
    "Weber":          ["060117",    "062013", "062113", "062315", "062813", "091036", "091536", "092036", "092536", "093036", "093536", "094036", "094536"],
    "Alchemist":      ["060118",    "062014", "062114", "062316", "062814", "091037", "091537", "092037", "092537", "093037", "093537", "094037", "094537"],
    "Gourmet":        ["060119",    "062015", "062115", "062317", "062815", "091038", "091538", "092038", "092538", "093038", "093538", "094038", "094538"],

    "Minenarbeiter":  ["060120",    "062016", "062116", "062318", "062816", "091039", "091539", "092039", "092539", "093039", "093539", "094039", "094539"],
    "Gärtner":        ["060121",    "062017", "062117", "062319", "062817", "091040", "091540", "092040", "092540", "093040", "093540", "094040", "094540"],
    "Fischer":        ["060122",    "062018", "062118", "062320", "062818", "091041", "091541", "092041", "092541", "093041", "093541", "094041", "094541"],

    "Chocobo":        ["060842",    "062043", "062143", "",       "",       "091088", "091588", "092088", "092588", "093088", "093588", "094088", "094588"],

    "Gladiator":      ["060102",    "062001", "062101", "062301", "062801", "091022", "091522", "092022", "092522", "093022", "093522", "094022", "094522"],
    "Faustkämpfer":   ["060101",    "062002", "062102", "062302", "062802", "091023", "091523", "092023", "092523", "093023", "093523", "094023", "094523"],
    "Marodeur":       ["060103",    "062003", "062103", "062303", "062803", "091024", "091524", "092024", "092524", "093024", "093524", "094024", "094524"],
    "Pikenier":       ["060104",    "062004", "062104", "062304", "062804", "091025", "091525", "092025", "092525", "093025", "093525", "094025", "094525"],
    "Waldläufer":     ["060105",    "062005", "062105", "062305", "062805", "091026", "091526", "092026", "092526", "093026", "093526", "094026", "094526"],
    "Druide":         ["060107",    "062006", "062106", "062306", "062806", "091028", "091528", "092028", "092528", "093028", "093528", "094028", "094528"],
    "Thaumaturg":     ["060108",    "062007", "062107", "062307", "062807", "091029", "091529", "092029", "092529", "093029", "093529", "094029", "094529"],
    "Hermetiker":     ["060109",    "062026", "062126", "062308", "062826", "091030", "091530", "092030", "092530", "093030", "093530", "094030", "094530"],
    "Schurke":        ["060106",    "062029", "062129", "062309", "062829", "091121", "091621", "092121", "092621", "093121", "093621", "094121", "094621"],

    "Paladin":        ["",          "062019", "062119", "062401", "062819", "091079", "091579", "092079", "092579", "093079", "093579", "094079", "094579"],
    "Mönch":          ["",          "062020", "062120", "062402", "062820", "091080", "091580", "092080", "092580", "093080", "093580", "094080", "094580"],
    "Krieger":        ["",          "062021", "062121", "062403", "062821", "091081", "091581", "092081", "092581", "093081", "093581", "094081", "094581"],
    "Dragoon":        ["",          "062022", "062122", "062404", "062822", "091082", "091582", "092082", "092582", "093082", "093582", "094082", "094582"],
    "Barde":          ["",          "062023", "062123", "062405", "062823", "091083", "091583", "092083", "092583", "093083", "093583", "094083", "094583"],
    "Weißmagier":     ["",          "062024", "062124", "062406", "062824", "091084", "091584", "092084", "092584", "093084", "093584", "094084", "094584"],
    "Schwarzmagier":  ["",          "062025", "062125", "062407", "062825", "091085", "091585", "092085", "092585", "093085", "093585", "094085", "094585"],
    "Beschwörer":     ["",          "062027", "062127", "062408", "062827", "091086", "091586", "092086", "092586", "093086", "093586", "094086", "094586"],
    "Gelehrter":      ["060178",    "062028", "062128", "062409", "062828", "091087", "091587", "092087", "092587", "093087", "093587", "094087", "094587"],
    "Ninja":          ["",          "062030", "062130", "062410", "062830", "091122", "091622", "092122", "092622", "093122", "093622", "094122", "094622"],
    "Maschinist":     ["060172",    "062031", "062131", "062411", "062831", "091125", "091625", "092125", "092625", "093125", "093625", "094125", "094625"],
    "Dunkelritter":   ["060170",    "062032", "062132", "062412", "062832", "091123", "091623", "092123", "092623", "093123", "093623", "094123", "094623"],
    "Astrologe":      ["060171",    "062033", "062133", "062413", "062833", "091124", "091624", "092124", "092624", "093124", "093624", "094124", "094624"],
    "Samurai":        ["060177",    "062034", "062134", "062414", "062834", "091127", "091627", "092127", "092627", "093127", "093627", "094127", "094627"],
    "Rotmagier":      ["060176",    "062035", "062135", "062415", "062835", "091128", "091628", "092128", "092628", "093128", "093628", "094128", "094628"],
    "Blaumagier":     ["060180",    "062036", "062136", "062416", "062836", "091129", "091629", "092129", "092629", "093129", "093629", "094129", "094629"],
    "Revolverklinge": ["060181",    "062037", "062137", "062417", "062837", "091130", "091630", "092130", "092630", "093130", "093630", "094130", "094630"],
    "Tänzer":         ["060182",    "062038", "062138", "062418", "062838", "091131", "091631", "092131", "092631", "093131", "093631", "094131", "094631"],
    "Schnitter":      ["060183",    "062039", "062139", "062419", "062839", "091132", "091632", "092132", "092632", "093132", "093632", "094132", "094632"],
    "Weiser":         ["060184",    "062040", "062140", "062420", "062840", "091133", "091633", "092133", "092633", "093133", "093633", "094133", "094633"],
    "Viper":          ["060187",    "062041", "062141", "062421", "062841", "091185", "091685", "092185", "092685", "093185", "093685", "094185", "094685"],
    "Piktomant":      ["060188",    "062042", "062142", "062422", "062842", "091186", "091686", "092186", "092686", "093186", "093686", "094186", "094686"],
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
                "buff": "buff" if str(s['StatusCategory']) == "1" else "debuff",
                "duration": None
            }
        elif s['ClassJobCategory'] == "Handwerker":
            for crafter in ['ZMR', 'GRS', 'PLA', 'GLD', 'GER', 'WEB', 'ALC', 'GRM']:
                default_status[crafter][str(hex(int(key)))[2:].upper()] = {
                    "name": s['Name'],
                    "icon": s['Icon'],
                    "buff": "buff" if str(s['StatusCategory']) == "1" else "debuff",
                    "duration": None
                }
    return default_status


def get_classJobKeyMapping() -> dict[Any, Any]:
    global cjs
    results = {}
    for key, value in cjs.items():
        results[value['Name']['Value']] = key
    return results

kristall_list = {}
def getJobKristall(job):
    global kristall_list
    if kristall_list == {}:
        for key, item in items_trans.items():
            if item['Name_de'].endswith("-Kristall"):
                kristall_list[item['Name_de'].replace("-Kristall", "")] = item['Icon']
    if kristall_list.get(job, kristall_list.get(job+'n', kristall_list.get(job+'en', kristall_list.get(job[:-1]+'n', None)))):
        image = getImage(kristall_list.get(job, kristall_list.get(job+'n', kristall_list.get(job+'en', kristall_list.get(job[:-1]+'n', None)))))
        return f'jobkristall: "/assets/img/game_assets{image}"\n'
    print(f"No Jobkristall for {job[:-1]}")
    return ""


additionalJobIcons = {
    "MIN": "062116_hr1",
    "GÄR": "062117_hr1",
    "GRM": "062115_hr1",
    "ALC": "062114_hr1",
    "WEB": "062113_hr1",
    "GER": "062112_hr1",
    "ZMR": "062108_hr1",
    "GRS": "062109_hr1",
    "PLA": "062110_hr1",
    "GLD": "062111_hr1",
    "BMA": "062136_hr1"
}
def getIconForJob(job_abb):
    global bannertimeline
    global additionalJobIcons
    icon = ""
    for key, value in bannertimeline.items():
        if value["AcceptClassJobCategory"] == job_abb:
            return getImage(value["Icon"])
    if additionalJobIcons.get(job_abb, None):
        return getImage("062000/" + additionalJobIcons[job_abb] + ".webp")
    return icon

# these are the classes before they are job and usually dont need change

roleicons: dict[str, str] = {
    "Tank":                "062000/062581_hr1.webp",
    "Melee Dps":           "062000/062584_hr1.webp",
    "Physical Ranged Dps": "062000/062586_hr1.webp",
    "Healer":              "062000/062582_hr1.webp",
    "Magical Ranged Dps":  "062000/062587_hr1.webp"
}
roleiconsextra = {
    "2": ("/assets/img/game_assets/uld/pure-healer.webp", "Primärheiler"),
    "6": ("/assets/img/game_assets/uld/barrier-healer.webp", "Barriereheiler")
}
additionalClassIcons = {
    "PLD": "062101_hr1",
    "MÖN": "062102_hr1",
    "KRG": "062103_hr1",
    "DRG": "062104_hr1",
    "BRD": "062105_hr1",
    "WMA": "062106_hr1",
    "SMA": "062107_hr1",
    "BSW": "062126_hr1",
    "GLT": "062126_hr1",
    "NIN": "062129_hr1"
}

def addExtraIcons(_type: str, jobicon: str, classicon: str) -> str:
    if _type == "":
        return ""
    result: str = ""
    for index, icon in enumerate(ExtraIcons[_type]):
        if icon == "":
            continue
        nicon = getImage(f"{icon[:3]}000/{icon}_hr1.webp")
        if jobicon and nicon == jobicon:
            continue
        if classicon and nicon == classicon:
            continue
        result += f'    - name: "/assets/img/game_assets{nicon}"\n'
        result += f'      desc: "{ExtraIconsCategory[index]}"\n'
    return result


def addKlassJobs():
    global cjs_trans
    global cjs
    global addon_trans
    global status_ncj
    global additionalClassIcons
    global job_translations
    global klass_translations
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
    prepare_eureka_bozja_data(actions, status, status_trans, actions_trans, actiontransient_trans, cjs)
    eureka_actions = getEurekaActionDetails()
    bozja_actions = getBozjaActionDetails()
    #print_color_yellow(pretty_json(bozja_actions))
    cj_key_lookup = get_classJobKeyMapping()
    ncj = sorted(cjs_trans.items(), key=lambda item: int(item[0].split(".")[0]))
    status_ncj = getStatusFromFile(ncj)

    counter = 0
    # print_color_red(pretty_json(ncj))
    maxlvl = "0"
    for k in ncj:
        job_d = k[1]
        job = job_d['Name_de']
        job_abb = job_d['Abbreviation_de']
        job_data = skills.get(job, None)
        job_data_pvp = pvpskills.get(job, None)
        job_party_bonus = str(cjs[k[0]]['PartyBonus'])
        if job in ["Ninja", "Viper"]:
            job_party_bonus = "3"
        if not job_data:
            continue
        if job_d['0xID'] == "0":
            continue
        allPartyMittigation[job] = []
        counter += 1
        #if not job == "Rotmagier":
        #    continue
        base_class: str = cjs[k[0]]["ClassJob"]['Parent'] if not cjs[k[0]]["ClassJob"]['Parent'] == job else ""
        print_color_red(job)

        # prepare translation elements
        job_translations = {}
        for lang in LANGUAGES:
            job_translations[lang] = {}

        tmpmaxlvl = str(max([int(data["Level"]) for key, data in job_data.items() if int(data['Level']) < 99999]))
        if job == "Blaumagier":
            maxlvl = "80"
        else:
            maxlvl = tmpmaxlvl if int(tmpmaxlvl) > int(maxlvl) else maxlvl

        gear = gear_get(lvl_from=1, lvl_to=int(maxlvl), ilvl_from=1, ilvl_to=999999, rarity=[1, 7, 2, 3, 4], classjob=job_d['Abbreviation_de'], category="Rumpf")
        maxilvl = str(max([int(e["Level_Item"]) for e in gear]))

        filecontent = ""
        filecontent += '---\n'
        filecontent += 'wip: "True"\n'
        full_title_en = f'{job_d["Name_en"].title()} ({cjs_trans[cj_key_lookup[base_class]]["Name_en"].title()})' if base_class else job_d["Name_en"].title()
        filecontent += 'title:\n'
        for lang in LANGUAGES:
            full_title = f'{job_d[f"Name_{lang}"].title()} ({cjs_trans[cj_key_lookup[base_class]]["Name_"+lang].title()})' if base_class else job_d[f"Name_{lang}"].title()
            filecontent += f'  {lang}: "{full_title}"\n'
            klass_translations[lang][f'Sidebar_Title_Full_{full_title_en}'] = full_title
            klass_translations[lang][f'Content_Title_{full_title_en}'] = full_title

        filecontent += 'layout: klassen\n'
        filecontent += 'page_type: guide\n'
        roletypeinparty_en_name_key = f'{addon_trans[partybonus[job_party_bonus]]["Text_en"].title()}'
        #roletypeinparty_de_name_key = f'{addon_trans[partybonus[job_party_bonus]][f"Text_de"].title()}'
        filecontent += f'roletypeinparty: "{roletypeinparty_en_name_key}"\n'
        for lang in LANGUAGES:
            klass_translations[lang][f'Sidebar_Role_{roletypeinparty_en_name_key}'] = f'{addon_trans[partybonus[job_party_bonus]][f"Text_{lang}"].title()}'
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
        if os.path.exists(f"{os.getcwd()}/../assets/img/content/klassen/{job}.webp"):
            filecontent += f'image: "/assets/img/content/klassen/{job}.webp"\n'
        else:
            print(f"Missing img: {job}.webp")
        jobicon: str = getIconForJob(job_abb)
        if jobicon:
            filecontent += f'jobicon: "/assets/img/game_assets{jobicon}"\n'
        classicon: str = additionalClassIcons.get(job_abb, "")
        if classicon:
            classicon = getImage(f"062000/{classicon}.webp")
            filecontent += f'classicon: "/assets/img/game_assets/{classicon}"\n'
        if roletypeinparty_en_name_key:
            if roleicons.get(roletypeinparty_en_name_key, None):
                filecontent += f'roleicon: "/assets/img/game_assets/{getImage(roleicons[roletypeinparty_en_name_key])}"\n'
                if roletypeinparty_en_name_key == "Healer":
                    healicon, healname = roleiconsextra[cjs[k[0]]["col_46"]]
                    filecontent += f'roleiconextra:\n'
                    filecontent += f'    - name: "{healname}"\n'
                    filecontent += f'      icon: "{healicon}"\n'
        filecontent += getJobKristall(job)
        filecontent += "extraicons:\n"
        filecontent += addExtraIcons(base_class, jobicon, classicon)
        filecontent += addExtraIcons(job, jobicon, classicon)
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
        for lang in LANGUAGES:
            filecontent += f'    - term: "{job_d[f"Name_{lang}"].title()}"\n'
            if base_class:
                filecontent += f'    - term: "{cjs_trans[cj_key_lookup[base_class]]["Name_"+lang].title()}"\n'
        filecontent += f'sortid: {counter}\n'
        filecontent += f'order: {counter}\n'
        filecontent += f'plvl: {maxlvl}\n'
        filecontent += f'ilvl: {maxilvl}\n'
        if pvp:
            filecontent += f'deepdungeon: {job.lower()}\n'
        else:
            filecontent += f'pixelicon: {job.lower()}\n'
        filecontent += f'lodestone: "https://na.finalfantasyxiv.com/jobguide/{job_d["Name_en"].replace(" ", "").lower()}/"\n'
        for lang in LANGUAGES:
            n_lang = lang
            if lang in ["en", "cn", "ko"]:
                n_lang = "na"
            elif lang == "ja":
                n_lang = "jp"
            klass_translations[lang][f'Sidebar_LodestoneURL_{full_title_en}'] = f'https://{n_lang}.finalfantasyxiv.com/jobguide/{job_d["Name_en"].replace(" ", "").lower()}/'

        if base_class:
            filecontent += f'base_class: "{cjs_trans[cj_key_lookup[base_class]]["Name_en"].title()}"\n'
            baseclass_en_name_key = cjs_trans[cj_key_lookup[base_class]]["Name_en"].title()
            for lang in LANGUAGES:
                klass_translations[lang][f'Sidebar_BaseClass_{baseclass_en_name_key}'] = cjs_trans[cj_key_lookup[base_class]]["Name_"+lang].title()

        # ugly step to create translation file for abbreviations

        abbreviations = f"{cjs_trans[cj_key_lookup[base_class]]["Abbreviation_en"]}, {job_d["Abbreviation_en"]}" if base_class else job_d["Abbreviation_en"]
        filecontent += f'abbreviations: "{abbreviations}"\n'
        for lang in LANGUAGES:
            abbreviations_v = f"{cjs_trans[cj_key_lookup[base_class]]["Abbreviation_"+lang]}, {job_d["Abbreviation_"+lang]}" if base_class else job_d["Abbreviation_"+lang]
            klass_translations[lang][f'Sidebar_ClassShort_{abbreviations}'] = abbreviations_v

        filecontent += "bosses:\n"
        title_en = job_d["Name_en"].title()
        filecontent += f'  - title: "{title_en}"\n'
        for lang in LANGUAGES:
            #filecontent += f'      {lang}: ""\n'
            klass_translations[lang][f'Content_Title_{title_en}'] = job_d[f"Name_{lang}"].title()
        filecontent += "    id: \"" + "boss" + str(counter) + "\"\n"
        if job == "Blaumagier":
            x, job_translations = addBlueAttackDetails(job_data, craftactions_trans, actions_trans, items_trans, logdata, job_translations)
            filecontent += x
        else:
            attack_text, attack_skills = addAttackDetails(job_data)
            pvp_text, pvp_skills = addAttackDetails(job_data_pvp, True)
            filecontent += attack_text
            filecontent += pvp_text

        # get eureka und bozja data here for status bt add text later to filecontent
        ea, ea_text, eureka_skills = addEurekaActions(job, eureka_actions, job_translations)
        bz, bz_text, bozja_skills = addBozjaActions(job, bozja_actions, job_translations)
        filecontent += addStatusDetails(job, job_abb, attack_skills, pvp_skills, eureka_skills, bozja_skills)
        #filecontent += addOldStatusDetails(job, job_abb)
        filecontent += addTraitDetails(job)
        filecontent += ea_text
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

        write_class_translation_file(job_translations, job_d['Name_en'])
        filename = f"klassen_und_jobs/2013-01-01--2.0--{counter}--{job}.md"
        with open(filename, encoding="utf8") as f:
            doc = f.read()
        if not doc == filecontent:
            with open(filename, "w", encoding="utf8") as f:
                f.write(filecontent)
    return counter


def write_class_translation_file(job_translations, classname):
    filename_translation_location = f"../assets/translations/klassen/{classname}"
    if not os.path.exists(filename_translation_location):
        os.makedirs(filename_translation_location)
    for lang in LANGUAGES:
        # if case is used to save recompilation time if no file needs to be changed when running liveserver
        if os.path.exists(filename_translation_location + f"/{LANGUAGES_MAPPING[lang]}.json"):
            old_data_json = readJsonFile(filename_translation_location + f"/{LANGUAGES_MAPPING[lang]}.json")
            if not old_data_json == job_translations[lang]:
                writeJsonFile(filename_translation_location + f"/{LANGUAGES_MAPPING[lang]}.json", job_translations[lang])
        else:
            writeJsonFile(filename_translation_location + f"/{LANGUAGES_MAPPING[lang]}.json", job_translations[lang])


def run():
    os.chdir("..")
    get_class_translation_data()
    load_global_data()
    os.chdir("_posts")
    addKlassJobs()
    addChocobo(actions, actions_trans, actiontransient_trans, traits, traits_trans, traitstransient_trans, klass_translations, write_class_translation_file, addExtraIcons)
    write_class_translation_data(klass_translations)


if __name__ == "__main__":
    run()
    #test([{'Ort': 'Abyssos - Fünfter Kreis', 'Gegner': 'Proto-Karfunkel'}, {'Ort': 'Abyssos - Fünfter Kreis (episch)', 'Gegner': 'Proto-Karfunkel'}, {'Ort': 'Das Fenn', 'Gegner': 'Mahisha'}, {'Ort': 'Die Nichts-Arche', 'Gegner': 'Cuchulainn'}, {'Ort': 'Die Welt der Dunkelheit', 'Gegner': 'Cerberus'}, {'Ort': 'Himmelssäule (Ebenen 61-70)', 'Gegner': 'Kenko'}, {'Ort': 'Himmelssäule (Ebenen 81-90)', 'Gegner': 'Himmelssäulen-Gozu'}, {'Ort': 'Historisches Amdapor', 'Gegner': 'Verrottender Gourmet'}, {'Ort': 'Sankt Mocianne-Arboretum (schwer)', 'Gegner': 'Nullchu'}, {'Ort': 'Thavnair', 'Gegner': 'Yilan'}, {'Ort': 'Verschlungene Schatten 1', 'Gegner': '(InGame Hinweis)'}, {'Ort': 'Verschlungene Schatten 2 - 1', 'Gegner': 'Rafflesia'}, {'Ort': 'Verschlungene Schatten 3 - 4', 'Gegner': 'Schmerz Von Meracydia'}])





