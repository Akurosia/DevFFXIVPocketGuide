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
job_translations = None


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
        for lang in LANGUAGES:
            result += f'          {lang}: "{t[f"Name_{lang}"]}"\n'
            job_translations[lang][f'Class_Skill_Name_{t["Name_en"]}'] = t[f"Name_{lang}"]
        result += f'        icon: "{getImage(t["Icon"])}"\n'
        #result += f'        level: "{actions[key]["Level"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{deal_with_extras_in_text(actiontransient_trans[key][f"Description_{lang}"])}"\n'
            job_translations[lang][f'Class_Skill_Desc_{t["Name_en"]}'] = deal_with_extras_in_text(actiontransient_trans[key][f"Description_{lang}"])
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
        for lang in LANGUAGES:
            result += f'          {lang}: "{value[f"Name_{lang}"]}"\n'
            job_translations[lang][f'Class_Skill_Name_{value["Name_en"]}'] = value[f"Name_{lang}"]
        result += f'        title_id: "{key}"\n'
        result += f'        icon: "{getImage(value["Icon"])}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{deal_with_extras_in_text(value[f"Description_{lang}"])}"\n'
            job_translations[lang][f'Class_Skill_Desc_{value["Name_en"]}'] = deal_with_extras_in_text(actiontransient_trans[key][f"Description_{lang}"])
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
        for lang in LANGUAGES:
            result += f'          {lang}: "{t[f"Name_{lang}"]}"\n'
            job_translations[lang][f'Class_Trait_Name_{t["Name_en"]}'] = t[f"Name_{lang}"]
        result += f'        icon: "{getImage(t["Icon"])}"\n'
        result += f'        level: "{traits[key]["Level"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{deal_with_extras_in_text(traitstransient_trans[key][f"Description_{lang}"])}"\n'
            job_translations[lang][f'Class_Trait_Desc_{t["Name_en"]}'] = deal_with_extras_in_text(traitstransient_trans[key][f"Description_{lang}"])
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
        for lang in LANGUAGES:
            result += f'          {lang}: "{value[f"Name_{lang}"]}"\n'
            job_translations[lang][f'Class_Skill_Name_{value["Name_en"]}'] = value[f"Name_{lang}"]
        result += f'        title_id: "{key}"\n'
        result += f'        icon: "{getImage(value["Icon"])}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{deal_with_extras_in_text(value[f"Description_{lang}"])}"\n'
            job_translations[lang][f'Class_Skill_Desc_{value["Name_en"]}'] = deal_with_extras_in_text(value[f"Description_{lang}"])
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
        for lang in LANGUAGES:
            result += f'          {lang}: "{value[f"col_0_{lang}"]}"\n'
            job_translations[lang][f'Class_Skill_Name_{value["col_0_en"]}'] = value[f"col_0_{lang}"]
        result += f'        title_id: "{key}"\n'
        result += '        phases:\n'
        result += '          - phase: "05"\n'
    return result


def addChocobo(actions, actions_trans, actiontransient_trans, traits, traits_trans, traitstransient_trans, klass_translations, callback_function, addExtraIcons):
    global job_translations
    cb_load_global_data(actions, actions_trans, actiontransient_trans, traits, traits_trans, traitstransient_trans)

    # prepare translation elements
    job_translations = {}
    for lang in LANGUAGES:
        job_translations[lang] = {}

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
    icon = getImage("062000/062143_hr1.webp")
    filecontent += f'jobicon: "{icon}"\n'

    filecontent += "extraicons:\n"
    filecontent += addExtraIcons(job, icon, icon)
    filecontent += 'slug: "klassen_und_jobs_' + job.lower() + '"\n'
    if os.path.exists(f"{os.getcwd()}/../assets/img/content/klassen/{job}.webp"):
        filecontent += f'image: "/assets/img/content/klassen/{job}.webp"\n'
    else:
        print(f"Missing img: {job}.webp")
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
    filecontent += f'  - title: "{job_d["Name_en"]}"\n'
    for lang in LANGUAGES:
        klass_translations[lang][f'Content_Title_{job_d["Name_en"]}'] = job_d[f"Name_{lang}"]
    filecontent += "    id: \"" + "boss0\"\n"
    # todo add chocobo stuff
    filecontent += addChocoboPartnerSkills()
    filecontent += addRennChocoboSkills_trans()
    # addRennChocoboStatus()
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
    # filecontent += "      - phase: \"04\"\n"
    # filecontent += "        name: \"Renn-Chocobo-Status\"\n"
    filecontent += "      - phase: \"04\"\n"
    filecontent += "        name: \"Renn-Chocobo-Items\"\n"
    filecontent += "      - phase: \"05\"\n"
    filecontent += "        name: \"Renn-Chocobo-Missions\"\n"
    filecontent += '---\n'

    callback_function(job_translations, "chocobo")

    filename = f"klassen_und_jobs/2013-01-01--2.0--0--{job}.md"
    with open(filename, encoding="utf8") as f:
        doc = f.read()
    if not doc == filecontent:
        with open(filename, "w", encoding="utf8") as f:
            f.write(filecontent)
