import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from python_scripts.convert_skills_to_guide_form_helper.beastmaster import (
    build_capture_list, build_pet_attacks, build_beastmaster_job_skills, load_beastmaster_data,
)


class BeastmasterTests(unittest.TestCase):
    def test_job_skills_come_from_bst_player_actions_only(self):
        row = {"ClassJob": {"row_id": "43"}, "IsPlayerAction": "True", "IsPvP": "False",
               "Name_en": "Smash Axe", "ClassJobLevel": "1", "ActionCategory": {"row_id": "3"}}
        actions = {"44879": row, "7559": {**row, "ClassJob": {"row_id": "25"}},
                   "9": {**row, "IsPvP": "True"}, "10": {**row, "IsPlayerAction": "False"}}
        skills = build_beastmaster_job_skills(actions, {"44879": {"Description_en": "Attack"}})
        self.assertEqual(list(skills), ["44879"])
        self.assertEqual(skills["44879"]["Level"], "1")
        self.assertEqual(skills["44879"]["Type"], "GCD")
        self.assertEqual(skills["44879"]["Description"]["en"], "Attack")

    def test_pet_attacks_use_descriptions_and_convert_timing(self):
        ability = {"row_id": "44939", "Name": "Vliesabreibung", "Recast100ms": "100",
                   "Icon": {"path_hr1": "ui/icon/003000/003906_hr1.tex"}}
        attacks = build_pet_attacks({"Abilities": [ability, ability, {"row_id": "0"}]},
                                   {"44939": {"Description": "Attacke\\nWert: <500>"}})
        self.assertEqual(len(attacks), 1)
        self.assertEqual(attacks[0]["recast"], "10s")
        self.assertEqual(attacks[0]["icon"], "003000/003906_hr1.webp")
        self.assertEqual(attacks[0]["description"]["de"], "Attacke<br>Wert: &lt;500&gt;")

    def test_local_file_wins_including_empty_export(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "XBMPet.json").write_text('{}', encoding="utf-8-sig")
            loader = Mock(side_effect=AssertionError("Must not call server"))
            with patch.dict(sys.modules, {"ffxiv_aku": SimpleNamespace(loadDataTheQuickestWay=loader)}):
                self.assertEqual(load_beastmaster_data("XBMPet", local_dir=path), {})

    def test_missing_local_file_uses_raw_server_sheet(self):
        with TemporaryDirectory() as directory:
            loader = Mock(return_value={"1": {"Name": "Schaf"}})
            with patch.dict(sys.modules, {"ffxiv_aku": SimpleNamespace(loadDataTheQuickestWay=loader)}):
                self.assertEqual(load_beastmaster_data("Pet", local_dir=Path(directory)), loader.return_value)
            loader.assert_called_once_with("Pet.json", translate=False)

    def test_invalid_local_file_is_not_silently_replaced(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "XBMPet.json").write_text('{', encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_beastmaster_data("XBMPet", local_dir=path)

    def test_match_only_in_hint_zone_and_not_inside_other_words(self):
        rows = {"0": {"Pet": {"value": "0"}}, "14": {
            "Pet": {"value": "60"}, "Location": {"value": "30", "sheet": "PlaceName"},
        }}
        logs = {"Zentrales La Noscea": {
            "Junger Puk": {"id": ["401", "401"]}, "Spukgespenst": {"id": "404"},
            "Puk": {"name": "metadata"},
        }, "Anderer Ort": {"Puk": {"id": "999"}}}
        entries = build_capture_list(rows, {"60": {"Name": "Puk"}},
                                     {"30": {"Name_de": "Zentrales La Noscea"}}, {}, logs)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["sightings"], [{"name": "Junger Puk", "enemy_ids": ["401"]}])

    def test_dungeon_and_missing_hint_remain_visible_without_sightings(self):
        rows = {"1": {"Pet": {"value": "47"}, "Location": {"value": "0"}},
                "48": {"Pet": {"value": "95"}, "Location": {"value": "28", "sheet": "ContentFinderCondition"}}}
        entries = build_capture_list(rows, {"47": {"Name": "Cu Sith"}, "95": {"Name": "Karlabos"}},
                                     {}, {"28": {"Name": "Sastasha (schwer)"}}, {})
        self.assertEqual(entries[0]["location"], "")
        self.assertEqual(entries[1]["location"], "Sastasha (schwer)")
        self.assertEqual(entries[1]["location_type"], "Inhalt")
        self.assertEqual(entries[1]["sightings"], [])

    def test_unresolved_pet_and_empty_sheet_fail_loudly(self):
        with self.assertRaises(ValueError):
            build_capture_list({"1": {"Pet": {"value": "47"}}}, {}, {}, {}, {})
        with self.assertRaises(ValueError):
            build_capture_list({"0": {"Pet": {"value": "0"}}}, {}, {}, {}, {})


if __name__ == "__main__":
    unittest.main()
