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

FFXIV_DATA = dict[str, dict[str,str|dict[str,str]]]

ENTRY_DATA = dict[str, Union[
    str,  # For all string values
    int,  # For integer values like 'line_index'
    list[str],  # For lists of strings like 'bosse', 'tags', 'adds'
    dict[str, str]  # For nested dictionaries like 'quest', 'quest_location', 'quest_npc', 'titles'
]]

storeFilesInTmp(False)

# from guide_helper/guide
patchversions: FFXIV_DATA = get_any_Versiondata()
logdata: dict[str, Any] = get_any_Logdata()
logdata_lower = dict((k.lower(), v) for k, v in logdata.items())

storeFilesInTmp(True)


BASEPATH = r"C:\Users\kamot\Desktop\XIVAPI\translated"

# from header
territorytype: FFXIV_DATA = readJsonFile(BASEPATH + r"\TerritoryType.json")
mounts: FFXIV_DATA = readJsonFile(BASEPATH + r"\Mount.json")
exversion: FFXIV_DATA = readJsonFile(BASEPATH + r"\ExVersion.json")
minions: FFXIV_DATA = readJsonFile(BASEPATH + r"\Companion.json")
orchestrions: FFXIV_DATA = readJsonFile(BASEPATH + r"\Orchestrion.json")
orchestrionpath: FFXIV_DATA = readJsonFile(BASEPATH + r"\OrchestrionPath.json")
ttcards: FFXIV_DATA = readJsonFile(BASEPATH + r"\TripleTriadCard.json")
contentfindercondition: FFXIV_DATA = readJsonFile(BASEPATH + r"\ContentFinderCondition.json")
contentfinderconditiontransient: FFXIV_DATA = readJsonFile(BASEPATH + r"\ContentFinderConditionTransient.json")
instancecontent: FFXIV_DATA = readJsonFile(BASEPATH + r"\InstanceContent.json")
contentmembertype: FFXIV_DATA = readJsonFile(BASEPATH + r"\ContentMemberType.json")
classjob: FFXIV_DATA = readJsonFile(BASEPATH + r"\Classjob.json")
items: FFXIV_DATA = readJsonFile(BASEPATH + r"\Item.json")
try:
    gamerscape_items: FFXIV_DATA = readJsonFile("python_scripts/gamerscape_items/after_item_scan.json")
except:
    gamerscape_items: FFXIV_DATA = readJsonFile("gamerscape_items/after_item_scan.json")

fates: FFXIV_DATA = readJsonFile(BASEPATH + r"\Fate.json")
ces: FFXIV_DATA = readJsonFile(BASEPATH + r"\DynamicEvent.json")
ces_type: FFXIV_DATA = readJsonFile(BASEPATH + r"\DynamicEventType.json")

# from guide_helper
action: FFXIV_DATA = readJsonFile(BASEPATH + r"\Action.json")
bnpcname: FFXIV_DATA = readJsonFile(BASEPATH + r"\BNpcName.json")
eobjname: FFXIV_DATA = readJsonFile(BASEPATH + r"\EObjName.json")
enpcresident: FFXIV_DATA = readJsonFile(BASEPATH + r"\ENpcResident.json")

# from helper
placename: FFXIV_DATA = readJsonFile(BASEPATH + r"\PlaceName.json")

# from guide/guide_helper
status: FFXIV_DATA = readJsonFile(BASEPATH + r"\Status.json")

# from xlsx entry helper
quests: FFXIV_DATA = readJsonFile(BASEPATH + r"\Quest.json")

npcyell: FFXIV_DATA = readJsonFile(BASEPATH + r"\NpcYell.json")
instancecontenttextdata: FFXIV_DATA = readJsonFile(BASEPATH + r"\InstanceContentTextData.json")
fateevent: FFXIV_DATA = readJsonFile(BASEPATH + r"\FateEvent.json")

level: FFXIV_DATA = readJsonFile(BASEPATH + r"\Level.json")
treasurespot: FFXIV_DATA = readJsonFile(BASEPATH + r"\TreasureSpot.json")
treasurehuntrank: FFXIV_DATA = readJsonFile(BASEPATH + r"\TreasureHuntRank.json")
treasurehunttexture: FFXIV_DATA = readJsonFile(BASEPATH + r"\TreasureHuntTexture.json")
journalgenre: FFXIV_DATA = readJsonFile(BASEPATH + r"\JournalGenre.json")

#maps = readJsonFile(BASEPATH + r"\Map.json")
aethercurrent = readJsonFile(BASEPATH + r"\AetherCurrent.json")
