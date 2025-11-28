from PIL.ImageFile import ImageFile
from ffxiv_aku import *
from PIL import Image, ImageDraw, ImageFont
try:

    from .helper import *
    from .convert_skills_to_guide_form_helper.helper import LANGUAGES, LANGUAGES_MAPPING
    from .fileimports import *
except:
    from convert_skills_to_guide_form_helper.helper import LANGUAGES, LANGUAGES_MAPPING
    from fileimports import *
    from helper import *

#treasurespot = loadDataTheQuickestWay("TreasureSpot.json")
#treasurehuntrank = loadDataTheQuickestWay("TreasureHuntRank.json")
#treasurehunttexture = loadDataTheQuickestWay("TreasureHuntTexture.json")

#ttype = loadDataTheQuickestWay("territorytype_all.json", translate=True)
#items  = loadDataTheQuickestWay("item_all.json", translate=True)
#placename = loadDataTheQuickestWay("placename_all.json", translate=True)
#contentfindercondition = loadDataTheQuickestWay("contentfindercondition_all.json", translate=True)
map_translations = None

def cache_results(func):
    cache = {}  # Dictionary to store cached results
    def wrapper(*args):
        if args in cache:
            return cache[args]  # Return cached result
        result = func(*args)  # Call the original function
        cache[args] = result  # Cache the result
        return result

    return wrapper

@cache_results
def get_placename(name):
    for key, value in placename.items():
        if value['Name_de'] == name:
            return value

@cache_results
def get_contentfindercondition(name):
    for key, value in contentfindercondition.items():
        if value['Name_de'] == name:
            return value


@cache_results
def get_item(name):
    for key, value in items.items():
        if value['Name_de'] == name:
            return value


def get_map_translation_data() -> None:
    global map_translations
    map_translations = {}
    for lang in LANGUAGES:
        #map_translations[lang] = readJsonFile(f'assets/translations/klassen/{LANGUAGES_MAPPING[lang]}.json')
        map_translations[lang] = {}


def write_map_translation_data() -> None:
    global map_translations
    origin: str = os.getcwd()
    os.chdir("..")
    for lang in LANGUAGES:
        writeJsonFile(f'assets/translations/treasuremaps/{LANGUAGES_MAPPING[lang]}.json', map_translations[lang])
    os.chdir(origin)


def add_watermark(image, watermark_text, font_path="arial.ttf", font_size=30):
    # Create a copy of the image to avoid modifying the original
    watermarked_image = image.copy()
    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font not found. Using default font.")
        font = ImageFont.load_default()

    # Calculate position for watermark (bottom-right corner)
    text_bbox = font.getbbox(watermark_text)  # Get bounding box of the text
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    padding = 10
    position = (watermarked_image.width - text_width - padding, watermarked_image.height - text_height - padding)

    # Add watermark text with semi-transparent fill
    watermark_color = (255, 255, 255, 128)  # White with 50% transparency
    watermark_layer = Image.new("RGBA", watermarked_image.size, (0, 0, 0, 0))
    watermark_draw = ImageDraw.Draw(watermark_layer)
    watermark_draw.text(position, watermark_text, font=font, fill=watermark_color)

    # Composite the watermark layer with the original image
    watermarked_image = Image.alpha_composite(watermarked_image.convert("RGBA"), watermark_layer)

    return watermarked_image.convert("RGB")


def get_croped_image(_id: str = "0"):
    # Load the overlay image (e.g., icon or stamp)
    file_name: str = treasurehunttexture[_id]['Unknown0'].lower()
    overlay_path = f"P:/extras/images/ui/uld/uld_data/{file_name}_hr1.tex.png"  # Replace with your overlay image path
    overlay_image = Image.open(overlay_path)
    _, height = overlay_image.size
    overlay_cropped = overlay_image.crop((0, 0, 450, height))

    # Resize the cropped overlay image if necessary
    x = 220
    y = 200
    overlay_size = (x, y)  # Adjust the size as needed
    overlay_cropped = overlay_cropped.resize(overlay_size)
    return overlay_cropped, int(x/2), int(y/2)


def get_x_image(_id: str = "0"):
    # Load the overlay image (e.g., icon or stamp)
    file_name: str = treasurehunttexture[_id]['Unknown0'].lower()
    overlay_path = f"P:/extras/images/ui/uld/uld_data/{file_name}_hr1.tex.png"  # Replace with your overlay image path
    overlay_image = Image.open(overlay_path)

    # Crop the overlay image to the first third
    overlay_cropped = overlay_image.crop((1010, 200, 1100, 260))

    # Resize the cropped overlay image if necessary
    x = 40
    y = 30
    overlay_size = (x, y)  # Adjust the size as needed
    overlay_cropped = overlay_cropped.resize(overlay_size)
    return overlay_cropped, int(x/2), int(y/2)


def get_sub_images(original_image, overlay_cropped, x, y, output_path, name):
    modified_image = original_image.copy()
    w,h = overlay_cropped.size
    modified_image.paste(overlay_cropped, (x, y), overlay_cropped if overlay_cropped.mode == 'RGBA' else None)
    modified_image = modified_image.crop((x, y, x+w, y+h))

    font1 = ImageFont.truetype('timesbd.ttf',50)
    write = ImageDraw.Draw(modified_image)
    write.text(xy=(0,0), text=chr(name), fill=(255, 255, 255), font=font1)

    font1 = ImageFont.truetype('timesbd.ttf',40)
    write = ImageDraw.Draw(modified_image)
    write.text(xy=(3,5), text=chr(name), fill=(0, 0, 0), font=font1)


    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.exists(output_path + f"{chr(name)}.webp"):
        modified_image = add_watermark(modified_image, "AkurosiaKamo")
        modified_image.save(output_path + f"{chr(name)}.webp", format='WEBP', lossless=True)
        print(f"Saved modified image: {output_path}{chr(name)}.webp")

treasuredungeons: dict[str, list[str]] = {
    "12243": ["Aquapolis"],
    "17836": ["Kanäle von Uznair", "Glücksaltäre von Uznair"],
    "19770": ["Vergessene Kanäle von Uznair"],
    "26745": ["Verliese von Lyhe Ghiah", "Das Karussell von Lyhe Ghiah"],
    "36612": ["Euphoratron"],
    "39591": ["Gymnasion Agonon"],
    "43557": ["Cenote Ja Ja Gural"],
}

plevelmax = {
    "2": "50",
    "3": "60",
    "4": "70",
    "5": "80",
    "6": "90",
    "7": "100",
}

def code_for_image(overlay_id, posible_maps, location, item_name):
    #print(f"code_for_image({overlay_id=}, {posible_maps=}, {location=}, {item_name=})")

    image_path: str = posible_maps[0]
    original_image: ImageFile = Image.open(image_path)
    modified_image: Image.Image = original_image.copy()

    overlay_cropped, x_off, y_off = get_croped_image(overlay_id)
    overlay_x_cropped, xx_off, xy_off = get_x_image(overlay_id)
    overlay_cropped.paste(overlay_x_cropped, (x_off-xx_off, y_off-xy_off), overlay_x_cropped if overlay_x_cropped.mode == 'RGBA' else None)

    # the followign block will save the empty map for leaflet usage
    tmp_out: str = f"../assets/img/treasuremaps/{item_name}/"
    if not os.path.exists(tmp_out):
        os.makedirs(tmp_out)
    if not os.path.exists(tmp_out + f"empty_map.webp"):
        overlay_cropped.save(tmp_out + f"empty_map.webp", format='WEBP', lossless=True)

    w, h = modified_image.size
    full_placename = None
    _extra: list[str] = []
    for i, coord in enumerate(location):
        x, y , placename = coord
        full_placename = get_placename(placename)

        output_path: str = f"../assets/img/treasuremaps/{item_name}/{placename}/"
        x+= w/2
        y+= h/2
        modified_image.paste(overlay_cropped, (int(x)-x_off, int(y)-y_off), overlay_cropped if overlay_cropped.mode == 'RGBA' else None)

        font1 = ImageFont.truetype('timesbd.ttf',50)
        write = ImageDraw.Draw(modified_image)
        write.text(xy=(int(x)-x_off, int(y)-y_off), text=chr(65+i), fill=(255, 255, 255), font=font1)

        font1 = ImageFont.truetype('timesbd.ttf',40)
        write = ImageDraw.Draw(modified_image)
        write.text(xy=(int(x)-x_off+3, int(y)-y_off+5), text=chr(65+i), fill=(0, 0, 0), font=font1)

        get_sub_images(original_image, overlay_cropped, int(x)-x_off, int(y)-y_off, output_path, 65+i)
        _extra.append(chr(65+i))
    return _extra, full_placename, output_path, modified_image, placename

GETPATCHDATA = {
    "Timeworn Leather Map":             ("2.10", "2.1"),
    "Timeworn Goatskin Map":            ("2.10", "2.1"),
    "Timeworn Toadskin Map":            ("2.10", "2.1"),
    "Timeworn Boarskin Map":            ("2.10", "2.1"),
    "Timeworn Peisteskin Map":          ("2.10", "2.1"),
    "Mysterious Map":                   ("2.28", "2.28"),
    "Unhidden Leather Map":             ("2.30", "2.3"),
    "Thorne Dynasty Map":               ("2.51", "2.51"),
    "Timeworn Archaeoskin Map":         ("3.00", "3.0"),
    "Timeworn Wyvernskin Map":          ("3.00", "3.0"),
    "Timeworn Dragonskin Map":          ("3.00", "3.0"),
    "Timeworn Gaganaskin Map":          ("4.00", "4.0"),
    "Timeworn Gazelleskin Map":         ("4.00", "4.0"),
    "Timeworn Thief's Map":             ("4.10", "4.1"),
    "Seemingly Special Timeworn Map":   ("4.58", "4.58"),
    "Timeworn Gliderskin Map":          ("5.00", "5.0"),
    "Timeworn Zonureskin Map":          ("5.00", "5.0"),
    "Ostensibly Special Timeworn Map":  ("5.50", "5.5"),
    "Timeworn Saigaskin Map":           ("6.00", "6.0"),
    "Timeworn Kumbhiraskin Map":        ("6.00", "6.0"),
    "Timeworn Ophiotauroskin Map":      ("6.30", "6.3"),
    "Potentially Special Timeworn Map": ("6.30", "6.3"),
    "Conceivably Special Timeworn Map": ("6.40", "6.4"),
    "Timeworn Br'aaxskin Map":          ("7.00", "7.0"),
    "Timeworn Loboskin Map":            ("7.00", "7.0"),
    "Timeworn Gargantuaskin Map":       ("7.30", "7.3"),
}
def show_image(circle_coords: dict[str, dict[str, Any]]):
    global map_translations
    for tmap, locations in circle_coords.items():
        #if not tmap == "1":
        #    continue
        output_path: str = ""
        placename: str = ""
        overlay_id = str(treasurehuntrank[tmap]['TreasureHuntTexture'])
        item_name = treasurehuntrank[tmap]['ItemName']['Name_de']
        active_treasuremap = get_item(item_name)
        patch , patch2 = GETPATCHDATA[active_treasuremap["Name_en"]]

        _date = patchversions[patch]["date"].replace(".", "-")
        _post = '---\n'
        _post += 'wip: "True"\n'
        _post += f'id: "{int(active_treasuremap['row_id'])}"\n'
        _post += 'title:\n'
        for lang in LANGUAGES:
            _post += f'  {lang}: "{active_treasuremap["Name_"+lang]}"\n'
            map_translations[lang][f'Map_Name_{active_treasuremap["Name_"+"en"]}'] = active_treasuremap["Name_"+lang]
        _post += 'layout: treasuremap\n'
        _post += 'page_type: guide\n'
        _post += 'categories: "treasuremap"\n'
        _post += 'instanceType: "treasuremap"\n'
        _post += f'date: "{patchversions[patch]["date"]}"\n'
        _post += f'patchNumber: "{patch2}"\n'
        _post += f'patchName: "{patchversions[patch]["name"]}"\n'
        _post += f'expac: "{patchversions[patch]["pname"]}"\n'
        _post += 'image: "/assets/img/content/klassen/Chocobo.webp"\n'
        _post += 'terms:\n'
        _post += '    - term: "TreasureMaps"\n'
        _post += f'    - term: "{patchversions[patch]["name"]}"\n'
        _post += f'sortid: {tmap}\n'
        _post += f'order: {tmap}\n'
        plvl = plevelmax[patch[0]]
        _post += f'plvl: {plvl}\n'
        _post += f'slug: "{fix_slug(active_treasuremap["Name_de"])}"\n'
        #if treasurehuntrank[tmap]["InstanceMap"]:
        #    _post += f'instancemap: {treasurehuntrank[tmap]["InstanceMap"]}\n'
        _post += f'maxpartysize: {treasurehuntrank[tmap]["MaxPartySize"]}\n'
        if treasuredungeons.get(str(int(active_treasuremap['row_id'])), None):
            _post += f'treasuredungeons:\n'
            for k in treasuredungeons[str(int(active_treasuremap['row_id']))]:
                cfc = get_contentfindercondition(k)
                _post += f'  - name: "{cfc["Name_en"]}"\n'
                for lang in LANGUAGES:
                    map_translations[lang][f'TreasureDungeon_Name_{cfc["Name_"+"en"]}'] = cfc["Name_"+lang]

        _post += f'zones:\n'
        for _id, location in locations.items():
            folder: str = _id[:3]
            name: str = _id.split("/")[0]
            posible_maps: list[str] = []
            for x in glob(f"P:/extras/images/ui/map/{folder}/{name}*.png"):
                if not len(x.split(" - ")) == 2: continue
                if "_event" in x: continue
                if "Altes Bootshaus.png" in x: continue
                if "Dom der Einkehr.png" in x: continue
                if "Nabaath-Mine.png" in x: continue
                if "Ruinen von Ronka.png" in x: continue
                posible_maps.append(x)
            if len(posible_maps) > 1:
                print(posible_maps)

            _extra, full_placename, output_path, modified_image, placename = code_for_image(overlay_id, posible_maps, location, item_name)

            _post += f'  - zonename: "{full_placename["Name_en"]}"\n'
            for lang in LANGUAGES:
                map_translations[lang][f'Map_Section_{full_placename["Name_"+"en"]}'] = full_placename["Name_"+lang]
            _post += f'    fullimage: "/assets/img/treasuremaps/{item_name}/{placename}/{placename}.webp"\n'
            _post += f'    subimage:\n'
            for img in _extra:
                _post += f'      - "/assets/img/treasuremaps/{item_name}/{placename}/{img}.webp"\n'
            # Generate output file name and save the image
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            if not os.path.exists(output_path + f"{placename}.webp"):
                modified_image = add_watermark(modified_image, "AkurosiaKamo")
                modified_image.save(output_path + f"{placename}.webp", format='WEBP', lossless=True)
                print(f"Saved modified image: {output_path}{placename}.webp")
        _post += '---'

        _id = f"0{patch[0]}-{patchversions[patch]["pname"]}"
        if not os.path.exists(f"../_posts/treasuremaps/{_id}/"):
            os.makedirs(f"../_posts/treasuremaps/{_id}/")
        #write _post file
        with open(f"../_posts/treasuremaps/{_id}/{_date}--{patch2}--0--{active_treasuremap["Name_en"]}.md", "w", encoding="utf8") as f:
            f.write(_post)


def get_coords_later(coords_later):
    map_ = ""
    for key, value in treasurespot.items():
        lev = str(value['Location'].get('row_id'))
        if not lev or lev == "0" or lev == "None":
            continue

        treasure_hunt_rank_id, _ = key.split(".")
        coords = getCoordsFromLocationLevel(value['Location'], True)
        map_ = str(level[lev]['Map']['Id'])


        if not coords_later.get(treasure_hunt_rank_id, None):
            coords_later[treasure_hunt_rank_id] = {}
        if not coords_later[treasure_hunt_rank_id].get(map_, None):
            coords_later[treasure_hunt_rank_id][map_] = []
        coords_later[treasure_hunt_rank_id][map_].append(((coords['x']), (coords['y']), coords['placename']))
        #print(((coords['x']), (coords['y']), coords['placename']))
    return coords_later


def run():
    print("[TS] Start TreasureSpotGenerator")
    print(os.getcwd())
    get_map_translation_data()
    coords_later: dict[str, dict[str, Any]] = {}
    coords_later = {'1': {'f1f1/00': [(364.9, 60.0, 'Tiefer Wald'), (-105.6, -162.0, 'Tiefer Wald'), (63.1, 272.0, 'Tiefer Wald')], 'f1f2/00': [(-408.1, 87.4, 'Ostwald'), (-315.1, 384.0, 'Ostwald'), (57.8, 182.6, 'Ostwald')], 'f1f3/00': [(-209.2, 8.1, 'Südwald'), (-308.6, 405.5, 'Südwald'), (307.0, -191.8, 'Südwald')], 'f1f4/00': [(246.6, -3.2, 'Nordwald'), (290.6, 166.3, 'Nordwald'), (-59.2, 335.3, 'Nordwald')], 's1f1/00': [(55.8, -293.5, 'Zentrales La Noscea'), (138.9, 303.3, 'Zentrales La Noscea'), (49.6, -119.1, 'Zentrales La Noscea')], 's1f2/00': [(62.6, 180.8, 'Unteres La Noscea'), (448.6, -6.5, 'Unteres La Noscea'), (-72.4, 542.0, 'Unteres La Noscea')], 's1f3/01': [(269.0, 524.0, 'Östliches La Noscea'), (52.8, 105.6, 'Östliches La Noscea'), (-199.4, 590.4, 'Östliches La Noscea')], 's1f4/00': [(638.5, 333.2, 'Westliches La Noscea'), (159.8, 106.2, 'Westliches La Noscea'), (451.3, 277.0, 'Westliches La Noscea')], 's1f5/00': [(688.5, 163.2, 'Oberes La Noscea'), (-350.4, 143.8, 'Oberes La Noscea'), (414.8, 184.3, 'Oberes La Noscea')], 's1f6/00': [(-361.9, -264.1, 'Äußeres La Noscea'), (-64.1, -280.8, 'Äußeres La Noscea'), (-53.0, -219.7, 'Äußeres La Noscea')], 'w1f1/00': [(91.5, 129.4, 'Westliches Thanalan'), (140.3, 270.1, 'Westliches Thanalan'), (-250.4, -338.9, 'Westliches Thanalan')], 'w1f2/00': [(141.4, 639.6, 'Zentrales Thanalan'), (191.6, -171.5, 'Zentrales Thanalan'), (-199.3, -124.1, 'Zentrales Thanalan')], 'w1f3/00': [(261.3, -119.3, 'Östliches Thanalan'), (127.0, -147.6, 'Östliches Thanalan'), (-331.1, -110.6, 'Östliches Thanalan')], 'w1f4/01': [(56.5, -418.0, 'Südliches Thanalan'), (-176.1, 416.2, 'Südliches Thanalan'), (-343.3, -276.1, 'Südliches Thanalan')], 'r1f1/00': [(327.2, 117.7, 'Zentrales Hochland von Coerthas'), (155.2, 289.0, 'Zentrales Hochland von Coerthas'), (111.4, -76.2, 'Zentrales Hochland von Coerthas')]}, '2': {'f1f1/00': [(163.5, 530.7, 'Tiefer Wald'), (202.2, -18.1, 'Tiefer Wald'), (-192.3, -38.7, 'Tiefer Wald')], 'f1f2/00': [(114.7, 468.1, 'Ostwald'), (3.3, 199.4, 'Ostwald'), (-204.4, 13.4, 'Ostwald')], 'f1f3/00': [(18.9, -96.1, 'Südwald'), (318.1, 41.9, 'Südwald'), (200.3, -164.3, 'Südwald')], 'f1f4/00': [(-162.5, 275.4, 'Nordwald'), (353.7, 234.2, 'Nordwald'), (415.0, 69.7, 'Nordwald')], 's1f1/00': [(190.8, 178.2, 'Zentrales La Noscea'), (143.8, -26.9, 'Zentrales La Noscea'), (-169.1, -400.0, 'Zentrales La Noscea')], 's1f2/00': [(397.5, -385.7, 'Unteres La Noscea'), (164.9, 289.8, 'Unteres La Noscea'), (379.8, -259.0, 'Unteres La Noscea')], 's1f3/01': [(405.6, 743.8, 'Östliches La Noscea'), (-155.2, 169.0, 'Östliches La Noscea'), (401.3, 147.3, 'Östliches La Noscea')], 's1f4/00': [(404.5, 21.2, 'Westliches La Noscea'), (90.2, 8.9, 'Westliches La Noscea'), (730.4, 440.6, 'Westliches La Noscea')], 's1f5/00': [(-370.5, 195.0, 'Oberes La Noscea'), (585.4, 121.3, 'Oberes La Noscea'), (293.9, 110.5, 'Oberes La Noscea')], 's1f6/00': [(-392.2, -328.2, 'Äußeres La Noscea'), (66.9, -315.2, 'Äußeres La Noscea'), (-289.2, -287.9, 'Äußeres La Noscea')], 'w1f1/00': [(276.8, -220.1, 'Westliches Thanalan'), (-460.4, -474.6, 'Westliches Thanalan'), (160.6, 113.5, 'Westliches Thanalan')], 'w1f2/00': [(-39.1, -414.4, 'Zentrales Thanalan'), (-271.6, -58.8, 'Zentrales Thanalan'), (21.9, 54.9, 'Zentrales Thanalan')], 'w1f3/00': [(161.7, 47.6, 'Östliches Thanalan'), (397.8, -197.3, 'Östliches Thanalan'), (-134.8, 112.8, 'Östliches Thanalan')], 'w1f4/01': [(39.1, -366.5, 'Südliches Thanalan'), (125.1, -675.0, 'Südliches Thanalan'), (-278.7, -67.3, 'Südliches Thanalan')], 'r1f1/00': [(68.1, 170.9, 'Zentrales Hochland von Coerthas'), (249.2, -386.3, 'Zentrales Hochland von Coerthas'), (524.7, 303.9, 'Zentrales Hochland von Coerthas')]}, '3': {'f1f1/00': [(443.3, -2.7, 'Tiefer Wald'), (154.1, -15.0, 'Tiefer Wald'), (-258.5, -186.3, 'Tiefer Wald')], 'f1f2/00': [(42.1, 434.9, 'Ostwald'), (-276.4, 108.0, 'Ostwald'), (207.9, 74.9, 'Ostwald')], 'f1f3/00': [(-219.4, 547.2, 'Südwald'), (-168.8, 125.7, 'Südwald'), (84.2, 13.6, 'Südwald')], 'f1f4/00': [(160.3, 211.3, 'Nordwald'), (-244.5, 203.1, 'Nordwald'), (355.1, 18.1, 'Nordwald')], 's1f1/00': [(-204.3, -444.0, 'Zentrales La Noscea'), (-72.4, -408.0, 'Zentrales La Noscea'), (134.4, 69.0, 'Zentrales La Noscea')], 's1f2/00': [(428.8, -148.1, 'Unteres La Noscea'), (101.8, 79.2, 'Unteres La Noscea'), (-91.6, 665.2, 'Unteres La Noscea')], 's1f3/01': [(-99.4, 684.2, 'Östliches La Noscea'), (234.3, 619.5, 'Östliches La Noscea'), (352.7, 710.2, 'Östliches La Noscea')], 's1f4/00': [(-243.2, 485.7, 'Westliches La Noscea'), (322.3, 159.0, 'Westliches La Noscea'), (12.4, 101.0, 'Westliches La Noscea')], 's1f5/00': [(-463.1, 220.0, 'Oberes La Noscea'), (346.4, -151.3, 'Oberes La Noscea'), (-586.1, -12.9, 'Oberes La Noscea')], 's1f6/00': [(-288.5, -531.4, 'Äußeres La Noscea'), (192.8, -279.5, 'Äußeres La Noscea'), (-362.2, -373.3, 'Äußeres La Noscea')], 'w1f1/00': [(-151.1, -248.9, 'Westliches Thanalan'), (202.6, -192.3, 'Westliches Thanalan'), (-362.1, -719.6, 'Westliches Thanalan')], 'w1f2/00': [(-170.1, -8.7, 'Zentrales Thanalan'), (40.5, 612.1, 'Zentrales Thanalan'), (-157.0, -195.8, 'Zentrales Thanalan')], 'w1f3/00': [(-235.1, 434.5, 'Östliches Thanalan'), (287.9, -184.9, 'Östliches Thanalan'), (-228.6, 122.4, 'Östliches Thanalan')], 'w1f4/01': [(142.3, 474.2, 'Südliches Thanalan'), (-229.0, -522.2, 'Südliches Thanalan'), (-388.9, 893.7, 'Südliches Thanalan')], 'r1f1/00': [(460.0, -284.9, 'Zentrales Hochland von Coerthas'), (-301.6, 681.6, 'Zentrales Hochland von Coerthas'), (-89.7, -302.1, 'Zentrales Hochland von Coerthas')], 'l1f1/01': [(271.9, -602.8, 'Mor Dhona'), (128.7, -447.3, 'Mor Dhona'), (-203.4, -667.9, 'Mor Dhona')]}, '4': {'f1f1/00': [(-380.9, 5.6, 'Tiefer Wald'), (352.0, -38.3, 'Tiefer Wald'), (43.7, 191.9, 'Tiefer Wald')], 'f1f2/00': [(285.3, 23.5, 'Ostwald'), (-191.4, -105.4, 'Ostwald'), (-428.3, 301.5, 'Ostwald')], 'f1f3/00': [(254.7, 47.9, 'Südwald'), (-104.3, -111.6, 'Südwald'), (-66.8, 368.9, 'Südwald')], 'f1f4/00': [(-189.4, 235.3, 'Nordwald'), (56.4, 331.2, 'Nordwald'), (62.6, 256.7, 'Nordwald')], 's1f1/00': [(80.4, 239.1, 'Zentrales La Noscea'), (-191.3, -77.3, 'Zentrales La Noscea'), (67.4, -218.8, 'Zentrales La Noscea')], 's1f2/00': [(23.1, 727.0, 'Unteres La Noscea'), (275.4, 12.7, 'Unteres La Noscea'), (349.2, -65.6, 'Unteres La Noscea')], 's1f3/01': [(-245.1, 160.6, 'Östliches La Noscea'), (256.2, 681.7, 'Östliches La Noscea'), (310.2, 181.9, 'Östliches La Noscea')], 's1f4/00': [(-125.1, 51.1, 'Westliches La Noscea'), (460.0, 425.6, 'Westliches La Noscea'), (-236.3, 679.9, 'Westliches La Noscea')], 's1f5/00': [(323.1, 7.3, 'Oberes La Noscea'), (-488.5, 17.7, 'Oberes La Noscea'), (731.6, 170.4, 'Oberes La Noscea')], 's1f6/00': [(51.5, -216.1, 'Äußeres La Noscea'), (-310.1, -444.1, 'Äußeres La Noscea'), (60.2, -497.7, 'Äußeres La Noscea')], 'w1f1/00': [(27.6, 212.5, 'Westliches Thanalan'), (72.5, -25.2, 'Westliches Thanalan'), (-289.2, -180.3, 'Westliches Thanalan')], 'w1f2/00': [(300.0, -36.3, 'Zentrales Thanalan'), (-237.2, -258.5, 'Zentrales Thanalan'), (262.0, 471.3, 'Zentrales Thanalan')], 'w1f3/00': [(-42.6, 368.5, 'Östliches Thanalan'), (-340.5, -248.7, 'Östliches Thanalan'), (-544.5, 79.5, 'Östliches Thanalan')], 'w1f4/01': [(-429.2, 711.6, 'Südliches Thanalan'), (-10.5, 375.4, 'Südliches Thanalan'), (-196.0, 929.0, 'Südliches Thanalan')], 'w1f5/00': [(155.5, 106.7, 'Nördliches Thanalan'), (-93.2, -18.5, 'Nördliches Thanalan'), (-87.5, -139.7, 'Nördliches Thanalan')], 'r1f1/00': [(-775.7, -142.0, 'Zentrales Hochland von Coerthas'), (104.8, -647.2, 'Zentrales Hochland von Coerthas'), (-685.9, -436.5, 'Zentrales Hochland von Coerthas')], 'l1f1/01': [(-201.7, -528.4, 'Mor Dhona'), (214.7, -466.6, 'Mor Dhona'), (-307.2, -516.3, 'Mor Dhona')]}, '5': {'f1f1/00': [(-13.5, 377.1, 'Tiefer Wald'), (-289.1, -101.9, 'Tiefer Wald'), (-454.4, -204.6, 'Tiefer Wald')], 'f1f2/00': [(-178.2, 164.3, 'Ostwald'), (361.4, -152.3, 'Ostwald'), (350.3, -32.8, 'Ostwald')], 'f1f3/00': [(451.3, 171.1, 'Südwald'), (376.1, 142.1, 'Südwald'), (67.7, 152.8, 'Südwald')], 'f1f4/00': [(48.2, 120.7, 'Nordwald'), (21.4, -23.1, 'Nordwald'), (-14.2, 518.6, 'Nordwald')], 's1f1/00': [(-374.9, -489.2, 'Zentrales La Noscea'), (3.8, -332.0, 'Zentrales La Noscea'), (-347.8, -372.4, 'Zentrales La Noscea')], 's1f2/00': [(622.9, -278.0, 'Unteres La Noscea'), (154.3, 160.3, 'Unteres La Noscea'), (-8.3, 459.5, 'Unteres La Noscea')], 's1f3/01': [(116.5, 15.5, 'Östliches La Noscea'), (-161.1, 688.6, 'Östliches La Noscea'), (428.7, -43.0, 'Östliches La Noscea')], 's1f4/00': [(-189.4, -295.1, 'Westliches La Noscea'), (-140.4, -116.8, 'Westliches La Noscea'), (-343.5, -220.8, 'Westliches La Noscea')], 's1f5/00': [(-603.5, 14.9, 'Oberes La Noscea'), (-394.4, 22.4, 'Oberes La Noscea'), (291.3, -190.3, 'Oberes La Noscea')], 's1f6/00': [(55.3, -351.2, 'Äußeres La Noscea'), (64.9, -460.9, 'Äußeres La Noscea'), (-138.6, -305.5, 'Äußeres La Noscea')], 'w1f1/00': [(-276.5, -739.0, 'Westliches Thanalan'), (-533.9, -778.5, 'Westliches Thanalan'), (-72.1, 328.3, 'Westliches Thanalan')], 'w1f2/00': [(-210.9, -444.0, 'Zentrales Thanalan'), (-257.4, 85.6, 'Zentrales Thanalan'), (66.2, -99.4, 'Zentrales Thanalan')], 'w1f3/00': [(-114.4, -32.1, 'Östliches Thanalan'), (191.1, 203.9, 'Östliches Thanalan'), (452.7, 249.5, 'Östliches Thanalan')], 'w1f4/01': [(-272.7, 138.9, 'Südliches Thanalan'), (235.6, 820.5, 'Südliches Thanalan'), (162.2, -26.0, 'Südliches Thanalan')], 'w1f5/00': [(-71.7, -243.3, 'Nördliches Thanalan'), (-234.1, -138.8, 'Nördliches Thanalan'), (97.3, 225.5, 'Nördliches Thanalan')], 'r1f1/00': [(-741.7, 435.9, 'Zentrales Hochland von Coerthas'), (-622.9, -52.5, 'Zentrales Hochland von Coerthas'), (476.1, -254.9, 'Zentrales Hochland von Coerthas')], 'l1f1/01': [(-160.4, -193.1, 'Mor Dhona'), (-501.3, -254.8, 'Mor Dhona'), (-541.4, -356.3, 'Mor Dhona')]}, '6': {'f1f1/00': [(-538.0, 103.6, 'Tiefer Wald'), (-11.2, 431.5, 'Tiefer Wald')], 'f1f2/00': [(-296.1, -22.3, 'Ostwald'), (195.8, -532.0, 'Ostwald')], 'f1f3/00': [(140.6, 171.7, 'Südwald'), (120.8, -128.9, 'Südwald')], 'f1f4/00': [(-264.9, 288.7, 'Nordwald'), (123.9, 234.4, 'Nordwald')], 's1f1/00': [(-177.1, -176.5, 'Zentrales La Noscea'), (13.7, 179.0, 'Zentrales La Noscea')], 's1f2/00': [(650.0, -356.7, 'Unteres La Noscea'), (105.7, 880.9, 'Unteres La Noscea')], 's1f3/01': [(450.3, 310.1, 'Östliches La Noscea'), (-222.3, 490.2, 'Östliches La Noscea')], 's1f4/00': [(-459.3, 718.9, 'Westliches La Noscea'), (565.2, 301.5, 'Westliches La Noscea')], 's1f5/00': [(-365.7, -13.9, 'Oberes La Noscea'), (454.9, 170.4, 'Oberes La Noscea')], 's1f6/00': [(68.0, -257.7, 'Äußeres La Noscea'), (-308.1, -319.3, 'Äußeres La Noscea')], 'w1f1/00': [(7.7, 90.1, 'Westliches Thanalan'), (-96.8, 241.5, 'Westliches Thanalan')], 'w1f2/00': [(-114.9, -397.8, 'Zentrales Thanalan'), (411.3, -106.4, 'Zentrales Thanalan')], 'w1f3/00': [(91.7, 295.5, 'Östliches Thanalan'), (-546.0, -163.7, 'Östliches Thanalan')], 'w1f4/01': [(49.0, 871.3, 'Südliches Thanalan'), (-8.3, -665.8, 'Südliches Thanalan')], 'w1f5/00': [(-41.2, 314.2, 'Nördliches Thanalan'), (-49.7, 32.4, 'Nördliches Thanalan')], 'r1f1/00': [(85.4, -274.3, 'Zentrales Hochland von Coerthas'), (-533.0, 290.7, 'Zentrales Hochland von Coerthas')], 'l1f1/01': [(508.5, -384.0, 'Mor Dhona'), (-416.4, -548.7, 'Mor Dhona')]}, '7': {'f1f1/00': [(154.4, 343.6, 'Tiefer Wald'), (-285.1, 102.3, 'Tiefer Wald')], 'f1f2/00': [(-343.6, 248.6, 'Ostwald'), (-10.9, 8.3, 'Ostwald')], 'f1f3/00': [(-283.3, -99.7, 'Südwald'), (-171.2, 249.5, 'Südwald')], 'f1f4/00': [(223.3, 275.9, 'Nordwald'), (-101.7, 362.6, 'Nordwald')], 's1f1/00': [(-99.8, -140.8, 'Zentrales La Noscea'), (-318.8, -552.6, 'Zentrales La Noscea')], 's1f2/00': [(218.0, 29.5, 'Unteres La Noscea'), (507.9, -237.2, 'Unteres La Noscea')], 's1f3/01': [(342.8, 466.8, 'Östliches La Noscea'), (-329.0, 437.1, 'Östliches La Noscea')], 's1f4/00': [(-300.6, 612.1, 'Westliches La Noscea'), (52.4, -36.7, 'Westliches La Noscea')], 's1f5/00': [(335.3, -62.7, 'Oberes La Noscea'), (258.7, 74.6, 'Oberes La Noscea')], 's1f6/00': [(-324.2, -136.0, 'Äußeres La Noscea'), (-396.1, -268.6, 'Äußeres La Noscea')], 'w1f1/00': [(114.3, -137.6, 'Westliches Thanalan'), (-130.1, 385.6, 'Westliches Thanalan')], 'w1f2/00': [(-3.4, -312.5, 'Zentrales Thanalan'), (-71.0, 30.8, 'Zentrales Thanalan')], 'w1f3/00': [(-284.1, 255.1, 'Östliches Thanalan'), (-237.4, -3.8, 'Östliches Thanalan')], 'w1f4/01': [(-60.1, -284.8, 'Südliches Thanalan'), (16.9, 486.1, 'Südliches Thanalan')], 'w1f5/00': [(17.8, 296.8, 'Nördliches Thanalan'), (12.1, 168.9, 'Nördliches Thanalan')], 'r1f1/00': [(365.5, -398.3, 'Zentrales Hochland von Coerthas'), (-288.4, -133.6, 'Zentrales Hochland von Coerthas')], 'l1f1/01': [(112.0, -558.7, 'Mor Dhona'), (487.2, -494.6, 'Mor Dhona')]}, '8': {'f1f1/00': [(-25.4, 327.3, 'Tiefer Wald'), (215.9, -60.5, 'Tiefer Wald')], 'f1f2/00': [(-62.8, 278.1, 'Ostwald'), (40.8, 448.9, 'Ostwald')], 'f1f3/00': [(-237.2, 61.9, 'Südwald'), (-194.2, 422.8, 'Südwald')], 'f1f4/00': [(-15.7, 427.4, 'Nordwald'), (430.6, 261.9, 'Nordwald')], 's1f1/00': [(-116.3, -288.0, 'Zentrales La Noscea'), (-15.5, -94.7, 'Zentrales La Noscea')], 's1f2/00': [(202.3, 137.4, 'Unteres La Noscea'), (627.1, -199.0, 'Unteres La Noscea')], 's1f3/01': [(-264.8, 226.3, 'Östliches La Noscea'), (520.3, 549.3, 'Östliches La Noscea')], 's1f4/00': [(263.2, 142.6, 'Westliches La Noscea'), (611.5, 440.5, 'Westliches La Noscea')], 's1f5/00': [(334.4, 204.0, 'Oberes La Noscea'), (366.2, 26.3, 'Oberes La Noscea')], 's1f6/00': [(-333.3, -156.6, 'Äußeres La Noscea'), (117.5, -259.2, 'Äußeres La Noscea')], 'w1f1/00': [(-51.3, 136.4, 'Westliches Thanalan'), (249.4, 41.7, 'Westliches Thanalan')], 'w1f2/00': [(209.5, -65.8, 'Zentrales Thanalan'), (100.7, 412.8, 'Zentrales Thanalan')], 'w1f3/00': [(-346.4, 411.0, 'Östliches Thanalan'), (-132.9, 157.9, 'Östliches Thanalan')], 'w1f4/01': [(-85.6, -630.4, 'Südliches Thanalan'), (-125.2, 533.0, 'Südliches Thanalan')]}, '9': {'r2f1/00': [(15.7, 110.2, 'Westliches Hochland von Coerthas'), (-96.3, -222.1, 'Westliches Hochland von Coerthas'), (-546.6, -561.9, 'Westliches Hochland von Coerthas'), (377.8, 59.0, 'Westliches Hochland von Coerthas'), (314.8, -551.2, 'Westliches Hochland von Coerthas'), (343.3, 492.9, 'Westliches Hochland von Coerthas'), (111.0, 499.3, 'Westliches Hochland von Coerthas')], 'd2f1/00': [(-60.5, -150.5, 'Dravanisches Vorland'), (-491.6, 234.3, 'Dravanisches Vorland'), (-264.2, 672.4, 'Dravanisches Vorland'), (612.8, -601.0, 'Dravanisches Vorland'), (366.0, 277.3, 'Dravanisches Vorland'), (638.2, -134.5, 'Dravanisches Vorland'), (740.2, -606.4, 'Dravanisches Vorland'), (57.6, 555.8, 'Dravanisches Vorland')], 'd2f3/00': [(-216.0, -60.6, 'Wallende Nebel'), (-199.8, 230.5, 'Wallende Nebel'), (373.0, -39.8, 'Wallende Nebel'), (37.4, 146.5, 'Wallende Nebel'), (387.2, 224.4, 'Wallende Nebel'), (271.5, -224.8, 'Wallende Nebel'), (237.5, -572.4, 'Wallende Nebel'), (560.2, -0.9, 'Wallende Nebel')]}, '10': {'r2f1/00': [(-310.1, 27.6, 'Westliches Hochland von Coerthas'), (-323.6, 435.6, 'Westliches Hochland von Coerthas'), (23.9, 226.3, 'Westliches Hochland von Coerthas'), (509.8, -793.9, 'Westliches Hochland von Coerthas'), (626.1, -573.6, 'Westliches Hochland von Coerthas'), (263.9, -533.4, 'Westliches Hochland von Coerthas'), (641.4, -303.0, 'Westliches Hochland von Coerthas'), (529.9, -150.8, 'Westliches Hochland von Coerthas')], 'd2f1/00': [(261.6, -518.7, 'Dravanisches Vorland'), (-627.4, 649.2, 'Dravanisches Vorland'), (-40.2, 639.7, 'Dravanisches Vorland'), (-98.1, 124.9, 'Dravanisches Vorland'), (371.9, 534.8, 'Dravanisches Vorland'), (703.3, -245.6, 'Dravanisches Vorland'), (305.8, 194.6, 'Dravanisches Vorland'), (118.4, -460.5, 'Dravanisches Vorland'), (69.7, 77.1, 'Dravanisches Vorland')], 'd2f3/00': [(-517.7, -292.3, 'Wallende Nebel'), (-457.2, 356.6, 'Wallende Nebel'), (11.7, 86.1, 'Wallende Nebel'), (467.6, -289.3, 'Wallende Nebel'), (595.1, 311.5, 'Wallende Nebel'), (275.0, 70.3, 'Wallende Nebel'), (-264.7, 663.3, 'Wallende Nebel'), (-504.6, 628.8, 'Wallende Nebel'), (740.0, -233.8, 'Wallende Nebel')], 'a2f1/00': [(-427.8, -571.2, 'Abalathisches Wolkenmeer'), (-571.9, -219.9, 'Abalathisches Wolkenmeer'), (-414.3, -44.0, 'Abalathisches Wolkenmeer'), (249.9, 32.5, 'Abalathisches Wolkenmeer'), (705.7, -84.9, 'Abalathisches Wolkenmeer'), (215.5, 620.1, 'Abalathisches Wolkenmeer'), (599.3, 705.4, 'Abalathisches Wolkenmeer'), (-601.9, 195.7, 'Abalathisches Wolkenmeer'), (606.9, -574.6, 'Abalathisches Wolkenmeer'), (692.6, -332.9, 'Abalathisches Wolkenmeer')], 'd2f2/00': [(-355.7, -56.2, 'Dravanisches Hinterland'), (-490.4, 153.1, 'Dravanisches Hinterland'), (-167.1, 592.4, 'Dravanisches Hinterland'), (151.4, -64.7, 'Dravanisches Hinterland'), (253.2, 274.1, 'Dravanisches Hinterland'), (756.3, 73.4, 'Dravanisches Hinterland'), (-362.5, 539.5, 'Dravanisches Hinterland'), (607.0, 353.3, 'Dravanisches Hinterland')]}, '11': {'r2f1/00': [(-749.4, -493.3, 'Westliches Hochland von Coerthas'), (-109.9, 397.7, 'Westliches Hochland von Coerthas'), (-41.7, -490.1, 'Westliches Hochland von Coerthas'), (585.2, -704.5, 'Westliches Hochland von Coerthas'), (683.9, 198.2, 'Westliches Hochland von Coerthas'), (314.8, -332.0, 'Westliches Hochland von Coerthas'), (-496.6, 90.4, 'Westliches Hochland von Coerthas')], 'd2f1/00': [(40.5, 156.3, 'Dravanisches Vorland'), (-564.0, 360.2, 'Dravanisches Vorland'), (-430.5, 576.0, 'Dravanisches Vorland'), (233.4, 392.1, 'Dravanisches Vorland'), (309.4, 72.6, 'Dravanisches Vorland'), (50.1, 440.3, 'Dravanisches Vorland'), (-497.0, 591.9, 'Dravanisches Vorland'), (-360.4, 565.1, 'Dravanisches Vorland'), (-178.0, 548.9, 'Dravanisches Vorland')], 'd2f3/00': [(-465.0, -439.0, 'Wallende Nebel'), (-575.4, -112.4, 'Wallende Nebel'), (55.9, -156.4, 'Wallende Nebel'), (454.9, 146.1, 'Wallende Nebel'), (-245.9, 529.9, 'Wallende Nebel'), (260.7, 710.9, 'Wallende Nebel'), (-695.4, -233.4, 'Wallende Nebel'), (-579.4, -614.1, 'Wallende Nebel'), (-44.6, 726.7, 'Wallende Nebel')], 'a2f1/00': [(13.1, -559.6, 'Abalathisches Wolkenmeer'), (-386.9, 207.0, 'Abalathisches Wolkenmeer'), (-174.4, 588.4, 'Abalathisches Wolkenmeer'), (-55.8, 455.5, 'Abalathisches Wolkenmeer'), (314.5, 73.7, 'Abalathisches Wolkenmeer'), (433.1, -173.1, 'Abalathisches Wolkenmeer'), (-753.6, -725.7, 'Abalathisches Wolkenmeer'), (-90.4, -818.2, 'Abalathisches Wolkenmeer'), (-574.9, 786.1, 'Abalathisches Wolkenmeer'), (-252.4, -277.6, 'Abalathisches Wolkenmeer')]}, '12': {'g3f1/00': [(-247.7, -595.6, 'Abanisches Grenzland'), (352.9, -565.6, 'Abanisches Grenzland'), (214.2, -248.2, 'Abanisches Grenzland'), (540.3, 272.8, 'Abanisches Grenzland'), (116.2, 602.0, 'Abanisches Grenzland'), (-234.5, 355.7, 'Abanisches Grenzland'), (-335.8, -0.9, 'Abanisches Grenzland'), (-258.8, -221.8, 'Abanisches Grenzland')], 'g3f2/00': [(-666.7, -480.0, 'Die Zinnen'), (-476.1, -575.0, 'Die Zinnen'), (-12.9, -422.0, 'Die Zinnen'), (333.2, -306.4, 'Die Zinnen'), (284.9, 550.3, 'Die Zinnen'), (-171.5, 339.4, 'Die Zinnen'), (-447.8, 239.8, 'Die Zinnen'), (-420.9, 632.6, 'Die Zinnen')], 'g3f3/00': [(-856.9, -257.6, 'Das Fenn'), (-772.1, -571.7, 'Das Fenn'), (-340.8, -73.2, 'Das Fenn'), (-161.2, -356.3, 'Das Fenn'), (272.1, -455.9, 'Das Fenn'), (333.6, 264.3, 'Das Fenn'), (279.4, 594.0, 'Das Fenn'), (-561.1, 118.3, 'Das Fenn')], 'e3f1/00': [(-517.1, -724.0, 'Rubinsee'), (-28.2, -758.5, 'Rubinsee'), (847.4, -134.0, 'Rubinsee'), (500.2, 59.8, 'Rubinsee'), (747.0, 486.3, 'Rubinsee'), (436.2, 848.9, 'Rubinsee'), (77.5, 576.6, 'Rubinsee'), (-615.0, 186.4, 'Rubinsee')], 'e3f2/00': [(-214.9, -307.0, 'Yanxia'), (187.5, -593.5, 'Yanxia'), (-1.6, -638.6, 'Yanxia'), (570.6, -675.9, 'Yanxia'), (124.6, 14.2, 'Yanxia'), (447.1, 88.9, 'Yanxia'), (139.0, 698.7, 'Yanxia'), (-273.5, 301.6, 'Yanxia')], 'e3f3/00': [(-540.5, -85.1, 'Azim-Steppe'), (-233.8, -581.0, 'Azim-Steppe'), (288.9, -116.0, 'Azim-Steppe'), (654.0, 358.5, 'Azim-Steppe'), (227.2, 719.9, 'Azim-Steppe'), (-8.8, 555.0, 'Azim-Steppe'), (-514.2, 712.2, 'Azim-Steppe'), (-589.2, 307.9, 'Azim-Steppe')]}, '13': {'g3f1/00': [(-605.7, -448.4, 'Abanisches Grenzland'), (97.1, -465.2, 'Abanisches Grenzland'), (219.0, -66.1, 'Abanisches Grenzland'), (505.5, -33.9, 'Abanisches Grenzland'), (573.7, 499.7, 'Abanisches Grenzland'), (-515.4, 484.2, 'Abanisches Grenzland'), (-658.4, 335.9, 'Abanisches Grenzland'), (-295.3, -237.4, 'Abanisches Grenzland')], 'g3f2/00': [(-458.1, -779.2, 'Die Zinnen'), (-262.3, -602.3, 'Die Zinnen'), (229.2, -385.0, 'Die Zinnen'), (585.6, -581.2, 'Die Zinnen'), (127.4, 508.2, 'Die Zinnen'), (-301.1, 73.8, 'Die Zinnen'), (-285.0, 581.4, 'Die Zinnen'), (-643.8, 554.4, 'Die Zinnen')], 'g3f3/00': [(-776.9, -734.9, 'Das Fenn'), (185.4, -679.9, 'Das Fenn'), (522.9, -749.3, 'Das Fenn'), (415.7, -197.1, 'Das Fenn'), (154.3, 529.7, 'Das Fenn'), (-91.0, 95.0, 'Das Fenn'), (-276.9, 361.2, 'Das Fenn'), (-643.8, -187.2, 'Das Fenn')], 'e3f1/00': [(-809.9, -319.2, 'Rubinsee'), (-224.2, -591.7, 'Rubinsee'), (544.2, -628.1, 'Rubinsee'), (570.8, -151.5, 'Rubinsee'), (456.2, 198.9, 'Rubinsee'), (315.3, 426.9, 'Rubinsee'), (-147.4, 751.7, 'Rubinsee'), (-688.2, 413.5, 'Rubinsee')], 'e3f2/00': [(-467.7, -134.6, 'Yanxia'), (-72.8, -793.1, 'Yanxia'), (12.3, -378.5, 'Yanxia'), (525.4, -799.7, 'Yanxia'), (479.3, 355.6, 'Yanxia'), (519.8, 701.7, 'Yanxia'), (37.6, 317.0, 'Yanxia'), (-412.4, 435.3, 'Yanxia')], 'e3f3/00': [(-543.2, -274.4, 'Azim-Steppe'), (402.8, -480.0, 'Azim-Steppe'), (475.8, 30.6, 'Azim-Steppe'), (388.7, 696.0, 'Azim-Steppe'), (18.8, 779.7, 'Azim-Steppe'), (-323.6, 575.4, 'Azim-Steppe'), (-245.3, 178.3, 'Azim-Steppe'), (-828.2, 208.2, 'Azim-Steppe')]}, '14': {'g3f3/00': [(34.5, -12.9, 'Das Fenn'), (-217.9, -114.2, 'Das Fenn'), (-0.9, -282.8, 'Das Fenn'), (103.4, 207.7, 'Das Fenn')], 'e3f1/00': [(651.4, 441.1, 'Rubinsee'), (-209.2, 210.6, 'Rubinsee'), (-126.2, -155.1, 'Rubinsee'), (356.7, -337.2, 'Rubinsee'), (188.9, 69.0, 'Rubinsee')], 'e3f2/00': [(-662.0, -240.7, 'Yanxia'), (44.3, 677.1, 'Yanxia'), (-614.0, 577.4, 'Yanxia'), (-475.7, -614.0, 'Yanxia')], 'e3f3/00': [(-2.3, 195.1, 'Azim-Steppe'), (-129.9, 107.5, 'Azim-Steppe')]}, '16': {'g3f1/00': [(-605.7, -448.4, 'Abanisches Grenzland'), (97.1, -465.2, 'Abanisches Grenzland'), (219.0, -66.1, 'Abanisches Grenzland'), (505.5, -33.9, 'Abanisches Grenzland'), (573.7, 499.7, 'Abanisches Grenzland'), (-515.4, 484.2, 'Abanisches Grenzland'), (-658.4, 335.9, 'Abanisches Grenzland'), (-295.3, -237.4, 'Abanisches Grenzland')], 'g3f2/00': [(-458.1, -779.2, 'Die Zinnen'), (-262.3, -602.3, 'Die Zinnen'), (229.2, -385.0, 'Die Zinnen'), (585.6, -581.2, 'Die Zinnen'), (127.4, 508.2, 'Die Zinnen'), (-301.1, 73.8, 'Die Zinnen'), (-285.0, 581.4, 'Die Zinnen'), (-643.8, 554.4, 'Die Zinnen')], 'g3f3/00': [(-776.9, -734.9, 'Das Fenn'), (185.4, -679.9, 'Das Fenn'), (522.9, -749.3, 'Das Fenn'), (415.7, -197.1, 'Das Fenn'), (154.3, 529.7, 'Das Fenn'), (-91.0, 95.0, 'Das Fenn'), (-276.9, 361.2, 'Das Fenn'), (-643.8, -187.2, 'Das Fenn')], 'e3f1/00': [(-809.9, -319.2, 'Rubinsee'), (-224.2, -591.7, 'Rubinsee'), (544.2, -628.1, 'Rubinsee'), (570.8, -151.5, 'Rubinsee'), (456.2, 198.9, 'Rubinsee'), (315.3, 426.9, 'Rubinsee'), (-147.4, 751.7, 'Rubinsee'), (-688.2, 413.5, 'Rubinsee')], 'e3f2/00': [(-467.7, -134.6, 'Yanxia'), (-72.8, -793.1, 'Yanxia'), (12.3, -378.5, 'Yanxia'), (525.4, -799.7, 'Yanxia'), (479.3, 355.6, 'Yanxia'), (519.8, 701.7, 'Yanxia'), (37.6, 317.0, 'Yanxia'), (-412.4, 435.3, 'Yanxia')], 'e3f3/00': [(-543.2, -274.4, 'Azim-Steppe'), (402.8, -480.0, 'Azim-Steppe'), (475.8, 30.6, 'Azim-Steppe'), (388.7, 696.0, 'Azim-Steppe'), (18.8, 779.7, 'Azim-Steppe'), (-323.6, 575.4, 'Azim-Steppe'), (-245.3, 178.3, 'Azim-Steppe'), (-828.2, 208.2, 'Azim-Steppe')]}, '17': {'n4f1/00': [(295.9, 290.0, 'Seenland'), (-34.2, -596.8, 'Seenland'), (-320.0, -15.0, 'Seenland'), (28.8, -47.9, 'Seenland'), (450.0, -260.0, 'Seenland'), (604.6, -310.0, 'Seenland'), (110.0, -140.0, 'Seenland'), (250.0, 550.0, 'Seenland')], 'n4f2/00': [(800.0, 300.0, 'Kholusia'), (301.9, 559.8, 'Kholusia'), (87.3, 141.5, 'Kholusia'), (-311.8, 546.2, 'Kholusia'), (-650.0, 43.4, 'Kholusia'), (680.0, -100.0, 'Kholusia'), (331.1, -433.5, 'Kholusia'), (-100.0, 10.0, 'Kholusia')], 'n4f3/00': [(695.5, -371.9, 'Amh Araeng'), (-75.0, -630.0, 'Amh Araeng'), (-400.0, -90.0, 'Amh Araeng'), (-90.0, -230.0, 'Amh Araeng'), (478.0, 147.6, 'Amh Araeng'), (-590.0, 60.0, 'Amh Araeng'), (-60.9, 137.3, 'Amh Araeng'), (-320.0, 320.0, 'Amh Araeng')], 'n4f4/00': [(190.0, 679.6, 'Il Mheg'), (10.0, 320.0, 'Il Mheg'), (446.1, 3.5, 'Il Mheg'), (-130.0, 670.0, 'Il Mheg'), (-430.0, 790.0, 'Il Mheg'), (-740.0, 370.0, 'Il Mheg'), (-860.0, 200.0, 'Il Mheg'), (-750.0, -40.0, 'Il Mheg')], 'n4f5/00': [(-762.2, 616.5, "Der Große Wald Rak'tika"), (432.7, -496.5, "Der Große Wald Rak'tika"), (-32.5, -352.7, "Der Große Wald Rak'tika"), (-500.0, 580.0, "Der Große Wald Rak'tika"), (-310.0, 500.0, "Der Große Wald Rak'tika"), (527.2, 136.9, "Der Große Wald Rak'tika"), (-272.0, 93.2, "Der Große Wald Rak'tika"), (-747.0, -8.6, "Der Große Wald Rak'tika")], 'n4f6/00': [(230.8, -802.1, 'Tempest'), (350.0, 430.0, 'Tempest'), (180.0, 70.0, 'Tempest'), (-130.0, 10.0, 'Tempest'), (740.0, 50.0, 'Tempest'), (490.0, -470.0, 'Tempest'), (708.7, -296.6, 'Tempest'), (130.0, -90.0, 'Tempest')]}, '18': {'n4f1/00': [(-550.0, 200.0, 'Seenland'), (-660.0, -20.0, 'Seenland'), (665.2, 217.6, 'Seenland'), (-180.0, -220.0, 'Seenland'), (-385.6, -433.1, 'Seenland'), (-537.4, -491.0, 'Seenland'), (837.9, -382.0, 'Seenland'), (-160.0, -690.0, 'Seenland')], 'n4f2/00': [(469.1, -210.0, 'Kholusia'), (588.1, 513.6, 'Kholusia'), (-680.0, -169.6, 'Kholusia'), (-400.0, -238.8, 'Kholusia'), (-69.8, -220.6, 'Kholusia'), (-46.5, -612.0, 'Kholusia'), (-480.0, -374.8, 'Kholusia'), (668.3, -537.9, 'Kholusia')], 'n4f3/00': [(549.9, -642.3, 'Amh Araeng'), (734.9, -498.3, 'Amh Araeng'), (310.9, -426.5, 'Amh Araeng'), (630.0, -200.0, 'Amh Araeng'), (-459.2, -357.0, 'Amh Araeng'), (-413.7, 427.5, 'Amh Araeng'), (270.0, 120.0, 'Amh Araeng'), (440.9, 462.0, 'Amh Araeng')], 'n4f4/00': [(-706.1, -200.0, 'Il Mheg'), (-550.0, -420.0, 'Il Mheg'), (-430.0, -45.0, 'Il Mheg'), (10.0, -689.1, 'Il Mheg'), (-362.6, 302.2, 'Il Mheg'), (480.0, -870.0, 'Il Mheg'), (590.0, -550.0, 'Il Mheg'), (183.9, -451.3, 'Il Mheg')], 'n4f5/00': [(235.4, 665.6, "Der Große Wald Rak'tika"), (60.0, 550.0, "Der Große Wald Rak'tika"), (-492.6, -94.5, "Der Große Wald Rak'tika"), (170.0, 310.0, "Der Große Wald Rak'tika"), (-399.0, 128.7, "Der Große Wald Rak'tika"), (690.0, 50.0, "Der Große Wald Rak'tika"), (647.4, -219.9, "Der Große Wald Rak'tika"), (150.0, -300.0, "Der Große Wald Rak'tika")], 'n4f6/00': [(-380.0, -324.7, 'Tempest'), (-264.0, -146.4, 'Tempest'), (-441.9, -491.4, 'Tempest'), (-120.0, -660.0, 'Tempest'), (200.0, -500.0, 'Tempest'), (793.0, -184.8, 'Tempest'), (556.6, -814.7, 'Tempest'), (433.9, -25.6, 'Tempest')]}, '20': {'n4f1/00': [(-550.0, 200.0, 'Seenland'), (-660.0, -20.0, 'Seenland'), (665.2, 217.6, 'Seenland'), (-180.0, -220.0, 'Seenland'), (-385.6, -433.1, 'Seenland'), (-537.4, -491.0, 'Seenland'), (837.9, -382.0, 'Seenland'), (-160.0, -690.0, 'Seenland')], 'n4f2/00': [(469.1, -210.0, 'Kholusia'), (588.1, 513.6, 'Kholusia'), (-680.0, -169.6, 'Kholusia'), (-400.0, -238.8, 'Kholusia'), (-69.8, -220.6, 'Kholusia'), (-46.5, -612.0, 'Kholusia'), (-480.0, -374.8, 'Kholusia'), (668.3, -537.9, 'Kholusia')], 'n4f3/00': [(549.9, -642.3, 'Amh Araeng'), (734.9, -498.3, 'Amh Araeng'), (310.9, -426.5, 'Amh Araeng'), (630.0, -200.0, 'Amh Araeng'), (-459.2, -357.0, 'Amh Araeng'), (-413.7, 427.5, 'Amh Araeng'), (270.0, 120.0, 'Amh Araeng'), (440.9, 462.0, 'Amh Araeng')], 'n4f4/00': [(-706.1, -200.0, 'Il Mheg'), (-550.0, -420.0, 'Il Mheg'), (-430.0, -45.0, 'Il Mheg'), (10.0, -689.1, 'Il Mheg'), (-362.6, 302.2, 'Il Mheg'), (480.0, -870.0, 'Il Mheg'), (590.0, -550.0, 'Il Mheg'), (183.9, -451.3, 'Il Mheg')], 'n4f5/00': [(235.4, 665.6, "Der Große Wald Rak'tika"), (60.0, 550.0, "Der Große Wald Rak'tika"), (-492.6, -94.5, "Der Große Wald Rak'tika"), (170.0, 310.0, "Der Große Wald Rak'tika"), (-399.0, 128.7, "Der Große Wald Rak'tika"), (690.0, 50.0, "Der Große Wald Rak'tika"), (647.4, -219.9, "Der Große Wald Rak'tika"), (150.0, -300.0, "Der Große Wald Rak'tika")], 'n4f6/00': [(-380.0, -324.7, 'Tempest'), (-264.0, -146.4, 'Tempest'), (-441.9, -491.4, 'Tempest'), (-120.0, -660.0, 'Tempest'), (200.0, -500.0, 'Tempest'), (793.0, -184.8, 'Tempest'), (556.6, -814.7, 'Tempest'), (433.9, -25.6, 'Tempest')]}, '21': {'k5f1/00': [(271.6, 74.6, 'Labyrinthos'), (-658.9, -151.3, 'Labyrinthos'), (154.5, 637.1, 'Labyrinthos'), (-479.9, 741.5, 'Labyrinthos'), (-343.3, -707.3, 'Labyrinthos'), (510.5, 77.6, 'Labyrinthos'), (-57.5, -499.5, 'Labyrinthos'), (434.1, -272.9, 'Labyrinthos')], 'm5f1/00': [(292.0, 116.1, 'Thavnair'), (-131.1, 554.4, 'Thavnair'), (423.0, 356.1, 'Thavnair'), (-571.6, -235.2, 'Thavnair'), (134.7, -664.9, 'Thavnair'), (-116.2, -431.4, 'Thavnair'), (146.5, -491.2, 'Thavnair'), (-40.9, 68.8, 'Thavnair')], 'm5f2/00': [(-695.7, -621.3, 'Garlemald'), (127.2, 326.4, 'Garlemald'), (-163.8, -83.0, 'Garlemald'), (553.7, -805.8, 'Garlemald'), (389.5, 374.0, 'Garlemald'), (234.4, -4.7, 'Garlemald'), (-180.0, 587.7, 'Garlemald'), (-413.9, 51.7, 'Garlemald')], 'u5f1/00': [(390.6, 799.7, 'Mare Lamentorum'), (167.8, 240.4, 'Mare Lamentorum'), (-44.3, -49.8, 'Mare Lamentorum'), (-98.3, 619.7, 'Mare Lamentorum'), (393.0, 508.4, 'Mare Lamentorum'), (-236.3, 55.7, 'Mare Lamentorum'), (689.1, 127.5, 'Mare Lamentorum'), (174.3, -127.3, 'Mare Lamentorum')], 'u5f2/00': [(32.4, -758.4, 'Ultima Thule'), (263.9, -378.5, 'Ultima Thule'), (-704.3, 143.8, 'Ultima Thule'), (-549.3, 606.7, 'Ultima Thule'), (-567.4, -72.7, 'Ultima Thule'), (24.5, 462.4, 'Ultima Thule'), (505.6, -392.3, 'Ultima Thule'), (-236.5, 791.2, 'Ultima Thule')]}, '22': {'k5f1/00': [(-144.0, -167.1, 'Labyrinthos'), (162.4, 410.0, 'Labyrinthos'), (-733.9, -26.9, 'Labyrinthos'), (20.5, 805.5, 'Labyrinthos'), (138.4, -528.6, 'Labyrinthos'), (-651.7, 449.0, 'Labyrinthos'), (518.3, -350.5, 'Labyrinthos'), (174.5, 16.7, 'Labyrinthos')], 'm5f1/00': [(268.2, 373.2, 'Thavnair'), (24.4, -21.6, 'Thavnair'), (-20.1, 290.7, 'Thavnair'), (540.5, -352.6, 'Thavnair'), (-96.9, -362.7, 'Thavnair'), (-332.8, 259.6, 'Thavnair'), (-337.3, -677.9, 'Thavnair'), (283.2, -626.8, 'Thavnair')], 'm5f2/00': [(195.6, -451.3, 'Garlemald'), (639.3, -574.9, 'Garlemald'), (-253.5, -464.5, 'Garlemald'), (649.2, -208.0, 'Garlemald'), (-265.4, -180.5, 'Garlemald'), (-482.1, 212.1, 'Garlemald'), (335.6, 250.5, 'Garlemald'), (393.7, 697.7, 'Garlemald')], 'u5f1/00': [(668.3, 423.0, 'Mare Lamentorum'), (210.7, 592.5, 'Mare Lamentorum'), (-217.1, -103.8, 'Mare Lamentorum'), (-134.1, 213.6, 'Mare Lamentorum'), (-463.6, 258.7, 'Mare Lamentorum'), (-278.8, 648.7, 'Mare Lamentorum'), (451.8, 174.7, 'Mare Lamentorum'), (66.2, 741.2, 'Mare Lamentorum')], 'u5f2/00': [(264.0, 701.9, 'Ultima Thule'), (-0.9, 744.2, 'Ultima Thule'), (-765.3, -119.9, 'Ultima Thule'), (408.6, -603.3, 'Ultima Thule'), (214.7, -211.3, 'Ultima Thule'), (-666.0, 462.7, 'Ultima Thule'), (-178.1, 277.1, 'Ultima Thule'), (-436.7, -403.4, 'Ultima Thule')]}, '24': {'n5f1/00': [(286.7, 142.8, 'Elpis'), (53.9, 158.0, 'Elpis'), (-230.3, 478.5, 'Elpis'), (378.3, -196.2, 'Elpis'), (422.3, -598.2, 'Elpis'), (-424.0, -635.2, 'Elpis'), (-480.3, 584.5, 'Elpis'), (784.1, -145.1, 'Elpis')]}, '25': {'k5f1/00': [(-144.0, -167.1, 'Labyrinthos'), (162.4, 410.0, 'Labyrinthos'), (-733.9, -26.9, 'Labyrinthos'), (20.5, 805.5, 'Labyrinthos'), (138.4, -528.6, 'Labyrinthos'), (-651.7, 449.0, 'Labyrinthos'), (518.3, -350.5, 'Labyrinthos'), (174.5, 16.7, 'Labyrinthos')], 'm5f1/00': [(268.2, 373.2, 'Thavnair'), (24.4, -21.6, 'Thavnair'), (-20.1, 290.7, 'Thavnair'), (540.5, -352.6, 'Thavnair'), (-96.9, -362.7, 'Thavnair'), (-332.8, 259.6, 'Thavnair'), (-337.3, -677.9, 'Thavnair'), (283.2, -626.8, 'Thavnair')], 'm5f2/00': [(195.6, -451.3, 'Garlemald'), (639.3, -574.9, 'Garlemald'), (-253.5, -464.5, 'Garlemald'), (649.2, -208.0, 'Garlemald'), (-265.4, -180.5, 'Garlemald'), (-482.1, 212.1, 'Garlemald'), (335.6, 250.5, 'Garlemald'), (393.7, 697.7, 'Garlemald')], 'u5f1/00': [(668.3, 423.0, 'Mare Lamentorum'), (210.7, 592.5, 'Mare Lamentorum'), (-217.1, -103.8, 'Mare Lamentorum'), (-134.1, 213.6, 'Mare Lamentorum'), (-463.6, 258.7, 'Mare Lamentorum'), (-278.8, 648.7, 'Mare Lamentorum'), (451.8, 174.7, 'Mare Lamentorum'), (66.2, 741.2, 'Mare Lamentorum')], 'u5f2/00': [(264.0, 701.9, 'Ultima Thule'), (-0.9, 744.2, 'Ultima Thule'), (-765.3, -119.9, 'Ultima Thule'), (408.6, -603.3, 'Ultima Thule'), (214.7, -211.3, 'Ultima Thule'), (-666.0, 462.7, 'Ultima Thule'), (-178.1, 277.1, 'Ultima Thule'), (-436.7, -403.4, 'Ultima Thule')]}, '26': {'n5f1/00': [(286.7, 142.8, 'Elpis'), (53.9, 158.0, 'Elpis'), (-230.3, 478.5, 'Elpis'), (378.3, -196.2, 'Elpis'), (422.3, -598.2, 'Elpis'), (-424.0, -635.2, 'Elpis'), (-480.3, 584.5, 'Elpis'), (784.1, -145.1, 'Elpis')]}, '27': {'x6f1/00': [(32.4, 279.1, 'Shaaloani'), (-736.1, -312.8, 'Shaaloani'), (-375.5, 186.5, 'Shaaloani'), (-183.6, 587.2, 'Shaaloani'), (-200.5, -591.9, 'Shaaloani'), (659.8, 239.4, 'Shaaloani'), (24.9, -329.5, 'Shaaloani'), (700.2, -521.9, 'Shaaloani')], 'x6f2/00': [(-148.1, 658.9, 'Ewiges Erbe'), (235.3, 703.8, 'Ewiges Erbe'), (197.8, 183.8, 'Ewiges Erbe'), (-537.9, 96.8, 'Ewiges Erbe'), (-132.6, -790.1, 'Ewiges Erbe'), (-280.6, -276.6, 'Ewiges Erbe'), (222.1, -426.0, 'Ewiges Erbe'), (643.1, -580.1, 'Ewiges Erbe')], 'y6f1/00': [(-558.4, -489.5, 'Urqopacha'), (-117.6, -144.2, 'Urqopacha'), (13.4, 117.2, 'Urqopacha'), (314.8, -560.6, 'Urqopacha'), (653.2, 225.1, 'Urqopacha'), (490.6, -22.3, 'Urqopacha'), (-375.2, 38.4, 'Urqopacha'), (-775.4, 123.7, 'Urqopacha')], 'y6f2/00': [(854.7, -13.1, "Kozama'uka"), (206.5, -713.3, "Kozama'uka"), (-186.4, -106.0, "Kozama'uka"), (-504.4, -683.4, "Kozama'uka"), (723.1, 362.4, "Kozama'uka"), (248.4, 741.3, "Kozama'uka"), (152.9, 238.9, "Kozama'uka"), (-716.0, 232.4, "Kozama'uka")], 'y6f3/00': [(127.6, -535.0, "Yak T'el"), (339.0, -318.2, "Yak T'el"), (-607.9, 279.5, "Yak T'el"), (-222.8, -65.4, "Yak T'el"), (-496.3, -648.4, "Yak T'el"), (351.2, 219.4, "Yak T'el"), (799.0, -133.6, "Yak T'el"), (-371.9, 816.7, "Yak T'el")]}, '28': {'x6f1/00': [(-163.2, -19.6, 'Shaaloani'), (-444.2, -352.7, 'Shaaloani'), (-88.2, 652.7, 'Shaaloani'), (523.5, 572.3, 'Shaaloani'), (393.2, -652.2, 'Shaaloani'), (-145.9, -490.9, 'Shaaloani'), (704.4, -224.9, 'Shaaloani'), (208.8, -85.2, 'Shaaloani')], 'x6f2/00': [(239.0, 467.9, 'Ewiges Erbe'), (-231.1, 717.2, 'Ewiges Erbe'), (-211.3, 38.0, 'Ewiges Erbe'), (-241.7, -419.4, 'Ewiges Erbe'), (719.2, 205.5, 'Ewiges Erbe'), (-623.5, -11.4, 'Ewiges Erbe'), (34.5, -117.0, 'Ewiges Erbe'), (484.9, -653.3, 'Ewiges Erbe')], 'y6f1/00': [(639.2, 379.9, 'Urqopacha'), (-391.8, -365.1, 'Urqopacha'), (6.1, 119.3, 'Urqopacha'), (14.6, 228.0, 'Urqopacha'), (-286.6, 457.8, 'Urqopacha'), (-228.9, 96.7, 'Urqopacha'), (373.8, 130.1, 'Urqopacha'), (638.4, 560.1, 'Urqopacha')], 'y6f2/00': [(771.1, -760.0, "Kozama'uka"), (497.2, -326.1, "Kozama'uka"), (-75.1, -724.8, "Kozama'uka"), (-727.5, -103.2, "Kozama'uka"), (-621.9, 620.4, "Kozama'uka"), (-129.1, 51.6, "Kozama'uka"), (823.9, 11.6, "Kozama'uka"), (540.5, 732.1, "Kozama'uka")], 'y6f3/00': [(64.0, 717.3, "Yak T'el"), (-301.7, 268.9, "Yak T'el"), (-790.4, -92.3, "Yak T'el"), (760.9, -448.5, "Yak T'el"), (485.3, 22.8, "Yak T'el"), (-511.4, 588.8, "Yak T'el"), (163.2, -24.7, "Yak T'el"), (56.4, -781.7, "Yak T'el")]}, '30': {'x6f3/00': [(851.1, 332.2, 'Lebende Erinnerung'), (678.9, 694.8, 'Lebende Erinnerung'), (-61.1, 80.9, 'Lebende Erinnerung'), (480.7, -166.5, 'Lebende Erinnerung'), (-147.3, -279.7, 'Lebende Erinnerung'), (-608.9, -535.6, 'Lebende Erinnerung'), (-549.8, 728.3, 'Lebende Erinnerung'), (179.2, -728.9, 'Lebende Erinnerung')]}}
    if coords_later == {}:
        coords_later = get_coords_later(coords_later)

    #print(coords_later)
    show_image(coords_later)
    write_map_translation_data()

if __name__ == "__main__":
    run()
