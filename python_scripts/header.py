#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
from ffxiv_aku import print_color_red, true, glob
from copy import deepcopy
from typing import Any
try:
    from python_scripts.constants import LANGUAGES
    from python_scripts.helper import seperate_data_into_array, getImage, EntryType
    from python_scripts.fileimports import (
        territorytype_trans,
        territorytype,
        patchversions,
        mounts,
        minions,
        orchestrions,
        orchestrionpath,
        ttcards,
        contentfindercondition,
        contentfindercondition_trans,
        contentfinderconditiontransient,
        instancecontent,
        contentmembertype,
        classjob,
        items
    )
except Exception as e:
    print_color_red(e)
    from constants import LANGUAGES
    from helper import seperate_data_into_array, getImage, EntryType
    from fileimports import (
        territorytype_trans,
        territorytype,
        patchversions,
        mounts,
        minions,
        orchestrions,
        orchestrionpath,
        ttcards,
        contentfindercondition,
        contentfindercondition_trans,
        contentfinderconditiontransient,
        instancecontent,
        contentmembertype,
        classjob,
        items
    )

import logging


logger: logging.Logger = logging.getLogger()

def getClassJobDict() -> dict[Any, Any]:
    final_array: dict[Any, Any] = {}
    for _, value in classjob.items():
        if int(value['JobIndex']) != 0:
            final_array[value['Abbreviation']] = {
                "Waffe": [],
                "Schild": [],
                "Kopf": [],
                "Rumpf": [],
                "Hände": [],
                "Beine": [],
                "Füße": [],
                "Ohrring": [],
                "Halskette": [],
                "Armreif": [],
                "Ring": [],
                "Verschiedenes": []
            }
    return final_array
class_job_item_array: dict[Any, Any] = getClassJobDict()


def get_territorytype_from_mapid(entry) -> tuple[str, str]:
    for key, tt_type in territorytype_trans.items():
        if tt_type["TerritoryType"].lower() == entry["mapid"].lower():
            return tt_type, territorytype[key]['Bg']
    print_color_red(f"Could not find territorytype for {entry['mapid']} ({entry['title']})")
    return "", ""


def replaceSlug(text: Any) -> str:
    text = str(text).replace("_", "-").replace(".", "-").replace(",", "").replace("'", "")
    text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae")
    text = text.replace("Ö", "Oe").replace("Ü", "Ue").replace("ß", "ss")
    return text


def myCapitalize(string: str) -> str:
    if string == "":
        return ""
    return string[:1].upper() + string[1:]


def writeTags(header_data: str, entry: EntryType, tt_type_name: str|dict[str, str]) -> str:
    # write tags per expansion
    if entry["categories"] == "arr":
        header_data += "  - term: \"A Realm Reborn\"\n"
        header_data += "  - term: \"ARR\"\n"
    elif entry["categories"] == "hw":
        header_data += "  - term: \"Heavensward\"\n"
        header_data += "  - term: \"HW\"\n"
    elif entry["categories"] == "sb":
        header_data += "  - term: \"Stormblood\"\n"
        header_data += "  - term: \"SB\"\n"
    elif entry["categories"] == "shb":
        header_data += "  - term: \"Shadowbringers\"\n"
        header_data += "  - term: \"ShB\"\n"
    elif entry["categories"] == "ew":
        header_data += "  - term: \"Endwalker\"\n"
        header_data += "  - term: \"EW\"\n"
    else:
        pass

    if not tt_type_name == "":
        for lang in LANGUAGES:
            header_data += "  - term: \"" + tt_type_name["Name_" + lang] + "\"\n"

    for lang in LANGUAGES:
        header_data += "  - term: \"" + myCapitalize(entry[f"titles"][lang]) + "\"\n"

    # write rest of the tags
    header_data += "  - term: \"" + entry["difficulty"] + "\"\n"
    header_data += "  - term: \"" + entry["patchNumber"] + "!\"\n"
    if entry["patchNumber"].endswith("0"):
        header_data += "  - term: \"" + entry["patchNumber"][:-1] + "!\"\n"
    #entry["patchNumber"] = [entry["patchNumber"] if len(entry["patchNumber"].split(".")[1]) == 2 else str(entry["patchNumber"]) + "0" ][0]
    header_data += "  - term: \"" + entry["patchName"] + "\"\n"

    for lang in LANGUAGES:
        if not entry['quest'].get(lang, "") == "":
            header_data += "  - term: \"" + entry['quest'][lang] + "\"\n"

    found, data = checkVariable(entry, "mount")
    if found:
        header_data += "  - term: \"mounts\"\n"
        header_data += "  - term: \"Reittier\"\n"
    found, data = checkVariable(entry, "minion")
    if found:
        header_data += "  - term: \"minions\"\n"
        header_data += "  - term: \"Begleiter\"\n"
    found, data = checkVariable(entry, "tt_card")
    if found:
        header_data += "  - term: \"tt_cards\"\n"
        header_data += "  - term: \"Triple Triad Karte\"\n"
    found, data = checkVariable(entry, "gearset_loot")
    if found:
        for d in data:
            header_data += "  - term: \"" + d + "\"\n"
    found, data = checkVariable(entry, "orchestrion")
    if found:
        header_data += "  - term: \"orchestrion\"\n"
        header_data += "  - term: \"Notenrolle\"\n"
    found, data = checkVariable(entry, "orchestrion_material")
    if found:
        header_data += "  - term: \"orchestrion_material\"\n"
    if entry["instanceType"] == "trial":
        header_data += "  - term: \"Prüfung\"\n"
        header_data += "  - term: \"Trial\"\n"
        header_data += "  - term: \"Primae\"\n"
        header_data += "  - term: \"Primal\"\n"
    header_data += "  - term: \"" + entry["instanceType"] + "\"\n"

    found_roulette = False
    if entry.get("allianceraid", None) == "True":
        header_data += "  - term: \"allianceraid\"\n"
        found_roulette = True
    if entry.get("frontier", None) == "True":
        header_data += "  - term: \"frontier\"\n"
        found_roulette = True
    if entry.get("expert", None) == "True":
        header_data += "  - term: \"expert\"\n"
        found_roulette = True
    if entry.get("guildhest", None) == "True":
        header_data += "  - term: \"guildhest\"\n"
        found_roulette = True
    if entry.get("highlevelroulette", None) == "True":
        header_data += "  - term: \"highlevelroulette\"\n"
        found_roulette = True
    if entry.get("levelcaproulette", None) == "True":
        header_data += "  - term: \"levelcaproulette\"\n"
        found_roulette = True
    if entry.get("leveling", None) == "True":
        header_data += "  - term: \"leveling\"\n"
        found_roulette = True
    if entry.get("main", None) == "True":
        header_data += "  - term: \"main\"\n"
        found_roulette = True
    if entry.get("mentor", None) == "True":
        header_data += "  - term: \"mentor\"\n"
        found_roulette = True
    if entry.get("normalraid", None) == "True":
        header_data += "  - term: \"normalraid\"\n"
        found_roulette = True
    if entry.get("trial", None) == "True":
        header_data += "  - term: \"trial\"\n"
        found_roulette = True
    if found_roulette:
        header_data += "  - term: \"Zufallsinhalt\"\n"
        header_data += "  - term: \"roulette\"\n"

    if not entry["bosse"] == ['']:
        for b in entry["bosse"]:
            if b != "Unknown_":
                header_data += "  - term: \"" + b + "\"\n"
    if not entry["tags"] == ['']:
        for t in entry["tags"]:
            if t != "Unknown_":
                header_data += "  - term: \"" + t + "\"\n"
    return header_data


def addEntries(header_data: str, data, get_data_function, content_translations, cat) -> str:
    if data:
        _id, array = get_data_function(data)
        if _id:
            header_data += f'  - name: "{array.get("Singular_en", array.get("Name_en", ""))}"\n'
            for lang in LANGUAGES:
                #header_data += f'      {lang}: "' + array.get(f"Singular_{lang}", array.get(f"Name_{lang}", "")) + '"\n'
                content_translations[lang][f'{cat}_{array.get("Singular_en", array.get("Name_en", ""))}'] = array.get(f"Singular_{lang}", array.get(f"Name_{lang}", ""))
        else:
            header_data += '  - name: "' + data + '"\n'
        if _id:
            header_data += '    id: "' + _id + '"\n'
    return header_data


def get_order_id(entry) -> str:
    patch = "0000"
    plvl = "00"
    sortid = "0000"
    if "." in entry["patchNumber"]:
        t_minor = 0
        major, minor = entry["patchNumber"].split(".")
        if str(minor).endswith("a") or str(minor).endswith("b"):
            t_minor = int(minor[:-1])
            t_minor = t_minor * 10 if t_minor < 10 else t_minor
            t_minor = t_minor * 10 if t_minor < 100 else t_minor
            if str(minor).endswith("a"):
                minor = t_minor + 1
            elif str(minor).endswith("b"):
                minor = t_minor + 2
        else:
            minor = f"{minor}0" if len(minor) < 2 else minor
            minor = f"{minor}0" if len(minor) < 3 else minor
        patch = f"{major}{minor}"
    if entry["plvl"]:
        plvl = int(entry["plvl"]) * 10 if len(entry["plvl"]) < 2 else entry["plvl"]
    if entry["sortid"]:
        sortid = f"0{entry['sortid']}" if len(entry["sortid"]) < 1 else entry["sortid"]
        sortid = f"0{sortid}" if len(sortid) < 2 else sortid
        sortid = f"0{sortid}" if len(sortid) < 3 else sortid
        sortid = f"0{sortid}" if len(sortid) < 4 else sortid
    return f"{patch}{plvl}{sortid}"


def checkVariable(element, name):
    e = element[name]
    if e is None or e == "" or e == [] or e == "[]" or e == "###":
        return False, None
    if isinstance(e, list):
        return True, e
    if e.startswith("[") and e.endswith("]") and len(e) > 2:
        return True, seperate_data_into_array(name, element)
    if e:
        return True, [e]
    return False, None


def get_video_url(url):
    if url.startswith("https"):
        return url
    return "https://www.youtube.com/watch?v={}".format(url)


def get_lvl_data(entry: EntryType):
    global contentfindercondition
    lvl_data = ""
    _id = entry['CFC_ID']
    if _id.endswith(".0"):
        _id = _id[:-2]
    cfc_value = contentfindercondition.get(_id, None)
    if cfc_value:
        lvl_data += 'plvl: ' + cfc_value["ClassJobLevel"]["Required"] + '\n'
        lvl_data += 'plvl_sync: ' + cfc_value["ClassJobLevel"]["Sync"] + '\n'
        lvl_data += 'ilvl: ' + cfc_value["ItemLevel"]["Required"] + '\n'
        lvl_data += 'ilvl_sync: ' + cfc_value["ItemLevel"]["Sync"] + '\n'
    return lvl_data

cat_to_instance_image: dict[str, str] = {
    "dungeon":      "/061000/061801_hr1.png",
    "trial":        "/061000/061804_hr1.png",
    "raid":         "/061000/061802_hr1.png",
    "ultimate":     "/061000/061832_hr1.png",
    "allianzraid":  "/061000/061844_hr1.png",
    "gewölbesuche": "/061000/061846_hr1.png",
    "feldexkursion":"/061000/061837_hr1.png",
    "bluemage":     "/061000/061836_hr1.png",
    "potd":         "/061000/061824_hr1.png",
    "guildhest":    "/061000/061803_hr1.png",
    "treasure":     "/061000/061808_hr1.png",
    "pvp":          "/061000/061806_hr1.png",
    "training":     "/061000/061823_hr1.png",
    "overworld":    "/052000/052474_hr1.png"
}
def get_cat_image(instancetype, cfc_key):
    global cat_to_instance_image
    global contentfindercondition
    # this case handels latest primals and savage content as they are always classified as hardcore content
    if contentfindercondition.get(cfc_key, {}).get("HighEndDuty", None) == "True":
        return cat_to_instance_image['ultimate']
    return cat_to_instance_image.get(instancetype, None)


def getMapImages(mapid: str, contentname: str) -> str:
    result: str = ""
    path: str = "P:\\extras\\images\\ui\\map\\"
    files: list[str] = glob(path + mapid[:3] + "\\*.png")
    found_valid_maps: list[str] = []
    for file in files:
        if "_ow_" in file:
            continue
        if contentname+".png" in file and not "_event" in file and mapid in file:
            found_valid_maps.append(file)
            if "_event" in file:
                print_color_red(file)
    if found_valid_maps:
        found_valid_maps = [ x.replace(path, "").replace("\\", "/") for x in found_valid_maps ]
        result += "mapimage:\n"
        for image in found_valid_maps:
            result += f'    - image: "{image}"\n'
    return result

def rewrite_content_even_if_exists(entry: EntryType, old_wip, cfc_key, content_translations):
    global contentfindercondition
    global instancecontent
    header_data = ""
    tt_type_name, tt_bg_entry = get_territorytype_from_mapid(entry)
    if old_wip in ["True", "False"]:
        header_data += 'wip: "' + str(old_wip).title() + '"\n'
    else:
        header_data += 'wip: "True"\n'
    # header_data += 'title: "' + entry["title"] + '"\n'
    #! DO NOT TOUCH TITLE HERE AS IT IS NEEDED FOR TAGS
    header_data += 'title:\n'
    for lang in LANGUAGES:
        tmp = entry["titles"][lang]
        tmp = tmp.replace(f' ({entry["difficulty"].lower()})', "")
        tmp = tmp.replace(f' ({entry["difficulty"].title()})', "")
        tmp = tmp.replace('Traumprüfung - ', "")
        tmp = myCapitalize(tmp)
        header_data += f'  {lang}: "' + tmp + '"\n'
    header_data += 'layout: guide_post\n'
    header_data += 'page_type: guide\n'
    header_data += f'excel_line: \"{entry["line_index"]}\"\n'
    header_data += 'categories: "' + entry["categories"] + '"\n'
    header_data += 'patchNumber: "' + entry["patchNumber"].replace("'", "") + '"\n'
    entry["patchNumber"] = [entry["patchNumber"] if len(entry["patchNumber"].split(".")[1]) == 2 else str(entry["patchNumber"]) + "0" ][0]
    if patchversions.get(entry["patchNumber"], None):
        header_data += 'patchLink: "' + patchversions[entry["patchNumber"]]['link_to_patch'] + '"\n'
    header_data += 'difficulty: "' + entry["difficulty"] + '"\n'
    header_data += 'instanceType: "' + entry["instanceType"] + '"\n'
    header_data += 'date: "' + entry["date"] + '"\n'
    header_data += 'slug: "' + replaceSlug(entry["slug"]) + '"\n'
    if entry["prev_content"]:
        header_data += 'previous_slug: "' + replaceSlug(entry["prev_content"]) + '"\n'
    if entry["next_content"]:
        header_data += 'next_slug: "' + replaceSlug(entry["next_content"]) + '"\n'
    if entry["image"]:
        header_data += f'image: "{getImage(entry["image"])}"\n'
        # header_data += '  - url: \"/' +  + '\n'
    cat_image = get_cat_image(entry["instanceType"], cfc_key)
    if cat_image:
        header_data += f'jobicon: "{getImage(cat_image)}"\n'
    header_data += 'terms:\n'
    header_data = writeTags(header_data, entry, tt_type_name)
    header_data += 'patchName: "' + entry["patchName"] + '"\n'
    if entry.get("mapid", None):
        header_data += 'mapid: "' + entry["mapid"] + '"\n'
    if not tt_bg_entry == "":
        header_data += 'mappath: "' + tt_bg_entry + '"\n'
    if not tt_type_name == "":
        # header_data += 'contentname: "' + tt_type_name["Name_de"] + '"\n'
        header_data += f'contentname: "{tt_type_name["Name_en"]}"\n'
        for lang in LANGUAGES:
            content_translations[lang][f'ContentName_{tt_type_name["Name_en"]}'] = tt_type_name[f"Name_{lang}"]
            # header_data += f'  {lang}: "' + tt_type_name[f"Name_{lang}"] + '"\n'
    if entry.get("mapid", None) and tt_bg_entry:
        header_data += getMapImages(mapid=entry["mapid"], contentname=tt_type_name["Name_de"])
    header_data += 'sortid: ' + entry["sortid"] + '\n'
    header_data += get_lvl_data(entry)
    # quests
    x = False
    for lang in LANGUAGES:
        if not entry['quest'].get(lang, "") == "":
            if not x:
                x = True
                header_data += f'quest: "{entry["quest"]["en"]}"\n'
            content_translations[lang][f'QuestName_{entry["quest"]["en"]}'] = entry['quest'][lang]
    x = False
    for lang in LANGUAGES:
        if not entry['quest_location'].get(lang, "") == "":
            if not x:
                x = True
                header_data += f'quest_location: "{entry["quest_location"]["en"]}"\n'
            content_translations[lang][f'QuestLocation_{entry["quest_location"]["en"]}'] = entry['quest_location'][lang]
    x = False
    for lang in LANGUAGES:
        if not entry['quest_npc'].get(lang, "") == "":
            if not x:
                x = True
                header_data += f'quest_npc: "{entry['quest_npc']["en"]}"\n'
            content_translations[lang][f'QuestNPC_{entry["quest_npc"]["en"]}'] = entry['quest_npc'][lang]

    # header_data += 'order: ' + get_order_id(entry) + '\n'
    header_data += 'order: ' + entry["sortid"] + '\n'

    # TODO add funcion for Orchestrio Material
    category_names = {
        'mount': getMountIDByName,
        'minion': getMinionIDByName,
        'gearset_loot': "gsetname",
        'tt_card': getTTCardIDByName,
        'orchestrion': getOrchestrionIDByName,
        'orchestrion_material': getOrchestrionMaterialIDByName,
        'mtqvid': "url",
        'mrhvid': "url",
        'hector': "url"
    }
    for cat, fun in category_names.items():
        found, data = checkVariable(entry, cat)
        if not found:
            continue
        if isinstance(fun, str):
            header_data += f'{cat}:\n'
            for i, d in enumerate(data):
                if fun == "url":
                    header_data += f'  - {fun}: "' + get_video_url(d.strip()) + '"\n'
                else:
                    header_data += f'  - {fun}: "' + d.strip() + '"\n'
        elif fun:
            header_data += f'{cat}:\n'
            for i, d in enumerate(data):
                header_data = addEntries(header_data, d.strip(), fun, content_translations, cat)
        else:
            pass

    # rouletts
    if entry.get("expert", None):
        # first check is to see if elements are even there, this one is for the actual filter
        if eval(entry["allianceraid"]) or eval(entry["frontier"]) or eval(entry["expert"]) or eval(entry["guildhest"]) or eval(entry["highlevelroulette"]) or eval(entry["levelcaproulette"]) or eval(entry["leveling"]) or eval(entry["main"]) or eval(entry["mentor"]) or eval(entry["normalraid"]) or eval(entry["trial"]):
            header_data += 'rouletts:\n'
            if eval(entry["allianceraid"]):
                header_data += '    allianceraid: ' + entry["allianceraid"] + "\n"
            if eval(entry["frontier"]):
                header_data += '    frontier: ' + entry["frontier"] + "\n"
            if eval(entry["expert"]):
                header_data += '    expert: ' + entry["expert"] + "\n"
            if eval(entry["guildhest"]):
                header_data += '    guildhest: ' + entry["guildhest"] + "\n"
            if eval(entry["highlevelroulette"]):
                header_data += '    highlevelroulette: ' + entry["highlevelroulette"] + "\n"
            if eval(entry["levelcaproulette"]):
                header_data += '    levelcaproulette: ' + entry["levelcaproulette"] + "\n"
            if eval(entry["leveling"]):
                header_data += '    leveling: ' + entry["leveling"] + "\n"
            if eval(entry["main"]):
                header_data += '    main: ' + entry["main"] + "\n"
            if eval(entry["mentor"]):
                header_data += '    mentor: ' + entry["mentor"] + "\n"
            if eval(entry["normalraid"]):
                header_data += '    normalraid: ' + entry["normalraid"] + "\n"
            if eval(entry["trial"]):
                header_data += '    trial: ' + entry["trial"] + "\n"
    # links:
    # TODO Fix big if check
    if checkVariable(entry, "teamcraftlink") or checkVariable(entry, "garlandtoolslink") or checkVariable(entry, "gamerescapelink"):
        header_data += 'links:\n'
        for x in ["teamcraftlink", "garlandtoolslink", "gamerescapelink"]:
            found, data = checkVariable(entry, x)
            if found:
                header_data += f'    {x}: "' + data[0] + '"\n'
    # get bgmusic
    instancecontent_id = contentfindercondition.get(cfc_key, {}).get('Content', "").replace("InstanceContent#", "")
    if instancecontent_id not in  ["0", "", None]:
        instancecontent_entry = instancecontent[instancecontent_id]
        bgm = instancecontent_entry["BGM"].replace(".scd", ".ogg")
        if not bgm == "":
            header_data += f'bgmusic: "{bgm}"\n'
    return header_data, entry


def getItemsList(gs_items):
    final_array = deepcopy(class_job_item_array)
    item_list = ""
    for gs_item in gs_items:
        #print(items[gs_item])
        found = False
        for _class, class_data in final_array.items():
            if _class in items[gs_item]['ClassJobCategory']:
                found = True
                cat = "Waffe" if "waffe" in items[gs_item]['ItemUICategory'].lower() else items[gs_item]['ItemUICategory']
                cat = "Waffe" if cat == "Grimoire" else cat

                if items[gs_item]['Name'] not in final_array[_class][cat]:
                    final_array[_class][cat].append(items[gs_item]['Name'])
        if not found:
            print(items[gs_item])
        item_list += f'  - item: "{items[gs_item]["Name"]}"\n'
    print(final_array)
    return item_list


def addContentZoneIdToHeader(contentzoneid, entry, content_translations):
    global contentfindercondition
    global contentfindercondition_trans
    cmt = None
    header_data = ""
    working_key = ""
    if not contentzoneid == "":
        header_data += 'contentzoneids:\n'
        for zone in contentzoneid:
            header_data += '  - id: ' + zone + '\n'
    for key, value in contentfindercondition.items():
        if contentfindercondition_trans[key]['Name_de'] == entry['titles']['de']:
            working_key = key
            cmt = value['ContentMemberType']
            if "InstanceContent" not in value['Content']:
                continue
            contentid = value['Content'].replace("InstanceContent#", "")
            if not contentid:
                continue
            working_key = key
            _id = "8003" + str(hex(int(contentid))[2:]).rjust(4, '0').upper()

            if "contentzoneids:" not in header_data:
                header_data += 'contentzoneids:\n'

            if _id not in header_data:
                # if _id not in contentzoneid:
                header_data += '  - id: ' + _id + '\n'
                # add transient on the first valid entry
    if "contentdescription" not in header_data and not working_key == "":
        content_en_desc = contentfinderconditiontransient[working_key]["Description_en"].replace("\n", "<br/>").replace('"', '\\"')
        header_data += f'contentdescription: "{content_en_desc}"\n'
        tmp = entry["title"]
        tmp = tmp.replace(f' ({entry["difficulty"].lower()})', "")
        tmp = tmp.replace(f' ({entry["difficulty"].title()})', "")
        tmp = tmp.replace('Traumprüfung - ', "")
        tmp = myCapitalize(tmp)
        for lang in LANGUAGES:
            content_translations[lang][f'ContentDesc_{tmp}'] = contentfinderconditiontransient[working_key][f"Description_{lang}"].replace("\n", "<br/>").replace('"', '\\"')
            #header_data += f'    {lang}: "' + contentfinderconditiontransient[working_key][f"Description_{lang}"].replace("\n", "<br/>").replace('"', '\\"') + '"\n'

    return header_data, cmt, working_key


def addGroupCollections(cmt, entry):
    global contentmembertype
    header_data = ""
    if entry['instanceType'] == "overworld":
        return header_data
    if entry['instanceType'] == "overworlds":
        return header_data
    skip_lookoup = False
    if not cmt:
        if "Traumprüfung" in entry['title'] or "Dalriada" in entry['title'] or "Castrum Lacus Litore" in entry['title']:
            cmt_entry = 8
            healerp = 2
            tankp = 2
            meleep = 2
            rangep = 2
            skip_lookoup = true
        else:
            print("Could not find GroupCollection for: " + entry['title'])
            return header_data

    if not skip_lookoup:
        wanted_id = cmt.split("#")[1]
        cmt_entry = contentmembertype[f"{wanted_id}"]
        healerp = cmt_entry['HealersPerParty']
        tankp = cmt_entry['TanksPerParty']
        meleep = cmt_entry['MeleesPerParty']
        rangep = cmt_entry['RangedPerParty']

    if int(healerp) + int(tankp) + int(meleep) + int(rangep) > 0:
        header_data += "group:\n"
        if not healerp == "0":
            header_data += f'    healer: "{healerp}"\n'
        if not tankp == "0":
            header_data += f'    tank: "{tankp}"\n'
        if not meleep == "0":
            header_data += f'    melee: "{meleep}"\n'
        if not rangep == "0":
            header_data += f'    range: "{rangep}"\n'
    return header_data


def getMountIDByName(name):
    for _id, mount in mounts.items():
        if mount['Singular_de'] == name:
            return _id, mount
    return None, None


def getMinionIDByName(name):
    for _id, minion in minions.items():
        if minion['Singular_de'] == name:
            return _id, minion
    return None, None


def getTTCardIDByName(name):
    for id, ttcard in ttcards.items():
        if ttcard['Name_de'] == name:
            return id.split(".0")[0], ttcard
    return None, None


def getOrchestrionIDByName(name):
    for _id, orchestrion in orchestrions.items():
        if orchestrion['Name_de'].lower() == name.lower():
            return _id, orchestrion
    return None, None


def getOrchestrionMaterialIDByName(name):
    for _id, orchestrion in orchestrions.items():
        if orchestrion['Name_de'].lower() == name.lower():
            return _id, orchestrion
    return None, None


def getBGMPath(_id: str, name: str) -> str:
    global orchestrionpath
    return orchestrionpath[_id]['File'].replace(".scd", f"-{name}.ogg")


def addMusic(header_data: str, music: list[str], content_translations) -> str:
    header_data += "music:\n"
    for m in music:
        _id, orchestrion = getOrchestrionIDByName(m)
        name = None
        if _id:
            header_data += f'  - name: "{orchestrion.get("Name_en", "")}"\n'
            for lang in LANGUAGES:
                name: str = orchestrion.get(f"Name_{lang}", "")
                if name == "":
                    name = f'{orchestrion.get("Name_de", "")} (no official translation)'
                content_translations[lang][f'music_{orchestrion.get("Name_en", "")}'] = name
            name = orchestrion.get("Name_de", "")
        else:
            if m != "Victory!":
                header_data += f'  - name: {m}\n'
                name = m
                for lang in LANGUAGES:
                    content_translations[lang][f'music_{name}'] = name
        if _id:
            header_data += '    id: "' + _id + '"\n'
            header_data += '    bgm_path: "' + getBGMPath(_id, name) + '"\n'
    return header_data


def addHeader(entry, old_data, music, contentzoneid, content_translations):
    logger.info("test")
    # the order was changed so that we have the cfc_key to retrief the correct icon for the content (latest ex primals and savage raids)
    content_data, cmt, cfc_key = addContentZoneIdToHeader(contentzoneid, entry, content_translations)
    header_data, entry = rewrite_content_even_if_exists(entry, old_data.get('wip', False), cfc_key, content_translations)
    header_data += content_data
    header_data += addGroupCollections(cmt, entry)
    if music:
        header_data = addMusic(header_data, music, content_translations)
    return header_data

if __name__ == "__main__":
    print(LANGUAGES)
