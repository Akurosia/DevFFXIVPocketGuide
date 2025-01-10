
from ffxiv_aku import *
from natsort import natsorted

#storeFilesInTmp(state=True)
GCRankGridaniaFemaleText = loadDataTheQuickestWay("GCRankGridaniaFemaleText", translate=True)
GCRankGridaniaMaleText = loadDataTheQuickestWay("GCRankGridaniaMaleText", translate=True)
GCRankLimsaFemaleText = loadDataTheQuickestWay("GCRankLimsaFemaleText", translate=True)
GCRankLimsaMaleText = loadDataTheQuickestWay("GCRankLimsaMaleText", translate=True)
GCRankUldahFemaleText = loadDataTheQuickestWay("GCRankUldahFemaleText", translate=True)
GCRankUldahMaleText = loadDataTheQuickestWay("GCRankUldahMaleText", translate=True)

random_data = {
    #       Die Bruderschaft, Der Mahlstrom, Die Legion , Money, Unlock
    #       Gridania,Limsa,    Uldah,    Money,         Unlock
    "1":  ["083351", "083301", "083401", "10000 Taler", "[QUEST]"],
    "2":  ["083352", "083302", "083402", "15000 Taler", "2000 Taler"],
    "3":  ["083353", "083303", "083403", "20000 Taler", "3000 Taler"],
    "4":  ["083354", "083304", "083404", "25000 Taler", "4000 Taler"],
    "5":  ["083355", "083305", "083405", "30000 Taler", "5000 Taler + Bestiarium 01"],
    "6":  ["083356", "083306", "083406", "35000 Taler", "6000 Taler"],
    "7":  ["083357", "083307", "083407", "40000 Taler", "7000 Taler"],
    "8":  ["083358", "083308", "083408", "45000 Taler", "8000 Taler"],
    "9":  ["083359", "083309", "083409", "50000 Taler", "10000 Taler + Bestiarium 02"],
    "10": ["083360", "083310", "083410", "80000 Taler", "Lvl 40 Kommando"],
    "11": ["083361", "083311", "083411", "90000 Taler", "5 Kommando Dungeons + 'Eliminierung einer Eliteeinheit'"],
    "12": ["083362", "083312", "083412", "",            ""],
    "13": ["083363", "083313", "083413", "",            ""],
    "14": ["083364", "083314", "083414", "",            ""],
    "15": ["083365", "083315", "083415", "",            ""],
    "16": ["083366", "083316", "083416", "",            ""],
    "17": ["083367", "083317", "083417", "",            ""],
    "18": ["083368", "083318", "083418", "",            ""],
    "19": ["083369", "083319", "083419", "",            ""],
    "20": ["083370", "083320", "083420", "",            ""]
}

def run():
    r_data  = "---\n"
    r_data += 'layout: gcrank\n'
    r_data += 'title: Grand Company\n'
    r_data += 'last_modified_at: 2022-03-17\n'
    r_data += 'permalink: /gcrank/\n'
    r_data += 'description: "Search through Grand Company guides on the FFXIV Pocket Guide."\n'
    r_data += 'page_type: index\n'
    r_data += 'page_category: gcrank\n'
    r_data += 'gcrank:\n'
    print(f"{"Nr": >2} | {"Gridania Female": <35} | {"Gridania Male": <30} | {"Limsa Female": <30} | {"Limsa Male": <30} | {"Uldah Female": <30} | {"Uldah Male": <30}")
    for key in natsorted(GCRankGridaniaFemaleText):
        if key == "0":
            continue
        gcGridFemale = GCRankGridaniaFemaleText[key]['Singular_de']
        gcGridMale = GCRankGridaniaMaleText[key]['Singular_de']
        gcLimsaFemale = GCRankLimsaFemaleText[key]['Singular_de']
        gcLimsaMale = GCRankLimsaMaleText[key]['Singular_de']
        gcUldahFemale = GCRankUldahFemaleText[key]['Singular_de']
        gcUldahMale = GCRankUldahMaleText[key]['Singular_de']
        print(f"{key: >2} | {gcGridFemale: <35} | {gcGridMale: <30} | {gcLimsaFemale: <30} | {gcLimsaMale: <30} | {gcUldahFemale: <30} | {gcUldahMale: <30}")
        r_data += f'    - name:\n'
        r_data += f'        gridania_male: "{gcGridMale}" \n'
        r_data += f'        gridania_female: "{gcGridFemale}" \n'
        r_data += f'        limsa_male: "{gcLimsaMale}" \n'
        r_data += f'        limsa_female: "{gcLimsaFemale}" \n'
        r_data += f'        uldah_male: "{gcUldahMale}" \n'
        r_data += f'        uldah_female: "{gcUldahFemale}" \n'
        r_data += f'      id: "{key}"\n'
        r_data += f'      cap: "{random_data[key][3]}"\n'
        r_data += f'      unlocked_by: "{random_data[key][4]}"\n'
        r_data += f'      icons:\n'
        r_data += f'        gridania: "{random_data[key][0]}_hr1.webp"\n'
        r_data += f'        limsa: "{random_data[key][1]}_hr1.webp"\n'
        r_data += f'        uldah: "{random_data[key][2]}_hr1.webp"\n'
    r_data += f'    - name:\n'
    r_data += f'        gridania_male: "" \n'
    r_data += f'        gridania_female: "" \n'
    r_data += f'        limsa_male: "" \n'
    r_data += f'        limsa_female: "" \n'
    r_data += f'        uldah_male: "" \n'
    r_data += f'        uldah_female: "" \n'
    r_data += f'      id: "20"\n'
    r_data += f'      cap: "{random_data['20'][3]}"\n'
    r_data += f'      unlocked_by: "{random_data['20'][4]}"\n'
    r_data += f'      icons:\n'
    r_data += f'        gridania: "{random_data['20'][0]}_hr1.webp"\n'
    r_data += f'        limsa: "{random_data['20'][1]}_hr1.webp"\n'
    r_data += f'        uldah: "{random_data['20'][2]}_hr1.webp"\n'
    print(r_data)

    filename = "_pages/gcrank/index.html"
    with open(filename, encoding="utf8") as f:
        doc = f.read()
    if not doc == r_data:
        with open(filename, "w", encoding="utf8") as f:
            f.write(r_data)

if __name__ == "__main__":
    os.chdir("..")
    run()
    #print(["1", "2", "3"][-1])
