from ffxiv_aku import *
from helper import getImage

def get_traps():
    return """
                <!-- traps -->
                    <h3 class="guide__accordion-title">Tiefes Gewölbe Fallen</h3>
                    <div class="guide__mechanics-wrapper">
                        <table class="table-striped table-dark bg-charcoal text-light" style="text-align: center">
                            <thead>
                                <tr>
                                    <td>Icon</td>
                                    <td>Name</td>
                                    <td>Description</td>
                                </tr>
                            </thead>
                            <tbody>
                                {%- if page.contentname == "The Palace of the Dead" -%}<tr>
                                    <td><img loading="lazy" style="object-fit: scale-down; height: 100px" src="/assets/img/content/potd/Froschfalle.webp" alt="Froschfalle.webp"/></td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Toading Trap (The Palace of the Dead)</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Froschfalle (Palast der Toten)</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Piège Batracien (Palais des morts)</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">トードトラップ (死者の宮殿)</span>
                                    </td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Turns you into a toad, preventing all actions and reducing max HP by 30% for 20 seconds. Beware snakes while you are toaded, as they will use Devour to instantly kill a toad</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Verwandelt dich in eine Kröte (Frosch), verhindert alle Aktionen und reduziert die maximale HP 20 Sekunden lang um 30 %. Hüte dich vor Schlangen, da sie im Krötenzustand Verschlingen einsetzen und dich sofort töten können.</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Vous transforme en crapaud, empêche toute action et réduit les PV max de 30 % pendant 20 secondes. Méfiez-vous des serpents, car ils utiliseront Dévorer pour tuer instantanément un crapaud.</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">20秒間行動不能になり、最大HPが30％減少してヒキガエルに変化する。変化中はヘビに注意。ヘビは「捕食」を使用し、ヒキガエルを即死させる。</span>
                                    </td>
                                </tr>{%- endif -%}
                                {%- if page.contentname == "Heaven-on-High" -%}<tr>
                                    <td><img loading="lazy" style="object-fit: scale-down; height: 100px" src="/assets/img/content/potd/Otterfalle.webp" alt="Otterfalle.webp"/></td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Odder Trap (Heaven-on-High)</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Otterfalle (Himmelssäule)</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Piège Loutre Choute (Pilier des Cieux)</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">ウソウソトラップ (アメノミハシラ)</span>
                                    </td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Turns you into an otter, preventing all actions and reducing max HP by 50% for 30 seconds</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Verwandelt dich in einen Otter (Geottert), verhindert alle Aktionen und reduziert die maximale HP 30 Sekunden lang um 50 %.</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Vous transforme en loutre, empêche toute action et réduit les PV max de 50 % pendant 30 secondes.</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">30秒間行動不能になり、最大HPが50％減少してカワウソに変化する。</span>
                                    </td>
                                </tr>{%- endif -%}
                                {%- if page.contentname == "Eureka Orthos" -%}<tr>
                                    <td><img loading="lazy" style="object-fit: scale-down; height: 100px" src="/assets/img/content/potd/Eulettenfalle.webp" alt="Eulettenfalle.webp"/></td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Owling Trap (Eureka Orthos)</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Eulettenfalle (Eureka Orthos)</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Piège Du Bébé Hibou (Eurêka Orthos)</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">オウレットトラップ (オルト・エウレカ)</span>
                                    </td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Turns you into an owlet, preventing all actions and reducing max HP by 50% for 30 seconds</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Verwandelt dich in ein Käuzchen (Eulette), verhindert alle Aktionen und reduziert die maximale HP 30 Sekunden lang um 50 %.</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Vous transforme en chouette, empêche toute action et réduit les PV max de 50 % pendant 30 secondes.</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">30秒間行動不能になり、最大HPが50％減少してフクロウの雛に変化する。</span>
                                    </td>
                                </tr>{%- endif -%}
                                {%- if page.contentname == "Pilgrim's Traverse" -%}<tr>
                                    <td><img loading="lazy" style="object-fit: scale-down; height: 100px" src="/assets/img/content/potd/Feenfalle.webp" alt="Feenfalle.webp"/></td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Fae Trap (Pilgrim's Traverse)</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Feenfalle (Pilgers Pfad)</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Piège féérique (Le Sanctuaire des pèlerins)</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">妖精トラップ (ピルグリム・トラバース)</span>
                                    </td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Turns you into a faerie, preventing all actions and reducing max HP by 50% for 30 seconds</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Verwandelt dich in eine Fee (Feewerdung), verhindert alle Aktionen und reduziert die maximale HP 30 Sekunden lang um 50 %.</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Vous transforme en fée, empêche toute action et réduit les PV max de 50 % pendant 30 secondes.</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">30秒間行動不能となり、最大HPが50％減少し、妖精の姿に変化する。</span>
                                    </td>
                                </tr>{%- endif -%}
                                <tr>
                                    <td><img loading="lazy" style="object-fit: scale-down; height: 100px" src="/assets/img/content/potd/hinderfalle.webp" alt="Hinderfalle.webp"/></td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Impeding Trap</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Hinderfalle</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Piège Inhibant</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">阻害トラップ</span>
                                    </td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Applies silence and pacification to everyone nearby (enemies included)</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Wirkt Stumm und Pacem auf alle in der Nähe (einschließlich Gegnern).</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Applique silence et pacification à tous les proches (ennemis inclus).</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">周囲の全員（敵を含む）にサイレンスとパシフィケーションを付与する。</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td><img loading="lazy" style="object-fit: scale-down; height: 100px" src="/assets/img/content/potd/Landmine.webp" alt="Landmine.webp"/></td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Landmine</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Mine</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Mine</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">地雷</span>
                                    </td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Deals damage equal to 80% of current health to everyone nearby (enemies included)</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Fügt allen in der Nähe (einschließlich Gegnern) Schaden in Höhe von 80 % der aktuellen HP zu.</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Inflige à tous les proches (ennemis inclus) des dégâts égaux à 80 % des PV actuels.</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">周囲の全員（敵を含む）に現在HPの80％分のダメージを与える。</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td><img loading="lazy" style="object-fit: scale-down; height: 100px" src="/assets/img/content/potd/Schwächefalle.webp" alt="Schwächefalle.webp"/></td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Enfeebling Trap</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Schwächfalle</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Piège Affaiblissant</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">弱体トラップ</span>
                                    </td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Increases damage taken by 30% and reduces damage dealt by 20%</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Fügt "Schöner Salat" zu. Erhöht erlittenen Schaden um 30 % und verringert verursachten Schaden um 20 %.</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Augmente les dégâts reçus de 30 % et réduit les dégâts infligés de 20 %.</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">被ダメージが30％増加し、与ダメージが20％減少する。</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td><img loading="lazy" style="object-fit: scale-down; height: 100px" src="/assets/img/content/potd/Ziehfalle.webp" alt="Ziehfalle.webp"/></td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Luring Trap</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Ziehfalle</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Piège Attracteur</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">誘引トラップ</span>
                                    </td>
                                    <td>
                                        <span class="lang-toggle lang-toogle-en" style="display: none;">Spawns 3 enemies with agro on the person who hit the trap</span>
                                        <span class="lang-toggle lang-toogle-de" style="display: none;">Beschwört 3 Feinde, die denjenigen ins Visier nehmen, der die Falle ausgelöst hat.</span>
                                        <span class="lang-toggle lang-toogle-fr" style="display: none;">Fait apparaître 3 ennemis qui prennent en cible la personne ayant déclenché le piège.</span>
                                        <span class="lang-toggle lang-toogle-ja" style="display: none;">罠を踏んだプレイヤーに敵視を向けた敵が3体出現する。</span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div\n"""

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
    return pomander_table


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
            elif item_data[f'{fields[0]}_de'] in ["Demiklon-Unei", "Demiklon-Doga", "Demiklon-Zwiebelritter"]:
                additions = " (EO Only)"
                before = '{%- if page.contentname == "Eureka Orthos" -%}'
            elif item_data[f'{fields[0]}_de'] in ["Ifrit-Zauberstein", "Titan-Zauberstein", "Garuda-Zauberstein", "Odin-Zauberstein"]:
                additions = " (HoH Only)"
                before = '{%- if page.contentname == "Heaven-on-High" -%}'

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
    return pomander_table

if __name__ == "__main__":
    with open("test.html", "w", encoding="utf8") as f:
        f.write("""<!-- Include from _includes/presets/DeedDungeonTraps -->
                <div class="guide__accordion-copy-wrapper akutables">""")
        f.write(get_traps())
        f.write(get_pomanders())
        f.write(get_stones_demis())
        f.write("""                </div>
<!-- END Include from _includes/presets/DeedDungeonTraps -->""")
