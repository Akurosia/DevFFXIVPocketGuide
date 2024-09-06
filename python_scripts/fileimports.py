# -*- coding: utf-8 -*-
# coding: utf8
from typing import Any, Union
from ffxiv_aku import (
    loadDataTheQuickestWay,
    get_any_Versiondata,
    get_any_Logdata,
    storeFilesInTmp,
    readJsonFile,
)

storeFilesInTmp(False)

# from guide_helper/guide
logdata: dict[str, Any] = get_any_Logdata()
logdata_lower = dict((k.lower(), v) for k, v in logdata.items())

storeFilesInTmp(True)

FFXIV_DATA = dict[str, dict[str,str|dict[str,str]]]

ENTRY_DATA = dict[str, Union[
    str,  # For all string values
    int,  # For integer values like 'line_index'
    list[str],  # For lists of strings like 'bosse', 'tags', 'adds'
    dict[str, str]  # For nested dictionaries like 'quest', 'quest_location', 'quest_npc', 'titles'
]]

# from header
territorytype_trans: FFXIV_DATA = loadDataTheQuickestWay("territorytype_all.json", translate=True)
territorytype: FFXIV_DATA = loadDataTheQuickestWay("TerritoryType.json")
patchversions: FFXIV_DATA = get_any_Versiondata()
mounts: FFXIV_DATA = loadDataTheQuickestWay("mount_all.json", translate=True)
exversion: FFXIV_DATA = loadDataTheQuickestWay("exversion_all.json", translate=True)
minions: FFXIV_DATA = loadDataTheQuickestWay("companion_all.json", translate=True)
orchestrions: FFXIV_DATA = loadDataTheQuickestWay("orchestrion_all.json", translate=True)
orchestrionpath: FFXIV_DATA = loadDataTheQuickestWay("OrchestrionPath.json", translate=False)
ttcards: FFXIV_DATA = loadDataTheQuickestWay("tripletriadcard_all.json", translate=True)
contentfindercondition: FFXIV_DATA = loadDataTheQuickestWay("ContentFinderCondition.de.json")
contentfindercondition_trans: FFXIV_DATA = loadDataTheQuickestWay("ContentFinderCondition", translate=True)
contentfinderconditiontransient: FFXIV_DATA = loadDataTheQuickestWay("ContentFinderConditionTransient", translate=True)
instancecontent: FFXIV_DATA = loadDataTheQuickestWay("InstanceContent.json")
contentmembertype: FFXIV_DATA = loadDataTheQuickestWay("ContentMemberType.json")
classjob: FFXIV_DATA = loadDataTheQuickestWay("Classjob.de.json")
items: FFXIV_DATA = loadDataTheQuickestWay("Item.de.json")
gamerscape_items: FFXIV_DATA = readJsonFile("python_scripts/gamerscape_items/after_item_scan.json")


fates: FFXIV_DATA = loadDataTheQuickestWay("Fate.de.json")
fates_trans: FFXIV_DATA = loadDataTheQuickestWay("fate_all.json", translate=True)

# from guide_helper
action: FFXIV_DATA = loadDataTheQuickestWay("action_all.json", translate=True)
bnpcname: FFXIV_DATA = loadDataTheQuickestWay("bnpcname_all.json", translate=True)
eobjname: FFXIV_DATA = loadDataTheQuickestWay("eobjname_all.json", translate=True)
enpcresident: FFXIV_DATA = loadDataTheQuickestWay("enpcresident_all.json", translate=True)

# from helper
placename: FFXIV_DATA = loadDataTheQuickestWay("placename_all.json", translate=True)

# from guide/guide_helper
status: FFXIV_DATA = loadDataTheQuickestWay("status_all.json", translate=True)

# from xlsx entry helper
# quests = loadDataTheQuickestWay("Quest.de.json")
quests_all: FFXIV_DATA = loadDataTheQuickestWay("quest_all.json", translate=True)
questss: FFXIV_DATA = loadDataTheQuickestWay("Quest.de.json", exd="raw-exd-all")
enpcresidents: FFXIV_DATA = loadDataTheQuickestWay("Enpcresident.de.json")
enpcresidentss: FFXIV_DATA = loadDataTheQuickestWay("Enpcresident", translate=True)
contentfinderconditionX: FFXIV_DATA = loadDataTheQuickestWay("ContentFinderCondition.de.json")
