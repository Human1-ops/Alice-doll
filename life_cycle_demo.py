"""
Generational Life and Baby Care Simulation Demo.

Features:
- Babydow-like baby care:
  - Months 0 to 9: Fed with breast milk. Solid baby foods cannot be used yet.
  - Months 9+: Transition to real/solid baby foods.
  - Fictional baby food brands (e.g., TinyTummy Organics, NutriTot Purees, LittleSprout Munchies).
  - Fictional diaper brands (e.g., CloudyBottoms Ultra Dry, SnuggleBum Eco Diapers, CuddlePaws Comfort Fit).
  - Diaper changes, feeding, soothing, and milestone tracking.
- BitLife-like childhood and teenage years (Ages 1 through 17):
  - Yearly choices, stats (Health, Happiness, Smarts, Relationship with parents).
  - School, friendships, hobbies, teenage milestones.
- Adulthood & Spending time together (Ages 18 to 35):
  - College/career choices, romance, maintaining bond with parents.
  - At age 35: They have a child and bring you your grandbaby!
- Generational Rebirth:
  - You now take over and play as the grandbaby in BitLife/Babydow mode, beginning the cycle anew!
"""

import random
import sys
from typing import Dict, List, Optional, Tuple

FICTIONAL_BABY_FOODS = [
    {"brand": "TinyTummy Organics", "item": "Mashed Sweet Potato & Carrot Puree"},
    {"brand": "NutriTot Purees", "item": "Apple Banana Oatmeal Mash"},
    {"brand": "LittleSprout Munchies", "item": "Pea, Spinach & Pear Blend"},
    {"brand": "ChubbyCheeks Gourmet", "item": "Gentle Harvest Butternut Squash"},
]

FICTIONAL_DIAPERS = [
    {"brand": "CloudyBottoms Ultra Dry", "feature": "12-hour leak lock feather softness"},
    {"brand": "SnuggleBum Eco Diapers", "feature": "100% plant-based breathable bamboo"},
    {"brand": "CuddlePaws Comfort Fit", "feature": "Stretchy flex-waistband with wetness indicator"},
]


class Character:
    def __init__(self, name: str, generation: int = 1, parent_name: Optional[str] = None):
        self.name = name
        self.generation = generation
        self.parent_name = parent_name
        self.age_months = 0
        self.age_years = 0
        self.health = 100
        self.happiness = 100
        self.smarts = 50
        self.relationship_with_parent = 100
        self.hunger = 0  # 0 = full, 100 = starving
        self.hygiene = 100  # 100 = clean, 0 = messy
        self.milestones: List[str] = []
        self.career: Optional[str] = None
        self.child_name: Optional[str] = None

    @property
    def is_infant(self) -> bool:
        return self.age_years == 0

    def feed(self, food_type: str, brand_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Feed the infant/child.
        Rules:
        - Months 0 to 8 (< 9 months): Only breast milk is allowed. Solid food is rejected.
        - Month 9 and onward: Real baby food can be eaten.
        """
        if self.age_months < 9:
            if food_type.lower() != "breast milk":
                msg = (
                    f"⚠️ {self.name} is only {self.age_months} months old! "
                    f"Babies under 9 months need breast milk; "
                    f"{food_type} ({brand_name or 'solid food'}) cannot be digested yet."
                )
                return False, msg
            self.hunger = max(0, self.hunger - 40)
            self.happiness = min(100, self.happiness + 15)
            self.health = min(100, self.health + 5)
            return True, f"🍼 Fed {self.name} warm breast milk. {self.name} is happy and nourished!"
        else:
            if food_type.lower() == "breast milk":
                self.hunger = max(0, self.hunger - 25)
                return True, f"🍼 Fed {self.name} breast milk as a gentle supplement."
            # Solid baby food
            self.hunger = max(0, self.hunger - 50)
            self.happiness = min(100, self.happiness + 20)
            brand_info = f" [{brand_name}]" if brand_name else ""
            return True, f"🥣 Fed {self.name} delicious {food_type}{brand_info}! Yum!"

    def change_diaper(self, diaper_brand_index: int = 0) -> str:
        brand = FICTIONAL_DIAPERS[diaper_brand_index % len(FICTIONAL_DIAPERS)]
        self.hygiene = 100
        self.happiness = min(100, self.happiness + 10)
        return (
            f"🧷 Changed {self.name}'s diaper using '{brand['brand']}' "
            f"({brand['feature']}). Clean and cozy!"
        )

    def advance_month(self) -> List[str]:
        """Advances 1 month during infancy (0 to 12 months)."""
        logs = []
        self.age_months += 1
        self.hunger = min(100, self.hunger + 30)
        self.hygiene = max(0, self.hygiene - 30)

        # Milestone triggers
        if self.age_months == 3 and "First Smile" not in self.milestones:
            self.milestones.append("First Smile")
            logs.append(f"✨ Milestone: {self.name} flashed their very first bright smile at you!")
        elif self.age_months == 6 and "Sitting Up" not in self.milestones:
            self.milestones.append("Sitting Up")
            logs.append(f"✨ Milestone: {self.name} can now sit up unsupported and play with rattles!")
        elif self.age_months == 9 and "Starting Solid Food" not in self.milestones:
            self.milestones.append("Starting Solid Food")
            logs.append(
                f"🎉 Major Milestone: {self.name} has turned 9 months old! "
                f"They are now ready to transition from breast milk to solid baby foods!"
            )
        elif self.age_months == 12:
            self.age_years = 1
            if "First Birthday & Steps" not in self.milestones:
                self.milestones.append("First Birthday & Steps")
                logs.append(f"🎂 Milestone: {self.name} celebrated their 1st birthday and took their first wobbly steps!")
        return logs

    def advance_year(self) -> List[str]:
        """Advances 1 year (Ages 1 through 35+)."""
        self.age_years += 1
        self.age_months = self.age_years * 12
        logs = [f"📅 {self.name} has turned {self.age_years} years old."]
        return logs

    def gender_hint(self) -> str:
        return "female" if self.name in ["Luna", "Aria", "Maya", "Chloe"] else "male"


BITLIFE_YEARLY_EVENTS = {
    2: {
        "event": "You discovered colorful crayons and a pristine living room wall.",
        "options": [
            ("Create a magnificent scribbled masterpiece on the wall", {"happiness": 15, "smarts": 5, "relationship": -10}),
            ("Color politely in your coloring book", {"happiness": 5, "smarts": 10, "relationship": 15}),
        ],
    },
    5: {
        "event": "It's your first day of kindergarten! Another kid takes your favorite building blocks.",
        "options": [
            ("Share the blocks and build a giant tower together", {"happiness": 10, "smarts": 10, "relationship": 5}),
            ("Throw a dramatic tantrum and demand your blocks back", {"happiness": -5, "smarts": -5, "relationship": 0}),
        ],
    },
    10: {
        "event": "Your school is hosting a science fair and sports club registration.",
        "options": [
            ("Build a baking soda volcano for the science fair", {"happiness": 10, "smarts": 20, "relationship": 5}),
            ("Join the junior soccer team and practice kicks", {"happiness": 15, "health": 15, "relationship": 5}),
        ],
    },
    14: {
        "event": "High school drama! Someone is gossiping about your best friend in the hallway.",
        "options": [
            ("Stand up for your friend bravely and tell everyone to stop", {"happiness": 15, "smarts": 10, "relationship": 10}),
            ("Stay out of it and focus on studying in the library", {"happiness": 0, "smarts": 15, "relationship": 0}),
        ],
    },
    17: {
        "event": "High school graduation is here! You need to decide on your immediate future path.",
        "options": [
            ("Study hard for university to become a Pediatrician", {"smarts": 25, "happiness": 10, "career": "Pediatrician"}),
            ("Pursue your passion in culinary arts to become a Gourmet Chef", {"happiness": 20, "career": "Gourmet Chef"}),
            ("Enter software development and design life simulation games", {"smarts": 20, "happiness": 15, "career": "Game Developer"}),
        ],
    },
    22: {
        "event": "You graduated and started your career! Your parent calls asking how work is going.",
        "options": [
            ("Spend Sunday visiting parent and having home-cooked dinner", {"happiness": 20, "relationship": 25}),
            ("Send a quick text message because you're busy working late", {"happiness": -5, "relationship": -5}),
        ],
    },
    28: {
        "event": "You find a wonderful life partner who loves family gatherings and road trips.",
        "options": [
            ("Introduce your partner to your parent during family Thanksgiving", {"happiness": 25, "relationship": 20}),
            ("Elope on a tropical island getaway", {"happiness": 20, "relationship": -5}),
        ],
    },
    32: {
        "event": "You and your partner start discussing having children of your own.",
        "options": [
            ("Prepare your nursery and ask your parent for baby-rearing tips", {"happiness": 20, "relationship": 20}),
            ("Read stacks of parenting books and plan a babymoon trip", {"happiness": 15, "smarts": 10}),
        ],
    },
}


class SimulationDemo:
    def __init__(self, baby_name: str = "Luna", auto_play: bool = True):
        self.current_character = Character(name=baby_name, generation=1, parent_name="You")
        self.auto_play = auto_play
        self.logs: List[str] = []

    def log(self, message: str) -> None:
        self.logs.append(message)
        print(message)

    def run_infancy_stage(self, character: Character) -> None:
        """Babydow-like infancy: months 0 through 12."""
        self.log("\n" + "=" * 65)
        self.log(f"🍼 [BABYDOW MODE] Generation {character.generation}: Caring for Baby {character.name}")
        self.log("=" * 65)
        self.log(f"Baby {character.name} is born! Welcome to the world.")

        for month in range(12):
            self.log(f"\n--- Month {character.age_months} ---")

            # Try invalid food before 9 months to demonstrate rule enforcement
            if character.age_months == 4:
                food = FICTIONAL_BABY_FOODS[0]
                ok, reason = character.feed(food["item"], food["brand"])
                self.log(f"Attempting to feed solid food too early: {reason}")

            # Proper feeding according to age
            if character.age_months < 9:
                ok, res = character.feed("breast milk")
                self.log(res)
            else:
                food_idx = (character.age_months - 9) % len(FICTIONAL_BABY_FOODS)
                food = FICTIONAL_BABY_FOODS[food_idx]
                ok, res = character.feed(food["item"], food["brand"])
                self.log(res)

            # Diaper change
            diaper_log = character.change_diaper(month)
            self.log(diaper_log)

            # Advance month
            milestones = character.advance_month()
            for m in milestones:
                self.log(m)

        self.log(f"\n🎉 {character.name} has completed infancy and is now a happy 1-year-old toddler!")

    def run_childhood_and_teen_stage(self, character: Character) -> None:
        """BitLife-like childhood & adolescence: ages 1 through 17."""
        self.log("\n" + "=" * 65)
        self.log(f"🎒 [BITLIFE MODE] Growing Up: Ages 1 to 17 - {character.name}")
        self.log("=" * 65)

        for age in range(1, 18):
            character.advance_year()
            current_age = character.age_years

            if current_age in BITLIFE_YEARLY_EVENTS:
                evt = BITLIFE_YEARLY_EVENTS[current_age]
                self.log(f"\n[Age {current_age} Event]: {evt['event']}")
                chosen_option, impacts = evt["options"][0]  # Pick top choice for demo
                self.log(f"  👉 Choice: {chosen_option}")
                for stat, val in impacts.items():
                    if stat == "career":
                        character.career = val
                        self.log(f"     Career Path chosen: {val}")
                    elif hasattr(character, stat):
                        cur_val = getattr(character, stat)
                        setattr(character, stat, max(0, min(100, cur_val + val)))

            if current_age % 4 == 0 or current_age == 17:
                self.log(
                    f"   Stats at Age {current_age} -> Health: {character.health}%, "
                    f"Happiness: {character.happiness}%, Smarts: {character.smarts}%, "
                    f"Bond with Parent: {character.relationship_with_parent}%"
                )

        self.log(f"\n🎓 {character.name} graduated high school at 17 and enters young adulthood!")

    def run_adulthood_stage(self, character: Character) -> Character:
        """Ages 18 to 35: Spending time together, career, and bringing grandbaby at 35."""
        self.log("\n" + "=" * 65)
        self.log(f"💼 [ADULTHOOD & FAMILY TIME] Ages 18 to 35 - {character.name}")
        self.log("=" * 65)

        for age in range(18, 36):
            character.advance_year()
            current_age = character.age_years

            if current_age in BITLIFE_YEARLY_EVENTS:
                evt = BITLIFE_YEARLY_EVENTS[current_age]
                self.log(f"\n[Age {current_age} Life Milestone]: {evt['event']}")
                chosen_option, impacts = evt["options"][0]
                self.log(f"  👉 Choice: {chosen_option}")
                for stat, val in impacts.items():
                    if hasattr(character, stat):
                        cur_val = getattr(character, stat)
                        setattr(character, stat, max(0, min(100, cur_val + val)))
            elif current_age in (20, 25, 30):
                self.log(f"Age {current_age}: {character.name} spends quality weekend time with family, sharing memories and laughter.")
                character.relationship_with_parent = min(100, character.relationship_with_parent + 10)

            if current_age == 35:
                grandbaby_name = "Aria" if character.gender_hint() == "female" else "Leo"
                character.child_name = grandbaby_name
                self.log("\n" + "*" * 65)
                self.log(f"👶 [GRANDBABY ARRIVAL] At age 35, {character.name} has a baby!")
                self.log(
                    f"{character.name} walks through the front door and proudly brings you your grandbaby, {grandbaby_name}!"
                )
                self.log(f"\"Mom / Dad, meet your grandbaby {grandbaby_name}! We couldn't have done this without you.\"")
                self.log("*" * 65)

                # Create next generation character
                grandbaby = Character(name=grandbaby_name, generation=character.generation + 1, parent_name=character.name)
                return grandbaby

        return character

    def run_full_generation_loop(self) -> None:
        """Executes full simulation flow including generational reincarnation."""
        gen1 = self.current_character
        self.run_infancy_stage(gen1)
        self.run_childhood_and_teen_stage(gen1)
        grandbaby = self.run_adulthood_stage(gen1)

        self.log("\n" + "#" * 65)
        self.log("🔄 [GENERATIONAL REBIRTH - BITLIFE / BABYDOW MODE]")
        self.log(f"The torch has been passed! You now step into the shoes of the grandbaby, {grandbaby.name} (Generation {grandbaby.generation})!")
        self.log(f"Your parent is now {grandbaby.parent_name}. The cycle begins anew!")
        self.log("#" * 65)

        # Demonstrate playing again as the grandbaby in Babydow mode
        self.current_character = grandbaby
        self.run_infancy_stage(grandbaby)
        self.log("\n✨ Demo completed successfully! Generational cycle continues forever.")


def main():
    print("Starting Generational Life & Baby Care Simulation Demo...")
    demo = SimulationDemo(baby_name="Luna", auto_play=True)
    demo.run_full_generation_loop()


if __name__ == "__main__":
    main()
