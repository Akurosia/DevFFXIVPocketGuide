# -*- coding: utf-8 -*-
# coding: utf8
from typing import Any, Union
from ffxiv_aku import (
    loadDataTheQuickestWay,
    get_any_Versiondata,
    get_any_Logdata,
    storeFilesInTmp,
    readJsonFile,
    get_skills_for_player
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

storeFilesInTmp(False)


BASEPATH = r"P:\extras\json\xivapi_data"

# from header
territorytype: FFXIV_DATA = loadDataTheQuickestWay("TerritoryType.json")
mounts: FFXIV_DATA = loadDataTheQuickestWay("Mount.json")
exversion: FFXIV_DATA = loadDataTheQuickestWay("ExVersion.json")
minions: FFXIV_DATA = loadDataTheQuickestWay("Companion.json")
orchestrions: FFXIV_DATA = loadDataTheQuickestWay("Orchestrion.json")
orchestrionpath: FFXIV_DATA = loadDataTheQuickestWay("OrchestrionPath.json")
ttcards: FFXIV_DATA = loadDataTheQuickestWay("TripleTriadCard.json")
contentfindercondition: FFXIV_DATA = loadDataTheQuickestWay("ContentFinderCondition.json")
contentfinderconditiontransient: FFXIV_DATA = loadDataTheQuickestWay("ContentFinderConditionTransient.json")
instancecontent: FFXIV_DATA = loadDataTheQuickestWay("InstanceContent.json")
contentmembertype: FFXIV_DATA = loadDataTheQuickestWay("ContentMemberType.json")
classjob: FFXIV_DATA = loadDataTheQuickestWay("Classjob.json")
items: FFXIV_DATA = loadDataTheQuickestWay("Item.json")
try:
    gamerscape_items: FFXIV_DATA = readJsonFile("python_scripts/gamerscape_items/after_item_scan.json")
except:
    gamerscape_items: FFXIV_DATA = readJsonFile("gamerscape_items/after_item_scan.json")

fates: FFXIV_DATA = loadDataTheQuickestWay("Fate.json")
ces: FFXIV_DATA = loadDataTheQuickestWay("DynamicEvent.json")
ces_type: FFXIV_DATA = loadDataTheQuickestWay("DynamicEventType.json")

# from guide_helper
action: FFXIV_DATA = loadDataTheQuickestWay("Action.json")
bnpcname: FFXIV_DATA = loadDataTheQuickestWay("BNpcName.json")
eobjname: FFXIV_DATA = loadDataTheQuickestWay("EObjName.json")
enpcresident: FFXIV_DATA = loadDataTheQuickestWay("ENpcResident.json")

# from helper
placename: FFXIV_DATA = loadDataTheQuickestWay("PlaceName.json")

# from guide/guide_helper
status: FFXIV_DATA = loadDataTheQuickestWay("Status.json")

# from xlsx entry helper
quests: FFXIV_DATA = loadDataTheQuickestWay("Quest.json")

npcyell: FFXIV_DATA = loadDataTheQuickestWay("NpcYell.json")
instancecontenttextdata: FFXIV_DATA = loadDataTheQuickestWay("InstanceContentTextData.json")
fateevent: FFXIV_DATA = loadDataTheQuickestWay("FateEvent.json")

level: FFXIV_DATA = loadDataTheQuickestWay("Level.json")
treasurespot: FFXIV_DATA = loadDataTheQuickestWay("TreasureSpot.json")
treasurehuntrank: FFXIV_DATA = loadDataTheQuickestWay("TreasureHuntRank.json")
treasurehunttexture: FFXIV_DATA = loadDataTheQuickestWay("TreasureHuntTexture.json")
journalgenre: FFXIV_DATA = loadDataTheQuickestWay("JournalGenre.json")

maps = loadDataTheQuickestWay("Map.json")
aethercurrent: FFXIV_DATA = loadDataTheQuickestWay("AetherCurrent.json")

achivment: FFXIV_DATA = loadDataTheQuickestWay("Achievement.json")
achivmentkind: FFXIV_DATA = loadDataTheQuickestWay("AchievementKind.json")
achivmentcategory: FFXIV_DATA = loadDataTheQuickestWay("AchievementCategory.json")


miragestoresetitem: FFXIV_DATA = loadDataTheQuickestWay("MirageStoreSetItem.json")
miragestoresetitemlookup: FFXIV_DATA = loadDataTheQuickestWay("MirageStoreSetItemLookup.json")


skills = get_skills_for_player()
pvpskills = get_skills_for_player(True)

addon: FFXIV_DATA = loadDataTheQuickestWay("Addon.json")
actiontransient: FFXIV_DATA = loadDataTheQuickestWay("ActionTransient.json")
craftactions: FFXIV_DATA = loadDataTheQuickestWay("CraftAction.json")
traits: FFXIV_DATA = loadDataTheQuickestWay("Trait.json")
traitstransient: FFXIV_DATA = loadDataTheQuickestWay("TraitTransient.json")
leves: FFXIV_DATA = loadDataTheQuickestWay("Leve.json")
craftleves: FFXIV_DATA = loadDataTheQuickestWay("CraftLeve.json")
bannertimeline: FFXIV_DATA = loadDataTheQuickestWay("BannerTimeline.json")
