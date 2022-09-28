#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
LANGUAGES = ["de", "en", "fr", "ja", "cn", "ko"]
XLSXELEMENTS = ["exclude", "date", "sortid", "title", "categories", "slug", "image", "patchNumber", "patchName", "difficulty", "plvl", "plvl_sync", "ilvl", "ilvl_sync", "quest_id", "gearset_loot", "tt_card1", "tt_card2", "orchestrion", "orchestrion2", "orchestrion3", "orchestrion4", "orchestrion5", "orchestrion_material1", "orchestrion_material2", "orchestrion_material3", "mtqvid1", "mtqvid2", "mrhvid1", "mrhvid2", "mount1", "mount2", "minion1", "minion2", "minion3", "instanceType", "mapid", "bosse", "tags", "teamcraftlink", "garlandtoolslink", "gamerescapelink", "done"]
UNKNOWNTITLE = {'de': 'Unbekannte Herkunft', 'en': 'Unknown Source', 'fr': 'Unknown Source', 'ja': 'Unknown Source', 'cn': 'Unknown Source', 'ko': 'Unknown Source'}

DIFFERENT_PRONOUNS = {'0': 'Der', '1': 'Die', '2': 'Das'}
DIFFERENT_PRONOUNSS = {'0': 'er', '1': 'e', '2': 'es'}

_enemy = {
    "title": "",
    "title_en": "",
    "id": "",
    "hp": {
        "min": 100,
        "max": 0
    },
    "attacks": [{
        "title": "",
        "title_id": "",
        "title_en": "",
        "attack_in_use": "",
        "disable": "",
        "type": "",
        "damage_type": "",
        "damage": {
            "min": 100,
            "max": 0
        },
        "phases": [{"phase": "", }],
        "roles": [{"role": "", }],
        "tags": [{"tag": "", }],
        "notes": [{"note": "", }],
    }],
}
EXAMPLE_SEQUENCE = {
    "sequence": [{
        "phase": "09",
        "name": "phase_name",
        "alerts": [{
            "alert": "Die folgenden Angriffe haben sind entweder unbekannt oder haben keine klare Herkunft",
        }],
        "mechanics": [{
            "title": "sequence-mechanic-01",
            "notes": [{
                "note": "sequence-mechanic-note-01",
            }],
        }],
        "attacks": [{
            "attack": "sequence-attack-01",
        }],
        "images": [{
            "url": "/assets/img/test.jpg",
            "alt": "/assets/img/test.jpg",
            "height": "250px",
        }],
        "videos": [{
            "url": "https&#58;//ffxivguide.akurosia.de/upload/test.mp4",
        }],
    }]
}
EXAMPLE_ADD_SEQUENCE = {
    "sequence": [{"phase": "09", }]
}
