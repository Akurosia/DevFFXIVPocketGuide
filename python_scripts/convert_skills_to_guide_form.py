#!/usr/bin/env python3
# coding: utf8
import os
from ffxiv_aku import print_color_red, gear_get, getLevel, deal_with_extras_in_text, readJsonFile, print_pretty_json, writeJsonFile
from ffxiv_aku import storeFilesInTmp, get_skills_for_player, loadDataTheQuickestWay, get_any_Logdata, print_color_green
from collections import OrderedDict
from operator import getitem

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

def get_class_translation_data():
    global klass_translations
    klass_translations = {}
    for lang in LANGUAGES:
        #klass_translations[lang] = readJsonFile(f'assets/translations/klassen/{LANGUAGES_MAPPING[lang]}.json')
        klass_translations[lang] = {}


def write_class_translation_data(data):
    origin = os.getcwd()
    os.chdir("..")
    for lang in LANGUAGES:
        klass_translations[lang] = writeJsonFile(f'assets/translations/klassen/{LANGUAGES_MAPPING[lang]}.json', data[lang])
    os.chdir(origin)


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


def addAttackDetails(job_data, pvp=False):
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

    #print_pretty_json(job_data.get('7429', ""))

    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, skill_data in job_data.items():
        #print_color_red(pretty_json(skill_data) + "\n")
        name = {}
        for lang in LANGUAGES:
            name[lang] = actions_trans.get(skill_data["Id"], {}).get(f"Name_{lang}", "").replace("\n", "</br>").replace("</br></br>", "</br>")
        if name["en"] == "":
            for lang in LANGUAGES:
                name[lang] = craftactions_trans[skill_data["Id"]][f"Name_{lang}"].replace("\n", "</br>").replace("</br></br>", "</br>")
        level = "0" if skill_data['Level'] == "99999" else skill_data['Level']

        #if _id == "7429":
        #    print_pretty_json(skill_data)

        tpye_damage = "Schaden" if skill_data["IsDamageSkill"] else None
        tpye_heilung = "Heilung" if skill_data["IsHealingSkill"] else None
        type_shield = "P-Schild-Mitigation" if skill_data["IsShieldSkill"] else None
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
        result += f'        icon: "{getImage(skill_data["Icon"])}"\n'
        result += f'        range: "{skill_data["Range"]}"\n'
        result += f'        effectrange: "{skill_data["EffectRange"]}"\n'
        result += f'        cast: "{skill_data["Cast"]}"\n'
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
            job_translations[lang][f'Class_Skill_Desc_{pvp_text_field}{name["en"]}'] = skill_data["Description"][lang]
        #if "%" in description["en"]:
        #    print(name["en"])
        #    print(description["en"])
        result += '        phases:\n'
        if pvp:
            result += '          - phase: "04"\n'
        else:
            result += '          - phase: "01"\n'
    return result, attack_skills


def addOldStatusDetails(job, job_abb):
    global logdata
    global status_trans
    global status_ncj
    global status
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
            for lang in LANGUAGES:
                result += f'          {lang}: "' + deal_with_extras_in_text(status_trans[_id][f"Name_{lang}"]) + '"\n'
            result += f'        title_id: "{key}"\n'
            if "_hr1" in getImage(s["icon"]):
                result += f'        icon: "{getImage(s["icon"])}"\n'
            else:
                result += f'        icon: "{getImage(s["icon"]).replace(".png", "_hr1.png")}"\n'
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
                result += '          icon: "' + actions_trans[str(int(s['was_added_by_action'], 16))]['Icon'].replace("ui/icon/", "") + '"\n'
                for lang in LANGUAGES:
                    result += f'          {lang}: "' + actions_trans[str(int(s['was_added_by_action'], 16))][f'Name_{lang}'] + '"\n'
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
            result += f'        icon: "{image}"\n'
        else:
            result += f'        icon: "{image.replace(".png", "_hr1.png")}"\n'
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
        result += f'        icon: "{getImage(trait_data["Icon"].replace(".tex", "_hr1.png"))}"\n'
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


def get_classJobKeyMapping():
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
        return f'jobkristall: "{image}"\n'
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
        return getImage("062000/" + additionalJobIcons[job_abb] + ".png")
    return icon

# these are the classes before they are job and usually dont need change
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
    maxlvl = ""
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
        allPartyMittigation[job] = []
        counter += 1
        #if not job == "Beschwörer":
        #    continue
        base_class = cjs[k[0]]["ClassJob"]['Parent'] if not cjs[k[0]]["ClassJob"]['Parent'] == job else None
        print_color_red(job)

        # prepare translation elements
        job_translations = {}
        for lang in LANGUAGES:
            job_translations[lang] = {}

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
        if os.path.exists(f"{os.getcwd()}/../assets/img/content/klassen/{job}.png"):
            filecontent += f'image: "/assets/img/content/klassen/{job}.png"\n'
        else:
            print(f"Missing img: {job}.png")
        jobicon = getIconForJob(job_abb)
        if jobicon:
            filecontent += f'jobicon: "{jobicon}"\n'
        classicon = additionalClassIcons.get(job_abb, None)
        if classicon:
            classicon = getImage(f"062000/{classicon}.png")
            filecontent += f'classicon: "{classicon}"\n'
        filecontent += getJobKristall(job)
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
    addChocobo(actions, actions_trans, actiontransient_trans, traits, traits_trans, traitstransient_trans, klass_translations, write_class_translation_file)
    write_class_translation_data(klass_translations)


if __name__ == "__main__":
    run()
    #test([{'Ort': 'Abyssos - Fünfter Kreis', 'Gegner': 'Proto-Karfunkel'}, {'Ort': 'Abyssos - Fünfter Kreis (episch)', 'Gegner': 'Proto-Karfunkel'}, {'Ort': 'Das Fenn', 'Gegner': 'Mahisha'}, {'Ort': 'Die Nichts-Arche', 'Gegner': 'Cuchulainn'}, {'Ort': 'Die Welt der Dunkelheit', 'Gegner': 'Cerberus'}, {'Ort': 'Himmelssäule (Ebenen 61-70)', 'Gegner': 'Kenko'}, {'Ort': 'Himmelssäule (Ebenen 81-90)', 'Gegner': 'Himmelssäulen-Gozu'}, {'Ort': 'Historisches Amdapor', 'Gegner': 'Verrottender Gourmet'}, {'Ort': 'Sankt Mocianne-Arboretum (schwer)', 'Gegner': 'Nullchu'}, {'Ort': 'Thavnair', 'Gegner': 'Yilan'}, {'Ort': 'Verschlungene Schatten 1', 'Gegner': '(InGame Hinweis)'}, {'Ort': 'Verschlungene Schatten 2 - 1', 'Gegner': 'Rafflesia'}, {'Ort': 'Verschlungene Schatten 3 - 4', 'Gegner': 'Schmerz Von Meracydia'}])





