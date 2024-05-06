import os
from collections import OrderedDict
from .helper import getImage, deal_with_extras_in_text, LANGUAGES
from ffxiv_aku import storeFilesInTmp, loadDataTheQuickestWay, os
from operator import getitem

chocoboskills_trans = None
chocoboitems_trans = None
chocobochallange_trans = None
buddyskill_raw = None
actions = None
actions_trans = None
actiontransient_trans = None
traits = None
traits_trans = None
traitstransient_trans = None


def cb_load_global_data(cb_actions, cb_actions_trans, cb_actiontransient_trans, cb_traits, cb_traits_trans, cb_traitstransient_trans):
    global chocoboskills_trans
    global chocoboitems_trans
    global chocobochallange_trans
    global buddyskill_raw
    global actions
    global actions_trans
    global actiontransient_trans
    global traits
    global traits_trans
    global traitstransient_trans
    origin = os.getcwd()
    os.chdir("..")
    storeFilesInTmp(True)

    actions = cb_actions
    actions_trans = cb_actions_trans
    actiontransient_trans = cb_actiontransient_trans
    traits = cb_traits
    traits_trans = cb_traits_trans
    traitstransient_trans = cb_traitstransient_trans
    chocoboskills_trans = loadDataTheQuickestWay("chocoboraceability", translate=True)
    chocoboitems_trans = loadDataTheQuickestWay("chocoboraceitem", translate=True)
    chocobochallange_trans = loadDataTheQuickestWay("chocoboracechallenge", translate=True)
    buddyskill_raw = loadDataTheQuickestWay("buddyskill.json", exd="raw-exd-all")
    os.chdir(origin)


def addChocoboPartnerSkills():
    global actions
    global actions_trans
    global actiontransient_trans

    global buddyskill_raw
    test = [ [ x['Attacker'], x['Defender'], x['Healer'] ] for key, x in buddyskill_raw.items() if x['IsActive'] == "True" and not key == "0" ]
    chocobo_skills = []
    for x in test:
        chocobo_skills += x
    chocobo_skillss = { key:actions[key] for key in chocobo_skills }
    #print(chocobo_skillss)
    ordered = OrderedDict(sorted(chocobo_skillss.items(), key=lambda x: int(x[0])))
    result = ""
    result += "    attacks:\n"
    for key, _ in ordered.items():
        t = actions_trans[key]
        result += '      - title:\n'
        result += f'          de: "{t["Name_de"]}"\n'
        result += f'          en: "{t["Name_en"]}"\n'
        result += f'          fr: "{t["Name_fr"]}"\n'
        result += f'          ja: "{t["Name_ja"]}"\n'
        result += f'          cn: "{t["Name_cn"]}"\n'
        result += f'          ko: "{t["Name_ko"]}"\n'
        result += f'        icon: "{getImage(t["Icon"])}"\n'
        #result += f'        level: "{actions[key]["Level"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += '        description:\n'
        result += '          de: "' + deal_with_extras_in_text(actiontransient_trans[key]["Description_de"]) + '"\n'
        result += '          en: "' + deal_with_extras_in_text(actiontransient_trans[key]["Description_en"]) + '"\n'
        result += '          fr: "' + deal_with_extras_in_text(actiontransient_trans[key]["Description_fr"]) + '"\n'
        result += '          ja: "' + deal_with_extras_in_text(actiontransient_trans[key]["Description_ja"]) + '"\n'
        result += '          cn: "' + deal_with_extras_in_text(actiontransient_trans[key]["Description_cn"]) + '"\n'
        result += '          ko: "' + deal_with_extras_in_text(actiontransient_trans[key]["Description_ko"]) + '"\n'
        result += '        phases:\n'
        result += '          - phase: "01"\n'
    return result


def addRennChocoboSkills_trans():
    global chocoboskills_trans
    ordered = OrderedDict(sorted(chocoboskills_trans.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["Name_de"] == "":
            continue
        # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        result += '      - title:\n'
        result += f'          de: "{value["Name_de"]}"\n'
        result += f'          en: "{value["Name_en"]}"\n'
        result += f'          fr: "{value["Name_fr"]}"\n'
        result += f'          ja: "{value["Name_ja"]}"\n'
        result += f'          cn: "{value["Name_cn"]}"\n'
        result += f'          ko: "{value["Name_ko"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += f'        icon: "{getImage(value["Icon"])}"\n'
        result += '        description:\n'
        result += '          de: "' + deal_with_extras_in_text(value["Description_de"]) + '"\n'
        result += '          en: "' + deal_with_extras_in_text(value["Description_en"]) + '"\n'
        result += '          fr: "' + deal_with_extras_in_text(value["Description_fr"]) + '"\n'
        result += '          ja: "' + deal_with_extras_in_text(value["Description_ja"]) + '"\n'
        result += '          cn: "' + deal_with_extras_in_text(value["Description_cn"]) + '"\n'
        result += '          ko: "' + deal_with_extras_in_text(value["Description_ko"]) + '"\n'
        result += '        phases:\n'
        result += '          - phase: "03"\n'
    return result


def addChocoboPartnerTraits():
    global traits
    global traits_trans
    global traitstransient_trans
    global buddyskill_raw
    test = [ [x['Attacker'], x['Defender'], x['Healer']] for key, x in buddyskill_raw.items() if x['IsActive'] == "False" and not key == "0"]
    chocobo_traits = []
    for x in test:
        chocobo_traits += x
    chocobo_traits = sorted(chocobo_traits)
    chocobo_traits_trans = { key:traits[key] for key in chocobo_traits }
    ordered = OrderedDict(sorted(chocobo_traits_trans.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    result = ""
    result += "    traits:\n"
    for key, _ in ordered.items():
        t = traits_trans[key]
        result += '      - title:\n'
        result += f'          de: "{t["Name_de"]}"\n'
        result += f'          en: "{t["Name_en"]}"\n'
        result += f'          fr: "{t["Name_fr"]}"\n'
        result += f'          ja: "{t["Name_ja"]}"\n'
        result += f'          cn: "{t["Name_cn"]}"\n'
        result += f'          ko: "{t["Name_ko"]}"\n'
        result += f'        icon: "{getImage(t["Icon"])}"\n'
        result += f'        level: "{traits[key]["Level"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += '        description:\n'
        result += '          de: "' + deal_with_extras_in_text(traitstransient_trans[key]["Description_de"]) + '"\n'
        result += '          en: "' + deal_with_extras_in_text(traitstransient_trans[key]["Description_en"]) + '"\n'
        result += '          fr: "' + deal_with_extras_in_text(traitstransient_trans[key]["Description_fr"]) + '"\n'
        result += '          ja: "' + deal_with_extras_in_text(traitstransient_trans[key]["Description_ja"]) + '"\n'
        result += '          cn: "' + deal_with_extras_in_text(traitstransient_trans[key]["Description_cn"]) + '"\n'
        result += '          ko: "' + deal_with_extras_in_text(traitstransient_trans[key]["Description_ko"]) + '"\n'
        result += '        phases:\n'
        result += '          - phase: "02"\n'
    return result


def addRennChocoboItems_trans():
    global chocoboitems_trans
    ordered = OrderedDict(sorted(chocoboitems_trans.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["Name_de"] == "":
            continue
        # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        result += '      - title:\n'
        result += f'          de: "{value["Name_de"]}"\n'
        result += f'          en: "{value["Name_en"]}"\n'
        result += f'          fr: "{value["Name_fr"]}"\n'
        result += f'          ja: "{value["Name_ja"]}"\n'
        result += f'          cn: "{value["Name_cn"]}"\n'
        result += f'          ko: "{value["Name_ko"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += f'        icon: "{getImage(value["Icon"])}"\n'
        result += '        description:\n'
        result += '          de: "' + deal_with_extras_in_text(value["Description_de"]) + '"\n'
        result += '          en: "' + deal_with_extras_in_text(value["Description_en"]) + '"\n'
        result += '          fr: "' + deal_with_extras_in_text(value["Description_fr"]) + '"\n'
        result += '          ja: "' + deal_with_extras_in_text(value["Description_ja"]) + '"\n'
        result += '          cn: "' + deal_with_extras_in_text(value["Description_cn"]) + '"\n'
        result += '          ko: "' + deal_with_extras_in_text(value["Description_ko"]) + '"\n'
        result += '        phases:\n'
        result += '          - phase: "04"\n'
    return result


def addRennChocoboMissions():
    global chocobochallange_trans
    ordered = OrderedDict(sorted(chocobochallange_trans.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["col_0_de"] == "":
            continue
        result += '      - title:\n'
        result += f'          de: "{value["col_0_de"]}"\n'
        result += f'          en: "{value["col_0_en"]}"\n'
        result += f'          fr: "{value["col_0_fr"]}"\n'
        result += f'          ja: "{value["col_0_ja"]}"\n'
        result += f'          cn: "{value["col_0_cn"]}"\n'
        result += f'          ko: "{value["col_0_ko"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += '        phases:\n'
        result += '          - phase: "05"\n'
    return result


def addChocobo(actions, actions_trans, actiontransient_trans, traits, traits_trans, traitstransient_trans, klass_translations):
    cb_load_global_data(actions, actions_trans, actiontransient_trans, traits, traits_trans, traitstransient_trans)
    job = "Chocobo"
    job_d = {
        "Name_de": "Chocobo",
        "Name_en": "chocobo",
        "Name_fr": "chocobo",
        "Name_ja": "チョコボ",
        "Name_cn": "チョコボ",
        "Name_ko": "초코보"
    }
    filecontent = ""
    filecontent += '---\n'
    filecontent += 'wip: "True"\n'
    filecontent += 'title:\n'
    filecontent += f'  de: "{job_d["Name_de"]}"\n'
    filecontent += f'  en: "{job_d["Name_en"]}"\n'
    filecontent += f'  fr: "{job_d["Name_fr"]}"\n'
    filecontent += f'  ja: "{job_d["Name_ja"]}"\n'
    filecontent += f'  cn: "{job_d["Name_cn"]}"\n'
    filecontent += f'  ko: "{job_d["Name_ko"]}"\n'
    filecontent += 'layout: klassen\n'
    filecontent += 'page_type: guide\n'
    filecontent += f'roletypeinparty: "{job_d["Name_en"]}"\n'
    for lang in LANGUAGES:
        klass_translations[lang][f'Sidebar_Role_{job_d["Name_en"]}'] = job_d[f"Name_{lang}"]
    filecontent += 'categories: "klassenjobs"\n'
    filecontent += 'difficulty: "Normal"\n'
    filecontent += 'instanceType: "klassenjobs"\n'
    filecontent += 'date: "2013.01.01"\n'
    filecontent += 'patchNumber: "2.0"\n'
    filecontent += 'patchName: "A Realm Reborn"\n'
    filecontent += 'expac: "arr"\n'
    filecontent += 'slug: "klassen_und_jobs_' + job.lower() + '"\n'
    if os.path.exists(f"{os.getcwd()}/../assets/img/content/klassen/{job}.png"):
        filecontent += f'image: "/assets/img/content/klassen/{job}.png"\n'
    else:
        print(f"Missing img: {job}.png")
    filecontent += 'terms:\n'
    filecontent += '    - term: "Klassen"\n'
    filecontent += '    - term: "Jobs"\n'
    filecontent += '    - term: "Skills"\n'
    filecontent += '    - term: "Status"\n'
    filecontent += '    - term: "Traits"\n'
    filecontent += f'    - term: "{job_d["Name_de"]}"\n'
    filecontent += f'    - term: "{job_d["Name_en"]}"\n'
    filecontent += f'    - term: "{job_d["Name_fr"]}"\n'
    filecontent += f'    - term: "{job_d["Name_ja"]}"\n'
    filecontent += f'    - term: "{job_d["Name_cn"]}"\n'
    filecontent += f'    - term: "{job_d["Name_ko"]}"\n'
    filecontent += 'sortid: 0\n'
    filecontent += 'order: 0\n'
    filecontent += 'plvl: 50\n'
    filecontent += "bosses:\n"
    filecontent += "  - title:\n"
    filecontent += f'      de: "{job_d["Name_de"]}"\n'
    filecontent += f'      en: "{job_d["Name_en"]}"\n'
    filecontent += f'      fr: "{job_d["Name_fr"]}"\n'
    filecontent += f'      ja: "{job_d["Name_ja"]}"\n'
    filecontent += f'      cn: "{job_d["Name_cn"]}"\n'
    filecontent += f'      ko: "{job_d["Name_ko"]}"\n'
    filecontent += "    id: \"" + "boss0\"\n"
    #todo add chocobo stuff
    filecontent += addChocoboPartnerSkills()
    filecontent += addRennChocoboSkills_trans()
    #addRennChocoboStatus()
    filecontent += addRennChocoboItems_trans()
    filecontent += addRennChocoboMissions()
    filecontent += addChocoboPartnerTraits()
    filecontent += "    sequence:" + "\n"
    filecontent += "      - phase: \"01\"\n"
    filecontent += "        name: \"Chocobo-Partner-Skills\"\n"
    filecontent += "      - phase: \"02\"\n"
    filecontent += "        name: \"Chocobo-Partner-Traits\"\n"
    filecontent += "      - phase: \"03\"\n"
    filecontent += "        name: \"Renn-Chocobo-Skills\"\n"
    #filecontent += "      - phase: \"04\"\n"
    #filecontent += "        name: \"Renn-Chocobo-Status\"\n"
    filecontent += "      - phase: \"04\"\n"
    filecontent += "        name: \"Renn-Chocobo-Items\"\n"
    filecontent += "      - phase: \"05\"\n"
    filecontent += "        name: \"Renn-Chocobo-Missions\"\n"
    filecontent += '---\n'

    filename = f"klassen_und_jobs/2013-01-01--2.0--0--{job}.md"
    with open(filename, encoding="utf8") as f:
        doc = f.read()
    if not doc == filecontent:
        with open(filename, "w", encoding="utf8") as f:
            f.write(filecontent)
