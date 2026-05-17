import re
import os
from ffxiv_aku import fix_slug, print_color_red, convert_single_image
import shutil
try:
    from python_scripts.helper import getImage
except ImportError:
    from ..helper import getImage

LANGUAGES = ["de", "en", "fr", "ja"]
LANGUAGES_MAPPING = {
    "de": "de-DE",
    "en": "en-US",
    "fr": "fr-FR",
    "ja": "ja-JP",
}


def getStatusKey(stat, status):
    for k, v in status.items():
        if v["Name_de"] == stat:
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
