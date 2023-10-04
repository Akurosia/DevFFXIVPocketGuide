from ffxiv_aku import *

items_trans = loadDataTheQuickestWay("item_all.json", translate=True)
airshipexplorationpoint_trans = loadDataTheQuickestWay("airshipexplorationpoint_all.json", translate=True)
submarineexploration_trans = loadDataTheQuickestWay("submarineexploration_all.json", translate=True)
submarinemap_trans = loadDataTheQuickestWay("submarinemap_all.json", translate=True)
data = readJsonFile(r"T:\var\www\ffxiv\front\housing_missions\data2.json")


locations_translator = {
    "Wolkenmeer": "Wolkenmeer",
    "Deep-sea Site (Lv. 1-50) ":"Tiefsee",
    "Sea of Ash (Lv. 50-70) ": "Verbranntes Meer",
    "Sea of Jade (Lv. 70-90) ": "Jademeer",
    "Sirensong Sea (Lv. 90-105) ": "Sirenen-See",
    "The Lilac Sea (Lv. 105-) ": "Das Fliedermeer"
}

def get_translated_unlocks(asd, search):
    for key, value in asd.items():
        if value.get("Destination_en", value.get("Name_en", "")).lower() == search.lower():
            #print(value)
            return value
    #print("ERROR")
    return {}


def get_x_items(items):
    result = {'de': "", 'en': "", 'fr': "", 'ja': "", 'cn': "", 'ko': ""}
    itemnames = [x for x in items]
    for item in itemnames:
        for key, value in items_trans.items():
            if item == value['Name_en']:
                for lang in ['de', 'en', 'fr', 'ja', 'cn', 'ko']:
                    result[lang] += value[f'Name_{lang}'] + "</br>"
                break
    return result


def get_submarine_map(name):
    for key, value in submarinemap_trans.items():
        if name.lower() == value['Name_de'].lower():
            return value
    return {
            'Name_de': "Wolkenmeer",
            'Name_en': "Sea of Clouds",
            'Name_fr': "Mer de nuages",
            'Name_ja': "雲海",
            'Name_cn': "云海",
            'Name_ko': "구름바다"
    }


def run():
    r_data = ""
    r_data += "---\n"
    r_data += 'layout: airship_submarine\n'
    r_data += 'title: Airship and Submarine\n'
    r_data += 'last_modified_at: 2022-03-17\n'
    r_data += 'permalink: /airship_submarine/\n'
    r_data += 'description: "Search through class and jobs guides on the FFXIV Pocket Guide."\n'
    r_data += 'page_type: index\n'
    r_data += 'page_category: airship_submarine\n'
    r_data += 'locations:\n'
    for location, stops in data.items():
        location = locations_translator[location]
        # this will sort all entry to avoid 2 equal cases
        w_data = submarineexploration_trans
        if location == "Wolkenmeer":
            w_data = airshipexplorationpoint_trans

        r_data += f'    - name:\n'
        smm = get_submarine_map(location)
        for lang in ['de', 'en', 'fr', 'ja', 'cn', 'ko']:
            r_data += f'        {lang}: "{smm["Name_"+lang]}"\n'
        r_data += f'      stops:\n'
        for key in sorted([int(x) for x in w_data]):
            value = w_data[str(key)]
            for name, stop_data in stops.items():
                if not name.lower() == value.get("Destination_en", value.get("Name_en", "")).lower():
                    continue
                r_data += f'        - name:\n'
                for lang in ['de', 'en', 'fr', 'ja', 'cn', 'ko']:
                    r_data += f'            {lang}: "{value.get("Destination_"+lang, value.get("Name_"+lang, ""))}"\n'
                r_data += f'          unlocked:\n'
                tmp_x = get_translated_unlocks(w_data, stop_data['unlocked_by'])
                for lang in ['de', 'en', 'fr', 'ja', 'cn', 'ko']:
                    r_data += f'            {lang}: "{tmp_x.get("Destination_"+lang, tmp_x.get("Name_"+lang, ""))}"\n'
                r_data += f'          level: "{stop_data["lvl"]}"\n'
                r_data += f'          exp: "{stop_data["exp"]}"\n'
                if stop_data.get('alias'):
                    r_data += f'          alias: "{stop_data["alias"]}"\n'
                r_data += f'          items:\n'
                x_items = get_x_items(stop_data["items"])
                for lang in ['de', 'en', 'fr', 'ja', 'cn', 'ko']:
                    r_data += f'            {lang}: "{x_items.get(lang, "")[:-5]}"\n'
    r_data += "---\n"
    #print(r_data)

    filename = f"../_pages/airship_submarine/index.html"
    with open(filename, encoding="utf8") as f:
        doc = f.read()
    if not doc == r_data:
        with open(filename, "w", encoding="utf8") as f:
            f.write(r_data)

if __name__ == "__main__":
    run()
