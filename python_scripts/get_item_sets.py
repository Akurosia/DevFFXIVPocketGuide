from ffxiv_aku import *

items: dict[str, dict[str, str]] = loadDataTheQuickestWay("item_all.json", translate=True)
mssi: dict[str, Any] = loadDataTheQuickestWay("MirageStoreSetItem.json", exd="raw-exd-all")
mssil: dict[str, Any] = loadDataTheQuickestWay("MirageStoreSetItemLookup.json")

LANGUAGES: list[str] = ["de", "en", "fr", "ja", "cn", "ko"]
LANGUAGES_MAPPING: dict[str, str] = {
    "de": "de-DE",
    "en": "en-US",
    "fr": "fr-FR",
    "ja": "ja-JP",
    "cn": "cn-CN",
    "ko": "ko-KR"
}
klass_translations = None
def get_class_translation_data():
    global klass_translations
    klass_translations = {}
    for lang in LANGUAGES:
        #klass_translations[lang] = readJsonFile(f'assets/translations/housing_missions/{LANGUAGES_MAPPING[lang]}.json')
        klass_translations[lang] = {}


def write_class_translation_data(data):
    for lang in LANGUAGES:
        klass_translations[lang] = writeJsonFile(f'../assets/translations/itemsets/{LANGUAGES_MAPPING[lang]}.json', data[lang])


def getImage(image: str|None, _type: str="icon") -> str:
    if image is None or image == "":
        return ""
    image = image.replace(".png", "_hr1.png")
    if _type == "icon":
        image = image.replace(f"ui/{_type}/", "")
    return image

id_to_gear: dict[str, str] = {
    'col_0':  'Unknown_9',
    'col_1':  'Unknown_10',
    'col_2':  '0_Kopf',
    'col_3':  '1_Body',
    'col_4':  '2_Hände',
    'col_5':  '3_Hose',
    'col_6':  '4_Schuhe',
    'col_7':  '5_Ohrringe',
    'col_8':  '6_Halskette',
    'col_9':  '7_Armreif',
    'col_10': '8_Ring'
}

def add_element(col_k: str, col_id: str, row: str, r: dict[str, list[str]]) -> tuple[str, dict[str, list[str]]]:
    global klass_translations
    if col_id == "0":
        row += "<td></td>\n"
        return row, r
    i_name: str
    i_icon: str
    i_name, i_icon = [items[col_id]['Name_de'], getImage(items[col_id]['Icon'])]
    r[id_to_gear[col_k]] = [i_name, i_icon]
    for lang in LANGUAGES:
        klass_translations[lang][f"Set_Item_{col_id}"] = items[col_id][f'Name_{lang}']
    href = f'<a data-translate="Set_Item_{col_id}" target="_blank" rel="noopener noreferrer" href="https://garlandtools.org/db/#item/{col_id}">{i_name}</a>'
    row += f"<td id='{i_name}' onclick='myFunction(this)'><span>{href}</span><br><img loading='lazy' style='height: 80px;width: 80px;' src='https://xivapi.com/i/{i_icon}' alt='{i_name}'></td>\n"
    return row, r

def run():
    global klass_translations
    print(f"[GIS] Start Get Item Set")
    print(os.getcwd())
    get_class_translation_data()
    counter: int = 0
    setcompleted: list[str] = ["0"]
    #html = "<html>\n"
    #html += '<head><link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">\n<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script> </head>'
    #html += "<body>\n"
    html = "<table class='table table-bordered table-dark table-striped text-light patch_table'>\n"
    html += "<thead> <tr> <th>Set</th> <th>Kopf</th>  <th>Body</th>  <th>Hände</th>  <th>Hose</th>  <th>Schuhe</th>  <th>Ohrringe</th>  <th>Halskette</th>  <th>Armreif</th>  <th>Ring</th> <th>GetFrom</th>  </tr> </thead>\n"
    html += "<tbody>\n"
    result: dict[str, str] = {}
    for key, value in mssil.items():
        for k, _set in value['MirageStoreSetItem'].items():
            setid = _set.replace("MirageStoreSetItem#", "")
            if not setid in setcompleted:
                setcompleted.append(setid)
                name, icon = [items[setid]['Name_de'], getImage(items[setid]['Icon'])]
                for lang in LANGUAGES:
                    klass_translations[lang][f"Set_{setid}"] = items[setid][f'Name_{lang}']
                row = "<tr>\n"
                href = f'<a data-translate="Set_{setid}" target="_blank" rel="noopener noreferrer" href="https://garlandtools.org/db/#item/{setid}">{name}</a>'
                row += f"<td id='{name}' onclick='myFunction(this)' ><span>{href}</span><br><img loading='lazy' style='height: 80px;width: 80px;' src='https://xivapi.com/i/{icon}' alt='{name}'></td>\n"
                r = {}
                for col_k, col_id in mssi[setid].items():
                    if col_k in ["col_0", "col_1", "col_10"]:
                        continue
                    row, r = add_element(col_k, col_id, row, r)
                row, r = add_element("col_10", mssi[setid]["col_10"], row, r)
                row += "<td></td>\n"
                row += "</tr>\n"
                if not result.get(name, None):
                    result[name] = row
                else:
                    print_color_red(name)
                    result[name+"2"] = row
                #html += row
                counter += 1
    for key in sorted(result):
        html += result[key]

    html += "</tbody>\n"
    html += "</table><br>\n"
    html += "</body>"
    #html += "<style> td { display: ruby-text;} </style>"
    html += """<script>
    function myFunction(copyText) {
      const textToCopy = '/isearch "' + copyText.getElementsByTagName("span")[0].innerText + '"';
      navigator.clipboard.writeText(textToCopy).then(() => {
        console.log('Copied: ', textToCopy);
      }).catch(err => {
        console.error('Failed to copy: ', err);
      });
    }
    </script>"""
    #html += "</html>"

    write_class_translation_data(klass_translations)
    with open("../_includes/itemsets.html", "w", encoding="utf8") as f:
        f.write(html)

if __name__ == "__main__":
    run()
