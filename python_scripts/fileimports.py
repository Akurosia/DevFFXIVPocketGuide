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
territorytype: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\TerritoryType.json")
patchversions: FFXIV_DATA = get_any_Versiondata()
mounts: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\Mount.json")
exversion: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\ExVersion.json")
minions: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\Companion.json")
orchestrions: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\Orchestrion.json")
orchestrionpath: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\OrchestrionPath.json")
ttcards: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\TripleTriadCard.json")
contentfindercondition: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\ContentFinderCondition.json")
contentfinderconditiontransient: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\ContentFinderConditionTransient.json")
instancecontent: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\InstanceContent.json")
contentmembertype: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\ContentMemberType.json")
classjob: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\Classjob.json")
items: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\Item.json")
try:
    gamerscape_items: FFXIV_DATA = readJsonFile("python_scripts/gamerscape_items/after_item_scan.json")
except:
    gamerscape_items: FFXIV_DATA = readJsonFile("gamerscape_items/after_item_scan.json")

fates: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\Fate.json")
ces: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\DynamicEvent.json")
ces_type: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\DynamicEventType.json")

# from guide_helper
action: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\Action.json")
bnpcname: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\BNpcName.json")
eobjname: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\EObjName.json")
enpcresident: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\ENpcResident.json")

# from helper
placename: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\PlaceName.json")

# from guide/guide_helper
status: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\Status.json")

# from xlsx entry helper
quests: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\Quest.json")

npcyell: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\NpcYell.json")
instancecontenttextdata: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\InstanceContentTextData.json")
fateevent: FFXIV_DATA = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\FateEvent.json")
