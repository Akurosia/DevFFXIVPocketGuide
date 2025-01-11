from collections import OrderedDict
from .helper import getImage, deal_with_extras_in_text, get_propper_zone_name, LANGUAGES
import traceback
from operator import getitem
from glob import glob
from ffxiv_aku import loadDataTheQuickestWay, os, storeFilesInTmp

logdata = None
craftactions_trans = None
actions_trans = None
items_trans = None
aozaction_trans = None
aozactions_trans = None
aozactiontransient = None


def blu_load_global_data(blu_craftactions_trans, blu_actions_trans, blu_items_trans, blu_logdata):
    global logdata
    global actions_trans
    global aozaction_trans
    global aozactions_trans
    global aozactiontransient
    global craftactions_trans
    global items_trans
    origin = os.getcwd()
    os.chdir("..")
    storeFilesInTmp(True)
    actions_trans = blu_actions_trans
    aozaction_trans = loadDataTheQuickestWay("aozactiontransient", translate=True)
    aozactions_trans = loadDataTheQuickestWay("aozaction", translate=True)
    aozactiontransient = loadDataTheQuickestWay("AozActionTransient")
    craftactions_trans = blu_craftactions_trans
    items_trans = blu_items_trans
    logdata = blu_logdata
    os.chdir(origin)


def get_play_in_locations(locations):
    cfc = loadDataTheQuickestWay("ContentFindercondition")
    cmt = loadDataTheQuickestWay("ContentMemberType.json")
    new_locations = []
    for key, value in cfc.items():
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
                    new_locations.append(loc)
                #print(value)
    for loc in locations:
        found = False
        for loc2 in new_locations:
            if loc['Ort'] == loc2['Ort']:
                found = True
        if not found:
            new_locations.append(loc)
    return sorted(new_locations, key=lambda x: x['Ort'])


def addBlueAttackDetails(job_data, craftactions_trans, actions_trans, items_trans, logdata, klass_translations):
    blu_load_global_data(craftactions_trans, actions_trans, items_trans, logdata)
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
    for x, y in job_data.items():
        for key, value in aozactions_trans.items():
            if y['Name']['de'] == value['Name_de']:
                if not aozactiontransient[key]['Location'] == "":
                    job_data[x]["Location"] = {"Ort": aozactiontransient[key]['Location'], "Gegner": "(InGame Hinweis)"}
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = aozactiontransient[key]['Number']

                for lang in LANGUAGES:
                    job_data[x]["Description"][lang] += "\n\n<br/>#########################################<br/>\n\n" + deal_with_extras_in_text(aozaction_trans[key][f'Description_{lang}'])
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

    files = glob("**/**/*.md")

    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, skill_data in job_data.items():
        try:
            locations = []
            if skill_data.get('Location', None):
                locations.append(skill_data['Location'])
            name = {}
            for lang in LANGUAGES:
                name[lang] = deal_with_extras_in_text(actions_trans.get(skill_data["Id"], {}).get(f"Name_{lang}", ""))
            if name["en"] == "":
                name["en"] = craftactions_trans[skill_data["Id"] + ".0"]["Name_en"]
            level = skill_data['Level']
            #
            locations = getBLULocationsFromLogdata(skill_data["Name"]['de'], locations)
            locations = sorted(locations, key=lambda x: x['Ort'])
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
            for term in terms:
                result += f'          - term: "{term}"\n'
            result += f'        icon: "/assets/img/game_assets{getImage(skill_data["Icon"])}"\n'
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
    nresult = locations
    for location_name, location_data in logdata.items():
        if not location_name:
            continue
        for enemy_name, enemy_data in location_data.items():
            if not enemy_name or isinstance(enemy_data, list):
                continue
            for skill_id, skill_data in enemy_data.get("skill", {}).items():
                if not skill_id or not skill_data:
                    continue
                if name.lower() == skill_data["name"].lower():
                    tmp = {"Ort": location_name, "Gegner": enemy_name}
                    if tmp not in nresult:
                        nresult.append(tmp)
    return nresult


def get_blue_totem_skills():
    global items_trans
    result = ["Wasserkanone"]
    for key, value in items_trans.items():
        if "Totem der Blaumagie:" in value['Name_de']:
            result.append(value['Name_de'].replace("Totem der Blaumagie: ", ""))
    return result
