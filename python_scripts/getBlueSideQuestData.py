import os
import json
from ffxiv_aku import *
from ffxiv_aku import loadDataTheQuickestWay, false, true, wrap_in_color_green, wrap_in_color_red
try:
    from .convert_skills_to_guide_form_helper.helper import getImage
    from .helper import *
except ImportError:
    from convert_skills_to_guide_form_helper.helper import *
    from helper import *
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

file_location = os.path.dirname(os.path.realpath(__file__))
patched_data = None
path_of_main_script = ""

# test()
results = {}
mresults = {}
error = []
expansions = {
    "A Realm Reborn": "arr",
    "Heavensward": "hw",
    "Stormblood": "sb",
    "Shadowbringers": "shb",
    "Endwalker": "ew",
    "Dawntrail": "dt",
    "Evercold": "ec",
}

categories = ['dungeon', 'klasse', 'prüfung', 'gewoelbesuche', 'gildengeheiß', 'freibrief', "raid", "araid", "wilderstamm", "windäther", "hohejagd", "feldexkursion", "achivment", "relik", "hildi"]


def clean_quest_name(name):
    return str(name or "").replace(" ", "").replace(" ", "").strip()


def first_text(*values):
    for value in values:
        if value:
            return str(value).strip()
    return ""


def get_row_name(value):
    if isinstance(value, dict):
        return first_text(value.get("Name_de"), value.get("Name_en"), value.get("Singular_de"), value.get("Singular_en"), value.get("Name"))
    return first_text(value)


def add_unique(elements, value):
    value = first_text(value)
    if value and value not in elements:
        elements.append(value)


def has_any(text, needles):
    text = str(text or "").lower()
    return any(needle.lower() in text for needle in needles)


def get_content_finder_type(content_finder):
    name = get_row_name(content_finder.get("Name_de", ""))
    content_type = get_row_name(content_finder.get("ContentType", {}))
    content_member_type = get_row_name(content_finder.get("ContentMemberType", {}))
    content_link_type = " ".join([name, content_type, content_member_type])

    if has_any(content_link_type, ["allianz", "alliance", "24-spieler", "24 player"]):
        return "Allianz Raid"
    if has_any(content_link_type, ["gildengeheiß", "gildengeheiss", "guildhest"]):
        return "Gildengeheiß"
    if has_any(content_link_type, ["gewölbesuch", "gewoelbesuch", "variant", "criterion", "unterstadt", "aloalo", "rokon"]):
        return "Gewölbesuche"
    if has_any(content_link_type, ["tiefe gewölbe", "tiefe gewoelbe", "deep dungeon", "palast der toten", "himmelssäule", "himmelssaeule", "eureka orthos"]):
        return "Tiefe Gewölbe"
    if has_any(content_link_type, ["prüfung", "pruefung", "trial"]):
        return "Prüfung"
    if has_any(content_link_type, ["dungeon", "instanz"]):
        return "Dungeon"
    if has_any(content_link_type, ["raid"]):
        return "Raid"
    if has_any(content_link_type, ["pvp", "front", "crystalline conflict", "crystalline conflict"]):
        return "PvP"
    return ""


def format_content_finder_unlock(content_finder):
    name = get_row_name(content_finder.get("Name_de", ""))
    content_type = get_content_finder_type(content_finder)
    if content_type and not has_any(name, [f"({content_type})", content_type]):
        return f"{name} ({content_type})"
    return name


def find_content_finder_by_content_id(content_id):
    content_id = str(content_id or "0")
    if content_id == "0":
        return None
    for key, value in contentfindercondition.items():
        if str(value.get('Content', {}).get('row_id', "0")) == content_id:
            return value
    return None


def get_journal_based_unlocks(quest):
    elements = []
    journal = get_row_name(quest.get('JournalGenre', {}))
    journal_group = get_row_name(quest.get('JournalCategory', {}))
    journal_all = " / ".join([journal, journal_group])

    if "Jobaufträge" in journal or "Gildenaufträge der" in journal:
        add_unique(elements, (journal.replace("-Jobaufträge", "").replace("Gildenaufträge der", "").strip() + " (Klassenquest)").strip())
    if has_any(journal_all, ["hildibrand", "inspektor"]):
        add_unique(elements, "Hildibrand (Questreihe)")
    if has_any(journal_all, ["relikt", "zodiak", "anima", "eureka", "resistance", "manderville-waffe", "phantom"]):
        add_unique(elements, "Reliktwaffen (Questreihe)")
    if has_any(journal_all, ["wilder stamm", "stammesvölker", "stammesvoelker", "beast tribe", "allied society"]):
        add_unique(elements, "Wilder Stamm")
    if has_any(journal_all, ["freibrief", "leves"]):
        add_unique(elements, "Freibriefe")
    if has_any(journal_all, ["hohe jagd", "jagd", "mobhunt", "hunt"]):
        add_unique(elements, "Hohe Jagd")
    return elements


def get_script_unlock_text(script_instruction):
    value = first_text(script_instruction)
    if value in ["", "NONE", "UNLOCK_IMAGE_SEASON"]:
        return ""
    if value in ["UNLOCK_BANZOKU", "UNLOCK_BEAST"]:
        return "Wilder Stamm"
    if value == "LOG_MOBHUNT_ORDER_UNLOCK":
        return "Hohe Jagd"
    if value == "UNLOCK_IMAGE_GC_TEAM":
        return "Kommando (Squadron)"
    if value.startswith("UNLOCK_IMAGE_DUNGEON_"):
        return value.replace("UNLOCK_IMAGE_DUNGEON_", "").replace("_", " ").title() + " (Gewölbesuche)"
    if value.startswith("UNLOCK_IMAGE_DEEP_DUNGEON"):
        return "Tiefe Gewölbe"
    if value.startswith("UNLOCK_AETHER_CURRENT") or value.startswith("UNLOCK_FIELD_MARKER"):
        return "Windätherquelle"
    if value.startswith("UNLOCK"):
        return value.replace("UNLOCK_", "").replace("_", " ").title()
    return ""


def get_aether_current_unlocks(quest):
    elements = []
    quest_name = clean_quest_name(quest.get('Name_de', ""))
    for key, value in aethercurrent.items():
        if quest_name == clean_quest_name(value.get('Quest', {}).get('Name_de', "")):
            add_unique(elements, "Windätherquelle")
    return elements


def getQuestName(name, lang="en", color=False):
    for key, value in quests.items():
        try:
            if value["Name_de"].replace(" ", "").replace(" ", "").strip().lower() == name.replace(" ", "").replace(" ", "").strip().lower():
                if color:
                    return wrap_in_color_green(value)
                else:
                    # print(value)
                    return value
        except KeyError:
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

def clear_script_params(params: list(dict[str, str]), quest) -> list:
    new_params = []
    for param in params:
        if param.get("ScriptArg", "0") == "0":
            continue
        if param.get("ScriptInstruction", "") == "":
            continue
        if re.match(r"^(ACTOR|POPRANGE|EVENTRANGE|EOBJECT|INVIS_ACTOR_|LOC_ACTOR_|LOC_ACTOR_(.+)|BIND_ACTOR|SEQEV_|BIND_BAK|BIND_PRI|BIND_ALX|CUT_EOV)(\d+)?", param.get("ScriptInstruction", "")):
            continue
        new_params.append(param)
    return new_params

def findContentForQuest(quest, key2):
    elements = []

    content_finder = find_content_finder_by_content_id(quest.get('InstanceContentUnlock', {}).get('row_id', 0))
    if content_finder:
        add_unique(elements, format_content_finder_unlock(content_finder))

    for value in get_journal_based_unlocks(quest):
        add_unique(elements, value)

    params = clear_script_params(quest.get("QuestParams", []), quest)

    for param in params:
        script_instruction = first_text(param.get("ScriptInstruction", ""))
        if "UNLOCK_DUNGEON" in script_instruction or "UNLOCK_ADD_NEW_CONTENT_TO_CF" in script_instruction:
            content_finder = find_content_finder_by_content_id(param.get("ScriptArg", 0))
            if content_finder:
                add_unique(elements, format_content_finder_unlock(content_finder))
            continue
        if "UNLOCK" in script_instruction or "LOG_MOBHUNT_ORDER_UNLOCK" == script_instruction:
            add_unique(elements, get_script_unlock_text(script_instruction))

    for value in get_aether_current_unlocks(quest):
        add_unique(elements, value)

    if len(elements) > 1:
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
    result_file = os.path.join(path_of_main_script, "_posts", "single_page_content", "2013-01-01--2.0--1--quests.md")
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
                    write(out, f'   level: "{quest["level"]}"')
                    write(out, f'   icon: "{getImage(quest["icon"])}"')
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
                    print_color_red(quest["name"])

        write(out, "---")


def checkPatchedData(_id):
    global patched_data
    for c in categories:
        if isinstance(patched_data.get(c, None), dict) and patched_data[c].get(_id, None):
            return True
    if patched_data.get(_id, None):
        return True
    return False


def getPatchedData(_id):
    global patched_data
    for c in categories:
        if isinstance(patched_data.get(c, None), dict) and patched_data[c].get(_id, None):
            return patched_data[c].get(_id, None)
    if patched_data.get(_id, None):
        return patched_data.get(_id, None)
    return None


def main():
    for key, quest in quests.items():
        _id = key
        if checkPatchedData(_id):
            # continue
            pass
        elif not str(quest['EventIconType'].get('row_id')) in ["8", "10"] and not checkPatchedData(str(_id)):
            continue
        elif not (quest['ClassJobCategory0']['Name_de'] in ["Alle Klassen", "Krieger, Magier", "Handwerker", "Handwerker, Sammler", "Krieger oder Magier (außer beschränkte Jobs)", "Sammler"] or quest['ClassJobCategory1']['Name_de'] in ["Alle Klassen", "Krieger, Magier", "Krieger oder Magier (außer beschränkte Jobs)", "Handwerker, Sammler", "Handwerker", "Sammler"]):
            continue
        # remove repeatables aas they never can unlock anything
        elif quest["IsRepeatable"] == "True":
            continue
        name = quest['Name_de'].replace(" ", "").replace(" ", "")
        try:
            level_data = getCoordsFromLocationLevel(quest['IssuerLocation'])
        except Exception as e:
            print_color_red(f"[MAIN] Error for getLevel using '{quest['IssuerLocation']}' and questname '{name}' with error '{e}'")
            error.append(name)

        if name in error:
            error.remove(name)

        new_element = {
            "name": name,
            "level": quest['ClassJobLevel'][0],
            "icon": getImage(quest['Icon']['path'].replace('.tex', "_hr1.webp")),
            "place": f"{level_data['region']}",
            "previousquest": [str(quest['PreviousQuest'][0].get("Name_de", "")), str(quest['PreviousQuest'][1].get("Name_de", "")), str(quest['PreviousQuest'][2].get("Name_de", ""))],
            "journalgenre": quest['JournalGenre']['Name_de'],
            "issuer_location_": {"x": level_data['x'], "y": level_data['y'], },
            "issuer_start_": quest['IssuerStart']['Singular_de'],
        }
        if quest['PlaceName']['Name_de']:
            new_element["place"] += f" > {quest['PlaceName']['Name_de']}"
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
        except ValueError:
            pass

        exp = quest['Expansion']['Name_de']
        if not results.get(exp, None):
            results[exp] = {}
            mresults[exp] = {}

        # change this for both stuff
        if new_element.get("unlocks", None):
            results[exp][_id] = new_element
        else:
            mresults[exp][_id] = new_element


def run(main_script=r"C:\Users\kamot\Documents\GitHub\DevFFXIVPocketGuide"):
    global path_of_main_script
    global patched_data
    path_of_main_script = main_script

    with open(f"{path_of_main_script}/python_scripts/patchedBlueQuestData.json", "r", encoding="utf8") as f:
        patched_data = json.load(f)
    main()
    getListOfMissingSideQuests(mresults)
    getFinalData(results)

    # this will sort the file
    with open(f"{path_of_main_script}/python_scripts/patchedBlueQuestData.json", "w", encoding="utf8") as f:
        json.dump(patched_data, f, sort_keys=True, indent=4, ensure_ascii=False)
# if not error == []:
#    print_pretty_json(error)
#    # sys.exit(0)

if __name__ == "__main__":
    run()
