import math

import os
import sys
from ffxiv_aku import *
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

file_location = os.path.dirname(os.path.realpath(__file__))

quests = loadDataTheQuickestWay("Quest.de.json", translate=false)
t_quests = loadDataTheQuickestWay("quest_all.json", translate=true)
levels = loadDataTheQuickestWay("Level.json", translate=false)
maps = loadDataTheQuickestWay("Map.json", translate=false)
cfc = loadDataTheQuickestWay("ContentFindercondition.de.json", translate=false)
ac = loadDataTheQuickestWay("AetherCurrent.json", translate=false)

expansions = {
    "A Realm Reborn": "arr",
    "Heavensward": "hw",
    "Stormblood": "sb",
    "Shadowbringers": "shb",
    "Endwalker": "ew",
}

categories = ['dungeon', 'klasse', 'prüfung', 'gewoelbesuche', 'gildengeheiß', 'freibrief', "raid", "araid", "wilderstamm", "windäther", "hohejagd", "feldexkursion", "achivment", "relik", "hildi"]


def getQuestName(name, lang="en", color=False):
    for key, value in t_quests.items():
        try:
            if value["Name_de"].replace(" ", "").replace(" ", "").strip().lower() == name.replace(" ", "").replace(" ", "").strip().lower():
                if color:
                    return wrap_in_color_green(value)
                else:
                    # print(value)
                    return value
        except:
            pass
    return wrap_in_color_red(name)


def filtered_quest(quest):
    filter_values = ['AcceptBool', 'ActorDespawnSeq', 'ActorSpawnSeq', 'AnnounceBool', 'Behavior', 'CanTargetBool', 'ConditionBool', 'ConditionOperator', 'ConditionType', 'ConditionValue', 'CountableNum', 'ItemBool', 'Listener', 'QualifiedBool', 'QuestUInt8',
                     'VisibleBool', 'ToDoQty', 'ToDoMainLocation', 'ToDoCompleteSeq', 'ToDoChildLocation', 'OptionalItem', 'col_', 'Stain_Reward_', 'Item_Reward_', 'ItemCount_Reward_', 'Item_Catalyst_']
    new_element = {}
    if not quest['EventIconType'] == "EventIconType#8":
        return
    for key2, value in quest.items():
        if any([text in key2 for text in filter_values]):
            continue
        new_element[key2] = value
    return new_element


def findContentForQuest(quest, key2):
    global cfc
    elements = []
    if not quest['InstanceContent']['Unlock'] == "InstanceContent#0":
        _id = quest['InstanceContent']['Unlock']
        for key, value in cfc.items():
            if value['Content'] == _id:
                if not value['Name'] in elements:
                    elements.append(value['Name'])

    if "Jobaufträge" in quest['JournalGenre'] or "Gildenaufträge der" in quest['JournalGenre']:
        x = (quest['JournalGenre'].replace("-Jobaufträge", "")).replace("Gildenaufträge der", "") + " (Klassenquest)"
        if not x in elements:
            elements.append(x)

    for i in range(0, 50):
        if "UNLOCK_DUNGEON" in quest["Script"]['Instruction'][str(i)] or "UNLOCK_ADD_NEW_CONTENT_TO_CF" in quest["Script"]['Instruction'][str(i)]:
            _id = "InstanceContent#" + quest["Script"]['Arg'][str(i)]
            for key, value in cfc.items():
                if value['Content'] == _id:
                    if not value['Name'] in elements:
                        elements.append(value['Name'])
        elif "UNLOCK" in quest["Script"]['Instruction'][str(i)]:
            value = quest["Script"]['Instruction'][str(i)]
            if "UNLOCK_BANZOKU" == value or "UNLOCK_BEAST" == value:
                value = "Wilder Stamm"
            elif "UNLOCK_IMAGE_DUNGEON_" in value:
                value = value.replace("UNLOCK_IMAGE_DUNGEON_", "")
            elif "UNLOCK_IMAGE_SEASON" == value:
                continue
            elif "LOG_MOBHUNT_ORDER_UNLOCK" == value:
                value = "Hohe Jagd"
            elif "UNLOCK_IMAGE_GC_TEAM" == value:
                value = "Kommando (Squadron)"
            if not value in elements:
                elements.append(value)

    for key, value in ac.items():
        if quest['Name'].replace(" ", "").replace(" ", "").strip() == value['Quest'].replace(" ", "").replace(" ", "").strip():
            if not "[Location] Windätherquelle " in elements:
                elements.append("[Location] Windätherquelle ")
    if len(elements) > 1:
        # print(key2)
        # print(quest['Name'])
        # print(elements)
        # print()
        return " / ".join(elements)
    elif len(elements) > 0:
        return elements[0]
    else:
        return ""


def getListOfMissingSideQuests(results):
    # print_pretty_json(results)
    print("{")
    for key, value in results.items():
        counter = 0
        if len(value) > 0:
            print(f"{key} ({len(value)})")
            for id, quest in value.items():
                if patched_data.get(str(id), None):
                    continue
                    pass
                counter += 1
                if quest.get('unlocks', None):
                    print(f"\t\"{id}\": " + "{")
                    print(f"\t\t\"name\": \"{quest['name']}\",")
                    print(f"\t\t\"unlocks\": \"{quest.get('unlocks', '')}\"")
                    print("\t},")
                else:
                    print(f"\t\"{id}\": \"{quest['name']}\",")
            print(f"{key} ({counter})")
    print("}")


def write(out, data):
    out.write(str(data) + "\n")


def getFinalData(results):
    global file_location
    result_file = os.path.join(file_location, "..", "_posts", "quests", "2013-01-01--2.0--1--quests.md")
    print_color_green(f"Write result to {result_file}")
    with open(result_file, "w", encoding="utf8") as out:
        write(out, "---")
        write(out, 'wip: "True"')
        write(out, 'title: "Quests"')
        write(out, 'layout: index')
        write(out, 'page_type: guide')
        write(out, 'categories: "quests"')
        write(out, 'quests:')
        for key, value in results.items():
            for id, quest in value.items():
                try:
                    translated_quest_names = getQuestName(quest["name"])
                    write(out, f' - id: "{id}"')
                    write(out, f'   expansion: "{key}"')
                    write(out, f'   instanceType: "quest_{expansions[key]}"')
                    write(out, f'   name:')
                    write(out, f'     de: "{quest["name"]}"')
                    write(out, f'     en: "{translated_quest_names["Name_en"].replace(" ", "").replace(" ", "")}"')
                    write(out, f'     fr: "{translated_quest_names["Name_fr"].replace(" ", "").replace(" ", "")}"')
                    write(out, f'     ja: "{translated_quest_names["Name_ja"].replace(" ", "").replace(" ", "")}"')
                    write(out, f'     cn: "{translated_quest_names["Name_cn"].replace(" ", "").replace(" ", "")}"')
                    write(out, f'     ko: "{translated_quest_names["Name_ko"].replace(" ", "").replace(" ", "")}"')
                    write(out, f'   level: "{quest["level"]}"')
                    write(out, f'   icon: "{quest["icon"].replace("ui/icon","")}"')
                    write(out, f'   journal: "{quest["journalgenre"]}"')
                    write(out, f'   place: "{quest["place"]}"')
                    write(out, f'   location: "X: {quest["issuer_location_"]["x"]} / Y: {quest["issuer_location_"]["y"]}"')
                    write(out, f'   issuer: "{quest["issuer_start_"]}"')
                    write(out, f'   unlocks: "{quest["unlocks"]}"')
                    if len(quest['previousquest']) > 0:
                        write(out, f'   previousquest:')
                        for q in quest['previousquest']:
                            write(out, f'   - "{q}"')
                except:
                    print_color_red(translated_quest_names)

        write(out, "---")


def checkPatchedData(_id):
    global patched_data
    for c in categories:
        if patched_data[c].get(_id, None):
            return True
    if patched_data.get(_id, None):
        return True
    return False


def getPatchedData(_id):
    global patched_data
    for c in categories:
        if patched_data[c].get(_id, None):
            return patched_data[c].get(_id, None)
    if patched_data.get(_id, None):
        return patched_data.get(_id, None)
    return None


with open("patchedBlueQuestData.json", "r", encoding="utf8") as f:
    patched_data = json.load(f)
# this will sort the file
with open("patchedBlueQuestData.json", "w", encoding="utf8") as f:
    json.dump(patched_data, f, sort_keys=True, indent=4, ensure_ascii=False)

# test()
results = {}
mresults = {}
error = []
for key, quest in quests.items():
    _id = key
    if checkPatchedData(_id):
        # continue
        pass
    elif not quest['EventIconType'] in ["EventIconType#8", "EventIconType#10"] and not checkPatchedData(str(_id)):
        continue
    elif not (quest['ClassJobCategory']["0"] in ["Alle Klassen", "Krieger, Magier", "Handwerker", "Handwerker, Sammler", "Krieger oder Magier (außer beschränkte Jobs)", "Sammler"] or quest['ClassJobCategory']["1"] in ["Alle Klassen", "Krieger, Magier", "Krieger oder Magier (außer beschränkte Jobs)", "Handwerker, Sammler", "Handwerker", "Sammler"]):
        continue
    # remove repeatables aas they never can unlock anything
    elif quest["IsRepeatable"] == "True":
        continue

    name = quest['Name'].replace(" ", "").replace(" ", "")
    try:
        level_data = getLevel(quest['Issuer']['Location'])
    except Exception as e:
        print((e, name))
        error.append(name)

    if name in error:
        error.remove(name)
    new_element = {
        "name": name,
        "level": quest['ClassJobLevel']["0"],
        "icon": quest['Icon']['Value'].replace('.tex', "_hr1.png"),
        "place": f"{level_data['region']}",
        "previousquest": [quest['PreviousQuest']["0"], quest['PreviousQuest']["1"], quest['PreviousQuest']["2"]],
        "journalgenre": quest['JournalGenre'],
        "issuer_location_": {"x": level_data['x'], "y": level_data['y'], },
        "issuer_start_": quest['Issuer']['Start'],
    }
    if quest['PlaceName']:
        new_element["place"] += f" > {quest['PlaceName']}"
    if level_data['placename'] and level_data['placename'] not in new_element["place"]:
        new_element["place"] += f" > {level_data['placename']}"
    try:
        new_element["unlocks"] = findContentForQuest(quest, key)
    except Exception as e:
        print(e)
        asdfasdf
        pass

    if checkPatchedData(str(_id)):
        new_element["unlocks"] = getPatchedData(_id)

    try:
        new_element['previousquest'].remove("")
        new_element['previousquest'].remove("")
    except:
        pass

    exp = quest['Expansion']
    if not results.get(exp, None):
        results[exp] = {}
        mresults[exp] = {}

    # change this for both stuff
    if new_element.get("unlocks", None):
        results[exp][_id] = new_element
    else:
        mresults[exp][_id] = new_element


getListOfMissingSideQuests(mresults)
getFinalData(results)
# if not error == []:
#    print_pretty_json(error)
#    # sys.exit(0)
