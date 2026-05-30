from collections import OrderedDict
from copy import deepcopy
from .helper import getImage, deal_with_extras_in_text, get_propper_zone_name, LANGUAGES
import traceback
from operator import getitem
from glob import glob
from ffxiv_aku import loadDataTheQuickestWay, os, storeFilesInTmp

logdata = None
craftactions = None
actions = None
items = None
aozaction = None
aozactions = None
aozactiontransient = None
path_of_main_script = None


def numeric_sort_key(value):
    text = str(value).split(".")[0]
    return (0, int(text)) if text.isdigit() else (1, str(value))


def blu_load_global_data(blu_craftactions, blu_actions, blu_items, blu_logdata):
    global logdata
    global actions
    global aozaction
    global aozactions
    global aozactiontransient
    global craftactions
    global items
    storeFilesInTmp(False)
    actions = blu_actions
    aozaction = loadDataTheQuickestWay("AozActionTransient")
    aozactions = loadDataTheQuickestWay("AozAction")
    aozactiontransient = loadDataTheQuickestWay("AozActionTransient")
    craftactions = blu_craftactions
    items = blu_items
    logdata = blu_logdata


def sort_locations(locations):
    return sorted(
        locations,
        key=lambda x: (
            str(x.get('Ort', "")),
            str(x.get('Gegner', "")),
            str(x.get('type', "")),
            int(x.get('player', 0) or 0),
        ),
    )


def add_location_once(locations, location):
    if location not in locations:
        locations.append(location)


def get_play_in_locations(locations):
    cfc = loadDataTheQuickestWay("ContentFindercondition")
    cmt = loadDataTheQuickestWay("ContentMemberType.json")
    new_locations = []
    for key, value in sorted(cfc.items(), key=lambda item: numeric_sort_key(item[0])):
        player = 0
        for loc in locations:
            if value['Name'].lower() == loc['Ort'].lower():
                if value['TerritoryType'] == "w1tz":
                    loc["player"] = 1
                    loc["type"] = "Große Maskerade Masked Carnivale Himmlische Arena"
                else:
                    x = cmt[value['ContentMemberType'].split('#')[1]]
                    player = int(x['HealersPerParty']) + int(x['MeleesPerParty']) + int(x['RangedPerParty']) + int(x['TanksPerParty'])
                    loc["player"] = 1 if player == 0 else player
                    loc["type"] = value['ContentType']
                    add_location_once(new_locations, loc)
                #print(value)
    for loc in locations:
        found = False
        for loc2 in new_locations:
            if loc['Ort'] == loc2['Ort']:
                found = True
        if not found:
            add_location_once(new_locations, loc)
    return sort_locations(new_locations)


def addBlueAttackDetails(main_script, job_data, craftactions, actions, items, logdata, klass_translations):
    global path_of_main_script
    path_of_main_script = main_script
    blu_load_global_data(craftactions, actions, items, logdata)
    job_data = deepcopy(job_data)
    result = ""
    result += "    attacks:\n"
    # get special aoz action data from correct files e.g. number in blu spell book and description
    blueTotemSpells = get_blue_totem_skills()
    blueTotemCondition = {
        "Wasserkanone": "Blaumagier freischalten",
        "Weißer Wind": "10 Zauber gelernt",
        "Einschüchtern": "5 Zauber gelernt",
        "Assimilation": "20 Zauber gelernt",
        "Totalabwehr": "10 Zauber gelernt",
        "Mondflöte": "10 Mission der Himmlichen Arena abgeschlossen",
        "Verhängnis": "20 Mission der Himmlichen Arena abgeschlossen",
        "Rachestoß": "50 Zauber gelernt",
        "Engelsflüstern": "30 Mission der Himmlichen Arena abgeschlossen",
        "Engelspeise": "Level 70 mit dem Blaumagier erreicht",
        "Drachenkraft": "100 Zauber gelernt",
        "Matra-Magie": "100 Zauber gelernt",
        "Zauberatem": "Level 80 mit dem Blaumagier erreicht",
        "Kraftfeld": "120 Zauber gelernt"
    }
    for x, y in sorted(job_data.items(), key=lambda item: numeric_sort_key(item[0])):
        for key, value in sorted(aozactions.items(), key=lambda item: numeric_sort_key(item[0])):
            if y['Name']['de'] == value['Action']['Name_de']:
                if not aozactiontransient[key]['Location'].get('Name_de', "") == "":
                    job_data[x]["Location"] = {"Ort": aozactiontransient[key]['Location']['Name_de'], "Gegner": "(InGame Hinweis)"}
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = aozactiontransient[key]['Number']

                for lang in LANGUAGES:
                    job_data[x]["Description"][lang] += "\n\n<br/>#########################################<br/>\n\n" + deal_with_extras_in_text(aozaction[key][f'Description_{lang}'])
            #Special cases to sort in these 2 skills
            elif y['Name']['de'] == "Weißer Tod":
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = "84"
            elif y['Name']['de'] == "Göttlicher Katarakt":
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = "89"

        if not y.get("Number", None):
            job_data[x]["Number"] = job_data[x]["Level"]
            job_data[x]["Level"] = "90" + job_data[x]["Level"]

    files = sorted(glob("**/**/*.md"))

    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: (int(getitem(x[1], 'Level')), numeric_sort_key(x[1]["Id"]))))
    for _id, skill_data in job_data.items():
        try:
            locations = []
            if skill_data.get('Location', None):
                locations.append(skill_data['Location'])
            name = {}
            for lang in LANGUAGES:
                name[lang] = deal_with_extras_in_text(actions.get(skill_data["Id"], {}).get(f"Name_{lang}", ""))
            if name["en"] == "":
                name["en"] = craftactions[skill_data["Id"] + ".0"]["Name_en"]
            level = skill_data['Level']
            #
            locations = getBLULocationsFromLogdata(skill_data["Name"]['de'], locations)
            locations = sort_locations(locations)
            # somehow original locations got updated, just dont touch it
            #n_locations = get_play_in_locations(locations)
            desc = ""
            terms = []

            if not locations == [] or name['de'] in blueTotemSpells:
                desc += "\n\n<br/>#########################################<br/>\n\nLOCATIONS:\n"
                # special case to add totem entries
                if name["de"] in blueTotemSpells:
                    desc += "<table class='table-striped table-dark table-hover bg-charcoal text-light border-gold-metallic'><thead><td>Zone</td><td>Gegnername</td><td>Bedinnung</td></thead><tbody>"
                    desc += f"<tr><td>Ul'dah - Thal-Kreuzgang (X:12.5 Y:12.9)</td><td> Wayward Gaheel Ja (Totem der Blaumagie: {name['de']})</td><td> {blueTotemCondition[name['de']]} </td></tr>"
                    terms.append("Totems")
                else:
                    desc += "<table class='table-striped table-dark table-hover bg-charcoal text-light border-gold-metallic'><thead><td>Zone</td><td>Gegnername</td></thead><tbody>"
                    for location in locations:
                        zone_name = location["Ort"]
                        enemy_name = location["Gegner"]
                        if location.get('player', None):
                            if f"{location['player']}man" not in terms:
                                terms.append(f"{location['player']}man")
                        if location.get('type', None):
                            if location['type'] not in terms:
                                terms.append(location['type'])
                        p_zone_name = get_propper_zone_name(zone_name, files)
                        tmp = f"<tr><td>{zone_name} </td><td> {enemy_name}</td></tr>"
                        #tmp = "\n&emsp;" + f"{zone_name} -> {enemy_name}"
                        if p_zone_name:
                            tmp = f"<tr><td><a href='/DevFFXIVPocketGuide/{p_zone_name}' target='_blank'>{zone_name} </a></td><td> {enemy_name}</td></tr>"
                            #tmp = "\n&emsp;" + f"<a href='{p_zone_name}' target='_blank'>{zone_name}</a> -> {enemy_name}"
                        desc += tmp
            desc += "</tbody></table>"


            tpye_damage = "Schaden" if skill_data["IsDamageSkill"] else None
            tpye_heilung = "Heilung" if skill_data["IsHealingSkill"] else None
            type_shield = "P-Schild-Mitigation" if skill_data["IsShieldSkill"] else None
            mtype  = skill_data["MitigationType"]
            mvalue = skill_data["MitigationValue"]

            desc = desc.replace("\n", "</br>").replace("</br></br>", "</br>")
            if skill_data.get("Number", None) and int(level) < 901:
                result += '      - title:\n'
                for lang in LANGUAGES:
                    result += f'          {lang}: "{level}. {name[lang]}"\n'
                    klass_translations[lang][f"Class_Skill_Name_{level}. {name['en']}"] = f"{level}. {name[lang]}"
            else:
                result += '      - title:\n'
                for lang in LANGUAGES:
                    result += f'          {lang}: "{name[lang]}"\n'
                    klass_translations[lang][f"Class_Skill_Name_{name['en']}"] = f"{name[lang]}"
            result += f'        title_id: "{skill_data["Id"].split(".")[0]}"\n'
            if skill_data.get("Number", None):
                result += f'        level: "{skill_data["Number"]}"\n'
            else:
                result += f'        level: "{level}"\n'

            result += '        terms:\n'
            for term in sorted(terms):
                result += f'          - term: "{term}"\n'
            result += f'        icon: "{getImage(skill_data["Icon"])}"\n'
            result += f'        range: "{skill_data["Range"]}"\n'
            result += f'        effectrange: "{skill_data["EffectRange"]}"\n'
            result += f'        cast: "{skill_data["Cast"]}"\n'
            result += f'        recast: "{skill_data["Recast"]}"\n'
            result += f'        kategorie: "{skill_data["Kategorie"]['de']}"\n'
            if tpye_damage:
                result += f'        damage: "{tpye_damage}"\n'
            if tpye_heilung:
                result += f'        heal: "{tpye_heilung}"\n'
            if type_shield:
                result += f'        shield: "{type_shield}"\n'
            if mtype == "personal":
                result += '        pmitigation: "P-Mitigation"\n'
                result += f'        pmitigation_value: "{mvalue}"\n'
            if mtype == "group":
                result += '        gmitigation: "G-Mitigation"\n'
                result += f'        gmitigation_value: "{mvalue}"\n'
            result += '        description:\n'
            for lang in LANGUAGES:
                result += f'          {lang}: "' + deal_with_extras_in_text(skill_data["Description"][lang].replace('"', '\\"')) + f'{desc}"\n'
                klass_translations[lang][f"Class_Skill_Desc_{level}. {name['en']}"] = deal_with_extras_in_text(skill_data["Description"][lang].replace('"', '\\"')) + f'{desc}'
            result += '        phases:\n'
            result += '          - phase: "01"\n'
        except Exception:
            traceback.print_exc()
    return result, klass_translations


def getBLULocationsFromLogdata(name, locations):
    global logdata
    if not name:
        return locations
    nresult = list(locations)
    for location_name, location_data in sorted(logdata.items(), key=lambda item: str(item[0])):
        if not location_name:
            continue
        for enemy_name, enemy_data in sorted(location_data.items(), key=lambda item: str(item[0])):
            if not enemy_name or isinstance(enemy_data, list):
                continue
            for skill_id, skill_data in sorted(enemy_data.get("skill", {}).items(), key=lambda item: str(item[0])):
                if not skill_id or not skill_data:
                    continue
                if name.lower() == skill_data["name"].lower():
                    tmp = {"Ort": location_name, "Gegner": enemy_name}
                    add_location_once(nresult, tmp)
    return sort_locations(nresult)


def get_blue_totem_skills():
    global items
    result = ["Wasserkanone"]
    for key, value in sorted(items.items(), key=lambda item: numeric_sort_key(item[0])):
        if "Totem der Blaumagie:" in value['Name_de']:
            result.append(value['Name_de'].replace("Totem der Blaumagie: ", ""))
    return sorted(set(result))
