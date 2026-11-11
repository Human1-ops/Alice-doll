"""
Unit and integration tests for Sphere Device & Alphabet Adventure Game.
"""

import os
import subprocess
import sys
import pytest

from alphabet_adventure import (
    AlphabetAdventureGame,
    MicroSDCartridge,
    SphereDevice,
    build_default_cartridge,
)


class TestSphereDeviceHardware:
    def test_device_initialization_defaults(self):
        device = SphereDevice()
        assert device.SCREEN_DIAMETER_INCHES == 6.0
        assert device.bead_count == 24
        assert len(device.beads) == 24
        assert device.pull_cord_extension == 0.0
        assert device.rotation_degrees == 0.0
        assert device.stylus_down is False

    def test_pull_cord_mechanic(self):
        device = SphereDevice()
        # Normal pull
        ext = device.pull_cord(0.75)
        assert ext == 0.75
        assert device.pull_cord_extension == 0.75

        # Clamp max
        ext_max = device.pull_cord(1.5)
        assert ext_max == 1.0

        # Clamp min
        ext_min = device.pull_cord(-0.2)
        assert ext_min == 0.0

        # Release recoil
        device.pull_cord(0.8)
        recoil = device.release_pull_cord()
        assert recoil == 0.8
        assert device.pull_cord_extension == 0.0

    def test_twist_dial_mechanic(self):
        device = SphereDevice()
        # Relative twist
        rot = device.twist_dial(45.0)
        assert rot == 45.0
        assert device.rotation_degrees == 45.0

        # Wrap around 360
        rot2 = device.twist_dial(330.0)
        assert rot2 == 15.0

        # Set absolute rotation
        device.set_rotation(180.0)
        assert device.rotation_degrees == 180.0

    def test_shake_mechanic_and_beads(self):
        device = SphereDevice()
        init_positions = [(b.x, b.y) for b in device.beads]

        energy, count = device.rattle_beads(shake_intensity=2.5)
        assert energy == 2.5
        assert count == 24

        new_positions = [(b.x, b.y) for b in device.beads]
        # Positions or velocities must have changed due to rattle
        assert init_positions != new_positions

    def test_talk_mechanic(self):
        device = SphereDevice()
        phrase = device.speak("hello alpha", sound_level=0.9)
        assert phrase == "HELLO ALPHA"
        assert device.last_spoken_phrase == "HELLO ALPHA"
        assert device.last_sound_level == 0.9

    def test_stylus_mechanic(self):
        device = SphereDevice()
        device.dock_stylus()
        assert device.stylus_docked is True

        device.undock_stylus()
        assert device.stylus_docked is False

        device.stylus_touch(0.2, -0.3, is_touching=True)
        assert device.stylus_pos == (0.2, -0.3)
        assert len(device.stylus_stroke_history) == 1

        # Clamping outside circular 6-inch bounds
        device.stylus_touch(2.0, 0.0, is_touching=True)
        assert device.stylus_pos[0] == pytest.approx(1.0)
        assert len(device.stylus_stroke_history) == 2

        device.clear_stylus_strokes()
        assert len(device.stylus_stroke_history) == 0

    def test_microsd_cartridge_mechanic(self):
        device = SphereDevice()
        cart = build_default_cartridge()

        assert device.read_cartridge_data() is None

        inserted = device.insert_cartridge(cart)
        assert inserted is True
        assert device.cartridge_inserted == cart

        data = device.read_cartridge_data()
        assert data["title"] == cart.title
        assert len(data["levels"]) == len(cart.levels_data)

        ejected = device.eject_cartridge()
        assert ejected == cart
        assert device.cartridge_inserted is None


class TestAlphabetAdventureGame:
    def test_game_full_progression_stage_by_stage(self):
        device = SphereDevice()
        cart = build_default_cartridge()
        game = AlphabetAdventureGame(device)
        game.load_from_cartridge(cart)

        lvl = game.get_current_level()
        assert lvl["letter"] == "A"
        assert game.current_stage == 1

        # 1. Twist Dial stage
        ok, _ = game.check_twist_step()
        assert ok is False  # current dial 0 vs target 45
        device.twist_dial(45.0)
        ok, msg = game.check_twist_step()
        assert ok is True
        assert "Astronaut Island" in msg
        assert game.advance_stage_1_twist() is True
        assert game.current_stage == 2
        assert game.score == 100

        # 2. Shake Beads stage
        ok, _ = game.check_shake_step()
        assert ok is False
        device.rattle_beads(2.0)
        ok, msg = game.check_shake_step()
        assert ok is True
        assert game.advance_stage_2_shake() is True
        assert game.current_stage == 3
        assert game.score == 200

        # 3. Pull Cord stage
        ok, _ = game.check_pull_step()
        assert ok is False
        device.pull_cord(0.8)
        ok, msg = game.check_pull_step()
        assert ok is True
        assert game.advance_stage_3_pull() is True
        assert game.current_stage == 4
        assert game.score == 300
        assert device.pull_cord_extension == 0.0  # released

        # 4. Talk Phonics stage
        ok, _ = game.check_talk_step()
        assert ok is False
        device.speak("AH", sound_level=0.8)
        ok, msg = game.check_talk_step()
        assert ok is True
        assert game.advance_stage_4_talk() is True
        assert game.current_stage == 5
        assert game.score == 400

        # 5. Stylus Trace stage
        ok, _ = game.check_stylus_step()
        assert ok is False
        for pt in lvl["trace_template"]:
            device.stylus_touch(pt[0], pt[1], is_touching=True)
        ok, msg = game.check_stylus_step()
        assert ok is True
        assert game.advance_stage_5_stylus() is True

        # Now level 1 is completed, letter A added, saved to cartridge
        assert game.completed_letters == ["A"]
        assert game.score == 600
        assert cart.read_save("score") == 600
        assert cart.read_save("completed_letters") == ["A"]

        # Loop moves to level 2 (Letter B) and stage 1
        assert game.current_stage == 1
        assert game.get_current_level()["letter"] == "B"

    def test_cli_execution_subprocess(self):
        res = subprocess.run(
            [sys.executable, "alphabet_adventure.py", "--test-run"],
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )
        assert res.returncode == 0
        assert "SPHERE DEVICE - ALPHABET ADVENTURE HARDWARE DEMO" in res.stdout
        assert "LEVEL COMPLETE" in res.stdout
        assert "Golden Astronaut Apple" in res.stdout
