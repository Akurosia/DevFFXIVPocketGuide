#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import re
import copy
from operator import itemgetter
from collections import OrderedDict
from typing import Any
from ffxiv_aku import print_color_red, print_color_yellow, print_color_blue, print_pretty_json
try:
    from python_scripts.constants import LANGUAGES, UNKNOWNTITLE
    from python_scripts.fileimports import action, bnpcname, eobjname, enpcresident, status
except Exception:
    from constants import LANGUAGES, UNKNOWNTITLE
    from fileimports import action, bnpcname, eobjname, enpcresident, status
import logging

logger: logging.Logger = logging.getLogger()

disable_green_print = True
disable_yellow_print = True
disable_blue_print = True
disable_red_print = True


def sort_status_ids(status_list: Any) -> list[str]:
    if isinstance(status_list,list):
        try:
            return sorted(list(set(status_list)), key=lambda x: int(x,16))
        except:
            y: list[str] = []
            for x in status_list:
                if str(x['status']) not in y:
                    y.append(str(x['status']))
            return sorted(list(set(y)), key=lambda x: int(x,16))
    else:
        print_color_red(status_list)
    return list(set(status_list))


def delete_invalid_entries(tmp_attack: dict[str, Any]) -> dict[str, Any]:
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
        #tmp = sorted(list(attack['add_status']))
        tmp = attack['add_status']
        attack['add_status'] = []
        for s in tmp:
            if isinstance(s, dict):
                attack['add_status'].append(str(s['status']))
            else:
                attack['add_status'].append(str(s))

        for s in new_attack.get("add_status", []):
            if isinstance(s, str):
                attack['add_status'].append(str(s))
            else:
                attack['add_status'].append(str(s['status']))
        attack['add_status'] = sorted(list(set(attack['add_status'])))
    elif new_attack.get("add_status", None):
        attack['add_status'] = new_attack['add_status']

    # finally sort attacks
    if attack.get("add_status", None):
        attack["add_status"] = sort_status_ids(attack["add_status"])


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
        return {"en": f"Unknown_{_id}"}


ids_to_replace1: list[str] = ["10742", "11399", "13057"]
ids_to_replace2: list[str] = ["10744", "11402", "13058"]
def getBnpcNameFromID(_id, aname, nname, lang="en"):
    global ids_to_replace
    bnpc_new_name = ""
    eobjname = ""
    enpcresident_name = ""
    if nname == "???":
        nname = "\\?\\?\\?"
    if isinstance(_id, list):
        _id = _id[0]
    _id = str(_id)
    try:
        bnpc_new_name = bnpcname[_id]["Singular_de"]
        extra = ""
        if _id in ids_to_replace1:
            nname = nname.replace(" i", "")
            extra = " I"
        elif _id in ids_to_replace2:
            nname = nname.replace(" ii", "")
            extra = " II"
        m = re.search(nname, bnpc_new_name, re.IGNORECASE)
        n = re.search(aname, bnpc_new_name, re.IGNORECASE)
        if m or n:
            return bnpcname[_id][f"Singular_{lang}"] + extra
    except Exception:
        if nname == bnpc_new_name or aname == bnpc_new_name:
            return bnpcname[_id][f"Singular_{lang}"]

    try:
        eobjname = eobjname[_id]["Singular_de"]
        m = re.search(nname, eobjname, re.IGNORECASE)
        n = re.search(aname, eobjname, re.IGNORECASE)
        if m or n:
            return eobjname[_id][f"Singular_{lang}"]
    except Exception:
        if nname == eobjname or aname == eobjname:
            return eobjname[_id][f"Singular_{lang}"]

    try:
        enpcresident_name = enpcresident[_id]["Singular_de"]
        m = re.search(nname, enpcresident_name, re.IGNORECASE)
        n = re.search(aname, enpcresident_name, re.IGNORECASE)
        if m or n:
            return enpcresident[_id][f"Singular_{lang}"]
    except Exception:
        if nname == enpcresident_name or aname == enpcresident_name:
            return enpcresident[_id][f"Singular_{lang}"]

    if "α" not in bnpc_new_name and "β" not in bnpc_new_name and "（仮）鎖" not in bnpc_new_name:
        final_string = ""
        if bnpc_new_name:
            final_string += f"{bnpc_new_name=} "
        if eobjname:
            final_string += f"{eobjname=} "
        if enpcresident_name:
            final_string += f"{enpcresident_name=} "
        print_color_red(f"{final_string}not found '{aname}' ({nname}) - ({_id})")
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
    nname = aname.replace("er ", r"(\[a\]|(e|es|er|en)) ").replace("es ", r"(\[a\]|(e|es|er|en)) ").replace("en ", r"(\[a\]|(e|es|er|en)) ").replace("e ", r"(\[a\]|(e|es|er|en)) ").replace("?", "\\?")
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
        nname = "\\?\\?\\?"
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

        if attack.get("add_status", None):
            attack["add_status"] = sort_status_ids(attack["add_status"])
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
                if attack_index is None:
                    raise Exception(f"Skill {x_attack_name} ({attack_id}) wa snot found in logdata")

                tmp_attack = old_enemy_data['attacks'][attack_index]
                tmp_attack['type'] = "variation"
                #tmp_attack['notes'] = [{'note': 'Variation-note BIG'}]
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
                    except Exception:
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
                    except Exception:
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
                    except Exception:
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
                'damage_type': attack.get('damage_type', None),
                'phases': [{'phase': '09'}],
                'roles': [{'role': 'role'}],
                'tags': [{'tag': 'tag'}],
                #'notes': [{'note': 'note'}],
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
                try:
                    del tmp['notes']
                except: ...

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
            if isinstance(debuff['title'], str):
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
    if isinstance(debuff['description'], str):
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
    if old_enemy_data.get("debuffs", None):
        old_enemy_data["debuffs"] = sorted(old_enemy_data["debuffs"], key=itemgetter('title_id'))
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
            descriptions: dict[str, str] = get_fixed_status_description(status_id)
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
                #'notes': [{'note': 'note'}]
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
                if isinstance(old_enemy_data['title'], str):
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
            'de': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_de']),
            'fr': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_fr']),
            'ja': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_ja']),
            'cn': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_cn']),
            'ko': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_ko']),
        }
    return UNKNOWNTITLE


def workOnOldEnemies(guide_data, entry, enemy_type, old_enemies, logdata_instance_content, content_translations, callback=None):
    # hack to split guide and guide helper
    add_Enemy = callback
    empty_enemy_available = False
    if old_enemies:
        print_color_red(f"\t [workOnOldEnemies] Start looking at old_enem {enemy_type}", disable_red_print)
        old_enemies = reorder_old_enemies(entry, enemy_type, old_enemies)

        saved_used_skills_to_ignore_in_last = []
        for i, old_enemy_data in enumerate(old_enemies):
            if isinstance(old_enemy_data['title'], str):
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
            except Exception:
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

            guide_data += add_Enemy(old_enemy_data, enemy_type, new_enemy_data_c, content_translations)

            # this try catch will remove enemy from logdata, so it wont be readded later on
            try:
                if old_enemy_data['title']['de'].title() == "Hesperos I":
                    del logdata_instance_content["Hesperos"]
                elif old_enemy_data['title']['de'].title() == "Hephaistos I":
                    del logdata_instance_content["Hephaistos"]
                elif old_enemy_data['title']['de'].title() == "Tosender Donner I":
                    del logdata_instance_content["Tosender Donner"]
            except Exception:
                print_color_red(" [workOnOldEnemies] !Could not remove enemy: Hesperos", disable_red_print)

            try:
                del logdata_instance_content[fixCaptilaziationAndRomanNumerals(old_enemy_data['title']['de'])]
            except Exception:
                print_color_red(" [workOnOldEnemies] Could not remove enemy: " + old_enemy_data['title']['de'], disable_red_print)

            # handle enemy if name is ""
            if not empty_enemy_data == {}:
                empty_enemy_available = True
                base_data = {'title': UNKNOWNTITLE, 'id': f"boss0{i+2}", "sequence": [{"phase": "09"}], 'debuffs': []}
                old_enemy_data = {'title': UNKNOWNTITLE, 'id': f"boss0{i+2}", "sequence": [{"phase": "09"}], 'debuffs': []}
                old_enemy_data = merge_attacks(old_enemy_data, empty_enemy_data, enemy_type)
                old_enemy_data, saved_used_skills_to_ignore_in_last = merge_debuffs(old_enemy_data, empty_enemy_data, enemy_type, saved_used_skills_to_ignore_in_last)

                if not old_enemy_data == base_data:
                    guide_data += add_Enemy(old_enemy_data, enemy_type, new_enemy_data_c, content_translations)
    return guide_data, empty_enemy_available


def workOnLogDataEnemies(entry, enemy_type, logdata_instance_content, empty_enemy_available, content_translations, callback=None):
    # hack to split guide and guide helper
    add_Enemy = callback
    guide_data = ""
    if logdata_instance_content != {}:
        print_color_red(f"\t [workOnLogDataEnemies] Start looking at logdata {enemy_type}", disable_red_print)
        counter = 0
        if logdata_instance_content is None:
            print_color_red("\t [workOnLogDataEnemies] Skip because logdata_instance_content was not found", disable_red_print)
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
                tmp_guide_data_from_enemy = add_Enemy(enemy_data, enemy_type, new_enemy_data_c, content_translations)
                enemies_to_add.append(tmp_guide_data_from_enemy)

        # this will add bosses in order as specified and add adds in order they were added to the array
        if enemy_type == 'bosse':
            for boss in entry['bosse']:
                for e in enemies_to_add:
                    if f'  - title:\n      de: "{boss}"' in e:
                        guide_data += e
                        break
        else:
            for e in enemies_to_add:
                guide_data += e

        if empty_enemy and not empty_enemy_available:
            if empty_enemy.get("attacks", None) or empty_enemy.get("debuffs", None):
                guide_data += add_Enemy(empty_enemy, "bosse", {}, content_translations)

    return guide_data


#def getIDSFromText(enemy_names: dict[str, Any], texts: list[str]) -> dict[str, set]:
#    result: dict[str, set] = {'npcyell_ids': set(), 'instancecontenttextdata_ids': set()}
#    remove_text = set()
#    for key, value in npcyell.items():
#        for text in texts:
#            textx: str = text.strip()
#            de_val: str = value['Text_de'].replace("\n\n", " ").strip()
#            if textx == de_val:
#                result['npcyell_ids'].add(key)
#                remove_text.add(text)
#                break
#    for t in remove_text:
#        try:
#            texts.remove(t)
#        except: pass
#
#    remove_text = set()
#    for key, value in instancecontenttextdata.items():
#        for text in texts:
#            textx: str = text.strip()
#            de_val: str = value['Text_de'].replace("\n\n", " ").strip()
#            if textx == de_val:
#                result['instancecontenttextdata_ids'].add(key)
#                remove_text.add(text)
#
#    for t in remove_text:
#        try:
#            texts.remove(t)
#        except: pass
#    if texts != []:
#        print_color_red(f"\t{enemy_names}")
#        print_color_red(f"\t\t{texts}")
#    return result


def ugly_fix_enemy_data(enemy_data: dict[str, Any], new_enemy_data: dict[str, Any]) -> dict[str, Any]:
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
    if not enemy_data.get('text', None):
        enemy_data['text'] = {}
    enemy_data['text'] = new_enemy_data.get('text', {})
    #if new_enemy_data.get('text', None):
    #    _ids: dict[str, set] = getIDSFromText(enemy_data['title'], new_enemy_data['text'])
    #    for cat, _xids in _ids.items():
    #        for _id in _xids:
    #            if not enemy_data['text'].get(cat, None):
    #                enemy_data['text'][cat] = set()
    #            enemy_data['text'][cat].add(_id)
    #print(enemy_data['text'])
    return enemy_data


