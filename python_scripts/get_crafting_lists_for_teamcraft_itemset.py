from ffxiv_aku import *

items: dict[str, dict[str, str]] = loadDataTheQuickestWay("item_all.json", translate=True)
mssi: dict[str, Any] = loadDataTheQuickestWay("MirageStoreSetItem.json", exd="raw-exd-all")
mssil: dict[str, Any] = loadDataTheQuickestWay("MirageStoreSetItemLookup.json")

id_to_gear: dict[str, str] = {
    '0': '0_Kopf',
    '1': '1_Body',
    '2': '2_Hände',
    '3': '3_Hose',
    '4': '4_Schuhe',
    '5': '5_Ohrringe',
    '6': '6_Halskette',
    '7': '7_Armreif',
    '8': '8_Ring'
}

def add_element(col_k: str, col_id: dict[str, str], row: str, r: dict[str, list[str]]) -> tuple[str, dict[str, list[str]]]:
    global klass_translations
    if col_id == "0":
        return row, r
    i_name: str
    i_name = items[col_id]['Name_de']
    r[id_to_gear[col_k]] = i_name
    print(f"  {i_name}")
    row += f"item/{col_id}%7C"
    return row, r

def run():
    counter: int = 0
    setcompleted: list[str] = ["0"]

    couner = 0

    row = ""
    result: dict[str, str] = {}
    for key, value in mssil.items():
        for k, _set in value['MirageStoreSetItem'].items():
            setid = _set.replace("MirageStoreSetItem#", "")
            if not setid in setcompleted:
                setcompleted.append(setid)
                name = items[setid]['Name_de']
                if not name in ["Abenteurer-Kapuzenwestenset", "Boulevardier-Set", "Chocobo-Schlafset", "Coeurl-Bikinitop-Pareo-Set", "Coeurl-Bikinitop-Tanga-Set", "Coeurl-Talisman-Maro-Set", "Coeurl-Talisman-Strandhose-Set", "Dalmascanisches Kleidungsset", "Dhalmelleder-Mantelset", "Einfaches Schlafset", "Feuermond-Jackenset", "Flanellrockset mit Hosenträgern", "Frühlingskleid-Set", "Gesellschafts-Set", "Gletscher-Set", "Glücks-Set", "Grenzland-Jackenset", "Grenzland-Kleidset", "Himmelsratten-Set der Heilung (Replik)", "Himmelsratten-Set der Magie (Replik)", "Himmelsratten-Set der Verteidigung (Replik)", "Himmelsratten-Set des Schlagens (Replik)", "Himmelsratten-Set des Spähens (Replik)", "Himmelsratten-Set des Verstümmelns (Replik)", "Himmelsratten-Set des Zielens (Replik)", "Hochland-Set", "Kaktor-Schlafset", "Kampfkunst-Set", "Kellner-Galawestenset", "Kellner-Westenset", "Leichtstahl-Set", "Leinen-Pfadfinderset", "Luftpiraten-Set der Heilung (Replik)", "Luftpiraten-Set der Magie (Replik)", "Luftpiraten-Set der Verteidigung (Replik)", "Luftpiraten-Set des Schlagens (Replik)", "Luftpiraten-Set des Spähens (Replik)", "Luftpiraten-Set des Verstümmelns (Replik)", "Luftpiraten-Set des Zielens (Replik)", "Mantelset des Städters", "Mondsichel-Nachttalar-Nachtkappen-Set", "Mondsichel-Nachttalar-Spitzkappen-Set", "Ramien-Hemdset", "Ramien-Ponchoset", "Ramien-Waffenrockset", "Regenbogen-Justaucorps-Set", "Regenbogen-Reifrockset", "Südsee-Set mit Hemd und Hose", "Südsee-Set mit Hemd und Rock", "Taft-Set", "Trauzeugen-Set", "Trauzeugin-Set", "Turalisches Händlerset", "Turalisches Reiseset", "Universitäts-Set", "Unordnungshüter-Set", "Uräusmantel-Set", "Winterliches Rockset", "Winterliches Weithosenset", "Wissenschaftlerset", "Zugeknöpftes Universitäts-Set", "Ärmelloses Kampfkunst-Set"]:
                    continue
                print(name)
                couner += 1
                r = {}
                for col_k, col_id in mssi[setid]["Item"].items():
                    row, r = add_element(col_k, col_id, row, r)

                if not result.get(name, None):
                    result[name] = row
                else:
                    print_color_red(name)
                    result[name+"2"] = row
                #html += row
                counter += 1
    print(counter)
    print("https://garlandtools.org/db/#group/Crafting%20List%7B" + row[:-3] + "%7D")

if __name__ == "__main__":
    run()
