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
    image_path: str = posible_maps[0]
    original_image: ImageFile = Image.open(image_path)
    modified_image: Image.Image = original_image.copy()

    overlay_cropped, x_off, y_off = get_croped_image(overlay_id)
    overlay_x_cropped, xx_off, xy_off = get_x_image(overlay_id)
    overlay_cropped.paste(overlay_x_cropped, (x_off-xx_off, y_off-xy_off), overlay_x_cropped if overlay_x_cropped.mode == 'RGBA' else None)

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
        #if not tmap == "18":
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


def run():
    print("[TS] Start TreasureSpotGenerator")
    print(os.getcwd())
    get_map_translation_data()
    coords_later: dict[str, dict[str, Any]] = {}
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

    #coords_later[]['y6f3/00'] = [(127.6, -535.0), (339.0, -318.2), (-607.9, 279.5), (-222.8, -65.4), (-496.3, -648.4), (351.2, 219.4), (799.0, -133.6), (-371.9, 816.7), (64.0, 717.3), (-301.7, 268.9), (-790.4, -92.3), (760.9, -448.5), (485.3, 22.8), (-511.4, 588.8), (163.2, -24.7), (56.4, -781.7)]
    show_image(coords_later)
    write_map_translation_data()

if __name__ == "__main__":
    run()
