from ffxiv_aku import *
from helper import getImage

def get_pomanders():
    pomander_table = """                <!-- pommander -->
                    <h3 class="guide__accordion-title">Tiefes Gewölbe Tongefäße</h3>
                    <div class="guide__mechanics-wrapper">
                        <table class="table-striped table-dark bg-charcoal text-light" style="text-align: center">
                            <thead>
                                <tr>
                                    <td>Icon</td>
                                    <td>Name</td>
                                    <td>Tooltip</td>
                                </tr>
                            </thead>
                            <tbody>\n"""
    deepdungeon_items = loadDataTheQuickestWay("DeepDungeonItem.json")
    for item_key, item_data in deepdungeon_items.items():
        additions = ""
        before = ""
        after = ""

        if item_data['Name_de'] == "":
            continue
        elif item_data['Name_de'] in ["Tongefäß der Weisung", "Tongefäß der Reinigung", "Tongefäß der Hast"]:
            additions = " (PT Only)"
            before = '{%- if page.contentname == "Pilgrim\'s Traverse" -%}'
        elif item_data['Name_de'] in ["Ätherogefäß der Macht", "Ätherogefäß der Schwäche", "Ätherogefäß der Trägheit"]:
            additions = " (EO Only)"
            before = '{%- if page.contentname == "Eureka Orthos" -%}'
        elif item_data['Name_de'] in ["Tongefäß der Feindversteinerung", "Tongefäß des Verschwindens", "Tongefäß der Feindschwächung"]:
            additions = " (HoH Only)"
            before = '{%- if page.contentname == "Heaven-on-High" -%}'
        elif item_data['Name_de'] in ["Tongefäß der Kuribu", "Tongefäß der Sukkuben", "Tongefäß der Manticoren"]:
            additions = " (PotD Only)"
            before = '{%- if page.contentname == "The Palace of the Dead" -%}'
        if before:
            after = "{%- endif -%}"

        icon = item_data['Icon']['path_hr1'].replace(".tex", ".webp").replace("ui/icon/", "")
        getImage(item_data['Icon'])
        pomander_table += f"""                                {before}<tr>
                                    <td><img loading="lazy" style="object-fit: scale-down; height: 40px" src="/assets/img/game_assets/{icon}" alt="{item_data['Name_en']}"/></td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">{item_data['Name_en']}{additions}</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">{item_data['Name_de']}{additions}</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">{item_data['Name_fr']}{additions}</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">{item_data['Name_ja']}{additions}</span>
                                    </td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">{item_data['Tooltip_en']}</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">{item_data['Tooltip_de']}</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">{item_data['Tooltip_fr']}</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">{item_data['Tooltip_ja']}</span>
                                    </td>
                                </tr>{after}\n"""
    pomander_table += """                            </tbody>
                        </table>
                    </div>\n"""
    print(pomander_table)


def get_stones_demis():
    pomander_table = """                <!-- magicstones/demis -->
                    <h3 class="guide__accordion-title">Tiefes Gewölbe Steine/Demis</h3>
                    <div class="guide__mechanics-wrapper">
                        <table class="table-striped table-dark bg-charcoal text-light" style="text-align: center">
                            <thead>
                                <tr>
                                    <td>Icon</td>
                                    <td>Name</td>
                                    <td>Tooltip</td>
                                </tr>
                            </thead>
                            <tbody>\n"""
    deepdungeon_magic = loadDataTheQuickestWay("DeepDungeonMagicStone.json")
    deepdungeon_demi = loadDataTheQuickestWay("DeepDungeonDemiclone.json")

    for file in [deepdungeon_magic, deepdungeon_demi]:
        for item_key, item_data in file.items():
            # this magic sets the fields acording to the sheet
            fields = ["Name", "Tooltip"]
            try:
                item_data[f"{fields[0]}_de"]
            except:
                fields = ["Singular", "Description"]

            additions = ""
            before = ""
            after = ""

            if item_data[f'{fields[0]}_de'] == "":
                continue
            elif item_data[f'{fields[0]}_de'] in ["Todesbeeren", "Handvoll Wandelwurz", "Handvoll Sakralharz"]:
                additions = " (PT Only)"
                before = '{%- if page.contentname == "Pilgrim\'s Traverse" -%}'
            elif item_data[f'{fields[0]}_de'] in ["", "", ""]:
                additions = " (EO Only)"
                before = '{%- if page.contentname == "Eureka Orthos" -%}'
            elif item_data[f'{fields[0]}_de'] in ["", "", ""]:
                additions = " (HoH Only)"
                before = '{%- if page.contentname == "Heaven-on-High" -%}'
            elif item_data[f'{fields[0]}_de'] in ["", "", ""]:
                additions = " (PotD Only)"
                before = '{%- if page.contentname == "The Palace of the Dead" -%}'
            if before:
                after = "{%- endif -%}"

            icon = item_data['Icon']['path_hr1'].replace(".tex", ".webp").replace("ui/icon/", "")
            getImage(item_data['Icon'])
            pomander_table += f"""                                {before}<tr>
                                        <td><img loading="lazy" style="object-fit: scale-down; height: 40px" src="/assets/img/game_assets/{icon}" alt="{item_data[f'{fields[0]}_en']}"/></td>
                                        <td>
                                            <span class="lang-toggle lang-toogle-en" style="display: none;">{item_data[f'{fields[0]}_en']}{additions}</span>
                                            <span class="lang-toggle lang-toogle-de" style="display: none;">{item_data[f'{fields[0]}_de']}{additions}</span>
                                            <span class="lang-toggle lang-toogle-fr" style="display: none;">{item_data[f'{fields[0]}_fr']}{additions}</span>
                                            <span class="lang-toggle lang-toogle-ja" style="display: none;">{item_data[f'{fields[0]}_ja']}{additions}</span>
                                        </td>
                                        <td>
                                            <span class="lang-toggle lang-toogle-en" style="display: none;">{item_data[f'{fields[1]}_en']}</span>
                                            <span class="lang-toggle lang-toogle-de" style="display: none;">{item_data[f'{fields[1]}_de']}</span>
                                            <span class="lang-toggle lang-toogle-fr" style="display: none;">{item_data[f'{fields[1]}_fr']}</span>
                                            <span class="lang-toggle lang-toogle-ja" style="display: none;">{item_data[f'{fields[1]}_ja']}</span>
                                        </td>
                                    </tr>{after}\n"""

    pomander_table += """                            </tbody>
                        </table>
                    </div>\n"""
    print(pomander_table)

if __name__ == "__main__":
    get_stones_demis()
