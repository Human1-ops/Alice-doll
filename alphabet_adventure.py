#!/usr/bin/env python3
"""
Sphere Device & Alphabet Adventure Game Demo

Hardware Specifications:
- Form Factor: 360-degree Sphere Console (tactile handheld educational orb)
- Display: 6-inch circular high-resolution touchscreen
- Inputs & Sensory Mechanics:
    1. Pull Mechanic: Retractable spring-loaded pull cord / ripcord with force sensor
    2. Twist Mechanic: 360-degree rotating bezel / outer dial ring with click detents
    3. Talk Mechanic: Built-in microphone with speech/phonics detection
    4. Shake Mechanic: Internal cavity with physical acoustic beads detected by accelerometer
    5. Stylus Touch Mechanic: High-precision capacitive/EMR stylus dock & digitizer
    6. MicroSD Slot: Hot-swappable MicroSD game cartridges for loading adventures
"""

import argparse
import math
import os
import random
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class Bead:
    id: int
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    color: str = "gold"


@dataclass
class MicroSDCartridge:
    title: str
    cartridge_id: str
    version: str
    levels_data: List[Dict[str, Any]]
    save_data: Dict[str, Any] = field(default_factory=dict)

    def write_save(self, key: str, value: Any) -> None:
        self.save_data[key] = value

    def read_save(self, key: str, default: Any = None) -> Any:
        return self.save_data.get(key, default)


class SphereDevice:
    """
    Simulation of the physical 6-inch spherical gaming device.
    """

    SCREEN_DIAMETER_INCHES = 6.0
    TOTAL_BEADS = 24

    def __init__(self, name: str = "OrbPlay Sphere-6"):
        self.name = name
        self.screen_on = True

        # 1. Pull mechanic state: extension distance (0.0 relaxed to 1.0 fully pulled)
        self.pull_cord_extension: float = 0.0

        # 2. Twist mechanic state: rotation angle in degrees (0 to 359)
        self.rotation_degrees: float = 0.0

        # 3. Talk mechanic state: audio level (0.0 to 1.0) and recognized spoken phrase
        self.microphone_active: bool = True
        self.last_spoken_phrase: str = ""
        self.last_sound_level: float = 0.0

        # 4. Shake mechanic state: physical beads in internal chamber
        self.beads: List[Bead] = [
            Bead(
                id=i,
                x=math.cos(i * 2 * math.pi / self.TOTAL_BEADS) * 0.5,
                y=math.sin(i * 2 * math.pi / self.TOTAL_BEADS) * 0.5,
                color=random.choice(["#f59e0b", "#ef4444", "#3b82f6", "#10b981", "#8b5cf6"])
            )
            for i in range(self.TOTAL_BEADS)
        ]
        self.last_shake_energy: float = 0.0
        self.bead_count: int = self.TOTAL_BEADS

        # 5. Stylus digitizer state: active coordinates, strokes, and pressure
        self.stylus_docked: bool = False
        self.stylus_down: bool = False
        self.stylus_pos: Tuple[float, float] = (0.0, 0.0)
        self.stylus_stroke_history: List[Tuple[float, float]] = []

        # 6. MicroSD slot
        self.cartridge_inserted: Optional[MicroSDCartridge] = None

    # --- Hardware Mechanics APIs ---

    def insert_cartridge(self, cartridge: MicroSDCartridge) -> bool:
        self.cartridge_inserted = cartridge
        return True

    def eject_cartridge(self) -> Optional[MicroSDCartridge]:
        cart = self.cartridge_inserted
        self.cartridge_inserted = None
        return cart

    def read_cartridge_data(self) -> Optional[Dict[str, Any]]:
        if not self.cartridge_inserted:
            return None
        return {
            "title": self.cartridge_inserted.title,
            "version": self.cartridge_inserted.version,
            "levels": self.cartridge_inserted.levels_data,
        }

    def pull_cord(self, pull_strength: float) -> float:
        """
        Pull mechanic: Simulates pulling the spring-loaded ripcord / tab.
        pull_strength is clamped between 0.0 and 1.0.
        """
        self.pull_cord_extension = max(0.0, min(1.0, pull_strength))
        return self.pull_cord_extension

    def release_pull_cord(self) -> float:
        """Releases the ripcord back to resting position with snap recoil."""
        released_power = self.pull_cord_extension
        self.pull_cord_extension = 0.0
        return released_power

    def twist_dial(self, delta_degrees: float) -> float:
        """
        Twist mechanic: Rotates the outer sphere ring.
        Maintains degree range in [0, 360).
        """
        self.rotation_degrees = (self.rotation_degrees + delta_degrees) % 360.0
        return self.rotation_degrees

    def set_rotation(self, degrees: float) -> float:
        self.rotation_degrees = degrees % 360.0
        return self.rotation_degrees

    def speak(self, phrase: str, sound_level: float = 0.8) -> str:
        """
        Talk mechanic: Feeds verbal/phonics input to the onboard microphone.
        """
        self.last_spoken_phrase = phrase.strip().upper()
        self.last_sound_level = max(0.0, min(1.0, sound_level))
        return self.last_spoken_phrase

    def rattle_beads(self, shake_intensity: float = 1.0) -> Tuple[float, int]:
        """
        Shake mechanic: Shakes the spherical orb. Beads rattle inside the chamber,
        scattering and colliding with the inner shell.
        """
        self.last_shake_energy = max(0.0, min(5.0, shake_intensity))
        # Disperse beads based on shake intensity
        for bead in self.beads:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.1, 0.9) * self.last_shake_energy
            bead.vx = math.cos(angle) * speed
            bead.vy = math.sin(angle) * speed
            bead.x = max(-0.95, min(0.95, bead.x + bead.vx * 0.1))
            bead.y = max(-0.95, min(0.95, bead.y + bead.vy * 0.1))
        return (self.last_shake_energy, len(self.beads))

    def shake(self, shake_intensity: float = 1.0) -> Tuple[float, int]:
        """Alias for rattle_beads."""
        return self.rattle_beads(shake_intensity)

    def undock_stylus(self) -> None:
        self.stylus_docked = False

    def dock_stylus(self) -> None:
        self.stylus_docked = True
        self.stylus_down = False

    def stylus_touch(self, x: float, y: float, is_touching: bool = True) -> None:
        """
        Stylus mechanic: Touch screen interaction.
        x and y are normalized to screen radius (-1.0 to 1.0).
        """
        dist = math.sqrt(x * x + y * y)
        if dist > 1.0:
            # Constrain to circular 6-inch screen
            x /= dist
            y /= dist

        self.stylus_pos = (x, y)
        self.stylus_down = is_touching
        if is_touching:
            self.stylus_stroke_history.append((x, y))

    def clear_stylus_strokes(self) -> None:
        self.stylus_stroke_history.clear()


class AlphabetAdventureGame:
    """
    Alphabet Adventure Game implementation designed specifically
    for the Sphere Device hardware.

    Adventure Quest Stages:
    1. Twist Mechanic: Twist the sphere dial to locate the magical letter island.
    2. Shake Mechanic: Shake the sphere to make the internal beads rattle and shake dust/clouds off the letter.
    3. Pull Mechanic: Pull back the spring launcher cord to catapult the adventure explorer onto the island!
    4. Talk Mechanic: Speak the letter phonics/sound into the sphere microphone to awaken the letter spirit!
    5. Stylus Mechanic: Use the precision stylus on the 6" circular screen to trace and draw the letter to complete the quest!
    """

    ALPHABET_DATA = [
        {
            "letter": "A",
            "name": "Astronaut Island",
            "phonics": "AH",
            "word": "APPLE",
            "target_angle": 45.0,
            "target_letter": "A",
            "trace_template": [(-0.4, 0.4), (0.0, -0.5), (0.4, 0.4), (-0.2, 0.1), (0.2, 0.1)],
            "reward": "Golden Astronaut Apple",
        },
        {
            "letter": "B",
            "name": "Bumblebee Bay",
            "phonics": "BUH",
            "word": "BEAR",
            "target_angle": 120.0,
            "target_letter": "B",
            "trace_template": [(-0.3, -0.5), (-0.3, 0.5), (0.1, 0.0), (-0.3, 0.0), (0.2, 0.5)],
            "reward": "Bouncing Honey Berry",
        },
        {
            "letter": "C",
            "name": "Crystal Cave",
            "phonics": "KUH",
            "word": "CAT",
            "target_angle": 210.0,
            "target_letter": "C",
            "trace_template": [(0.3, -0.4), (0.0, -0.5), (-0.3, 0.0), (0.0, 0.5), (0.3, 0.4)],
            "reward": "Cosmic Cat Crystal",
        },
        {
            "letter": "D",
            "name": "Dragon Dunes",
            "phonics": "DUH",
            "word": "DRAGON",
            "target_angle": 300.0,
            "target_letter": "D",
            "trace_template": [(-0.3, -0.5), (-0.3, 0.5), (0.2, 0.3), (0.2, -0.3), (-0.3, -0.5)],
            "reward": "Dazzling Dragon Diamond",
        },
    ]

    STAGE_NAMES = [
        "1. TWIST DIAL - Align Compass with Target Island",
        "2. SHAKE BEADS - Clear Mystical Fog with Rattle Vibrations",
        "3. PULL CORD - Slingshot Launch onto the Island",
        "4. TALK PHONICS - Speak the Magic Phonics Sound",
        "5. STYLUS TRACE - Draw the Letter Shape on 6-inch Screen",
    ]

    def __init__(self, device: Optional[SphereDevice] = None):
        self.device = device or SphereDevice()
        self.current_level_idx: int = 0
        self.current_stage: int = 1  # Stages 1 to 5
        self.score: int = 0
        self.completed_letters: List[str] = []
        self.game_over: bool = False
        self.stage_message: str = ""

    def load_from_cartridge(self, cartridge: MicroSDCartridge) -> bool:
        if not self.device.insert_cartridge(cartridge):
            return False
        self.current_level_idx = cartridge.read_save("current_level", 0)
        self.score = cartridge.read_save("score", 0)
        self.completed_letters = cartridge.read_save("completed_letters", [])
        return True

    def get_current_level(self) -> Dict[str, Any]:
        return self.ALPHABET_DATA[self.current_level_idx % len(self.ALPHABET_DATA)]

    # Stage 1: Twist
    def check_twist_step(self, tolerance_degrees: float = 15.0) -> Tuple[bool, str]:
        level = self.get_current_level()
        target = level["target_angle"]
        curr = self.device.rotation_degrees
        # Calculate circular difference
        diff = abs((curr - target + 180) % 360 - 180)
        if diff <= tolerance_degrees:
            self.stage_message = f"Perfect! Dial locked on {level['name']} at {target:.0f}°!"
            return True, self.stage_message
        return False, f"Keep twisting! Target angle is {target:.0f}°, current dial is {curr:.1f}°."

    def advance_stage_1_twist(self) -> bool:
        ok, msg = self.check_twist_step()
        if ok and self.current_stage == 1:
            self.current_stage = 2
            self.score += 100
            return True
        return False

    # Stage 2: Shake beads
    def check_shake_step(self, min_energy: float = 1.5) -> Tuple[bool, str]:
        level = self.get_current_level()
        energy = self.device.last_shake_energy
        if energy >= min_energy:
            self.stage_message = f"Rattle beads dispersed the cloud cover! Island {level['name']} is visible!"
            return True, self.stage_message
        return False, f"Shake harder! Beads rattled with energy {energy:.1f}/{min_energy}."

    def advance_stage_2_shake(self) -> bool:
        ok, msg = self.check_shake_step()
        if ok and self.current_stage == 2:
            self.current_stage = 3
            self.score += 100
            return True
        return False

    # Stage 3: Pull cord
    def check_pull_step(self, min_pull: float = 0.7) -> Tuple[bool, str]:
        cord_extension = self.device.pull_cord_extension
        if cord_extension >= min_pull:
            self.stage_message = f"Sling cord primed at {cord_extension * 100:.0f}% tension! WHOOSH! Landed!"
            return True, self.stage_message
        return False, f"Pull the ripcord further back! Tension is {cord_extension * 100:.0f}%, need {min_pull * 100:.0f}%."

    def advance_stage_3_pull(self) -> bool:
        ok, msg = self.check_pull_step()
        if ok and self.current_stage == 3:
            self.device.release_pull_cord()
            self.current_stage = 4
            self.score += 100
            return True
        return False

    # Stage 4: Talk
    def check_talk_step(self) -> Tuple[bool, str]:
        level = self.get_current_level()
        spoken = self.device.last_spoken_phrase
        target_ph = level["phonics"]
        target_let = level["letter"]
        target_w = level["word"]

        # Matches phonics sound, letter name, or word
        valid_words = [target_ph, target_let, target_w]
        if any(w in spoken for w in valid_words) and self.device.last_sound_level >= 0.3:
            self.stage_message = f"The Letter Guardian heard '{spoken}'! The ancient glyph activates!"
            return True, self.stage_message
        return False, f"Speak loudly into the microphone! Say '{target_ph}', '{target_let}', or '{target_w}'."

    def advance_stage_4_talk(self) -> bool:
        ok, msg = self.check_talk_step()
        if ok and self.current_stage == 4:
            self.current_stage = 5
            self.score += 100
            return True
        return False

    # Stage 5: Stylus Trace
    def check_stylus_step(self, min_points: int = 5) -> Tuple[bool, str]:
        level = self.get_current_level()
        strokes = self.device.stylus_stroke_history
        if len(strokes) >= min_points:
            self.stage_message = f"Magnificent calligraphy! Letter '{level['letter']}' is forged with the stylus!"
            return True, self.stage_message
        return False, f"Trace letter '{level['letter']}' with the stylus! Traced points: {len(strokes)}/{min_points}."

    def advance_stage_5_stylus(self) -> bool:
        ok, msg = self.check_stylus_step()
        if ok and self.current_stage == 5:
            level = self.get_current_level()
            self.completed_letters.append(level["letter"])
            self.score += 200
            self.device.clear_stylus_strokes()

            if self.device.cartridge_inserted:
                self.device.cartridge_inserted.write_save("score", self.score)
                self.device.cartridge_inserted.write_save("completed_letters", self.completed_letters)

            self.current_level_idx += 1
            if self.current_level_idx >= len(self.ALPHABET_DATA):
                self.game_over = True
                self.stage_message = "All Alphabet Adventure Islands completed! You are the Alphabet Master!"
            else:
                self.current_stage = 1
                new_lvl = self.get_current_level()
                self.stage_message = f"Quest unlocked: Next Island is {new_lvl['name']} ({new_lvl['letter']})!"
            return True
        return False


def build_default_cartridge() -> MicroSDCartridge:
    return MicroSDCartridge(
        title="Alphabet Adventure: Realm of Letters",
        cartridge_id="ORB-CART-ALPHA-01",
        version="1.0.0",
        levels_data=AlphabetAdventureGame.ALPHABET_DATA,
    )


def run_demo_step_by_step(interactive: bool = False) -> None:
    print("=" * 65)
    print(" 🔮 SPHERE DEVICE - ALPHABET ADVENTURE HARDWARE DEMO 🔮")
    print("=" * 65)
    print("Spherical Chassis: 6-inch Circular Display with Touch Stylus")
    print("Built-in Mechanics: Twist Ring, Pull Ripcord, Microphone, Beads Shaker")
    print("Cartridge Slot: MicroSD Storage")
    print("-" * 65)

    # 1. Initialize Device & Insert Cartridge
    device = SphereDevice()
    cartridge = build_default_cartridge()
    print("[1] Inserting MicroSD Cartridge into Sphere slot...")
    device.insert_cartridge(cartridge)
    print(f"    --> Cartridge Mounted: '{cartridge.title}' (v{cartridge.version})")

    game = AlphabetAdventureGame(device)
    game.load_from_cartridge(cartridge)

    lvl = game.get_current_level()
    print(f"\n[STARTING LEVEL 1] Island: {lvl['name']} (Letter {lvl['letter']})")

    # STAGE 1: TWIST MECHANIC
    print("\n--- STAGE 1: TWIST MECHANIC ---")
    print(f"Goal: Twist the sphere dial to align with angle {lvl['target_angle']}°")
    device.twist_dial(lvl["target_angle"])
    print(f"Action: Dial twisted to {device.rotation_degrees}°.")
    success, msg = game.check_twist_step()
    print(f"Result: {msg}")
    game.advance_stage_1_twist()

    # STAGE 2: SHAKE MECHANIC WITH BUILT-IN BEADS
    print("\n--- STAGE 2: SHAKE MECHANIC (INTERNAL BEADS) ---")
    print("Goal: Rattle the sphere to produce bead collisions and clear the fog")
    intensity, bead_count = device.rattle_beads(shake_intensity=3.0)
    print(f"Action: Shook sphere with {intensity}x force! {bead_count} internal beads rattled.")
    success, msg = game.check_shake_step()
    print(f"Result: {msg}")
    game.advance_stage_2_shake()

    # STAGE 3: PULL MECHANIC
    print("\n--- STAGE 3: PULL MECHANIC ---")
    print("Goal: Pull the retractable spring ripcord to launch explorer")
    tension = device.pull_cord(0.85)
    print(f"Action: Pulled ripcord to {tension * 100:.0f}% tension.")
    success, msg = game.check_pull_step()
    print(f"Result: {msg}")
    game.advance_stage_3_pull()

    # STAGE 4: TALK MECHANIC
    print("\n--- STAGE 4: TALK MECHANIC ---")
    print(f"Goal: Speak the phonics sound '{lvl['phonics']}' into the microphone")
    spoken = device.speak(lvl["phonics"], sound_level=0.9)
    print(f"Action: Microphone captured voice audio: '{spoken}' (Volume: 90%)")
    success, msg = game.check_talk_step()
    print(f"Result: {msg}")
    game.advance_stage_4_talk()

    # STAGE 5: STYLUS TOUCH MECHANIC
    print("\n--- STAGE 5: STYLUS TOUCH MECHANIC ---")
    print(f"Goal: Un-dock precision stylus and trace letter '{lvl['letter']}' on 6-inch screen")
    device.undock_stylus()
    for pt in lvl["trace_template"]:
        device.stylus_touch(pt[0], pt[1], is_touching=True)
    print(f"Action: Stylus traced {len(device.stylus_stroke_history)} path points onto 6\" screen.")
    success, msg = game.check_stylus_step()
    print(f"Result: {msg}")
    game.advance_stage_5_stylus()

    print("\n" + "=" * 65)
    print(f"🎉 LEVEL COMPLETE! Reward Earned: {lvl['reward']}")
    print(f"Total Score: {game.score} pts | Completed Letters: {game.completed_letters}")
    print(f"Saved to MicroSD: {cartridge.save_data}")
    print("=" * 65)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sphere 6-inch Handheld Alphabet Adventure Demo"
    )
    parser.add_argument(
        "--test-run",
        action="store_true",
        help="Run through a non-interactive simulation of all mechanics",
    )
    args = parser.parse_args()

    run_demo_step_by_step(interactive=False)


if __name__ == "__main__":
    main()
