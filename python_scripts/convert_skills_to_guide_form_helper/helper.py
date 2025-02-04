import re
import os
from ffxiv_aku import fix_slug, print_color_red, convert_single_image
import shutil

LANGUAGES = ["de", "en", "fr", "ja", "cn", "ko"]
LANGUAGES_MAPPING = {
    "de": "de-DE",
    "en": "en-US",
    "fr": "fr-FR",
    "ja": "ja-JP",
    "cn": "cn-CN",
    "ko": "ko-KR"
}


def getImage(image: str, _type: str="icon") -> str:
    if image is None or image == "":
        return ""
    image = image.replace(".tex", "_hr1.png")
    if _type == "icon":
        image = image.replace(f"ui/{_type}/", "")
    image = copy_and_return_image_as_hr(img=image, _type=_type)
    if not image.startswith("/"):
        image = "/" + image
    return image


def copy_and_return_image_as_hr(img: str, _type: str="icon") -> str:
    if "_hr1" not in img and not _type == "map":
        img = img.replace(".png", "_hr1.png")
    img = img.replace(".webp", ".png" )

    basepath = None
    if os.name == 'nt':
        basepath = "P:/extras/images/ui/"
    elif sys.platform.startswith("linux"):
        basepath = "/var/www/ffxiv/extras/images/ui/"
    elif sys.platform == "darwin":
        basepath = "/Volumes/FFXIV/extras/images/ui/"

    if os.path.exists(f"{basepath}{_type}/" + img):
        new_path = "../assets/img/game_assets/"
        if os.getcwd().endswith("DevFFXIVPocketGuide"):
            new_path = "assets/img/game_assets/"
        if _type == "map":
            new_path += "map/"
        if not os.path.exists(new_path + img.replace(".png", ".webp")):
            if not os.path.exists(os.path.dirname(new_path + img)):
                os.makedirs(os.path.dirname(new_path + img))
            convert_single_image(f"{basepath}{_type}/" + img, replace_dir=(f"{basepath}{_type}/", new_path))
            #shutil.copyfile(f"{basepath}{_type}/" + img, new_path + img)
    else:
        print_color_red(f"{basepath}{_type}/" + img)
    img = img.replace(".png", ".webp")
    return img


def getStatusKey(stat, status):
    for k, v in status.items():
        if v["Name"] == stat:
            return k
    return "0"


def deal_with_extras_in_text(text):
    text = text.replace("\n", "</br>").replace("</br></br>", "</br>").replace("</br></br>", "</br>")
    #print(text)
    # filter if cases
    regex = "(<If(.*?)>)"
    x = re.findall(regex, text)
    for y in x:
        text = text.replace(y[0], "")

    # handle else cases
    regex = "(<Else/>\\d+)"
    x = re.findall(regex, text)
    #x = list(set(x))
    for y in x:
        text = text.replace(y, "")
    # handle else cases
    regex = "(<Else/>)"
    x = re.findall(regex, text)
    x = list(set(x))
    for y in x:
        text = text.replace(y, "/")
    if text.endswith(".//"):
        text = text[:-2]
    elif text.endswith("./"):
        text = text[:-1]
    text = text.replace('"', "&quot;")
    return text


def get_propper_zone_name(zone_name, files):
    n = fix_slug(zone_name)
    for file in files:
        if n in file:
            return file.split("\\")[0].replace("_new", "") + "/" + n.replace("_", "-") + ".html"
    return None
