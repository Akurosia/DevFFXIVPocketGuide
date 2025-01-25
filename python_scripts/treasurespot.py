from PIL.ImageFile import ImageFile
from ffxiv_aku import *
from PIL import Image, ImageDraw, ImageFont

treasurespot = loadDataTheQuickestWay("TreasureSpot.json")
treasurehuntrank = loadDataTheQuickestWay("TreasureHuntRank.json")
treasurehunttexture = loadDataTheQuickestWay("TreasureHuntTexture.json")
level = loadDataTheQuickestWay("Level.json")
ttype = loadDataTheQuickestWay("territorytype_all.json", translate=True)
items  = loadDataTheQuickestWay("item_all.json", translate=True)

def add_watermark(image, watermark_text, font_path="arial.ttf", font_size=30):
    # Create a copy of the image to avoid modifying the original
    watermarked_image = image.copy()
    draw = ImageDraw.Draw(watermarked_image)

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
    file_name: str = treasurehunttexture[_id]['col_0'].lower()
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
    file_name: str = treasurehunttexture[_id]['col_0'].lower()
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


ids: dict[str, list[str]] = {
    "6688":  ["A Realm Reborn", "arr", "02-arr"],
    "6689":  ["A Realm Reborn", "arr", "02-arr"],
    "6690":  ["A Realm Reborn", "arr", "02-arr"],
    "6691":  ["A Realm Reborn", "arr", "02-arr"],
    "6692":  ["A Realm Reborn", "arr", "02-arr"],
    "7884":  ["A Realm Reborn", "arr", "02-arr"],
    "8156":  ["A Realm Reborn", "arr", "02-arr"],
    "9900":  ["A Realm Reborn", "arr", "02-arr"],
    "12241": ["Heavensward", "hw", "03-hw"],
    "12242": ["Heavensward", "hw", "03-hw"],
    "12243": ["Heavensward", "hw", "03-hw"],
    "17835": ["Stormblood", "sb", "04-sb"],
    "17836": ["Stormblood", "sb", "04-sb"],
    "19770": ["Stormblood", "sb", "04-sb"],
    "24794": ["Stormblood", "sb", "04-sb"],
    "26744": ["Shadowbringers", "shb", "05-shb"],
    "26745": ["Shadowbringers", "shb", "05-shb"],
    "33328": ["Shadowbringers", "shb", "05-shb"],
    "36611": ["Endwalker", "ew", "06-ew"],
    "36612": ["Endwalker", "ew", "06-ew"],
    "39591": ["Endwalker", "ew", "06-ew"],
    "39593": ["Endwalker", "ew", "06-ew"],
    "39918": ["Endwalker", "ew", "06-ew"],
    "43556": ["Dawntrail", "dt", "07-dt"],
    "43557": ["Dawntrail", "dt", "07-dt"],
}

def show_image(circle_coords: dict[str, dict[str, Any]]):

    for tmap, locations in circle_coords.items():
        #if not tmap == "18":
        #    continue
        output_path: str = ""
        placename: str = ""
        overlay_id = treasurehuntrank[tmap]['TreasureHuntTexture']
        item_name = treasurehuntrank[tmap]['ItemName']
        active_treasuremap_id = None
        active_treasuremap = None
        for key, value in items.items():
            if value['Name_de'] == item_name:
                print(tmap, key, value['Name_de'])
                active_treasuremap = value
                active_treasuremap_id = key
                break
        _post = '---\n'
        _post += 'wip: "True"\n'
        _post += 'title:\n'
        _post += f'  de: "{active_treasuremap["Name_de"]}"\n'
        _post += f'  en: "{active_treasuremap["Name_en"]}"\n'
        _post += f'  fr: "{active_treasuremap["Name_fr"]}"\n'
        _post += f'  ja: "{active_treasuremap["Name_ja"]}"\n'
        _post += f'  cn: "{active_treasuremap["Name_cn"]}"\n'
        _post += f'  ko: "{active_treasuremap["Name_ko"]}"\n'
        _post += 'layout: treasuremap\n'
        _post += 'page_type: guide\n'
        _post += 'categories: "treasuremap"\n'
        _post += 'instanceType: "treasuremap"\n'
        _post += 'date: "2013.01.01"\n'
        _post += 'patchNumber: "2.0"\n'
        _post += f'patchName: "{ids[active_treasuremap_id][0]}"\n'
        _post += f'expac: "{ids[active_treasuremap_id][1]}"\n'
        _post += 'image: "/assets/img/content/klassen/Chocobo.webp"\n'
        _post += 'terms:\n'
        _post += '    - term: "TreasureMaps"\n'
        _post += f'    - term: "{ids[active_treasuremap_id][0]}"\n'
        _post += f'sortid: {tmap}\n'
        _post += f'order: {tmap}\n'
        _post += f'slug: "{fix_slug(active_treasuremap["Name_de"])}"\n'
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

            image_path: str = posible_maps[0]
            original_image: ImageFile = Image.open(image_path)
            modified_image: Image.Image = original_image.copy()

            overlay_cropped, x_off, y_off = get_croped_image(overlay_id)
            overlay_x_cropped, xx_off, xy_off = get_x_image(overlay_id)
            overlay_cropped.paste(overlay_x_cropped, (x_off-xx_off, y_off-xy_off), overlay_x_cropped if overlay_x_cropped.mode == 'RGBA' else None)

            w, h = modified_image.size
            _extra: list[str] = []
            for i, coord in enumerate(location):
                x, y , placename= coord
                output_path: str = f"../assets/img/TreasureMaps/{item_name}/{placename}/"
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
            _post += f'  - zonename: "{placename}"\n'
            _post += f'    fullimage: "/assets/img/TreasureMaps/{item_name}/{placename}/{placename}.webp"\n'
            _post += f'    subimage:\n'
            for img in _extra:
                _post += f'      - "/assets/img/TreasureMaps/{item_name}/{placename}/{img}.webp"\n'
            # Generate output file name and save the image
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            if not os.path.exists(output_path + f"{placename}.webp"):
                modified_image = add_watermark(modified_image, "AkurosiaKamo")
                modified_image.save(output_path + f"{placename}.webp", format='WEBP', lossless=True)
                print(f"Saved modified image: {output_path}{placename}.webp")
        _post += '---'

        if not os.path.exists(f"../_posts/treasuremaps/{ids[active_treasuremap_id][2]}/"):
            os.makedirs(f"../_posts/treasuremaps/{ids[active_treasuremap_id][2]}/")
        #write _post file
        with open(f"../_posts/treasuremaps/{ids[active_treasuremap_id][2]}/2013-01-01--2.0--0--{active_treasuremap["Name_en"]}.md", "w", encoding="utf8") as f:
            f.write(_post)


def run():
    print("[TS] Start TreasureSpotGenerator")
    print(os.getcwd())
    coords_later: dict[str, dict[str, Any]] = {}
    map_ = ""
    for key, value in treasurespot.items():
        lev = value['Location'][6:]
        if not lev:
            continue
        k, sub_id = key.split(".")

        coords: dict[str, dict[str, Any]] = getLevel(lev, pixel=True)
        map_ = level[lev]['Map']

        if not coords_later.get(k, None):
            coords_later[k] = {}
        if not coords_later[k].get(map_, None):
            coords_later[k][map_] = []
        #print(coords)
        coords_later[k][map_].append(((coords['x']), (coords['y']), coords['placename']))

    #coords_later[]['y6f3/00'] = [(127.6, -535.0), (339.0, -318.2), (-607.9, 279.5), (-222.8, -65.4), (-496.3, -648.4), (351.2, 219.4), (799.0, -133.6), (-371.9, 816.7), (64.0, 717.3), (-301.7, 268.9), (-790.4, -92.3), (760.9, -448.5), (485.3, 22.8), (-511.4, 588.8), (163.2, -24.7), (56.4, -781.7)]
    show_image(coords_later)

if __name__ == "__main__":
    run()
