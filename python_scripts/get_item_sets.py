from ffxiv_aku import *
try:
    from .convert_skills_to_guide_form_helper.helper import getImage
    from .helper import *
except:
    from convert_skills_to_guide_form_helper.helper import getImage
    from helper import *


LANGUAGES: list[str] = ["de", "en", "fr", "ja"]
LANGUAGES_MAPPING: dict[str, str] = {
    "de": "de-DE",
    "en": "en-US",
    "fr": "fr-FR",
    "ja": "ja-JP",
}
klass_translations = None
path_of_main_script = ""
def get_class_translation_data():
    global klass_translations
    klass_translations = {}
    for lang in LANGUAGES:
        #klass_translations[lang] = readJsonFile(f'assets/translations/housing_missions/{LANGUAGES_MAPPING[lang]}.json')
        klass_translations[lang] = {}


def write_class_translation_data(data):
    for lang in LANGUAGES:
        klass_translations[lang] = writeJsonFile(f'{path_of_main_script}/assets/translations/itemsets/{LANGUAGES_MAPPING[lang]}.json', data[lang])


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

def add_element(col_k: str, data: dict[str, str], row: str, r: dict[str, list[str]]) -> tuple[str, dict[str, list[str]]]:
    global klass_translations
    col_id = str(data.get('row_id', 0))
    if col_id == "0":
        row += "        <td></td>\n"
        return row, r
    i_name: str
    i_icon: str
    i_name, i_icon = [data['Name_de'], getImage(data['Icon']['path'])]
    r[id_to_gear[col_k]] = [i_name, i_icon]
    for lang in LANGUAGES:
        klass_translations[lang][f"Set_Item_{col_id}"] = data[f'Name_{lang}']
    href = f'<a style="color: #007bff" data-translate="Set_Item_{col_id}" target="_blank" rel="noopener noreferrer" href="https://garlandtools.org/db/#item/{col_id}">{i_name}</a>'
    row += f"        <td id='{i_name}' onclick='myFunction(this)'><span>{href}</span><br><img loading='lazy' style='height: 80px;width: 80px;' src='{i_icon}' alt='{i_name}'></td>\n"
    return row, r

def run(main_script=r"C:\Users\kamot\Documents\GitHub\DevFFXIVPocketGuide"):
    global path_of_main_script
    global klass_translations
    path_of_main_script = main_script
    print(f"[GIS] Start Get Item Set")
    get_class_translation_data()
    counter: int = 0
    setcompleted: list[str] = ["0"]
    #html = "<html>\n"
    #html += '<head><link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">\n<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script> </head>'
    #html += "<body>\n"
    html = "  <table class='table table-bordered table-dark table-striped text-light patch_table'>\n"
    html += "    <thead> <tr> <th>Set</th> <th>Kopf</th>  <th>Body</th>  <th>Hände</th>  <th>Hose</th>  <th>Schuhe</th>  <th>Ohrringe</th>  <th>Halskette</th>  <th>Armreif</th>  <th>Ring</th> <th>GetFrom</th>  </tr> </thead>\n"
    html += "    <tbody>\n"
    result: dict[str, str] = {}
    for key, value in miragestoresetitemlookup.items():
        for mirageset in value['Item']:
            if mirageset.get('row_id', 0) == 0:
                continue
            setid = str(mirageset.get('row_id', 0))
            if not setid in setcompleted:
                setcompleted.append(setid)
                name, icon = [mirageset['Name_de'], getImage(mirageset['Icon']['path'])]
                for lang in LANGUAGES:
                    klass_translations[lang][f"Set_{setid}"] = mirageset[f'Name_{lang}']
                row = "      <tr>\n"
                href = f'<a style="color: #007bff" data-translate="Set_{setid}" target="_blank" rel="noopener noreferrer" href="https://garlandtools.org/db/#item/{setid}">{name}</a>'
                row += f"        <td id='{name}' onclick='myFunction(this)' ><span>{href}</span><br><img loading='lazy' style='height: 80px;width: 80px;' src='{icon}' alt='{name}'></td>\n"
                r = {}
                row, r = add_element("0", miragestoresetitem[setid]['Head'], row, r)
                row, r = add_element("1", miragestoresetitem[setid]['Body'], row, r)
                row, r = add_element("2", miragestoresetitem[setid]['Hands'], row, r)
                row, r = add_element("3", miragestoresetitem[setid]['Legs'], row, r)
                row, r = add_element("4", miragestoresetitem[setid]['Feet'], row, r)

                row, r = add_element("5", miragestoresetitem[setid]['Earrings'], row, r)
                row, r = add_element("6", miragestoresetitem[setid]['Necklace'], row, r)
                row, r = add_element("7", miragestoresetitem[setid]['Bracelets'], row, r)
                row, r = add_element("8", miragestoresetitem[setid]['Ring'], row, r)

                #row, r = add_element("col_10", miragestoresetitem[setid]["col_10"], row, r)
                row += "        <td></td>\n"
                row += "      </tr>\n"
                if not result.get(name, None):
                    result[name] = row
                else:
                    print_color_red(name)
                    result[name+"2"] = row
                #html += row
                counter += 1
    for key in sorted(result):
        html += result[key]

    html += "    </tbody>\n"
    html += "  </table><br>\n"
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
    with open(f"{path_of_main_script}/_includes/single_pages/itemsets.html", "w", encoding="utf8") as f:
        f.write(html)

if __name__ == "__main__":
    run()
