#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
try:
    from python_scripts.constants import *
    from python_scripts.helper import *
except:
    from constants import *
    from helper import *
from ffxiv_aku import *

territorytype = loadDataTheQuickestWay("territorytype_all.json", translate=True)
patchversions = get_any_Versiondata()
mounts = loadDataTheQuickestWay("mount_all.json", translate=True)
exversion = loadDataTheQuickestWay("exversion_all.json", translate=True)
minions = loadDataTheQuickestWay("companion_all.json", translate=True)
orchestrions = loadDataTheQuickestWay("orchestrion_all.json", translate=True)
ttcards = loadDataTheQuickestWay("tripletriadcard_all.json", translate=True)
contentfinderconditionX = loadDataTheQuickestWay("ContentFinderCondition.de.json")
contentmembertype = loadDataTheQuickestWay("ContentMemberType.json")


def get_territorytype_from_mapid(entry):
    for _, tt_type in territorytype.items():
        if tt_type["TerritoryType"].lower() == entry["mapid"].lower():
            return tt_type
    print_color_red(f"Could not find territorytype for {entry['mapid']} ({entry['title']})")
    return ""


def replaceSlug(text):
    return str(text).replace("_", "-").replace(".", "-").replace(",", "").replace("'", "").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue").replace("ß", "ss")


def writeTags(header_data, entry, tt_type_name):
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
        header_data += "  - term: \"" + entry[f"title_{lang}"] + "\"\n"

    # write rest of the tags
    header_data += "  - term: \"" + entry["difficulty"] + "\"\n"
    header_data += "  - term: \"" + entry["patchNumber"] + "!\"\n"
    header_data += "  - term: \"" + entry["patchName"] + "\"\n"

    for lang in LANGUAGES:
        if not entry.get(f"quest_{lang}", "") == "":
            header_data += "  - term: \"" + entry[f"quest_{lang}"] + "\"\n"
    if checkVariable(entry, "mount1") or checkVariable(entry, "mount2"):
        header_data += "  - term: \"mounts\"\n"
        header_data += "  - term: \"Reittier\"\n"
    if checkVariable(entry, "minion1") or checkVariable(entry, "minion2") or checkVariable(entry, "minion3"):
        header_data += "  - term: \"minions\"\n"
        header_data += "  - term: \"Begleiter\"\n"
    if checkVariable(entry, "tt_card1") or checkVariable(entry, "tt_card2"):
        header_data += "  - term: \"tt_cards\"\n"
        header_data += "  - term: \"Triple Triad Karte\"\n"
    if checkVariable(entry, "gearset_loot"):
        for gset in entry["gearset_loot"].split(","):
            header_data += "  - term: \"" + gset + "\"\n"
    if checkVariable(entry, "orchestrion") or checkVariable(entry, "orchestrion2") or checkVariable(entry, "orchestrion3") or checkVariable(entry, "orchestrion4") or checkVariable(entry, "orchestrion5"):
        header_data += "  - term: \"orchestrion\"\n"
        header_data += "  - term: \"Notenrolle\"\n"
    if checkVariable(entry, "orchestrion_material1") or checkVariable(entry, "orchestrion_material2") or checkVariable(entry, "orchestrion_material3"):
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
    if entry.get("level50_60_70", None) == "True":
        header_data += "  - term: \"level50_60_70\"\n"
        found_roulette = True
    if entry.get("level80", None) == "True":
        header_data += "  - term: \"level80\"\n"
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


def addEntries(header_data, entry, field, get_data_function):
    if checkVariable(entry, field):
        _id, array = get_data_function(entry[field])
        if _id:
            header_data += '  - name:\n'
            for lang in LANGUAGES:
                header_data += f'      {lang}: "' + array.get(f"Singular_{lang}", array.get(f"Name_{lang}", "")) + '"\n'
        else:
            header_data += '  - name: "' + entry[field] + '"\n'
        if _id:
            header_data += '    id: "' + _id + '"\n'
    return header_data


def get_order_id(entry):
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
    if element[name] and not element[name] == "###":
        return True
    return False


def get_video_url(url):
    if url.startswith("https"):
        return url
    return "https://www.youtube.com/watch?v={}".format(url)


def rewrite_content_even_if_exists(entry, old_wip):
    header_data = ""
    tt_type_name = get_territorytype_from_mapid(entry)
    if old_wip in ["True", "False"]:
        header_data += 'wip: "' + str(old_wip).title() + '"\n'
    else:
        header_data += 'wip: "True"\n'
    #header_data += 'title: "' + entry["title"] + '"\n'
    header_data += 'title:\n'
    for lang in LANGUAGES:
        tmp = entry[f"title_{lang}"].replace(f' ({entry["difficulty"].lower()})', "")
        tmp = tmp.replace(f' ({entry["difficulty"].title()})', "")
        tmp = tmp.replace(f'Traumprüfung - ', "")
        header_data += f'  {lang}: "' + tmp + '"\n'
    header_data += 'layout: guide_post\n'
    header_data += 'page_type: guide\n'
    header_data += f'excel_line: \"{entry["line_index"]}\"\n'
    header_data += 'categories: "' + entry["categories"] + '"\n'
    header_data += 'patchNumber: "' + entry["patchNumber"].replace("'", "") + '"\n'
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
        header_data += 'image:\n'
        header_data += '  - url: \"/' + getImage(entry["image"]) + '\n'
    header_data += 'terms:\n'
    header_data = writeTags(header_data, entry, tt_type_name)
    header_data += 'patchName: "' + entry["patchName"] + '"\n'
    if entry.get("mapid", None):
        header_data += 'mapid: "' + entry["mapid"] + '"\n'
    if not tt_type_name == "":
        #header_data += 'contentname: "' + tt_type_name["Name_de"] + '"\n'
        header_data += 'contentname:\n'
        for lang in LANGUAGES:
            header_data += f'  {lang}: "' + tt_type_name[f"Name_{lang}"] + '"\n'
    header_data += 'sortid: ' + entry["sortid"] + '\n'
    header_data += 'plvl: ' + entry["plvl"] + '\n'
    header_data += 'plvl_sync: ' + entry["plvl_sync"] + '\n'
    header_data += 'ilvl: ' + entry["ilvl"] + '\n'
    header_data += 'ilvl_sync: ' + entry["ilvl_sync"] + '\n'
    # quests
    x = False
    for lang in LANGUAGES:
        if not entry.get(f"quest_{lang}", "") == "":
            if not x:
                x = True
                header_data += 'quest:\n'
            header_data += f'  {lang}: "' + entry[f"quest_{lang}"] + '"\n'
    x = False
    for lang in LANGUAGES:
        if not entry.get(f"quest_location_{lang}", "") == "":
            if not x:
                x = True
                header_data += 'quest_location:\n'
            header_data += f'  {lang}: "' + entry[f"quest_location_{lang}"] + '"\n'
    x = False
    for lang in LANGUAGES:
        if not entry.get(f"quest_npc_{lang}", "") == "":
            if not x:
                x = True
                header_data += 'quest_npc:\n'
            header_data += f'  {lang}: "' + entry[f"quest_npc_{lang}"] + '"\n'
    header_data += 'order: ' + get_order_id(entry) + '\n'
    # mounts
    if checkVariable(entry, "mount1") or checkVariable(entry, "mount2"):
        header_data += 'mount:\n'
        header_data = addEntries(header_data, entry, "mount1", getMountIDByName)
        header_data = addEntries(header_data, entry, "mount2", getMountIDByName)
    # minions
    if checkVariable(entry, "minion1") or checkVariable(entry, "minion2") or checkVariable(entry, "minion3"):
        header_data += 'minion:\n'
        header_data = addEntries(header_data, entry, "minion1", getMinionIDByName)
        header_data = addEntries(header_data, entry, "minion2", getMinionIDByName)
        header_data = addEntries(header_data, entry, "minion3", getMinionIDByName)
    # gearset_loot
    if checkVariable(entry, "gearset_loot"):
        header_data += 'gearset_loot:\n'
        for gset in entry["gearset_loot"] .split(","):
            header_data += '  - gsetname: "' + gset + '"\n'
    # tt_cards
    if checkVariable(entry, "tt_card1") or checkVariable(entry, "tt_card2"):
        header_data += 'tt_card:\n'
        header_data = addEntries(header_data, entry, "tt_card1", getTTCardIDByName)
        header_data = addEntries(header_data, entry, "tt_card2", getTTCardIDByName)
    # orchestrion
    if checkVariable(entry, "orchestrion") or checkVariable(entry, "orchestrion2") or checkVariable(entry, "orchestrion3") or checkVariable(entry, "orchestrion4") or checkVariable(entry, "orchestrion5"):
        header_data += 'orchestrion:\n'
        header_data = addEntries(header_data, entry, "orchestrion", getOrchestrionIDByName)
        header_data = addEntries(header_data, entry, "orchestrion2", getOrchestrionIDByName)
        header_data = addEntries(header_data, entry, "orchestrion3", getOrchestrionIDByName)
        header_data = addEntries(header_data, entry, "orchestrion4", getOrchestrionIDByName)
        header_data = addEntries(header_data, entry, "orchestrion5", getOrchestrionIDByName)
    # orchestrion material
    if checkVariable(entry, "orchestrion_material1") or checkVariable(entry, "orchestrion_material2") or checkVariable(entry, "orchestrion_material3"):
        header_data += 'orchestrion_material:\n'
        if checkVariable(entry, "orchestrion_material1"):
            header_data += '  - name: "' + entry["orchestrion_material1"] + '"\n'
        if checkVariable(entry, "orchestrion_material2"):
            header_data += '  - name: "' + entry["orchestrion_material2"] + '"\n'
        if checkVariable(entry, "orchestrion_material3"):
            header_data += '  - name: "' + entry["orchestrion_material3"] + '"\n'
    # rouletts
    if entry.get("expert", None):
        if entry["allianceraid"] or entry["frontier"] or entry["expert"] or entry["guildhest"] or entry["level50_60_70"] or entry["level80"] or entry["leveling"] or entry["main"] or entry["mentor"] or entry["normalraid"] or entry["trial"]:
            header_data += 'rouletts:\n'
        if entry["allianceraid"]:
            header_data += '    allianceraid: ' + entry["allianceraid"] + "\n"
        if entry["frontier"]:
            header_data += '    frontier: ' + entry["frontier"] + "\n"
        if entry["expert"]:
            header_data += '    expert: ' + entry["expert"] + "\n"
        if entry["guildhest"]:
            header_data += '    guildhest: ' + entry["guildhest"] + "\n"
        if entry["level50_60_70"]:
            header_data += '    level50_60_70: ' + entry["level50_60_70"] + "\n"
        if entry["level80"]:
            header_data += '    level80: ' + entry["level80"] + "\n"
        if entry["leveling"]:
            header_data += '    leveling: ' + entry["leveling"] + "\n"
        if entry["main"]:
            header_data += '    main: ' + entry["main"] + "\n"
        if entry["mentor"]:
            header_data += '    mentor: ' + entry["mentor"] + "\n"
        if entry["normalraid"]:
            header_data += '    normalraid: ' + entry["normalraid"] + "\n"
        if entry["trial"]:
            header_data += '    trial: ' + entry["trial"] + "\n"
    # links:
    if checkVariable(entry, "teamcraftlink") or checkVariable(entry, "garlandtoolslink") or checkVariable(entry, "gamerescapelink"):
        header_data += 'links:\n'
        if checkVariable(entry, "teamcraftlink"):
            header_data += f'    teamcraftlink: "' + entry["teamcraftlink"] + '"\n'
        if checkVariable(entry, "garlandtoolslink"):
            header_data += f'    garlandtoolslink: "' + entry["garlandtoolslink"] + '"\n'
        if checkVariable(entry, "gamerescapelink"):
            header_data += f'    gamerescapelink: "' + entry["gamerescapelink"] + '"\n'
    # videos
    if checkVariable(entry, "mtqvid1"):
        header_data += 'mtq_vid1: "' + get_video_url(entry["mtqvid1"]) + '"\n'
    if checkVariable(entry, "mtqvid2"):
        header_data += 'mtq_vid2: "' + get_video_url(entry["mtqvid2"]) + '"\n'
    if checkVariable(entry, "mrhvid1"):
        header_data += 'mrh_vid1: "' + get_video_url(entry["mrhvid1"]) + '"\n'
    if checkVariable(entry, "mrhvid2"):
        header_data += 'mrh_vid2: "' + get_video_url(entry["mrhvid2"]) + '"\n'
    return header_data, entry


def addContentZoneIdToHeader(header_data, contentzoneid, entry):
    global contentfinderconditionX
    cmt = None
    if not contentzoneid == "":
        header_data += 'contentzoneids:\n'
        for zone in contentzoneid:
            header_data += '  - id: ' + zone + '\n'
    for key, value in contentfinderconditionX.items():
        if value['Name'] == entry['title_de']:
            cmt = value['ContentMemberType']
            if not "InstanceContent" in value['Content']:
                continue
            contentid = value['Content'].replace("InstanceContent#", "")
            if not contentid:
                continue
            _id = "8003" + str(hex(int(contentid))[2:]).rjust(4, '0').upper()
            if "contentzoneids:" not in header_data:
                header_data += 'contentzoneids:\n'

            if _id not in header_data:
                # if _id not in contentzoneid:
                header_data += '  - id: ' + _id + '\n'
    return header_data, cmt


def addGroupCollections(cmt, entry):
    global contentmembertype
    header_data = ""
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


def addMusic(header_data, music):
    header_data += "music:\n"
    for m in music:
        _id, orchestrion = getOrchestrionIDByName(m)
        if _id:
            header_data += '  - name:\n'
            for lang in LANGUAGES:
                header_data += f'      {lang}: "' + orchestrion.get(f"Name_{lang}", "") + '"\n'
        else:
            header_data += '  - name:\n'
            header_data += '      de: "' + m + '"\n'
        if _id:
            header_data += '    id: "' + _id + '"\n'
    return header_data


def addHeader(entry, old_data, music, contentzoneid):
    header_data, entry = rewrite_content_even_if_exists(entry, old_data.get('wip', False))
    header_data, cmt = addContentZoneIdToHeader(header_data, contentzoneid, entry)
    header_data += addGroupCollections(cmt, entry)
    if music:
        header_data = addMusic(header_data, music)
    return header_data

if __name__ == "__main__":
    print(LANGUAGES)
