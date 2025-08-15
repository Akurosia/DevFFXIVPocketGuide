
import copy
import os
import traceback
from ffxiv_aku import get_any_Logdata, print_color_yellow, loadDataTheQuickestWay, print_color_red, pretty_json, print_pretty_json, writeJsonFile
try:
    from .convert_skills_to_guide_form_helper.helper import getImage
    from .helper import *
except:
    from convert_skills_to_guide_form_helper.helper import getImage
    from helper import *

LANGUAGES = ["de", "en", "fr", "ja"]
LANGUAGES_MAPPING = {
    "de": "de-DE",
    "en": "en-US",
    "fr": "fr-FR",
    "ja": "ja-JP",
}

translations = {
    "de": {},
    "en": {},
    "fr": {},
    "ja": {},
}

def translate_content_files(entry):
    global translations
    #exp = expansion_list[entry['categories']]
    #print(entry)
    for lang in LANGUAGES:
        if not translations[lang].get("achievments", None):
            translations[lang]["achievments"] = {}
        #name = entry[f'title_{lang}']
        translations[lang]["achievments"][f"Summary_Achievment_{entry['name']['en']}_Name"] = entry['name'][lang]
        translations[lang]["achievments"][f"Summary_Achievment_{entry['name']['en']}_Desc"] = entry['description'][lang]
    #print(translations)

def create_translation_files():
    global translations
    #print_pretty_json(translations)
    for lang, cat_data in translations.items():
        for cat, data in cat_data.items():
            writeJsonFile(f"assets/translations/achiements/{LANGUAGES_MAPPING[lang]}.json", data)

def get_achivment_kind():
    global translations
    kind = {}
    for key, value in achivmentkind.items():
        if not value['Name_de'] == "":
            kind[int(key)] = value['Name_de']

    for x in kind:
        for lang in LANGUAGES:
            if not translations[lang].get("achievments", None):
                translations[lang]["achievments"] = {}
            translations[lang]["achievments"][f"Summary_Achievment_{achivmentkind[str(x)]['Name_de']}_MainCat"] = achivmentkind[str(x)][f'Name_{lang}']
            translations[lang]["achievments"][f"Summary_Achievment_{achivmentkind[str(x)]['Name_de']}_MainCat"] = achivmentkind[str(x)][f'Name_{lang}']
    return kind


def get_achivment_categories():
    global translations
    cat = {}
    for key, value in achivmentcategory.items():
        if value['AchievementKind'].get('Name_de', '') == "":
            continue
        if not cat.get(value['AchievementKind'].get('Name_de', ''), None):
            cat[value['AchievementKind'].get('Name_de', '')] = {}
        cat[value['AchievementKind'].get('Name_de', '')][int(value['AchievementKind']['Order'])] = { "Name": value['Name_de'], "achievements": {} }
        for lang in LANGUAGES:
            if not translations[lang].get("achievments", None):
                translations[lang]["achievments"] = {}
            translations[lang]["achievments"][f"Summary_Achievment_{achivmentcategory[key]['Name_de']}_SubCat"] = achivmentcategory[key][f'Name_{lang}']
            translations[lang]["achievments"][f"Summary_Achievment_{achivmentcategory[key]['Name_de']}_SubCat"] = achivmentcategory[key][f'Name_{lang}']
    return cat


def get_achivment_per_categorie(basic_cat):
    cat = copy.deepcopy(basic_cat)
    #print_pretty_json(cat)
    for key, value in achivment.items():
        for cat_name, cat_data in cat.items():
            for sub_category_id, sub_category_data in cat_data.items():
                if value['AchievementCategory']['Name_de'] == sub_category_data['Name']:
                    order_id = float(value['AchievementCategory']['Order'])
                    if order_id == 0.0:
                        continue
                    while cat[cat_name][sub_category_id]['achievements'].get(order_id, None):
                        if cat[cat_name][sub_category_id]['achievements'].get(order_id, None):
                            #print(f"Douplicate ID found: {order_id}")
                            order_id += 0.1

                    cat[cat_name][sub_category_id]['achievements'][order_id] = {
                        "name": {
                            'de': achivment[key]['Name_de'],
                            'en': achivment[key]['Name_en'],
                            'fr': achivment[key]['Name_fr'],
                            'ja': achivment[key]['Name_ja'],
                        },
                        "description": {
                            'de': achivment[key]['Description_de'],
                            'en': achivment[key]['Description_en'],
                            'fr': achivment[key]['Description_fr'],
                            'ja': achivment[key]['Description_ja'],
                        },
                        "order": order_id,
                        "icon": getImage(value['Icon']),
                        "item": value['Item']['Name_de'],
                        "key": value['Key']['value'],
                        "points": value['Points'],
                        "title": value['Title']['Masculine_de'],
                        "type": value['Type']
                    }
    return cat


def write_yaml_data_for_guide(kind, a_data):
    doc_data = "---\n"
    doc_data += 'wip: "True"\n'
    doc_data += 'title: "Achivments"\n'
    doc_data += 'layout: index\n'
    doc_data += 'page_type: guide\n'
    doc_data += 'categories: "achivments"\n'
    doc_data += 'achivments:\n'

    for _id in sorted(kind):
        try:
            main_category = kind[_id]
            if main_category == "Legacy":
                continue
            if main_category == "Sammeln":
                main_category = "Synthese und Sammeln"
            data = a_data[main_category]
            for key in sorted(data):
                value = data[key]
                sub_category = value['Name']
                #print(value)
                for k in sorted(value['achievements']):
                    v = value['achievements'][k]
                    icon = getImage(v["icon"].replace(".tex", ".webp"))
                    order = round(v["order"], 1)
                    translate_content_files(v)
                    doc_data += ' - name:\n'
                    doc_data += f'     de: "{v["name"]["de"]}"\n'
                    doc_data += f'     en: "{v["name"]["en"]}"\n'
                    doc_data += f'     fr: "{v["name"]["fr"]}"\n'
                    doc_data += f'     ja: "{v["name"]["ja"]}"\n'
                    doc_data += '   description:\n'
                    doc_data += f'     de: "{v["description"]["de"]}"\n'
                    doc_data += f'     en: "{v["description"]["en"]}"\n'
                    doc_data += f'     fr: "{v["description"]["fr"]}"\n'
                    doc_data += f'     ja: "{v["description"]["ja"]}"\n'
                    doc_data += f'   main_category: "{main_category}"\n'
                    doc_data += f'   sub_category: "{sub_category}"\n'
                    doc_data += f'   icon: "{getImage(icon)}"\n'
                    doc_data += f'   order: "{order}"\n'
                    if not v['item'] == "":
                        doc_data += f'   item: "{v["item"]}"\n'
                    if not v['key'] == "":
                        doc_data += f'   key: "{v["key"]}"\n'
                    if not v['points'] == "":
                        doc_data += f'   points: "{v["points"]}"\n'
                    if not v['title'] == " / ":
                        doc_data += f'   title: "{v["title"]}"\n'
                    if not v['type'] == "":
                        doc_data += f'   type: "{v["type"]}"\n'
            #print_pretty_json(data)
        except Exception as e:
            print(traceback.format_exc())
            pass
    doc_data += '---\n'
    create_translation_files()
    with open("_posts/single_page_content/2013-01-01--2.0--1--achivments.md", "w", encoding="utf8") as f:
        f.write(doc_data)


def run():
    print(f"[ACHIEVMENTS] Script runs from: {os.getcwd()}")
    kind = get_achivment_kind()
    cat = get_achivment_categories()
    a_data = get_achivment_per_categorie(cat)
    write_yaml_data_for_guide(kind, a_data)
    print("[ACHIEVMENTS] Done Achivments!")


if __name__ == "__main__":
    os.chdir("..")
    run()

#{
#    'AchievementCategory': 'Saisonale Ereignisse',
#    'AchievementHideCondition': 'AchievementHideCondition#0',


#    'Type': '6',
#    'col_10': '0',
#    'col_12': '1',
#    'col_24': '1',
#    'col_4': '0',
#    'col_8': '255',
#    'col_9': '255'
#}
