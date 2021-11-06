#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import copy
import os
from operator import itemgetter
import traceback
import re
import errno
import openpyxl
import yaml
import collections

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python_module'))
from ffxiv_aku import *

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

disable_green_print = True
disable_yellow_print = True
disable_blue_print = True

enemy = {
    "title": "",
    "title_en": "",
    "id": "",
    "hp": {
        "min": 100,
        "max": 0
    },
    "attacks": [{
        "title": "",
        "title_id": "",
        "title_en": "",
        "attack_in_use": "",
        "disable": "",
        "type": "",
        "damage_type": "",
        "damage": {
            "min": 100,
            "max": 0
        },
        "phases": [{
            "phase": "",
        }],
        "roles": [{
            "role": "",
        }],
        "tags": [{
            "tag": "",
        }],
        "notes": [{
            "note": "",
        }],
    }],
}
example_sequence = {
    "sequence": [{
        "phase": "09",
        "name": "phase_name",
        "alerts": [{
            "alert": "Die folgenden Angriffe haben sind entweder unbekannt oder haben keine klare Herkunft",
        }],
        "mechanics": [{
            "title": "sequence-mechanic-01",
            "notes": [{
                "note": "sequence-mechanic-note-01",
            }],
        }],
        "attacks": [{
            "attack": "sequence-attack-01",
        }],
        "images": [{
            "url": "/assets/img/test.jpg",
            "alt": "/assets/img/test.jpg",
            "height": "250px",
        }],
        "videos": [{
            "url": "https&#58;//ffxivguide.akurosia.de/upload/test.mp4",
        }],
    }]
}
example_add_sequence = {
    "sequence": [{
        "phase": "09",
    }]
}


# specify elements you are looking for
elements = ["exclude", "date", "sortid", "title", "categories", "slug", "image", "patchNumber", "patchName", "difficulty", "plvl", "plvl_sync", "ilvl", "ilvl_sync", "quest", "quest_npc", "quest_location", "gearset_loot", "tt_card1", "tt_card2", "orchestrion", "orchestrion2", "orchestrion3", "orchestrion4", "orchestrion5", "orchestrion_material1", "orchestrion_material2", "orchestrion_material3", "mtqvid1", "mtqvid2", "mrhvid1", "mrhvid2", "mount1", "mount2", "minion1", "minion2", "minion3", "instanceType", "allianceraid", "frontier", "expert", "guildhest", "level50_60", "level70", "leveling", "main", "mentor", "normalraid", "trial", "mapid", "bosse", "adds", "mechanics", "tags", "teamcraftlink", "garlandtoolslink", "gamerescapelink", "done"]

storeFilesInTmp(True)
logdata = get_any_Logdata()
logdata_lower = dict((k.lower(), v) for k, v in logdata.items())
action = loadDataTheQuickestWay("action_all.json", translate=True)
territorytype = loadDataTheQuickestWay("territorytype_all.json", translate=True)
contentfindercondition = loadDataTheQuickestWay("contentfindercondition_all.json", translate=True)
placename = loadDataTheQuickestWay("placename_all.json", translate=True)
bnpcname = loadDataTheQuickestWay("bnpcname_all.json", translate=True)
eobjname = loadDataTheQuickestWay("eobjname_all.json", translate=True)
status = loadDataTheQuickestWay("status_all.json", translate=True)
enpcresident = loadDataTheQuickestWay("enpcresident_all.json", translate=True)


def checkVariable(element, name):
    if element[name] and not element[name] == "###":
        return True
    return False


ba_name = {
    "de": "Eureka Baldesions Arsenal",
    "en": "The Baldesion Arsenal",
    "fr": "Eurêka et son arsenal",
    "ja": "バルデシオンアーセナル",
    "cn": "兵武塔",
    "ko": "발데시온 무기고"
}


def getContentName(name, lang="en", difficulty=None, instanceType=None):
    name = uglyContentNameFix(name, instanceType, difficulty)
    if name == "Eureka Baldesions Arsenal":
        return ba_name[lang]
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


def getBnpcNameFromID(_id, aname, nname):
    bnew_name = ""
    enew_name = ""
    ennew_name = ""
    try:
        bnew_name = bnpcname[_id + ".0"]["Singular_de"]
        m = re.search(nname, bnew_name, re.IGNORECASE)
        n = re.search(aname, bnew_name, re.IGNORECASE)
        if m or n:
            return bnpcname[_id + ".0"]["Singular_en"]
    except Exception:
        pass
    try:
        enew_name = eobjname[_id + ".0"]["Singular_de"]
        m = re.search(nname, enew_name, re.IGNORECASE)
        n = re.search(aname, enew_name, re.IGNORECASE)
        if m or n:
            return eobjname[_id + ".0"]["Singular_en"]
    except Exception:
        pass
    try:
        ennew_name = enpcresident[_id + ".0"]["Singular_de"]
        m = re.search(nname, ennew_name, re.IGNORECASE)
        n = re.search(aname, ennew_name, re.IGNORECASE)
        if m or n:
            return enpcresident[_id + ".0"]["Singular_en"]
    except Exception:
        pass
    if "α" not in bnew_name and "β" not in bnew_name and "（仮）鎖" not in bnew_name:
        print_color_red(f"'{bnew_name}', '{enew_name}', '{ennew_name}' not found {aname} ({nname}) - ({_id})")
    return ""


def getBnpcName(name, _id, lang="en"):
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

    if not _id == "":
        resultname = getBnpcNameFromID(_id, aname, nname)
        if not resultname == "":
            return resultname
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
    print_color_yellow(f"Missing {name} examples where ({aname}) and ({nname})", disable_yellow_print)
    return ""


def uglyContentNameFix(name, instanceType=None, difficulty=None):
    if difficulty == "Fatal" and instanceType == "ultimate" and "fatal" not in name.lower():
        name = f"{name} (fatal)"
    elif difficulty == "Episch" and instanceType == "raid" and "episch" not in name.lower():
        name = f"{name} (episch)"
    elif difficulty == "Episch" and instanceType == "feldexkursion" and "episch" not in name.lower():
        name = f"{name} (episch)"
    elif difficulty == "Schwer" and instanceType == "dungeon" and "schwer" not in name.lower():
        name = f"{name} (schwer)"
    # handle stupid edge cases for primals
    elif name in ["Königliche Konfrontation", "Jagd auf Rathalos"] and difficulty.lower() != "normal":
        name = f"{name} ({difficulty.lower()})"
    elif name in ["Memoria Misera"] and difficulty.lower() != "normal":
        name = f"{name} ({difficulty.lower()})"
    elif name in ["Krieger des Lichts"] and difficulty.lower() == "extrem":
        name = f"{name} ({difficulty.lower()})"
    # handle edge cases PvP
    elif "(Flechtenhain)" in name:
        name = name.replace("(Flechtenhain)", "")
    elif "(Kampfplatz)" in name:
        name = name.replace("(Kampfplatz)", "")
    # placeholder
    elif name == "":
        return ""
    # make sure brackets are always lowercase
    name = name.replace("(Fatal)", "(fatal)").replace("(Episch)", "(episch)").replace("(Schwer)", "(schwer)").replace("(Extrem)", "(extrem)")
    return name


def translateAttack(skill_id, _type=action):
    try:
        text = _type[str(int(skill_id, 16)) + ".0"]["Name_en"]
        return fixCaptilaziationAndRomanNumerals(text)
    except KeyError:
        return f"Unknown_{skill_id}"


def fixCaptilaziationAndRomanNumerals(text):
    text = text.title()
    text = re.sub(r" (Ii|Iii|IIi|Vi|Vii|Viii|Iv|Ix|Xi|Xii|Xiii|Xliii|Iii-E|Xxiv|013Bl|Xii\.)\. ", lambda x:  x.group(0).upper(), text)
    text = re.sub(r" (Ii|Iii|IIi|Vi|Vii|Viii|Iv|Ix|Xi|Xii|Xiii|Xliii|Iii-E|Xxiv|013Bl|Xii\.)$", lambda x:  x.group(0).upper(), text)
    text = re.sub(r" (Ii) ", lambda x:  x.group(0).upper(), text)
    text = re.sub(r"('[a-zA-Z])(?! )", lambda x:  x.group(0).upper(), text)
    return text


def replaceSlug(text):
    return str(text).replace(",", "").replace("'", "").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue").replace("ß", "ss")


def getImage(image):
    image = image.replace(".tex", "_hr1.png\"")
    return image


def get_video_url(url):
    if url.startswith("https"):
        return url
    return "https://www.youtube.com/watch?v={}".format(url)


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


def clean_entries_from_single_quotes(_entry):
    for key, value in _entry.items():
        if value.startswith("'"):
            _entry[key] = value[1:]
        if value.endswith("'"):
            _entry[key] = value[:-1]
    return _entry


def seperate_data_into_array(tag, _entry):
    if _entry[tag]:
        _entry[tag] = _entry[tag].strip("'[").strip("]'").strip("\"[").strip("]\"").strip("[").strip("]").replace("\", \"", "', '").replace("\",\"", "', '").split("', '")
        _entry[tag] = [b for b in _entry[tag]]


def try_to_create_file(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


# returns existing boss data if available
def get_old_content_if_file_is_found(_existing_filename):
    if os.path.exists(_existing_filename):
        with open(_existing_filename, encoding="utf8") as f:
            docs = yaml.load_all(f, Loader=Loader)
            for doc in docs:
                return doc.get("bosses", None), doc.get("adds", None), doc.get("mechanics", "N/A"), doc.get("wip", None), True
    return None, None, "N/A", None, False


def read_xlsx_file():
    # open file, get sheet, last row and last coulmn
    wb = openpyxl.load_workbook('./guide_ffxiv.xlsx')
    sheet = wb['Tabelle1']
    max_row = sheet.max_row
    max_column = sheet.max_column
    return sheet, max_row, max_column


def get_data_from_xlsx(sheet, max_column, i):
    entry = {}
    # for every column in row add all elements into a dict:
    # max_column will ignore last column due to how range is working
    for j in range(1, max_column + 1):
        entry[elements[j - 1]] = str(sheet.cell(row=int(i), column=int(j)).value).replace("None", "")
    # fix fataler raid
    # if entry["instanceType"] == "fataler_raid":
    #     entry["instanceType"] = "raid"
    return entry


def cleanup_logdata(logdata_instance_content):
    try:
        del logdata_instance_content["combatants"]
    except Exception:
        pass
    try:
        del logdata_instance_content["zone"]
    except Exception:
        pass
    for enemy_name, enemy in logdata_instance_content.items():
        # try: del enemy["status"]
        # except Exception: pass
        try:
            del enemy["tether"]
        except Exception:
            pass
        try:
            del enemy["headmarker"]
        except Exception:
            pass
    new_lic = {}
    for k, v in logdata_instance_content.items():
        # if not k == "":
        new_lic[k] = v
    return new_lic


def compare_skill_ids(old_enemy_data, new_enemy_data, existing_attacks, remove_attack):
    for attack_id in new_enemy_data.get('skill', {}):
        for attack in old_enemy_data.get('attacks', []):
            existing_attacks[attack['title']] = attack['type']
            if attack_id == attack.get('title_id', None):
                remove_attack.append(attack_id)
            if attack.get("variation", None):
                for vari in attack.get("variation", None):
                    if attack_id == vari['title_id']:
                        remove_attack.append(attack_id)
    return existing_attacks, remove_attack


def compare_status_ids(old_enemy_data, new_enemy_data, existing_debuffs, remove_debuff):
    for debuff_id in new_enemy_data.get('status', {}):
        for debuff in old_enemy_data.get('debuffs', {}):
            existing_debuffs[debuff['title']] = ""
            if debuff_id == debuff.get('title_id', None):
                remove_debuff.append(debuff_id)
    return existing_debuffs, remove_debuff


def remove_skills_from_list_if_found(remove_attack, new_enemy_data):
    for x in remove_attack:
        try:
            del new_enemy_data["skill"][x]
        except Exception:
            pass
    return new_enemy_data


def remove_status_from_list_if_found(remove_debuff, new_enemy_data):
    for x in remove_debuff:
        try:
            del new_enemy_data["status"][x]
        except Exception:
            pass
    return new_enemy_data


def get_fixed_status_description(_id):
    try:
        description = status[str(int(_id, 16)) + ".0"]['Description_de']
        description = re.sub('<UIForeground>[0-9A-F]{1,6}</UIForeground>', '', description)
        description = re.sub('<UIGlow>[0-9A-F]{1,6}</UIGlow>', '', description)
        return description
    except KeyError:
        return f"Unknown_{_id}"


def delete_invalid_entries(tmp_attack):
    try:
        del tmp_attack['title_id']
    except Exception:
        pass
    try:
        del tmp_attack['damage_type']
    except Exception:
        pass
    try:
        del tmp_attack['roles']
    except Exception:
        pass
    try:
        del tmp_attack['tags']
    except Exception:
        pass
    return tmp_attack


def sort_list_of_skills(data):
    if data.get('attacks', None):
        data['attacks'] = sorted(data['attacks'], key=itemgetter('title'))
        unknown_attacks = []
        known_attacks = []
        for attack in data['attacks']:
            if attack['title'].startswith("Unknown_"):
                unknown_attacks.append(attack)
            else:
                known_attacks.append(attack)
        data['attacks'] = unknown_attacks + known_attacks
    return data


def merge_attacks(old_enemy_data, new_enemy_data, enemy_type):
    remove_attack = []
    existing_attacks = {}
    # comapre all skill ids
    existing_attacks, remove_attack = compare_skill_ids(old_enemy_data, new_enemy_data, existing_attacks, remove_attack)
    # remove skill ids if they were found before
    new_enemy_data = remove_skills_from_list_if_found(remove_attack, new_enemy_data)

    old_enemy_data = sort_list_of_skills(old_enemy_data)
    if not new_enemy_data.get('skill', None):
        return old_enemy_data
    # merge new keys
    for attack_id, attack in new_enemy_data['skill'].items():
        if attack["name"] == "":
            attack["name"] = "Unknown_" + attack_id
        if existing_attacks.get(attack['name'], None):
            # convert regular attk to variation
            if existing_attacks[attack['name']] == "regular":
                print_color_blue(f"\t\tNeed to convert: {attack['name']} ({attack_id})", disable_blue_print)
                # find attack
                attack_index = None
                for i, old_attack in enumerate(old_enemy_data['attacks']):
                    if old_attack.get('title', None) == attack['name']:
                        attack_index = i
                        break
                tmp_attack = old_enemy_data['attacks'][attack_index]
                tmp_attack['type'] = "variation"
                tmp_attack['notes'] = [{'note': 'Variation-note BIG'}]
                tmp = {
                    'title': tmp_attack['title'],
                    'title_id': tmp_attack['title_id'],
                    'damage_type': tmp_attack['damage_type']
                }
                if tmp_attack['title'] == "Attacke":
                    tmp['disable'] = 'false'
                if tmp_attack.get('damage', None):
                    tmp["damage"] = {}
                    tmp["damage"]["min"] = tmp_attack['damage']['min']
                    tmp["damage"]["max"] = tmp_attack['damage']['max']
                if tmp_attack.get('roles', None):
                    tmp['roles'] = list(tmp_attack.get('roles', None))
                    if tmp['roles'][0]['role'] == "role":
                        tmp['roles'][0]['role'] = "Variation-role 1"
                if tmp_attack.get('tags', None):
                    tmp['tags'] = list(tmp_attack.get('tags', None))
                    if tmp['tags'][0]['tag'] == "tag":
                        tmp['tags'][0]['tag'] = "Variation-tag 1"
                if tmp_attack.get('notes', None):
                    tmp['notes'] = [{'note': 'Variation-note BIG'}]
                    if tmp_attack['notes'][0]['note'] == "Variation-note BIG":
                        tmp['notes'][0]['note'] = "Variation-note 1"
                tmp_attack['variation'] = [tmp]

                # add new attack
                tmp2 = {
                    'title': attack['name'],
                    'title_id': attack_id,
                    'damage_type': attack['damage_type'],
                }
                if tmp_attack.get('damage', None):
                    tmp2["damage"] = {}
                    tmp2["damage"]["min"] = tmp_attack['damage']['min']
                    tmp2["damage"]["max"] = tmp_attack['damage']['max']
                if tmp_attack.get('roles', None):
                    tmp2['roles'] = list(tmp_attack.get('roles', None))
                    if tmp2['roles'][0]['role'] == "role":
                        tmp2['roles'][0]['role'] = "Variation-role 1"
                if tmp_attack.get('tags', None):
                    tmp2['tags'] = list(tmp_attack.get('tags', None))
                    if tmp2['tags'][0]['tag'] == "tag":
                        tmp2['tags'][0]['tag'] = "Variation-tag 1"
                if tmp_attack.get('notes', None):
                    tmp2['notes'] = [{'note': 'Variation-note BIG'}]
                    if tmp_attack['notes'][0]['note'] == "Variation-note BIG":
                        tmp2['notes'][0]['note'] = "Variation-note 1"
                tmp_attack['variation'].append(tmp2)

                # delete old invalid entries
                tmp_attack = delete_invalid_entries(tmp_attack)
                existing_attacks[attack['name']] = 'variation'
            else:
                print_color_blue("\t\tNeed to add to variation: " + attack['name'], disable_blue_print)
                # find attack
                attack_index = None
                for i, old_attack in enumerate(old_enemy_data['attacks']):
                    if old_attack.get('title', None) == attack['name']:
                        attack_index = i
                        break
                tmp_attack = old_enemy_data['attacks'][attack_index]
                # add new attack
                tmp = {
                    'title': attack['name'],
                    'title_id': attack_id,
                    'damage_type': attack['damage_type']
                }
                if tmp_attack['variation'][0].get('damage', None) or tmp_attack.get('damage', None):
                    tmp["damage"] = {}
                    tmp["damage"]["min"] = tmp_attack['variation'][0].get('damage', {}).get('min', None) or tmp_attack.get('damage', {}).get('min', None)
                    tmp["damage"]["max"] = tmp_attack['variation'][0].get('damage', {}).get('max', None) or tmp_attack.get('damage', {}).get('max', None)
                if tmp_attack['variation'][0].get('roles', None) or tmp_attack.get('roles', None):
                    tmp['roles'] = tmp_attack['variation'][0].get('roles', None) or tmp_attack.get('roles', None)
                if tmp_attack['variation'][0].get('tags', None) or tmp_attack.get('tags', None):
                    tmp['tags'] = tmp_attack['variation'][0].get('tags', None) or tmp_attack.get('tags', None)
                if tmp_attack['variation'][0].get('notes', None) or tmp_attack.get('notes', None):
                    tmp['notes'] = tmp_attack['variation'][0].get('notes', None) or tmp_attack.get('notes', None)
                tmp_attack['variation'].append(tmp)
        else:
            print_color_blue("\t\tAdded new entry for regular: " + attack['name'], disable_blue_print)
            # create new regular
            tmp = {
                'title': attack['name'],
                'title_id': attack_id,
                'title_en': translateAttack(attack_id),
                'attack_in_use': 'false',
                'disable': 'false',
                'type': 'regular',
                'damage_type': attack['damage_type'],
                'phases': [{'phase': '09'}],
                'roles': [{'role': 'role'}],
                'tags': [{'tag': 'tag'}],
                'notes': [{'note': 'note'}]
            }
            if attack.get('damage', None):
                tmp["damage"] = {}
                tmp["damage"]["min"] = attack['damage']['min']
                tmp["damage"]["max"] = attack['damage']['max']

            if tmp['title'] == "Attacke":
                tmp['attack_in_use'] = 'true'
                tmp['disable'] = 'true'
                tmp['roles'][0]['role'] = 'Tank'
                tmp['tags'][0]['tag'] = 'Auto-Angriff'
                del tmp['notes']

            if tmp['title'].startswith("Unknown_"):
                tmp['disable'] = 'true'

            if enemy_type == "adds" and tmp.get("notes", None):
                del tmp['notes']
            if old_enemy_data.get('attacks', []) == []:
                old_enemy_data['attacks'] = []
            old_enemy_data['attacks'].append(tmp)

            existing_attacks[attack['name']] = 'regular'

    old_enemy_data = sort_list_of_skills(old_enemy_data)
    return old_enemy_data


def addknowndebuff(status_id, status_data):
    tmp_status = {
        'title': fixCaptilaziationAndRomanNumerals(status_data['name']),
        'title_id': status_id,
        'title_en': translateAttack(status_id, _type=status),
        'icon': status_data['icon'],
        'description': get_fixed_status_description(status_id),
        'debuff_in_use': 'true',
        'disable': 'false',
        #'damage_type': status_data['damage_type'],
        'phases': [{'phase': '09'}],
        'roles': [{'role': 'Alle'}],
        'tags': [{'tag': 'Common'}],
    }
    return tmp_status


def merge_debuffs(old_enemy_data, new_enemy_data, enemy_type, saved_used_skills_to_ignore_in_last):
    remove_attack = []
    existing_debuffs = {}
    ignore_debuffs = ['130', '13d']
    obviouse_debuffs = ['82b', '82a', '82c', '9d4', '9d7', '95', '12', '38e', '828', '0e', '113', '06', '07', '01', '11', '282', 'ca', '11', '196', '1b6', '23c', '']
    # filter duplicate debuffs
    tmp_debuffs = []
    tmp_debuff_ids = []
    disable_yellow_print = False
    for x in old_enemy_data.get("debuffs", []):
        if x['title_id'] not in tmp_debuff_ids and x['title_id'] not in ignore_debuffs:
            saved_used_skills_to_ignore_in_last.append(x['title_id'])
            tmp_debuff_ids.append(x['title_id'])
            tmp_debuffs.append(x)
        else:
            print_color_yellow(f"Ignore Duplicate Debuff {x['title']}")
    disable_yellow_print = True
    old_enemy_data["debuffs"] = tmp_debuffs

    if not new_enemy_data.get('title', "") == 'Unbekannte Herkunft':
        # remove debuffs already manually adjusted
        for debuff in saved_used_skills_to_ignore_in_last:
            try:
                del new_enemy_data.get("status", {})[debuff]
            except Exception:
                pass
        # comapre all skill ids
        existing_debuffs, remove_attack = compare_status_ids(old_enemy_data, new_enemy_data, existing_debuffs, remove_attack)
        # remove skill ids if they were found before
        new_enemy_data = remove_status_from_list_if_found(remove_attack, new_enemy_data)
    # comapre all skill ids
    existing_debuffs, remove_attack = compare_status_ids(old_enemy_data, new_enemy_data, existing_debuffs, remove_attack)
    # remove skill ids if they were found before
    new_enemy_data = remove_status_from_list_if_found(remove_attack, new_enemy_data)

    # merge new keys
    if not old_enemy_data.get('debuffs', None):
        old_enemy_data['debuffs'] = []
    else:
        old_enemy_data['debuffs'] = sorted(old_enemy_data['debuffs'], key=itemgetter('title'))

    if not new_enemy_data.get('status', None):
        return old_enemy_data, saved_used_skills_to_ignore_in_last

    # get only status to make sorting easier
    new_enemy_data_status = new_enemy_data.get('status', {})

    # sort after the name key in subdicts
    new_enemy_data_status = collections.OrderedDict(sorted(new_enemy_data_status.items(), key=lambda x: x[1]['name']))

    for status_id, status_data in new_enemy_data_status.items():
        if status_data['name'] == "":
            continue
        if status_id in obviouse_debuffs:
            tmp_status = addknowndebuff(status_id, status_data)
        else:
            tmp_status = {
                'title': fixCaptilaziationAndRomanNumerals(status_data['name']),
                'title_id': status_id,
                'title_en': translateAttack(status_id, _type=status),
                'icon': status_data['icon'],
                'description': get_fixed_status_description(status_id),
                'debuff_in_use': 'false',
                'disable': 'false',
                #'damage_type': status_data['damage_type'],
                'phases': [{'phase': '09'}],
                'roles': [{'role': 'role'}],
                'tags': [{'tag': 'tag'}],
                'notes': [{'note': 'note'}]
            }
            if status_data.get('duration', None):
                tmp_status["durations"] = status_data['duration']
        old_enemy_data['debuffs'].append(tmp_status)
    old_enemy_data['debuffs'] = sorted(old_enemy_data['debuffs'], key=itemgetter('title'))
    return old_enemy_data, saved_used_skills_to_ignore_in_last


#####################################################################################################################################################

def check_Mechanics(_entry, guide_data, _old_mechanics="N/A"):
    # this contruct looks ugly but it forbidds the recreation of empty mechanics
    if not _old_mechanics == "N/A":
        guide_data += "mechanics:\n"
        if _old_mechanics:
            for mechanic in _old_mechanics:
                guide_data = add_Mechanic(guide_data, mechanic)
    elif _entry["mechanics"] != "":
        guide_data += "mechanics:\n"
        mechanics = _entry["mechanics"].strip("\"[").strip("]\"").split("\",\"")
        counter = 1
        for m in mechanics:
            mechanic = {
                "steps": [{
                    "step": "09",
                    "notes": [{"note": f"Mechanics-note {counter}", }],
                    "images": [{"url": "/assets/img/test.jpg", "alt": "/assets/img/test.jpg", "height": "250px", }],
                    "videos": [{"url": "https&#58;//akurosia.de/upload/test.mp4", }],
                }],
            }
            if mechanics == ['']:
                mechanic['title'] = f"Mechanic-Title {counter}"
            else:
                mechanic['title'] = m

            guide_data = add_Mechanic(guide_data, mechanic)
            counter += 1
    return guide_data


def ugly_fix_enemy_data(enemy_data, new_enemy_data):
    for attack in enemy_data.get('attacks', []):
        if attack['type'] in ["variation", "combo"]:
            for action in attack[attack['type']]:
                if new_enemy_data.get("skill", {}).get(action["title_id"], None):
                    x = new_enemy_data.get("skill", {}).get(action["title_id"], {})
                    if x.get("damage", {}).get("min", None) or x.get("damage", {}).get("max", None):
                        action['damage'] = {}
                        action['damage']['min'] = x.get("damage", {}).get("min", None)
                        action['damage']['max'] = x.get("damage", {}).get("max", None)
        elif attack['type'] == "regular":
            if new_enemy_data.get("skill", {}).get(attack["title_id"], None):
                x = new_enemy_data.get("skill", {}).get(attack["title_id"], {})
                if x.get("damage", {}).get("min", None) or x.get("damage", {}).get("max", None):
                    attack['damage'] = {}
                    attack['damage']['min'] = x.get("damage", {}).get("min", None)
                    attack['damage']['max'] = x.get("damage", {}).get("max", None)
    return enemy_data


def check_Enemy(_entry, guide_data, enemy_type, enemy_text, logdata_instance_content,  _old_enemy=None):
    if _old_enemy or logdata != {}:
        guide_data += f"{enemy_text}:\n"

    empty_enemy_available = False
    if _old_enemy:
        # sort old enemies
        final_old_enemy = []

        # do this only for bosses
        if _entry.get(enemy_type, None) and enemy_type == "bosse":
            for enemy in _entry[enemy_type]:
                for old_enemy_data in _old_enemy:
                    if old_enemy_data['title'].lower() == enemy.lower():
                        final_old_enemy.append(old_enemy_data)
        # if you created a new order, apply it
        if not final_old_enemy == []:
            _old_enemy = final_old_enemy

        saved_used_skills_to_ignore_in_last = []
        for i, old_enemy_data in enumerate(_old_enemy):
            if old_enemy_data['title'] == "":
                continue
            elif old_enemy_data['title'] == "Unbekannte Herkunft":
                empty_enemy_available = True

            old_enemy_data['title'] = old_enemy_data['title'].replace("&#246;", "ö").replace("&#252;", "ü").replace("&#228;", "ä").replace("&#223;", "ß")
            print_color_yellow(f"\tWork on '{old_enemy_data['title']}'", disable_yellow_print)
            empty_enemy_data = {}
            try:
                new_enemy_data = logdata_instance_content[old_enemy_data['title']]
                if enemy_type == 'bosse' and len(_old_enemy) == i + 1:
                    empty_enemy_data = logdata_instance_content['']
            except Exception:
                new_enemy_data = {}
            new_enemy_data_c = copy.deepcopy({**{}, **new_enemy_data})

            # get enemy attacks and debuffs for all enemies with a name
            old_enemy_data["enemy_id"] = new_enemy_data.get("id", "")

            if new_enemy_data.get("minHP", None) or new_enemy_data.get("maxHP", None):
                old_enemy_data["hp"] = {}
                old_enemy_data["hp"]["min"] = new_enemy_data.get("minHP", "")
                old_enemy_data["hp"]["max"] = new_enemy_data.get("maxHP", "")

            old_enemy_data = merge_attacks(old_enemy_data, new_enemy_data, enemy_type)
            old_enemy_data, saved_used_skills_to_ignore_in_last = merge_debuffs(old_enemy_data, new_enemy_data, enemy_type, saved_used_skills_to_ignore_in_last)

            guide_data = add_Enemy(guide_data, old_enemy_data, enemy_type, new_enemy_data_c)
            try:
                del logdata_instance_content[old_enemy_data['title']]
            except Exception:
                pass

            # handle enemy if name is ""
            if not empty_enemy_data == {}:
                empty_enemy_available = True
                base_data = {'title': 'Unbekannte Herkunft', 'title_en': 'Unknown Source', 'id': f"boss0{i+2}", "sequence": [{"phase": "09"}], 'debuffs': []}
                old_enemy_data = {'title': 'Unbekannte Herkunft', 'title_en': 'Unknown Source', 'id': f"boss0{i+2}", "sequence": [{"phase": "09"}], 'debuffs': []}
                old_enemy_data = merge_attacks(old_enemy_data, empty_enemy_data, enemy_type)
                old_enemy_data, saved_used_skills_to_ignore_in_last = merge_debuffs(old_enemy_data, empty_enemy_data, enemy_type, saved_used_skills_to_ignore_in_last)

                if not old_enemy_data == base_data:
                    guide_data = add_Enemy(guide_data, old_enemy_data, enemy_type, new_enemy_data_c)
    if logdata_instance_content != {}:
        counter = 0
        if logdata_instance_content is None:
            return guide_data

        empty_enemy = None
        for i, enemy in enumerate(logdata_instance_content, 1):
            if enemy == "" and enemy_type == 'adds':
                continue
            print_color_yellow(f"\tWork on '{enemy}'", disable_yellow_print)
            # for bosses, only write bosses, for adds skip bosse
            lower_enemy_list = [x.lower() for x in _entry[enemy_type]]
            lower_boss_list = [x.lower() for x in _entry['bosse']]
            lower_enemy_list.append("")
            if (enemy_type == 'bosse' and enemy.lower() not in lower_enemy_list) or (enemy_type == 'adds' and enemy.lower() in lower_boss_list):
                continue
            counter = counter + 1
            new_enemy_data = logdata_instance_content.get(enemy, "Unknown_")
            if new_enemy_data == {}:
                new_enemy_data = {'skill': {}}
            new_enemy_data_c = copy.deepcopy({**{}, **new_enemy_data})
            # create new template file to merge against
            enemy_id = new_enemy_data.get("id", "")
            tmp = {
                "title": enemy if enemy != "" else "Unbekannte Herkunft",
                "title_en": getBnpcName(enemy, enemy_id) if enemy != "" else "Unknown Source",
                "enemy_id": enemy_id,
                "id": f"{enemy_type[:-1]}{counter:02d}",
                "attacks": [],
                "debuffs": []
            }

            if new_enemy_data.get("minHP", None) or new_enemy_data.get("maxHP", None):
                tmp["hp"] = {}
                tmp["hp"]["min"] = new_enemy_data.get("minHP", "")
                tmp["hp"]["max"] = new_enemy_data.get("maxHP", "")

            enemy_data = merge_attacks(tmp, new_enemy_data, enemy_type)
            enemy_data['attacks'] = sorted(enemy_data['attacks'], key=itemgetter('title'))

            enemy_data, saved_used_skills_to_ignore_in_last = merge_debuffs(tmp, new_enemy_data, enemy_type, [])
            enemy_data['debuffs'] = sorted(enemy_data['debuffs'], key=itemgetter('title'))
            if enemy == "":
                empty_enemy = enemy_data
            else:
                guide_data = add_Enemy(guide_data, enemy_data, enemy_type, new_enemy_data_c)

        if empty_enemy and not empty_enemy_available:
            if empty_enemy.get("attacks", None) or empty_enemy.get("debuffs", None):
                guide_data = add_Enemy(guide_data, empty_enemy, "bosse", new_enemy_data_c)
    return guide_data


# Notizen, Bosse und Adds
def addGuide(_entry, _old_bosses, _old_adds, _old_mechanics):
    guide_data = ""
    logdata_instance_content = None
    # add mechanics
    guide_data = check_Mechanics(_entry, guide_data, _old_mechanics)

    # get correct title capitalization to read data from logdata
    title = uglyContentNameFix(_entry["title_de"].title(), _entry["instanceType"], _entry["difficulty"])
    # get the latest data from logdata
    if not _entry["title_de"] == "" and logdata_lower.get(_entry["title_de"].lower()):
        try:
            logdata_instance_content = dict(logdata[getContentName(title, lang="de")])
        except Exception:
            logdata_instance_content = dict(logdata[title])
        logdata_instance_content = cleanup_logdata(logdata_instance_content)
    print_color_green(f"Work on '{_entry['title_de']}'", disable_green_print)
    guide_data = check_Enemy(_entry, guide_data, "bosse", "bosses", logdata_instance_content, _old_bosses)
    guide_data = check_Enemy(_entry, guide_data, "adds", "adds", logdata_instance_content, _old_adds)
    #guide_data = check_Enemy(_entry, guide_data, "adds", _old_adds)
    return guide_data


def write_content_to_file(_entry, _filename, _old_bosses, _old_adds, _old_mechanics, old_wip, index):
    seperate_data_into_array("bosse", _entry)
    seperate_data_into_array("adds", _entry)
    seperate_data_into_array("tags", _entry)
    header_data = rewrite_content_even_if_exists(_entry, old_wip, index)
    guide_data = addGuide(_entry, _old_bosses, _old_adds, _old_mechanics)
    #print_color_blue(guide_data, disable_blue_print)

    with open(_filename, "w", encoding="utf8") as fi:
        fi.write('---\n')
        fi.write(header_data)
        fi.write(guide_data)
        fi.write('---')
        fi.write('\n')


def rewrite_content_even_if_exists(_entry, old_wip, index):
    header_data = ""
    tt_type_name = get_territorytype_from_mapid(_entry["mapid"])
    _entry["title_de"] = getContentName(_entry["title"], "de", _entry["difficulty"], _entry["instanceType"])
    _entry["title_en"] = getContentName(_entry["title"], "en", _entry["difficulty"], _entry["instanceType"])

    if old_wip in ["True", "False"]:
        header_data += 'wip: "' + str(old_wip).title() + '"\n'
    else:
        header_data += 'wip: "True"\n'
    header_data += 'title: "' + _entry["title"] + '"\n'
    header_data += 'title_de: "' + _entry["title_de"] + '"\n'
    header_data += 'title_en: "' + _entry["title_en"] + '"\n'
    header_data += 'layout: guide_post\n'
    header_data += 'page_type: guide\n'
    header_data += f'excel_line: \"{index}\"\n'
    header_data += 'categories: "' + _entry["categories"] + '"\n'
    header_data += 'patchNumber: "' + _entry["patchNumber"].replace("'", "") + '"\n'
    header_data += 'difficulty: "' + _entry["difficulty"] + '"\n'
    header_data += 'instanceType: "' + _entry["instanceType"] + '"\n'
    header_data += 'date: "' + _entry["date"] + '"\n'
    header_data += 'slug: "' + replaceSlug(_entry["slug"]) + '"\n'
    if _entry["image"]:
        header_data += 'image:\n'
        header_data += '    - urlSmall: \"https://ffxiv.akurosia.de/extras/images/' + getImage(_entry["image"]) + '\n'
        header_data += '    - url: \"https://ffxiv.akurosia.de/extras/images/' + getImage(_entry["image"]) + '\n'
    header_data += 'terms:\n'
    header_data = writeTags(header_data, _entry, tt_type_name)
    header_data += 'patchName: "' + _entry["patchName"] + '"\n'
    header_data += 'mapid: "' + _entry["mapid"] + '"\n'
    header_data += 'contentname: "' + tt_type_name["Name_de"] + '"\n'
    header_data += 'sortid: ' + _entry["sortid"] + '\n'
    header_data += 'plvl: ' + _entry["plvl"] + '\n'
    header_data += 'plvl_sync: ' + _entry["plvl_sync"] + '\n'
    header_data += 'ilvl: ' + _entry["ilvl"] + '\n'
    header_data += 'ilvl_sync: ' + _entry["ilvl_sync"] + '\n'
    if not _entry["quest"] == "":
        header_data += 'quest: "' + _entry["quest"] + '"\n'
    if not _entry["quest_location"] == "":
        header_data += 'quest_location: "' + _entry["quest_location"] + '"\n'
    if not _entry["quest_npc"] == "":
        header_data += 'quest_npc: "' + _entry["quest_npc"] + '"\n'
    header_data += 'order: ' + get_order_id(_entry) + '\n'
    # mounts
    if checkVariable(_entry, "mount1") or checkVariable(_entry, "mount2"):
        header_data += 'mount:\n'
        if checkVariable(_entry, "mount1"):
            header_data += '    - name: "' + _entry["mount1"] + '"\n'
        if checkVariable(_entry, "mount2"):
            header_data += '    - name: "' + _entry["mount2"] + '"\n'
    # minions
    if checkVariable(_entry, "minion1") or checkVariable(_entry, "minion2") or checkVariable(_entry, "minion3"):
        header_data += 'minion:\n'
        if checkVariable(_entry, "minion1"):
            header_data += '    - name: "' + _entry["minion1"] + '"\n'
        if checkVariable(_entry, "minion2"):
            header_data += '    - name: "' + _entry["minion2"] + '"\n'
        if checkVariable(_entry, "minion3"):
            header_data += '    - name: "' + _entry["minion3"] + '"\n'
    # gearset_loot
    if checkVariable(_entry, "gearset_loot"):
        header_data += 'gearset_loot:\n'
        for gset in _entry["gearset_loot"] .split(","):
            header_data += '    - gsetname: "' + gset + '"\n'
    # tt_cards
    if checkVariable(_entry, "tt_card1") or checkVariable(_entry, "tt_card2"):
        header_data += 'tt_card:\n'
        if checkVariable(_entry, "tt_card1"):
            header_data += '    - name: "' + _entry["tt_card1"] + '"\n'
        if checkVariable(_entry, "tt_card2"):
            header_data += '    - name: "' + _entry["tt_card2"] + '"\n'
    # orchestrion
    if checkVariable(_entry, "orchestrion") or checkVariable(_entry, "orchestrion2") or checkVariable(_entry, "orchestrion3") or checkVariable(_entry, "orchestrion4") or checkVariable(_entry, "orchestrion5"):
        header_data += 'orchestrion:\n'
        if checkVariable(_entry, "orchestrion"):
            header_data += '    - name: "' + _entry["orchestrion"] + '"\n'
        if checkVariable(_entry, "orchestrion2"):
            header_data += '    - name: "' + _entry["orchestrion2"] + '"\n'
        if checkVariable(_entry, "orchestrion3"):
            header_data += '    - name: "' + _entry["orchestrion3"] + '"\n'
        if checkVariable(_entry, "orchestrion4"):
            header_data += '    - name: "' + _entry["orchestrion4"] + '"\n'
        if checkVariable(_entry, "orchestrion5"):
            header_data += '    - name: "' + _entry["orchestrion5"] + '"\n'
    # orchestrion material
    if checkVariable(_entry, "orchestrion_material1") or checkVariable(_entry, "orchestrion_material2") or checkVariable(_entry, "orchestrion_material3"):
        header_data += 'orchestrion_material:\n'
        if checkVariable(_entry, "orchestrion_material1"):
            header_data += '    - name: "' + _entry["orchestrion_material1"] + '"\n'
        if checkVariable(_entry, "orchestrion_material2"):
            header_data += '    - name: "' + _entry["orchestrion_material2"] + '"\n'
        if checkVariable(_entry, "orchestrion_material3"):
            header_data += '    - name: "' + _entry["orchestrion_material3"] + '"\n'
    # rouletts
    if _entry["allianceraid"] == "True" or _entry["frontier"] == "True" or _entry["expert"] == "True" or _entry["guildhest"] == "True" or _entry["level50_60"] == "True" or _entry["level70"] == "True" or _entry["leveling"] == "True" or _entry["main"] == "True" or _entry["mentor"] == "True" or _entry["normalraid"] == "True" or _entry["trial"] == "True":
        header_data += 'rouletts:\n'
        if _entry["allianceraid"]:
            header_data += '    - allianceraid: ' + _entry["allianceraid"] + "\n"
        if _entry["frontier"]:
            header_data += '      frontier: ' + _entry["frontier"] + "\n"
        if _entry["expert"]:
            header_data += '      expert: ' + _entry["expert"] + "\n"
        if _entry["guildhest"]:
            header_data += '      guildhest: ' + _entry["guildhest"] + "\n"
        if _entry["level50_60"]:
            header_data += '      level50_60: ' + _entry["level50_60"] + "\n"
        if _entry["level70"]:
            header_data += '      level70: ' + _entry["level70"] + "\n"
        if _entry["leveling"]:
            header_data += '      leveling: ' + _entry["leveling"] + "\n"
        if _entry["main"]:
            header_data += '      main: ' + _entry["main"] + "\n"
        if _entry["mentor"]:
            header_data += '      mentor: ' + _entry["mentor"] + "\n"
        if _entry["normalraid"]:
            header_data += '      normalraid: ' + _entry["normalraid"] + "\n"
        if _entry["trial"]:
            header_data += '      trial: ' + _entry["trial"] + "\n"
    # links:
    if checkVariable(_entry, "teamcraftlink") or checkVariable(_entry, "garlandtoolslink") or checkVariable(_entry, "gamerescapelink"):
        header_data += 'links:\n'
        first = "-"
        if checkVariable(_entry, "teamcraftlink"):
            header_data += f'    {first} teamcraftlink: "' + _entry["teamcraftlink"] + '"\n'
            first = " "
        if checkVariable(_entry, "garlandtoolslink"):
            header_data += f'    {first} garlandtoolslink: "' + _entry["garlandtoolslink"] + '"\n'
            first = " "
        if checkVariable(_entry, "gamerescapelink"):
            header_data += f'    {first} gamerescapelink: "' + _entry["gamerescapelink"] + '"\n'
    # videos
    if checkVariable(_entry, "mtqvid1"):
        header_data += 'mtq_vid1: "' + get_video_url(_entry["mtqvid1"]) + '"\n'
    if checkVariable(_entry, "mtqvid2"):
        header_data += 'mtq_vid2: "' + get_video_url(_entry["mtqvid2"]) + '"\n'
    if checkVariable(_entry, "mrhvid1"):
        header_data += 'mrh_vid1: "' + get_video_url(_entry["mrhvid1"]) + '"\n'
    if checkVariable(_entry, "mrhvid2"):
        header_data += 'mrh_vid2: "' + get_video_url(_entry["mrhvid2"]) + '"\n'
    return header_data


def writeTags(header_data, _entry, tt_type_name):
    # write tags per expansion
    if _entry["categories"] == "arr":
        header_data += "    - term: \"A Realm Reborn\"\n"
        header_data += "    - term: \"ARR\"\n"
    elif _entry["categories"] == "hw":
        header_data += "    - term: \"Heavensward\"\n"
        header_data += "    - term: \"HW\"\n"
    elif _entry["categories"] == "sb":
        header_data += "    - term: \"Stormblood\"\n"
        header_data += "    - term: \"SB\"\n"
    elif _entry["categories"] == "shb":
        header_data += "    - term: \"Shadowbringers\"\n"
        header_data += "    - term: \"ShB\"\n"
    else:
        pass

    for lang in ["de", "en", "fr", "ja", "cn", "ko"]:
        header_data += "    - term: \"" + tt_type_name["Name_" + lang] + "\"\n"

    #header_data += "    - term: \"" + _entry["title"] + "\"\n"
    for lang in ["de", "en", "fr", "ja", "cn", "ko"]:
        header_data += "    - term: \"" + getContentName(_entry["title"], lang, _entry["difficulty"], _entry["instanceType"]) + "\"\n"

    # write rest of the tags
    header_data += "    - term: \"" + _entry["difficulty"] + "\"\n"
    header_data += "    - term: \"" + _entry["patchNumber"] + "\"\n"
    header_data += "    - term: \"" + _entry["patchName"] + "\"\n"
    header_data += "    - term: \"" + _entry["quest"] + "\"\n"
    if checkVariable(_entry, "mount1") or checkVariable(_entry, "mount2"):
        header_data += "    - term: \"mounts\"\n"
    if checkVariable(_entry, "minion1") or checkVariable(_entry, "minion2") or checkVariable(_entry, "minion3"):
        header_data += "    - term: \"minions\"\n"
    if checkVariable(_entry, "tt_card1") or checkVariable(_entry, "tt_card2"):
        header_data += "    - term: \"tt_cards\"\n"
    if checkVariable(_entry, "gearset_loot"):
        for gset in _entry["gearset_loot"].split(","):
            header_data += "    - term: \"" + gset + "\"\n"
    if checkVariable(_entry, "orchestrion") or checkVariable(_entry, "orchestrion2") or checkVariable(_entry, "orchestrion3") or checkVariable(_entry, "orchestrion4") or checkVariable(_entry, "orchestrion5"):
        header_data += "    - term: \"orchestrion\"\n"
    if checkVariable(_entry, "orchestrion_material1") or checkVariable(_entry, "orchestrion_material2") or checkVariable(_entry, "orchestrion_material3"):
        header_data += "    - term: \"orchestrion_material\"\n"
    if _entry["instanceType"] == "trial":
        header_data += "    - term: \"" + "Prüfung" + "\"\n"
        header_data += "    - term: \"Trial\"\n"
        header_data += "    - term: \"Primae\"\n"
        header_data += "    - term: \"Primal\"\n"
    header_data += "    - term: \"" + _entry["instanceType"] + "\"\n"

    if not _entry["bosse"] == ['']:
        for b in _entry["bosse"]:
            if b != "Unknown_":
                header_data += "    - term: \"" + b + "\"\n"
    if not _entry["tags"] == ['']:
        for t in _entry["tags"]:
            if t != "Unknown_":
                header_data += "    - term: \"" + t + "\"\n"
    return header_data


def add_Mechanic(guide_data, data):
    guide_data += f"  - title: \"{data['title']}\"\n"
    if data.get("steps", None):
        guide_data += "    steps:\n"
        for step in data["steps"]:
            guide_data += f"      - step: \"{int(step['step']):02d}\"\n"

            if step.get("notes", None):
                guide_data += "        notes:\n"
                for note in step["notes"]:
                    guide_data += f"          - note: \"{note['note']}\"\n"

            if step.get("images", None):
                guide_data += "        images:\n"
                for image in step["images"]:
                    guide_data += f"          - url: \"{image['url']}\"\n"
                    guide_data += f"            alt: \"{image.get('alt', image['url'])}\"\n"
                    guide_data += f"            height: \"{image.get('height', '250px')}\"\n"

            if step.get("videos", None):
                guide_data += "        videos:\n"
                for video in step["videos"]:
                    guide_data += f"          - url: \"{video['url']}\"\n"
    return guide_data


def add_Enemy(guide_data, enemy_data, enemy_type, new_enemy_data):
    enemy_data = ugly_fix_enemy_data(enemy_data, new_enemy_data)
    guide_data += f'  - title: "{enemy_data["title"]}"\n'
    guide_data += f'    title_en: "{enemy_data["title_en"]}"\n'
    guide_data += f'    enemy_id: "{enemy_data.get("enemy_id", "")}"\n'
    guide_data += f'    id: "{enemy_data["id"]}"\n'

    if enemy_data.get('hp', None):
        guide_data += f'    hp:\n'
        guide_data += f'      - min: {enemy_data["hp"]["min"] or "None"}\n'
        guide_data += f'      - max: {enemy_data["hp"]["max"] or "None"}\n'
    if enemy_data.get("attacks", None):
        guide_data += '    attacks:\n'
        for attack in enemy_data["attacks"]:
            if attack["type"] == "regular":
                guide_data = add_regular_Attack(guide_data, attack, enemy_type)
            elif attack["type"] == "variation":
                guide_data = add_variation_Attack(guide_data, attack, enemy_type)
            elif attack["type"] == "combo":
                guide_data = add_combo_Attack(guide_data, attack, enemy_type)
    if enemy_data.get("debuffs", None):
        guide_data += '    debuffs:\n'
        for debuff in enemy_data["debuffs"]:
            guide_data = add_Debuff(guide_data, debuff, enemy_type)
    if enemy_data.get("sequence", None):
        guide_data = add_Sequence(guide_data, enemy_data)
    else:
        if enemy_type == "bosse":
            guide_data = add_Sequence(guide_data, example_sequence)
        else:
            guide_data = add_Sequence(guide_data, example_add_sequence)

    return guide_data


def add_Debuff(guide_data, debuff, enemy_type):
    guide_data += f'      - title: "{debuff["title"]}"\n'
    guide_data += f'        title_id: "{debuff["title_id"]}"\n'
    if debuff.get("title_en", None):
        guide_data += f'        title_en: "{debuff["title_en"]}"\n'
    guide_data += f'        icon: "{debuff["icon"]}"\n'
    guide_data += f'        description: "{debuff["description"]}"\n'
    if debuff.get("durations", None):
        guide_data += f'        durations: {debuff["durations"]}\n'
    guide_data += f'        debuff_in_use: "{debuff["debuff_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{debuff["disable"] or "false"}"\n'
    #guide_data += f'        damage_type: "{debuff["damage_type"] or "None"}"\n'

    if debuff.get('phases', None):
        guide_data += f'        phases:\n'
        for phase in debuff.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if debuff["title"].startswith("Unknown_"):
        return guide_data

    if debuff.get('roles', None):
        guide_data += f'        roles:\n'
        for role in debuff.get('roles', {}):
            guide_data += f'          - role: "{role["role"]}"\n'

    if debuff.get('tags', None):
        guide_data += f'        tags:\n'
        for tag in debuff.get('tags', {}):
            guide_data += f'          - tag: "{tag["tag"]}"\n'

    if debuff.get('notes', None):
        guide_data += f'        notes:\n'
        for note in debuff.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if debuff.get('videos', None):
        guide_data += f'        videos:\n'
        for video in debuff.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'
    return guide_data


def add_regular_Attack(guide_data, attack, enemy_type):
    guide_data += f'      - title: "{attack["title"]}"\n'
    guide_data += f'        title_id: "{attack["title_id"]}"\n'
    if attack.get("title_en", None):
        guide_data += f'        title_en: "{attack["title_en"]}"\n'
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack["disable"] or "false"}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'
    guide_data += f'        damage_type: "{attack["damage_type"] or "None"}"\n'

    if attack.get('damage', None):
        guide_data += f'        damage:\n'
        guide_data += f'          - min: {attack["damage"]["min"] or "None"}\n'
        guide_data += f'          - max: {attack["damage"]["max"] or "None"}\n'

    if attack.get('phases', None):
        guide_data += f'        phases:\n'
        for phase in attack.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if attack["title"].startswith("Unknown_"):
        return guide_data

    if attack.get('roles', None):
        guide_data += f'        roles:\n'
        for role in attack.get('roles', {}):
            guide_data += f'          - role: "{role["role"]}"\n'

    if attack.get('tags', None):
        guide_data += f'        tags:\n'
        for tag in attack.get('tags', {}):
            guide_data += f'          - tag: "{tag["tag"]}"\n'

    if attack.get('notes', None):
        guide_data += f'        notes:\n'
        for note in attack.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if attack.get('images', None):
        guide_data += f'        images:\n'
        for image in attack.get('images', {}):
            guide_data += f'          - url: "{image["url"]}"\n'
            guide_data += f'            alt: "{image.get("alt", None) or image["url"]}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += f'        videos:\n'
        for video in attack.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'
    return guide_data


def add_variation_Attack(guide_data, attack, enemy_type):
    guide_data += f'      - title: "{attack["title"]}"\n'
    if attack.get("title_en", None):
        guide_data += f'        title_en: "{attack["title_en"]}"\n'
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack["disable"] or "false"}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'

    if attack.get('phases', None):
        guide_data += f'        phases:\n'
        for phase in attack.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if (attack.get('notes', None) and enemy_type != "adds") or (attack.get('notes', None) and enemy_type == "adds" and attack.get('notes', [{}])[0].get("note", None) != "Variation-note BIG"):
        guide_data += f'        notes:\n'
        for note in attack.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if attack.get('variation', None):
        guide_data += f'        variation:\n'
        for variation in attack.get('variation', {}):
            guide_data += f'          - title: "{variation["title"]}"\n'
            guide_data += f'            title_id: "{variation["title_id"]}"\n'
            guide_data += f'            damage_type: "{variation["damage_type"]}"\n'

            # print_color_yellow(variation)
            if variation.get('damage', None):
                guide_data += f'            damage:\n'
                guide_data += f'              - min: {variation["damage"]["min"] or "None"}\n'
                guide_data += f'              - max: {variation["damage"]["max"] or "None"}\n'

            if variation.get('roles', None):
                guide_data += f'            roles:\n'
                for role in variation.get('roles', {}):
                    guide_data += f'              - role: "{role["role"]}"\n'

            if variation.get('tags', None):
                guide_data += f'            tags:\n'
                for tag in variation.get('tags', {}):
                    guide_data += f'              - tag: "{tag["tag"]}"\n'

            if variation.get('notes', None) and enemy_type != "adds":
                guide_data += f'            notes:\n'
                for note in variation.get('notes', {}):
                    guide_data += f'              - note: "{note["note"]}"\n'

    if attack.get('images', None):
        guide_data += f'        images:\n'
        for image in attack.get('images', {}):
            guide_data += f'          - url: "{image["url"]}"\n'
            guide_data += f'            alt: "{image.get("alt", None) or image["url"]}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += f'        videos:\n'
        for video in attack.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'

    return guide_data


def add_combo_Attack(guide_data, attack, enemy_type):
    guide_data += f'      - title: "{attack["title"]}"\n'
    if attack.get("title_en", None):
        guide_data += f'        title_en: "{attack["title_en"]}"\n'
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack["disable"] or "false"}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'

    if attack.get('phases', None):
        guide_data += f'        phases:\n'
        for phase in attack.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if (attack.get('notes', None) and enemy_type != "adds") or (attack.get('notes', None) and enemy_type == "adds" and attack.get('notes', [{}])[0].get("note", None) != "Variation-note BIG"):
        guide_data += f'        notes:\n'
        for note in attack.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if attack.get('combo', None):
        guide_data += f'        combo:\n'
        for combo in attack.get('combo', {}):
            guide_data += f'          - title: "{combo["title"]}"\n'
            guide_data += f'            title_id: "{combo["title_id"]}"\n'
            guide_data += f'            damage_type: "{combo["damage_type"]}"\n'

            if combo.get('damage', None):
                guide_data += f'            damage:\n'
                guide_data += f'              - min: {combo["damage"]["min"] or "None"}\n'
                guide_data += f'              - max: {combo["damage"]["max"] or "None"}\n'

            if combo.get('roles', None):
                guide_data += f'            roles:\n'
                for role in combo.get('roles', {}):
                    guide_data += f'              - role: "{role["role"]}"\n'

            if combo.get('tags', None):
                guide_data += f'            tags:\n'
                for tag in combo.get('tags', {}):
                    guide_data += f'              - tag: "{tag["tag"]}"\n'

            if combo.get('notes', None) and enemy_type != "adds":
                guide_data += f'            notes:\n'
                for note in combo.get('notes', {}):
                    guide_data += f'              - note: "{note["note"]}"\n'

    if attack.get('images', None):
        guide_data += f'        images:\n'
        for image in attack.get('images', {}):
            guide_data += f'          - url: "{image["url"]}"\n'
            guide_data += f'            alt: "{image.get("alt", None) or image["url"]}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += f'        videos:\n'
        for video in attack.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'

    return guide_data


def add_Sequence(guide_data, data):
    guide_data += "    sequence:\n"
    for phase in data['sequence']:
        guide_data += f"      - phase: \"{phase['phase']}\"\n"
        if phase.get('name', None):
            guide_data += f"        name: \"{phase['name']}\"\n"

        if phase.get('alerts', None):
            guide_data += "        alerts:\n"
            for alert in phase['alerts']:
                guide_data += f"          - alert: \"{alert['alert']}\"\n"

        if phase.get('toolbox', None):
            guide_data += "        toolbox:\n"
            for toolbox in phase['toolbox']:
                guide_data += f"          - link: \"{toolbox['link']}\"\n"
                guide_data += f"            name: \"{toolbox['name']}\"\n"

        if phase.get('mechanics', None):
            guide_data += "        mechanics:\n"
            for mechanic in phase['mechanics']:
                guide_data += f"          - title: \"{mechanic['title']}\"\n"
                if mechanic.get('notes', None):
                    guide_data += f"            notes:\n"
                    for note in mechanic['notes']:
                        guide_data += f"              - note: \"{note['note']}\"\n"

        if phase.get('attacks', None):
            guide_data += "        attacks:\n"
            for attack in phase['attacks']:
                guide_data += f"          - attack: \"{attack['attack']}\"\n"

        if phase.get('images', None):
            guide_data += "        images:\n"
            for image in phase['images']:
                guide_data += f"          - url: \"{image['url']}\"\n"
                guide_data += f"            alt: \"{image.get('alt', image['url'])}\"\n"
                guide_data += f"            height: \"{image.get('height', '250px')}\"\n"

        if phase.get('videos', None):
            guide_data += "        videos:\n"
            for video in phase['videos']:
                guide_data += f"          - url: \"{video['url']}\"\n"
    return guide_data


def run(sheet, max_row, max_column):
    # for every row do:
    for i in range(2, max_row):
        try:
            # comment the 2 line out to filter fo a specific line, numbering starts with 1 like it is in excel
            # if i not in [257]:
            #    continue
            entry = get_data_from_xlsx(sheet, max_column, i)
            # if the done collumn is not prefilled
            if entry["exclude"] == "end":
                print("END FLAG WAS FOUND!")
                sys.exit(0)
            if not (entry["exclude"] or entry["done"]):
                entry = clean_entries_from_single_quotes(entry)
                # remove time from excel datetime
                entry["date"] = str(entry["date"]).replace(" 00:00:00", "").replace("-", ".")
                # convert special chars for html usage
                entry["title"] = entry["title"]
                filename = f"{entry['categories']}_new/{entry['instanceType']}/{entry['date'].replace('.', '-')}--{entry['patchNumber']}--{entry['sortid'].zfill(5)}--{entry['slug'].replace(',', '')}.md"
                existing_filename = f"{entry['categories']}/{entry['instanceType']}/{entry['date'].replace('.', '-')}--{entry['patchNumber']}--{entry['sortid'].zfill(5)}--{entry['slug'].replace(',', '')}.md"
                old_bosses, old_adds, old_mechanics, old_wip, replace_existing_file = get_old_content_if_file_is_found(existing_filename)
                # if old file was found, replace filename to save
                if replace_existing_file:
                    filename = existing_filename

                try_to_create_file(filename)
                write_content_to_file(entry, filename, old_bosses, old_adds, old_mechanics, old_wip, i)
        except Exception:
            print_color_red(f"Error when handeling '{filename}'")
            traceback.print_exception(*sys.exc_info())


if __name__ == "__main__":
    sheet, max_row, max_column = read_xlsx_file()
    # change into _posts dir
    os.chdir("./_posts")
    # first run to create all files
    run(sheet, max_row, max_column)
    # second run to fix boss order
    #run(sheet, max_row, max_column)
