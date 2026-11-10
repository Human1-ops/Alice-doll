import os
import subprocess
import sys
import pytest

from life_cycle_demo import (
    FICTIONAL_BABY_FOODS,
    FICTIONAL_DIAPERS,
    Character,
    SimulationDemo,
)


def test_infant_feeding_rules():
    baby = Character(name="Milo")
    assert baby.age_months == 0

    # Under 9 months: Solid food should be rejected
    success, msg = baby.feed("Mashed Sweet Potato & Carrot Puree", "TinyTummy Organics")
    assert not success
    assert "under 9 months need breast milk" in msg

    # Under 9 months: Breast milk accepted
    success, msg = baby.feed("breast milk")
    assert success
    assert "Fed Milo warm breast milk" in msg

    # Advance to 9 months
    for _ in range(9):
        baby.advance_month()
    assert baby.age_months == 9

    # At 9+ months: Solid baby food with fictional brand is accepted
    food = FICTIONAL_BABY_FOODS[0]
    success, msg = baby.feed(food["item"], food["brand"])
    assert success
    assert food["brand"] in msg
    assert "Yum!" in msg


def test_fictional_brands_present():
    food_brands = [f["brand"] for f in FICTIONAL_BABY_FOODS]
    assert "TinyTummy Organics" in food_brands
    assert "NutriTot Purees" in food_brands
    assert "LittleSprout Munchies" in food_brands

    diaper_brands = [d["brand"] for d in FICTIONAL_DIAPERS]
    assert "CloudyBottoms Ultra Dry" in diaper_brands
    assert "SnuggleBum Eco Diapers" in diaper_brands
    assert "CuddlePaws Comfort Fit" in diaper_brands


def test_diaper_change():
    baby = Character(name="Sam")
    baby.hygiene = 20
    res = baby.change_diaper(diaper_brand_index=1)
    assert baby.hygiene == 100
    assert "SnuggleBum Eco Diapers" in res


def test_milestones_and_growth():
    baby = Character(name="Emma")
    all_milestones = []
    for _ in range(12):
        logs = baby.advance_month()
        all_milestones.extend(logs)

    assert "First Smile" in baby.milestones
    assert "Sitting Up" in baby.milestones
    assert "Starting Solid Food" in baby.milestones
    assert "First Birthday & Steps" in baby.milestones
    assert baby.age_years == 1


def test_adulthood_and_grandbaby_at_35():
    demo = SimulationDemo(baby_name="Luna")
    char = demo.current_character
    # Advance to age 18
    for _ in range(18):
        char.advance_year()

    grandbaby = demo.run_adulthood_stage(char)
    assert char.age_years == 35
    assert char.child_name is not None
    assert grandbaby.generation == 2
    assert grandbaby.parent_name == "Luna"
    assert grandbaby.age_years == 0


def test_subprocess_demo_run():
    """Subprocess integration test for running the script via sys.executable."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    process = subprocess.run(
        [sys.executable, "life_cycle_demo.py"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert process.returncode == 0
    stdout = process.stdout
    assert "Starting Generational Life & Baby Care Simulation Demo..." in stdout
    assert "[BABYDOW MODE] Generation 1: Caring for Baby Luna" in stdout
    assert "TinyTummy Organics" in stdout
    assert "CloudyBottoms Ultra Dry" in stdout
    assert "ready to transition from breast milk to solid baby foods" in stdout
    assert "[BITLIFE MODE] Growing Up: Ages 1 to 17 - Luna" in stdout
    assert "[ADULTHOOD & FAMILY TIME] Ages 18 to 35 - Luna" in stdout
    assert "[GRANDBABY ARRIVAL] At age 35, Luna has a baby!" in stdout
    assert "[GENERATIONAL REBIRTH - BITLIFE / BABYDOW MODE]" in stdout
    assert "[BABYDOW MODE] Generation 2: Caring for Baby Aria" in stdout
