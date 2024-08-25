from ffxiv_aku import loadDataTheQuickestWay, get_any_Versiondata, get_any_Logdata, readJsonFile, storeFilesInTmp
storeFilesInTmp(False)

# from guide_helper/guide
logdata = get_any_Logdata()
logdata_lower = dict((k.lower(), v) for k, v in logdata.items())

storeFilesInTmp(True)

# from header
territorytype_trans = loadDataTheQuickestWay("territorytype_all.json", translate=True)
territorytype = loadDataTheQuickestWay("TerritoryType.json")
patchversions = get_any_Versiondata()
mounts = loadDataTheQuickestWay("mount_all.json", translate=True)
exversion = loadDataTheQuickestWay("exversion_all.json", translate=True)
minions = loadDataTheQuickestWay("companion_all.json", translate=True)
orchestrions = loadDataTheQuickestWay("orchestrion_all.json", translate=True)
orchestrionpath = loadDataTheQuickestWay("OrchestrionPath.json", translate=False)
ttcards = loadDataTheQuickestWay("tripletriadcard_all.json", translate=True)
contentfindercondition = loadDataTheQuickestWay("ContentFinderCondition.de.json")
contentfindercondition_trans = loadDataTheQuickestWay("ContentFinderCondition", translate=True)
contentfinderconditiontransient = loadDataTheQuickestWay("ContentFinderConditionTransient", translate=True)
instancecontent = loadDataTheQuickestWay("InstanceContent.json")
contentmembertype = loadDataTheQuickestWay("ContentMemberType.json")
classjob = loadDataTheQuickestWay("Classjob.de.json")
items = loadDataTheQuickestWay("Item.de.json")
gamerscape_items = readJsonFile("python_scripts/gamerscape_items/after_item_scan.json")

# from guide_helper
action = loadDataTheQuickestWay("action_all.json", translate=True)
bnpcname = loadDataTheQuickestWay("bnpcname_all.json", translate=True)
eobjname = loadDataTheQuickestWay("eobjname_all.json", translate=True)
enpcresident = loadDataTheQuickestWay("enpcresident_all.json", translate=True)

# from helper
placename = loadDataTheQuickestWay("placename_all.json", translate=True)

# from guide/guide_helper
status = loadDataTheQuickestWay("status_all.json", translate=True)

# from xlsx entry helper
# quests = loadDataTheQuickestWay("Quest.de.json")
quests_all = loadDataTheQuickestWay("quest_all.json", translate=True)
questss = loadDataTheQuickestWay("Quest.de.json", exd="raw-exd-all")
enpcresidents = loadDataTheQuickestWay("Enpcresident.de.json")
enpcresidentss = loadDataTheQuickestWay("Enpcresident", translate=True)
contentfinderconditionX = loadDataTheQuickestWay("ContentFinderCondition.de.json")
