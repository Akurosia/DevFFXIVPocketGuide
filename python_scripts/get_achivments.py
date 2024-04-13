from ffxiv_aku import get_any_Logdata, print_color_yellow, loadDataTheQuickestWay, print_color_red, pretty_json, print_pretty_json
import copy


def get_achivment_kind():
    achivmentkind = loadDataTheQuickestWay("AchievementKind", translate=False)
    kind = {}
    for key, value in achivmentkind.items():
        if not value['Name'] == "":
            kind[int(key)] = value['Name']

    for x in kind:
        print(kind[x])

    return kind


def get_achivment_categories():
    achivmentcategory = loadDataTheQuickestWay("AchievementCategory", translate=False)
    cat = {}
    for key, value in achivmentcategory.items():
        if value['AchievementKind'] == "":
            continue
        if not cat.get(value['AchievementKind'], None):
            cat[value['AchievementKind']] = {}
        cat[value['AchievementKind']][int(value['Order'])] = { "Name": value['Name'], "achievements": {} }
    return cat


def get_achivment_per_categorie(basic_cat):
    achivment = loadDataTheQuickestWay("Achievement", translate=False)
    trans_achivment = loadDataTheQuickestWay("Achievement", translate=True)
    cat = copy.deepcopy(basic_cat)
    #print_pretty_json(cat)
    for key, value in achivment.items():
        for cat_name, cat_data in cat.items():
            for sub_category_id, sub_category_data in cat_data.items():
                if value['AchievementCategory'] == sub_category_data['Name']:
                    order_id = float(value['Order'])
                    if order_id == 0.0:
                        continue
                    while cat[cat_name][sub_category_id]['achievements'].get(order_id, None):
                        if cat[cat_name][sub_category_id]['achievements'].get(order_id, None):
                            print(f"Douplicate ID found: {order_id}")
                            order_id += 0.1

                    cat[cat_name][sub_category_id]['achievements'][order_id] = {
                        "name": {
                            'de': trans_achivment[key]['Name_de'],
                            'en': trans_achivment[key]['Name_en'],
                            'fr': trans_achivment[key]['Name_fr'],
                            'ja': trans_achivment[key]['Name_ja'],
                            'cn': trans_achivment[key]['Name_cn'],
                            'ko': trans_achivment[key]['Name_ko']
                        },
                        "description": {
                            'de': trans_achivment[key]['Description_de'],
                            'en': trans_achivment[key]['Description_en'],
                            'fr': trans_achivment[key]['Description_fr'],
                            'ja': trans_achivment[key]['Description_ja'],
                            'cn': trans_achivment[key]['Description_cn'],
                            'ko': trans_achivment[key]['Description_ko']
                        },
                        "order": order_id,
                        "icon": value['Icon'],
                        "item": value['Item'],
                        "key": value['Key'],
                        "points": value['Points'],
                        "title": value['Title'],
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
            data = a_data[main_category]
            for key in sorted(data):
                value = data[key]
                sub_category = value['Name']
                #print(value)
                for k in sorted(value['achievements']):
                    v = value['achievements'][k]
                    icon = v["icon"].replace(".tex", ".png").replace("ui/icon/", "")
                    order = round(v["order"], 1)
                    doc_data += ' - name:\n'
                    doc_data += f'     de: "{v["name"]["de"]}"\n'
                    doc_data += f'     en: "{v["name"]["en"]}"\n'
                    doc_data += f'     fr: "{v["name"]["fr"]}"\n'
                    doc_data += f'     ja: "{v["name"]["ja"]}"\n'
                    doc_data += f'     cn: "{v["name"]["cn"]}"\n'
                    doc_data += f'     ko: "{v["name"]["ko"]}"\n'
                    doc_data += f'   description:\n'
                    doc_data += f'     de: "{v["description"]["de"]}"\n'
                    doc_data += f'     en: "{v["description"]["en"]}"\n'
                    doc_data += f'     fr: "{v["description"]["fr"]}"\n'
                    doc_data += f'     ja: "{v["description"]["ja"]}"\n'
                    doc_data += f'     cn: "{v["description"]["cn"]}"\n'
                    doc_data += f'     ko: "{v["description"]["ko"]}"\n'
                    doc_data += f'   main_category: "{main_category}"\n'
                    doc_data += f'   sub_category: "{sub_category}"\n'
                    doc_data += f'   icon: "{icon}"\n'
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
        except Exception:
            pass
    doc_data += '---\n'

    with open("../_posts/single_page_content/2013-01-01--2.0--1--achivments.md", "w", encoding="utf8") as f:
        f.write(doc_data)


if __name__ == "__main__":
    kind = get_achivment_kind()
    cat = get_achivment_categories()
    a_data = get_achivment_per_categorie(cat)
    #print_pretty_json(a_data)
    write_yaml_data_for_guide(kind, a_data)


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
