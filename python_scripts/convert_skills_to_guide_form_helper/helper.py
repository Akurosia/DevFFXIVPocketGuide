import re
import os
from ffxiv_aku import fix_slug, print_color_red, print_color_yellow, print_color_blue
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


def getImage(image):
    if image is None:
        return None
    image = image.replace(".tex", "_hr1.png")
    image = image.replace("ui/icon/", "")
    image = copy_and_return_image_as_hr(image)
    return image

def copy_and_return_image_as_hr(img):
    if "_hr1" not in img:
        img = img.replace(".png", "_hr1.png")
    if os.path.exists("P:\\extras\\images\\ui\\icon\\" + img):
        #print(os.getcwd())
        if not os.path.exists("..\\assets\\img\\game_assets\\" + img):
            if not os.path.exists(os.path.dirname("..\\assets\\img\\game_assets\\" + img)):
                os.makedirs(os.path.dirname("..\\assets\\img\\game_assets\\" + img))
            shutil.copyfile("P:\\extras\\images\\ui\\icon\\" + img, "..\\assets\\img\\game_assets\\" + img)
    else:
        print_color_red(img)
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
    return text


def get_propper_zone_name(zone_name, files):
    n = fix_slug(zone_name)
    for file in files:
        if n in file:
            return file.split("\\")[0].replace("_new", "") + "/" + n.replace("_", "-") + ".html"
    return None
