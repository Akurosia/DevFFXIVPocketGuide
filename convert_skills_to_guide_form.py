#!/usr/bin/env python3
# coding: utf8
import os
import sys
from ffxiv_aku import *
from collections import OrderedDict
from operator import getitem
import math

skills = None
pvpskills = None
logdata = None
cj = None
cjs = None
actions = None
craftactions = None
statuss = None
statusss = None
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


def load_global_data():
    global skills
    global pvpskills
    global logdata
    global cj
    global cjs
    global actions
    global craftactions
    global statuss
    global statusss
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
    skills = get_skills_for_player()
    pvpskills = get_skills_for_player(True)
    logdata = get_any_Logdata()
    cj = loadDataTheQuickestWay("classjob_all.json", translate=True)
    cjs = loadDataTheQuickestWay("ClassJob.de.json")
    actions = loadDataTheQuickestWay("action_all.json", translate=True)
    craftactions = loadDataTheQuickestWay("craftaction_all.json", translate=True)
    statuss = loadDataTheQuickestWay("status_all.json", translate=True)
    statusss = loadDataTheQuickestWay("Status.de.json")
    traits = loadDataTheQuickestWay("Trait.de.json")
    traitss = loadDataTheQuickestWay("trait_all.json", translate=True)
    traitstransient = loadDataTheQuickestWay("TraitTransient.de.json")
    aozactions = loadDataTheQuickestWay("aozaction_all.json", translate=True)
    aozactiontransient = loadDataTheQuickestWay("AozActionTransient.de.json")
    quests = loadDataTheQuickestWay("Quest.de.json")
    questss = loadDataTheQuickestWay("quest_all.json", translate=True)
    levels = loadDataTheQuickestWay("Level.json", translate=false)
    maps = loadDataTheQuickestWay("Map.json", translate=false)
    leves = loadDataTheQuickestWay("leve.de.json", translate=False)
    trans_leves = loadDataTheQuickestWay("leve_all.json", translate=True)
    craftleves = loadDataTheQuickestWay("craftleve.json", translate=False)


def getImage(image):
    image = image.replace(".tex", "_hr1.png")
    image = image.replace("ui/icon/", "")
    return image


def writeline(f, data):
    f.write(data)
    f.write("\n")


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


def addBlueAttackDetails(f, job_data):
    global actions
    global aozactions
    global aozactiontransient
    writeline(f, "    attacks:")
    # get special aoz action data from correct files e.g. number in blu spell book and description
    for x, y in job_data.items():
        for key, value in aozactions.items():
            if y['Name'] == value['Name_de']:
                if not aozactiontransient[key]['Location'] == "":
                    job_data[x]["Location"] = {"Ort": aozactiontransient[key]['Location'], "Gegner": "(InGame Hinweis)"}
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = aozactiontransient[key]['Number']
                job_data[x]["Description"] += "\n\n#########################################\n\n" + aozactiontransient[key]['Description']
            elif y['Name'] == "Weißer Tod":
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = "84"
            elif y['Name'] == "Göttlicher Katarakt":
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = "89"

        if not y.get("Number", None):
            job_data[x]["Number"] = job_data[x]["Level"]
            job_data[x]["Level"] = "90" + job_data[x]["Level"]
    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, skill_data in job_data.items():
        locations = []
        if skill_data.get('Location', None):
            locations.append(skill_data['Location'])
        en_name = actions.get(skill_data['id'], {}).get("Name_en", "").title()
        fr_name = actions.get(skill_data['id'], {}).get("Name_fr", "").title()
        ja_name = actions.get(skill_data['id'], {}).get("Name_ja", "").title()
        cn_name = actions.get(skill_data['id'], {}).get("Name_cn", "").title()
        ko_name = actions.get(skill_data['id'], {}).get("Name_ko", "").title()
        if en_name == "":
            en_name = craftactions[skill_data['id'] + ".0"]["Name_en"]
        level = skill_data['Level']
        desc = skill_data["Description"].replace("</br></br>", "</br>")
        locations = getBLULocationsFromLogdata(skill_data["Name"], locations)
        locations = sorted(locations, key=lambda x: x['Ort'])
        max_zone_length = 0
        max_enemyname_length = 0
        for location in locations:
            if len(location['Ort']) > max_zone_length:
                max_zone_length = len(location['Ort'])
            if len(location['Gegner']) > max_enemyname_length:
                max_enemyname_length = len(location['Gegner'])
        if not locations == []:
            desc += "\n\n#########################################\n\nLOCATIONS:\n" + "&emsp;Zone".ljust(max_zone_length) + " -> " + "Gegnername".ljust(max_enemyname_length) + ":"
        for location in locations:
            desc += "\n&emsp;" + location["Ort"].ljust(max_zone_length) + " -> " + location["Gegner"].ljust(max_enemyname_length)
        desc = desc.replace("\n", "</br>").replace("</br></br>", "</br>")
        if skill_data.get("Number", None) and int(level) < 901:
            writeline(f, f'      - title:')
            writeline(f, f'          de: "{level}. {skill_data["Name"]}"')
            writeline(f, f'          en: "{level}. {en_name}"')
            writeline(f, f'          fr: "{level}. {fr_name}"')
            writeline(f, f'          ja: "{level}. {ja_name}"')
            writeline(f, f'          cn: "{level}. {cn_name}"')
            writeline(f, f'          ko: "{level}. {ko_name}"')
        else:
            writeline(f, f'      - title:')
            writeline(f, f'          de: "{skill_data["Name"]}"')
            writeline(f, f'          en: "{en_name}"')
            writeline(f, f'          fr: "{fr_name}"')
            writeline(f, f'          ja: "{ja_name}"')
            writeline(f, f'          cn: "{cn_name}"')
            writeline(f, f'          ko: "{ko_name}"')
        writeline(f, f'        title_id: "{skill_data["id"].split(".")[0]}"')
        if skill_data.get("Number", None):
            writeline(f, f'        level: "{skill_data["Number"]}"')
        else:
            writeline(f, f'        level: "{level}"')
        writeline(f, f'        icon: "{getImage(skill_data["Icon"])}"')
        writeline(f, f'        range: "{skill_data["Range"]}"')
        writeline(f, f'        effectrange: "{skill_data["EffectRange"]}"')
        writeline(f, f'        cast: "{skill_data["Cast"]}"')
        writeline(f, f'        recast: "{skill_data["Recast"]}"')
        writeline(f, f'        kategorie: "{skill_data["Kategorie"]}"')
        writeline(f, f'        description: "{desc}"')
        writeline(f, f'        phases:')
        writeline(f, f'          - phase: "01"')


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


def addAttackDetails(f, job_data, pvp=False):
    global actions
    global craftactions
    # only print for normal attacks
    if not pvp:
        writeline(f, "    attacks:")
    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, skill_data in job_data.items():
        en_name = actions.get(skill_data['id'], {}).get("Name_en", "").title()
        fr_name = actions.get(skill_data['id'], {}).get("Name_fr", "").title()
        ja_name = actions.get(skill_data['id'], {}).get("Name_ja", "").title()
        cn_name = actions.get(skill_data['id'], {}).get("Name_cn", "").title()
        ko_name = actions.get(skill_data['id'], {}).get("Name_ko", "").title()
        if en_name == "":
            en_name = craftactions[skill_data['id']]["Name_en"].title()
            fr_name = craftactions[skill_data['id']]["Name_fr"].title()
            ja_name = craftactions[skill_data['id']]["Name_ja"].title()
            cn_name = craftactions[skill_data['id']]["Name_cn"].title()
            ko_name = craftactions[skill_data['id']]["Name_ko"].title()
        level = "0" if skill_data['Level'] == "99999" else skill_data['Level']
        desc = skill_data["Description"].replace("\n", "</br>").replace("</br></br>", "</br>")
        writeline(f, f'      - title:')
        writeline(f, f'          de: "{skill_data["Name"]}"')
        writeline(f, f'          en: "{en_name}"')
        writeline(f, f'          fr: "{fr_name}"')
        writeline(f, f'          ja: "{ja_name}"')
        writeline(f, f'          cn: "{cn_name}"')
        writeline(f, f'          ko: "{ko_name}"')
        writeline(f, f'        title_id: "{skill_data["id"].split(".")[0]}"')
        writeline(f, f'        level: "{level}"')
        writeline(f, f'        type: "{skill_data["Type"]}"')
        writeline(f, f'        icon: "{getImage(skill_data["Icon"])}"')
        writeline(f, f'        range: "{skill_data["Range"]}"')
        writeline(f, f'        effectrange: "{skill_data["EffectRange"]}"')
        writeline(f, f'        cast: "{skill_data["Cast"]}"')
        writeline(f, f'        recast: "{skill_data["Recast"]}"')
        writeline(f, f'        kategorie: "{skill_data["Kategorie"]}"')
        writeline(f, f'        description: "{desc}"')
        writeline(f, f'        phases:')
        if pvp:
            writeline(f, f'          - phase: "04"')
        else:
            writeline(f, f'          - phase: "01"')


def addStatusDetails(f, job):
    global logdata
    global statusss
    global statuss
    jobstatusdata = logdata["Klassen"].get(job, {}).get("status", {})
    if not jobstatusdata == {}:
        jobstatusdata = OrderedDict(sorted(jobstatusdata.items(), key=lambda x: getitem(x[1], 'name')))
        writeline(f, "    debuffs:")
        for key, status in jobstatusdata.items():
            _id = str(int(key, 16))
            desc = statusss[_id]["Description"].replace("\n", "</br>").replace("</br></br>", "</br>")
            writeline(f, f'      - title:')
            writeline(f, f'          de: "{status["name"].title()}"')
            writeline(f, f'          en: "{statuss[_id]["Name_en"].title()}"')
            writeline(f, f'          fr: "{statuss[_id]["Name_fr"].title()}"')
            writeline(f, f'          ja: "{statuss[_id]["Name_ja"].title()}"')
            writeline(f, f'          cn: "{statuss[_id]["Name_cn"].title()}"')
            writeline(f, f'          ko: "{statuss[_id]["Name_ko"].title()}"')
            writeline(f, f'        title_id: "{key}"')
            writeline(f, f'        icon: "{getImage(status["icon"])}"')
            writeline(f, f'        description: "{desc}"')
            writeline(f, f'        durations: {status["duration"]}')
            writeline(f, '        phases:')
            writeline(f, '          - phase: "02"')


def addTraitDetails(f, job):
    global traits
    # TODO get traits by class
    writeline(f, "    traits:")
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
        desc = traitstransient[_id]["Description"].replace("\n", "</br>").replace("</br></br>", "</br>")
        level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        writeline(f, f'      - title:')
        writeline(f, f'          de: "{trait_data["Name"].title()}"')
        writeline(f, f'          en: "{en_name}"')
        writeline(f, f'          fr: "{fr_name}"')
        writeline(f, f'          ja: "{ja_name}"')
        writeline(f, f'          cn: "{cn_name}"')
        writeline(f, f'          ko: "{ko_name}"')
        writeline(f, f'        title_id: "{_id.split(".")[0]}"')
        writeline(f, f'        level: "{level}"')
        writeline(f, f'        icon: "{getImage(trait_data["Icon"].replace(".tex", "_hr1.png"))}"')
        writeline(f, f'        description: "{desc}"')
        writeline(f, f'        phases:')
        writeline(f, f'          - phase: "03"')


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


def addCrafterLeve(f, job, all_crafter_leves):
    for key, value in all_crafter_leves.items():
        if job not in key:
            continue
        writeline(f, "    leves:")
        job_leve_data = OrderedDict(sorted(value.items(), key=lambda x: int(getitem(x[1], 'level'))))
        for _id, leve_data in job_leve_data.items():
            level = "0" if leve_data['level'] == "99999" else leve_data['level']
            writeline(f, f'      - title:')
            writeline(f, f'          de: "{leve_data["Name_DE"]}"')
            writeline(f, f'          en: "{leve_data["Name_EN"]}"')
            writeline(f, f'          fr: "{leve_data["Name_FR"]}"')
            writeline(f, f'          ja: "{leve_data["Name_JA"]}"')
            writeline(f, f'          cn: "{leve_data["Name_CN"]}"')
            writeline(f, f'          ko: "{leve_data["Name_KO"]}"')
            writeline(f, f'        title_id: "{leve_data["0xID"]}"')
            writeline(f, f'        level: "{level}"')
            writeline(f, f'        leveamount: "{leve_data["Freibriefanzahl"]}"')
            if leve_data.get('item', None):
                writeline(f, f'        item: "{leve_data["item"]}"')
                writeline(f, f'        itemamount: "{leve_data["item_amount"]}"')
                writeline(f, f'        repeat: "{leve_data["Wiederholbar"]}"')
            writeline(f, f'        exphq: "{leve_data["EXP_per_full_hq_leve"]}"')
            writeline(f, f'        gilhq: "{leve_data["Gil_per_full_hq_leve"]}"')
            writeline(f, f'        phases:')
            writeline(f, f'          - phase: "04"')
        return True
    return False


def getMaps(_map):
    global maps
    for key, value in maps.items():
        if value['Id'] == _map:
            return value
    sys.exit()


def truncate(f):
    result = math.floor(f * 10 ** 1) / 10 ** 1
    return result


def ToMapCoordinate(val, sizefactor):
    c = sizefactor / 100.0
    val *= c
    return ((41.0 / c) * ((val + 1024.0) / 2048.0)) + 1


def getLevel(level):
    global levels
    try:
        level = levels[level.replace('Level#', "")]
        map_ = getMaps(level['Map'])
        x = truncate(ToMapCoordinate(float(level['X'].replace(",", ".")), float(map_['SizeFactor'])))
        y = truncate(ToMapCoordinate(float(level['Z'].replace(",", ".")), float(map_['SizeFactor'])))
        return {"x": x, "y": y, "region": map_['PlaceName']['Region'], "placename": map_['PlaceName']['Value']}
    except Exception as e:
        print(f"Error in getLevel: {e}")
        return None


def addQuestkDetails(f, job, pvp):
    global quests
    global questss
    newjob, newclass = convertJobToAbrev(job)
    klassenquests = {}
    for key, quest in quests.items():
        if "Restaurierung der Reliktwaffen" in quest['Name']:
            continue
        if quest['ClassJobCategory']["0"] in [newjob, newclass] or quest['ClassJobCategory']["1"] in [newjob, newclass]:
            #print(" \t" + quest['Name'])
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
    writeline(f, "    quests:")
    for _level in sorted(klassenquests):
        quest = klassenquests[_level]
        en_name = questss.get(quest['id'], {}).get("Name_en", "").replace(" ", "").replace(" ", "").title()
        fr_name = questss.get(quest['id'], {}).get("Name_fr", "").replace(" ", "").replace(" ", "").title()
        ja_name = questss.get(quest['id'], {}).get("Name_ja", "").replace(" ", "").replace(" ", "").title()
        cn_name = questss.get(quest['id'], {}).get("Name_cn", "").replace(" ", "").replace(" ", "").title()
        ko_name = questss.get(quest['id'], {}).get("Name_ko", "").replace(" ", "").replace(" ", "").title()
        level = "0" if quest['level'] == "99999" else quest['level']
        #desc = skill_data["Description"].replace("\n", "</br>")
        writeline(f, f'      - title:')
        writeline(f, f'          de: "{quest["name"].title().replace(" ", "").replace(" ", "")}"')
        writeline(f, f'          en: "{en_name}"')
        writeline(f, f'          fr: "{fr_name}"')
        writeline(f, f'          ja: "{ja_name}"')
        writeline(f, f'          cn: "{cn_name}"')
        writeline(f, f'          ko: "{ko_name}"')
        writeline(f, f'        title_id: "{quest["id"].split(".")[0]}"')
        writeline(f, f'        level: "{level}"')
        writeline(f, f'        expansion: "{quest["expansion"]}"')
        writeline(f, f'        journalgenre: "{quest["journalgenre"]}"')
        writeline(f, f'        issuer_location: "{quest["issuer_location_"]}"')
        writeline(f, f'        issuer_start: "{quest["issuer_start_"]}"')
        writeline(f, f'        place: "{quest["place"]}"')
        writeline(f, f'        phases:')
        if pvp:
            writeline(f, f'          - phase: "05"')
        else:
            writeline(f, f'          - phase: "04"')


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


def main():
    global cj
    counter = 0
    # for job, job_data in skills.items():
    all_crafter_leves = getCrafterLeves()
    all_gatherer_leves = getGathererLeves()

    ncj = sorted(cj.items(), key=lambda item: int(item[0].split(".")[0]))
    maxlvl = ""
    for k in ncj:
        job_d = k[1]
        job = job_d['Name_de']
        en_name = job_d["Name_en"].title()
        job_data = skills.get(job, None)
        job_data_pvp = pvpskills.get(job, None)
        if not job_data:
            continue
        print(job)

        tmpmaxlvl = str(max([int(data["Level"]) for key, data in job_data.items() if int(data['Level']) < 99999]))
        if job == "Blaumagier":
            maxlvl = "70"
        else:
            maxlvl = tmpmaxlvl if tmpmaxlvl > maxlvl else maxlvl

        gear = ffxiv_aku_api.get_gear(lvl_from=1, lvl_to=maxlvl, ilvl_from=1, classjob=job_d['Abbreviation_de'], category="Rumpf")
        maxilvl = str(max([int(e["Level_Item"]) for e in gear]))

        counter += 1
        with open(f"klassen_und_jobs/2013-01-01--2.0--{counter}--{job}.md", "w", encoding="utf8") as f:
            writeline(f, '---')
            writeline(f, 'wip: "True"')
            writeline(f, 'title:')
            writeline(f, f'  de: "{job_d["Name_de"].title()}"')
            writeline(f, f'  en: "{job_d["Name_en"].title()}"')
            writeline(f, f'  fr: "{job_d["Name_fr"].title()}"')
            writeline(f, f'  ja: "{job_d["Name_ja"].title()}"')
            writeline(f, f'  cn: "{job_d["Name_cn"].title()}"')
            writeline(f, f'  ko: "{job_d["Name_ko"].title()}"')
            writeline(f, 'layout: klassen')
            writeline(f, 'page_type: guide')
            writeline(f, 'categories: "klassenjobs"')
            writeline(f, 'difficulty: "Normal"')
            writeline(f, 'instanceType: "klassenjobs"')

            if classDetails.get(job, {}):
                writeline(f, f'date: "{classDetails[job]["date"]}"')
                writeline(f, f'patchNumber: "{classDetails[job]["patchNumber"]}"')
                writeline(f, f'patchName: "{classDetails[job]["patchName"]}"')
            else:
                writeline(f, 'date: "2013.01.01"')
                writeline(f, 'patchNumber: "2.0"')
                writeline(f, 'patchName: "A Realm Reborn"')

            # this will be empty for non jobs (crafter/gatherer are clases so we know if they have pvp spells)
            pvp = getQuestName(job)

            writeline(f, 'slug: "klassen_und_jobs_' + job.lower() + '"')
            if os.path.exists(f"{os.getcwd()}/../assets/img/content/klassen/{job}.png"):
                writeline(f, 'image:')
                writeline(f, f'    - url: "/assets/img/content/klassen/{job}.png"')
                #writeline(f, f'    - url: "/assets/img/content/klassen/{job}.png"')
            else:
                print(f"Missing img: {job}.png")
            writeline(f, 'terms:')
            writeline(f, '    - term: "Klassen"')
            writeline(f, '    - term: "Jobs"')
            writeline(f, '    - term: "Skills"')
            writeline(f, '    - term: "Status"')
            writeline(f, '    - term: "Traits"')
            writeline(f, f'    - term: "{job_d["Name_de"].title()}"')
            writeline(f, f'    - term: "{job_d["Name_en"].title()}"')
            writeline(f, f'    - term: "{job_d["Name_fr"].title()}"')
            writeline(f, f'    - term: "{job_d["Name_ja"].title()}"')
            writeline(f, f'    - term: "{job_d["Name_cn"].title()}"')
            writeline(f, f'    - term: "{job_d["Name_ko"].title()}"')
            writeline(f, f'sortid: {counter}')
            writeline(f, f'order: {counter}')
            writeline(f, f'plvl: {maxlvl}')
            writeline(f, f'ilvl: {maxilvl}')
            writeline(f, "bosses:")
            writeline(f, "  - title:")
            writeline(f, f'      de: "{job_d["Name_de"].title()}"')
            writeline(f, f'      en: "{job_d["Name_en"].title()}"')
            writeline(f, f'      fr: "{job_d["Name_fr"].title()}"')
            writeline(f, f'      ja: "{job_d["Name_ja"].title()}"')
            writeline(f, f'      cn: "{job_d["Name_cn"].title()}"')
            writeline(f, f'      ko: "{job_d["Name_ko"].title()}"')
            writeline(f, "    id: \"" + "boss" + str(counter) + "\"")
            if job == "Blaumagier":
                addBlueAttackDetails(f, job_data)
            else:
                addAttackDetails(f, job_data)
                addAttackDetails(f, job_data_pvp, True)
            addStatusDetails(f, job)
            addTraitDetails(f, job)
            cleves = addCrafterLeve(f, job, all_crafter_leves)
            gleves = addCrafterLeve(f, job, all_gatherer_leves)
            #print(f"{cleves} - {gleves}")
            addQuestkDetails(f, job, pvp or leves)
            writeline(f, "    sequence:" + "")
            writeline(f, "      - phase: \"01\"")
            writeline(f, "        name: \"Skills\"")
            writeline(f, "      - phase: \"02\"")
            writeline(f, "        name: \"Status\"")
            writeline(f, "      - phase: \"03\"")
            writeline(f, "        name: \"Traits\"")
            writeline(f, "      - phase: \"04\"")
            if pvp:
                writeline(f, "        name: \"PvP\"")
                writeline(f, "      - phase: \"05\"")
            if cleves or gleves:
                writeline(f, "        name: \"Freibriefe\"")
                writeline(f, "      - phase: \"05\"")
            writeline(f, "        name: \"Quests\"")
            writeline(f, '---')


if __name__ == "__main__":
    load_global_data()
    os.chdir("./_posts")
    main()
