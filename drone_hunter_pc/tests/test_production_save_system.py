import os
import sys
import json
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.systems.save_system import SaveSystem, CURRENT_SAVE_VERSION, NUM_SAVE_SLOTS
from src.core.campaign_state import CampaignState
from src.core.save_controller import SaveController
from src.core.game_context import GameContext


class TestProductionSaveSystem(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _get_custom_save_sys(self, filename="save_slot_1.json"):
        sys = SaveSystem(save_filename=filename)
        sys.base_dir = self.test_dir
        sys.save_path = os.path.join(self.test_dir, filename)
        sys.temp_path = sys.save_path + ".tmp"
        return sys

    def test_default_save_schema_has_no_obsolete_fields(self):
        """Verify get_default_save_data() contains ONLY current schema and lacks obsolete fields."""
        save_sys = SaveSystem(slot_index=0)
        defaults = save_sys.get_default_save_data()

        self.assertIn("save_version", defaults)
        self.assertEqual(defaults["save_version"], CURRENT_SAVE_VERSION)
        self.assertIn("campaign_state", defaults)
        self.assertIn("scrap", defaults)

        # Obsolete fields MUST NOT exist in default save data
        self.assertNotIn("coins", defaults)
        self.assertNotIn("stages", defaults)
        self.assertNotIn("missions", defaults)
        self.assertNotIn("sector_progress", defaults)
        self.assertNotIn("sectors", defaults)
        self.assertNotIn("bosses_defeated", defaults)
        self.assertNotIn("selected_skin", defaults)

    def test_versioned_save_format(self):
        """Verify newly created saves write save_version: 1."""
        save_sys = self._get_custom_save_sys("test_ver.json")
        save_sys.save({"scrap": 500, "highscore": 12000})

        with open(save_sys.save_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("save_version", data)
        self.assertEqual(data["save_version"], CURRENT_SAVE_VERSION)
        self.assertEqual(data["scrap"], 500)
        self.assertEqual(data["highscore"], 12000)

    def test_future_save_version_rejected(self):
        """Verify an unsupported future save_version (e.g. 999) is safely rejected and returns safe defaults."""
        save_sys = self._get_custom_save_sys("future_save.json")
        future_payload = {
            "save_version": 999,
            "scrap": 999999,
            "highscore": 999999,
            "campaign_state": {"current_mission": "S99_M99"}
        }
        with open(save_sys.save_path, "w", encoding="utf-8") as f:
            json.dump(future_payload, f)

        loaded = save_sys.load()
        # Should return safe defaults instead of corrupting runtime state
        self.assertEqual(loaded["scrap"], 0)
        self.assertEqual(loaded["highscore"], 0)
        self.assertEqual(loaded["campaign_state"]["current_mission"], "S1_M1")

    def test_obsolete_fields_omitted_from_new_saves(self):
        """Verify new saves do NOT write coins, stages, bosses_defeated, selected_skin, or duplicate missions trees."""
        save_sys = self._get_custom_save_sys("test_clean.json")
        save_sys.save({
            "scrap": 300,
            "coins": 300,
            "stages": [True] * 15,
            "bosses_defeated": [1, 2],
            "selected_skin": 2,
            "missions": {"current_sector": 2}
        })

        with open(save_sys.save_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        self.assertNotIn("coins", raw_data)
        self.assertNotIn("stages", raw_data)
        self.assertNotIn("bosses_defeated", raw_data)
        self.assertNotIn("selected_skin", raw_data)
        self.assertNotIn("missions", raw_data)
        self.assertNotIn("sector_progress", raw_data)
        self.assertNotIn("sectors", raw_data)
        self.assertIn("campaign_state", raw_data)
        self.assertIn("save_version", raw_data)

    def test_save_load_round_trip(self):
        """Verify save -> load preserves active gameplay state."""
        save_sys = self._get_custom_save_sys("test_roundtrip.json")
        camp = CampaignState.deserialize({
            "current_mission": "S2_M3",
            "completed_missions": ["S1_M1", "S1_M2", "S2_M1", "S2_M2"],
            "unlocked_missions": ["S1_M1", "S1_M2", "S2_M1", "S2_M2", "S2_M3"],
            "completed_sectors": [1],
            "unlocked_sectors": [1, 2]
        })
        save_sys.save({
            "scrap": 1250,
            "highscore": 45000,
            "play_time": 360,
            "selected_drone": "interceptor",
            "campaign_state": camp.serialize(),
            "unlocked_weapons": ["pulse", "rapid", "scatter"],
            "difficulty_mode": 2
        })

        loaded = save_sys.load()
        self.assertEqual(loaded["scrap"], 1250)
        self.assertEqual(loaded["highscore"], 45000)
        self.assertEqual(loaded["play_time"], 360)
        self.assertEqual(loaded["selected_drone"], "interceptor")
        self.assertEqual(loaded["unlocked_weapons"], ["pulse", "rapid", "scatter"])
        self.assertEqual(loaded["difficulty_mode"], 2)

        restored_camp = CampaignState.deserialize(loaded["campaign_state"])
        self.assertEqual(restored_camp.current_mission, "S2_M3")
        self.assertIn("S2_M2", restored_camp.completed_missions)

    def test_legacy_unversioned_save_compatibility(self):
        """Verify an old unversioned save containing coins, missions, and stages loads correctly."""
        save_sys = self._get_custom_save_sys("legacy_save.json")
        legacy_data = {
            "coins": 850,
            "highscore": 9990,
            "missions": {
                "current_sector": 3,
                "current_mission": 2,
                "completed": ["S1_M1", "S1_M2", "S2_M1"],
                "unlocked": ["S1_M1", "S1_M2", "S2_M1", "S3_M2"]
            },
            "sector_progress": {
                "completed": [1, 2],
                "unlocked": [1, 2, 3]
            },
            "bosses_defeated": [1, 2],
            "selected_skin": 1,
            "stages": [True] * 15
        }
        with open(save_sys.save_path, "w", encoding="utf-8") as f:
            json.dump(legacy_data, f)

        loaded = save_sys.load()
        # coins migrated to scrap
        self.assertEqual(loaded["scrap"], 850)
        self.assertEqual(loaded["highscore"], 9990)
        # Reconstructed campaign_state
        self.assertIn("campaign_state", loaded)
        camp = CampaignState.deserialize(loaded["campaign_state"])
        self.assertEqual(camp.current_mission, "S3_M2")
        self.assertIn("S2_M1", camp.completed_missions)
        self.assertIn(3, camp.unlocked_sectors)

    def test_corrupted_json_fallback(self):
        """Verify corrupted/malformed JSON falls back safely to default values."""
        save_sys = self._get_custom_save_sys("corrupt.json")
        with open(save_sys.save_path, "w", encoding="utf-8") as f:
            f.write("{ INVALID JSON DATA %%% NOT PARSABLE }")

        loaded = save_sys.load()
        self.assertEqual(loaded["scrap"], 0)
        self.assertEqual(loaded["highscore"], 0)
        self.assertIn("campaign_state", loaded)

    def test_missing_save_fallback(self):
        """Verify non-existent save file returns default state without crashing."""
        save_sys = self._get_custom_save_sys("non_existent_file.json")
        loaded = save_sys.load()
        self.assertEqual(loaded["scrap"], 0)
        self.assertEqual(loaded["highscore"], 0)
        self.assertEqual(loaded["selected_drone"], "striker")

    def test_invalid_payload_normalization(self):
        """Verify malformed payload fields (negative scrap, invalid difficulty, bad drone) are sanitized."""
        save_sys = self._get_custom_save_sys("sanitize.json")
        save_sys.save({
            "scrap": -999,
            "highscore": -500,
            "difficulty_mode": 19,
            "selected_drone": "non_existent_cheat_drone",
            "upgrades": "not_a_dict",
            "weapon_upgrades": "not_a_dict",
            "audio_settings": "not_a_dict"
        })

        loaded = save_sys.load()
        self.assertGreaterEqual(loaded["scrap"], 0)
        self.assertGreaterEqual(loaded["highscore"], 0)
        self.assertIn(loaded["difficulty_mode"], [0, 1, 2, 3, 4])
        self.assertEqual(loaded["selected_drone"], "striker")
        self.assertIsInstance(loaded["upgrades"], dict)
        self.assertIsInstance(loaded["weapon_upgrades"], dict)
        self.assertIsInstance(loaded["audio_settings"], dict)

    def test_slot_isolation(self):
        """Verify slots 0, 1, 2 save and load independently without cross-contamination."""
        sys0 = SaveSystem(slot_index=0)
        sys0.base_dir = self.test_dir
        sys0.set_slot(0)

        sys1 = SaveSystem(slot_index=1)
        sys1.base_dir = self.test_dir
        sys1.set_slot(1)

        sys2 = SaveSystem(slot_index=2)
        sys2.base_dir = self.test_dir
        sys2.set_slot(2)

        sys0.save({"scrap": 100, "highscore": 1000})
        sys1.save({"scrap": 200, "highscore": 2000})
        sys2.save({"scrap": 300, "highscore": 3000})

        self.assertEqual(sys0.load()["scrap"], 100)
        self.assertEqual(sys1.load()["scrap"], 200)
        self.assertEqual(sys2.load()["scrap"], 300)

    def test_strict_slot_validation(self):
        """Verify valid slots 0..2 succeed while invalid slot indices are rejected strictly."""
        sys = SaveSystem(slot_index=0)
        sys.base_dir = self.test_dir

        # Valid slots
        sys.set_slot(0)
        sys.set_slot(1)
        sys.set_slot(2)

        # Invalid slot indices MUST raise ValueError
        with self.assertRaises(ValueError):
            sys.set_slot(-1)

        with self.assertRaises(ValueError):
            sys.set_slot(3)

        with self.assertRaises(ValueError):
            sys.set_slot(99)

        with self.assertRaises(ValueError):
            SaveSystem(slot_index=-1)

        with self.assertRaises(ValueError):
            SaveSystem(slot_index=3)

        # delete_save_slot returns False on invalid slots
        self.assertFalse(sys.delete_save_slot(-1))
        self.assertFalse(sys.delete_save_slot(3))
        self.assertFalse(sys.delete_save_slot(99))

    def test_stale_temp_file_ignored(self):
        """Verify a stale .tmp file does not overwrite or corrupt loading of main save."""
        save_sys = self._get_custom_save_sys("main_save.json")
        save_sys.save({"scrap": 777})

        # Create a stale corrupted temp file
        with open(save_sys.temp_path, "w", encoding="utf-8") as f:
            f.write("{ CORRUPT TEMP FILE }")

        loaded = save_sys.load()
        self.assertEqual(loaded["scrap"], 777)

    def test_save_controller_integration(self):
        """Verify SaveController serializes and restores CampaignState and runtime settings."""
        save_sys = SaveSystem(slot_index=0)
        save_sys.base_dir = self.test_dir
        save_sys.set_slot(0)
        ctrl = SaveController(save_system=save_sys, initial_slot=0)

        ctx = GameContext()
        ctx.scrap = 900
        ctx.highscore = 15000
        ctx.campaign_state = CampaignState.deserialize({
            "current_mission": "S3_M1",
            "completed_missions": ["S1_M1", "S2_M1"],
            "unlocked_missions": ["S1_M1", "S2_M1", "S3_M1"],
            "completed_sectors": [1, 2],
            "unlocked_sectors": [1, 2, 3]
        })
        ctx.selected_drone = "command"

        success = ctrl.save_current_progress(ctx)
        self.assertTrue(success)

        # Restore into clean context
        new_ctx = GameContext()
        ctrl.load_slot(0, new_ctx)

        self.assertEqual(new_ctx.scrap, 900)
        self.assertEqual(new_ctx.highscore, 15000)
        self.assertEqual(new_ctx.selected_drone, "command")
        self.assertEqual(new_ctx.campaign_state.current_mission, "S3_M1")
        self.assertIn("S2_M1", new_ctx.campaign_state.completed_missions)


if __name__ == "__main__":
    unittest.main()
