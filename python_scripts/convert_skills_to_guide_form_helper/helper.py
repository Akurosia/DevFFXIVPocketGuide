import re
from ffxiv_aku import fix_slug

LANGUAGES = ["de", "en", "fr", "ja", "cn", "ko"]


def getStatusKey(stat, status):
    for k, v in status.items():
        if v["Name"] == stat:
            return k
    return "0"


def getImage(image: str) -> str:
    image = image.replace(".tex", "_hr1.png")
    image = image.replace("ui/icon/", "")
    return image


def deal_with_extras_in_text(text):
    #print(text)
    # filter if cases
    regex = "(<If(.*?)>)"
    x = re.findall(regex, text)
    for y in x:
        text = text.replace(y[0], "")

    # handle else cases
    regex = "(<Else/>\\d+)"
    x = re.findall(regex, text)
    x = list(set(x))
    for y in x:
        text = text.replace(y, "")

    # handle else cases
    regex = "(<Else/>)"
    x = re.findall(regex, text)
    x = list(set(x))
    for y in x:
        text = text.replace(y, "/")
    text = text.replace("\n", "</br>").replace("</br></br>", "</br>").replace("</br></br>", "</br>")
    return text


def get_propper_zone_name(zone_name, files):
    n = fix_slug(zone_name)
    for file in files:
        if n in file:
            return file.split("\\")[0].replace("_new", "") + "/" + n.replace("_", "-") + ".html"
    return None
