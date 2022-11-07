#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import re
import copy
from operator import itemgetter
from collections import OrderedDict
from ffxiv_aku import *
try:
    from python_scripts.constants import *
    from python_scripts.custom_logger import *
    from python_scripts.helper import *
except:
    from constants import *
    from custom_logger import *
    from helper import *


logger = getLogger()
storeFilesInTmp(False)
# storeFilesInTmp(True)
logdata = get_any_Logdata()
logdata_lower = dict((k.lower(), v) for k, v in logdata.items())
action = loadDataTheQuickestWay("action_all.json", translate=True)
bnpcname = loadDataTheQuickestWay("bnpcname_all.json", translate=True)
eobjname = loadDataTheQuickestWay("eobjname_all.json", translate=True)
status = loadDataTheQuickestWay("status_all.json", translate=True)
enpcresident = loadDataTheQuickestWay("enpcresident_all.json", translate=True)

disable_green_print = True
disable_yellow_print = True
disable_blue_print = True
disable_red_print = True


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


def check_Mechanics(entry, old_mechanics):
    guide_data = ""
    # this contruct looks ugly but it forbidds the recreation of empty mechanics
    if old_mechanics:
        guide_data += "mechanics:\n"
        if old_mechanics:
            for mechanic in old_mechanics:
                guide_data += add_Mechanic(mechanic)
    # if no old mechanics are found and excel contains [] it will create the example mechanic
    elif entry["mechanics"] != "":
        guide_data += "mechanics:\n"
        mechanics = entry["mechanics"].strip("\"[").strip("]\"").split("\",\"")
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

            guide_data += add_Mechanic(mechanic)
            counter += 1
    return guide_data


def add_Mechanic(data):
    guide_data = ""
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


def compare_skill_ids(old_enemy_data, new_enemy_data, existing_attacks, remove_attack):
    for new_attack_id, new_attack in new_enemy_data.get('skill', {}).items():
        for attack in old_enemy_data.get('attacks', []):
            # fix skill title if it has no translations
            if type(attack['title']) == str:
                _id = attack.get('title_id', None)
                if not attack.get('title_id', None):
                    if attack.get('variation', None):
                        _id = attack['variation'][0]['title_id']
                attack['title'] = addLanguageElements("action", _id, attack['title'])
            existing_attacks[attack['title']['de']] = attack['type']
            # add new filds to already existing data
            if new_attack['name'] == attack['title']['de']:
                attack['add_status'] = new_attack.get("add_status", []) + new_attack.get("add_status", [])
                attack['add_status'] = list(set(attack['add_status']))
            # add ids to remove_attack array
            if new_attack_id == attack.get('title_id', None):
                remove_attack.append(new_attack_id)
            if attack.get("variation", None):
                for vari in attack.get("variation", None):
                    if new_attack_id == vari['title_id']:
                        remove_attack.append(new_attack_id)
            # add status if available
            if new_attack_id == attack.get('title_id', None):
                handle_add_status(attack, new_attack)
    return existing_attacks, remove_attack


def handle_add_status(attack, new_attack):
    if attack.get("add_status", None):
        tmp = sorted(list(attack['add_status']))
        attack['add_status'] = []
        for s in tmp: 
            if isinstance(s, dict):
                attack['add_status'].append(s['status'])
            else:
                attack['add_status'].append(s)
                    
        for s in new_attack.get("add_status", []):
            if isinstance(s, str):
                attack['add_status'].append(s)
            else:
                attack['add_status'].append(s['status'])
        attack['add_status'] = sorted(list(set(attack['add_status'])))
    if new_attack.get("add_status", None):
        attack['add_status'] = new_attack['add_status']


def remove_skills_from_list_if_found(remove_attack, new_enemy_data):
    for x in remove_attack:
        try:
            del new_enemy_data["skill"][x]
        except Exception:
            pass
    return new_enemy_data


def addSortName(old_enemy_data, type_):
    if old_enemy_data.get(type_, None):
        for i, attack in enumerate(old_enemy_data[type_]):
            if not old_enemy_data[type_][i].get('sortname', None):
                if type(old_enemy_data[type_][i]['title']) == str:
                    x = "status"
                    if type_ == "attacks":
                        x = "action"
                    if not old_enemy_data[type_][i].get('title_id', None):
                        if old_enemy_data[type_][i].get('variation', None):
                            _id = old_enemy_data[type_][i]['variation'][0]['title_id']
                    else:
                        _id = old_enemy_data[type_][i]['title_id']
                    old_enemy_data[type_][i]['title'] = addLanguageElements(x, _id, old_enemy_data[type_][i]['title'])
                old_enemy_data[type_][i]['sortname'] = old_enemy_data[type_][i]['title']['de']
    return old_enemy_data


def sort_list_of_skills(data):
    if data.get('attacks', None):
        data['attacks'] = sorted(data['attacks'], key=itemgetter('sortname'))
        unknown_attacks = []
        known_attacks = []
        for attack in data['attacks']:
            if attack['title']['de'].startswith("Unknown_"):
                unknown_attacks.append(attack)
            else:
                known_attacks.append(attack)
        data['attacks'] = unknown_attacks + known_attacks
    return data


def translateAttack(skill_id, _type=action, lang="en"):
    try:
        text = _type[str(int(skill_id, 16))][f"Name_{lang}"]
        text = fixCaptilaziationAndRomanNumerals(text)
        if text == "":
            text = f"Unknown_{skill_id}"
        return text
    except KeyError:
        return f"Unknown_{skill_id}"


def fixCaptilaziationAndRomanNumerals(text):
    text = text.title()
    text = re.sub(r" (Ii|Iii|IIi|Vi|Vii|Viii|Iv|Ix|Xi|Xii|Xiii|Xliii|Iii-E|Xxiv|013Bl|Xii\.)\. ", lambda x:  x.group(0).upper(), text)
    text = re.sub(r" (Ii|Iii|IIi|Vi|Vii|Viii|Iv|Ix|Xi|Xii|Xiii|Xliii|Iii-E|Xxiv|013Bl|Xii\.)$", lambda x:  x.group(0).upper(), text)
    text = re.sub(r" (Ii) ", lambda x:  x.group(0).upper(), text)
    text = re.sub(r"('[a-zA-Z])(?! )", lambda x:  x.group(0).upper(), text)
    text = re.sub(r"('[a-zA-Z]) ", lambda x:  x.group(0).lower(), text)
    text = text.replace('"', r'\"')
    text = text.replace("&#246;", "ö").replace("&#252;", "ü").replace("&#228;", "ä").replace("&#223;", "ß")
    return text


def get_fixed_status_description(_id):
    try:
        description = {}
        for lang in LANGUAGES:
            tmp = status[str(int(_id, 16))][f'Description_{lang}']
            tmp = re.sub('<UIForeground>[0-9A-F]{1,6}</UIForeground>', '', tmp)
            tmp = re.sub('<UIGlow>[0-9A-F]{1,6}</UIGlow>', '', tmp)
            tmp = tmp.replace("\n\n", "<br>")
            tmp = tmp.replace("\n", "<br>")
            description[lang] = tmp
        return description
    except KeyError:
        return {"de": f"Unknown_{_id}"}


ids_to_replace = ["10742", "11399", "10744", "11402"]
def getBnpcNameFromID(_id, aname, nname, lang="en"):
    global ids_to_replace
    bnew_name = ""
    enew_name = ""
    ennew_name = ""
    if nname == "???":
        nname = "\?\?\?"
    if type(_id) == list:
        _id = _id[0]
    _id = str(_id)
    try:
        bnew_name = bnpcname[_id]["Singular_de"]
        if _id in ids_to_replace:
            nname = nname.replace(" ii", "").replace(" i", "")
        m = re.search(nname, bnew_name, re.IGNORECASE)
        n = re.search(aname, bnew_name, re.IGNORECASE)
        if m or n:
            return bnpcname[_id][f"Singular_{lang}"]
    except Exception:
        if nname == bnew_name or aname == bnew_name:
            return bnpcname[_id][f"Singular_{lang}"]

    try:
        enew_name = eobjname[_id]["Singular_de"]
        m = re.search(nname, enew_name, re.IGNORECASE)
        n = re.search(aname, enew_name, re.IGNORECASE)
        if m or n:
            return eobjname[_id][f"Singular_{lang}"]
    except Exception:
        if nname == enew_name or aname == enew_name:
            return eobjname[_id][f"Singular_{lang}"]

    try:
        ennew_name = enpcresident[_id]["Singular_de"]
        m = re.search(nname, ennew_name, re.IGNORECASE)
        n = re.search(aname, ennew_name, re.IGNORECASE)
        if m or n:
            return enpcresident[_id][f"Singular_{lang}"]
    except Exception:
        if nname == ennew_name or aname == ennew_name:
            return enpcresident[_id][f"Singular_{lang}"]

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
    nname = aname.replace("er ", r"(\[a\]|(e|es|er|en)) ").replace("es ", r"(\[a\]|(e|es|er|en)) ").replace("en ", r"(\[a\]|(e|es|er|en)) ").replace("e ", r"(\[a\]|(e|es|er|en)) ").replace("?", "\?")
    if nname.endswith("e"):
        nname = nname[:-1] + r"(\[a\]|(e|es|er|en))"
    elif nname.endswith("en") or nname.endswith("es") or nname.endswith("er"):
        nname = nname[:-2] + r"(\[a\]|(e|es|er|en))"

    if not _id == "":
        resultname = getBnpcNameFromID(_id, aname, nname, lang)
        if not resultname == "":
            return fixCaptilaziationAndRomanNumerals(resultname)
    # check results agains bnpcname
    if nname == "???":
        nname = "\?\?\?"
    for _, bnpc in bnpcname.items():
        m = re.search(nname, bnpc["Singular_de"].lower())
        if m:
            return fixCaptilaziationAndRomanNumerals(bnpc[f"Singular_{lang}"])

    # check results agains eobjname
    for _, eobj in eobjname.items():
        m = re.search(nname, eobj["Singular_de"].lower())
        if m:
            return fixCaptilaziationAndRomanNumerals(eobj[f"Singular_{lang}"])

    # check results agains eobjname
    for _, eobj in enpcresident.items():
        m = re.search(nname, eobj["Singular_de"].lower())
        if m:
            return fixCaptilaziationAndRomanNumerals(eobj[f"Singular_{lang}"])
    # return anything, just in case
    print_color_yellow(f"Missing {name} examples where ({aname}) and ({nname})", disable_yellow_print)
    return ""


def merge_attacks(old_enemy_data, new_enemy_data, enemy_type):
    remove_attack = []
    existing_attacks = {}
    # comapre all skill ids
    existing_attacks, remove_attack = compare_skill_ids(old_enemy_data, new_enemy_data, existing_attacks, remove_attack)
    #remove_attack = []
    # remove skill ids if they were found before
    new_enemy_data = remove_skills_from_list_if_found(remove_attack, new_enemy_data)

    old_enemy_data = addSortName(old_enemy_data, "attacks")
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
                x_attack_name = fixCaptilaziationAndRomanNumerals(attack['name'])
                for i, old_attack in enumerate(old_enemy_data['attacks']):
                    if old_attack.get('title', {}).get('de', None) == x_attack_name:
                        attack_index = i
                        break
                tmp_attack = old_enemy_data['attacks'][attack_index]
                tmp_attack['type'] = "variation"
                tmp_attack['notes'] = [{'note': 'Variation-note BIG'}]
                tmp = {
                    'title': {
                        'en': translateAttack(tmp_attack['title_id'], lang="en"),
                        'de': translateAttack(tmp_attack['title_id'], lang="de"),
                        'fr': translateAttack(tmp_attack['title_id'], lang="fr"),
                        'ja': translateAttack(tmp_attack['title_id'], lang="ja"),
                        'cn': translateAttack(tmp_attack['title_id'], lang="cn"),
                        'ko': translateAttack(tmp_attack['title_id'], lang="ko")
                    },
                    'title_id': tmp_attack['title_id'],
                    'damage_type': tmp_attack['damage_type'],
                    'add_status': tmp_attack.get("add_status", []),
                    'single_or_aoe': attack['type_id']
                }
                if tmp_attack['title'] == "Attacke":
                    tmp['disable'] = 'false'
                if tmp_attack.get('damage', None):
                    tmp["damage"] = {}
                    try:
                        tmp["damage"]["min"] = tmp_attack['damage']['min']
                        tmp["damage"]["max"] = tmp_attack['damage']['max']
                    except:
                        tmp["damage"]["min"] = tmp_attack['damage'][0]['min']
                        tmp["damage"]["max"] = tmp_attack['damage'][1]['max']
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
                    'title': {
                        'en': translateAttack(attack_id, lang="en"),
                        'de': translateAttack(attack_id, lang="de"),
                        'fr': translateAttack(attack_id, lang="fr"),
                        'ja': translateAttack(attack_id, lang="ja"),
                        'cn': translateAttack(attack_id, lang="cn"),
                        'ko': translateAttack(attack_id, lang="ko")
                    },
                    'title_id': attack_id,
                    'damage_type': attack['damage_type'],
                    'single_or_aoe': attack['type_id'],
                    'add_status': attack.get("add_status", [])
                }
                if tmp_attack.get('damage', None):
                    tmp2["damage"] = {}
                    try:
                        tmp2["damage"]["min"] = tmp_attack['damage']['min']
                        tmp2["damage"]["max"] = tmp_attack['damage']['max']
                    except:
                        tmp2["damage"]["min"] = tmp_attack['damage'][0]['min']
                        tmp2["damage"]["max"] = tmp_attack['damage'][1]['max']
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
            elif existing_attacks[attack['name']] == "variation":
                print_color_blue("\t\tNeed to add to variation: " + attack['name'], disable_blue_print)
                # find attack
                attack_index = None
                for i, old_attack in enumerate(old_enemy_data['attacks']):
                    if old_attack.get('title', {}).get('de', None) == attack['name']:
                        attack_index = i
                        break
                tmp_attack = old_enemy_data['attacks'][attack_index]
                # add new attack
                tmp = {
                    'title': {
                        'en': translateAttack(attack_id, lang="en"),
                        'de': translateAttack(attack_id, lang="de"),
                        'fr': translateAttack(attack_id, lang="fr"),
                        'ja': translateAttack(attack_id, lang="ja"),
                        'cn': translateAttack(attack_id, lang="cn"),
                        'ko': translateAttack(attack_id, lang="ko")
                    },
                    'title_id': attack_id,
                    'damage_type': attack['damage_type'],
                    'add_status': attack.get("add_status", []) + tmp_attack.get('add_status', []),
                    'single_or_aoe': attack['type_id']
                }
                if tmp_attack['variation'][0].get('damage', None) or tmp_attack.get('damage', None):
                    tmp["damage"] = {}
                    try:
                        tmp["damage"]["min"] = tmp_attack['variation'][0].get('damage', {}).get('min', None) or tmp_attack.get('damage', {}).get('min', None)
                        tmp["damage"]["max"] = tmp_attack['variation'][0].get('damage', {}).get('max', None) or tmp_attack.get('damage', {}).get('max', None)
                    except:
                        tmp["damage"]["min"] = tmp_attack['variation'][0].get('damage', {})[0].get('min', None) or tmp_attack.get('damage', {})[0].get('min', None)
                        tmp["damage"]["max"] = tmp_attack['variation'][0].get('damage', {})[1].get('max', None) or tmp_attack.get('damage', {})[1].get('max', None)
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
                'sortname': translateAttack(attack_id, lang="de"),
                'title': {
                    'en': translateAttack(attack_id, lang="en"),
                    'de': translateAttack(attack_id, lang="de"),
                    'fr': translateAttack(attack_id, lang="fr"),
                    'ja': translateAttack(attack_id, lang="ja"),
                    'cn': translateAttack(attack_id, lang="cn"),
                    'ko': translateAttack(attack_id, lang="ko")
                },
                'title_id': attack_id,
                'attack_in_use': 'false',
                'add_status': attack.get("add_status", []),
                'disable': 'false',
                'type': 'regular',
                'damage_type': attack['damage_type'],
                'phases': [{'phase': '09'}],
                'roles': [{'role': 'role'}],
                'tags': [{'tag': 'tag'}],
                'notes': [{'note': 'note'}],
                'single_or_aoe': attack['type_id']
            }
            if attack.get('damage', None):
                tmp["damage"] = {}
                tmp["damage"]["min"] = attack['damage']['min']
                tmp["damage"]["max"] = attack['damage']['max']

            if tmp['title']['de'] == "Attacke":
                tmp['attack_in_use'] = 'true'
                tmp['disable'] = 'true'
                tmp['roles'][0]['role'] = 'Tank'
                tmp['tags'][0]['tag'] = 'Auto-Angriff'
                del tmp['notes']

            if tmp['title']['de'].startswith("Unknown_"):
                tmp['disable'] = 'true'

            if enemy_type == "adds" and tmp.get("notes", None):
                del tmp['notes']
            if old_enemy_data.get('attacks', []) == []:
                old_enemy_data['attacks'] = []
            old_enemy_data['attacks'].append(tmp)

            existing_attacks[attack['name']] = 'regular'

    old_enemy_data = sort_list_of_skills(old_enemy_data)
    return old_enemy_data


def compare_status_ids(old_enemy_data, new_enemy_data, existing_debuffs, remove_debuff):
    for debuff_id in new_enemy_data.get('status', {}):
        for debuff in old_enemy_data.get('debuffs', {}):
            if type(debuff['title']) == str:
                debuff['title'] = addLanguageElements("status", debuff.get('title_id', None), debuff['title'])
            existing_debuffs[debuff['title']['de']] = ""
            if debuff_id == debuff.get('title_id', None):
                remove_debuff.append(debuff_id)
    return existing_debuffs, remove_debuff


def remove_status_from_list_if_found(remove_debuff, new_enemy_data):
    for x in remove_debuff:
        try:
            del new_enemy_data["status"][x]
        except Exception:
            pass
    return new_enemy_data


def fixDebuffDescription(debuff):
    if type(debuff['description']) == str:
        debuff['description'] = get_fixed_status_description(debuff['title_id'])
    return debuff


def merge_debuffs(old_enemy_data, new_enemy_data, enemy_type, saved_used_skills_to_ignore_in_last):
    remove_attack = []
    existing_debuffs = {}
    ignore_debuffs = ['130', '13d']
    obviouse_debuffs = ['82b', '82a', '82c', '9d4', '9d7', '95', '12', '38e', '828', '0e', '113', '06', '07', '01', '11', '282', 'ca', '11', '196', '1b6', '23c', '']
    # filter duplicate debuffs
    tmp_debuffs = []
    tmp_debuff_ids = []
    for x in old_enemy_data.get("debuffs", []):
        if x['title_id'] not in tmp_debuff_ids and x['title_id'] not in ignore_debuffs:
            saved_used_skills_to_ignore_in_last.append(x['title_id'])
            x = fixDebuffDescription(x)
            tmp_debuff_ids.append(x['title_id'])
            tmp_debuffs.append(x)
        else:
            print_color_yellow(f"Ignore Duplicate Debuff {x['title']}")
    old_enemy_data["debuffs"] = tmp_debuffs

    if not new_enemy_data.get('title', {}).get('de', "") == 'Unbekannte Herkunft':
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

    old_enemy_data = addSortName(old_enemy_data, "debuffs")
    # merge new keys
    if not old_enemy_data.get('debuffs', None):
        old_enemy_data['debuffs'] = []
    else:
        old_enemy_data['debuffs'] = sorted(old_enemy_data['debuffs'], key=itemgetter('sortname'))

    if not new_enemy_data.get('status', None):
        return old_enemy_data, saved_used_skills_to_ignore_in_last

    # get only status to make sorting easier
    new_enemy_data_status = new_enemy_data.get('status', {})

    # sort after the name key in subdicts
    new_enemy_data_status = OrderedDict(sorted(new_enemy_data_status.items(), key=lambda x: x[1]['name']))

    for status_id, status_data in new_enemy_data_status.items():
        if status_data['name'] == "":
            continue
        if status_id in obviouse_debuffs:
            tmp_status = addknowndebuff(status_id, status_data)
        else:
            descriptions = get_fixed_status_description(status_id)
            tmp_status = {
                'sortname': translateAttack(status_id, _type=status, lang="de"),
                'title': {
                    'en': translateAttack(status_id, _type=status, lang="en"),
                    'de': translateAttack(status_id, _type=status, lang="de"),
                    'fr': translateAttack(status_id, _type=status, lang="fr"),
                    'ja': translateAttack(status_id, _type=status, lang="ja"),
                    'cn': translateAttack(status_id, _type=status, lang="cn"),
                    'ko': translateAttack(status_id, _type=status, lang="ko")
                },
                'title_id': status_id,
                'icon': status_data['icon'],
                'description': {
                    'en': descriptions.get('en', ""),
                    'de': descriptions.get('de', ""),
                    'fr': descriptions.get('fr', ""),
                    'ja': descriptions.get('ja', ""),
                    'cn': descriptions.get('cn', ""),
                    'ko': descriptions.get('ko', "")
                },
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
    old_enemy_data['debuffs'] = sorted(old_enemy_data['debuffs'], key=itemgetter('sortname'))
    return old_enemy_data, saved_used_skills_to_ignore_in_last


def addknowndebuff(status_id, status_data):
    descriptions = get_fixed_status_description(status_id)
    tmp_status = {
        'sortname': translateAttack(status_id, _type=status, lang="de"),
        'title': {
            'en': translateAttack(status_id, _type=status, lang="en"),
            'de': translateAttack(status_id, _type=status, lang="de"),
            'fr': translateAttack(status_id, _type=status, lang="fr"),
            'ja': translateAttack(status_id, _type=status, lang="ja"),
            'cn': translateAttack(status_id, _type=status, lang="cn"),
            'ko': translateAttack(status_id, _type=status, lang="ko")
        },
        'title_id': status_id,
        'icon': status_data['icon'],
        'description': {
            'en': descriptions.get('en', ""),
            'de': descriptions.get('de', ""),
            'fr': descriptions.get('fr', ""),
            'ja': descriptions.get('ja', ""),
            'cn': descriptions.get('cn', ""),
            'ko': descriptions.get('ko', "")
        },
        'debuff_in_use': 'true',
        'disable': 'false',
        #'damage_type': status_data['damage_type'],
        'phases': [{'phase': '09'}],
        'roles': [{'role': 'Alle'}],
        'tags': [{'tag': 'Common'}],
    }
    return tmp_status


def reorder_old_enemies(entry, enemy_type, old_enemies):
    # sort old enemies
    final_old_enemy = []

    # do this only for bosses as they will be reorderd in the same order as in the EXCEL file
    if entry.get(enemy_type, None) and enemy_type == "bosse":
        for enemy in entry[enemy_type]:
            for old_enemy_data in old_enemies:
                # if old title is empty set it to default
                if not old_enemy_data['title']:
                    old_enemy_data['title'] = UNKNOWNTITLE
                if type(old_enemy_data['title']) == str:
                    old_enemy_data['title'] = addLanguageElements("bnpc", old_enemy_data['enemy_id'], old_enemy_data['title'])
                if old_enemy_data['title'].get('de', "").lower() == enemy.lower():
                    final_old_enemy.append(old_enemy_data)

    # if you created a new order, apply it
    if not final_old_enemy == []:
        old_enemies = final_old_enemy
    return old_enemies


def addLanguageElements(_type, _id, ori_value):
    if _type == "bnpc":
        data = bnpcname
        field = "Singular"
    if _type == "action":
        data = action
        field = "Name"
        _id = str(int(_id, 16))
    if _type == "status":
        data = status
        field = "Name"
        _id = str(int(_id, 16))

    if _id:
        return {
            'en': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_en']),
            'de': fixCaptilaziationAndRomanNumerals(ori_value),
            'fr': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_fr']),
            'ja': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_ja']),
            'cn': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_cn']),
            'ko': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_ko']),
        }
    return UNKNOWNTITLE


def workOnOldEnemies(guide_data, entry, enemy_type, old_enemies, logdata_instance_content):
    empty_enemy_available = False
    if old_enemies:
        print_color_red(f"\t [workOnOldEnemies] Start looking at old_enem {enemy_type}", disable_red_print)
        old_enemies = reorder_old_enemies(entry, enemy_type, old_enemies)

        saved_used_skills_to_ignore_in_last = []
        for i, old_enemy_data in enumerate(old_enemies):
            if type(old_enemy_data['title']) == str:
                old_enemy_data['title'] = addLanguageElements("bnpc", old_enemy_data['enemy_id'], old_enemy_data['title'])
            if old_enemy_data['title']['de'] == "":
                continue
            elif old_enemy_data['title']['de'] == "Unbekannte Herkunft":
                empty_enemy_available = True

            old_enemy_data['title']['de'] = fixCaptilaziationAndRomanNumerals(old_enemy_data['title']['de'])
            print_color_yellow(f"\t [workOnOldEnemies] Work on '{old_enemy_data['title']['de']}'", disable_yellow_print)
            empty_enemy_data = {}
            try:
                new_enemy_data = logdata_instance_content[old_enemy_data['title']['de']]
                if enemy_type == 'bosse' and len(old_enemies) == i + 1:
                    empty_enemy_data = logdata_instance_content['']
            except Exception as e:
                # print(logdata_instance_content)
                if not old_enemy_data['title']['de'] == "Unbekannte Herkunft":
                    print(f" [workOnOldEnemies] Could not find {old_enemy_data['title']['de']} in logdata")
                new_enemy_data = {}
            new_enemy_data_c = copy.deepcopy({**{}, **new_enemy_data})
            # get enemy attacks and debuffs for all enemies with a name
            old_enemy_data["enemy_id"] = new_enemy_data.get("id", old_enemy_data.get('enemy_id', ""))

            if new_enemy_data.get("minHP", None) or new_enemy_data.get("maxHP", None):
                old_enemy_data["hp"] = {}
                old_enemy_data["hp"]["min"] = new_enemy_data.get("minHP", "")
                old_enemy_data["hp"]["max"] = new_enemy_data.get("maxHP", "")

            old_enemy_data = merge_attacks(old_enemy_data, new_enemy_data, enemy_type)
            old_enemy_data, saved_used_skills_to_ignore_in_last = merge_debuffs(old_enemy_data, new_enemy_data, enemy_type, saved_used_skills_to_ignore_in_last)

            guide_data += add_Enemy(old_enemy_data, enemy_type, new_enemy_data_c)

            # this try catch will remove enemy from logdata, so it wont be readded later on
            try:
                if old_enemy_data['title']['de'].title() == "Hesperos I":
                    del logdata_instance_content["Hesperos"]
                elif old_enemy_data['title']['de'].title() == "Hephaistos I":
                    del logdata_instance_content["Hephaistos"]
            except:
                print_color_red(" [workOnOldEnemies] !Could not remove enemy: Hesperos", disable_red_print)

            try:
                del logdata_instance_content[fixCaptilaziationAndRomanNumerals(old_enemy_data['title']['de'])]
            except Exception as e:
                print_color_red(" [workOnOldEnemies] Could not remove enemy: " + old_enemy_data['title']['de'], disable_red_print)

            # handle enemy if name is ""
            if not empty_enemy_data == {}:
                empty_enemy_available = True
                base_data = {'title': UNKNOWNTITLE, 'id': f"boss0{i+2}", "sequence": [{"phase": "09"}], 'debuffs': []}
                old_enemy_data = {'title': UNKNOWNTITLE, 'id': f"boss0{i+2}", "sequence": [{"phase": "09"}], 'debuffs': []}
                old_enemy_data = merge_attacks(old_enemy_data, empty_enemy_data, enemy_type)
                old_enemy_data, saved_used_skills_to_ignore_in_last = merge_debuffs(old_enemy_data, empty_enemy_data, enemy_type, saved_used_skills_to_ignore_in_last)

                if not old_enemy_data == base_data:
                    guide_data += add_Enemy(old_enemy_data, enemy_type, new_enemy_data_c)
    return guide_data, empty_enemy_available


def workOnLogDataEnemies(entry, enemy_type, logdata_instance_content, empty_enemy_available):
    guide_data = ""
    if logdata_instance_content != {}:
        print_color_red(f"\t [workOnLogDataEnemies] Start looking at logdata {enemy_type}", disable_red_print)
        counter = 0
        if logdata_instance_content is None:
            print_color_red(f"\t [workOnLogDataEnemies] Skip because logdata_instance_content was not found", disable_red_print)
            return guide_data

        # the array is used to sort bosses
        enemies_to_add = []
        empty_enemy = None
        for enemy in logdata_instance_content:
            print_color_blue(f"\t [workOnLogDataEnemies] Start looking at enemy {enemy}", disable_blue_print)
            if enemy == "" and enemy_type == 'adds':
                continue
            print_color_yellow(f"\t [workOnLogDataEnemies] Work on '{enemy}'", disable_yellow_print)
            # for bosses, only write bosses, for adds skip bosse
            lower_enemy_list = [x.lower() for x in entry[enemy_type]]
            lower_boss_list = [x.lower() for x in entry['bosse']]
            lower_enemy_list.append("")
            if (enemy_type == 'bosse' and enemy.lower() not in lower_enemy_list) or (enemy_type == 'adds' and enemy.lower() in lower_boss_list):
                logger.debug(f"Skip {enemy} ({enemy_type}) -> " + str(enemy.lower() not in lower_enemy_list))
                continue
            counter = counter + 1
            new_enemy_data = logdata_instance_content.get(enemy, "Unknown_")
            if new_enemy_data == {}:
                new_enemy_data = {'skill': {}}
            new_enemy_data_c = copy.deepcopy({**{}, **new_enemy_data})
            # create new template file to merge against
            enemy_id = new_enemy_data.get("id", "")
            de_and_sort_name = enemy if enemy != "" else "Unbekannte Herkunft"
            tmp = {
                "sortname": de_and_sort_name,
                "title": {
                    "en": getBnpcName(enemy, enemy_id, "en") if enemy != "" else "Unknown Source",
                    "de": de_and_sort_name,
                    "fr": getBnpcName(enemy, enemy_id, "fr") if enemy != "" else "Unknown Source",
                    "ja": getBnpcName(enemy, enemy_id, "ja") if enemy != "" else "Unknown Source",
                    "cn": getBnpcName(enemy, enemy_id, "cn") if enemy != "" else "Unknown Source",
                    "ko": getBnpcName(enemy, enemy_id, "ko") if enemy != "" else "Unknown Source"
                },
                "enemy_id": enemy_id,
                "id": f"{enemy_type[:-1]}{counter:02d}",
                "attacks": [],
                "debuffs": [],
                "add_status": []
            }

            if new_enemy_data.get("minHP", None) or new_enemy_data.get("maxHP", None):
                tmp["hp"] = {}
                tmp["hp"]["min"] = new_enemy_data.get("minHP", "")
                tmp["hp"]["max"] = new_enemy_data.get("maxHP", "")

            enemy_data = merge_attacks(tmp, new_enemy_data, enemy_type)
            enemy_data['attacks'] = sorted(enemy_data['attacks'], key=itemgetter('sortname'))

            enemy_data, saved_used_skills_to_ignore_in_last = merge_debuffs(tmp, new_enemy_data, enemy_type, [])
            enemy_data['debuffs'] = sorted(enemy_data['debuffs'], key=itemgetter('sortname'))
            if enemy == "":
                empty_enemy = enemy_data
            else:
                tmp_guide_data_from_enemy = add_Enemy(enemy_data, enemy_type, new_enemy_data_c)
                enemies_to_add.append(tmp_guide_data_from_enemy)

        # this will add bosses in order as specified and add adds in order they were added to the array
        if enemy_type == 'bosse':
            for boss in entry['bosse']:
                for e in enemies_to_add:
                    if f'      de: "{boss}"' in e:
                        guide_data += e
                        break
        else:
            for e in enemies_to_add:
                guide_data += e

        if empty_enemy and not empty_enemy_available:
            if empty_enemy.get("attacks", None) or empty_enemy.get("debuffs", None):
                guide_data += add_Enemy(empty_enemy, "bosse", new_enemy_data_c)

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


def setMultipleLanguageStrings(guide_data, elementName, elemntArray, spaces):
    for lang in LANGUAGES:
        if type(elemntArray[elementName]) == str or type(elemntArray[elementName]) == None:
            continue
        if elemntArray[elementName].get(f"{lang}", None):
            guide_data += f'{spaces}{lang}: "{elemntArray[elementName][lang]}"\n'
    return guide_data


def add_Debuff(guide_data, debuff, enemy_type):
    guide_data += f'      - title:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "title", debuff, "          ")
    guide_data += f'        title_id: "{debuff["title_id"]}"\n'
    guide_data += f'        icon: "{getImage(debuff["icon"])}"\n'
    guide_data += f'        description:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "description", debuff, "          ")
    if debuff.get("durations", None):
        guide_data += f'        durations: {debuff["durations"]}\n'
    guide_data += f'        debuff_in_use: "{debuff["debuff_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{debuff["disable"] or "false"}"\n'
    #guide_data += f'        damage_type: "{debuff["damage_type"] or "None"}"\n'

    if debuff.get('phases', None):
        guide_data += f'        phases:\n'
        for phase in debuff.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if debuff["title"]['de'].startswith("Unknown_"):
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
    guide_data += f'      - title:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "title", attack, "          ")
    guide_data += f'        title_id: "{attack["title_id"]}"\n'
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack.get("disable", "false")}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'
    guide_data += f'        damage_type: "{attack.get("damage_type", None)}"\n'

    if attack.get('add_status', None):
        guide_data += f'        add_status:\n'
        for e in attack['add_status']:
            s = status[str(int(e, 16))]
            guide_data += f'          - status: {e}\n'
            guide_data += f'            icon: "{getImage(s["Icon"])}"\n'
            guide_data += f'            name:\n'
            for lang in LANGUAGES:
                guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

    if attack.get('damage', None):
        guide_data += f'        damage:\n'
        try:
            guide_data += f'          - min: {attack["damage"]["min"] or "None"}\n'
            guide_data += f'          - max: {attack["damage"]["max"] or "None"}\n'
        except TypeError:
            guide_data += f'          - min: {attack["damage"][0]["min"] or "None"}\n'
            guide_data += f'          - max: {attack["damage"][1]["max"] or "None"}\n'

    if attack.get('phases', None):
        guide_data += f'        phases:\n'
        for phase in attack.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if attack["title"]['de'].startswith("Unknown_"):
        return guide_data

    if attack.get('roles', None):
        guide_data += f'        roles:\n'
        for role in attack.get('roles', {}):
            guide_data += f'          - role: "{role["role"]}"\n'

    if attack.get('tags', None):
        guide_data += f'        tags:\n'
        for tag in attack.get('tags', {}):
            guide_data += f'          - tag: "{tag["tag"]}"\n'
        if attack.get('single_or_aoe', None):
            x = "AoE" if attack["single_or_aoe"] == "22" else "Single"
            guide_data += f'          - tag: "{x}"\n'

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
    guide_data += f'      - title:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "title", attack, "          ")
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack.get("disable", "false")}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'

    if attack.get('add_status', None):
        guide_data += f'        add_status:\n'
        for e in attack['add_status']:
            s = status[str(int(e, 16))]
            guide_data += f'          - status: {e}\n'
            guide_data += f'            icon: "{getImage(s["Icon"])}"\n'
            guide_data += f'            name:\n'
            for lang in LANGUAGES:
                guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

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
            #guide_data += f'          - title:\n'
            #guide_data = setMultipleLanguageStrings(guide_data, "title", variation, "              ")
            guide_data += f'          - title_id: "{variation["title_id"]}"\n'
            guide_data += f'            damage_type: "{variation.get("damage_type", None)}"\n'

            if variation.get('add_status', None):
                guide_data += f'            add_status:\n'
                for e in variation['add_status']:
                    s = status[str(int(e, 16))]
                    guide_data += f'              - status: {e}\n'
                    guide_data += f'                icon: "{getImage(s["Icon"])}"\n'
                    guide_data += f'                name:\n'
                    for lang in LANGUAGES:
                        guide_data += f'                 {lang}: "' + s[f"Name_{lang}"] + '"\n'

            # print_color_yellow(variation)
            if variation.get('damage', None):
                guide_data += f'            damage:\n'
                try:
                    guide_data += f'              - min: {variation["damage"]["min"] or "None"}\n'
                    guide_data += f'              - max: {variation["damage"]["max"] or "None"}\n'
                except TypeError:
                    guide_data += f'              - min: {variation["damage"][0]["min"] or "None"}\n'
                    guide_data += f'              - max: {variation["damage"][1]["max"] or "None"}\n'

            if variation.get('roles', None):
                guide_data += f'            roles:\n'
                for role in variation.get('roles', {}):
                    guide_data += f'              - role: "{role["role"]}"\n'

            if variation.get('tags', None):
                guide_data += f'            tags:\n'
                for tag in variation.get('tags', {}):
                    guide_data += f'              - tag: "{tag["tag"]}"\n'
                if variation.get('single_or_aoe', None):
                    x = "AoE" if variation["single_or_aoe"] == "22" else "Single"
                    guide_data += f'              - tag: "{x}"\n'

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
    guide_data += f'      - title:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "title", attack, "          ")
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack["disable"] or "false"}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'

    if attack.get('add_status', None):
        guide_data += f'        add_status:\n'
        for e in attack['add_status']:
            s = status[str(int(e, 16))]
            guide_data += f'          - status: {e}\n'
            guide_data += f'            icon: "{getImage(s["Icon"])}"\n'
            guide_data += f'            name:\n'
            for lang in LANGUAGES:
                guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

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
                if combo.get('single_or_aoe', None):
                    x = "AoE" if combo["single_or_aoe"] == "22" else "Single"
                    guide_data += f'              - tag: "{x}"\n'

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


def add_Enemy(enemy_data, enemy_type, new_enemy_data):
    guide_data = ""
    enemy_data = ugly_fix_enemy_data(enemy_data, new_enemy_data)
    guide_data += f'  - title:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "title", enemy_data, "      ")
    if type(enemy_data.get("enemy_id", "")) == list:
        guide_data += f'    enemy_id: "{", ".join(enemy_data.get("enemy_id", ""))}"\n'
    else:
        guide_data += f'    enemy_id: "{enemy_data.get("enemy_id", "")}"\n'
    guide_data += f'    id: "{enemy_data["id"]}"\n'

    if enemy_data.get('hp', None):
        guide_data += f'    hp:\n'
        try:
            guide_data += f'      - min: {enemy_data["hp"]["min"] or "None"}\n'
            guide_data += f'      - max: {enemy_data["hp"]["max"] or "None"}\n'
        except TypeError:
            guide_data += f'      - min: {enemy_data["hp"][0]["min"] or "None"}\n'
            guide_data += f'      - max: {enemy_data["hp"][1]["max"] or "None"}\n'
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
            guide_data = add_Sequence(guide_data, EXAMPLE_SEQUENCE)
        else:
            guide_data = add_Sequence(guide_data, EXAMPLE_ADD_SEQUENCE)
    return guide_data


def check_Enemy(entry, enemy_type, logdata_instance_content, old_enemies):
    guide_data = ""
    if old_enemies == {} and logdata == {}:
        return guide_data
    guide_data += "bosses:\n" if enemy_type == "bosse" else "adds:\n"
    guide_data, empty_enemy_available = workOnOldEnemies(guide_data, entry, enemy_type, old_enemies, logdata_instance_content)
    #print_color_yellow(guide_data, disable_yellow_print)
    guide_data += workOnLogDataEnemies(entry, enemy_type, logdata_instance_content, empty_enemy_available)
    #print_color_blue(guide_data, disable_blue_print)
    return guide_data


# Notizen, Bosse und Adds
def addGuide(entry, old_data, logdata_instance_content):
    guide_data = ""
    # add mechanics
    guide_data += check_Mechanics(entry, old_data.get('mechanics', None))
    print_color_green(f"Work on '{entry['title_de']}'", disable_green_print)
    guide_data += check_Enemy(entry, "bosse", logdata_instance_content, old_data.get('bosses', {}))
    guide_data += check_Enemy(entry, "adds", logdata_instance_content, old_data.get('adds', {}))
    return guide_data


if __name__ == "__main__":
    a = {'title': {'de': 'Hephaistos II', 'en': 'Hephaistos', 'fr': 'Héphaïstos', 'ja': 'ヘファイストス'}, 'enemy_id': '11402', 'id': 'boss03', 'hp': {'min': 32885224, 'max': 32885224}, 'attacks': [{'title': {'de': 'Unknown_72C2', 'en': 'Unknown_72C2', 'fr': 'Unknown_72C2', 'ja': 'Unknown_72C2', 'cn': 'Unknown_72C2', 'ko': 'Unknown_72C2'}, 'title_id': '72C2', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'damage': [{'min': 6}, {'max': 358819}], 'phases': [{'phase': '01'}, {'phase': '03'}, {'phase': '05'}, {'phase': '06'}, {'phase': '07'}]}, {'title': {'de': 'Unknown_79F0', 'en': 'Unknown_79F0', 'fr': 'Unknown_79F0', 'ja': 'Unknown_79F0', 'cn': 'Unknown_79F0', 'ko': 'Unknown_79F0'}, 'title_id': '79F0', 'attack_in_use': 'false', 'disable': 'true', 'type': 'regular', 'damage_type': 'None', 'add_status': [{'status': 'D4E', 'icon': '015000/015117.png', 'name': {'de': 'Macht des Phoinix', 'en': 'Everburn', 'fr': "Puissance de l'oiseau immortel", 'ja': '不死鳥の力', 'cn': '_rsv_', 'ko': '_rsv_'}}], 'damage': [{'min': 3406}, {'max': 3406}], 'phases': [{'phase': '09'}]}, {'title': {'de': 'Aioniopyr', 'en': 'Aioniopyr', 'fr': 'Aion Pur', 'ja': 'アイオンピュール', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79DF', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'add_status': [{'status': 'B87', 'icon': '015000/015530.png', 'name': {'de': 'Blutung', 'en': 'Bleeding', 'fr': 'Saignement', 'ja': 'ペイン', 'cn': '出血', 'ko': '고통'}}], 'damage': [{'min': 10}, {'max': 58941}], 'phases': [{'phase': '01'}, {'phase': '03'}, {'phase': '05'}, {'phase': '06'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Aschelodern', 'en': 'Ashing Blaze', 'fr': 'Enfer Cendreux', 'ja': 'アッシュブレイズ', 'cn': 'Unknown_79D7', 'ko': 'Unknown_79D7'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '02'}, {'phase': '03'}, {'phase': '06'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '79D7', 'damage_type': 'Magical', 'damage': [{'min': 20663}, {'max': 2179391}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '79D8', 'damage_type': 'Magical', 'damage': [{'min': 39623}, {'max': 2200324}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Beleben Des Kreises', 'en': 'Arcane Control', 'fr': 'Activation Arcanique', 'ja': '魔法陣起動', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79B6', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'None', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'Single'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Bodenhebung', 'en': 'Orogenic Shift', 'fr': 'Surrection', 'ja': '地盤隆起', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79DC', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Blunt', 'add_status': [{'status': 'D2C', 'icon': '015000/015722.png', 'name': {'de': 'Erdresistenz - (stark)', 'en': 'Earth Resistance Down II', 'fr': 'Résistance à la terre réduite+', 'ja': '土属性耐性低下［強］', 'cn': '', 'ko': ''}}], 'damage': [{'min': 396}, {'max': 559628}], 'phases': [{'phase': '08'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'Single'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Bodensturz', 'en': 'Orogenic Annihilation', 'fr': 'Érosion Des Sols', 'ja': '地盤崩壊', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79DA', 'attack_in_use': 'false', 'disable': 'false', 'type': 'regular', 'damage_type': 'Blunt', 'add_status': [{'status': 'B5F', 'icon': '015000/015520.png', 'name': {'de': 'Schaden -', 'en': 'Damage Down', 'fr': 'Malus de dégâts', 'ja': 'ダメージ低下', 'cn': '伤害降低', 'ko': '주는 피해량 감소'}}], 'damage': [{'min': 12728}, {'max': 67597}], 'phases': [{'phase': '09'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Chaotisches Konzept', 'en': 'Failure Of Imagination', 'fr': 'Désordre Conceptuel', 'ja': '混沌概念', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79B1', 'attack_in_use': 'false', 'disable': 'false', 'type': 'regular', 'damage_type': 'None', 'damage': [{'min': 9953404}, {'max': 9999897}], 'phases': [{'phase': '09'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Detonation', 'en': 'Big Burst', 'fr': 'Grosse Explosion', 'ja': '大爆発', 'cn': 'Unknown_79D6', 'ko': 'Unknown_79D6'}, 'title_id': '79D6', 'attack_in_use': 'false', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'add_status': [{'status': 'B5F', 'icon': '015000/015520.png', 'name': {'de': 'Schaden -', 'en': 'Damage Down', 'fr': 'Malus de dégâts', 'ja': 'ダメージ低下', 'cn': '伤害降低', 'ko': '주는 피해량 감소'}}], 'damage': [{'min': 8833}, {'max': 67440}], 'phases': [{'phase': '09'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Egotod', 'en': 'Ego Death', 'fr': "Destruction De L'Ego", 'ja': '自己概念崩壊', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '07'}, {'phase': '08'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '79BA', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7A86', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7A87', 'damage_type': 'None', 'damage': [{'min': 9956936}, {'max': 9985818}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7AA0', 'damage_type': 'None', 'damage': [{'min': 9968254}, {'max': 9998139}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '79E4', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Eiserne Agonie', 'en': 'Aionagonia', 'fr': 'Aion Agonia', 'ja': 'アイオンアゴニア', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '7A22', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'add_status': [{'status': 'B87', 'icon': '015000/015530.png', 'name': {'de': 'Blutung', 'en': 'Bleeding', 'fr': 'Saignement', 'ja': 'ペイン', 'cn': '出血', 'ko': '고통'}}], 'damage': [{'min': 321}, {'max': 49982}], 'phases': [{'phase': '08'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erzwungenes Di-Einfrieren', 'en': 'Forcible Difreeze', 'fr': 'Di Gel Forcé', 'ja': 'フォースド・ディフリーズ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79BE', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'add_status': [{'status': 'B7D', 'icon': '015000/015057.png', 'name': {'de': 'Erhöhte Magie-Verwundbarkeit', 'en': 'Magic Vulnerability Up', 'fr': 'Vulnérabilité magique augmentée', 'ja': '被魔法ダメージ増加', 'cn': '魔法受伤加重', 'ko': '받는 마법 피해량 증가'}}], 'damage': [{'min': 2422}, {'max': 16443254}], 'phases': [{'phase': '02'}, {'phase': '06'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erzwungenes Feuga', 'en': 'Forcible Fire III', 'fr': 'Méga Feu Forcé', 'ja': 'フォースド・ファイガ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79BF', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'add_status': [{'status': 'B7D', 'icon': '015000/015057.png', 'name': {'de': 'Erhöhte Magie-Verwundbarkeit', 'en': 'Magic Vulnerability Up', 'fr': 'Vulnérabilité magique augmentée', 'ja': '被魔法ダメージ増加', 'cn': '魔法受伤加重', 'ko': '받는 마법 피해량 증가'}}], 'damage': [{'min': 1450}, {'max': 376256}], 'phases': [{'phase': '02'}, {'phase': '06'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erzwungenes Feura', 'en': 'Forcible Fire II', 'fr': 'Extra Feu Forcé', 'ja': 'フォースド・ファイラ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79C0', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'add_status': [{'status': 'B7D', 'icon': '015000/015057.png', 'name': {'de': 'Erhöhte Magie-Verwundbarkeit', 'en': 'Magic Vulnerability Up', 'fr': 'Vulnérabilité magique augmentée', 'ja': '被魔法ダメージ増加', 'cn': '魔法受伤加重', 'ko': '받는 마법 피해량 증가'}}], 'damage': [{'min': 784}, {'max': 1559897}], 'phases': [{'phase': '02'}, {'phase': '06'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erzwungenes Trifeuer', 'en': 'Forcible Trifire', 'fr': 'Tri Feu Forcé', 'ja': 'フォースド・トリファイア', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79BD', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'add_status': [{'status': 'B7D', 'icon': '015000/015057.png', 'name': {'de': 'Erhöhte Magie-Verwundbarkeit', 'en': 'Magic Vulnerability Up', 'fr': 'Vulnérabilité magique augmentée', 'ja': '被魔法ダメージ増加', 'cn': '魔法受伤加重', 'ko': '받는 마법 피해량 증가'}}], 'damage': [{'min': 3062}, {'max': 2041365}], 'phases': [{'phase': '02'}, {'phase': '06'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Explosion', 'en': 'Burst', 'fr': 'Explosion', 'ja': '爆発', 'cn': 'Unknown_79D5', 'ko': 'Unknown_79D5'}, 'title_id': '79D5', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'add_status': [{'status': 832, 'icon': '015000/015595.png', 'name': {'de': 'Feuerresistenz - (stark)', 'en': 'Fire Resistance Down II', 'fr': 'Résistance au feu réduite+', 'ja': '火属性耐性低下[強]', 'cn': '火属性耐性大幅降低', 'ko': '불속성 저항 감소[강]'}}], 'damage': [{'min': 58}, {'max': 1089213}], 'phases': [{'phase': '05'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Feuga Des Tyrannen', 'en': "Tyrant's Fire III", 'fr': 'Méga Feu De Tyran', 'ja': 'タイラント・ファイガ', 'cn': 'Unknown_75F0', 'ko': 'Unknown_75F0'}, 'title_id': '75F0', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'add_status': [{'status': 832, 'icon': '015000/015595.png', 'name': {'de': 'Feuerresistenz - (stark)', 'en': 'Fire Resistance Down II', 'fr': 'Résistance au feu réduite+', 'ja': '火属性耐性低下[強]', 'cn': '火属性耐性大幅降低', 'ko': '불속성 저항 감소[강]'}}, {'status': 'B7D', 'icon': '015000/015057.png', 'name': {'de': 'Erhöhte Magie-Verwundbarkeit', 'en': 'Magic Vulnerability Up', 'fr': 'Vulnérabilité magique augmentée', 'ja': '被魔法ダメージ増加', 'cn': '魔法受伤加重', 'ko': '받는 마법 피해량 증가'}}], 'damage': [{'min': 5053}, {'max': 519977}], 'phases': [{'phase': '05'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Flare Des Tyrannen', 'en': "Tyrant's Flare", 'fr': 'Brasier De Tyran', 'ja': 'タイラント・フレア', 'cn': 'Unknown_7A89', 'ko': 'Unknown_7A89'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '02'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7A89', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7A8A', 'damage_type': 'Magical', 'damage': [{'min': 38826}, {'max': 2222113}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Flare Des Tyrannen II', 'en': "Tyrant's Flare II", 'fr': 'Brasier De Tyran II', 'ja': 'タイラント・フレアIi', 'cn': 'Unknown_7A88', 'ko': 'Unknown_7A88'}, 'title_id': '7A88', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'None', 'add_status': [{'status': 'B5F', 'icon': '015000/015520.png', 'name': {'de': 'Schaden -', 'en': 'Damage Down', 'fr': 'Malus de dégâts', 'ja': 'ダメージ低下', 'cn': '伤害降低', 'ko': '주는 피해량 감소'}}], 'damage': [{'min': 20390}, {'max': 512363}], 'phases': [{'phase': '05'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Gewaltige Bodenhebung', 'en': 'Orogenic Deformation', 'fr': 'Grande Surrection', 'ja': '地盤大隆起', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79DB', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Blunt', 'add_status': [{'status': 'D2C', 'icon': '015000/015722.png', 'name': {'de': 'Erdresistenz - (stark)', 'en': 'Earth Resistance Down II', 'fr': 'Résistance à la terre réduite+', 'ja': '土属性耐性低下［強］', 'cn': '', 'ko': ''}}], 'damage': [{'min': 4678}, {'max': 15193}], 'phases': [{'phase': '08'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'Single'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Großer Zirkelimpuls', 'en': 'Arcane Wave', 'fr': 'Grande Vague Arcanique', 'ja': '魔陣大波動', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79B8', 'attack_in_use': 'false', 'disable': 'false', 'type': 'regular', 'damage_type': 'None', 'damage': [{'min': 9956364}, {'max': 9999897}], 'phases': [{'phase': '09'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptkontrolle', 'en': 'High Concept', 'fr': 'Manipulation Conceptuelle', 'ja': '概念支配', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '03'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '710A', 'damage_type': 'Magical', 'damage': [{'min': 35}, {'max': 105561}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '79AC', 'damage_type': 'None', 'damage': [{'min': 467}, {'max': 105561}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Konzeptreflektion', 'en': 'Splicer', 'fr': 'Réaction Conceptuelle', 'ja': '概念反発', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '03'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '79B2', 'damage_type': 'None', 'damage': [{'min': 21197}, {'max': 16636563}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '79B3', 'damage_type': 'None', 'damage': [{'min': 2734}, {'max': 13967154}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '79B4', 'damage_type': 'None', 'damage': [{'min': 1438}, {'max': 14386634}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Konzepttilgung', 'en': 'Deconceptualize', 'fr': 'Effacement Conceptuel', 'ja': '概念消去', 'cn': 'Unknown_7A8E', 'ko': 'Unknown_7A8E'}, 'title_id': '7A8E', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'None', 'phases': [{'phase': '03'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'Single'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptumsetzung', 'en': 'Conception', 'fr': 'Conceptualisation', 'ja': '概念生成', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79B0', 'attack_in_use': 'false', 'disable': 'false', 'type': 'regular', 'damage_type': 'None', 'phases': [{'phase': '09'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptänderung', 'en': 'Conceptual Shift', 'fr': 'Bascule Conceptuelle', 'ja': '概念変異', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '03'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '79AD', 'damage_type': 'Magical', 'damage': [{'min': 8031}, {'max': 2148547}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '79AE', 'damage_type': 'None', 'damage': [{'min': 4639}, {'max': 2243281}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '79AF', 'damage_type': 'None', 'damage': [{'min': 10875}, {'max': 2083138}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Kosmische Verkohlung', 'en': 'Limitless Desolation', 'fr': 'Cendrage Universel', 'ja': '万象灰燼', 'cn': 'Unknown_75ED', 'ko': 'Unknown_75ED'}, 'title_id': '75ED', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'phases': [{'phase': '05'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'Single'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Magische Umkehr', 'en': 'Inverse Magicks', 'fr': 'Inversion Magique', 'ja': 'マジックインヴァージョン', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79C2', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'None', 'phases': [{'phase': '06'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'Single'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Phoinix-Erschaffung', 'en': 'Everburn', 'fr': 'Oiseau Immortel', 'ja': '不死鳥創造', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79B5', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'None', 'add_status': [{'status': 'D10', 'icon': '015000/015103.png', 'name': {'de': 'Konzeptumsetzung: Phoinix', 'en': 'Immortal Conception', 'fr': 'Conceptualisation: oiseau immortel', 'ja': '概念生成：不死鳥', 'cn': '_rsv_', 'ko': '_rsv_'}}], 'damage': [{'min': 9981451}, {'max': 9987641}], 'phases': [{'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Rituelle Anpassung', 'en': 'Natural Alignment', 'fr': 'Description Rituelle', 'ja': '術式記述', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79BB', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'None', 'phases': [{'phase': '02'}, {'phase': '06'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'Single'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Rituelle Zerstörung', 'en': 'Forcible Failure', 'fr': 'Rituel Destructeur', 'ja': '崩壊術式', 'cn': 'Unknown_75EC', 'ko': 'Unknown_75EC'}, 'title_id': '75EC', 'attack_in_use': 'false', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'damage': [{'min': 9940286}, {'max': 9999897}], 'phases': [{'phase': '09'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Schlag Des Herrschers', 'en': 'Dominion', 'fr': 'Poing Du Maître', 'ja': '支配者の一撃', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79D9', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Blunt', 'damage': [{'min': 7503}, {'max': 52856}], 'phases': [{'phase': '08'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'AoE'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Unheiliges Dunkel Des Tyrannen', 'en': "Tyrant's Unholy Darkness", 'fr': 'Miracle Ténébreux De Tyran', 'ja': 'タイラント・ダークホーリー', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '01'}, {'phase': '03'}, {'phase': '06'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '79DD', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '79DE', 'damage_type': 'Magical', 'damage': [{'min': 350}, {'max': 281401}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Zirkelimpuls', 'en': 'Arcane Channel', 'fr': 'Vague Arcanique', 'ja': '魔陣波動', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79B7', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'Magical', 'add_status': [{'status': 'B7D', 'icon': '015000/015057.png', 'name': {'de': 'Erhöhte Magie-Verwundbarkeit', 'en': 'Magic Vulnerability Up', 'fr': 'Vulnérabilité magique augmentée', 'ja': '被魔法ダメージ増加', 'cn': '魔法受伤加重', 'ko': '받는 마법 피해량 증가'}}], 'damage': [{'min': 3301}, {'max': 1179285}], 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'Single'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Zwangsbeschwörung', 'en': 'Twist Nature', 'fr': 'Incantation Forcée', 'ja': '強制詠唱', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': '79BC', 'attack_in_use': 'true', 'disable': 'false', 'type': 'regular', 'damage_type': 'None', 'phases': [{'phase': '02'}, {'phase': '06'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}, {'tag': 'Single'}], 'notes': [{'note': 'note'}]}], 'debuffs': [{'title': {'de': 'Blutung', 'en': 'Bleeding', 'fr': 'Saignement', 'ja': 'ペイン', 'cn': '出血', 'ko': '고통'}, 'title_id': 'B87', 'icon': '015000/015530_hr1.png', 'description': {'de': 'Erleidet schrittweise Schaden.', 'en': 'Sustaining damage over time.', 'fr': 'Des dégâts périodiques neutres sont subis.', 'ja': '無属性ダメージにより、ＨＰが徐々に失われる状態。', 'cn': '无属性持续伤害，体力逐渐流失', 'ko': '무속성 피해로 HP가 서서히 줄어드는 상태.'}, 'durations': [6, 9], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '01'}, {'phase': '03'}, {'phase': '05'}, {'phase': '06'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Einfache Konzeptreflektion', 'en': 'Solosplice', 'fr': 'Concept Adverse Simple', 'ja': '単相式反発概念', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D11', 'icon': '015000/015104_hr1.png', 'description': {'de': 'Löst nach Ablauf eine flächendeckende Reaktion aus.', 'en': 'Self-concept is being warped beyond recognition, resulting in an adverse reaction determined by nearby influences when this effect expires.', 'fr': "La conception du soi est altérée. À la fin de l'effet, l'influence des alentours provoque une réaction spontanée.", 'ja': '自身のイデアが変異しかけている状態。効果終了時、周囲の影響を受けて反発反応を引き起こす。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [8], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erdresistenz - (Stark)', 'en': 'Earth Resistance Down II', 'fr': 'Résistance À La Terre Réduite+', 'ja': '土属性耐性低下［強］', 'cn': 'Unknown_D2C', 'ko': 'Unknown_D2C'}, 'title_id': 'D2C', 'icon': '015000/015722_hr1.png', 'description': {'de': 'Resistenz gegen Erde ist stark verringert.', 'en': 'Earth resistance is significantly reduced.', 'fr': "La résistance à l'élément terre est considérablement réduite.", 'ja': '土属性に対する耐性が著しく低下した状態。'}, 'durations': [9], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '08'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erhöhte Magie-Verwundbarkeit', 'en': 'Magic Vulnerability Up', 'fr': 'Vulnérabilité Magique Augmentée', 'ja': '被魔法ダメージ増加', 'cn': '魔法受伤加重', 'ko': '받는 마법 피해량 증가'}, 'title_id': 'B7D', 'icon': '015000/015057_hr1.png', 'description': {'de': 'Erlittener Magieschaden ist erhöht.', 'en': 'Magic damage taken is increased.', 'fr': 'Les dégâts magiques reçus sont augmentés.', 'ja': '受ける魔法ダメージが増加する状態。', 'cn': '受到魔法攻击的伤害增加', 'ko': '마법 공격으로 받는 피해량이 증가하는 상태.'}, 'durations': [2], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '02'}, {'phase': '06'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Feuerresistenz - (Stark)', 'en': 'Fire Resistance Down II', 'fr': 'Résistance Au Feu Réduite+', 'ja': '火属性耐性低下[強]', 'cn': '火属性耐性大幅降低', 'ko': '불속성 저항 감소[강]'}, 'title_id': '832', 'icon': '015000/015595_hr1.png', 'description': {'de': 'Resistenz gegen Feuer ist stark verringert.', 'en': 'Fire resistance is significantly reduced.', 'fr': "La résistance à l'élément feu est considérablement réduite.", 'ja': '火属性に対する耐性が著しく低下した状態。', 'cn': '对抗火属性的耐性有显著降低', 'ko': '불속성 저항이 크게 떨어진 상태.'}, 'durations': [9], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '05'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Komplexe Konzeptreflektion', 'en': 'Supersplice', 'fr': 'Concept Adverse Puissant', 'ja': '重相式反発概念', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D13', 'icon': '015000/015106_hr1.png', 'description': {'de': 'Löst nach Ablauf eine flächendeckende Reaktion aus.', 'en': 'Self-concept is being warped beyond recognition, resulting in an adverse reaction determined by nearby influences when this effect expires.', 'fr': "La conception du soi est altérée. À la fin de l'effet, l'influence des alentours provoque une réaction spontanée.", 'ja': '自身のイデアが変異しかけている状態。効果終了時、周囲の影響を受けて反発反応を引き起こす。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [8], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptablehnung', 'en': 'Inconceivable', 'fr': 'Rejet Conceptuel', 'ja': '概念拒絶', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D08', 'icon': '015000/015495_hr1.png', 'description': {'de': 'Wird während der Wirkungsdauer nicht von vollständigen Konzepten beeinflusst.', 'en': 'Unable to draw upon perfect concepts until this effect expires.', 'fr': "L'influence des concepts matures hébergés chez les autres n'est plus subie.", 'ja': '効果時間終了まで他者の完成概念の影響を受けない状態。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [3], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptfragment: Phoinix', 'en': 'Immortal Spark', 'fr': 'Concept Fragmentaire: Oiseau Immortel', 'ja': '概念の断片：不死鳥', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D0F', 'icon': '015000/015102_hr1.png', 'description': {'de': 'Löst bei 4 Stapeln Konzeptumsetzung: Phoinix aus.', 'en': 'Conceiving of the Phoenix in part. Together, four such sparks will give birth to a legendary bird.', 'fr': "Le corps héberge un fragment du concept d'oiseau immortel. Si quatre fragments sont réunis, un concept complet est créé.", 'ja': '不死鳥の概念の断片を身に宿した状態。4つ集めることで不死鳥の概念が生成される。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [10], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptumsetzung: Flammengeist', 'en': 'Fiery Conception', 'fr': 'Conceptualisation: Esprit Des Flammes', 'ja': '概念生成：火精', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D0C', 'icon': '015000/015499_hr1.png', 'description': {'de': 'Erleidet schrittweise Schaden.', 'en': 'Realizing a burning concept, causing damage over time until this effect expires.', 'fr': "Un concept d'esprit des flammes est créé, faisant subir des dégâts périodiques.", 'ja': '火精の概念を生成した状態。効果時間終了までＨＰが徐々に失われる。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [38], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptumsetzung: Flugwesen', 'en': 'Winged Conception', 'fr': 'Conceptualisation: Créature Volante', 'ja': '概念生成：飛行生物', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D09', 'icon': '015000/015496_hr1.png', 'description': {'de': 'Verleiht Resistenz gegen bestimmte Windzauber.', 'en': 'Realizing an airborne concept. Resistance to certain wind magicks is increased until this effect expires.', 'fr': 'Un concept de créature volante est créé, octroyant une résistance à certains sorts de vent.', 'ja': '飛行生物の概念を生成した状態。効果時間終了まで特定の風属性魔法に耐性を得る。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [18], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptumsetzung: Gewitterwesen', 'en': 'Shocking Conception', 'fr': 'Conceptualisation: Raijû', 'ja': '概念生成：雷獣', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D0B', 'icon': '015000/015498_hr1.png', 'description': {'de': 'Verleiht Resistenz gegen bestimmte Blitzzauber.', 'en': 'Realizing a levin-wielding concept. Resistance to certain lightning magicks is increased until this effect expires.', 'fr': 'Un concept de Raijû est créé, octroyant une résistance à certains sorts de foudre.', 'ja': '雷獣の概念を生成した状態。効果時間終了まで特定の雷属性魔法に耐性を得る。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [18], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptumsetzung: Gifttier', 'en': 'Toxic Conception', 'fr': 'Conceptualisation: Créature Venimeuse', 'ja': '概念生成：有毒生物', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D0D', 'icon': '015000/015500_hr1.png', 'description': {'de': 'Erleidet schrittweise Schaden.', 'en': 'Realizing a poisonous concept, causing damage over time until this effect expires.', 'fr': 'Un concept de créature venimeuse est créé, faisant subir des dégâts périodiques.', 'ja': '有毒生物の概念を生成した状態。効果時間終了までＨＰが徐々に失われる。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [38], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptumsetzung: Pflanzenwesen', 'en': 'Growing Conception', 'fr': 'Conceptualisation: Créature Végétale', 'ja': '概念生成：草木生物', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D0E', 'icon': '015000/015101_hr1.png', 'description': {'de': 'Erleidet schrittweise Schaden.', 'en': 'Realizing a plantlike concept, causing damage over time until this effect expires.', 'fr': 'Un concept de créature végétale est créé, faisant subir des dégâts périodiques.', 'ja': '草木生物の概念を生成した状態。効果時間終了までＨＰが徐々に失われる。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [38], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptumsetzung: Phoinix', 'en': 'Immortal Conception', 'fr': 'Conceptualisation: Oiseau Immortel', 'ja': '概念生成：不死鳥', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D10', 'icon': '015000/015103_hr1.png', 'description': {'de': 'Wurde von der Kraft des Phoinix wiederbelebt.', 'en': 'Realizing a Phoenix concept.', 'fr': "Le concept d'oiseau immortel a été créé.", 'ja': '不死鳥の概念を生成した状態。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [40], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Konzeptumsetzung: Wasserorganismus', 'en': 'Aquatic Conception', 'fr': 'Conceptualisation: Créature Marine', 'ja': '概念生成：水棲生物', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D0A', 'icon': '015000/015497_hr1.png', 'description': {'de': 'Verleiht Resistenz gegen bestimmte Wasserzauber.', 'en': 'Realizing an aquatic concept. Resistance to certain water magicks is increased until this effect expires.', 'fr': "Un concept de créature marine est créé, octroyant une résistance à certains sorts d'eau.", 'ja': '水棲生物の概念を生成した状態。効果時間終了まで特定の水属性魔法に耐性を得る。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [18], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Macht Des Phoinix', 'en': 'Everburn', 'fr': "Puissance De L'Oiseau Immortel", 'ja': '不死鳥の力', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D4E', 'icon': '015000/015117_hr1.png', 'description': {'de': 'Ausgeteilter Schaden ist erhöht.', 'en': 'Calling upon the power of a Phoenix concept. Damage dealt is increased.', 'fr': "Un concept d'oiseau immortel est créé, augmentant les dégâts infligés.", 'ja': '不死鳥の概念を生成し、その力を身に宿した状態。与ダメージが上昇する。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [9999], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Magische Einnistung', 'en': 'Conceptual Mastery', 'fr': 'Conception Magique', 'ja': 'マジックコンシーヴ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'CFD', 'icon': '015000/015486_hr1.png', 'description': {'de': 'Magische Energie nistet sich in den Körper ein.', 'en': 'Primed with powerful magicks.', 'fr': "Le corps héberge un sort qui peut se déclencher n'importe quand.", 'ja': '発動する魔法を自身に宿した状態。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [9999], 'debuff_in_use': 'false', 'disable': 'false', 'phases': [{'phase': '09'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Magische Umkehr', 'en': 'Inverse Magicks', 'fr': 'Inversion Magique', 'ja': 'マジックインヴァージョン', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D15', 'icon': '015000/015107_hr1.png', 'description': {'de': 'Die Reihenfolge der zwanghaft gewirkten Zauber wird umgekehrt.', 'en': 'The order of forcible magicks to be cast is inverted.', 'fr': "L'odre de lancement des sorts dont l'incantation est forcée est inversé.", 'ja': '自身が強制詠唱させられる魔法の発動順が逆転した状態。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [25], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '06'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Multiple Konzeptreflektion', 'en': 'Multisplice', 'fr': 'Concepts Adverses Multiples', 'ja': '複相式反発概念', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D12', 'icon': '015000/015105_hr1.png', 'description': {'de': 'Löst nach Ablauf eine flächendeckende Reaktion aus.', 'en': 'Self-concept is being warped beyond recognition, resulting in an adverse reaction determined by nearby influences when this effect expires.', 'fr': "La conception du soi est altérée. À la fin de l'effet, l'influence des alentours provoque une réaction spontanée.", 'ja': '自身のイデアが変異しかけている状態。効果終了時、周囲の影響を受けて反発反応を引き起こす。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [8], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Rituelle Anpassung (Empfangen)', 'en': 'Natural Alignment', 'fr': 'Description Rituelle (Ciblage)', 'ja': '術式記述[被]', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D54', 'icon': '015000/015272_hr1.png', 'description': {'de': "Hephaistos' Kräfte verursachen schrittweise Schaden. Löst Rituelle Zerstörung aus, wenn von einem Kommando betroffen, das durch Zwangsbeschwörung gewirkt wurde.", 'en': 'Graven with a sigil and sustaining damage over time. Taking damage from certain actions caused by Twist Nature will result in a destructive forcible failure.', 'fr': 'Des dégâts périodiques sont subis. Rituel destructeur se déclenche si la victime subit un certain sort à incantation forcée.', 'ja': 'ヘファイストスの術式が刻まれ、ＨＰが徐々に失われる状態。「強制詠唱」によって放たれた特定アクションを受けた場合、崩壊術式が発動する。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [48], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '02'}, {'phase': '06'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Schaden +', 'en': 'Damage Up', 'fr': 'Bonus De Dégâts', 'ja': 'ダメージ上昇', 'cn': '伤害提高', 'ko': '주는 피해량 증가'}, 'title_id': '9F6', 'icon': '017000/017061_hr1.png', 'description': {'de': 'Ausgeteilter Schaden ist erhöht.', 'en': 'Damage dealt is increased.', 'fr': 'Les dégâts infligés sont augmentés.', 'ja': '与ダメージが上昇した状態。', 'cn': '攻击所造成的伤害提高', 'ko': '적에게 주는 피해량이 증가하는 상태.'}, 'durations': [9999], 'debuff_in_use': 'false', 'disable': 'false', 'phases': [{'phase': '09'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Schaden -', 'en': 'Damage Down', 'fr': 'Malus De Dégâts', 'ja': 'ダメージ低下', 'cn': '伤害降低', 'ko': '주는 피해량 감소'}, 'title_id': 'B5F', 'icon': '015000/015520_hr1.png', 'description': {'de': 'Ausgeteilter Schaden ist verringert.', 'en': 'Damage dealt is reduced.', 'fr': 'Les dégâts infligés sont réduits.', 'ja': '与ダメージが低下した状態。', 'cn': '攻击所造成的伤害降低', 'ko': '적에게 주는 피해량이 감소하는 상태.'}, 'durations': [30], 'debuff_in_use': 'false', 'disable': 'false', 'phases': [{'phase': '09'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Unvollständiges Konzept Α', 'en': 'Imperfection: Alpha', 'fr': 'Concept Immature: Α', 'ja': '未完概念：Α', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D02', 'icon': '015000/015489_hr1.png', 'description': {'de': 'Löst nach Ablauf eine Explosion aus, die das eigene Konzept und Konzepte in der Nähe beeinflusst.', 'en': 'Imbued with a concept incompatible with this form, which will cause an explosive reaction and influence self and nearby concepts when this effect expires.', 'fr': "L'être est contaminé par le concept d'une créature. Une explosion se produit à la fin de l'effet, impactant la victime et les concepts alentour.", 'ja': '自身とは異なる生体のイデアを付与された状態。効果終了時に爆発反応を起こし、自身と周囲のイデアに影響を及ぼす。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [8, 26], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Unvollständiges Konzept Β', 'en': 'Imperfection: Beta', 'fr': 'Concept Immature: Β', 'ja': '未完概念：Β', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D03', 'icon': '015000/015490_hr1.png', 'description': {'de': 'Löst nach Ablauf eine Explosion aus, die das eigene Konzept und Konzepte in der Nähe beeinflusst.', 'en': 'Imbued with a concept incompatible with this form, which will cause an explosive reaction and influence self and nearby concepts when this effect expires.', 'fr': "L'être est contaminé par le concept d'une créature. Une explosion se produit à la fin de l'effet, impactant la victime et les concepts alentour.", 'ja': '自身とは異なる生体のイデアを付与された状態。効果終了時に爆発反応を起こし、自身と周囲のイデアに影響を及ぼす。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [8, 26], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Unvollständiges Konzept Γ', 'en': 'Imperfection: Gamma', 'fr': 'Concept Immature: Γ', 'ja': '未完概念：Γ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D04', 'icon': '015000/015491_hr1.png', 'description': {'de': 'Löst nach Ablauf eine Explosion aus, die das eigene Konzept und Konzepte in der Nähe beeinflusst.', 'en': 'Imbued with a concept incompatible with this form, which will cause an explosive reaction and influence self and nearby concepts when this effect expires.', 'fr': "L'être est contaminé par le concept d'une créature. Une explosion se produit à la fin de l'effet, impactant la victime et les concepts alentour.", 'ja': '自身とは異なる生体のイデアを付与された状態。効果終了時に爆発反応を起こし、自身と周囲のイデアに影響を及ぼす。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [8, 26], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Vollständiges Konzept Α', 'en': 'Perfection: Alpha', 'fr': 'Concept Mature: Α', 'ja': '完成概念：Α', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D05', 'icon': '015000/015492_hr1.png', 'description': {'de': 'Gegenseitige Beeinflussung, wenn sich vollständige Konzepte von anderen in der Nähe befinden.', 'en': 'The perfect vessel for a perfect concept. Drawing near to other perfect concepts will result in mutual influence.', 'fr': "Le corps héberge le concept mature d'une créature. En cas de rapprochement avec un autre concept mature, une influence mutuelle se produit.", 'ja': '自身とは異なる生体のイデアが身体に宿った状態。他者の完成概念と近づくことで互いに影響を及ぼす。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [30], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Vollständiges Konzept Β', 'en': 'Perfection: Beta', 'fr': 'Concept Mature: Β', 'ja': '完成概念：Β', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D06', 'icon': '015000/015493_hr1.png', 'description': {'de': 'Gegenseitige Beeinflussung, wenn sich vollständige Konzepte von anderen in der Nähe befinden.', 'en': 'The perfect vessel for a perfect concept. Drawing near to other perfect concepts will result in mutual influence.', 'fr': "Le corps héberge le concept mature d'une créature. En cas de rapprochement avec un autre concept mature, une influence mutuelle se produit.", 'ja': '自身とは異なる生体のイデアが身体に宿った状態。他者の完成概念と近づくことで互いに影響を及ぼす。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [30], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Vollständiges Konzept Γ', 'en': 'Perfection: Gamma', 'fr': 'Concept Mature: Γ', 'ja': '完成概念：Γ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D07', 'icon': '015000/015494_hr1.png', 'description': {'de': 'Gegenseitige Beeinflussung, wenn sich vollständige Konzepte von anderen in der Nähe befinden.', 'en': 'The perfect vessel for a perfect concept. Drawing near to other perfect concepts will result in mutual influence.', 'fr': "Le corps héberge le concept mature d'une créature. En cas de rapprochement avec un autre concept mature, une influence mutuelle se produit.", 'ja': '自身とは異なる生体のイデアが身体に宿った状態。他者の完成概念と近づくことで互いに影響を及ぼす。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [30], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}], 'sequence': [{'phase': '01', 'name': 'Anfang', 'attacks': [{'attack': '3x --auto--'}, {'attack': 'Aioniopyr'}, {'attack': '2x --auto--'}, {'attack': 'Unheiliges Dunkel des Tyrannen'}, {'attack': '2x --auto--'}]}, {'phase': '02', 'name': 'Rituelle Anpassung 1', 'attacks': [{'attack': 'Rituelle Anpassung 1'}, {'attack': 'Zwangsbeschwörung'}, {'attack': 'Flare des Tyrannen'}, {'attack': 'Erzwungenes Feuga/Erzwungenes Feura'}, {'attack': 'Flare des Tyrannen'}, {'attack': 'Erzwungenes Feura/Erzwungenes Feuga'}, {'attack': 'Aschelodern'}, {'attack': 'Erzwungenes Trifeuer/Erzwungenes Di-Einfrieren'}, {'attack': 'Erzwungenes Di-Einfrieren/Erzwungenes Trifeuer'}]}, {'phase': '03', 'name': 'Konzeptkontrolle 1', 'attacks': [{'attack': 'Aioniopyr'}, {'attack': '2x --auto--'}, {'attack': 'Unheiliges Dunkel des Tyrannen'}, {'attack': '--auto--'}, {'attack': 'Konzeptkontrolle 1'}, {'attack': '--nich anvisierbar--'}, {'attack': 'Beleben des Kreises'}, {'attack': 'Konzeptänderung'}, {'attack': 'Konzeptreflektion'}, {'attack': 'Aschelodern'}, {'attack': 'Zirkelimpuls'}, {'attack': 'Beleben des Kreises'}, {'attack': 'Konzeptänderung'}, {'attack': 'Aschelodern'}, {'attack': 'Zirkelimpuls'}, {'attack': '--anvisierbar--'}, {'attack': 'Konzepttilgung'}]}, {'phase': '05', 'name': 'Kosmische Verkohlung', 'attacks': [{'attack': 'Aioniopyr'}, {'attack': '3x --auto--'}, {'attack': 'Kosmische Verkohlung'}, {'attack': 'Feuga des Tyrannen x4'}, {'attack': 'Flare des Tyrannen II'}, {'attack': 'Explosion 1'}, {'attack': 'Flare des Tyrannen II'}, {'attack': 'Explosion 2'}, {'attack': 'Flare des Tyrannen II'}, {'attack': 'Explosion 3'}, {'attack': 'Flare des Tyrannen II'}, {'attack': 'Explosion 4'}]}, {'phase': '06', 'name': 'Rituelle Anpassung 2', 'attacks': [{'attack': 'Aioniopyr'}, {'attack': '2x --auto--'}, {'attack': 'Unheiliges Dunkel des Tyrannen'}, {'attack': '2x --auto--'}, {'attack': 'Rituelle Anpassung'}, {'attack': 'Magische Umkehr'}, {'attack': 'Zwangsbeschwörung'}, {'attack': 'Erzwungenes Feuga/Erzwungenes Feura'}, {'attack': 'Erzwungenes Feura/Erzwungenes Feuga'}, {'attack': 'Erzwungenes Trifeuer/Erzwungenes Di-Einfrieren'}, {'attack': 'Erzwungenes Di-Einfrieren/Erzwungenes Trifeuer'}, {'attack': 'Aschelodern'}]}, {'phase': '07', 'name': 'Konzeptkontrolle 2', 'attacks': [{'attack': 'Aioniopyr'}, {'attack': '2x --auto--'}, {'attack': 'Unheiliges Dunkel des Tyrannen'}, {'attack': '--auto--'}, {'attack': 'Konzeptkontrolle 2'}, {'attack': '--nich anvisierbar--'}, {'attack': 'Beleben des Kreises'}, {'attack': 'Konzeptänderung'}, {'attack': 'Konzeptreflektion'}, {'attack': 'Aschelodern'}, {'attack': 'Zirkelimpuls'}, {'attack': 'Beleben des Kreises'}, {'attack': 'Konzeptänderung'}, {'attack': 'Ende aller Tage'}, {'attack': 'Zirkelimpuls'}, {'attack': '--anvisierbar--'}, {'attack': 'Egotod'}]}, {'phase': '08', 'name': 'Dominion Endspurt', 'attacks': [{'attack': 'Eiserne Agonie 1'}, {'attack': 'Schlag des Herrschers'}, {'attack': 'Gewaltige Bodenhebung'}, {'attack': 'Bodenhebung x2'}, {'attack': 'Eiserne Agonie 2'}, {'attack': 'Schlag des Herrschers'}, {'attack': 'Gewaltige Bodenhebung'}, {'attack': 'Bodenhebung x2'}, {'attack': 'Eiserne Agonie 3'}, {'attack': 'Egotod (Finalangriff)'}]}, {'phase': '09', 'name': 'phase_name', 'alerts': [{'alert': 'Die folgenden Angriffe haben sind entweder unbekannt oder haben keine klare Herkunft'}], 'mechanics': [{'title': 'sequence-mechanic-01', 'notes': [{'note': 'sequence-mechanic-note-01'}]}], 'attacks': [{'attack': 'sequence-attack-01'}], 'images': [{'url': '/assets/img/test.jpg', 'alt': '/assets/img/test.jpg', 'height': '250px'}], 'videos': [{'url': 'https&#58;//ffxivguide.akurosia.de/upload/test.mp4'}]}]}
    b = {'id': '11402', 'maxHP': 32885224, 'minHP': 32885224, 'skill': {'710A': {'damage': {'max': 105561, 'min': 35}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Konzeptkontrolle', 'type_id': '22'}, '72C2': {'damage': {'max': 358819, 'min': 6}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': '', 'type_id': '22'}, '75EC': {'damage': {'max': 9999897, 'min': 9940286}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Rituelle Zerstörung', 'type_id': '22'}, '75ED': {'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Kosmische Verkohlung', 'type_id': '21'}, '75F0': {'add_status': ['832', 'B7D'], 'damage': {'max': 519977, 'min': 5053}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Feuga Des Tyrannen', 'type_id': '22'}, '79AC': {'damage_type': 'None', 'element': 'None', 'name': 'Konzeptkontrolle', 'type_id': '22'}, '79AD': {'add_status': ['D05', 'D08'], 'damage': {'max': 2148547, 'min': 8031}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Konzeptänderung', 'type_id': '22'}, '79AE': {'add_status': ['D06', 'D08', 'B7D'], 'damage': {'max': 2243281, 'min': 4639}, 'damage_type': 'None', 'element': 'None', 'name': 'Konzeptänderung', 'type_id': '22'}, '79AF': {'add_status': ['D07', 'D08', 'B7D'], 'damage': {'max': 2083138, 'min': 10875}, 'damage_type': 'None', 'element': 'None', 'name': 'Konzeptänderung', 'type_id': '22'}, '79B0': {'damage_type': 'None', 'element': 'None', 'name': 'Konzeptumsetzung', 'type_id': '22'}, '79B1': {'damage': {'max': 9999897, 'min': 9953404}, 'damage_type': 'None', 'element': 'None', 'name': 'Chaotisches Konzept', 'type_id': '22'}, '79B2': {'add_status': ['B7D'], 'damage': {'max': 16636563, 'min': 21197}, 'damage_type': 'None', 'element': 'None', 'name': 'Konzeptreflektion', 'type_id': '22'}, '79B3': {'add_status': ['B7D'], 'damage': {'max': 13967154, 'min': 2734}, 'damage_type': 'None', 'element': 'None', 'name': 'Konzeptreflektion', 'type_id': '22'}, '79B4': {'add_status': ['B7D'], 'damage': {'max': 14386634, 'min': 1438}, 'damage_type': 'None', 'element': 'None', 'name': 'Konzeptreflektion', 'type_id': '22'}, '79B5': {'add_status': ['D10'], 'damage': {'max': 9987641, 'min': 9981451}, 'damage_type': 'None', 'element': 'Fire', 'name': 'Phoinix-Erschaffung', 'type_id': '22'}, '79B6': {'damage_type': 'None', 'element': 'None', 'name': 'Beleben Des Kreises', 'type_id': '20'}, '79B7': {'add_status': ['B7D'], 'damage': {'max': 1179285, 'min': 3301}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Zirkelimpuls', 'type_id': '21'}, '79B8': {'damage': {'max': 9999897, 'min': 9956364}, 'damage_type': 'None', 'element': 'None', 'name': 'Großer Zirkelimpuls', 'type_id': '22'}, '79BA': {'damage_type': 'None', 'element': 'None', 'name': 'Egotod', 'type_id': '21'}, '79BB': {'damage_type': 'None', 'element': 'None', 'name': 'Rituelle Anpassung', 'type_id': '21'}, '79BC': {'damage_type': 'None', 'element': 'None', 'name': 'Zwangsbeschwörung', 'type_id': '21'}, '79BD': {'add_status': ['B7D'], 'damage': {'max': 2041365, 'min': 3062}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Erzwungenes Trifeuer', 'type_id': '22'}, '79BE': {'add_status': ['B7D'], 'damage': {'max': 16443254, 'min': 2422}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Erzwungenes Di-Einfrieren', 'type_id': '22'}, '79BF': {'add_status': ['B7D'], 'damage': {'max': 376256, 'min': 1450}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Erzwungenes Feuga', 'type_id': '22'}, '79C0': {'add_status': ['B7D'], 'damage': {'max': 1559897, 'min': 784}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Erzwungenes Feura', 'type_id': '22'}, '79C2': {'damage_type': 'None', 'element': 'None', 'name': 'Magische Umkehr', 'type_id': '21'}, '79D5': {'add_status': ['832'], 'damage': {'max': 1089213, 'min': 58}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Explosion', 'type_id': '22'}, '79D6': {'add_status': ['B5F'], 'damage': {'max': 67440, 'min': 8833}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Detonation', 'type_id': '22'}, '79D7': {'add_status': ['B5F'], 'damage': {'max': 2179391, 'min': 20663}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Aschelodern', 'type_id': '22'}, '79D8': {'add_status': ['B5F'], 'damage': {'max': 2200324, 'min': 39623}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Aschelodern', 'type_id': '22'}, '79D9': {'damage': {'max': 52856, 'min': 7503}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Schlag Des Herrschers', 'type_id': '22'}, '79DA': {'add_status': ['B5F'], 'damage': {'max': 67597, 'min': 12728}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Bodensturz', 'type_id': '22'}, '79DB': {'add_status': ['D2C'], 'damage': {'max': 15193, 'min': 4678}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Gewaltige Bodenhebung', 'type_id': '21'}, '79DC': {'add_status': ['D2C'], 'damage': {'max': 559628, 'min': 396}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Bodenhebung', 'type_id': '21'}, '79DD': {'damage_type': 'None', 'element': 'None', 'name': 'Unheiliges Dunkel Des Tyrannen', 'type_id': '21'}, '79DE': {'damage': {'max': 281401, 'min': 350}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Unheiliges Dunkel Des Tyrannen', 'type_id': '22'}, '79DF': {'add_status': ['B87'], 'damage': {'max': 58941, 'min': 10}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Aioniopyr', 'type_id': '22'}, '79E4': {'damage_type': 'None', 'element': 'None', 'name': 'Egotod', 'type_id': '22'}, '79F0': {'add_status': ['D4E'], 'damage': {'max': 3406, 'min': 3406}, 'damage_type': 'None', 'element': 'Water', 'name': '', 'type_id': '22'}, '7A22': {'add_status': ['B87'], 'damage': {'max': 49982, 'min': 321}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Eiserne Agonie', 'type_id': '22'}, '7A86': {'damage_type': 'None', 'element': 'None', 'name': 'Egotod', 'type_id': '22'}, '7A87': {'damage': {'max': 9985818, 'min': 9956936}, 'damage_type': 'None', 'element': 'None', 'name': 'Egotod', 'type_id': '22'}, '7A88': {'add_status': ['B5F'], 'damage': {'max': 512363, 'min': 20390}, 'damage_type': 'None', 'element': 'None', 'name': 'Flare Des Tyrannen Ii', 'type_id': '22'}, '7A89': {'damage_type': 'None', 'element': 'None', 'name': 'Flare Des Tyrannen', 'type_id': '21'}, '7A8A': {'add_status': ['B5F'], 'damage': {'max': 2222113, 'min': 38826}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Flare Des Tyrannen', 'type_id': '22'}, '7A8E': {'damage_type': 'None', 'element': 'None', 'name': 'Konzepttilgung', 'type_id': '21'}, '7AA0': {'damage': {'max': 9998139, 'min': 9968254}, 'damage_type': 'None', 'element': 'Water', 'name': 'Egotod', 'type_id': '22'}}, 'status': {'832': {'duration': [9], 'icon': 'ui/icon/015000/015595_hr1.png', 'name': 'Feuerresistenz - (Stark)', 'type_id': '30'}, '9F6': {'duration': [9999], 'icon': 'ui/icon/017000/017061_hr1.png', 'name': 'Schaden +', 'type_id': '26'}, 'B5F': {'duration': [6, 20, 30], 'icon': 'ui/icon/015000/015520_hr1.png', 'name': 'Schaden -', 'type_id': '30'}, 'B7D': {'duration': [2], 'icon': 'ui/icon/015000/015057_hr1.png', 'name': 'Erhöhte Magie-Verwundbarkeit', 'type_id': '30'}, 'B87': {'duration': [6, 9], 'icon': 'ui/icon/015000/015530_hr1.png', 'name': 'Blutung', 'type_id': '30'}, 'D05': {'duration': [30], 'icon': 'ui/icon/015000/015492_hr1.png', 'name': 'Vollständiges Konzept Α', 'type_id': '30'}, 'D06': {'duration': [30], 'icon': 'ui/icon/015000/015493_hr1.png', 'name': 'Vollständiges Konzept Β', 'type_id': '30'}, 'D07': {'duration': [30], 'icon': 'ui/icon/015000/015494_hr1.png', 'name': 'Vollständiges Konzept Γ', 'type_id': '30'}, 'D08': {'duration': [3], 'icon': 'ui/icon/015000/015495_hr1.png', 'name': 'Konzeptablehnung', 'type_id': '30'}, 'D10': {'duration': [40], 'icon': 'ui/icon/015000/015103_hr1.png', 'name': 'Konzeptumsetzung: Phoinix', 'type_id': '30'}, 'D2C': {'duration': [9], 'icon': 'ui/icon/015000/015722_hr1.png', 'name': 'Erdresistenz - (Stark)', 'type_id': '30'}, 'D4E': {'duration': [9999], 'icon': 'ui/icon/015000/015117_hr1.png', 'name': 'Macht Des Phoinix', 'type_id': '30'}}}
    c = "bosse"
    print(merge_attacks(a, b, c))
