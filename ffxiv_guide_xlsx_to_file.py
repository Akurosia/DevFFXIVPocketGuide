#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import os
import sys
import re
import errno
import json
import urllib.request
import openpyxl
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color_green(text, end="\n"):
    print(f"{bcolors.OKGREEN}{text}{bcolors.ENDC}", end=end)
def print_color_yellow(text, end="\n"):
    print(f"{bcolors.WARNING}{text}{bcolors.ENDC}", end=end)
def print_color_red(text, end="\n"):
    print(f"{bcolors.FAIL}{text}{bcolors.ENDC}", end=end)
def print_color_blue(text, end="\n"):
    print(f"{bcolors.OKBLUE}{text}{bcolors.ENDC}", end=end)

def get_Logdata(_filename, _type, data):
    if not data == {}:
        return data
    try:
        if _type == "local":
            with open(_filename, encoding="utf8") as fi:
                _logdata = json.load(fi)
                return _logdata
        elif _type == "web":
            with urllib.request.urlopen(_filename) as fi:
                _logdata = json.load(fi)
                return _logdata
    except Exception as e:
        print(e)
        return {}
    return {}


def get_any_Logdata():
    data = {}
    if os.name == 'nt':
        data = get_Logdata(r"\\192.168.2.4\Root\var\www\ffxiv\extras\FFlogs\logdata_de.json", "local", data)
        data = get_Logdata(r"V:\ffxiv\extras\FFlogs\logdata_de.json", "local", data)
    else:
        data = get_Logdata("/var/www/ffxiv/extras/FFlogs/logdata_de.json", "local", data)
    data = get_Logdata("https://ffxiv.akurosia.de/extras/FFlogs/logdata_de.json", "web", data)
    if data == {}:
        raise Exception("No Data found")
    return data


def loadDataTheQuickestWay(_filename):
    try:
        base = "\\\\192.168.2.4\\Root\\var\\www\\ffxiv\\extras\\json\\exd-all\\latest\\"
        with open(base + _filename, encoding="utf8") as fi:
            return json.load(fi)
    except:
        try:
            base = "V:\\ffxiv\\extras\\json\\exd-all\\latest"
            with open(base + _filename, encoding="utf8") as fi:
                return json.load(fi)
        except:
            base = "https://ffxiv.akurosia.de/py/translate/exd-all/latest/"
            with urllib.request.urlopen(base + _filename) as f:
                return json.load(f)


logdata = get_any_Logdata()
logdata_lower = dict((k.lower(),v) for k,v in logdata.items())
action = loadDataTheQuickestWay("action_all.json")
territorytype = loadDataTheQuickestWay("territorytype_all.json")
contentfindercondition = loadDataTheQuickestWay("contentfindercondition_all.json")
placename = loadDataTheQuickestWay("placename_all.json")
bnpcname = loadDataTheQuickestWay("bnpcname_all.json")
eobjname = loadDataTheQuickestWay("eobjname_all.json")
enpcresident = loadDataTheQuickestWay("enpcresident_all.json")


def checkVariable(element, name):
    if element[name] and not element[name] == "###":
        return True
    return False


def getContentName(name, lang="en", difficulty=None, instanceType=None):
    name = uglyContentNameFix(name, instanceType, difficulty)
    try:
        for key, content in contentfindercondition.items():
            if "memoria" in content["Name_de"].lower().strip() and "memoria" in name.lower().strip():
                return content[f"Name_{lang}"]
            if content["Name_de"].lower().strip() == name.lower().strip():
                return content[f"Name_{lang}"]
        for key, place in placename.items():
            if place["Name_de"].lower().strip() == name.lower().strip():
                return place[f"Name_{lang}"]
    except KeyError:
        pass
    print_color_red("Could not translate: " + name)
    return ""


def getBnpcName(name, lang="en"):
    name = name.lower()
    aname = ""
    # take care of all the article cases
    name_match = re.search("^(der|die|das) ", name)
    if name_match:
        aname = name.replace("der ", r"(\[t\]|(der|die|das)) ").replace("die ", r"(\[t\]|(der|die|das)) ").replace("das ", r"(\[t\]|(der|die|das)) ")

    name_match = re.search(" (der|die|das)", name)
    if name_match:
        aname = name.replace(" der ", r" (\[t\]|(der|die|das)) ").replace(" die ", r" (\[t\]|(der|die|das)) ").replace(" das ", r" (\[t\]|(der|die|das)) ")

    if aname == "":
        aname = name

    # take care of the german gender cases
    nname = aname.replace("er ", r"(\[a\]|(e|es|er|en)) ").replace("es ", r"(\[a\]|(e|es|er|en)) ").replace("en ", r"(\[a\]|(e|es|er|en)) ").replace("e ", r"(\[a\]|(e|es|er|en)) ")
    if nname.endswith("e"):
        nname = nname[:-1] + r"(\[a\]|(e|es|er|en))"
    elif nname.endswith("en") or nname.endswith("es") or nname.endswith("er"):
        nname = nname[:-2] + r"(\[a\]|(e|es|er|en))"

    # check results agains bnpcname
    for key, bnpc in bnpcname.items():
        m = re.search(nname, bnpc["Singular_de"].lower())
        if m:
            return bnpc[f"Singular_{lang}"]

    # check results agains eobjname
    for key, eobj in eobjname.items():
        m = re.search(nname, eobj["Singular_de"].lower())
        if m:
            return eobj[f"Singular_{lang}"]

    # check results agains eobjname
    for key, eobj in enpcresident.items():
        m = re.search(nname, eobj["Singular_de"].lower())
        if m:
            return eobj[f"Singular_{lang}"]
    # return anything, just in case
    print_color_yellow(f"Missing {name} examples where ({aname}) and ({nname})")
    return ""


def uglyContentNameFix(name, instanceType=None, difficulty=None):
    if difficulty == "Fatal" and instanceType == "raid" and "fatal" not in name.lower():
        name = f"{name} (fatal)"
    elif difficulty == "Episch" and instanceType == "raid" and "episch" not in name.lower():
        name = f"{name} (episch)"
    elif difficulty == "Schwer" and instanceType == "dungeon" and "schwer" not in name.lower():
        name = f"{name} (schwer)"
    # handle stupid edge cases for primals
    elif name in ["Königliche Konfrontation", "Jagd auf Rathalos"] and difficulty.lower() != "normal":
        name = f"{name} ({difficulty.lower()})"
    elif name in ["Memoria Misera"] and difficulty.lower() != "normal":
        name = f"{name} ({difficulty.lower()})"
    # handle edge cases PvP
    elif "(Flechtenhain)" in name:
        name = name.replace("(Flechtenhain)", "")
    elif "(Kampfplatz)" in name:
        name = name.replace("(Kampfplatz)", "")
    # placeholder
    elif name == "":
        return ""
    return name


def translateAttack(skill_id):
    return action[str(int(skill_id, 16)) + ".0"]["Name_en"].title().replace("Iii", "III").replace("Ii", "II").replace(" Iv", " IV")


def replaceSlug(text):
    return str(text).replace(",", "").replace("'", "").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue").replace("ß", "ss")


def getImage(image):
    image = image.replace(".tex", ".png\"")
    return image


def writeTags(fi, _entry, tt_type_name):
    # write tags per expansion
    if _entry["categories"] == "arr":
        fi.write("    - term: \"A Realm Reborn\"\n")
        fi.write("    - term: \"ARR\"\n")
    elif _entry["categories"] == "hw":
        fi.write("    - term: \"Heavensward\"\n")
        fi.write("    - term: \"HW\"\n")
    elif _entry["categories"] == "sb":
        fi.write("    - term: \"Stormblood\"\n")
        fi.write("    - term: \"SB\"\n")
    elif _entry["categories"] == "shb":
        fi.write("    - term: \"Shadowbringers\"\n")
        fi.write("    - term: \"ShB\"\n")
    else:
        pass

    for lang in ["de", "en", "fr", "ja", "cn", "ko"]:
        fi.write("    - term: \"" + tt_type_name["Name_" + lang] + "\"\n")

    #fi.write("    - term: \"" + _entry["title"] + "\"\n")
    for lang in ["de", "en", "fr", "ja", "cn", "ko"]:
        fi.write("    - term: \"" + getContentName(_entry["title"], lang, _entry["difficulty"], _entry["instanceType"]) + "\"\n")

    # write rest of the tags
    fi.write("    - term: \"" + _entry["difficulty"] + "\"\n")
    fi.write("    - term: \"" + _entry["patchNumber"] + "\"\n")
    fi.write("    - term: \"" + _entry["patchName"] + "\"\n")
    fi.write("    - term: \"" + _entry["quest"] + "\"\n")
    if checkVariable(_entry,"mount1") or checkVariable(_entry,"mount2"):
        fi.write("    - term: \"mounts\"\n")
    if checkVariable(_entry,"minion1") or checkVariable(_entry,"minion2") or checkVariable(_entry,"minion3"):
        fi.write("    - term: \"minions\"\n")
    if checkVariable(_entry,"tt_card1") or checkVariable(_entry,"tt_card2"):
        fi.write("    - term: \"tt_cards\"\n")
    if checkVariable(_entry,"gearset_loot"):
        for gset in _entry["gearset_loot"].split(","):
            fi.write("    - term: \"" + gset + "\"\n")
    if checkVariable(_entry,"orchestrion") or checkVariable(_entry,"orchestrion2") or checkVariable(_entry,"orchestrion3") or checkVariable(_entry,"orchestrion4") or checkVariable(_entry,"orchestrion5"):
        fi.write("    - term: \"orchestrion\"\n")
    if checkVariable(_entry,"orchestrion_material1") or checkVariable(_entry,"orchestrion_material2") or checkVariable(_entry,"orchestrion_material3"):
        fi.write("    - term: \"orchestrion_material\"\n")
    if _entry["instanceType"] == "trial":
        fi.write("    - term: \"" + "Prüfung" + "\"\n")
        fi.write("    - term: \"Trial\"\n")
        fi.write("    - term: \"Primae\"\n")
        fi.write("    - term: \"Primal\"\n")
    fi.write("    - term: \"" + _entry["instanceType"] + "\"\n")

    if not _entry["bosse"] == ['']:
        for b in _entry["bosse"]:
            if b != "Unknown_":
                fi.write("    - term: \"" + b + "\"\n")
    if not _entry["tags"] == ['']:
        for t in _entry["tags"]:
            if t != "Unknown_":
                fi.write("    - term: \"" + t + "\"\n")


#Gray box above attacks for each enemy entry
def add_example_Sequence(spaces, fi, combatant):
    fi.write(spaces + "sequence:\n")
    fi.write(spaces + "  - phase: \"09\"\n")
    if combatant == "add":
        return
    fi.write(spaces + "    alerts:\n")
    fi.write(spaces + "      - alert: \"Die folgenden Angriffe haben sind entweder unbekannt oder haben keine klare Herkunft\"\n")
    fi.write(spaces + "    mechanics:\n")
    fi.write(spaces + "      - title: \"sequence-mechanic-01\"\n")
    fi.write(spaces + "        notes:\n")
    fi.write(spaces + "          - note: \"sequence-mechanic-note-01\"\n")
    fi.write(spaces + "    attacks:\n")
    fi.write(spaces + "      - attack: \"sequence-attack-01\"\n")
    fi.write(spaces + "    images:\n")
    fi.write(spaces + "      - url: \"/assets/img/test.jpg\"\n")
    fi.write(spaces + "    videos:\n")
    fi.write(spaces + "      - url: \"https&#58;//akurosia.de/upload/test.mp4\"\n")


def regular_attack(spaces, fi, combatant, data=["Attack-titel", "Attack-titel", "false", "false", "regular", "None", "09", "Attack-role", "Attack-tag", "Attack-note"]):
    fi.write(spaces + f"  - title: \"{data[0]}\"\n")
    fi.write(spaces + f"    title_en: \"{data[1]}\"\n")
    fi.write(spaces + f"    attack_in_use: \"{data[2]}\"\n")
    fi.write(spaces + f"    disable: \"{data[3]}\"\n")
    fi.write(spaces + f"    type: \"{data[4]}\"\n")
    fi.write(spaces + f"    damage_type: \"{data[5]}\"\n")
    fi.write(spaces + f"    phases:\n")
    fi.write(spaces + f"      - phase: \"{data[6]}\"\n")
    fi.write(spaces + f"    roles:\n")
    fi.write(spaces + f"      - role: \"{data[7]}\"\n")
    fi.write(spaces + f"    tags:\n")
    fi.write(spaces + f"      - tag: \"{data[8]}\"\n")
    if combatant == "add":
        return
    fi.write(spaces + "    notes:\n")
    fi.write(spaces + f"      - note: \"{data[9]}\"\n")


def combo_attack(spaces, fi, data=["Combo-titel", "Combo-titel", "false", "combo", "None", "09", "Combo-title 1", "Combo-role 1", "Combo-tag 1", "Combo-note 1", "Combo-title 2", "Combo-role 2", "Combo-tag 2", "Combo-note 2", "Combo-note BIG"]):
    fi.write(spaces + f"  - title: \"{data[0]}\"\n")
    fi.write(spaces + f"    title_en: \"{data[1]}\"\n")
    fi.write(spaces + f"    attack_in_use: \"{data[2]}\"\n")
    fi.write(spaces + f"    type: \"{data[3]}\"\n")
    fi.write(spaces + f"    damage_type: \"{data[4]}\"\n")
    fi.write(spaces + "    phases:\n")
    fi.write(spaces + f"      - phase: \"{data[5]}\"\n")
    fi.write(spaces + "    combo:\n")
    fi.write(spaces + f"      - title: \"{data[6]}\"\n")
    fi.write(spaces + "        roles:\n")
    fi.write(spaces + f"          - role: \"{data[7]}\"\n")
    fi.write(spaces + "        tags:\n")
    fi.write(spaces + f"          - tag: \"{data[8]}\"\n")
    fi.write(spaces + "        notes:\n")
    fi.write(spaces + f"          - note: \"{data[9]}\"\n")
    fi.write(spaces + f"      - title: \"{data[10]}\"\n")
    fi.write(spaces + "        roles:\n")
    fi.write(spaces + f"          - role: \"{data[11]}\"\n")
    fi.write(spaces + "        tags:\n")
    fi.write(spaces + f"          - tag: \"{data[12]}\"\n")
    fi.write(spaces + "        notes:\n")
    fi.write(spaces + f"          - note: \"{data[13]}\"\n")
    fi.write(spaces + "    notes:\n")
    fi.write(spaces + f"      - note: \"{data[14]}\"\n")


def variation_attack(spaces, fi, data=["Variation-titel", "Variation-titel", "false", "variation", "09", "Variation-note BIG", "Variation-title 1", "Variation-title_id 1", "None", "Variation-role 1", "Variation-tag 1", "Variation-note 1", "Variation-title 2", "Variation-title_id 2", "None", "Variation-role 2", "Variation-tag 2", "Variation-note 2"]):
    fi.write(spaces + f"  - title: \"{data[0]}\"\n")
    fi.write(spaces + f"    title_en: \"{data[1]}\"\n")
    fi.write(spaces + f"    attack_in_use: \"{data[2]}\"\n")
    fi.write(spaces + f"    type: \"{data[3]}\"\n")
    fi.write(spaces + "    phases:\n")
    fi.write(spaces + f"      - phase: \"{data[4]}\"\n")
    fi.write(spaces + "    notes:\n")
    fi.write(spaces + f"      - note: \"{data[5]}\"\n")
    fi.write(spaces + "    variation:\n")
    fi.write(spaces + f"      - title: \"{data[6]}\"\n")
    fi.write(spaces + f"        title_id: \"{data[7]}\"\n")
    fi.write(spaces + f"        damage_type: \"{data[8]}\"\n")
    fi.write(spaces + "        roles:\n")
    fi.write(spaces + f"          - role: \"{data[9]}\"\n")
    fi.write(spaces + "        tags:\n")
    fi.write(spaces + f"          - tag: \"{data[10]}\"\n")
    fi.write(spaces + "        notes:\n")
    fi.write(spaces + f"          - note: \"{data[11]}\"\n")
    fi.write(spaces + f"      - title: \"{data[12]}\"\n")
    fi.write(spaces + f"        title_id: \"{data[13]}\"\n")
    fi.write(spaces + f"        damage_type: \"{data[14]}\"\n")
    fi.write(spaces + "        roles:\n")
    fi.write(spaces + f"          - role: \"{data[15]}\"\n")
    fi.write(spaces + "        tags:\n")
    fi.write(spaces + f"          - tag: \"{data[16]}\"\n")
    fi.write(spaces + "        notes:\n")
    fi.write(spaces + f"          - note: \"{data[17]}\"\n")


def addAttacks(spaces, fi, combatant, attack_json=None):
    fi.write(spaces + "attacks:\n")
    inProgress = False
    currentSkill = ""
    # if logdata with attack of the enemy is available
    if attack_json != {} and attack_json is not None:
        attack_json = sorted(attack_json.items(), key = lambda x: x[1]['name'])
        # get skills with same name but different ID
        variations = checkAttacksForVariations(attack_json)
        for skill_id, skill in attack_json:
            # check if it might be a variation
            if skill['name'] in variations:
                # if variation was already added
                if not skill['name'] == currentSkill:
                    inProgress = False
                # add variation and add it also to the check array
                inProgress, currentSkill = addVariation("    ", fi, [skill_id, skill], inProgress)
                continue

            # this if loop is to filter out empty names, it is dump because i am lazy to make it propper for the title_en
            if skill["name"] == "":
                skill_name = "Unknown_" + skill_id
            else:
                skill_name = skill["name"]
            fi.write(spaces + f"  - title: \"{skill_name}\"\n")
            fi.write(spaces + f"    title_id: \"{skill_id}\"\n")
            if not skill["name"] == "":
                fi.write(spaces + f"    title_en: \"{translateAttack(skill_id)}\"\n")
            fi.write(spaces +  "    attack_in_use: \"false\"\n")
            if skill_name.startswith("Unknown_") or skill_name == ("Attacke"):
                fi.write(spaces + "    disable: \"true\"\n")
            else:
                fi.write(spaces + "    disable: \"false\"\n")
            fi.write(spaces + "    type: \"regular\"\n")
            fi.write(spaces + "    damage_type: \"" + skill["damage_type"] + "\"\n")
            fi.write(spaces + "    phases:\n")
            fi.write(spaces + "      - phase: \"09\"\n")
            # dont add roles, tags and notes for unknown skills
            if skill_name.startswith("Unknown_"):
                continue
            # add customized roles and tags attacke skills
            if skill_name == ("Attacke"):
                fi.write(spaces + "    roles:\n")
                fi.write(spaces + "      - role: \"Tank\"\n")
                fi.write(spaces + "    tags:\n")
                fi.write(spaces + "      - tag: \"Auto-Angriff\"\n")
                continue
            fi.write(spaces + "    roles:\n")
            fi.write(spaces + "      - role: \"role\"\n")
            fi.write(spaces + "    tags:\n")
            fi.write(spaces + "      - tag: \"tag\"\n")
            # dont notes for adds
            if combatant == "add":
                continue
            fi.write(spaces + "    notes:\n")
            fi.write(spaces + "      - note: \"note\"\n")
    else:
        # add default attack
        regular_attack(spaces, fi, combatant)


def addVariation(spaces, fi, attack_json={}, inProgress=False):
    if attack_json:
        if not inProgress:
            inProgress = True
            fi.write(spaces + f"  - title: \"{attack_json[1]['name']}\"\n")
            if not attack_json[1]['name'] == "":
                fi.write(spaces + f"    title_en: \"{translateAttack(attack_json[0])}\"\n")
            fi.write(spaces + "    attack_in_use: \"false\"\n")
            fi.write(spaces + "    type: \"variation\"\n")
            fi.write(spaces + "    phases:\n")
            fi.write(spaces + "      - phase: \"09\"\n")
            fi.write(spaces + "    notes:\n")
            fi.write(spaces + "      - note: \"Variation-note BIG\"\n")
            fi.write(spaces + "    variation:\n")
        fi.write(spaces + f"      - title: \"{attack_json[1]['name']}\"\n")
        fi.write(spaces + f"        title_id: \"{attack_json[0]}\"\n")
        fi.write(spaces + f"        damage_type: \"{attack_json[1]['damage_type']}\"\n")
        fi.write(spaces + "        roles:\n")
        fi.write(spaces + "          - role: \"Variation-role 1\"\n")
        fi.write(spaces + "        tags:\n")
        fi.write(spaces + "          - tag: \"Variation-tag 1\"\n")
        fi.write(spaces + "        notes:\n")
        fi.write(spaces + "          - note: \"Variation-note 1\"\n")
        return inProgress, attack_json[1]['name']
    else:
        variation_attack(spaces, fi)

def checkAttacksForVariations(json):
    douplicate_keys = {}
    for item in json:
        douplicate_keys[item[1]['name']] =  douplicate_keys.get(item[1]['name'], 0) + 1

    remove_keys = ['']
    for x in douplicate_keys:
        if douplicate_keys[x] == 1:
            remove_keys.append(x)

    for x in remove_keys:
        try:
            del douplicate_keys[x]
        except:
            pass

    return douplicate_keys


def remove_skill_from_overview(_all, removed):
    try:
        del _all[removed]
    except:
        pass
        #print("Error when removing: " + removed)
    return _all

def addOldEnemyData(fi, enemy, title):
    all_enemy_attacks = dict(logdata.get(title, {}).get(str(enemy.get("title", None)), {}).get("skill", {}))
    # add boss name and id
    addTextIfFoundToEnemyData(fi, enemy, "title", "  - title: \"" + str(enemy.get("title", None)) + "\"\n")
    addTextIfFoundToEnemyData(fi, enemy, "title_en", "    title_en: \"" + str(enemy.get("title_en", None)) + "\"\n")
    addTextIfFoundToEnemyData(fi, enemy, "id", "    id: \"" + str(enemy.get("id", None)) + "\"\n")

    # add attack section
    if enemy.get("attacks", None):
        fi.write("    attacks:\n")
        for attack in enemy.get("attacks", None):
            all_enemy_attacks = remove_skill_from_overview(all_enemy_attacks, str(attack.get("title_id", None)))
            addTextIfFoundToEnemyData(fi, attack, "title", "      - title: \"" + str(attack.get("title", None)) + "\"\n")
            if attack.get("type", "regular") in ["regular", "dutyActions"]:
                addTextIfFoundToEnemyData(fi, attack, "title_id", "        title_id: \"" + str(attack.get("title_id", None)) + "\"\n")
            if attack.get("title_en", None):
                addTextIfFoundToEnemyData(fi, attack, "title_en", "        title_en: \"" + str(attack.get("title_en", None)) + "\"\n")
            addTextIfFoundToEnemyData(fi, attack, "attack_in_use", "        attack_in_use: \"" + str(attack.get("attack_in_use", "false")) + "\"\n")
            addTextIfFoundToEnemyData(fi, attack, "disable", "        disable: \"" + str(attack.get("disable", "false")) + "\"\n")
            addTextIfFoundToEnemyData(fi, attack, "type", "        type: \"" + str(attack.get("type", "regular")) + "\"\n")
            if attack.get("type", "regular") in ["regular", "dutyActions"]:
                addTextIfFoundToEnemyData(fi, attack, "damage_type", "        damage_type: \"" + str(attack.get("damage_type", None)) + "\"\n", True, title, enemy.get("title", None), attack.get("title_id", None))
            addElementForEnemyData(fi, attack, "dutyActions", "          - ", "action")
            addElementForEnemyData(fi, attack, "phases", "          - ", "phase")
            if str(attack.get("title", None)).startswith("Unknown_"):
                continue
            addElementForEnemyData(fi, attack, "roles", "          - ", "role")
            addElementForEnemyData(fi, attack, "tags", "          - ", "tag")
            addElementForEnemyData(fi, attack, "notes", "          - ", "note")
            if attack.get("variation", None):
                fi.write("        variation:\n")
                for variation in attack.get("variation", None):
                    all_enemy_attacks = remove_skill_from_overview(all_enemy_attacks, str(variation.get("title_id", None)))
                    addTextIfFoundToEnemyData(fi, variation, "title", f"          - title: \"" + str(variation.get('title', None)) + "\"\n")
                    addTextIfFoundToEnemyData(fi, variation, "title_id", f"            title_id: \"" + str(variation.get('title_id', None)) + "\"\n")
                    addTextIfFoundToEnemyData(fi, variation, "damage_type", "            damage_type: \"" + str(variation.get("damage_type", None)) + "\"\n", True, title, enemy.get("title", None), variation.get("title_id", None))
                    addElementForEnemyData(fi, variation, "phases", "              - ", "phase")
                    addElementForEnemyData(fi, variation, "roles", "              - ", "role")
                    addElementForEnemyData(fi, variation, "tags", "              - ", "tag")
                    addElementForEnemyData(fi, variation, "notes", "              - ", "note")
                    addElementForEnemyData(fi, variation, "images", "              - ", ["url", "alt", "height"])
                    addElementForEnemyData(fi, variation, "videos", "              - ", "url")
            if attack.get("combo", None):
                fi.write("        combo:\n")
                for combo in attack.get("combo", None):
                    all_enemy_attacks = remove_skill_from_overview(all_enemy_attacks, str(combo.get("title_id", None)))
                    if combo.get("title", None):
                        fi.write(f"          - title: \"" + f"{combo.get('title', None)}" + "\"\n")
                        fi.write(f"            title_id: \"" + f"{combo.get('title_id', None)}" + "\"\n")
                        fi.write(f"            damage_type: \"" + f"{combo.get('damage_type', None)}" + "\"\n")
                    addElementForEnemyData(fi, combo, "roles", "              - ", "role")
                    addElementForEnemyData(fi, combo, "tags", "              - ", "tag")
                    addElementForEnemyData(fi, combo, "notes", "              - ", "note")
                    addElementForEnemyData(fi, combo, "images", "              - ", ["url", "alt", "height"])
                    addElementForEnemyData(fi, combo, "videos", "              - ", "url")
            addElementForEnemyData(fi, attack, "images", "          - ", ["url", "alt", "height"])
            addElementForEnemyData(fi, attack, "videos", "          - ", "url")
    # if any attack is not in the created file, print it out
    if not all_enemy_attacks == {}:
        print_color_blue(title, end=" -> ")
        print_color_red(str(enemy.get("title", None)), end=" -> ")
        print_color_yellow(f"Missing attacks: {all_enemy_attacks}\n")
    #add sequence section
    if enemy.get("sequence", None):
        fi.write("    sequence:\n")
        for sequence in enemy.get("sequence", None):
            addTextIfFoundToEnemyData(fi, sequence, "phase", "      - phase: \"" + f"{int(sequence.get('phase', None)):02d}" + "\"\n")
            addElementForEnemyData(fi, sequence, "alerts", "          - ", "alert")
            if sequence.get("mechanics", None):
                fi.write("        mechanics:\n")
                for mechanic in sequence.get("mechanics", None):
                    addTextIfFoundToEnemyData(fi, mechanic, "title", "          - title: \"" + str(mechanic.get("title", None)) + "\"\n")
                    addElementForEnemyData(fi, mechanic, "notes", "              - ", "note")
            addElementForEnemyData(fi, sequence, "attacks", "          - ", "attack")
            addElementForEnemyData(fi, sequence, "images", "          - ", ["url", "alt", "height"])
            addElementForEnemyData(fi, sequence, "videos", "          - ", "url")


def debugPrint(title, text):
    if title == "title":
        print(text)


def addTextIfFoundToEnemyData(fi, element_array, needed_elements, text, addTemplate=False, title=None, enemy=None, attack_id=None):
    if addTemplate:
        try:
            if logdata_lower.get(title.lower(), None):
                debugPrint(title, f"\nFound title {title}")
                if logdata[title].get(enemy, None):
                    debugPrint(title, f"Found enemy {enemy}")
                    if logdata[title][enemy].get("skill", None):
                        debugPrint(title, f"Found skills {logdata[title][enemy].get('skill', None)}")
                        debugPrint(title, f"Try to get skill {attack_id}")
                        if logdata[title][enemy]["skill"].get(attack_id, None):
                            debugPrint(title, f"Write: {text.replace('None', logdata[title][enemy]['skill'][attack_id][needed_elements])}")
                            fi.write(text.replace("None", logdata[title][enemy]["skill"][attack_id][needed_elements]))
                            return
        except:
            fi.write(text)
            return
    fi.write(text)


def addElementForEnemyData(fi, element_array, leftside_elements, before_tag, rightside_elements):
    ori_before_tag = before_tag
    # convert rightside_elements to array
    if type(rightside_elements) == str:
        rightside_elements = [rightside_elements]
    if element_array.get(leftside_elements, None):
        fi.write(f"{before_tag[:-4]}{leftside_elements}:\n")
        for element in element_array.get(leftside_elements, None):
            # cycle through all elements that were either converted in the beginning or not
            for i, e in enumerate(rightside_elements):
                # handle the "-" option before yamle list elements
                if i > 0 and e != rightside_elements[0]:
                    before_tag = before_tag[0:-2] + "  "
                else:
                    before_tag = ori_before_tag
                if element.get(e, None):
                    if type(element[e]) == int:
                        value = str(f"{element[e]:02d}")
                    else:
                        value = "\"" + str(element[e]) + "\""
                    fi.write(f"{before_tag}{e}: " + value + "\n")


def addBosseOrAdds(_entry, fi, _old_bosses, all_combatants, combatant):
    title = _entry["title"].title()
    title = uglyContentNameFix(title, _entry['instanceType'], _entry['difficulty'])
    if _old_bosses:
        if all_combatants == "bosse":
            fi.write("bosses:\n")
        else:
            fi.write(f"{all_combatants}:\n")
        for enemy in _old_bosses:
            addOldEnemyData(fi, enemy, title)
    # if logdata is available
    elif logdata_lower.get(title.lower(), None):
        if all_combatants == "bosse":
            fi.write("bosses:\n")
        else:
            fi.write(f"{all_combatants}:\n")
        counter = 1
        for enemy_name, enemy_attacks in logdata_lower.get(title.lower(), None).items():
            if enemy_name == "" or enemy_name.lower() == "zone" or enemy_name.lower() == "combatants":
                continue
            # this sorts adds and bosses
            if enemy_name.lower() in [x.lower() for x in _entry["bosse"]] and combatant == "add":
                continue
            if enemy_name.lower() not in [x.lower() for x in _entry["bosse"]] and combatant == "boss":
                continue
            fi.write("  - title: \"" + enemy_name + "\"\n")
            fi.write("    title_en: \"" + getBnpcName(enemy_name) + "\"\n")
            fi.write(f"    id: \"{combatant}" + str(f"{counter:02d}") + "\"\n")
            addAttacks("    ", fi, combatant, enemy_attacks.get("skill", {}))
            add_example_Sequence("    ", fi, combatant)
            counter += 1
    # if no logdata is available
    elif _entry[all_combatants] != "":
        if _entry["instanceType"] != "pvp":
            print(f"Error on {title}, use {all_combatants} from XLSX")
        if all_combatants == "bosse":
            fi.write("bosses:\n")
        else:
            fi.write(f"{all_combatants}:\n")
        counter = 1
        for b in _entry[all_combatants]:
            fi.write("  - title: \"" + b + "\"\n")
            fi.write("    title_en: \"" + getBnpcName(b) + "\"\n")
            fi.write(f"    id: \"{combatant}" + str(f"{counter:02d}") + "\"\n")
            addAttacks("    ", fi, combatant)
            combo_attack("    ", fi)
            addVariation("    ", fi)
            add_example_Sequence("    ", fi, combatant)
            counter += 1


# XYZ Notizen
def addMechanics(_entry, fi, _old_mechanics=None):
    if _old_mechanics:
        fi.write("mechanics:\n")
        for mechanic in _old_mechanics:
            fi.write("  - title: \"" + mechanic['title'] + "\"\n")
            if mechanic.get("steps", None):
                fi.write("    steps:\n")
                for step in mechanic["steps"]:
                    fi.write(f"      - step: \"{int(step['step']):02d}\"\n")
                    addElementForEnemyData(fi, step, "notes", "          - ", "note")
                    addElementForEnemyData(fi, step, "images", "          - ", ["url", "alt", "height"])
                    addElementForEnemyData(fi, step, "videos", "          - ", "url")
    elif _entry["mechanics"] != "":
        fi.write("mechanics:\n")
        mechanics = _entry["mechanics"].strip("\"[").strip("]\"").split("\",\"")
        counter = 1
        for m in mechanics:
            if mechanics == ['']:
                fi.write(f"  - title: \"Mechanic-Title {counter}\"\n")
            else:
                fi.write("  - title: \"" + m + "\"\n")
            fi.write("    steps:\n")
            fi.write("      - step: 09\n")
            fi.write("        notes:\n")
            fi.write(f"          - note: \"Mechanics-note {counter}\"\n")
            fi.write("        images:\n")
            fi.write("          - url: \"/assets/img/test.jpg\"\n")
            fi.write("            alt: \"/assets/img/test.jpg\"\n")
            fi.write("            height: \"500px\"\n")
            fi.write("        videos:\n")
            fi.write("          - url: \"https&#58;//akurosia.de/upload/test.mp4\"\n")
            counter += 1


# Notizen, Bosse und Adds
def addGuide(fi, _entry, _old_bosses, _old_adds, _old_mechanics):
    addMechanics(_entry, fi, _old_mechanics)
    addBosseOrAdds(_entry, fi, _old_bosses, "bosse", "boss")
    addBosseOrAdds(_entry, fi, _old_adds, "adds", "add")


def get_video_url(url):
    if url.startswith("https"):
        return url
    return "https://www.youtube.com/watch?v={}".format(url)


def clean_entries(_entry):
    for key, value in _entry.items():
        if value.startswith("'"):
            _entry[key] = value[1:]
        if value.endswith("'"):
            _entry[key] = value[:-1]
    return _entry


def get_order_id(_entry):
    patch = "0000"
    plvl = "00"
    sortid = "0000"
    if "." in _entry["patchNumber"]:
        t_minor = 0
        major, minor = _entry["patchNumber"].split(".")
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
    if _entry["plvl"]:
        plvl = int(_entry["plvl"]) * 10 if len(_entry["plvl"]) < 2 else _entry["plvl"]
    if _entry["sortid"]:
        sortid = f"0{_entry['sortid']}" if len(_entry["sortid"]) < 1 else _entry["sortid"]
        sortid = f"0{sortid}" if len(sortid) < 2 else sortid
        sortid = f"0{sortid}" if len(sortid) < 3 else sortid
        sortid = f"0{sortid}" if len(sortid) < 4 else sortid
    return f"{patch}{plvl}{sortid}"


def get_territorytype_from_mapid(mapid):
    for key, tt_type in territorytype.items():
        if tt_type["Name"].lower() == mapid.lower():
            return tt_type
    return "unknown Zone"


def rewrite_content_even_if_exists(_entry, fi, index):
    tt_type_name = get_territorytype_from_mapid(_entry["mapid"])
    fi.write('title: "' + _entry["title"] + '"\n')
    fi.write('title_de: "' + getContentName(_entry["title"], "de", _entry["difficulty"], _entry["instanceType"]) + '"\n')
    fi.write('title_en: "' + getContentName(_entry["title"], "en", _entry["difficulty"], _entry["instanceType"]) + '"\n')
    fi.write('layout: guide_post\n')
    fi.write('page_type: guide\n')
    fi.write(f'excel_line: \"{index}\"\n')
    fi.write('categories: "' + _entry["categories"] + '"\n')
    fi.write('patchNumber: "' + _entry["patchNumber"].replace("'", "") + '"\n')
    fi.write('difficulty: "' + _entry["difficulty"] + '"\n')
    fi.write('instanceType: "' + _entry["instanceType"] + '"\n')
    fi.write('date: "' + _entry["date"] + '"\n')
    fi.write('slug: "' + replaceSlug(_entry["slug"]) + '"\n')
    if _entry["image"]:
        fi.write('image:\n')
        fi.write('    - urlSmall: \"https://ffxiv.akurosia.de/extras/images/' + getImage(_entry["image"]) + '\n')
        fi.write('    - url: \"https://ffxiv.akurosia.de/extras/images/' + getImage(_entry["image"]) + '\n')
    fi.write('terms:\n')
    writeTags(fi, _entry, tt_type_name)
    fi.write('patchName: "' + _entry["patchName"] + '"\n')
    fi.write('mapid: "' + _entry["mapid"] + '"\n')
    fi.write('contentname: "' + tt_type_name["Name_de"] + '"\n')
    fi.write('sortid: ' + _entry["sortid"] + '\n')
    fi.write('plvl: ' + _entry["plvl"] + '\n')
    fi.write('plvl_sync: ' + _entry["plvl_sync"] + '\n')
    fi.write('ilvl: ' + _entry["ilvl"] + '\n')
    fi.write('ilvl_sync: ' + _entry["ilvl_sync"] + '\n')
    if not _entry["quest"] == "":
        fi.write('quest: "' + _entry["quest"] + '"\n')
    if not _entry["quest_location"] == "":
        fi.write('quest_location: "' + _entry["quest_location"] + '"\n')
    if not _entry["quest_npc"] == "":
        fi.write('quest_npc: "' + _entry["quest_npc"] + '"\n')
    fi.write('order: ' + get_order_id(_entry) + '\n')
    # mounts
    if checkVariable(_entry,"mount1") or checkVariable(_entry,"mount2"):
        fi.write('mount:\n')
        if checkVariable(_entry,"mount1"):
            fi.write('    - name: "' + _entry["mount1"] + '"\n')
        if checkVariable(_entry,"mount2"):
            fi.write('    - name: "' + _entry["mount2"] + '"\n')
    # minions
    if checkVariable(_entry,"minion1") or checkVariable(_entry,"minion2") or checkVariable(_entry,"minion3"):
        fi.write('minion:\n')
        if checkVariable(_entry,"minion1"):
            fi.write('    - name: "' + _entry["minion1"] + '"\n')
        if checkVariable(_entry,"minion2"):
            fi.write('    - name: "' + _entry["minion2"] + '"\n')
        if checkVariable(_entry,"minion3"):
            fi.write('    - name: "' + _entry["minion3"] + '"\n')
    # gearset_loot
    if checkVariable(_entry,"gearset_loot"):
        fi.write('gearset_loot:\n')
        for gset in _entry["gearset_loot"] .split(","):
            fi.write('    - gsetname: "' + gset + '"\n')
    # tt_cards
    if checkVariable(_entry,"tt_card1") or checkVariable(_entry,"tt_card2"):
        fi.write('tt_card:\n')
        if checkVariable(_entry,"tt_card1"):
            fi.write('    - name: "' + _entry["tt_card1"] + '"\n')
        if checkVariable(_entry,"tt_card2"):
            fi.write('    - name: "' + _entry["tt_card2"] + '"\n')
    # orchestrion
    if checkVariable(_entry,"orchestrion") or checkVariable(_entry,"orchestrion2") or checkVariable(_entry,"orchestrion3") or checkVariable(_entry,"orchestrion4") or checkVariable(_entry,"orchestrion5"):
        fi.write('orchestrion:\n')
        if checkVariable(_entry,"orchestrion"):
            fi.write('    - name: "' + _entry["orchestrion"] + '"\n')
        if checkVariable(_entry,"orchestrion2"):
            fi.write('    - name: "' + _entry["orchestrion2"] + '"\n')
        if checkVariable(_entry,"orchestrion3"):
            fi.write('    - name: "' + _entry["orchestrion3"] + '"\n')
        if checkVariable(_entry,"orchestrion4"):
            fi.write('    - name: "' + _entry["orchestrion4"] + '"\n')
        if checkVariable(_entry,"orchestrion5"):
            fi.write('    - name: "' + _entry["orchestrion5"] + '"\n')
    # orchestrion material
    if checkVariable(_entry,"orchestrion_material1") or checkVariable(_entry,"orchestrion_material2") or checkVariable(_entry,"orchestrion_material3"):
        fi.write('orchestrion_material:\n')
        if checkVariable(_entry,"orchestrion_material1"):
            fi.write('    - name: "' + _entry["orchestrion_material1"] + '"\n')
        if checkVariable(_entry,"orchestrion_material2"):
            fi.write('    - name: "' + _entry["orchestrion_material2"] + '"\n')
        if checkVariable(_entry,"orchestrion_material3"):
            fi.write('    - name: "' + _entry["orchestrion_material3"] + '"\n')
    # rouletts
    if _entry["allianceraid"] == "True" or _entry["frontier"] == "True" or _entry["expert"] == "True" or _entry["guildhest"] == "True" or _entry["level50_60"] == "True" or _entry["level70"] == "True" or _entry["leveling"] == "True" or _entry["main"] == "True" or _entry["mentor"] == "True" or _entry["normalraid"] == "True"  or _entry["trial"] == "True":
        fi.write('rouletts:\n')
        if _entry["allianceraid"]:
            fi.write('    - allianceraid: ' + _entry["allianceraid"] + "\n")
        if _entry["frontier"]:
            fi.write('      frontier: ' + _entry["frontier"] + "\n")
        if _entry["expert"]:
            fi.write('      expert: ' + _entry["expert"] + "\n")
        if _entry["guildhest"]:
            fi.write('      guildhest: ' + _entry["guildhest"] + "\n")
        if _entry["level50_60"]:
            fi.write('      level50_60: ' + _entry["level50_60"] + "\n")
        if _entry["level70"]:
            fi.write('      level70: ' + _entry["level70"] + "\n")
        if _entry["leveling"]:
            fi.write('      leveling: ' + _entry["leveling"] + "\n")
        if _entry["main"]:
            fi.write('      main: ' + _entry["main"] + "\n")
        if _entry["mentor"]:
            fi.write('      mentor: ' + _entry["mentor"] + "\n")
        if _entry["normalraid"]:
            fi.write('      normalraid: ' + _entry["normalraid"] + "\n")
        if _entry["trial"]:
            fi.write('      trial: ' + _entry["trial"] + "\n")
    # links:
    if checkVariable(_entry,"teamcraftlink") or checkVariable(_entry,"garlandtoolslink") or checkVariable(_entry,"gamerescapelink"):
        fi.write('links:\n')
        if checkVariable(_entry,"teamcraftlink"):
            fi.write('    - teamcraftlink: "' + _entry["teamcraftlink"] + '"\n')
        if checkVariable(_entry,"garlandtoolslink"):
            fi.write('      garlandtoolslink: "' + _entry["garlandtoolslink"] + '"\n')
        if checkVariable(_entry,"gamerescapelink"):
            fi.write('      gamerescapelink: "' + _entry["gamerescapelink"] + '"\n')
    # videos
    if checkVariable(_entry,"mtqvid1"):
        fi.write('mtq_vid1: "' + get_video_url(_entry["mtqvid1"]) + '"\n')
    if checkVariable(_entry,"mtqvid2"):
        fi.write('mtq_vid2: "' + get_video_url(_entry["mtqvid2"]) + '"\n')
    if checkVariable(_entry,"mrhvid1"):
        fi.write('mrh_vid1: "' + get_video_url(_entry["mrhvid1"]) + '"\n')
    if checkVariable(_entry,"mrhvid2"):
        fi.write('mrh_vid2: "' + get_video_url(_entry["mrhvid2"]) + '"\n')


def seperateToArray(tag, _entry):
    if _entry[tag]:
        _entry[tag] = _entry[tag].strip("'[").strip("]'").strip("\"[").strip("]\"").strip("[").strip("]").replace("\", \"", "', '").replace("\",\"", "', '").split("', '")
        _entry[tag] = [b for b in _entry[tag]]


def write_content_to_file(_entry, _filename, _old_bosses, _old_adds, _old_mechanics, index):
    _entry = clean_entries(_entry)
    with open(_filename, "w", encoding="utf8") as fi:
        seperateToArray("bosse", _entry)
        seperateToArray("adds", _entry)
        seperateToArray("tags", _entry)

        fi.write('---\n')
        rewrite_content_even_if_exists(_entry, fi, index)
        # REST
        addGuide(fi, _entry, _old_bosses, _old_adds, _old_mechanics)
        fi.write('---')
        fi.write('\n')


#returns existing boss data if available
def get_old_content_if_file_is_found(_existing_filename):
    if os.path.exists(_existing_filename):
        with open(_existing_filename, encoding="utf8") as f:
            docs = yaml.load_all(f, Loader=Loader)
            for doc in docs:
                return doc.get("bosses", None), doc.get("adds", None), doc.get("mechanics", None), True
    return None, None, None, False


if __name__ == "__main__":
    # open file, get sheet, last row and last coulmn
    wb = openpyxl.load_workbook('./guide_ffxiv.xlsx')
    sheet = wb['Tabelle1']
    max_row = sheet.max_row
    max_column = sheet.max_column
    # specify elements you are looking for
    elements = ["exclude", "date", "sortid", "title", "categories", "slug", "image", "patchNumber", "patchName", "difficulty", "plvl", "plvl_sync", "ilvl", "ilvl_sync", "quest", "quest_npc", "quest_location", "gearset_loot", "tt_card1", "tt_card2", "orchestrion", "orchestrion2", "orchestrion3", "orchestrion4", "orchestrion5", "orchestrion_material1", "orchestrion_material2", "orchestrion_material3", "mtqvid1", "mtqvid2", "mrhvid1", "mrhvid2", "mount1", "mount2", "minion1", "minion2", "minion3", "instanceType", "allianceraid", "frontier", "expert", "guildhest", "level50_60", "level70", "leveling", "main", "mentor", "normalraid", "trial", "mapid", "bosse", "adds", "mechanics", "tags", "teamcraftlink", "garlandtoolslink", "gamerescapelink", "done"]
    # to avoid overlapping positions
    order = []
    # change into _posts dir
    os.chdir("./_posts")
    # for every row do:
    for i in range(2, max_row):
        # comment the 2 line out to filter fo a specific line, numbering starts with 1 like it is in excel
        #if i != 93:
        #    continue
        entry = {}
        # for every column in row add all elements into a dict:
        # max_column will ignore last column due to how range is working
        for j in range(1, max_column+1):
            entry[elements[j - 1]] = str(sheet.cell(row=int(i), column=int(j)).value).replace("None", "")
        # if the done collumn is not prefilled
        if entry["exclude"] == "end":
            print("END FLAG WAS FOUND!")
            sys.exit(0)
        if not (entry["exclude"] or entry["done"]):
            # remove time from excel datetime
            entry["date"] = str(entry["date"]).replace(" 00:00:00", "").replace("-", ".")
            # convert special chars for html usage
            entry["title"] = entry["title"]
            #print(entry["title"])
            entry['patchNumber'] = entry['patchNumber'][1:] if entry['patchNumber'].startswith("'") else entry['patchNumber']
            filename = f"{entry['categories']}_new/{entry['instanceType']}/{entry['date'].replace('.', '-')}--{entry['patchNumber']}--{entry['sortid'].zfill(5)}--{entry['slug'].replace(',', '')}.md"
            existing_filename = f"{entry['categories']}/{entry['instanceType']}/{entry['date'].replace('.', '-')}--{entry['patchNumber']}--{entry['sortid'].zfill(5)}--{entry['slug'].replace(',', '')}.md"
            old_bosses, old_adds, old_mechanics, replace_existing_file = get_old_content_if_file_is_found(existing_filename)
            # if old file was found, replace filename to save
            if replace_existing_file:
                filename = existing_filename
            # fix fataler raid
            if entry["instanceType"] == "fataler_raid":
                entry["instanceType"] = "raid"

            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            write_content_to_file(entry, filename, old_bosses, old_adds, old_mechanics, i)

