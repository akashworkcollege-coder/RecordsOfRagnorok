#!/usr/bin/env python3
"""
================================================================================
  RECORD OF RAGNAROK: RAGNAROK'S CALL — CLEAN EDITION v2.0
  25 FIGHTERS (13 Gods + 12 Humans) • 310 TOTAL ABILITIES
================================================================================
  GAME MODES: Tournament, Survival, Boss Rush, Gauntlet, Chaos, Training
  FEATURES: Adam's Divine Replication, Völundr System, Full Status Effects
================================================================================
CLEAN EDITION v2.0 IMPROVEMENTS:
  ✅ Passive abilities removed from action menu (no more wasted turns)
  ✅ Ichor-only abilities properly gated (Hades)
  ✅ Exhausted status applies to ALL characters (not just Beelzebub)
  ✅ Susanoo musouken_active flag properly resets after status expires
  ✅ Ultimate/Divine Technique now shows confirm dialog before use
  ✅ Ability descriptions use fast print (no more 10-second waits)
  ✅ Turn number displayed prominently in battle header
  ✅ Dead party section shows proper fallback message
  ✅ Banner corrected to 25 fighters (13 gods + 12 humans)
  ✅ Enhanced main menu with cleaner layout

ALL CRITICAL BUGS FIXED:
1. ✅ Damage abilities with effect keys now properly apply effects
2. ✅ Adam's Father's Love death trigger now fires in ALL cases
3. ✅ Beelzebub's Lilith Mark now properly triggers when killed
4. ✅ Zeus's Adamas Form timer now decrements correctly
5. ✅ Heracles' Healing Labor no longer applies tattoo damage
6. ✅ Loki's Clones now fully functional in combat
7. ✅ battle() no longer stores state as instance variables
8. ✅ Völundr now automatically activates when selecting characters
9. ✅ Valkyries only marked as fallen in Tournament mode
10. ✅ Jack the Ripper - Fixed duplicate class and ability initialization
11. ✅ Beelzebub - Fixed can_use_ability() signature mismatch
12. ✅ Hades - Fixed ichor-only ability checking
13. ✅ Poseidon - Fixed pride mechanic messaging
14. ✅ Odin's Life Theft - Fixed damage application and messaging
15. ✅ Loki's Clone Attack - Fixed damage calculation
16. ✅ Shiva's Arm Loss - Added tournament mode tracking
17. ✅ Zeus's Adamas Timer - Synchronized with status effect
18. ✅ Simo Häyhä - Added organ count display
19. ✅ Tesla - Added teleport charge display
20. ✅ Soji Okita - Increased illness damage
21. ✅ Buddha - Reworked future sight as prediction, not evasion
22. ✅ Heracles - Tattoo progress now persistent
23. ✅ Apollo - Expectation bonus now saves
24. ✅ Qin Shi Huang - Added counter ready indicator
25. ✅ Leonidas - Increased form switching cost
26. ✅ Hajun - Implemented possession mechanic
27. ✅ Zerofuku - Added misery level display
28. ✅ Thor - Teleport uses now persistent in tournament
29. ✅ Kintoki - Added rune cooldown
30. ✅ Jack - Real-time weapon status updates
31. ✅ Poseidon - Water level regenerates
32. ✅ Raiden - Added recoil damage to Muscle Release

ADDITIONAL FIXES:
33. ✅ Battle state - display_health_bars() and enemy_turn() now accept parameters
34. ✅ Adam - Death trigger now fires immediately after any damage
35. ✅ Beelzebub - Exhaustion no longer soft-locks (shows menu with skip only)
36. ✅ Hajun - Possession now triggers for utility-type ability
37. ✅ Poseidon - Energy now properly deducted on pride fail
38. ✅ Kintoki - Rune check now happens BEFORE damage
39. ✅ Shiva - karma_only abilities now properly restricted in menu
40. ✅ Odin - life_theft_active now resets when timer expires
41. ✅ Soji - Illness timer now properly synced with status effect
42. ✅ Susano'o - Removed uncanonical self-damage from Musouken
43. ✅ Loki - Clones can now be targeted by enemies (40% chance)
44. ✅ Enemy AI - Now follows patterns sequentially, not randomly
"""

import random
import time
import sys
import json
import os
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# ============================================================================
# CONFIGURATION
# ============================================================================

TEXT_SPEED = 0.02
BATTLE_START_DELAY = 1.0
TURN_DELAY = 0.5
ACTION_DELAY = 0.3
VICTORY_DELAY = 1.5
SAVE_FILE = "ragnarok_save.json"


def slow_print(text, delay=None):
    """Print text character by character for dramatic effect"""
    if delay is None:
        delay = TEXT_SPEED
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')



def print_ability_result(result):
    """Print ability result. Each sentence on its own line.
    [TRANSFORMATION: ...] is always split onto its own indented line.
    The original text content is NEVER changed — only the display layout."""
    if not result:
        return
    if '[TRANSFORMATION:' in result:
        parts = result.split('[TRANSFORMATION:', 1)
        main_text = parts[0].rstrip()
        trans_text = '[TRANSFORMATION:' + parts[1]
        # Print each sentence of the main text on its own line
        for line in main_text.split('\n'):
            s = line.strip()
            if s:
                print(f"  {s}")
        # Print transformation on its own indented line
        print(f"     ✦ {trans_text}")
    else:
        # Print each sentence on its own line
        for line in result.split('\n'):
            s = line.strip()
            if s:
                print(f"  {s}")


def print_desc(text, indent="      ", max_words=20):
    """Print a description as a paragraph, max ~20 words per line."""
    if not text:
        return
    words = text.split()
    line = []
    first_line = True
    for word in words:
        line.append(word)
        if len(line) >= max_words:
            prefix = "      " if not first_line else ""
            print(prefix + " ".join(line))
            line = []
            first_line = False
    if line:
        prefix = "      " if not first_line else ""
        print(prefix + " ".join(line))


def wrap_text(text, width=80):
    """Wrap text to specified width for better readability"""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(' '.join(current_line))

    return '\n      '.join(lines)


# ============================================================================
# VISUAL INDICATOR SYSTEM
# ============================================================================

class StatusEffect(Enum):
    """Visual indicators for status effects"""
    STUN = ("⚡", "STUNNED", "bright_yellow")
    BIND = ("🔗", "BOUND", "light_cyan")
    DEFEND = ("🛡️", "DEFENDING", "light_blue")
    DIVINE = ("✨", "DIVINE", "light_magenta")
    VOLUNDR = ("⚔️", "VÖLUNDR", "light_green")
    BERSERK = ("🔥", "BERSERK", "light_red")
    REGEN = ("💚", "REGEN", "light_green")
    POISON = ("💀", "POISONED", "dark_green")
    BLEED = ("🩸", "BLEEDING", "light_red")
    FROST = ("❄️", "FROST", "light_cyan")
    BURN = ("🔥", "BURNING", "light_red")
    SHIELD = ("🔮", "SHIELDED", "light_blue")
    CHARGE = ("⚡", "CHARGING", "light_yellow")
    EMPOWER = ("💪", "EMPOWERED", "light_magenta")
    WEAKEN = ("📉", "WEAKENED", "dark_gray")
    FEAR = ("😨", "FEAR", "dark_purple")
    BLIND = ("👁️", "BLIND", "dark_gray")
    HASTE = ("⏩", "HASTED", "light_cyan")
    SLOW = ("⏪", "SLOWED", "dark_blue")
    COPY = ("👁️", "COPY", "light_yellow")
    REALM_SPEED = ("🔵", "SPEED", "light_blue")
    REALM_STRENGTH = ("🔴", "STRENGTH", "light_red")
    REALM_ENDURANCE = ("🟢", "ENDURANCE", "light_green")
    REALM_TECHNIQUE = ("🩷", "TECHNIQUE", "light_magenta")
    REALM_WILL = ("🟣", "WILL", "light_purple")
    ICHOR = ("💧", "ICHOR", "dark_red")
    CERBERUS = ("🐕", "CERBERUS", "dark_red")
    ADAMAS = ("👑", "ADAMAS", "light_yellow")
    TANDAVA = ("💃", "TANDAVA", "light_red")
    KARMA = ("💓", "KARMA", "dark_red")
    FUTURE_SIGHT = ("🔮", "FUTURE", "light_cyan")
    GEMATRIA = ("🔬", "GEMATRIA", "light_blue")
    TESLA_WARP = ("⚡", "WARP", "light_blue")
    CLONE = ("👥", "CLONE", "dark_gray")
    PERFECT_CLONE = ("👤", "PERFECT", "light_magenta")
    TREASURE = ("💎", "TREASURE", "light_yellow")
    RUNE = ("✨", "RUNE", "light_gold")
    ORGAN_SAC = ("💥", "SACRIFICE", "dark_red")
    MUSOUKEN = ("⚔️", "MUSOUKEN", "invisible")
    STAR_EYES = ("👁️", "STAR EYES", "light_cyan")
    PHOENIX = ("🔥", "PHOENIX", "light_red")
    DEMON_CHILD = ("👹", "DEMON", "dark_red")
    DEMON_RELEASE = ("👹", "RELEASE", "blood_red")
    YATAGARASU = ("🐦‍⬛", "YATAGARASU", "dark_gray")
    ANDVARANAUT = ("💍", "ANDVARANAUT", "light_green")
    EXPECTATION = ("☀️", "EXPECTED", "light_yellow")
    THREAD_SHIELD = ("🛡️", "THREAD", "light_yellow")
    LILITH_MARK = ("🌹", "LILITH", "dark_purple")
    NECK_FIX = ("🩸", "NECK FIX", "light_red")
    MUSCLE_FORM = ("💪", "MUSCLE", "light_red")
    JARNGREIPR = ("🧤", "GLOVES", "dark_gray")
    MJOLNIR_AWAKENED = ("⚡", "AWAKENED", "light_blue")
    TELEPORT = ("🌀", "TELEPORT", "light_cyan")
    FOOTWORK = ("👣", "FOOTWORK", "light_cyan")
    WATER_BARRIER = ("🌊", "WATER", "light_blue")
    HYDROKINESIS = ("💧", "HYDRO", "light_blue")
    TATTOO = ("🦁", "TATTOO", "dark_red")
    ARM_LOSS = ("🦾", "ARM LOST", "dark_gray")
    MISERY = ("😢", "MISERY", "dark_gray")
    CLEAVER_HEADS = ("🎋", "HEADS", "dark_green")
    DESMOS = ("⚔️", "DESMOS", "dark_red")
    PALMYRA = ("🦟", "PALMYRA", "dark_green")
    CHAOS = ("🌀", "CHAOS", "dark_purple")
    EXHAUSTED = ("😫", "EXHAUSTED", "dark_gray")
    DARK_SOUL = ("👹", "DARK SOUL", "dark_purple")
    CLONE_LIMIT = ("∞", "UNLIMITED", "light_green")
    SHARED_VISION = ("👁️", "ALL-SEEING", "light_cyan")
    BATTLE_FORM = ("👤", "BATTLE", "light_white")
    LIFE_DRAIN = ("🌿", "DRAIN", "dark_green")
    MATTER_MANIP = ("✨", "MATTER", "light_cyan")
    GRAM = ("🗡️", "GRAM", "light_cyan")
    DRAUPNIR = ("💍", "DRAUPNIR", "light_yellow")
    EGIL = ("⛑️", "EGIL", "dark_gray")
    BRISINGAMEN = ("📿", "BRISINGAMEN", "light_blue")
    SKY_EATER = ("🏹", "SKY EATER", "light_blue")
    SCANNING = ("🔍", "SCANNING", "light_cyan")
    DUAL_WIELD = ("⚔️⚔️", "DUAL", "light_cyan")
    MANJU_MUSO = ("👁️", "MANJU", "light_cyan")
    SOUL_EYE = ("👁️", "SOUL EYE", "light_purple")
    ENVIRONMENT = ("🏙️", "ENV WEAPON", "dark_green")
    ARM_EXTENSION = ("🦾", "EXTENDED", "dark_gray")
    ORGAN_SHIFT = ("🫀", "ORGAN SHIFT", "light_red")
    MUSCLE_RELEASE = ("💪", "100%", "light_red")
    NIRVANA_SWORD = ("🗡️", "NIRVANA", "light_white")
    BLINDFOLD_OFF = ("👁️", "STAR EYES", "light_cyan")
    CHI_FLOW = ("✨", "CHI FLOW", "light_cyan")
    CHI_CRUX = ("⭐", "CRUX", "light_yellow")
    ZERO_MAX = ("0️⃣", "ZERO MAX", "light_blue")
    TESLA_STEP = ("👣", "TESLA STEP", "light_blue")
    GEMATRIA_ZONE = ("🔬", "ZONE", "light_blue")
    SHIELD_FORM = ("🛡️", "SHIELD", "dark_gray")
    SAW_FORM = ("⚙️", "SAW", "light_red")
    HAMMER_FORM = ("🔨", "HAMMER", "light_red")
    PHALANX = ("🛡️", "PHALANX", "light_blue")
    ILLNESS = ("🤒", "ILL", "dark_green")
    DEMON_AWAKE = ("👹", "AWAKE", "dark_red")
    WHITE_DEATH = ("❄️", "WHITE DEATH", "light_cyan")
    CAMOUFLAGE = ("🌨️", "CAMO", "light_cyan")
    GOLDEN_AGE = ("✨", "GOLDEN", "light_yellow")
    RUNE_OF_EIRIN = ("✨", "EIRIN", "light_gold")
    GOLDEN_LIGHTNING = ("⚡", "GOLDEN", "light_yellow")
    FURIOUS_FLASH = ("⚡", "FLASH", "light_yellow")
    GRAPPLE = ("🦯", "GRAPPLING", "light_cyan")
    EVASION = ("💨", "EVASION", "light_cyan")
    COUNTER_READY = ("🔄", "COUNTER", "light_blue")
    POSSESSED = ("👹", "POSSESSED", "dark_purple")
    RUNE_COOLDOWN = ("⏳", "RUNE CD", "dark_gray")
    ORGANS_LEFT = ("🫀", "ORGANS", "light_red")
    WATER_LEVEL = ("💧", "WATER", "light_blue")
    TELEPORT_CHARGES = ("⚡", "TELEPORT", "light_blue")
    MISERY_LEVEL = ("😢", "MISERY", "dark_gray")


@dataclass
class StatusEffectInstance:
    """Instance of a status effect on a character"""
    effect_type: StatusEffect
    duration: int
    value: float = 1.0
    stacks: int = 1
    source: str = ""


class VisualIndicator:
    """Manages visual indicators for all characters"""

    @staticmethod
    def get_status_icons(character) -> List[str]:
        """Get all status effect icons for a character - NO DUPLICATES"""
        icons = []
        seen_base_icons = set()

        # Get status effects from status_effects list
        if hasattr(character, 'status_effects'):
            for effect in character.status_effects:
                icon, symbol, _ = effect.effect_type.value
                # Use icon + stack count as unique key
                if effect.stacks > 1:
                    icon_key = f"{icon}{effect.stacks}"
                else:
                    icon_key = icon

                if icon_key not in seen_base_icons:
                    seen_base_icons.add(icon_key)
                    if effect.stacks > 1:
                        icons.append(f"{icon}{effect.stacks}")
                    else:
                        icons.append(icon)

        # Add Völundr indicator if active
        if hasattr(character, 'volund_active') and character.volund_active:
            icon = StatusEffect.VOLUNDR.value[0]
            if icon not in seen_base_icons:
                icons.append(icon)
                seen_base_icons.add(icon)

        # Add Divine mode indicator if active
        if hasattr(character, 'divine_mode') and character.divine_mode:
            icon = StatusEffect.DIVINE.value[0]
            if icon not in seen_base_icons:
                icons.append(icon)
                seen_base_icons.add(icon)

        # Add Realm indicator if active
        if hasattr(character, 'active_realm') and character.active_realm != Realm.NONE:
            realm_icons = {
                Realm.GODLY_SPEED: StatusEffect.REALM_SPEED.value[0],
                Realm.GODLY_STRENGTH: StatusEffect.REALM_STRENGTH.value[0],
                Realm.GODLY_ENDURANCE: StatusEffect.REALM_ENDURANCE.value[0],
                Realm.GODLY_TECHNIQUE: StatusEffect.REALM_TECHNIQUE.value[0],
                Realm.GODLY_WILL: StatusEffect.REALM_WILL.value[0]
            }
            icon = realm_icons.get(character.active_realm, '')
            if icon and icon not in seen_base_icons:
                icons.append(icon)
                seen_base_icons.add(icon)

        # Add Future Sight indicator if active
        if hasattr(character, 'future_sight_active') and character.future_sight_active:
            icon = StatusEffect.FUTURE_SIGHT.value[0]
            if icon not in seen_base_icons:
                icons.append(icon)
                seen_base_icons.add(icon)

        # Add Thread Shield indicator if active
        if hasattr(character, 'thread_shield_active') and character.thread_shield_active:
            icon = StatusEffect.THREAD_SHIELD.value[0]
            if icon not in seen_base_icons:
                icons.append(icon)
                seen_base_icons.add(icon)

        # Add Chi Flow indicator if active
        if hasattr(character, 'chi_flow') and character.chi_flow:
            icon = StatusEffect.CHI_FLOW.value[0]
            if icon not in seen_base_icons:
                icons.append(icon)
                seen_base_icons.add(icon)

        # Add Counter Ready indicator for Qin
        if hasattr(character, 'counter_ready') and character.counter_ready:
            icon = StatusEffect.COUNTER_READY.value[0]
            if icon not in seen_base_icons:
                icons.append(icon)
                seen_base_icons.add(icon)

        # Add Possessed indicator for Hajun's victims
        if hasattr(character, 'possessed') and character.possessed:
            icon = StatusEffect.POSSESSED.value[0]
            if icon not in seen_base_icons:
                icons.append(icon)
                seen_base_icons.add(icon)

        # Add custom indicators for special resources
        if character.name == "Simo Häyhä" and hasattr(character, 'organs_used'):
            organs_left = len(character.organs) - len(character.organs_used)
            if organs_left > 0:
                icons.append(f"🫀{organs_left}")

        if character.name == "Poseidon" and hasattr(character, 'water_level'):
            water_display = character.water_level // 10
            icons.append(f"💧{water_display}")

        if character.name == "Nikola Tesla" and hasattr(character, 'teleport_charges'):
            if character.teleport_charges > 0:
                icons.append(f"⚡{character.teleport_charges}")

        if character.name == "Zerofuku" and hasattr(character, 'misery_level'):
            if character.misery_level > 0:
                icons.append(f"😢{character.misery_level}")

        if character.name == "Sakata Kintoki" and hasattr(character, 'rune_cooldown'):
            if character.rune_cooldown > 0:
                icons.append(StatusEffect.RUNE_COOLDOWN.value[0])

        icons = [i for i in icons if i]
        return icons

    @staticmethod
    def format_status_bar(character, width=40):
        """Format a status bar with indicators"""
        if not character.is_alive():
            return "💀" * width

        filled = int(width * character.hp / character.max_hp)
        bar = "█" * filled + "░" * (width - filled)

        icons = VisualIndicator.get_status_icons(character)
        icon_str = " ".join(icons) if icons else ""

        return f"{bar} {character.hp:3}/{character.max_hp:3} {icon_str}"


# ============================================================================
# SAVE/LOAD SYSTEM
# ============================================================================

class SaveSystem:
    @staticmethod
    def save_game(game_state):
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False

    @staticmethod
    def load_game():
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"❌ Load failed: {e}")
            return None

    @staticmethod
    def delete_save():
        try:
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
                return True
            return False
        except:
            return False


# ============================================================================
# VALKYRIE ENUM - FIXED with get_index_by_name method
# ============================================================================

class Valkyrie(Enum):
    BRUNHILDE = (0, "👑 Brunhilde", "The Eldest - Tournament Organizer", "organizer", False)
    HRIST = (1, "🌪️ Hrist", "The Quaking (Dual Personality) - Kojiro's Partner", "available", True)
    THRUD = (2, "💪 Thrud", "The Strong One - Raiden's Partner (Fell in love)", "available", True)
    RANDGRIZ = (3, "🛡️ Randgriz", "Shield Breaker - Lü Bu's Partner", "available", True)
    GEIRÖLUL = (4, "⚔️ Geirölul", "The One Charging Forth - Leonidas' Partner", "available", True)
    SKALMÖLD = (5, "⚡ Skalmöld", "Sword Time - Soji Okita's Partner", "available", True)
    REGINLEIF = (6, "✨ Reginleif", "Daughter of the Gods - Adam's Partner", "available", True)
    RÁÐGRÍÐR = (7, "🎯 Ráðgríðr", "Plan Breaker - Simo Häyhä's Partner", "available", True)
    GÖNDUL = (8, "🔮 Göndul", "The Magic Wielder - Tesla's Partner", "available", True)
    ALVITR = (9, "🛡️ Alvitr", "Host-Guard - Qin Shi Huang's Partner", "available", True)
    HLÖKK = (10, "🔥 Hlökk", "The Battle Cry - Jack's Partner (Forced Völundr)", "available", True)
    SKEGGJÖLD = (11, "🪓 Skeggjöld", "Axe Age - Kintoki's Partner (Fuses with axe)", "available", True)
    GÖLL = (12, "💫 Göll", "The Youngest - Brunhilde's Assistant", "assistant", False)

    def __init__(self, index, icon_name, desc, default_status, can_fight):
        self.index = index
        self.icon_name = icon_name
        self.desc = desc
        self.default_status = default_status
        self.can_fight = can_fight

    @classmethod
    def get_by_index(cls, index):
        """Get Valkyrie by index number"""
        for valkyrie in cls:
            if valkyrie.index == index:
                return valkyrie
        return None

    @classmethod
    def get_by_name(cls, name):
        """Get Valkyrie by enum name (e.g., 'HRIST')"""
        for valkyrie in cls:
            if valkyrie.name == name:
                return valkyrie
        return None

    @classmethod
    def get_by_display_name(cls, display_name):
        """Get Valkyrie by display name (e.g., 'Hrist' or 'Hlökk')"""
        for valkyrie in cls:
            if display_name in valkyrie.icon_name:
                return valkyrie
        for valkyrie in cls:
            parts = valkyrie.icon_name.split(' ')
            if len(parts) > 1 and parts[1] == display_name:
                return valkyrie
        return None

    @classmethod
    def get_index_by_name(cls, name):
        """Get index by Valkyrie name - FIXED: Added this missing method"""
        for valkyrie in cls:
            if valkyrie.name == name:
                return valkyrie.index
        return -1


# Quick lookup dictionaries
VALKYRIE_INDEX_MAP = {
    "Brunhilde": 0,
    "Hrist": 1,
    "Thrud": 2,
    "Randgriz": 3,
    "Geirölul": 4,
    "Skalmöld": 5,
    "Reginleif": 6,
    "Ráðgríðr": 7,
    "Göndul": 8,
    "Alvitr": 9,
    "Hlökk": 10,
    "Skeggjöld": 11,
    "Göll": 12
}

INDEX_VALKYRIE_MAP = {v: k for k, v in VALKYRIE_INDEX_MAP.items()}


# ============================================================================
# REALM SYSTEM
# ============================================================================

class Realm(Enum):
    NONE = "⚪ Normal State"
    GODLY_SPEED = "🔵 Godly Speed"
    GODLY_STRENGTH = "🔴 Godly Strength"
    GODLY_ENDURANCE = "🟢 Godly Endurance"
    GODLY_TECHNIQUE = "🩷 Godly Technique"
    GODLY_WILL = "🟣 Godly Will"


# ============================================================================
# BASE CHARACTER CLASS - FIXED with better type handling
# ============================================================================

class Character:
    def __init__(self, name, title, hp, energy, realm_list=None):
        self.name = name
        self.title = title
        self.hp = hp
        self.max_hp = hp
        self.energy = energy
        self.max_energy = energy
        self.abilities = {}
        self.divine_technique = None
        self.valkyrie = None
        self.valkyrie_index = -1
        self.volund_active = False
        self.volund_weapon = ""
        self.realms = realm_list if realm_list else []
        self.active_realm = Realm.NONE
        self.realm_timer = 0
        self.affiliation = ""
        self.round = 0

        self.status_effects: List[StatusEffectInstance] = []
        self.defending = False
        self.stunned = False
        self.bound = False
        self.exhausted = False
        self.divine_mode = False
        self.divine_timer = 0
        self.soul_dark = False
        self.possessed = False  # For Hajun's possession

        # FIXED: Added missing visual indicator flags
        self.future_sight_active = False
        self.thread_shield_active = False
        self.chi_flow = False

    def add_status_effect(self, effect_type: StatusEffect, duration: int, value: float = 1.0, stacks: int = 1,
                          source: str = ""):
        for effect in self.status_effects:
            if effect.effect_type == effect_type:
                effect.duration = max(effect.duration, duration)
                effect.stacks += stacks
                effect.value = max(effect.value, value)
                return f"🔄 {effect_type.value[1]} intensified! (Now {effect.stacks} stacks)"

        self.status_effects.append(StatusEffectInstance(
            effect_type=effect_type,
            duration=duration,
            value=value,
            stacks=stacks,
            source=source
        ))
        icon, name, _ = effect_type.value
        return f"{icon} {name} applied for {duration} turns!"

    def remove_status_effect(self, effect_type: StatusEffect):
        self.status_effects = [e for e in self.status_effects if e.effect_type != effect_type]

    def has_status_effect(self, effect_type: StatusEffect) -> bool:
        return any(e.effect_type == effect_type for e in self.status_effects)

    def get_status_effect_value(self, effect_type: StatusEffect) -> float:
        for effect in self.status_effects:
            if effect.effect_type == effect_type:
                return effect.value
        return 1.0

    def get_status_effect_stacks(self, effect_type: StatusEffect) -> int:
        for effect in self.status_effects:
            if effect.effect_type == effect_type:
                return effect.stacks
        return 0

    def update_status_effects(self):
        # ── DoT / HoT processing ─────────────────────────────────────────
        # POISON: value = damage per tick (default 30)
        if self.has_status_effect(StatusEffect.POISON):
            dmg = int(self.get_status_effect_value(StatusEffect.POISON))
            if dmg <= 0:
                dmg = 30
            self.take_damage(dmg, ignore_defense=True)
            print(f"  💀 [POISON] {self.name} takes {dmg} poison damage!")

        # BURN: value = damage per tick (default 40)
        if self.has_status_effect(StatusEffect.BURN):
            dmg = int(self.get_status_effect_value(StatusEffect.BURN))
            if dmg <= 0:
                dmg = 40
            self.take_damage(dmg, ignore_defense=True)
            print(f"  🔥 [BURN] {self.name} takes {dmg} burn damage!")

        # BLEED: value = damage per tick (default 25)
        if self.has_status_effect(StatusEffect.BLEED):
            dmg = int(self.get_status_effect_value(StatusEffect.BLEED))
            if dmg <= 0:
                dmg = 25
            self.take_damage(dmg, ignore_defense=True)
            print(f"  🩸 [BLEED] {self.name} takes {dmg} bleed damage!")

        # REGEN: value = HP restored per tick (default 50)
        if self.has_status_effect(StatusEffect.REGEN):
            heal = int(self.get_status_effect_value(StatusEffect.REGEN))
            if heal <= 0:
                heal = 50
            self.hp = min(self.max_hp, self.hp + heal)
            print(f"  💚 [REGEN] {self.name} recovers {heal} HP!")

        # ── Duration tick & expiry ────────────────────────────────────────
        expired = []
        for effect in self.status_effects:
            effect.duration -= 1
            if effect.duration <= 0:
                expired.append(effect)

        for effect in expired:
            self.status_effects.remove(effect)
            icon, name, _ = effect.effect_type.value
            print(f"  ⏳ {icon} {name} faded.")

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg, ignore_defense=False):
        """FIXED: Returns damage dealt, properly handles ignore_defense and triggers death effects"""
        original_dmg = dmg

        # Check for possession (Hajun's victims can't control themselves)
        if self.possessed:
            print(f"  👹 {self.name} is possessed and cannot defend properly!")
            # Still take damage but no evasion/defense

        # Check for evasion from status effects
        elif self.has_status_effect(StatusEffect.EVASION):
            evade_chance = self.get_status_effect_value(StatusEffect.EVASION)
            if random.random() < evade_chance:
                print(f"  💨 {self.name} evades the attack!")
                return 0

        # Check for future sight prediction (not evasion)
        if self.has_status_effect(StatusEffect.FUTURE_SIGHT) and not self.possessed:
            # Future sight allows predicting and partially dodging
            if random.random() < 0.3:  # 30% chance to predict and reduce damage
                dmg = int(dmg * 0.5)
                print(f"  🔮 {self.name} predicts the attack and reduces damage by 50%!")

        # Apply defensive status effects
        if self.defending and not ignore_defense and not self.possessed:
            dmg = int(dmg * 0.5)
            print(f"  🛡️ {self.name} blocks half the damage!")

        if self.active_realm == Realm.GODLY_ENDURANCE and not self.possessed:
            dmg = int(dmg * 0.5)
            print(f"  🟢 {self.name}'s Endurance Realm reduces damage!")

        if self.has_status_effect(StatusEffect.SHIELD) and not self.possessed:
            reduction = self.get_status_effect_value(StatusEffect.SHIELD)
            dmg = int(dmg * reduction)
            print(f"  🔮 Shield reduces damage by {int((1 - reduction) * 100)}%!")

        # Apply damage amplification from status effects
        if self.has_status_effect(StatusEffect.BERSERK):
            dmg = int(dmg * 1.5)
            print(f"  🔥 Berserk amplifies damage by 50%!")

        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

        # FIXED: Trigger death effects immediately
        if self.hp <= 0:
            if hasattr(self, 'apply_effect') and hasattr(self, 'death_activated'):
                if not self.death_activated and self.name == "Adam":
                    result = self.apply_effect("fight_on_death")
                    if result:
                        print_ability_result(result)
            # Check for Beelzebub's Lilith mark
            if hasattr(self, 'check_lilith_mark'):
                result = self.check_lilith_mark()
                if result:
                    print_ability_result(result)

        if dmg > original_dmg * 1.5:
            print(f"  💥 CRITICAL HIT!")
        elif dmg < original_dmg * 0.5:
            print(f"  🛡️ Damage greatly reduced!")

        return dmg

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        print(f"  💚 {self.name} healed for {amount} HP!")

    def activate_realm(self, realm):
        if realm not in self.realms:
            return f"{self.name} cannot use {realm.value}!"
        self.active_realm = realm
        self.realm_timer = 5
        return f"\n✨ {realm.value} ACTIVATED!\n"

    def activate_volund(self, valkyrie):
        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index if valkyrie else -1
        self.volund_active = True
        self.add_status_effect(StatusEffect.VOLUNDR, 999)
        print(f"\n⚔️ VÖLUNDR: {self.name} x {valkyrie.icon_name}")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        return f"✅ Völundr successfully activated for {self.name}!"

    def reset_volund(self):
        """FIXED: Fully reset Völundr between battles.
        Restores base abilities from the snapshot taken at __init__ time."""
        self.volund_active = False
        self.volund_weapon = ""
        self.valkyrie_index = -1
        self.valkyrie = None
        self.divine_technique = None
        self.remove_status_effect(StatusEffect.VOLUNDR)
        # Restore base ability kit if a snapshot exists
        if hasattr(self, '_base_abilities'):
            self.abilities = dict(self._base_abilities)

    def get_damage_multiplier(self):
        """FIXED: Pure getter with no side effects"""
        mult = 1.0
        buffs = []

        if self.active_realm == Realm.GODLY_STRENGTH:
            mult *= 1.8
            buffs.append("🔴 STRENGTH")
        elif self.active_realm == Realm.GODLY_WILL and self.hp < self.max_hp * 0.3:
            mult *= 2.5
            buffs.append("🟣 WILL")

        if self.divine_mode:
            mult *= 2.0
            buffs.append("✨ DIVINE")

        if self.has_status_effect(StatusEffect.EMPOWER):
            empower_value = self.get_status_effect_value(StatusEffect.EMPOWER)
            mult *= empower_value
            buffs.append(f"💪 EMPOWERED x{empower_value}")

        if self.has_status_effect(StatusEffect.BERSERK):
            mult *= 1.5
            buffs.append("🔥 BERSERK")

        return mult, buffs

    def apply_effect(self, effect, target=None):
        """FIXED: Base apply_effect - to be overridden"""
        return ""

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": f"✨ {self.name}'s Ultimate Technique",
                "cost": 150,
                "dmg": (400, 600),
                "type": "damage",
                "desc": f"✨ The ultimate technique of {self.name}."
            }
        return self.divine_technique

    def to_dict(self):
        return {
            'name': self.name,
            'hp': self.hp,
            'energy': self.energy,
            'active_realm': self.active_realm.name if self.active_realm != Realm.NONE else None,
            'valkyrie': self.valkyrie.name if self.valkyrie else None,
            'valkyrie_index': self.valkyrie_index,
            'volund_active': self.volund_active,
            'volund_weapon': self.volund_weapon
        }

    def from_dict(self, data):
        self.hp = data.get('hp', self.max_hp)
        self.energy = data.get('energy', self.max_energy)

        realm_name = data.get('active_realm')
        if realm_name:
            for realm in Realm:
                if realm.name == realm_name:
                    self.active_realm = realm
                    break

        valkyrie_name = data.get('valkyrie')
        if valkyrie_name:
            for valkyrie in Valkyrie:
                if valkyrie.name == valkyrie_name:
                    self.valkyrie = valkyrie
                    break

        self.valkyrie_index = data.get('valkyrie_index', -1)
        self.volund_active = data.get('volund_active', False)
        self.volund_weapon = data.get('volund_weapon', "")


# ============================================================================
# ENEMY CLASS - FIXED with AI pattern tracking
# ============================================================================

class Enemy(Character):
    def __init__(self, name, title, hp, energy, abilities, rank, affiliation="", round_num=0, realm_list=None,
                 soul_dark=False):
        super().__init__(name, title, hp, energy, realm_list)
        self.abilities = {}
        for key, abil in abilities.items():
            self.abilities[key] = {
                "name": abil["name"],
                "dmg": abil["dmg"],
                "cost": abil.get("cost", 25),
                "type": abil.get("type", "damage"),
                "desc": abil.get("desc", ""),
                "divine": abil.get("divine", False),
                "blockable": abil.get("blockable", True)
            }
        self.rank = rank
        self.affiliation = affiliation
        self.round = round_num
        self.ai_pattern = []
        self.ai_pattern_index = 0  # FIXED: Track position in pattern
        self.soul_dark = soul_dark


# ============================================================================
# ADAM COPY MECHANICS
# ============================================================================

class AdamCopyMechanics:
    @staticmethod
    def calculate_copy_chance(adam, technique_name, target, enemy_rank, is_divine_technique=False):
        chance = 0.4
        factors = []

        chance += 0.2
        factors.append("Eyes of the Lord (+20%)")

        if technique_name in adam.technique_view_count:
            view_bonus = min(0.75, adam.technique_view_count[technique_name] * 0.15)
            if view_bonus > 0:
                chance += view_bonus
                factors.append(f"Seen {adam.technique_view_count[technique_name]}x (+{int(view_bonus * 100)}%)")

        if target == adam:
            chance += 0.5
            factors.append("Direct hit (+50%)")

        if adam.hp < adam.max_hp * 0.5:
            chance += 0.25
            factors.append("Fighting for children (+25%)")

        if is_divine_technique:
            chance -= 0.15
            factors.append("Divine technique (-15%)")

        if enemy_rank < 15:
            chance += 0.1
            factors.append("Copying a god (+10%)")

        if adam.volund_active:
            chance += 0.15
            factors.append("Völundr active (+15%)")

        if adam.active_realm == Realm.GODLY_TECHNIQUE:
            chance += 0.3
            factors.append("Technique Realm (+30%)")
        elif adam.active_realm == Realm.GODLY_SPEED:
            chance += 0.2
            factors.append("Speed Realm (+20%)")

        if adam.blindness > 0:
            blindness_penalty = adam.blindness * 0.05
            chance -= blindness_penalty
            factors.append(f"Blindness (-{int(blindness_penalty * 100)}%)")

        chance = min(0.95, max(0.1, chance))
        return chance, factors

    @staticmethod
    def improve_copied_technique(adam, technique_name, new_views):
        if technique_name not in adam.copied_techniques_data:
            return None

        old_data = adam.copied_techniques_data[technique_name]
        old_dmg = old_data["damage"]
        old_views = old_data["views"]

        view_increase = new_views - old_views
        if view_increase <= 0:
            return None

        dmg_increase = min(80, view_increase * 8)
        new_min_dmg = old_dmg[0] + dmg_increase
        new_max_dmg = old_dmg[1] + dmg_increase

        if "key" in old_data:
            key = old_data["key"]
            if key in adam.abilities:
                adam.abilities[key]["dmg"] = (new_min_dmg, new_max_dmg)
                adam.abilities[key]["views"] = new_views

        adam.copied_techniques_data[technique_name]["views"] = new_views
        adam.copied_techniques_data[technique_name]["damage"] = (new_min_dmg, new_max_dmg)

        return f"👁️✨ [COPY MASTERY] Adam perfects {technique_name}! (Now seen {new_views} times, +{dmg_increase} damage) [TRANSFORMATION: The technique becomes more refined with each viewing]"

    @staticmethod
    def get_copy_stats(adam):
        print("\n" + "=" * 110)
        slow_print("👁️👁️👁️ ADAM'S DIVINE REPLICATION STATISTICS 👁️👁️👁️", 0.03)
        print("=" * 110)
        print(f"   • Techniques Copied: {adam.copy_count}/{adam.max_copy}")
        print(f"   • Blindness Level: {adam.blindness}")
        print(f"   • Völundr Active: {'✅' if adam.volund_active else '❌'}")
        print()

        if adam.copied_techniques_data:
            print("   📖 COPIED TECHNIQUES:")
            for technique, data in adam.copied_techniques_data.items():
                print(f"      • {technique}: Seen {data['views']}x | DMG: {data['damage'][0]}-{data['damage'][1]}")
        else:
            print("   No techniques copied yet.")

        if adam.technique_view_count:
            print("\n   👁️ TECHNIQUES OBSERVED:")
            for technique, views in adam.technique_view_count.items():
                if technique not in adam.copied_techniques:
                    chance = min(95, 40 + (views * 15))
                    print(f"      • {technique}: Seen {views}x ({chance}% copy chance)")

        print("=" * 110)


# ============================================================================
# ADAM - Father of Humanity (FIXED with immediate death trigger)
# ============================================================================

class Adam(Character):
    def __init__(self):
        super().__init__(
            "Adam",
            "Father of Humanity",
            1300, 440,
            [Realm.GODLY_SPEED, Realm.GODLY_WILL]
        )
        self.round = 2
        self.affiliation = "Humanity"
        self.can_copy = True
        self.copy_count = 0
        self.max_copy = 15
        self.copied_techniques = []
        self.copied_techniques_data = {}
        self.technique_view_count = {}
        self.blindness = 0
        self.death_activated = False

        self.abilities = {
            '1': {"name": "👁️ Divine Replication", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "👁️ [EYES OF THE LORD] Adam's eyes can copy any divine technique AND biology he witnesses. When copying the Serpent, his hands grew three times in size with black-green scales and sharp bone claws. Success chance increases with each viewing. [TRANSFORMATION: Divine energy flows through Adam's body, allowing him to perfectly replicate any technique AND biological transformation he sees]"},
            '2': {"name": "👊 Basic Strike", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "👊 [BASIC PUNCH] A basic attack from the Father of Humanity. Even this simple strike carries the weight of paternal love. [TRANSFORMATION: Pure paternal love manifests as raw physical force]"},
            '3': {"name": "👁️ Father's Love", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "effect": "fight_on_death",
                  "desc": "👁️ [FATHER'S SACRIFICE] Even after death, Adam fights on for his children. His will is so strong that his body continues to fight even after being killed. [TRANSFORMATION: Love transcends mortality itself - Adam's spirit refuses to fade]"},
            '4': {"name": "🐍 The Serpent's Claws", "cost": 40, "dmg": (190, 260), "type": "damage",
                  "effect": "serpent_claws",
                  "desc": "🐍 [SERPENT'S CLAWS] Adam copies the Serpent's attack that once assaulted Eve. His hands grow three times in size with black-green scales and sharp bone claws capable of rending divine flesh. [TRANSFORMATION: Adam's biology morphs - hands become draconic claws]"},
        }
        self.abilities['98'] = {"name": "📊 View Copy Statistics", "cost": 0, "dmg": (0, 0), "type": "utility",
                                "desc": "📊 [COPY ANALYSIS] View detailed statistics about Adam's copied techniques including copy chances, blindness level, and technique mastery."}
        self._base_abilities = dict(self.abilities)  # FIXED: snapshot after ability 98 is added

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.REGINLEIF:
            return f"❌ Adam can only bond with Reginleif!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Brass Knuckles (メリケンサック)"

        self.divine_technique = {
            "name": "👁️ DIVINE REPLICATION: EYES OF THE LORD",
            "cost": 200,
            "dmg": (600, 800),
            "type": "damage",
            "desc": "👁️ [ULTIMATE COPY] Adam's ultimate technique - combines all copied techniques into one devastating attack. Every technique Adam has ever witnessed flows through him simultaneously, creating the ultimate divine strike. [TRANSFORMATION: Every technique Adam has ever witnessed flows through him simultaneously]"
        }

        self.abilities['1']["desc"] += " [VÖLUNDR BOOST: Reginleif's power increases copy chance by +15%]"

        print(f"\n⚔️ VÖLUNDR: Adam x Reginleif")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → [TRANSFORMATION: Reginleif's divine power")
        print(f"      crystallizes into brass knuckles")
        print(f"      around Adam's fist]")
        print(f"   → Copy chance +15%")
        return f"✅ Völundr successfully activated for Adam!"

    def apply_effect(self, effect, target=None):
        if effect == "fight_on_death" and not self.death_activated:
            self.death_activated = True
            self.hp = 1
            self.divine_mode = True
            self.divine_timer = 3
            self.add_status_effect(StatusEffect.DIVINE, 3)
            return "👁️ [FATHER'S LOVE] Adam fights even AFTER DEATH! The Father of Humanity will not abandon his children! [TRANSFORMATION: Adam's soul burns brighter than ever, defying death itself]"
        elif effect == "serpent_claws":
            self.add_status_effect(StatusEffect.ARM_EXTENSION, 3)
            return "🐍 [SERPENT'S CLAWS] Adam's hands transform into draconic claws! [TRANSFORMATION: Adam's biology morphs - hands become draconic claws for 3 turns]"
        return ""

    def attempt_copy(self, technique_name, technique_damage, target, enemy_rank, is_divine=False):
        if technique_name in self.technique_view_count:
            self.technique_view_count[technique_name] += 1
        else:
            self.technique_view_count[technique_name] = 1

        current_views = self.technique_view_count[technique_name]

        if technique_name in self.copied_techniques:
            result = AdamCopyMechanics.improve_copied_technique(self, technique_name, current_views)
            if result:
                return result
            return None

        if self.copy_count >= self.max_copy:
            return None

        chance, factors = AdamCopyMechanics.calculate_copy_chance(
            self, technique_name, target, enemy_rank, is_divine
        )

        if random.random() < chance:
            return self._add_copied_technique(technique_name, technique_damage, current_views, factors)
        elif chance > 0.7 and random.random() < 0.3:
            return f"👁️ [COPY ATTEMPT] Adam's eyes follow {technique_name}... almost got it! ({int(chance * 100)}% chance)"

        return None

    def _add_copied_technique(self, technique_name, technique_damage, views, factors=None):
        self.copied_techniques.append(technique_name)
        self.copy_count += 1

        base_dmg = max(technique_damage[0] // 2, 80)
        view_bonus = min(100, views * 8)
        total_min_dmg = base_dmg + view_bonus
        total_max_dmg = base_dmg + view_bonus + 50

        new_key = str(10 + self.copy_count)
        self.abilities[new_key] = {
            "name": f"👁️ Copy: {technique_name}",
            "cost": 25 + (views * 2),
            "dmg": (total_min_dmg, total_max_dmg),
            "type": "damage",
            "views": views,
            "desc": f"👁️ [COPIED TECHNIQUE] Adam's replication of {technique_name}. Seen {views} times. Through the Eyes of the Lord, Adam perfectly reproduces this divine technique, though each copy strains his divine vision. [TRANSFORMATION: Through the Eyes of the Lord, Adam perfectly reproduces this divine technique]"
        }

        self.copied_techniques_data[technique_name] = {
            "key": new_key,
            "views": views,
            "damage": (total_min_dmg, total_max_dmg)
        }

        self.blindness += 1
        if self.blindness >= 3:
            self.add_status_effect(StatusEffect.BLIND, 1, stacks=self.blindness)

        blindness_msg = ""
        if self.blindness >= 3:
            blindness_msg = f" ⚠️ Vision deteriorating! Blindness level: {self.blindness}"
        if self.blindness >= 5:
            self.stunned = True
            blindness_msg += " Adam is temporarily BLIND!"

        factors_str = f" ({' + '.join(factors)})" if factors and random.random() < 0.3 else ""
        view_word = "time" if views == 1 else "times"

        return f"👁️✨ [COPY SUCCESS] ADAM COPIES {technique_name}! (Seen {views} {view_word}){factors_str}{blindness_msg}"

    def get_copy_stats(self):
        AdamCopyMechanics.get_copy_stats(self)

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()

        if self.copy_count > 0:
            technique_mastery = 1.0 + (self.copy_count * 0.03)
            mult *= technique_mastery
            buffs.append(f"📚 {self.copy_count} TECHNIQUES")

        if self.blindness > 0:
            overcoming_bonus = 1.0 + (self.blindness * 0.1)
            mult *= overcoming_bonus
            buffs.append(f"🕶️ OVERCOMING BLINDNESS (+{self.blindness * 10}%)")

        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "👁️ DIVINE REPLICATION: EYES OF THE LORD",
                "cost": 200,
                "dmg": (600, 800),
                "type": "damage",
                "desc": "👁️ [ULTIMATE COPY] Adam's ultimate technique - combines all copied techniques into one devastating attack. Every technique Adam has ever witnessed flows through him simultaneously, creating the ultimate divine strike. [TRANSFORMATION: Every technique Adam has ever witnessed flows through him simultaneously]"
            }
        return self.divine_technique


# ============================================================================
# THOR - God of Thunder (FIXED with blockable handling)
# ============================================================================

class Thor(Character):
    def __init__(self):
        super().__init__(
            "Thor",
            "God of Thunder • Norse Pantheon",
            1250, 450,
            [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE]
        )
        self.volund_weapon = "Mjölnir (ミョルニル)"
        self.round = 1
        self.affiliation = "Gods"
        self.járngreipr_active = True
        self.mjolnir_awakened = False
        self.teleport_uses = 3
        self.gloves_damage_timer = 0
        self.tournament_teleport_uses = 3

        self.divine_technique = {
            "name": "⚡ GEIRRÖD THOR'S HAMMER",
            "cost": 180,
            "dmg": (550, 750),
            "type": "damage",
            "desc": "⚡ [GEIRRÖD THOR'S HAMMER] Thor's ultimate technique combining Thor's Hammer and Awakened Thunder Hammer. This technique matched and overwhelmed Lü Bu's Sky Eater. Mjölnir becomes a thunderstorm incarnate, lightning combining with centrifugal force to create unparalleled destructive power. [TRANSFORMATION: Mjölnir becomes a thunderstorm incarnate, lightning combining with centrifugal force]"
        }

        self.abilities = {
            '1': {"name": "⚡ Mjolnir Strike", "cost": 25, "dmg": (150, 210), "type": "damage", "divine": True,
                  "blockable": True,
                  "desc": "⚡ [MJÖLNIR STRIKE] A basic strike with the divine hammer Mjölnir. Forged by dwarven brothers, Mjölnir channels Thor's divine power into each swing, each strike carrying the weight of thunder itself. [TRANSFORMATION: Forged by dwarven brothers, Mjölnir channels Thor's divine power into each swing]"},
            '2': {"name": "⚡ Thor's Hammer", "cost": 45, "dmg": (220, 290), "type": "damage", "divine": True,
                  "blockable": True,
                  "desc": "⚡ [THOR'S HAMMER] Thor winds up Mjölnir and hurls it with tremendous force. Mjölnir becomes a projectile of pure thunder, returning to Thor's hand after striking its target like a boomerang of lightning. [TRANSFORMATION: Mjölnir becomes a projectile of pure thunder, returning to Thor's hand after striking]"},
            '3': {"name": "🧤 Remove Járngreipr", "cost": 30, "dmg": (0, 0), "type": "buff",
                  "effect": "remove_gloves",
                  "desc": "🧤 [JÁRNGREIPR REMOVAL] Thor removes his iron gauntlets Járngreipr. Without the gauntlets, Mjölnir's true power awakens, though Thor's grip becomes dangerously hot, causing him damage. The gloves were actually protecting Mjölnir from being crushed by Thor's grip. [TRANSFORMATION: Without the gauntlets, Mjölnir's true power awakens, though Thor's grip becomes dangerously hot]"},
            '4': {"name": "⚡ Awakened Mjolnir", "cost": 70, "dmg": (320, 400), "type": "damage", "divine": True,
                  "blockable": True,
                  "desc": "⚡ [AWAKENED MJÖLNIR] Thor awakens Mjölnir's true power. The hammer crackles with divine lightning, veins of power pulsing across its surface as it becomes so hot the orichalcum surrounding it melts like lava. [TRANSFORMATION: The hammer crackles with divine lightning, veins of power pulsing across its surface]"},
            '5': {"name": "⚡ Geirröd's Power", "cost": 100, "dmg": (450, 550), "type": "damage", "divine": True,
                  "blockable": False,
                  "desc": "⚡ [GEIRRÖD'S POWER] Thor channels the power of the giant Geirröd. Lightning becomes unblockable - it WILL find its mark, striking with the fury of a giant's rage. [TRANSFORMATION: Lightning becomes unblockable - it WILL find its mark]"},
            '6': {"name": "⚡ Teleport", "cost": 40, "dmg": (0, 0), "type": "utility", "effect": "teleport",
                  "desc": "⚡ [LIGHTNING TELEPORT] Thor teleports using Mjölnir's connection to lightning. 3 uses per battle. Thor becomes one with lightning, instantaneously repositioning anywhere on the battlefield. [TRANSFORMATION: Thor becomes one with lightning, instantaneously repositioning]"},
            '7': {"name": "👁️ Menacing Aura", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "👁️ [GODLY PRESENCE] Thor's mere presence radiates divine intimidation. The air crackles with electricity, making lesser beings tremble and even frightening Göll. [TRANSFORMATION: The air crackles with electricity, making lesser beings tremble]"},
            '8': {"name": "⚡ Geirröd Thor's Hammer", "cost": 150, "dmg": (500, 650), "type": "damage", "divine": True,
                  "blockable": False,
                  "desc": "⚡ [GEIRRÖD THOR'S HAMMER] Thor combines his two strongest moves - Thor's Hammer and Awakened Thunder Hammer. This technique matched and overwhelmed Lü Bu's Sky Eater. Mjölnir becomes a thunderstorm incarnate, lightning combining with centrifugal force. [TRANSFORMATION: Mjölnir becomes a thunderstorm incarnate, lightning combining with centrifugal force]"}
        }

    def apply_effect(self, effect, target=None):
        if effect == "remove_gloves":
            self.járngreipr_active = False
            self.gloves_damage_timer = 5
            self.take_damage(20)
            self.add_status_effect(StatusEffect.MJOLNIR_AWAKENED, 5)
            return "🧤 [JÁRNGREIPR REMOVAL] Thor removes iron gloves! Mjölnir's true power awakens! [TRANSFORMATION: Mjölnir's power increases but the heat deals damage over time]"
        elif effect == "teleport":
            if self.teleport_uses > 0:
                self.teleport_uses -= 1
                self.defending = True
                self.add_status_effect(StatusEffect.TELEPORT, 1)
                self.add_status_effect(StatusEffect.EVASION, 1, 0.7)
                self.add_status_effect(StatusEffect.DEFEND, 1)
                return f"⚡ [LIGHTNING TELEPORT] Thor teleports! {self.teleport_uses} uses remaining. [TRANSFORMATION: Thor dissolves into lightning and reforms elsewhere]"
            return "❌ No teleport uses remaining!"
        return ""

    def update_status_effects(self):
        super().update_status_effects()
        if not self.járngreipr_active and self.gloves_damage_timer > 0:
            self.gloves_damage_timer -= 1
            damage = 15
            self.take_damage(damage)
            print(f"  🔥 [GLOVES HEAT] Thor takes {damage} damage from Mjölnir's heat!")

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()
        if not self.járngreipr_active:
            mult *= 2.0
            buffs.append("⚡ AWAKENED MJÖLNIR")
        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "⚡ GEIRRÖD THOR'S HAMMER",
                "cost": 180,
                "dmg": (550, 750),
                "type": "damage",
                "desc": "⚡ [GEIRRÖD THOR'S HAMMER] Thor's ultimate technique combining Thor's Hammer and Awakened Thunder Hammer. This technique matched and overwhelmed Lü Bu's Sky Eater. Mjölnir becomes a thunderstorm incarnate, lightning combining with centrifugal force. [TRANSFORMATION: Mjölnir becomes a thunderstorm incarnate, lightning combining with centrifugal force]"
            }
        return self.divine_technique


# ============================================================================
# ZEUS - Godfather of the Cosmos (FIXED take_damage signature and Adamas timer)
# ============================================================================

class Zeus(Character):
    def __init__(self):
        super().__init__(
            "Zeus",
            "Godfather of the Cosmos • Greek Pantheon",
            1300, 500,
            [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE]
        )
        self.volund_weapon = "Heavenly Supremacy Gauntlets (天上天下唯我独尊)"
        self.round = 2
        self.affiliation = "Gods"
        self.form = "Normal"
        self.adamas_timer = 0
        self.neck_fix_available = True
        self.meteor_jab_count = 0
        self.footwork_active = False

        self.divine_technique = {
            "name": "👊 FIST THAT TRANSCENDS TIME",
            "cost": 200,
            "dmg": (600, 800),
            "type": "damage",
            "desc": "👊 [TIME SURPASSING FIST] Zeus's ultimate technique. A punch so impossibly fast that it transcends time itself. The fist moves before the concept of 'before' exists - by the time you see it, you've already been hit. This was Kronos' final strike which Zeus burnt into his body. [TRANSFORMATION: The fist moves before the concept of 'before' exists - by the time you see it, you've already been hit]"
        }

        self.abilities = {
            '1': {"name": "👊 Divine Punch", "cost": 25, "dmg": (160, 220), "type": "damage", "divine": True,
                  "desc": "👊 [DIVINE STRIKE] A basic punch from the Godfather of the Cosmos. Divine authority crystallizes into raw force with each strike, carrying the weight of Olympus itself. [TRANSFORMATION: Divine authority crystallizes into raw force with each strike]"},
            '2': {"name": "⚡ Meteor Jab", "cost": 35, "dmg": (190, 260), "type": "damage", "effect": "meteor_jab",
                  "divine": True,
                  "desc": "⚡ [METEOR JAB] Zeus's signature meteor jabs. Starts at near-light speed (0.01 seconds) and increases 10x with each punch. Speed multiplies exponentially - first jab is fast, tenth moves at 0.00000001 seconds, becoming a veritable meteor shower of divine punishment. [TRANSFORMATION: Speed multiplies exponentially - first jab is fast, tenth moves at 0.00000001 seconds]"},
            '3': {"name": "🦵 Divine Axe Kick", "cost": 40, "dmg": (220, 300), "type": "damage", "divine": True,
                  "desc": "🦵 [DIVINE AXE KICK] Zeus brings his leg down like a divine axe. The leg becomes a weapon that can split mountains and bisect opponents with a single devastating sweep. [TRANSFORMATION: The leg becomes a weapon that can split mountains]"},
            '4': {"name": "👣 Zeus' Footwork", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "footwork",
                  "desc": "👣 [ZEUS' FOOTWORK] Zeus employs his strange, unpredictable footwork. Afterimages confuse opponents, making Zeus appear to be everywhere at once, granting 40% evasion next turn. [TRANSFORMATION: Afterimages confuse opponents, making Zeus appear to be everywhere at once]"},
            '5': {"name": "💪 True God's Form (Muscle)", "cost": 50, "dmg": (0, 0), "type": "buff",
                  "effect": "muscle_form",
                  "desc": "💪 [TRUE GOD'S FORM] Zeus transforms into his muscle form for 3 turns. His body bulges with divine power, muscles swelling to impossible proportions, massively increasing his physical strength. [TRANSFORMATION: His body bulges with divine power, muscles swelling to impossible proportions]"},
            '6': {"name": "👑 Adamas Form", "cost": 100, "dmg": (0, 0), "type": "buff", "effect": "adamas_form",
                  "desc": "👑 [ADAMAS FORM] Zeus assumes his ultimate Adamas form. 70% damage reduction for 5 turns. His body hardens to diamond-like density, becoming virtually indestructible, though this form slowly destroys his body. [TRANSFORMATION: His body hardens to diamond-like density, becoming virtually indestructible]"},
            '7': {"name": "👊 True God's Right", "cost": 60, "dmg": (300, 370), "type": "damage", "divine": True,
                  "desc": "👊 [TRUE GOD'S RIGHT] Zeus's divine right cross. The authority of the King of Olympus manifests in this strike, a punch that carries the full might of the Godfather of the Cosmos. [TRANSFORMATION: The authority of the King of Olympus manifests in this strike]"},
            '8': {"name": "👊 Time Transcending Fist", "cost": 150, "dmg": (500, 650), "type": "damage", "divine": True,
                  "desc": "👊 [TIME TRANSCENDING FIST] A prelude to Zeus's ultimate technique. Time seems to stop as the fist travels, warping the very fabric of reality around it. [TRANSFORMATION: Time seems to stop as the fist travels]"},
            '9': {"name": "🩸 Fix Broken Neck", "cost": 0, "dmg": (0, 0), "type": "heal", "effect": "fix_neck",
                  "desc": "🩸 [NECK FIX] Zeus forcibly realigns his vertebrae. Heals 150 HP. Once per battle. Even with a broken neck, Zeus's vitality allows him to continue fighting, fixing his own spine with his bare hands. [TRANSFORMATION: Even with a broken neck, Zeus's vitality allows him to continue fighting]"},
            '10': {"name": "👊 The Fist That Surpassed Time", "cost": 200, "dmg": (650, 850), "type": "damage",
                   "divine": True,
                   "desc": "👊 [FIST THAT SURPASSED TIME] Kronos' final strike which Zeus burnt into his body. A punch so fast that time itself seems to halt. Time becomes frozen - the fist moves before the concept of 'before' exists. [TRANSFORMATION: Time becomes frozen - the fist moves before the concept of 'before' exists]"}
        }

    def apply_effect(self, effect, target=None):
        if effect == "meteor_jab":
            self.meteor_jab_count += 1
            speed = 0.01 / (10 ** self.meteor_jab_count)
            self.add_status_effect(StatusEffect.EMPOWER, 1, 1.0 + (self.meteor_jab_count * 0.1))
            return f"⚡ [METEOR JAB] Meteor Jab at {speed} seconds! Speed increased 10x! Damage +{self.meteor_jab_count * 10}% [TRANSFORMATION: Each jab moves 10x faster than the last]"
        elif effect == "footwork":
            self.footwork_active = True
            self.add_status_effect(StatusEffect.EVASION, 1, 0.4)
            self.add_status_effect(StatusEffect.FOOTWORK, 1)
            return "👣 [ZEUS' FOOTWORK] Strange footwork with afterimages! 40% evasion next turn."
        elif effect == "muscle_form":
            self.form = "Muscle"
            self.divine_mode = True
            self.divine_timer = 3
            self.add_status_effect(StatusEffect.MUSCLE_FORM, 3)
            self.add_status_effect(StatusEffect.EMPOWER, 3, 1.5)
            return "💪 [TRUE GOD'S FORM] ZEUS TRANSFORMS! His muscles bulge with divine power! [TRANSFORMATION: Zeus's body swells with godly muscle mass]"
        elif effect == "adamas_form":
            self.form = "Adamas"
            self.divine_mode = True
            self.divine_timer = 5
            self.adamas_timer = 5
            self.add_status_effect(StatusEffect.ADAMAS, 5)
            return "👑 [ADAMAS FORM] ADAMAS FORM! Virtually indestructible! But this form destroys his body... [TRANSFORMATION: Zeus's body compresses to diamond-like density, muscles turning inside out]"
        elif effect == "fix_neck":
            if self.neck_fix_available:
                if self.hp < self.max_hp * 0.3:
                    self.neck_fix_available = False
                    self.heal(150)
                    self.add_status_effect(StatusEffect.NECK_FIX, 999)
                    return "🩸 [NECK FIX] Zeus fixes his own broken neck! Heals 150 HP. [TRANSFORMATION: Zeus forcibly realigns his vertebrae with his bare hands]"
                else:
                    return "❌ Can only use Neck Fix when below 30% HP!"
            return "❌ Neck fix already used!"
        return ""

    def take_damage(self, dmg, ignore_defense=False):
        """FIXED: Proper signature and Adamas timer decrement"""
        if self.has_status_effect(StatusEffect.ADAMAS):
            dmg = int(dmg * 0.3)
        return super().take_damage(dmg, ignore_defense)

    def update_status_effects(self):
        super().update_status_effects()
        if self.adamas_timer > 0:
            self.adamas_timer -= 1
            if self.adamas_timer <= 0 and self.has_status_effect(StatusEffect.ADAMAS):
                self.form = "Normal"
                self.remove_status_effect(StatusEffect.ADAMAS)
                print(f"  ⏳ Zeus's Adamas Form fades.")

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "👊 FIST THAT TRANSCENDS TIME",
                "cost": 200,
                "dmg": (600, 800),
                "type": "damage",
                "desc": "👊 [TIME SURPASSING FIST] Zeus's ultimate technique. A punch so impossibly fast that it transcends time itself. The fist moves before the concept of 'before' exists - by the time you see it, you've already been hit. [TRANSFORMATION: The fist moves before the concept of 'before' exists - by the time you see it, you've already been hit]"
            }
        return self.divine_technique


# ============================================================================
# POSEIDON - God of the Seas (FIXED with move tracking and petrify effect)
# ============================================================================

class Poseidon(Character):
    def __init__(self):
        super().__init__(
            "Poseidon",
            "God of the Seas • Greek Pantheon",
            1200, 460,
            [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE]
        )
        self.volund_weapon = "Trident of the Deep (海神の三叉戟)"
        self.round = 3
        self.affiliation = "Gods"
        self.used_moves = []
        self.water_level = 100
        self.water_regen_timer = 0

        self.divine_technique = {
            "name": "🌊 40 DAYS AND 40 NIGHTS OF FLOOD",
            "cost": 180,
            "dmg": (550, 750),
            "type": "damage",
            "desc": "🌊 [FORTY DAY FLOOD] Poseidon's ultimate technique. A relentless assault of 40 consecutive trident thrusts. Like the great flood that drowned the world, this technique is inescapable and overwhelming. [TRANSFORMATION: Like the great flood that drowned the world, this technique is inescapable and overwhelming]"
        }

        self.abilities = {
            '1': {"name": "🌊 Trident Thrust", "cost": 25, "dmg": (160, 220), "type": "damage", "divine": True,
                  "desc": "🌊 [TRIDENT THRUST] A basic thrust of Poseidon's divine trident. Sea foam crystallizes into the divine trident with each thrust, each strike as inevitable as the tide. [TRANSFORMATION: Sea foam crystallizes into the divine trident with each thrust]"},
            '2': {"name": "🌊 Divine Speed", "cost": 30, "dmg": (190, 250), "type": "damage", "divine": True,
                  "desc": "🌊 [DIVINE SPEED] Poseidon attacks with the speed of a raging sea. The trident becomes a blur, striking faster than the eye can follow, like waves crashing against the shore. [TRANSFORMATION: The trident becomes a blur, striking faster than the eye can follow]"},
            '3': {"name": "🌊 Amphitrite", "cost": 40, "dmg": (220, 290), "type": "damage", "divine": True,
                  "blockable": False,
                  "desc": "🌊 [AMPHITRITE] Named after Poseidon's queen, this thrust flows like water around defenses. The trident becomes fluid, finding gaps where none should exist, like water seeping through cracks. [TRANSFORMATION: The trident becomes fluid, finding gaps where none should exist]"},
            '4': {"name": "🌊 Chione Tyro Demeter", "cost": 55, "dmg": (270, 340), "type": "damage", "divine": True,
                  "blockable": True,
                  "desc": "🌊 [CHIONE TYRO DEMETER] A threefold thrust combining the powers of snow, fertility, and the harvest. Three divine aspects merge into one devastating strike, as unstoppable as winter, spring, and autumn combined. [TRANSFORMATION: Three divine aspects merge into one devastating strike]"},
            '5': {"name": "🌊 Medusa Alope Demeter", "cost": 75, "dmg": (350, 430), "type": "damage", "divine": True,
                  "blockable": True,
                  "effect": "petrify",
                  "desc": "🌊 [MEDUSA ALOPE DEMETER] A devastating combination that turns opponents to stone and drowns them. The trident strikes with the petrifying power of Medusa and the drowning force of the sea. [TRANSFORMATION: The trident strikes with the petrifying power of Medusa and the drowning force of the sea]"},
            '6': {"name": "🌊 Hydrokinesis", "cost": 35, "dmg": (0, 0), "type": "utility", "effect": "hydrokinesis",
                  "desc": "🌊 [HYDROKINESIS] Poseidon manipulates water to create defensive barriers. Water rises from the ground, forming a protective wall that can block attacks. [TRANSFORMATION: Water rises from the ground, forming a protective wall]"},
            '7': {"name": "✨ Materialize Trident", "cost": 15, "dmg": (0, 0), "type": "buff", "effect": "materialize",
                  "desc": "✨ [MATERIALIZE TRIDENT] Poseidon materializes his divine trident from sea foam, +20 energy. Sea foam condenses into the divine trident, ready to strike. [TRANSFORMATION: Sea foam crystallizes into the divine trident]"},
            '8': {"name": "👑 Pride of the Seas", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "👑 [PRIDE OF THE SEAS] Poseidon's divine pride makes him refuse to acknowledge any opponent as worthy. This arrogance is both his greatest strength and weakness, driving him to fight with absolute contempt for his enemies. [PASSIVE: This arrogance is both his greatest strength and weakness]"}
        }

    def apply_effect(self, effect, target=None):
        if effect == "hydrokinesis":
            if self.water_level >= 10:
                self.water_level -= 10
                self.defending = True
                self.add_status_effect(StatusEffect.WATER_BARRIER, 1)
                return f"🌊 [WATER BARRIER] Water barrier created. Water level: {self.water_level}% [TRANSFORMATION: Ocean water forms a protective barrier around Poseidon]"
            return "❌ Water level too low!"
        elif effect == "materialize":
            self.energy = min(self.max_energy, self.energy + 20)
            return "✨ [TRIDENT MATERIALIZATION] Poseidon materializes his trident! +20 energy. [TRANSFORMATION: Sea foam condenses into the divine trident]"
        elif effect == "petrify":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.SLOW, 2, 0.5)
            return "🗿 [PETRIFY] Medusa's power turns the target's movements to stone! SLOWED for 2 turns."
        return ""

    def use_ability(self, ability_key):
        if ability_key in self.abilities:
            ability = self.abilities[ability_key]
            ability_name = ability["name"]

            if ability_name in self.used_moves:
                print(f"👑 [PRIDE OF THE SEAS] Poseidon's pride refuses to repeat {ability_name}! He never uses the same move twice.")
                return False

            self.used_moves.append(ability_name)

            return True
        return True

    def update_status_effects(self):
        super().update_status_effects()
        self.water_regen_timer += 1
        if self.water_regen_timer >= 3:
            self.water_regen_timer = 0
            if self.water_level < 100:
                self.water_level = min(100, self.water_level + 10)
                print(f"  💧 Poseidon's water level regenerates to {self.water_level}%")

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "🌊 40 DAYS AND 40 NIGHTS OF FLOOD",
                "cost": 180,
                "dmg": (550, 750),
                "type": "damage",
                "desc": "🌊 [FORTY DAY FLOOD] Poseidon's ultimate technique. A relentless assault of 40 consecutive trident thrusts. Like the great flood that drowned the world, this technique is inescapable and overwhelming. [TRANSFORMATION: Like the great flood that drowned the world, this technique is inescapable and overwhelming]"
            }
        return self.divine_technique


# ============================================================================
# HERACLES - God of Fortitude (FIXED with healing labor no longer triggering tattoo)
# ============================================================================

class Heracles(Character):
    def __init__(self):
        super().__init__(
            "Heracles",
            "God of Fortitude • Greek Pantheon",
            1350, 430,
            [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE]
        )
        self.volund_weapon = "Nemean Lion Pelt Armour (ネメアの獅子の毛皮)"
        self.round = 4
        self.affiliation = "Gods"
        self.labors_used = 0
        self.tattoo_progress = 0
        self.cerberus_active = False

        self.divine_technique = {
            "name": "🦁 CERBERUS: Hound of Hades",
            "cost": 180,
            "dmg": (520, 680),
            "type": "damage",
            "desc": "🦁 [CERBERUS FUSION] Heracles fuses with Cerberus, the three-headed hound of Hades. Heracles gains claws, fangs, and demonic power, becoming a beast that rivals the monsters he once defeated. [TRANSFORMATION: Heracles gains claws, fangs, and demonic power, becoming a beast that rivals the monsters he once defeated]"
        }

        self.abilities = {
            '1': {"name": "🦁 1st Labor: Nemean Lion", "cost": 30, "dmg": (170, 230), "type": "damage", "labor": 1,
                  "desc": "🦁 [NEMEAN LION] Heracles uses the pelt of the Nemean Lion. The lion's invulnerable hide manifests around Heracles' strike, making it as unstoppable as the legendary beast. [TRANSFORMATION: The lion's invulnerable hide manifests around Heracles' strike]"},
            '2': {"name": "🐍 2nd Labor: Lernaean Hydra", "cost": 35, "dmg": (190, 250), "type": "damage", "labor": 2,
                  "desc": "🐍 [LERNAEAN HYDRA] Heracles channels the Hydra's regenerative power. Each strike seems to multiply, like the heads of the Hydra, growing more numerous with each attack. [TRANSFORMATION: Each strike seems to multiply, like the heads of the Hydra]"},
            '3': {"name": "🦌 3rd Labor: Ceryneian Hind", "cost": 30, "dmg": (180, 240), "type": "damage", "labor": 3,
                  "desc": "🦌 [CERYNEIAN HIND] Heracles moves with the speed of the golden-horned hind. Swift and precise as the sacred animal of Artemis, his attacks become impossible to predict. [TRANSFORMATION: Swift and precise as the sacred animal of Artemis]"},
            '4': {"name": "🐗 4th Labor: Erymanthian Boar", "cost": 40, "dmg": (210, 280), "type": "damage", "labor": 4,
                  "desc": "🐗 [ERYMANTHIAN BOAR] Heracles charges with the unstoppable force of the Erymanthian Boar. Trampling everything in his path like the savage beast. [TRANSFORMATION: Trampling everything in his path]"},
            '5': {"name": "💧 5th Labor: Augean Stables", "cost": 35, "dmg": (200, 260), "type": "damage", "labor": 5,
                  "desc": "💧 [AUGEAN STABLES] Heracles diverts rivers of power into his attacks. Overwhelming opponents with sheer volume like the redirected rivers. [TRANSFORMATION: Overwhelming opponents with sheer volume]"},
            '6': {"name": "🐦 6th Labor: Stymphalian Birds", "cost": 40, "dmg": (220, 290), "type": "damage", "labor": 6,
                  "desc": "🐦 [STYMPHALIAN BIRDS] Heracles launches rapid strikes like the bronze-feathered birds. Each strike sharp as a blade, a storm of feathers. [TRANSFORMATION: Each strike sharp as a blade]"},
            '7': {"name": "🐂 7th Labor: Cretan Bull", "cost": 45, "dmg": (240, 310), "type": "damage", "labor": 7,
                  "desc": "🐂 [CRETAN BULL] Heracles wrestles with the power of the Cretan Bull. Using the bull's own strength against it, turning raw power into technique. [TRANSFORMATION: Using the bull's own strength against it]"},
            '8': {"name": "🐴 8th Labor: Mares of Diomedes", "cost": 35, "dmg": (210, 270), "type": "damage", "labor": 8,
                  "desc": "🐴 [MARES OF DIOMEDES] Heracles unleashes the man-eating fury of Diomedes' mares. Savage and relentless, like the flesh-eating horses. [TRANSFORMATION: Savage and relentless]"},
            '9': {"name": "👑 9th Labor: Hippolyta's Belt", "cost": 40, "dmg": (230, 300), "type": "damage", "labor": 9,
                  "desc": "👑 [HIPPOLYTA'S BELT] Heracles strikes with the authority of the Amazon queen. Precise and deadly, a queen's judgment. [TRANSFORMATION: Precise and deadly]"},
            '10': {"name": "🐮 10th Labor: Geryon's Cattle", "cost": 45, "dmg": (250, 320), "type": "damage",
                   "labor": 10,
                   "desc": "🐮 [GERYON'S CATTLE] Heracles drives forward like the cattle of the three-bodied giant. Multiple impacts overwhelm the opponent, three bodies worth of power. [TRANSFORMATION: Multiple impacts overwhelm the opponent]"},
            '11': {"name": "🍎 11th Labor: Apples of Hesperides", "cost": 50, "dmg": (0, 0), "type": "heal", "labor": 11,
                   "effect": "heal",
                   "desc": "🍎 [APPLES OF HESPERIDES] Heracles reaches for the golden apples of immortality. Divine essence restores health, the fruit of the gods. [TRANSFORMATION: Divine essence restores health]"},
            '12': {"name": "🐕 12th Labor: Cerberus", "cost": 100, "dmg": (400, 500), "type": "damage", "labor": 12,
                   "effect": "cerberus",
                   "desc": "🐕 [CERBERUS SUBJUGATION] Heracles subdues Cerberus, the three-headed hound of Hades. This ultimate labor allows him to tap into the beast's power, fusing with the hound. [TRANSFORMATION: This ultimate labor allows him to tap into the beast's power]"},
            '13': {"name": "🐾 Claw of Heracles", "cost": 60, "dmg": (320, 410), "type": "damage", "cerberus_only": True,
                   "desc": "🐾 [CLAW OF HERACLES] Only available in Cerberus form. Heracles slashes with claws that rend souls. Cerberus' power manifests as invisible claws - each attack creates giant cuts in synchrony with Heracles' movements. The air itself is torn by demonic energy. [TRANSFORMATION: Cerberus' power manifests as invisible claws - each attack creates giant cuts in synchrony with Heracles' movements. The air itself is torn by demonic energy]"},
            '14': {"name": "👊 Apheles Heros", "cost": 80, "dmg": (380, 480), "type": "damage", "cerberus_only": True,
                   "desc": "👊 [APHELES HEROS] 'Great Hero's Fist' - Heracles focuses power in his right arm, enlarging it for a devastating punch that creates a gigantic crater. His arm swells with divine power - the fist of a true hero. [TRANSFORMATION: His arm swells with divine power - the fist of a true hero]"}
        }

    def apply_effect(self, effect, target=None):
        if effect == "cerberus":
            self.cerberus_active = True
            self.divine_mode = True
            self.divine_timer = 5
            self.add_status_effect(StatusEffect.CERBERUS, 5)
            return "🐕 [CERBERUS FUSION] HERACLES FUSES WITH CERBERUS! Gains claws, fangs, and demonic power! His tattoo glows crimson! [TRANSFORMATION: Gains claws, fangs, and demonic power! His tattoo glows crimson]"
        elif effect == "heal":
            heal_amount = 150
            self.heal(heal_amount)
            return f"🍎 [APPLES OF HESPERIDES] Heracles heals for {heal_amount} HP!"
        elif effect == "divine_protection":
            self.defending = True
            self.add_status_effect(StatusEffect.DEFEND, 1)
            self.add_status_effect(StatusEffect.SHIELD, 1, 0.5)
            return "🦁 [DIVINE PROTECTION] Heracles braces himself with divine fortitude! Damage reduced by 50% this turn!"
        return ""

    def use_labor(self, labor_num):
        if labor_num == 11:
            return None

        self.labors_used += 1
        self.tattoo_progress += 8

        if self.tattoo_progress > 100:
            self.tattoo_progress = 100

        damage_taken = 10 + (self.tattoo_progress // 2)
        actual_damage = self.take_damage(damage_taken)

        self.add_status_effect(StatusEffect.TATTOO, 1, stacks=self.tattoo_progress // 10)

        if self.tattoo_progress >= 100:
            self.hp = 0
            return "💀 [TATTOO COMPLETE] The tattoo covers Heracles' entire body. He falls. [TRANSFORMATION: The divine tattoo finally consumes him entirely]"
        return f"🩸 [TATTOO SPREAD] Tattoo spreads! Heracles takes {actual_damage} damage. Tattoo: {self.tattoo_progress}% [TRANSFORMATION: The labors scar his body, each one bringing him closer to death]"

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "🦁 CERBERUS: Hound of Hades",
                "cost": 180,
                "dmg": (520, 680),
                "type": "damage",
                "desc": "🦁 [CERBERUS FUSION] Heracles fuses with Cerberus, the three-headed hound of Hades. Heracles gains claws, fangs, and demonic power, becoming a beast that rivals the monsters he once defeated. [TRANSFORMATION: Heracles gains claws, fangs, and demonic power, becoming a beast that rivals the monsters he once defeated]"
            }
        return self.divine_technique


# ============================================================================
# SHIVA - God of Destruction (FIXED with proper damage return)
# ============================================================================

class Shiva(Character):
    def __init__(self):
        super().__init__(
            "Shiva",
            "God of Destruction • Hindu Pantheon",
            1280, 450,
            [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE]
        )
        self.volund_weapon = "Four Divine Arms (四神の腕)"
        self.round = 5
        self.affiliation = "Gods"
        self.arms_remaining = 4
        self.tandava_level = 0
        self.tandava_karma_active = False
        self.permanent_arm_loss = False

        self.divine_technique = {
            "name": "🔥 DEVA LOKA",
            "cost": 190,
            "dmg": (580, 750),
            "type": "damage",
            "desc": "🔥 [DEVA LOKA] Shiva's ultimate spinning heel kick performed in Tandava Karma state. With his heart accelerated to divine speeds, he becomes a whirlwind of destruction, each rotation generating enough force to shatter divine weapons. [TRANSFORMATION: With his heart accelerated to divine speeds, he becomes a whirlwind of destruction]"
        }

        self.abilities = {
            '1': {"name": "🔥 Four Arms Strike", "cost": 30, "dmg": (180, 240), "type": "damage", "multi": 4,
                  "desc": "🔥 [FOUR ARMS STRIKE] Shiva attacks with all four arms simultaneously. A barrage of blows from multiple angles, each arm delivering destruction from a different direction. [TRANSFORMATION: A barrage of blows from multiple angles]"},
            '2': {"name": "💃 Tandava Dance", "cost": 50, "dmg": (240, 320), "type": "damage", "effect": "tandava",
                  "desc": "💃 [TANDAVA DANCE] Shiva begins his cosmic dance of destruction. Each movement flows into the next, building power and momentum as he dances to the rhythm of the cosmos. [TRANSFORMATION: Each movement flows into the next, building power and momentum]"},
            '3': {"name": "🔥 Krittivasa", "cost": 45, "dmg": (230, 300), "type": "damage",
                  "blockable": False,
                  "desc": "🔥 [KRITTIVASA] Named after Shiva's form 'clad in skin,' this technique strips away defenses. Devastating palm strikes that bypass protection, hitting the soul directly. [TRANSFORMATION: Devastating palm strikes that bypass protection]"},
            '4': {"name": "💓 Tandava Karma", "cost": 100, "dmg": (0, 0), "type": "buff", "effect": "karma",
                  "karma_only": False,
                  "desc": "💓 [TANDAVA KARMA] Shiva forces his heart to beat faster, directly stimulating his atman (spirit). Massive power boost for 5 turns, but his body slowly burns away. Blue flames consume his body - each moment of power brings him closer to ash. [TRANSFORMATION: Blue flames consume his body - each moment of power brings him closer to ash]"},
            '5': {"name": "🕉️ Deva Loka", "cost": 70, "dmg": (350, 450), "type": "damage", "karma_only": True,
                  "desc": "🕉️ [DEVA LOKA] Shiva's spinning heel kick, delivered from the realm of the gods. Each rotation generates enough force to shatter divine weapons. [TRANSFORMATION: Each rotation generates enough force to shatter divine weapons]"},
            '6': {"name": "🔄 Unpredictable Rhythm", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "🔄 [UNPREDICTABLE RHYTHM] Shiva's dance follows no predictable pattern. His movements seem chaotic but follow the divine rhythm of destruction itself, making his attacks impossible to anticipate. [PASSIVE: His movements seem chaotic but follow the divine rhythm of destruction itself]"},
            '7': {"name": "💫 Hidden Treasure of the Indian Pantheon", "cost": 65, "dmg": (200, 260), "type": "damage",
                  "multi": 3, "effect": "hidden_treasure",
                  "desc": "💫 [HIDDEN TREASURE OF THE INDIAN PANTHEON] Shiva's go-to move — a blazing martial dance that unleashes multi-hit attacks at enhanced speed. His movements become so unpredictable that the opponent feels assaulted by many enemies at once, each strike flowing seamlessly into the next. [TRANSFORMATION: The opponent is overwhelmed — it feels as though a dozen warriors strike from every angle simultaneously]"}
        }

    def apply_effect(self, effect, target=None):
        if effect == "tandava":
            self.tandava_level = 1
            self.add_status_effect(StatusEffect.TANDAVA, 3)
            self.add_status_effect(StatusEffect.EMPOWER, 3, 1.2)
            return "💃 [TANDAVA DANCE] SHIVA BEGINS THE TANDAVA! Power increases each turn as his dance grows more intense! [TRANSFORMATION: Power increases each turn as his dance grows more intense]"
        elif effect == "karma":
            self.tandava_karma_active = True
            self.divine_mode = True
            self.divine_timer = 5
            self.add_status_effect(StatusEffect.KARMA, 5)
            self.add_status_effect(StatusEffect.BURN, 5)
            self.add_status_effect(StatusEffect.EMPOWER, 5, 2.0)
            return "💓 [TANDAVA KARMA] SHIVA'S HEART ACCELERATES! Blue flames consume his body - massive power boost but he slowly burns! [TRANSFORMATION: Blue flames consume his body - massive power boost but he slowly burns]"
        elif effect == "hidden_treasure":
            self.add_status_effect(StatusEffect.EMPOWER, 2, 1.3)
            return "💫 [HIDDEN TREASURE] SHIVA UNLEASHES HIS GO-TO MOVE! A blazing martial dance — multi-hit assault from all angles! The opponent feels surrounded by dozens of warriors! [TRANSFORMATION: His dance accelerates into pure chaos, each limb a separate attacker]"
        return ""

    def take_damage(self, dmg, ignore_defense=False):
        actual_damage = super().take_damage(dmg, ignore_defense)

        if self.arms_remaining > 1 and random.random() < 0.1 and actual_damage > 50:
            self.arms_remaining -= 1
            self.permanent_arm_loss = True
            self.add_status_effect(StatusEffect.ARM_LOSS, 999, stacks=self.arms_remaining)
            print(
                f"🔥 [ARM LOST] Shiva loses an arm! {self.arms_remaining} arms remaining. [TRANSFORMATION: The divine tattoo fades from one of his arms]")

        return actual_damage

    def update_status_effects(self):
        # FIXED: Tandava escalates each turn — the dance grows more intense
        had_tandava = self.has_status_effect(StatusEffect.TANDAVA)
        super().update_status_effects()
        if had_tandava and self.has_status_effect(StatusEffect.TANDAVA):
            self.tandava_level = min(5, self.tandava_level + 1)
            print(f"  💃 [TANDAVA ESCALATES] Shiva's dance intensifies! Level {self.tandava_level}/5")

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()

        arm_mult = 1.0 + ((self.arms_remaining - 1) * 0.1)
        mult *= arm_mult
        buffs.append(f"🦾 {self.arms_remaining} ARMS")

        # FIXED: tandava_level now adds a stacking damage bonus each turn
        if self.tandava_level > 1:
            tandava_bonus = 1.0 + ((self.tandava_level - 1) * 0.1)
            mult *= tandava_bonus
            buffs.append(f"💃 TANDAVA LV{self.tandava_level} +{(self.tandava_level-1)*10}%")

        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "🔥 DEVA LOKA",
                "cost": 190,
                "dmg": (580, 750),
                "type": "damage",
                "desc": "🔥 [DEVA LOKA] Shiva's ultimate spinning heel kick performed in Tandava Karma state. With his heart accelerated to divine speeds, he becomes a whirlwind of destruction. [TRANSFORMATION: With his heart accelerated to divine speeds, he becomes a whirlwind of destruction]"
            }
        return self.divine_technique


# ============================================================================
# ZEROFUKU - God of Misfortune (FIXED with misery scaling)
# ============================================================================

class Zerofuku(Character):
    def __init__(self):
        super().__init__(
            "Zerofuku",
            "God of Misfortune • Seven Lucky Gods",
            1150, 410,
            [Realm.GODLY_STRENGTH]
        )
        self.volund_weapon = "Misery Cleaver (不幸の大鎌)"
        self.round = 6
        self.affiliation = "Gods"
        self.misery_level = 0
        self.cleaver_heads = 1

        self.divine_technique = {
            "name": "🎋 MISERY CLEAVER - STORM FORM",
            "cost": 170,
            "dmg": (500, 650),
            "type": "damage",
            "desc": "🎋 [MISERY STORM] Zerofuku transforms his Misery Cleaver into a storm of countless black blades. The accumulated misfortune of all humanity manifests as an inescapable rain of destruction. [TRANSFORMATION: The accumulated misfortune of all humanity manifests as an inescapable rain of destruction]"
        }

        self.abilities = {
            '1': {"name": "🎋 Misery Cleaver", "cost": 25, "dmg": (150, 210), "type": "damage",
                  "desc": "🎋 [MISERY CLEAVER] Zerofuku's divine weapon, formed from accumulated misfortune. Misfortune crystallizes into a physical blade that grows with each swing. [TRANSFORMATION: Misfortune crystallizes into a physical blade]"},
            '2': {"name": "😢 Absorb Misfortune", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "absorb",
                  "desc": "😢 [ABSORB MISFORTUNE] Zerofuku absorbs misfortune, increasing the power of his cleaver. Negative energy flows into the blade, making it grow more monstrous with each absorption. [TRANSFORMATION: Negative energy flows into the blade, making it grow]"},
            '3': {"name": "🎋 Six-Headed Form", "cost": 60, "dmg": (300, 380), "type": "damage",
                  "desc": "🎋 [SIX-HEADED FORM] The Misery Cleaver splits into six separate blades. Each head seeks out different parts of the opponent's body, attacking from multiple angles. [TRANSFORMATION: Each head seeks out different parts of the opponent's body]"},
            '4': {"name": "⚔️ Sword Transformation", "cost": 50, "dmg": (240, 330), "type": "damage",
                  "desc": "⚔️ [SWORD TRANSFORMATION] Zerofuku reshapes his cleaver into different weapon forms. The blade adapts to the flow of battle, becoming whatever weapon is needed. [TRANSFORMATION: The blade adapts to the flow of battle]"},
            '5': {"name": "🌪️ Storm Form", "cost": 100, "dmg": (400, 500), "type": "damage",
                  "desc": "🌪️ [STORM FORM] The Misery Cleaver transforms into a whirlwind of blades. Attacks from all directions at once, an inescapable storm of misfortune. [TRANSFORMATION: Attacks from all directions at once]"},
            '6': {"name": "🎋 Seven Lucky Gods Union", "cost": 120, "dmg": (470, 590), "type": "damage",
                  "desc": "🎋 [SEVEN LUCKY GODS UNION] Zerofuku channels the power of all Seven Lucky Gods. Each deity adds their unique blessing to his attack, creating a strike of both fortune and misfortune. [TRANSFORMATION: Each deity adds their unique blessing to his attack]"}
        }

    def apply_effect(self, effect, target=None):
        if effect == "misery":
            self.misery_level = min(7, self.misery_level + 1)
            self.add_status_effect(StatusEffect.MISERY, 999, stacks=self.misery_level)
            return f"🎋 [MISERY] Zerofuku channels accumulated misery! Misery Level: {self.misery_level}"
        elif effect == "cleaver_heads":
            self.cleaver_heads = min(7, self.cleaver_heads + 1)
            self.add_status_effect(StatusEffect.CLEAVER_HEADS, 999, stacks=self.cleaver_heads)
            return f"🎋 [CLEAVER HEADS] The Great Cleaver grows another head! Total heads: {self.cleaver_heads}"
        elif effect == "absorb":
            self.misery_level += 1
            self.cleaver_heads = min(7, 1 + self.misery_level)
            self.add_status_effect(StatusEffect.MISERY, 3, stacks=self.misery_level)
            self.add_status_effect(StatusEffect.CLEAVER_HEADS, 999, stacks=self.cleaver_heads)
            return f"😢 [MISFORTUNE ABSORPTION] Misfortune absorbed! Cleaver now has {self.cleaver_heads} heads. Misery Level: {self.misery_level} [TRANSFORMATION: The blade grows more monstrous with each absorption]"
        return ""

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()

        if self.misery_level > 0:
            misery_mult = 1.0 + (self.misery_level * 0.1)
            mult *= misery_mult
            buffs.append(f"😢 MISERY +{self.misery_level * 10}%")

        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "🎋 MISERY CLEAVER - STORM FORM",
                "cost": 170,
                "dmg": (500, 650),
                "type": "damage",
                "desc": "🎋 [MISERY STORM] Zerofuku transforms his Misery Cleaver into a storm of countless black blades. The accumulated misfortune of all humanity manifests as an inescapable rain of destruction. [TRANSFORMATION: The accumulated misfortune of all humanity manifests as an inescapable rain of destruction]"
            }
        return self.divine_technique


# ============================================================================
# HAJUN - Demon King of Sixth Heaven (FIXED with possession mechanic)
# ============================================================================

class Hajun(Character):
    def __init__(self):
        super().__init__(
            "Hajun",
            "Demon King of Sixth Heaven",
            1600, 500,
            [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE, Realm.GODLY_WILL]
        )
        self.volund_weapon = "Crown of Helheim (ヘルヘイムの王冠)"
        self.round = 6
        self.affiliation = "Helheim"
        self.soul_dark = True
        self.possession_active = False
        self.possession_target = None

        self.divine_technique = {
            "name": "👹 DEMON KING'S WRATH",
            "cost": 220,
            "dmg": (650, 850),
            "type": "damage",
            "desc": "👹 [DEMON KING'S WRATH] The attack that destroyed half of Helheim. Hajun unleashes his full demonic power. Pure demonic energy erupts, erasing everything in its path. [TRANSFORMATION: Pure demonic energy erupts, erasing everything in its path]"
        }

        self.abilities = {
            '1': {"name": "👹 Demon Strike", "cost": 35, "dmg": (200, 270), "type": "damage",
                  "desc": "👹 [DEMON STRIKE] A basic strike from the Demon King. Demonic energy coats each strike, carrying the weight of slaughtered souls from Helheim. [TRANSFORMATION: Demonic energy coats each strike, carrying the weight of slaughtered souls]"},
            '2': {"name": "👹 Helheim's Wrath", "cost": 55, "dmg": (300, 380), "type": "damage",
                  "desc": "👹 [HELHEIM'S WRATH] Hajun channels the rage of Helheim itself. The fury of an entire realm manifests in each attack. [TRANSFORMATION: The fury of an entire realm manifests in each attack]"},
            '3': {"name": "👹 Dark Soul", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "👹 [DARK SOUL] Hajun's soul radiates pure darkness. Techniques that rely on seeing the soul's light cannot perceive his attacks. Buddha's future sight and similar abilities fail against him. [PASSIVE: Buddha's future sight and similar abilities fail against him]"},
            '4': {"name": "👹 Demon King's Domain", "cost": 70, "dmg": (350, 450), "type": "damage",
                  "desc": "👹 [DEMON KING'S DOMAIN] Hajun expands his demonic aura, amplifying all attacks. Demonic energy expands, creating a domain where all attacks are amplified. [TRANSFORMATION: Demonic energy expands, creating a domain where all attacks are amplified]"},
            '5': {"name": "👹 Destruction of Helheim", "cost": 100, "dmg": (500, 650), "type": "damage",
                  "desc": "👹 [DESTRUCTION OF HELHEIM] Hajun replicates the attack that destroyed half of Helheim. Pure annihilation - the same power that devastated a realm. [TRANSFORMATION: Pure annihilation - the same power that devastated a realm]"},
            '6': {"name": "👹 Possess", "cost": 150, "dmg": (0, 0), "type": "utility", "effect": "possess",
                  "desc": "👹 [POSSESSION] Hajun attempts to possess an enemy, taking control of their body. The target will be unable to act for 2 turns and takes damage each turn from demonic corruption. [TRANSFORMATION: Demonic energy seeks to overwrite the target's soul]"}
        }

    def apply_effect(self, effect, target=None):
        if effect == "possess":
            self.possession_active = True
            self.add_status_effect(StatusEffect.DARK_SOUL, 1)
            return "👹 [POSSESSION] Hajun's demonic energy reaches out to possess the enemy! The target will be unable to act for 2 turns!"
        return ""

    def use_possession(self, target):
        if self.possession_active and not target.possessed:
            self.possession_active = False
            target.possessed = True
            target.add_status_effect(StatusEffect.POSSESSED, 2)
            possession_damage = 50
            target.take_damage(possession_damage, ignore_defense=True)
            return f"👹 [POSSESSION] Hajun possesses {target.name}! They take {possession_damage} damage and cannot act for 2 turns!"
        return None

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "👹 DEMON KING'S WRATH",
                "cost": 220,
                "dmg": (650, 850),
                "type": "damage",
                "desc": "👹 [DEMON KING'S WRATH] The attack that destroyed half of Helheim. Hajun unleashes his full demonic power. Pure demonic energy erupts, erasing everything in its path. [TRANSFORMATION: Pure demonic energy erupts, erasing everything in its path]"
            }
        return self.divine_technique


# ============================================================================
# HADES - God of the Underworld (FIXED with proper drain mechanics and ichor_only check)
# ============================================================================

class Hades(Character):
    def __init__(self):
        super().__init__(
            "Hades",
            "God of the Underworld • Greek Pantheon",
            1400, 460,
            [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE]
        )
        self.volund_weapon = "Bident of the Dead (冥府の二又槍) — Forged from the remnants of Poseidon's trident, fused as tribute to his fallen brother. A fin-like protrusion extends from the shaft where the divine trident was joined."
        self.round = 7
        self.affiliation = "Gods"
        self.ichor_active = False
        self.desmos_active = False
        self.drain_timer = 0

        self.divine_technique = {
            "name": "💀 ICHOR DESMOS",
            "cost": 200,
            "dmg": (600, 780),
            "type": "damage",
            "desc": "💀 [ICHOR DESMOS] Hades's ultimate technique. He infuses his bident with his own divine blood (ichor). The bident becomes a LIVING SPEAR, moving with a will of its own. [TRANSFORMATION: The bident becomes a LIVING SPEAR, moving with a will of its own]"
        }

        self.abilities = {
            '1': {"name": "💀 Bident Thrust", "cost": 25, "dmg": (170, 230), "type": "damage",
                  "desc": "💀 [BIDENT THRUST] A basic thrust of Hades's divine bident. Clean, dignified, and utterly lethal, each thrust carries the weight of the underworld. [TRANSFORMATION: Clean, dignified, and utterly lethal]"},
            '2': {"name": "💀 Persephone-Kallichoron", "cost": 45, "dmg": (240, 320), "type": "damage",
                  "desc": "💀 [PERSEPHONE-KALLICHORON] 'Iron Hammer of the Netherworld' - Named after the sacred well of Persephone. Flows like water, finding cracks in any defense. [TRANSFORMATION: Flows like water, finding cracks in any defense]"},
            '3': {"name": "💀 Persephone-Lore", "cost": 55, "dmg": (290, 370), "type": "damage",
                  "desc": "💀 [PERSEPHONE-LORE] 'Destroyer of Storms' - A thrust that carries the weight of Persephone's wisdom. Strikes at the exact moment an opponent's guard drops. [TRANSFORMATION: Strikes at the exact moment an opponent's guard drops]"},
            '4': {"name": "💀 Persephone-Titan", "cost": 60, "dmg": (330, 410), "type": "damage",
                  "desc": "💀 [PERSEPHONE-TITAN] 'The Earth Crusher' - Hades channels the power of the Titans through his bident. An earth-shattering thrust. [TRANSFORMATION: An earth-shattering thrust]"},
            '5': {"name": "🦵 Cornucopia", "cost": 40, "dmg": (230, 310), "type": "damage",
                  "desc": "🦵 [CORNUCOPIA] 'Horn of Plenty' - A sweeping kick that embodies the abundance of the underworld. A kick that carries the weight of countless souls. [TRANSFORMATION: A kick that carries the weight of countless souls]"},
            '6': {"name": "💧 Ichor Activation", "cost": 40, "dmg": (0, 0), "type": "buff", "effect": "ichor",
                  "desc": "💧 [ICHOR ACTIVATION] Hades activates the ichor flowing through his veins. Divine blood begins to flow, enhancing attacks but draining life. [TRANSFORMATION: Divine blood begins to flow, enhancing attacks but draining life]"},
            '7': {"name": "💀 Ichor-Eos", "cost": 80, "dmg": (400, 500), "type": "damage", "ichor_only": True,
                  "desc": "💀 [ICHOR-EOS] 'Dawn Guided by Blood' - Hades thrusts Desmos forward while charging. The force broke through Qin Shi Huang's Pauldron of Divine Embrace. The spear drinks Hades' blood and becomes imbued with the light of dawn. [TRANSFORMATION: The spear drinks Hades' blood and becomes imbued with the light of dawn]"},
            '8': {"name": "⚔️ Ichor Desmos", "cost": 120, "dmg": (0, 0), "type": "buff", "effect": "desmos",
                  "desc": "⚔️ [ICHOR DESMOS] 'Four-Blooded Spear of Fate' - Hades infuses his bident with his life force. The spear becomes a LIVING BEING with its own flow of Qi. The bident writhes with life - two prongs merge into a bloodstained living spear. [TRANSFORMATION: The bident writhes with life - two prongs merge into a bloodstained living spear]"}
        }

    def apply_effect(self, effect, target=None):
        if effect == "ichor":
            self.ichor_active = True
            self.add_status_effect(StatusEffect.ICHOR, 5)
            return "💧 [ICHOR ACTIVATION] HADES ACTIVATES ICHOR! His divine blood enhances his attacks but DRAINS HIS LIFE! Crimson energy flows through his veins. [TRANSFORMATION: His divine blood enhances his attacks but DRAINS HIS LIFE! Crimson energy flows through his veins]"
        elif effect == "desmos":
            self.desmos_active = True
            self.divine_mode = True
            self.divine_timer = 5
            self.drain_timer = 5
            self.add_status_effect(StatusEffect.DESMOS, 5)
            return "⚔️ [ICHOR DESMOS] ICHOR DESMOS ACTIVATED! Living spear form! The bident becomes a writhing, living extension of Hades himself! +100% damage but drains 25 HP per turn. [TRANSFORMATION: The bident becomes a writhing, living extension of Hades himself! +100% damage but drains 25 HP per turn]"
        return ""

    def update_status_effects(self):
        super().update_status_effects()
        # FIXED: Ichor drains life each turn (divine blood burns from within)
        if self.ichor_active and self.has_status_effect(StatusEffect.ICHOR):
            self.take_damage(15)
            print(f"  💧 [ICHOR DRAIN] {self.name}'s divine blood corrodes — loses 15 HP!")
        # FIXED: Desmos message now correctly says 'Desmos' not 'ichor'
        if self.desmos_active and self.drain_timer > 0:
            self.drain_timer -= 1
            self.take_damage(25)
            print(f"  ⚔️ [DESMOS DRAIN] {self.name} loses 25 HP from Desmos life-force drain!")

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()
        if self.ichor_active:
            mult *= 1.5
            buffs.append("💧 ICHOR ACTIVE +50%")
        if self.desmos_active:
            mult *= 2.0
            buffs.append("⚔️ DESMOS ACTIVE")
        return mult, buffs

    def can_use_ability(self, ability=None):
        if ability and ability.get("ichor_only") and not self.ichor_active:
            return False, "❌ This ability requires Ichor Activation first!"
        return True, ""

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "💀 ICHOR DESMOS",
                "cost": 200,
                "dmg": (600, 780),
                "type": "damage",
                "desc": "💀 [ICHOR DESMOS] Hades's ultimate technique. He infuses his bident with his own divine blood (ichor). The bident becomes a LIVING SPEAR, moving with a will of its own. [TRANSFORMATION: The bident becomes a LIVING SPEAR, moving with a will of its own]"
            }
        return self.divine_technique


# ============================================================================
# BEELZEBUB - Lord of the Flies (FIXED with proper shield and Lilith mark)
# ============================================================================

class Beelzebub(Character):
    def __init__(self):
        super().__init__(
            "Beelzebub",
            "Lord of the Flies",
            1250, 450,
            [Realm.GODLY_TECHNIQUE]
        )
        self.volund_weapon = "Staff of Apomyius (アポミュウスの杖)"
        self.round = 8
        self.affiliation = "Gods"
        self.chaos_used = False
        self.lilith_mark = True
        self.lilith_mark_used = False
        self.exhausted = False
        self.exhausted_timer = 0  # FIXED: Track exhaustion duration

        self.divine_technique = {
            "name": "🦟 ORIGINAL SIN: CHAOS",
            "cost": 250,
            "dmg": (700, 900),
            "type": "damage",
            "desc": "🦟 [ORIGINAL SIN] Beelzebub's forbidden technique. He creates a black sphere of absolute annihilation. The Staff of Apomyius consumes itself, creating a void that erases everything it touches. [TRANSFORMATION: The Staff of Apomyius consumes itself, creating a void that erases everything it touches]"
        }

        self.abilities = {
            '1': {"name": "🦟 Palmyra", "cost": 30, "dmg": (180, 240), "type": "damage",
                  "desc": "🦟 [PALMYRA] 'Devil's Beating Wings' - Beelzebub projects amplified resonances as seismic waves, causing powerful earthquakes or concentrating them into a narrow cutting point. His right hand vibrates at high frequency, creating waves that can destroy solid objects. [TRANSFORMATION: His right hand vibrates at high frequency, creating waves that can destroy solid objects]"},
            '2': {"name": "🛡️ Sorath Samekh", "cost": 25, "dmg": (0, 0), "type": "defense",
                  "effect": "shield",
                  "desc": "🛡️ [SORATH SAMEKH] 'Gates of Hell' - Beelzebub generates an almost indestructible force field made of resonances. Left hand resonances create a dark barrier - the gates of Hell itself. Can block Tesla's Plasma Jet Punches and even Thor's Mjölnir. [TRANSFORMATION: Left hand resonances create a dark barrier - the gates of Hell itself]"},
            '3': {"name": "🦟 Sorath Vav", "cost": 55, "dmg": (280, 350), "type": "damage",
                  "desc": "🦟 [SORATH VAV] 'Fallen Angel of Gluttony' - The sixth glyph of power - Beelzebub manifests hooks of darkness. Right hand resonances condense into hooks that tear at the soul. [TRANSFORMATION: Right hand resonances condense into hooks that tear at the soul]"},
            '4': {"name": "🦟 Sorath Tau", "cost": 70, "dmg": (350, 430), "type": "damage",
                  "desc": "🦟 [SORATH TAU] 'Prayer of Darkness' - The final glyph - a cross of pure darkness. Dark energy crucifies opponents with shadows. [TRANSFORMATION: Dark energy crucifies opponents with shadows]"},
            '5': {"name": "🦟 Sorath Resh", "cost": 85, "dmg": (430, 530), "type": "damage",
                  "desc": "🦟 [SORATH RESH] 'Satan's Horns' - The head glyph - Using both his right index and middle fingers, Beelzebub pierces the opponent's chest, then extends his resonance blade inward to crush their heart from the inside. A strike so precise it bypasses armor entirely. [TRANSFORMATION: Two fingers plunge forward — the resonance blade extends within, crushing the heart]"},
            '6': {"name": "💀 Lilith's Mark", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "💀 [LILITH'S MARK] The mark of Lilith allows Beelzebub to cheat death once per battle. The rose tattoo on his chest glows, refusing to let him die. [TRANSFORMATION: The rose tattoo on his chest glows, refusing to let him die]"},
            '7': {"name": "🦟 CHAOS", "cost": 150, "dmg": (550, 700), "type": "damage", "taboo": True,
                  "effect": "chaos",
                  "desc": "🦟 [CHAOS] 'No.0: Chaos' - A forbidden technique that creates a sphere of annihilation. Both hands resonate together, creating a black hole that consumes all. [TRANSFORMATION: Both hands resonate together, creating a black hole that consumes all]"}
        }
        self._base_abilities = dict(self.abilities)  # Snapshot for restoration after battle

    def apply_effect(self, effect, target=None):
        if effect == "palmyra":
            self.add_status_effect(StatusEffect.PALMYRA, 2)
            self.add_status_effect(StatusEffect.EMPOWER, 2, 1.3)
            return "🦟 [PALMYRA] Devil's Beating Wings — seismic resonance waves radiate outward! +30% damage for 2 turns."
        elif effect == "lilith_mark":
            self.lilith_mark = True
            self.add_status_effect(StatusEffect.LILITH_MARK, 999)
            return "💀 [LILITH'S MARK] The rose tattoo pulses with dark energy — death itself will be cheated once."
        elif effect == "chaos":
            self.chaos_used = True
            self.exhausted = True
            self.exhausted_timer = 3
            self.add_status_effect(StatusEffect.CHAOS, 1)
            self.add_status_effect(StatusEffect.EXHAUSTED, 3)
            # Canon: Staff of Apomyius is PERMANENTLY destroyed — all staff-based resonance
            # abilities are gone forever after CHAOS fires. Only Lilith's Mark (passive)
            # and the shield (Sorath Samekh, which uses his hands not the staff) remain.
            staff_abilities = ['1', '3', '4', '5', '7']  # Palmyra + all Sorath dmg + CHAOS itself
            for key in staff_abilities:
                self.abilities.pop(key, None)
            print("💥 [STAFF DESTROYED] The Staff of Apomyius is consumed! Palmyra, Sorath Vav, Sorath Tau, Sorath Resh, and CHAOS are gone PERMANENTLY.")
            return "🦟 [CHAOS] CHAOS UNLEASHED! A black sphere of annihilation forms! The Staff of Apomyius is consumed, creating a void that erases reality. [TRANSFORMATION: The Staff of Apomyius is consumed, creating a void that erases reality]"
        elif effect == "shield":
            self.defending = True
            self.add_status_effect(StatusEffect.SHIELD, 2, 0.5)
            return "🛡️ [SORATH SAMEKH] The Gates of Hell rise to protect Beelzebub! 50% damage reduction for 2 turns."
        return ""

    def check_lilith_mark(self):
        if self.hp <= 0 and self.lilith_mark and not self.lilith_mark_used:
            self.lilith_mark_used = True
            self.hp = 1
            self.add_status_effect(StatusEffect.LILITH_MARK, 999)
            return "🌹 [LILITH'S MARK] LILITH'S MARK ACTIVATES! Beelzebub cheats death! The rose tattoo blooms, vines reaching out to pull him back from the abyss. [TRANSFORMATION: The rose tattoo blooms, vines reaching out to pull him back from the abyss]"
        return None

    def can_use_ability(self, ability=None):
        if self.exhausted:
            return False, "❌ Beelzebub is exhausted from using CHAOS and cannot act!"
        return True, ""

    def update_status_effects(self):
        super().update_status_effects()
        if self.exhausted_timer > 0:
            self.exhausted_timer -= 1
            if self.exhausted_timer <= 0:
                self.exhausted = False
                print(f"  😫 [EXHAUSTED] {self.name} recovers from exhaustion!")

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "🦟 ORIGINAL SIN: CHAOS",
                "cost": 250,
                "dmg": (700, 900),
                "type": "damage",
                "desc": "🦟 [ORIGINAL SIN] Beelzebub's forbidden technique. He creates a black sphere of absolute annihilation. The Staff of Apomyius consumes itself, creating a void that erases everything it touches. [TRANSFORMATION: The Staff of Apomyius consumes itself, creating a void that erases everything it touches]"
            }
        return self.divine_technique


# ============================================================================
# APOLLO - God of the Sun (FIXED with proper thread mechanics)
# ============================================================================

class Apollo(Character):
    def __init__(self):
        super().__init__(
            "Apollo",
            "God of the Sun • Greek Pantheon",
            1180, 440,
            [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE]
        )
        self.volund_weapon = "Silver Bow & Lyre (銀の弓と竪琴)"
        self.round = 9
        self.affiliation = "Gods"
        self.expectation_bonus = 0
        self.threads_active = False
        self.thread_shield_active = False
        self.next_attack_multiplier = 1.0  # FIXED: Track moonlight

        self.divine_technique = {
            "name": "🎯 ARGYROTOXOS",
            "cost": 190,
            "dmg": (600, 780),
            "type": "damage",
            "desc": "🎯 [ARGYROTOXOS] Apollo's ultimate technique. He launches himself like a silver arrow. Apollo's entire body becomes the arrow, covered in blinding light. [TRANSFORMATION: Apollo's entire body becomes the arrow, covered in blinding light]"
        }

        self.abilities = {
            '1': {"name": "🎯 Silver Bow Shot", "cost": 25, "dmg": (160, 220), "type": "damage",
                  "desc": "🎯 [SILVER BOW SHOT] Apollo fires an arrow of pure light from his silver bow. Light condenses into a physical arrow, moving faster than sound. [TRANSFORMATION: Light condenses into a physical arrow, moving faster than sound]"},
            '2': {"name": "🧵 Threads of Light", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "threads",
                  "desc": "🧵 [THREADS OF LIGHT] Apollo weaves threads of sunlight into invisible snares. Sunbeams become physical threads, weaving traps. [TRANSFORMATION: Sunbeams become physical threads, weaving traps]"},
            '3': {"name": "🎸 Phoebus' Lyre", "cost": 35, "dmg": (0, 0), "type": "buff", "effect": "lyre",
                  "desc": "🎸 [PHOEBUS' LYRE] 'The Shimmering Harp' - Apollo plays his divine lyre, creating melodies that inspire him. Threads transform into boxing bracers. Threads of light form a lyre, music empowering Apollo. [TRANSFORMATION: Threads of light form a lyre, music empowering Apollo]"},
            '4': {"name": "🎯 Artemis Elenchos", "cost": 40, "dmg": (190, 250), "type": "damage", "bind": True,
                  "effect": "bind",
                  "desc": "🎯 [ARTEMIS ELENCHOS] 'Shining Domination' - Apollo wraps his threads around the opponent's limb to immobilize them. Threads of light become unbreakable chains, binding the target's movements. The target cannot move next turn! [TRANSFORMATION: Threads of light become unbreakable chains, binding the target's movements. The target cannot move next turn!]"},
            '5': {"name": "☀️ Embrace of Eternal Midnight Sun", "cost": 60, "dmg": (0, 0), "type": "buff",
                  "effect": "expectations",
                  "desc": "☀️ [EMBRACE OF ETERNAL MIDNIGHT SUN] 'The Sun Shall Never Set on Me' - Apollo basks in the expectations of his fans. Damage +5% each use. Light radiates from Apollo, growing brighter with each expectation. [TRANSFORMATION: Light radiates from Apollo, growing brighter with each expectation]"},
            '6': {"name": "🎯 Apollo Epicurious", "cost": 55, "dmg": (270, 340), "type": "damage",
                  "desc": "🎯 [APOLLO EPICURIOUS] 'Golden Arrows of the Shining Meteor' - A luxurious attack that flows like fine wine. A volley of golden arrows, each one a work of art. [TRANSFORMATION: A volley of golden arrows, each one a work of art]"},
            '7': {"name": "🌙 Moonlight of Artemis", "cost": 80, "dmg": (0, 0), "type": "buff", "effect": "moonlight",
                  "desc": "🌙 [MOONLIGHT OF ARTEMIS] Apollo channels the power of his sister Artemis. Next attack double damage. A giant statue of Artemis rises, moonlight bathing the battlefield. [TRANSFORMATION: A giant statue of Artemis rises, moonlight bathing the battlefield]"},
            '8': {"name": "🛡️ Thread Shield", "cost": 30, "dmg": (0, 0), "type": "defense", "effect": "shield",
                  "desc": "🛡️ [THREAD SHIELD] Apollo weaves threads of light into a defensive barrier. Light threads weave into an impenetrable shield. [TRANSFORMATION: Light threads weave into an impenetrable shield]"},
            '9': {"name": "🎯 Argyrotoxos", "cost": 100, "dmg": (470, 600), "type": "damage",
                  "desc": "🎯 [ARGYROTOXOS] 'Soul-Piercing Silver Arrow' - Apollo transforms into a living arrow of silver light. Apollo himself becomes the arrow, launching at the speed of light. [TRANSFORMATION: Apollo himself becomes the arrow, launching at the speed of light]"}
        }

    def apply_effect(self, effect, target=None):
        if effect == "expectations":
            self.expectation_bonus += 5
            self.add_status_effect(StatusEffect.EXPECTATION, 3, 1.0 + (self.expectation_bonus / 100))
            return f"☀️ [EXPECTATIONS] Expectations fuel Apollo! Damage +{self.expectation_bonus}% [TRANSFORMATION: Light grows brighter as the crowd's expectations rise]"
        elif effect == "moonlight":
            self.next_attack_multiplier = 2.0
            self.add_status_effect(StatusEffect.EMPOWER, 1, 2.0)
            return "🌙 [MOONLIGHT OF ARTEMIS] Moonlight of Artemis summoned! Next attack deals double damage! [TRANSFORMATION: A giant statue of Artemis rises, aiming her bow at the target]"
        elif effect == "shield":
            self.defending = True
            self.thread_shield_active = True
            self.add_status_effect(StatusEffect.THREAD_SHIELD, 1)
            return "🛡️ [THREAD SHIELD] Thread shield created! [TRANSFORMATION: Light threads weave into a protective barrier around Apollo]"
        elif effect == "threads":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.SLOW, 3, 0.7)
            self.threads_active = True
            return "🧵 [THREADS OF LIGHT] Apollo weaves threads of sunlight into invisible snares! Enemy is slowed."
        elif effect == "bind":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.BIND, 1)
            return "🧵 [THREADS OF LIGHT: BIND] Light threads entangle the target completely!"
        elif effect == "lyre":
            self.add_status_effect(StatusEffect.EMPOWER, 3, 1.2)
            return "🎸 [PHOEBUS' LYRE] Apollo's music empowers him! +20% damage for 3 turns."
        return ""

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()

        if self.expectation_bonus > 0:
            expectation_mult = 1.0 + (self.expectation_bonus / 100)
            mult *= expectation_mult
            buffs.append(f"☀️ EXPECTATIONS +{self.expectation_bonus}%")

        if self.next_attack_multiplier > 1.0:
            mult *= self.next_attack_multiplier
            buffs.append("🌙 MOONLIGHT")
            self.next_attack_multiplier = 1.0  # Reset after use

        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "🎯 ARGYROTOXOS",
                "cost": 190,
                "dmg": (600, 780),
                "type": "damage",
                "desc": "🎯 [ARGYROTOXOS] Apollo's ultimate technique. He launches himself like a silver arrow. Apollo's entire body becomes the arrow, covered in blinding light. [TRANSFORMATION: Apollo's entire body becomes the arrow, covered in blinding light]"
            }
        return self.divine_technique


# ============================================================================
# SUSANO'O - God of Storms (FIXED with weapon form bonuses and Musouken effect - no self-damage)
# ============================================================================

class Susanoo(Character):
    def __init__(self):
        super().__init__(
            "Susano'o no Mikoto",
            "God of Storms • Japanese Pantheon",
            1280, 450,
            [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH]
        )
        self.volund_weapon = "Ame-no-Murakumo-no-Tsurugi (天叢雲剣)"
        self.round = 10
        self.affiliation = "Gods"
        self.musouken_used = 0
        self.max_musouken = 2
        self.yatagarasu_form = False
        self.weapon_form = "onikiri"
        self.musouken_active = False
        self.shinra_active = False  # FIXED: tracks active counter-parry state
        self.sword_broken = False  # Musouken unlocks only after sword is shattered

        self.divine_technique = {
            "name": "🌪️ MUSOUKEN: Unarmed Sword",
            "cost": 250,
            "dmg": (700, 900),
            "type": "damage",
            "desc": "🌪️ [MUSOUKEN] Susano'o's ultimate technique. He creates an invisible blade of nothingness that cuts only the INSIDE of the body. Nothingness itself becomes a blade, cutting internal organs while leaving the outside untouched. [TRANSFORMATION: Nothingness itself becomes a blade, cutting internal organs while leaving the outside untouched]"
        }

        self.abilities = {
            '1': {"name": "🌪️ Storm's Wrath", "cost": 30, "dmg": (180, 240), "type": "damage",
                  "desc": "🌪️ [STORM'S WRATH] Susano'o channels the fury of the storm into his strikes. Each blow carries the force of hurricane winds. [TRANSFORMATION: Each blow carries the force of hurricane winds]"},
            '2': {"name": "⚔️ Divine Lightning", "cost": 35, "dmg": (200, 270), "type": "damage",
                  "desc": "⚔️ [DIVINE LIGHTNING] Susano'o calls down lightning from the heavens. Lightning channels through his blade for devastating effect. [TRANSFORMATION: Lightning channels through his blade for devastating effect]"},
            '3': {"name": "👁️ Shinra Yaoyorozu", "cost": 40, "dmg": (0, 0), "type": "buff", "effect": "shinra",
                  "desc": "👁️ [SHINRA YAOYOROZU] 'Divine Myriad' - Susano'o awakens the eight million gods within him. Countless divine spirits manifest around him, ready to counter any sword attack. [TRANSFORMATION: Countless divine spirits manifest around him, ready to counter any sword attack]"},
            '4': {"name": "🌪️ Ama no Magaeshi", "cost": 60, "dmg": (330, 410), "type": "damage",
                  "desc": "🌪️ [AMA NO MAGAESHI] 'Heavenly Demon Counter' - The heavenly reverse - turns opponent's strength against them. Air itself is cut, creating a vacuum blade that flies forward. [TRANSFORMATION: Air itself is cut, creating a vacuum blade that flies forward]"},
            '5': {"name": "🌪️ Ama no Magaeshi: Avici", "cost": 50, "dmg": (290, 360), "type": "damage",
                  "desc": "🌪️ [AMA NO MAGAESHI: AVICI] 'Ceaseless Reverse Heavenly Demon' - A faster but weaker version that sends opponents to the deepest hell. Quicker vacuum blade with reduced power. [TRANSFORMATION: Quicker vacuum blade with reduced power]"},
            '6': {"name": "🌪️ Ama no Magaeshi: Yakumo", "cost": 70, "dmg": (370, 470), "type": "damage",
                  "desc": "🌪️ [AMA NO MAGAESHI: YAKUMO] 'Eight Clouds Reverse Heavenly Demon' - A multi-layered heavenly reverse. Eight clouds of destruction form around the opponent. [TRANSFORMATION: Eight clouds of destruction form around the opponent]"},
            '7': {"name": "⚔️ Musouken", "cost": 150, "dmg": (550, 700), "type": "damage", "invisible": True,
                  "effect": "musouken",
                  "desc": "⚔️ [MUSOUKEN] 'Unarmed Sword' - A desperate last resort unlocked only after Susano'o's sword is shattered. An invisible blade of nothingness that cuts only the inside. Can only be used twice. 🔒 LOCKED until sword is broken. [TRANSFORMATION: Nothingness itself becomes a blade, visible only to those who have reached the peak of swordsmanship]"},
            '8': {"name": "🐦‍⬛ Yatagarasu Form", "cost": 40, "dmg": (0, 0), "type": "buff", "effect": "yatagarasu",
                  "desc": "🐦‍⬛ [YATAGARASU FORM] Susano'o transforms into the three-legged crow Yatagarasu. 80% evasion for 2 turns. Susano'o becomes the divine crow, watching all swordsmen throughout history. [TRANSFORMATION: Susano'o becomes the divine crow, watching all swordsmen throughout history]"},
            '9': {"name": "⚔️ Switch Weapon", "cost": 50, "dmg": (0, 0), "type": "buff", "effect": "switch_weapon",
                  "desc": "⚔️ [SWITCH WEAPON] Susano'o switches between his divine swords. The blade transforms between Onikiri, Ame-no-Murakumo, and Totsuka. Each form provides different combat bonuses. [TRANSFORMATION: The blade transforms between Onikiri, Ame-no-Murakumo, and Totsuka]"}
        }

    def apply_effect(self, effect, target=None):
        if effect == "musouken":
            if not self.sword_broken:
                return "❌ [MUSOUKEN LOCKED] Musouken can only be unleashed after the sword is shattered! Susano'o needs his blade broken to awaken the Unarmed Sword."
            if self.musouken_used < self.max_musouken:
                self.musouken_used += 1
                self.musouken_active = True
                self.add_status_effect(StatusEffect.MUSOUKEN, 1)
                return f"⚔️ [MUSOUKEN] MUSOUKEN ACTIVATED! {self.max_musouken - self.musouken_used} uses remaining [TRANSFORMATION: An invisible blade of nothingness forms - it cuts only the inside, leaving the outside untouched]"
            return "❌ Cannot use Musouken again!"
        elif effect == "yatagarasu":
            self.yatagarasu_form = True
            self.divine_mode = True
            self.divine_timer = 2
            self.add_status_effect(StatusEffect.YATAGARASU, 2)
            self.add_status_effect(StatusEffect.EVASION, 2, 0.8)
            return "🐦‍⬛ [YATAGARASU FORM] SUSANO'O TRANSFORMS INTO YATAGARASU! 80% evasion for 2 turns! [TRANSFORMATION: He becomes the three-legged crow, watching from above]"
        elif effect == "switch_weapon":
            weapons = ["onikiri", "ame-no-murakumo", "totsuka"]
            current_idx = weapons.index(self.weapon_form)
            self.weapon_form = weapons[(current_idx + 1) % 3]
            weapon_names = {"onikiri": "Onikiri (Demon-Slaying Sword) - Balanced form",
                            "ame-no-murakumo": "Ame-no-Murakumo (Heavenly Sword of Gathering Clouds) - +20% damage",
                            "totsuka": "Totsuka (Ten-Hand Sword) - +10% damage, +10% defense"}
            return f"⚔️ [SWITCH] Switched to {weapon_names[self.weapon_form]}! [TRANSFORMATION: The blade's form shifts to a different divine sword]"
        elif effect == "shinra":
            # FIXED: Set shinra_active flag and COUNTER_READY so the game can resolve the parry
            self.shinra_active = True
            self.add_status_effect(StatusEffect.DEFEND, 1)
            self.add_status_effect(StatusEffect.COUNTER_READY, 1)
            return "👁️ [SHINRA YAOYOROZU] Shinra Yaoyorozu activated! Eight million gods stand ready to parry any sword attack! [TRANSFORMATION: Eight million gods manifest around Susano'o, ready to parry]"
        return ""

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()

        weapon_bonuses = {
            "onikiri": 1.0,
            "ame-no-murakumo": 1.2,
            "totsuka": 1.1
        }
        mult *= weapon_bonuses.get(self.weapon_form, 1.0)
        buffs.append(f"⚔️ {self.weapon_form.replace('-', ' ').title()}")

        return mult, buffs

    def update_status_effects(self):
        # FIXED: Reset musouken_active flag when MUSOUKEN status expires
        had_musouken = self.has_status_effect(StatusEffect.MUSOUKEN)
        # FIXED: Reset shinra_active when COUNTER_READY window expires
        had_shinra = self.has_status_effect(StatusEffect.COUNTER_READY)
        super().update_status_effects()
        if had_musouken and not self.has_status_effect(StatusEffect.MUSOUKEN):
            self.musouken_active = False
            print(f"  ⚔️ Susano'o's Musouken fades.")
        if had_shinra and not self.has_status_effect(StatusEffect.COUNTER_READY):
            self.shinra_active = False
            print(f"  👁️ Shinra Yaoyorozu — counter window closes.")

    def take_damage(self, dmg, ignore_defense=False):
        actual_damage = super().take_damage(dmg, ignore_defense)
        if not self.sword_broken and actual_damage >= 200:
            self.sword_broken = True
            print(f"  ⚔️ [SWORD SHATTERED] Susano'o's divine sword is destroyed! MUSOUKEN UNLOCKED — the Unarmed Sword awakens from desperation!")
        return actual_damage

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "🌪️ MUSOUKEN: Unarmed Sword",
                "cost": 250,
                "dmg": (700, 900),
                "type": "damage",
                "desc": "🌪️ [MUSOUKEN] Susano'o's ultimate technique. He creates an invisible blade of nothingness that cuts only the INSIDE of the body. Nothingness itself becomes a blade, cutting internal organs while leaving the outside untouched. [TRANSFORMATION: Nothingness itself becomes a blade, cutting internal organs while leaving the outside untouched]"
            }
        return self.divine_technique


# ============================================================================
# LOKI - God of Mischief (FIXED with clone combat and clone targeting)
# ============================================================================

class Loki(Character):
    def __init__(self):
        super().__init__(
            "Loki",
            "God of Mischief • Norse Pantheon",
            1220, 440,
            [Realm.GODLY_TECHNIQUE]
        )
        self.volund_weapon = "Svartálfaheimr Ring (スヴァルトアルフヘイムの指輪)"
        self.round = 11
        self.affiliation = "Gods"
        self.clones = []
        self.max_clones = 5
        self.perfect_clone = None
        self.andvaranaut_active = False
        self.shared_vision = False

        self.divine_technique = {
            "name": "🎭 HEIMSKRINGLA: Endurlífa",
            "cost": 200,
            "dmg": (550, 700),
            "type": "damage",
            "desc": (
                "🎭 [HEIMSKRINGLA] Loki's ultimate trick. He creates a perfect clone and can swap "
                "positions at will. Reality itself bends as Loki creates an indistinguishable copy, "
                "then swaps places through space. ALL active clones attack simultaneously on the "
                "same turn. [TRANSFORMATION: Reality itself bends as Loki creates an "
                "indistinguishable copy, then swaps places through space]"
            )
        }

        self.abilities = {
            '1': {
                "name": "🎭 Illusion Strike", "cost": 25, "dmg": (150, 210), "type": "damage",
                "desc": (
                    "🎭 [ILLUSION STRIKE] Loki strikes from behind an illusion. An illusion of Loki "
                    "distracts while the real one attacks from behind. [TRANSFORMATION: An illusion "
                    "of Loki distracts while the real one attacks from behind]"
                )
            },
            '2': {
                "name": "🎭 Shapeshift", "cost": 30, "dmg": (0, 0), "type": "buff",
                "effect": "shapeshift",
                "desc": (
                    "🎭 [SHAPESHIFT] Loki shifts his form, becoming harder to predict. Loki's "
                    "appearance flickers between forms, confusing enemies. [TRANSFORMATION: "
                    "Loki's appearance flickers between forms, confusing enemies]"
                )
            },
            '3': {
                "name": "🔗 Dual-Chained Hooks", "cost": 35, "dmg": (190, 260), "type": "damage",
                "desc": (
                    "🔗 [DUAL-CHAINED HOOKS] Loki throws his chained hooks, binding opponents. "
                    "Chains extend from his palms, seeking targets. [TRANSFORMATION: Chains "
                    "extend from his palms, seeking targets]"
                )
            },
            '4': {
                "name": "🔄 Heimskringla: Copy", "cost": 40, "dmg": (0, 0), "type": "clone",
                "effect": "copy",
                "desc": (
                    "🔄 [HEIMSKRINGLA: COPY] Loki creates a copy of himself. Dark mist coalesces "
                    "into an identical copy. Each copy fights autonomously and adds bonus damage "
                    "to Trickster's Gambit. [TRANSFORMATION: Dark mist coalesces into an "
                    "identical copy]"
                )
            },
            '5': {
                "name": "👤 Hveðrung", "cost": 60, "dmg": (0, 0), "type": "clone",
                "effect": "hvedrung",
                "desc": (
                    "👤 [HVEÐRUNG] 'False Divine Shadow' - Loki creates a PERFECT clone that "
                    "shares his full power, personality, and knowledge. This clone deals 100% "
                    "damage and attacks alongside Loki during Trickster's Gambit. Dark mist "
                    "from Loki's palm coalesces into an indistinguishable duplicate — same "
                    "power, same mind, same will. [TRANSFORMATION: Dark mist from Loki's palm "
                    "coalesces into an indistinguishable duplicate]"
                )
            },
            '6': {
                "name": "👁️ Níu Heimr Auga", "cost": 35, "dmg": (0, 0), "type": "buff",
                "effect": "share_vision",
                "desc": (
                    "👁️ [NÍU HEIMR AUGA] 'Peephole of the Nine Worlds' - Loki shares his vision "
                    "with all clones. When active, clone attacks during Trickster's Gambit each "
                    "gain +20% damage. His pupils visibly dilate as he sees through every clone's "
                    "eyes simultaneously. [TRANSFORMATION: Nine realms of vision merge]"
                )
            },
            '7': {
                "name": "🔄 Endurlífa", "cost": 50, "dmg": (0, 0), "type": "utility",
                "effect": "endurlifa",
                "desc": (
                    "🔄 [ENDURLÍFA] 'Gate of Resurrection' - Loki instantly swaps positions with "
                    "any of his clones. The target copy dissolves in the process. Space itself "
                    "warps — Loki and his clone exchange places through a dimensional gate. "
                    "[TRANSFORMATION: Space itself warps — Loki and his clone exchange places]"
                )
            },
            '8': {
                "name": "💍 Andvaranaut", "cost": 80, "dmg": (0, 0), "type": "buff",
                "effect": "andvaranaut",
                "desc": (
                    "💍 [ANDVARANAUT] 'Ring of Proliferation' - Loki activates the cursed ring "
                    "Andvaranaut, removing his clone limit for 3 turns. The silver ring glows "
                    "with cursed power, removing all limits on cloning. [TRANSFORMATION: "
                    "The silver ring glows with cursed power, removing all limits on cloning]"
                )
            },
            '9': {
                "name": "🎭 Trickster's Gambit", "cost": 70, "dmg": (330, 410), "type": "damage",
                "effect": "gambit",
                "desc": (
                    "🎭 [TRICKSTER'S GAMBIT] Loki's ultimate trick — he attacks from one direction "
                    "while every active clone strikes from a different direction simultaneously. "
                    "Base damage from Loki himself, PLUS each clone rolls independent damage "
                    "scaled by its power level. Perfect clones deal full damage. Multiple Lokis "
                    "appear from all directions at once — the true terror of the God of Mischief. "
                    "[TRANSFORMATION: Multiple Lokis appear from all directions simultaneously]"
                )
            },
            '10': {
                "name": "🛡️ Shield of Skuld", "cost": 35, "dmg": (0, 0), "type": "defense",
                "effect": "shield",
                "desc": (
                    "🛡️ [SHIELD OF SKULD] Loki conjures a piece of stone wall with an ornate "
                    "wooden door. Created by Heimskringla, it can halt even powerful piercing "
                    "attacks for a few seconds. Dark mist from Loki's palm solidifies into an "
                    "ancient stone barrier — the door of fate itself blocks the attack. "
                    "[TRANSFORMATION: Dark mist solidifies into an ancient stone barrier]"
                )
            },
        }

    # ------------------------------------------------------------------
    # apply_effect — handles all buff/utility effects
    # ------------------------------------------------------------------
    def apply_effect(self, effect, target=None):
        if effect == "copy":
            if len(self.clones) < self.max_clones or self.andvaranaut_active:
                # Power scales down with each additional clone
                base_power = max(10, 100 // (len(self.clones) + 2))
                damage_mult = base_power / 100.0
                clone_data = {
                    "power": base_power,
                    "active": True,
                    "hp": 100,
                    "max_hp": 100,
                    "damage_mult": damage_mult,
                    "perfect": False,
                }
                self.clones.append(clone_data)
                self.add_status_effect(StatusEffect.CLONE, 1, stacks=len(self.clones))
                pct = int(damage_mult * 100)
                return (
                    f"✅ [CLONE] Clone {len(self.clones)} created! "
                    f"Total clones: {len(self.clones)} — each deals {pct}% damage. "
                    "[TRANSFORMATION: Dark mist from Loki's palm forms a copy]"
                )
            return "❌ Maximum clones reached!"

        elif effect == "hvedrung":
            if len(self.clones) < self.max_clones or self.andvaranaut_active:
                self.perfect_clone = {
                    "power": 100,
                    "active": True,
                    "hp": 200,
                    "max_hp": 200,
                    "damage_mult": 1.0,
                    "perfect": True,
                }
                self.clones.append(self.perfect_clone)
                self.add_status_effect(StatusEffect.PERFECT_CLONE, 999)
                return (
                    f"✅ [PERFECT CLONE] Hveðrung — a PERFECT clone created! "
                    f"Deals 100% damage alongside Loki. Total clones: {len(self.clones)}. "
                    "[TRANSFORMATION: A perfect duplicate emerges, sharing Loki's full power]"
                )
            return "❌ Maximum clones reached!"

        elif effect == "gambit":
            # NOTE: The base damage roll is handled in use_ability() as a normal damage ability.
            # This effect fires AFTER the base hit to add clone contributions.
            return self._execute_clone_attacks()

        elif effect == "share_vision":
            self.shared_vision = True
            self.add_status_effect(StatusEffect.SHARED_VISION, 3)
            return (
                "👁️ [SHARED VISION] Vision shared with all clones for 3 turns! "
                "Clone attacks during Trickster's Gambit gain +20% damage. "
                "[TRANSFORMATION: Loki's eyes glow as he sees through every clone simultaneously]"
            )

        elif effect == "endurlifa":
            active = [c for c in self.clones if c.get("active")]
            if active:
                self.add_status_effect(StatusEffect.TELEPORT, 1)
                self.add_status_effect(StatusEffect.EVASION, 1, 0.9)
                # Remove one clone (it dissolved in the swap)
                clone = random.choice(active)
                clone["active"] = False
                self.clones = [c for c in self.clones if c.get("active")]
                return (
                    "🔄 [SWAP] Loki swaps positions with a clone! 90% evasion this turn. "
                    "[TRANSFORMATION: Loki and his clone instantaneously exchange places]"
                )
            return "❌ No clones to swap with!"

        elif effect == "andvaranaut":
            self.andvaranaut_active = True
            self.add_status_effect(StatusEffect.ANDVARANAUT, 3)
            self.add_status_effect(StatusEffect.CLONE_LIMIT, 3)
            return (
                "💍 [ANDVARANAUT] Andvaranaut activated! Clone limit removed for 3 turns! "
                "[TRANSFORMATION: The silver ring multiplies, its cursed power breaking all limits]"
            )

        elif effect == "shapeshift":
            self.add_status_effect(StatusEffect.EVASION, 2, 0.3)
            return "🎭 [SHAPESHIFT] Loki's form flickers, making him harder to hit! (+30% evasion, 2 turns)"

        elif effect == "shield":
            self.defending = True
            self.add_status_effect(StatusEffect.SHIELD, 1, 0.7)
            self.add_status_effect(StatusEffect.EVASION, 1, 0.3)
            return (
                "🛡️ [SHIELD OF SKULD] An ancient stone barrier rises to protect Loki! "
                "(50% damage reduction + 30% evasion)"
            )

        return ""

    # ------------------------------------------------------------------
    # _execute_clone_attacks — called from gambit effect
    # ------------------------------------------------------------------
    def _execute_clone_attacks(self):
        """
        Each active clone attacks the same target that Loki just hit.
        Damage per clone = randint(80,120) * clone["damage_mult"]
        Perfect clones get the full multiplier (1.0).
        Shared vision adds +20% per clone.
        Returns a summary string.
        """
        active_clones = [c for c in self.clones if c.get("active")]
        if not active_clones:
            return ""  # No clones — only Loki's base hit landed.

        lines = []
        vision_bonus = 1.2 if self.shared_vision else 1.0

        # We need the current enemy target. Retrieve from self.enemies if available.
        # (battle() sets self.enemies before use_ability is called.)
        targets = []
        if hasattr(self, '_last_gambit_target') and self._last_gambit_target:
            targets = [self._last_gambit_target]

        if not targets:
            return (
                f"  👥 [{len(active_clones)} clones ready but no target stored — "
                "call _set_gambit_target(target) before triggering gambit effect]"
            )

        target = targets[0]
        total_clone_dmg = 0

        for i, clone in enumerate(active_clones):
            base = random.randint(80, 120)
            dmg = int(base * clone["damage_mult"] * vision_bonus)
            dmg = max(5, dmg)
            target.take_damage(dmg)
            total_clone_dmg += dmg
            label = "👤 PERFECT CLONE" if clone.get("perfect") else f"👥 Clone {i + 1}"
            pct = int(clone["damage_mult"] * 100)
            lines.append(f"  {label} ({pct}% power) hits for {dmg} damage!")

        vision_note = " [+20% from Shared Vision]" if self.shared_vision else ""
        lines.append(
            f"  🎭 [CLONE TOTAL] All clones dealt {total_clone_dmg} bonus damage!{vision_note}"
        )
        return "\n".join(lines)

    def _set_gambit_target(self, target):
        """Store the target so _execute_clone_attacks can reference it."""
        self._last_gambit_target = target

    # ------------------------------------------------------------------
    # clone_attack — autonomous attacks (called from battle loop)
    # ------------------------------------------------------------------
    def clone_attack(self, clone_index, target):
        if clone_index < len(self.clones) and self.clones[clone_index]["active"]:
            clone = self.clones[clone_index]
            base_damage = random.randint(80, 120)
            damage = int(base_damage * clone["damage_mult"])
            damage = max(10, damage)
            target.take_damage(damage)
            label = "👤 Perfect Clone" if clone.get("perfect") else f"👥 Clone {clone_index + 1}"
            pct = int(clone["damage_mult"] * 100)
            print(f"  {label} ({pct}% power) attacks for {damage} damage!")
            return True
        return False

    # ------------------------------------------------------------------
    # clone_take_damage
    # ------------------------------------------------------------------
    def clone_take_damage(self, clone_index, damage):
        if clone_index < len(self.clones) and self.clones[clone_index]["active"]:
            clone = self.clones[clone_index]
            clone["hp"] -= damage
            label = "Perfect Clone" if clone.get("perfect") else f"Clone {clone_index + 1}"
            print(f"  👥 {label} takes {damage} damage! (HP: {clone['hp']}/{clone['max_hp']})")
            if clone["hp"] <= 0:
                clone["active"] = False
                self.clones = [c for c in self.clones if c.get("active")]
                # Remove perfect_clone reference if it was the one destroyed
                if clone.get("perfect") and self.perfect_clone is clone:
                    self.perfect_clone = None
                    self.remove_status_effect(StatusEffect.PERFECT_CLONE)
                # Sync CLONE count status
                self.remove_status_effect(StatusEffect.CLONE)
                if self.clones:
                    self.add_status_effect(StatusEffect.CLONE, 999, stacks=len(self.clones))
                print(f"  💥 {label} is destroyed!")
            return True
        return False

    # ------------------------------------------------------------------
    # get_damage_multiplier — clone bonus for ALL player attacks
    # ------------------------------------------------------------------
    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()
        active_clones = [c for c in self.clones if c.get("active")]
        if active_clones:
            # Ambient intimidation bonus — not the direct attack bonus (that's in gambit)
            clone_bonus = sum(c.get("damage_mult", 0) * 0.3 for c in active_clones)
            mult *= (1.0 + clone_bonus)
            perfect_count = sum(1 for c in active_clones if c.get("perfect"))
            normal_count = len(active_clones) - perfect_count
            clone_desc = []
            if perfect_count:
                clone_desc.append(f"{perfect_count}✦")
            if normal_count:
                clone_desc.append(f"{normal_count}◆")
            buffs.append(f"👥 CLONES {''.join(clone_desc)} (+{int(clone_bonus*100)}%)")
        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "🎭 HEIMSKRINGLA: Endurlífa",
                "cost": 200,
                "dmg": (550, 700),
                "type": "damage",
                "desc": (
                    "🎭 [HEIMSKRINGLA] Loki's ultimate trick. He creates a perfect clone and can "
                    "swap positions at will. ALL active clones attack the same target simultaneously. "
                    "[TRANSFORMATION: Reality itself bends as Loki creates an indistinguishable copy]"
                )
            }
        return self.divine_technique

    def update_status_effects(self):
        """Override to reset Loki's flag state when timed statuses expire."""
        had_andvaranaut = self.has_status_effect(StatusEffect.ANDVARANAUT)
        had_shared_vision = self.has_status_effect(StatusEffect.SHARED_VISION)

        super().update_status_effects()

        # Reset flags if their associated status effect just expired
        if had_andvaranaut and not self.has_status_effect(StatusEffect.ANDVARANAUT):
            self.andvaranaut_active = False
            print("  💍 Andvaranaut's power fades — clone limit restored.")
        if had_shared_vision and not self.has_status_effect(StatusEffect.SHARED_VISION):
            self.shared_vision = False
            print("  👁️ Shared Vision fades — clone bonus vision gone.")


# ============================================================================
# PATCH: use_ability() — wire gambit target storage
# ============================================================================
# In RagnarokGame.use_ability(), find the block that handles ability type "damage"
# and ADD these two lines just before calling apply_effect for Loki's gambit:
#
#   # Store target for clone attacks (Loki's Trickster's Gambit)
#   if character.name == "Loki" and ability.get("effect") == "gambit":
#       if hasattr(character, '_set_gambit_target'):
#           character._set_gambit_target(target)
#
# The full diff for that section looks like:
#
#   if ability.get("type") == "damage":
#       target = self.select_target()
#       if target:
#           ...
#           # [ADD THESE 3 LINES]
#           if character.name == "Loki" and ability.get("effect") == "gambit":
#               if hasattr(character, '_set_gambit_target'):
#                   character._set_gambit_target(target)
#           # [END ADD]
#           if "effect" in ability and ability["effect"] not in ["bind"]:
#               if hasattr(character, 'apply_effect'):
#                   result = character.apply_effect(ability["effect"])
#                   if result:
#                       print_ability_result(result)


# ============================================================================
# ODIN - All-Father (COMPLETE: All 18 Cursed Hymns implemented)
# ============================================================================


class Odin(Character):
    def __init__(self):
        super().__init__(
            "Odin",
            "All-Father • Norse Pantheon",
            1500, 520,
            [Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL]
        )
        self.volund_weapon = "Gungnir — Spear of Destiny (グングニル)"
        self.round = 12
        self.affiliation = "Gods"
        self.form = "Old"
        self.life_theft_active = False
        self.active_treasures = set()  # Multiple treasures can be active simultaneously
        self.treasure_timers = {}   # Per-treasure timers {name: turns_remaining}
        self.yggdrasil_awakening = False  # All 4 treasures at once
        self.drain_timer = 0

        self.divine_technique = {
            "name": "🔱 GUNGNIR: Absolute Certainty",
            "cost": 220,
            "dmg": (650, 850),
            "type": "damage",
            "desc": (
                "🔱 [GUNGNIR] Odin throws Gungnir, the spear that never misses. The spear's "
                "trajectory is absolute and unavoidable. Gungnir becomes one with fate itself "
                "— once thrown, it WILL hit its target no matter what. "
                "[TRANSFORMATION: Gungnir becomes one with fate itself]"
            )
        }

        self.abilities = {
            # ── Combat ──────────────────────────────────────────────────
            '1': {
                "name": "🔱 Gungnir Thrust", "cost": 35, "dmg": (200, 270), "type": "damage",
                "desc": (
                    "🔱 [GUNGNIR THRUST] A thrust of the legendary spear Gungnir. "
                    "The spear of destiny manifests in Odin's hand, its aim true. "
                    "[TRANSFORMATION: The spear of destiny manifests in Odin's hand, its aim true]"
                )
            },
            # ── Ravens ──────────────────────────────────────────────────
            '2': {
                "name": "🐦‍⬛ Huginn's Sight", "cost": 30, "dmg": (0, 0), "type": "buff",
                "effect": "huginn",
                "desc": (
                    "🐦‍⬛ [HUGINN'S SIGHT] Odin sends Huginn (Thought) across the battlefield. "
                    "50% dodge next turn. Thought itself becomes a raven, revealing enemy movements. "
                    "[TRANSFORMATION: Thought itself becomes a raven, revealing enemy movements]"
                )
            },
            '3': {
                "name": "🐦‍⬛ Muninn's Memory", "cost": 30, "dmg": (0, 0), "type": "buff",
                "effect": "muninn",
                "desc": (
                    "🐦‍⬛ [MUNINN'S MEMORY] Odin sends Muninn (Memory) through time. "
                    "Next attack deals double damage. Memory becomes a raven, "
                    "recalling enemy weaknesses from the past. "
                    "[TRANSFORMATION: Memory becomes a raven, recalling past weaknesses]"
                )
            },
            # ── 18 Cursed Hymns (Galder) ─────────────────────────────────
            # Hymn 1 — binding
            '4': {
                "name": "🔮 1st Galder: Ljóðatal", "cost": 30, "dmg": (160, 220), "type": "damage",
                "effect": "hymn_bind",
                "desc": (
                    "🔮 [1ST GALDER: LJÓÐATAL] 'Song of Songs' — The first hymn, the mother of "
                    "all runes. Dark runes form chains of language that bind opponents. "
                    "The target is slowed for 1 turn. "
                    "[TRANSFORMATION: Runes of the oldest language crystallise into chains]"
                )
            },
            # Hymn 2 — healing
            '5': {
                "name": "🔮 2nd Galder: Lyfjaberg", "cost": 35, "dmg": (0, 0), "type": "heal",
                "effect": "hymn_heal",
                "desc": (
                    "🔮 [2ND GALDER: LYFJABERG] 'Healing Mountain' — The second hymn calls "
                    "on the healing magic of Menglöð. Restores 120 HP. "
                    "[TRANSFORMATION: Golden runes flow across Odin's wounds, knitting them shut]"
                )
            },
            # Hymn 3 — shackle (bind)
            '6': {
                "name": "🔮 3rd Galder: Þjóðvitni", "cost": 40, "dmg": (190, 260), "type": "damage",
                "effect": "hymn_shackle",
                "desc": (
                    "🔮 [3RD GALDER: ÞJÓÐVITNI] 'Folk-Wolf' — The third hymn summons spectral "
                    "chains from the World Tree. The target is bound for 1 turn and takes "
                    "ongoing rune-damage. "
                    "[TRANSFORMATION: Yggdrasil's roots manifest as spectral chains]"
                )
            },
            # Hymn 4 — fire rune
            '7': {
                "name": "🔮 4th Galder: Fýrisvellir", "cost": 45, "dmg": (240, 310), "type": "damage",
                "effect": "hymn_fire",
                "desc": (
                    "🔮 [4TH GALDER: FÝRISVELLIR] 'Field of Fire' — The fourth hymn ignites "
                    "the battlefield with rune-fire. Applies BURN status for 3 turns. "
                    "[TRANSFORMATION: The Isa rune shatters, releasing trapped fire-energy]"
                )
            },
            # Hymn 5 — Fafnir (existing, moved to key '8')
            '8': {
                "name": "🔮 5th Galder: Fafnir", "cost": 60, "dmg": (330, 410), "type": "damage",
                "desc": (
                    "🔮 [5TH GALDER: FAFNIR] 'Divine Ring Barrier' — Odin channels the greed "
                    "and power of the dragon Fafnir. Dragon energy coalesces, striking with "
                    "avaricious fury. "
                    "[TRANSFORMATION: Dragon energy coalesces, striking with avaricious fury]"
                )
            },
            # Hymn 6 — Hel Víta (existing, moved to key '9')
            '9': {
                "name": "🔮 6th Galder: Hel Víta", "cost": 45, "dmg": (240, 320), "type": "damage",
                "effect": "hymn_hel_vita",
                "desc": (
                    "🔮 [6TH GALDER: HEL VÍTA] 'Shockwave of the Dead' — Odin lifts the opponent off the ground with a "
                    "devastating impact before releasing a concussive shockwave that sends them crashing into the arena walls. "
                    "Powerful enough to hurl a giant across the battlefield. STUN applied on hit. "
                    "[TRANSFORMATION: The opponent is lifted airborne — then flung backward by a divine shockwave]"
                )
            },
            # Hymn 7 — frost rune
            '10': {
                "name": "🔮 7th Galder: Niflheimr", "cost": 50, "dmg": (270, 350), "type": "damage",
                "effect": "hymn_frost",
                "desc": (
                    "🔮 [7TH GALDER: NIFLHEIMR] 'World of Mist' — The seventh hymn draws power "
                    "from Niflheim, the primordial realm of ice. Applies FROST status for 2 turns "
                    "and reduces enemy energy by 20. "
                    "[TRANSFORMATION: Primordial ice crystalises around the Hagalaz rune]"
                )
            },
            # Hymn 8 — knowledge rune (empower self)
            '11': {
                "name": "🔮 8th Galder: Mímisbrunnr", "cost": 55, "dmg": (0, 0), "type": "buff",
                "effect": "hymn_knowledge",
                "desc": (
                    "🔮 [8TH GALDER: MÍMISBRUNNR] 'Well of Wisdom' — The eighth hymn recreates "
                    "Odin's sacrifice at the Well of Mimir. +40% damage for 2 turns. "
                    "He paid with an eye for this wisdom — the rune glows in its socket. "
                    "[TRANSFORMATION: The Ansuz rune blazes — Odin's sacrificed eye burns with "
                    "divine understanding]"
                )
            },
            # Hymn 9 — Vindsskuggr (existing, moved to key '12')
            '12': {
                "name": "🔮 9th Galder: Vindsskuggr", "cost": 70, "dmg": (370, 470), "type": "damage",
                "desc": (
                    "🔮 [9TH GALDER: VINDSSKUGGR] 'Whirling Shadow Wind Fang' — The ninth "
                    "cursed hymn. Odin summons blades of darkness. Shadows of the wind become "
                    "physical blades. "
                    "[TRANSFORMATION: Shadows of the wind become physical blades]"
                )
            },
            # Hymn 10 — curse (weaken enemy)
            '13': {
                "name": "🔮 10th Galder: Galdralag", "cost": 65, "dmg": (300, 390), "type": "damage",
                "effect": "hymn_curse",
                "desc": (
                    "🔮 [10TH GALDER: GALDRALAG] 'Incantation Metre' — The tenth hymn layers "
                    "curse upon curse. Applies WEAKEN status reducing enemy damage by 30% "
                    "for 2 turns. "
                    "[TRANSFORMATION: Runic syllables stack into a lattice of debilitation]"
                )
            },
            # Hymn 11 — life drain (passive aura, active trigger)
            '14': {
                "name": "🔮 11th Galder: Sigrdrífumál", "cost": 70, "dmg": (340, 430), "type": "damage",
                "effect": "hymn_victory",
                "desc": (
                    "🔮 [11TH GALDER: SIGRDRÍFUMÁL] 'Victory Speech' — The eleventh hymn, "
                    "the speech that Sigrdrífa gave to Sigurd. Empowers Odin with victory "
                    "runes — deals damage and grants EMPOWER (+30%) for 1 turn. "
                    "[TRANSFORMATION: Victory runes blaze gold across Odin's spear arm]"
                )
            },
            # Hymn 12 — illusion / confusion
            '15': {
                "name": "🔮 12th Galder: Fjölsvinnsmál", "cost": 60, "dmg": (0, 0), "type": "utility",
                "effect": "hymn_illusion",
                "desc": (
                    "🔮 [12TH GALDER: FJÖLSVINNSMÁL] 'Words of Great Wisdom' — The twelfth "
                    "hymn shrouds Odin in illusion. Grants 60% evasion for 1 turn and "
                    "BLINDS the enemy for 1 turn. "
                    "[TRANSFORMATION: Odin's form fractures into twelve simultaneous afterimages]"
                )
            },
            # Hymn 13 — rune shield
            '16': {
                "name": "🔮 13th Galder: Rígsþula", "cost": 65, "dmg": (0, 0), "type": "defense",
                "effect": "hymn_rune_shield",
                "desc": (
                    "🔮 [13TH GALDER: RÍGSÞULA] 'Song of Ríg' — The thirteenth hymn, the "
                    "rune of the divine ancestor. Odin manifests a rune-shield absorbing the "
                    "next hit entirely (once). Applies SHIELD (0 damage once) for 1 turn. "
                    "[TRANSFORMATION: A perfect circle of runes forms around Odin, "
                    "absorbing all incoming force]"
                )
            },
            # Hymn 14 — summon wolves
            '17': {
                "name": "🔮 14th Galder: Geri Freki", "cost": 75, "dmg": (380, 480), "type": "damage",
                "effect": "hymn_wolves",
                "desc": (
                    "🔮 [14TH GALDER: GERI FREKI] 'Greedy & Ravenous' — The fourteenth hymn "
                    "summons Odin's wolves Geri and Freki as spectral constructs. Multi-hit: "
                    "two separate bites for split damage. Applies BLEED for 2 turns. "
                    "[TRANSFORMATION: Two spectral wolves solidify from Odin's shadow]"
                )
            },
            # Hymn 15 — death curse
            '18': {
                "name": "🔮 15th Galder: Vafþrúðnismál", "cost": 80, "dmg": (420, 530), "type": "damage",
                "effect": "hymn_death",
                "desc": (
                    "🔮 [15TH GALDER: VAFÞRÚÐNISMÁL] 'Words of Vafþrúðnir' — The fifteenth "
                    "hymn recalls Odin's wisdom-contest with the giant. Deals heavy damage and "
                    "has a 20% chance to instantly STUN for 2 turns. "
                    "[TRANSFORMATION: The Dagaz rune — dawn and dusk simultaneously — "
                    "detonates in the target's chest]"
                )
            },
            # Hymn 16 — world tree drain
            '19': {
                "name": "🔮 16th Galder: Yggdrasil", "cost": 90, "dmg": (460, 580), "type": "damage",
                "effect": "hymn_world_tree",
                "desc": (
                    "🔮 [16TH GALDER: YGGDRASIL] 'World Tree' — The sixteenth hymn channels "
                    "the life-force of Yggdrasil itself. Deals damage AND heals Odin for "
                    "50% of damage dealt. "
                    "[TRANSFORMATION: The Eihwaz rune — the axis of the world — "
                    "tears life-energy from the target and feeds it to Odin]"
                )
            },
            # Hymn 17 — Ragnarök foretelling (massive nuke, self-damage)
            '20': {
                "name": "🔮 17th Galder: Völuspá", "cost": 120, "dmg": (500, 650), "type": "damage",
                "effect": "hymn_ragnarok",
                "desc": (
                    "🔮 [17TH GALDER: VÖLUSPÁ] 'Prophecy of the Völva' — The seventeenth hymn "
                    "recites the end of the world. Odin channels the destruction of Ragnarök "
                    "into a single strike. Ignores all defenses. Odin takes 40 recoil damage. "
                    "[TRANSFORMATION: Every rune Odin knows blazes simultaneously — "
                    "the Wyrd of all things flows through him]"
                )
            },
            # Hymn 18 — the unknowable hymn
            '21': {
                "name": "🔮 18th Galder: The Unknowable", "cost": 150, "dmg": (550, 700), "type": "damage",
                "effect": "hymn_unknowable",
                "desc": (
                    "🔮 [18TH GALDER: THE UNKNOWABLE] The eighteenth and final hymn — Odin "
                    "refuses to reveal its name. He says: 'I alone know it, and I will carry "
                    "it to the grave.' Whatever it does, it has never been witnessed by anyone "
                    "who survived. Ignores all defenses. Applies WEAKEN + BLIND + SLOW "
                    "simultaneously. "
                    "[TRANSFORMATION: All known runes go dark. Something older takes their place.]"
                )
            },
            # ── Life Theft ───────────────────────────────────────────────
            '22': {
                "name": "🌿 Life Theft", "cost": 40, "dmg": (0, 0), "type": "buff",
                "effect": "life_theft",
                "desc": (
                    "🌿 [LIFE THEFT] Odin drains the life energy from all enemies for 3 turns. "
                    "A dark aura extends from Odin, siphoning vitality. "
                    "[TRANSFORMATION: A dark aura extends from Odin, siphoning vitality]"
                )
            },
            # ── Matter Manipulation ──────────────────────────────────────
            '23': {
                "name": "✨ Matter Manipulation", "cost": 40, "dmg": (0, 0), "type": "buff",
                "effect": "matter",
                "desc": (
                    "✨ [MATTER MANIPULATION] Odin shapes reality around him. Next attack "
                    "ignores defenses. Reality bends to Odin's will — matter itself obeys "
                    "his command. The crystal ornament Gungnir reshapes into its spear form. "
                    "[TRANSFORMATION: Reality bends to Odin's will]"
                )
            },
            # ── Treasures ────────────────────────────────────────────────
            '24': {
                "name": "🗡️ Manifest Gram", "cost": 50, "dmg": (0, 0), "type": "buff",
                "effect": "gram",
                "desc": (
                    "🗡️ [MANIFEST GRAM] Odin manifests Gram, the legendary sword of Sigurd. "
                    "+50% damage for 3 turns. The sword containing the soul of the Primordial "
                    "Odin materializes from his flesh. "
                    "[TRANSFORMATION: The blade materializes from his flesh]"
                )
            },
            '25': {
                "name": "💍 Manifest Draupnir", "cost": 50, "dmg": (0, 0), "type": "buff",
                "effect": "draupnir",
                "desc": (
                    "💍 [MANIFEST DRAUPNIR] Odin manifests Draupnir, the self-multiplying ring. "
                    "The ring of Chaos multiplies endlessly, each duplicate a weapon. "
                    "[TRANSFORMATION: The ring multiplies endlessly]"
                )
            },
            '26': {
                "name": "⛑️ Manifest Egil", "cost": 50, "dmg": (0, 0), "type": "buff",
                "effect": "egil",
                "desc": (
                    "⛑️ [MANIFEST EGIL] Odin manifests the helmet Egil, focusing dark energy. "
                    "The helmet of Satan forms, dark energy concentrating. "
                    "[TRANSFORMATION: The helmet of Satan forms]"
                )
            },
            '27': {
                "name": "📿 Manifest Brisingamen", "cost": 50, "dmg": (0, 0), "type": "buff",
                "effect": "brisingamen",
                "desc": (
                    "📿 [MANIFEST BRISINGAMEN] Odin manifests the necklace Brisingamen, "
                    "channeling frost. The necklace of Ymir appears, radiating primordial cold. "
                    "[TRANSFORMATION: Ancient frost radiates from the divine necklace]"
                )
            },
            # ── Battle Form ──────────────────────────────────────────────
            '28': {
                "name": "👤 Battle Form", "cost": 80, "dmg": (0, 0), "type": "buff",
                "effect": "battle_form",
                "desc": (
                    "👤 [BATTLE FORM] Odin's true warrior form — his aged facade disintegrates "
                    "to ash, revealing the young god beneath. Black hair with white accents, "
                    "six marks around his eye crackling with power. Gods and humans tremble "
                    "before this sacred, inviolable form. "
                    "[TRANSFORMATION: The Supreme God sheds his mortal guise]"
                )
            },
            # ── Ultimate Gungnir ─────────────────────────────────────────
            '29': {
                "name": "🔱 Gungnir: Absolute Certainty", "cost": 150, "dmg": (550, 700),
                "type": "damage",
                "desc": (
                    "🔱 [GUNGNIR: ABSOLUTE CERTAINTY] Odin throws Gungnir with absolute certainty. "
                    "Gungnir becomes one with fate — its trajectory is absolute. "
                    "[TRANSFORMATION: Gungnir becomes one with fate]"
                )
            },
            # ── Passives ─────────────────────────────────────────────────
            '30': {
                "name": "🌿 Life Theft/Decay", "cost": 0, "dmg": (0, 0), "type": "passive",
                "desc": (
                    "🌿 [LIFE THEFT/DECAY] When Odin experiences strong emotions, nearby life "
                    "withers and dies. Passive aura drains 5 HP from all enemies each turn "
                    "when Odin's excitement rises. "
                    "[TRANSFORMATION: Divine excitement causes flowers to wilt]"
                )
            },
            '31': {
                "name": "📿 18 Cursed Hymns", "cost": 0, "dmg": (0, 0), "type": "passive",
                "desc": (
                    "📿 [18 GALDER] Odin knows all 18 runic hymns consisting of 164 verses. "
                    "Each hymn has unique effects: binding, healing, fire, frost, wisdom, "
                    "curse, victory, illusion, rune-shield, wolves, death, world-tree drain, "
                    "Ragnarök foretelling, and the unknowable 18th. "
                    "[TRANSFORMATION: Ancient Norse runes glow in the air as Odin chants]"
                )
            },
        }

    # ------------------------------------------------------------------
    # apply_effect
    # ------------------------------------------------------------------
    def apply_effect(self, effect, target=None):
        # ── Ravens ──────────────────────────────────────────────────────
        if effect == "huginn":
            self.add_status_effect(StatusEffect.DEFEND, 1, 0.5)
            return (
                "🐦‍⬛ [HUGINN'S SIGHT] Huginn reveals enemy's next move! "
                "50% dodge next turn. [TRANSFORMATION: Thought becomes a raven]"
            )
        elif effect == "muninn":
            self.add_status_effect(StatusEffect.EMPOWER, 1, 2.0)
            return (
                "🐦‍⬛ [MUNINN'S MEMORY] Muninn reveals enemy's weakness! "
                "Next attack deals double damage! [TRANSFORMATION: Memory becomes a raven]"
            )

        # ── 18 Hymns ─────────────────────────────────────────────────────
        elif effect == "hymn_hel_vita":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.STUN, 1)
            return "🔮 [6TH GALDER: HEL VÍTA] Odin lifts the opponent skyward — a divine shockwave HURLS them into the arena walls! STUN applied! [TRANSFORMATION: The target crashes against the boundary walls of the arena]"

        elif effect == "hymn_bind":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.SLOW, 1, 0.5)
            return "🔮 [1ST GALDER] Ljóðatal — rune-chains slow the target! (-50% action speed)"

        elif effect == "hymn_heal":
            self.heal(120)
            return "🔮 [2ND GALDER] Lyfjaberg — Odin heals 120 HP from the mountain of healing!"

        elif effect == "hymn_shackle":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.BURN, 2)  # ongoing rune-damage represented as burn
            return (
                "🔮 [3RD GALDER] Þjóðvitni — spectral chains bind the target! "
                "BURN (rune damage) for 2 turns."
            )

        elif effect == "hymn_fire":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.BURN, 3)
            return "🔮 [4TH GALDER] Fýrisvellir — rune-fire ignites the battlefield! BURN for 3 turns."

        elif effect == "hymn_frost":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.FROST, 2)
            return (
                "🔮 [7TH GALDER] Niflheimr — primordial ice descends! "
                "FROST for 2 turns + enemy loses 20 energy."
            )

        elif effect == "hymn_knowledge":
            self.add_status_effect(StatusEffect.EMPOWER, 2, 1.4)
            return "🔮 [8TH GALDER] Mímisbrunnr — wisdom of the Well! +40% damage for 2 turns."

        elif effect == "hymn_curse":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.WEAKEN, 2, 0.7)
            return "🔮 [10TH GALDER] Galdralag — curse layered on curse! Enemy damage -30% for 2 turns."

        elif effect == "hymn_victory":
            self.add_status_effect(StatusEffect.EMPOWER, 1, 1.3)
            return "🔮 [11TH GALDER] Sigrdrífumál — victory runes blaze! +30% damage this turn."

        elif effect == "hymn_illusion":
            tgt = target if target else self
            self.add_status_effect(StatusEffect.EVASION, 1, 0.6)
            tgt.add_status_effect(StatusEffect.BLIND, 1)
            return (
                "🔮 [12TH GALDER] Fjölsvinnsmál — Odin fractures into twelve afterimages! "
                "60% evasion this turn + enemy BLIND for 1 turn."
            )

        elif effect == "hymn_rune_shield":
            # Shield value of 0.0 = absorb next hit entirely
            self.add_status_effect(StatusEffect.SHIELD, 1, 0.0)
            return "🔮 [13TH GALDER] Rígsþula — rune-circle forms! Next hit is absorbed entirely."

        elif effect == "hymn_wolves":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.BLEED, 2)
            return (
                "🔮 [14TH GALDER] Geri Freki — two spectral wolves strike! "
                "Dual-hit + BLEED for 2 turns."
            )

        elif effect == "hymn_death":
            tgt = target if target else self
            if random.random() < 0.20:
                tgt.add_status_effect(StatusEffect.STUN, 2)
                return (
                    "🔮 [15TH GALDER] Vafþrúðnismál — the Dagaz rune detonates! "
                    "20% stun proc TRIGGERED — target STUNNED for 2 turns!"
                )
            return (
                "🔮 [15TH GALDER] Vafþrúðnismál — the Dagaz rune detonates! "
                "(Stun proc: missed this time)"
            )

        elif effect == "hymn_world_tree":
            return "🔮 [16TH GALDER] Yggdrasil — life-force drained! Odin heals 50% of damage dealt."

        elif effect == "hymn_ragnarok":
            self.take_damage(40)
            return (
                "🔮 [17TH GALDER] Völuspá — Ragnarök in miniature! "
                "Ignores all defenses. Odin takes 40 recoil damage."
            )

        elif effect == "hymn_unknowable":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.WEAKEN, 2, 0.6)
            tgt.add_status_effect(StatusEffect.BLIND, 2)
            tgt.add_status_effect(StatusEffect.SLOW, 2, 0.5)
            return (
                "🔮 [18TH GALDER] The Unknowable — something older than runes acts through Odin. "
                "WEAKEN + BLIND + SLOW applied simultaneously for 2 turns."
            )

        # ── Life Theft ───────────────────────────────────────────────────
        elif effect == "life_theft":
            self.life_theft_active = True
            self.drain_timer = 3
            self.add_status_effect(StatusEffect.LIFE_DRAIN, 3)
            return (
                "🌿 [LIFE THEFT] Life energy drained from all enemies for 3 turns! "
                "[TRANSFORMATION: Dark tendrils extend from Odin, siphoning vitality]"
            )

        # ── Matter Manipulation ──────────────────────────────────────────
        elif effect == "matter":
            self.add_status_effect(StatusEffect.MATTER_MANIP, 1)
            return (
                "✨ [MATTER MANIPULATION] Matter manipulation active! "
                "Next attack ignores defenses. [TRANSFORMATION: Reality bends to Odin's will]"
            )

        # ── Treasures ────────────────────────────────────────────────────
        elif effect == "gram":
            self.active_treasures.add("gram")
            self.treasure_timers["gram"] = 3
            self.add_status_effect(StatusEffect.GRAM, 3)
            self.add_status_effect(StatusEffect.EMPOWER, 3, 1.5)
            result = "🗡️ [MANIFEST GRAM] Gram manifested! +50% damage for 3 turns. [TRANSFORMATION: The blade materializes from his flesh]"
            if self._check_all_treasures():
                result += " | 🌳 [YGGDRASIL AWAKENING] ALL FOUR TREASURES OF CALAMITY UNITED! THE WORLD TREE STIRS!"
            return result
        elif effect == "draupnir":
            self.active_treasures.add("draupnir")
            self.treasure_timers["draupnir"] = 3
            self.add_status_effect(StatusEffect.DRAUPNIR, 3)
            self.add_status_effect(StatusEffect.EMPOWER, 3, 1.3)
            result = "💍 [MANIFEST DRAUPNIR] Draupnir manifested! The self-multiplying ring of Chaos!"
            if self._check_all_treasures():
                result += " | 🌳 [YGGDRASIL AWAKENING] ALL FOUR TREASURES OF CALAMITY UNITED! THE WORLD TREE STIRS!"
            return result
        elif effect == "egil":
            self.active_treasures.add("egil")
            self.treasure_timers["egil"] = 3
            self.add_status_effect(StatusEffect.EGIL, 3)
            self.add_status_effect(StatusEffect.SHIELD, 3, 0.5)
            result = "⛑️ [MANIFEST EGIL] Egil manifested! The helmet of Satan focuses dark energy!"
            if self._check_all_treasures():
                result += " | 🌳 [YGGDRASIL AWAKENING] ALL FOUR TREASURES OF CALAMITY UNITED! THE WORLD TREE STIRS!"
            return result
        elif effect == "brisingamen":
            self.active_treasures.add("brisingamen")
            self.treasure_timers["brisingamen"] = 3
            self.add_status_effect(StatusEffect.BRISINGAMEN, 3)
            self.add_status_effect(StatusEffect.FROST, 3)
            result = "📿 [MANIFEST BRISINGAMEN] Brisingamen manifested! Primordial frost radiates!"
            if self._check_all_treasures():
                result += " | 🌳 [YGGDRASIL AWAKENING] ALL FOUR TREASURES OF CALAMITY UNITED! THE WORLD TREE STIRS!"
            return result

        # ── Battle Form ──────────────────────────────────────────────────
        elif effect == "battle_form":
            self.form = "Young"
            self.divine_mode = True
            self.divine_timer = 5
            self.max_hp += 200
            self.hp += 200
            self.add_status_effect(StatusEffect.BATTLE_FORM, 5)
            self.add_status_effect(StatusEffect.EMPOWER, 5, 2.0)
            return (
                "👤 [BATTLE FORM] ODIN REVEALS HIS BATTLE FORM! His aged form disintegrates "
                "to ash, revealing the young warrior god beneath — black hair with white "
                "accents, six marks around his eye crackling with power. "
                "[TRANSFORMATION: The Supreme God sheds his mortal guise]"
            )

        return ""

    def _check_all_treasures(self):
        """Returns True and activates Yggdrasil Awakening if all 4 treasures are active."""
        all_four = {"gram", "draupnir", "egil", "brisingamen"}
        if all_four.issubset(self.active_treasures):
            self.yggdrasil_awakening = True
            self.add_status_effect(StatusEffect.EMPOWER, 3, 2.5)
            return True
        return False

    # ------------------------------------------------------------------
    # Post-damage hook for world-tree drain (Hymn 16)
    # ------------------------------------------------------------------
    def post_damage_hook(self, damage_dealt, effect):
        """Call this after dealing damage when effect == 'hymn_world_tree'."""
        if effect == "hymn_world_tree" and damage_dealt > 0:
            heal_amount = damage_dealt // 2
            self.heal(heal_amount)
            print(f"  🌿 [YGGDRASIL DRAIN] Odin heals {heal_amount} HP from life-force siphoned!")

    # NOTE: To wire post_damage_hook for hymn_world_tree in use_ability(),
    # add after taking damage in the type=="damage" branch:
    #
    #   if hasattr(character, 'post_damage_hook') and "effect" in ability:
    #       character.post_damage_hook(dmg, ability["effect"])

    # ------------------------------------------------------------------
    # hymn_wolves multi-hit helper (called from use_ability type=="damage")
    # ------------------------------------------------------------------
    # The Geri Freki hymn (key '17') uses the "hymn_wolves" effect.
    # In use_ability(), detect this and split the damage into 2 bites:
    #
    #   if ability.get("effect") == "hymn_wolves":
    #       bite1 = dmg // 2
    #       bite2 = dmg - bite1
    #       target.take_damage(bite1)
    #       target.take_damage(bite2)
    #       print(f"  🐺 Geri bites for {bite1}! Freki bites for {bite2}!")
    #   else:
    #       target.take_damage(dmg, ignore_defense=ignore_defense)

    # ------------------------------------------------------------------
    # update_status_effects
    # ------------------------------------------------------------------
    def update_status_effects(self):
        super().update_status_effects()
        if self.life_theft_active and self.drain_timer > 0:
            self.drain_timer -= 1
            if self.drain_timer <= 0:
                self.life_theft_active = False
                self.remove_status_effect(StatusEffect.LIFE_DRAIN)
                print(f"  🌿 Odin's Life Theft fades.")

        expired = [t for t, timer in self.treasure_timers.items() if timer <= 1]
        for t in expired:
            del self.treasure_timers[t]
            self.active_treasures.discard(t)
            print(f"  ⏳ Odin's {t.title()} fades.")
        for t in list(self.treasure_timers):
            self.treasure_timers[t] -= 1
        was_awakened = self.yggdrasil_awakening
        self.yggdrasil_awakening = len(self.active_treasures) == 4
        if was_awakened and not self.yggdrasil_awakening:
            print("  🌳 [YGGDRASIL AWAKENING ENDS] The Four Treasures are no longer all united.")

    # ------------------------------------------------------------------
    # get_damage_multiplier
    # ------------------------------------------------------------------
    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()
        if "gram" in self.active_treasures:
            mult *= 1.5
            buffs.append("🗡️ GRAM")
        if "draupnir" in self.active_treasures:
            mult *= 1.3
            buffs.append("💍 DRAUPNIR")
        if "egil" in self.active_treasures:
            buffs.append("⛑️ EGIL")
        if "brisingamen" in self.active_treasures:
            buffs.append("📿 BRISINGAMEN")
        if self.yggdrasil_awakening:
            mult *= 2.5
            buffs.append("🌳 YGGDRASIL AWAKENING x2.5!")
        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique:
            self.divine_technique = {
                "name": "🔱 GUNGNIR: Absolute Certainty",
                "cost": 220,
                "dmg": (650, 850),
                "type": "damage",
                "desc": (
                    "🔱 [GUNGNIR] Odin throws Gungnir, the spear that never misses. "
                    "The spear's trajectory is absolute and unavoidable. "
                    "[TRANSFORMATION: Gungnir becomes one with fate itself]"
                )
            }
        return self.divine_technique

class LuBu(Character):
    def __init__(self):
        super().__init__(
            "Lü Bu",
            "The Flying General • China",
            1250, 430,
            [Realm.GODLY_STRENGTH, Realm.GODLY_WILL]
        )
        self.round = 1
        self.affiliation = "Humanity"
        self.legs_broken = False
        self.red_hare_active = False

        self.divine_technique = None

        self.abilities = {
            '1': {"name": "🏹 Sky Piercer", "cost": 30, "dmg": (160, 220), "type": "damage",
                  "desc": "🏹 [SKY PIERCER] Lü Bu thrusts his spear with enough force to pierce the heavens. Raw power alone creates a shockwave that reaches the sky. [TRANSFORMATION: Raw power alone creates a shockwave that reaches the sky]"},
            '2': {"name": "🐎 Red Hare Charge", "cost": 35, "dmg": (190, 260), "type": "damage",
                  "desc": "🐎 [RED HARE CHARGE] Lü Bu charges forward on his legendary steed Red Hare. Man and horse become one, moving as a single unstoppable force. [TRANSFORMATION: Man and horse become one, moving as a single unstoppable force]"},
            '3': {"name": "🏹 Basic Strike", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "🏹 [BASIC STRIKE] A basic attack from the Flying General."},
            '4': {"name": "🏹 Incomplete Sky Eater", "cost": 50, "dmg": (270, 340), "type": "damage",
                  "desc": "🏹 [INCOMPLETE SKY EATER] A preliminary version of Sky Eater. The first hints of heaven-rending power. [TRANSFORMATION: The first hints of heaven-rending power]"},
            '5': {"name": "🏹 Sky Eater", "cost": 100, "dmg": (430, 550), "type": "damage",
                  "desc": "🏹 [SKY EATER] The technique that defines Lü Bu. The sky itself trembles before this strike. [TRANSFORMATION: The sky itself trembles before this strike]"},
            '6': {"name": "🦯 Broken Legs Fighting", "cost": 40, "dmg": (220, 290), "type": "damage",
                  "effect": "break_legs",
                  "desc": "🦯 [BROKEN LEGS FIGHTING] Even with broken legs, Lü Bu continues to fight. Pain becomes power - even crippled, he stands. [TRANSFORMATION: Pain becomes power - even crippled, he stands]"},
            '7': {"name": "🏹 The Strongest Warrior from China", "cost": 50, "dmg": (280, 350), "type": "damage",
                  "effect": "shatter",
                  "desc": "🏹 [STRONGEST WARRIOR FROM CHINA] Lü Bu crouches low, placing his left hand on the ground while raising his halberd. He leaps forward with devastating force, shattering enemy weapons. The raw power of China's mightiest warrior concentrates into a single explosive leap. [TRANSFORMATION: The raw power of China's mightiest warrior concentrates into a single explosive leap]"}
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.RANDGRIZ:
            return f"❌ Lü Bu can only bond with Randgriz!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Fang Tian Ji (方天画戟)"
        self.add_status_effect(StatusEffect.VOLUNDR, 999)

        self.divine_technique = {
            "name": "🏹 SKY EATER",
            "cost": 180,
            "dmg": (550, 700),
            "type": "damage",
            "desc": "🏹 [SKY EATER] Lü Bu's ultimate technique with Randgriz. He channels all his strength into a single strike that splits the sky itself. The halberd becomes an extension of Lü Bu's very soul, capable of tearing the heavens asunder. [TRANSFORMATION: The halberd becomes an extension of Lü Bu's very soul, capable of tearing the heavens asunder]"
        }

        print(f"\n⚔️ VÖLUNDR: Lü Bu x Randgriz")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → [TRANSFORMATION: Randgriz fuses with")
        print(f"      his halberd, creating a weapon")
        print(f"      that can shatter any defense]")
        return f"✅ Völundr successfully activated for Lü Bu!"

    def apply_effect(self, effect, target=None):
        if effect == "break_legs":
            self.legs_broken = True
            self.red_hare_active = True
            self.add_status_effect(StatusEffect.BERSERK, 3)
            return "🦯 [BROKEN LEGS] Lü Bu fights with broken legs! [TRANSFORMATION: Pain becomes fuel - even with shattered legs, he stands and fights]"
        elif effect == "shatter":
            return "💥 [SHATTER] Lü Bu's attack shatters enemy weapons! [TRANSFORMATION: The raw power of China's mightiest warrior concentrates into a single explosive leap]"
        return ""

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()

        if self.legs_broken:
            mult *= 1.5
            buffs.append("🦯 BROKEN LEGS")

        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "🏹 SKY EATER",
                "cost": 180,
                "dmg": (550, 700),
                "type": "damage",
                "desc": "🏹 [SKY EATER] Lü Bu's ultimate technique with Randgriz. He channels all his strength into a single strike that splits the sky itself. The halberd becomes an extension of Lü Bu's very soul, capable of tearing the heavens asunder. [TRANSFORMATION: The halberd becomes an extension of Lü Bu's very soul, capable of tearing the heavens asunder]"
            }
        return self.divine_technique


# ============================================================================
# KOJIRO SASAKI - History's Greatest Loser (FIXED with scanning evasion)
# ============================================================================

class KojiroSasaki(Character):
    def __init__(self):
        super().__init__(
            "Kojiro Sasaki",
            "History's Greatest Loser • Japan",
            1180, 420,
            [Realm.GODLY_TECHNIQUE]
        )
        self.round = 3
        self.affiliation = "Humanity"
        self.scan_progress = 0
        self.simulations_complete = 0
        self.weapon_broken = False
        self.dual_wielding = False
        self.manju_muso = False
        self.damage_pressure = 0  # Accumulates on hits; raises Re-Völundr chance

        self.abilities = {
            '1': {"name": "⚔️ Scanning", "cost": 20, "dmg": (0, 0), "type": "buff", "effect": "scan",
                  "desc": "⚔️ [SCANNING] Kojiro scans his opponent, analyzing their movements. Thousands of simulations run in his mind with each scan. [TRANSFORMATION: Thousands of simulations run in his mind with each scan]"},
            '2': {"name": "⚔️ Basic Slash", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "⚔️ [BASIC SLASH] A basic sword slash."}
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.HRIST:
            return f"❌ Kojiro can only bond with Hrist!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Bizen Nagamitsu / Monohoshizao (備前長光 / 物干竿)"
        self.add_status_effect(StatusEffect.VOLUNDR, 999)

        self.divine_technique = {
            "name": "⚔️ SŌENZANKO BANJINRYŌRAN",
            "cost": 180,
            "dmg": (550, 700),
            "type": "damage",
            "desc": "⚔️ [SŌENZANKO BANJINRYŌRAN] 'Ten Thousand Tiger-Slaying Blade of the Twin Swallows' - Kojiro's ultimate technique combining Tsubame Gaeshi and Torakiri with both swords. Two swords become one technique, each strike flowing into the next. [TRANSFORMATION: Two swords become one technique, each strike flowing into the next]"
        }

        self.abilities = {
            '1': {"name": "⚔️ Scanning", "cost": 20, "dmg": (0, 0), "type": "buff", "effect": "scan",
                  "desc": "⚔️ [SCANNING] Kojiro scans his opponent, analyzing their movements. Thousands of simulations run in his mind with each scan. [TRANSFORMATION: Thousands of simulations run in his mind with each scan]"},
            '2': {"name": "⚔️ Basic Slash", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "⚔️ [BASIC SLASH] A basic sword slash."},
            '3': {"name": "⚔️ Tsubame Gaeshi", "cost": 40, "dmg": (200, 270), "type": "damage",
                  "desc": "⚔️ [TSUBAME GAESHI] 'Swallow Reversal' - The legendary swallow reversal. The blade stops mid-descent and reverses direction, catching even swallows in mid-flight. [TRANSFORMATION: The blade stops mid-descent and reverses direction, catching even swallows]"},
            '4': {"name": "⚔️ Torakiri", "cost": 35, "dmg": (180, 250), "type": "damage",
                  "desc": "⚔️ [TORAKIRI] 'Tiger Claw' - A horizontal slash that flows like water. The blade shifts to a reverse grip, striking from unexpected angles. [TRANSFORMATION: The blade shifts to a reverse grip, striking from unexpected angles]"},
            '5': {"name": "⚔️ Sōenzanko", "cost": 100, "dmg": (430, 550), "type": "damage",
                  "desc": "⚔️ [SŌENZANKO] 'Twin Swallow Tiger' - The ultimate combination technique. Tsubame Gaeshi and Torakiri merge into one devastating combo. [TRANSFORMATION: Tsubame Gaeshi and Torakiri merge into one devastating combo]"},
            '6': {"name": "👁️ Manju Muso", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "👁️ [MANJU MUSO] 'Ultimate Vision of Ten Thousand Moves' - Kojiro's Senju Muso evolves to its peak. He can now analyze not just opponents but also vibrations traveling through air and ground, predicting movements with absolute precision. The world itself becomes readable - every vibration tells him where the enemy will strike. [TRANSFORMATION: The world itself becomes readable - every vibration tells him where the enemy will strike]"},
            '7': {"name": "🧠 Image Training", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "🧠 [IMAGE TRAINING] Kojiro has memorized the attack patterns of every opponent he's ever faced. He can simulate fights with them anytime to improve. All techniques improve over time through mental simulation. [PASSIVE: All techniques improve over time through mental simulation]"}
        }

        print(f"\n⚔️ VÖLUNDR: Kojiro x Hrist")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → [TRANSFORMATION: Hrist's dual nature")
        print(f"      manifests in the blade - it can")
        print(f"      split into two when broken]")
        return f"✅ Völundr successfully activated for Kojiro Sasaki!"

    def apply_effect(self, effect, target=None):
        if effect == "scan":
            self.scan_progress += 1
            self.simulations_complete += 1000
            evasion = min(0.8, self.scan_progress * 0.1)
            crit = min(0.5, self.scan_progress * 0.05)
            self.add_status_effect(StatusEffect.EVASION, 3, evasion)
            self.add_status_effect(StatusEffect.SCANNING, 3, stacks=self.scan_progress)
            if self.scan_progress >= 5:
                self.manju_muso = True
                self.add_status_effect(StatusEffect.MANJU_MUSO, 999)
            return f"🔍 [SCAN] Scan {self.scan_progress}: {evasion * 100}% evasion, {crit * 100}% crit. [TRANSFORMATION: {self.simulations_complete} simulations complete - every possible move calculated]"
        return ""

    def take_damage(self, dmg, ignore_defense=False):
        actual = super().take_damage(dmg, ignore_defense)
        if self.volund_active and not self.weapon_broken and actual > 0:
            # Each hit adds pressure proportional to damage taken vs max HP
            self.damage_pressure += actual / self.max_hp
        return actual

    def check_weapon_break(self):
        if not self.weapon_broken:
            # Base 15% + up to +50% from accumulated damage pressure (capped at 65%)
            pressure_bonus = min(0.50, self.damage_pressure * 0.8)
            chance = 0.15 + pressure_bonus
            if random.random() < chance:
                self.weapon_broken = True
                self.dual_wielding = True
                self.damage_pressure = 0
                self.add_status_effect(StatusEffect.DUAL_WIELD, 999)
                pct = int(chance * 100)
                return (f"💥 [RE-VÖLUNDR] Monohoshizao SHATTERS under the relentless assault! "
                        f"({pct}% break chance from battle damage) "
                        f"Re-Völundr activates! Kojiro now wields TWO SWORDS! "
                        f"[TRANSFORMATION: Hrist's dual nature emerges - one blade becomes two]")
        return None

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()

        if self.dual_wielding:
            mult *= 2.0
            buffs.append("⚔️⚔️ DUAL WIELD")

        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "⚔️ SŌENZANKO BANJINRYŌRAN",
                "cost": 180,
                "dmg": (550, 700),
                "type": "damage",
                "desc": "⚔️ [SŌENZANKO BANJINRYŌRAN] 'Ten Thousand Tiger-Slaying Blade of the Twin Swallows' - Kojiro's ultimate technique combining Tsubame Gaeshi and Torakiri with both swords. Two swords become one technique, each strike flowing into the next. [TRANSFORMATION: Two swords become one technique, each strike flowing into the next]"
            }
        return self.divine_technique


# ============================================================================
# JACK THE RIPPER - The Whitechapel Demon (FIXED with organ shift and proper abilities)
# ============================================================================

class JackTheRipper(Character):
    def __init__(self):
        super().__init__(
            "Jack the Ripper",
            "The Whitechapel Demon • England",
            1150, 400,
            [Realm.GODLY_TECHNIQUE]
        )
        self.round = 4
        self.affiliation = "Humanity"
        self.environment_weapons = []
        self.organs_can_shift = True
        self.soul_eye = True
        self.arm_extended = False
        self.has_environment_weapon = False
        self.organ_shift_used = False

        self.magic_pouches = {
            "knives": 50,
            "piano_wires": 10,
            "umbrellas": 2,
            "scissors": 1,
            "switchblade": 1,
            "grappling_hook": 1,
            "throwing_axes": 2,
            "cannonball": 1
        }

        self.abilities = {
            '1': {"name": "🗡️ Knife Strike", "cost": 15, "dmg": (110, 160), "type": "damage",
                  "weapon": "Knife Strike", "max_uses": 50, "uses_left": 50,
                  "desc": "🗡️ [KNIFE STRIKE] A quick knife attack. Jack carries 50 knives in his magic pouches. [MAGIC GLOVES: Turns ordinary knife into DIVINE THROWING BLADE]"},
            '2': {"name": "👁️ Soul Eye", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "weapon": "Soul Eye", "max_uses": float('inf'),
                  "desc": "👁️ [SOUL EYE] Jack can see the 'color' of people's souls. [PASSIVE ABILITY - NOT A WEAPON]"},
            '3': {"name": "🗡️ Dear Jane", "cost": 25, "dmg": (130, 190), "type": "damage",
                  "weapon": "Dear Jane", "max_uses": 50, "uses_left": 50,
                  "desc": "🗡️ [DEAR JANE] A simple knife attack named after Jack's mother. [MAGIC GLOVES: Turns ordinary knife into DIVINE WEAPON, named for the mother he loved and killed]"},
            '4': {"name": "🎻 Piano Wire", "cost": 30, "dmg": (150, 210), "type": "damage",
                  "weapon": "Piano Wire", "max_uses": 10, "uses_left": 10,
                  "desc": "🎻 [PIANO WIRE] Jack uses piano wire to strangle his opponents. 10 uses. [MAGIC GLOVES: Turns ordinary piano wire into INVISIBLE DIVINE GARROTE]"},
            '5': {"name": "☂️ Umbrella", "cost": 25, "dmg": (0, 0), "type": "defense",
                  "weapon": "Umbrella", "max_uses": 2, "uses_left": 2,
                  "effect": "umbrella_shield",
                  "desc": "☂️ [UMBRELLA] Jack's umbrella can be used as a shield. Only 2. [MAGIC GLOVES: Turns ordinary umbrella into DIVINE SHIELD, capable of deflecting godly strikes]"},
            '6': {"name": "✂️ Giant Scissors", "cost": 35, "dmg": (190, 260), "type": "damage",
                  "weapon": "Giant Scissors", "max_uses": 1, "uses_left": 1,
                  "desc": "✂️ [GIANT SCISSORS] Massive scissors that can sever limbs. One-time use. [MAGIC GLOVES: Turns scissors into DIVINE SEVERING WEAPON]"},
            '7': {"name": "🔪 Giant Switchblade", "cost": 40, "dmg": (210, 290), "type": "damage",
                  "weapon": "Giant Switchblade", "max_uses": 1, "uses_left": 1,
                  "desc": "🔪 [GIANT SWITCHBLADE] A massive switchblade that extends unexpectedly. Single use. [MAGIC GLOVES: Turns switchblade into EXTENDING DIVINE BLADE]"},
            '8': {"name": "🪓 Throwing Axes", "cost": 45, "dmg": (230, 310), "type": "damage",
                  "weapon": "Throwing Axes", "max_uses": 2, "uses_left": 2,
                  "desc": "🪓 [THROWING AXES] Jack throws axes with deadly precision. He carries 2. [MAGIC GLOVES: Turns axes into DIVINE RETURNING AXES]"},
            '9': {"name": "⚫ Cannonball", "cost": 50, "dmg": (270, 350), "type": "damage",
                  "weapon": "Cannonball", "max_uses": 1, "uses_left": 1,
                  "desc": "⚫ [CANNONBALL] Jack produces a cannonball and hurls it. One shot only. [MAGIC GLOVES: Turns cannonball into DIVINE EXPLOSIVE SHOT]"},
            '10': {"name": "🏙️ Environment Weapon", "cost": 35, "dmg": (160, 230), "type": "utility",
                   "weapon": "Environment Weapon", "max_uses": float('inf'),
                   "effect": "environment",
                   "desc": "🏙️ [ENVIRONMENT WEAPON] Jack turns his surroundings into weapons - lampposts become spears, cobblestones become bullets. [MAGIC GLOVES: Turns ENVIRONMENT into DIVINE WEAPONS] Unlimited."},
            '11': {"name": "🌫️ Bloody Mist", "cost": 40, "dmg": (0, 0), "type": "buff",
                   "weapon": "Bloody Mist", "max_uses": float('inf'),
                   "effect": "mist",
                   "desc": "🌫️ [BLOODY MIST] Jack creates a mist of blood that conceals his movements. [MAGIC GLOVES: Turns BLOOD into DIVINE CONCEALING MIST]"},
            '12': {"name": "🎪 Rondo of Blessing", "cost": 60, "dmg": (300, 380), "type": "damage",
                   "weapon": "Rondo of Blessing", "max_uses": float('inf'),
                   "effect": "rondo",
                   "desc": "🎪 [RONDO OF BLESSING] A graceful dance of death. Jack uses his cloak as a Divine Weapon, cutting an entire building to collapse onto his enemy. [TRANSFORMATION: Magic Gloves turn his cloak into a DIVINE BLADED CLOAK - the building becomes a DIVINE CRUSHING STRUCTURE]"},
            '13': {"name": "🦯 Grappling Hook", "cost": 20, "dmg": (0, 0), "type": "utility",
                   "weapon": "Grappling Hook", "max_uses": 1, "uses_left": 1,
                   "effect": "grapple",
                   "desc": "🦯 [GRAPPLING HOOK] Jack uses a grappling hook to reposition instantly. One-time. [MAGIC GLOVES: Turns grappling hook into DIVINE CATCHING TOOL]"},
            '14': {"name": "🦾 Arm Extension", "cost": 30, "dmg": (0, 0), "type": "buff",
                   "weapon": "Arm Extension", "max_uses": float('inf'),
                   "effect": "arm_extension",
                   "desc": "🦾 [ARM EXTENSION] Jack's arms extend unnaturally. [MAGIC GLOVES: Enhances his own BODY, allowing limbs to stretch]"},
            '15': {"name": "🗡️ Guidance of the Nocturne", "cost": 55, "dmg": (260, 330), "type": "damage",
                   "weapon": "Guidance of the Nocturne", "max_uses": float('inf'),
                   "desc": "🗡️ [GUIDANCE OF THE NOCTURNE] Jack strikes from the shadows. [MAGIC GLOVES: Turns SHADOWS into DIVINE SHADOW BLADES]"},
            '16': {"name": "🫀 Internal Organ Shift", "cost": 40, "dmg": (0, 0), "type": "buff",
                   "weapon": "Internal Organ Shift", "max_uses": float('inf'),
                   "effect": "organ_shift_manual",
                   "desc": "🫀 [INTERNAL ORGAN SHIFT] Jack manually shifts his internal organs to reduce damage for 3 turns. [MAGIC GLOVES: Enhances his own BODY, allowing organs to shift position]"},
            '17': {"name": "🎭 The Final Blow", "cost": 45, "dmg": (240, 320), "type": "damage",
                   "weapon": "The Final Blow", "max_uses": float('inf'),
                   "desc": "🎭 [THE FINAL BLOW] Jack performs the arm extension he learned fighting Alfred, increasing reach and momentum to throw a cannonball with enough force to drill through a torso. [TRANSFORMATION: Extended arms create devastating centrifugal force]"}
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.HLÖKK:
            return f"❌ Jack can only bond with Hlökk!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Magic Gloves (能力: あらゆるものを神器化)"
        self.add_status_effect(StatusEffect.VOLUNDR, 999)

        self.divine_technique = {
            "name": "🗡️ DEAR GOD",
            "cost": 200,
            "dmg": (550, 700),
            "type": "damage",
            "desc": "🗡️ [DEAR GOD] Jack's ultimate technique - he turns the entire city of London into his divine weapon. Every building, every street, every shadow becomes a divine tool for murder - all channeled through the Magic Gloves. [TRANSFORMATION: Every building, every street, every shadow becomes a divine tool for murder - all channeled through the Magic Gloves]"
        }

        print(f"\n⚔️ VÖLUNDR: Jack x Hlökk (FORCED)")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → {len(self.abilities)} weapons - Knives(50),")
        print(f"      Wire(10), Umbrella(2), etc.")
        print(f"   → [MAGIC GLOVES] Can turn ANY object")
        print(f"      into a Divine Weapon!")
        return f"✅ Völundr successfully activated for Jack the Ripper!"

    def use_ability(self, ability_key):
        if ability_key in self.abilities:
            ability = self.abilities[ability_key]
            if "uses_left" in ability:
                if ability["uses_left"] <= 0:
                    print(f"❌ [NO USES] No more {ability['name']} left in your magic pouches!")
                    return False
                ability["uses_left"] -= 1
                weapon_name = ability["name"]
                uses_left = ability["uses_left"]
                max_uses = ability["max_uses"]

                if "Knife" in weapon_name and "Dear" not in weapon_name:
                    print(
                        f"⚡ [MAGIC GLOVES] Jack touches the ordinary knife with his Magic Gloves - it transforms into a DIVINE THROWING BLADE!")
                elif "Dear Jane" in weapon_name:
                    print(
                        f"⚡ [MAGIC GLOVES] The knife named after his mother glows with divine light - transformed by the Magic Gloves!")
                elif "Piano" in weapon_name:
                    print(
                        f"⚡ [MAGIC GLOVES] Jack's Magic Gloves glow as he touches the piano wire - it becomes an INVISIBLE DIVINE GARROTE!")
                elif "Umbrella" in weapon_name:
                    print(
                        f"⚡ [MAGIC GLOVES] Jack opens his umbrella and the Magic Gloves transform it into an impenetrable DIVINE SHIELD!")
                elif "Scissors" in weapon_name:
                    print(
                        f"⚡ [MAGIC GLOVES] The giant scissors glow with divine light as Jack's Magic Gloves work their power - now a DIVINE SEVERING TOOL!")
                elif "Switchblade" in weapon_name:
                    print(
                        f"⚡ [MAGIC GLOVES] Click! The switchblade extends, now infused with divine energy from the Magic Gloves - an EXTENDING DIVINE BLADE!")
                elif "Axes" in weapon_name:
                    print(
                        f"⚡ [MAGIC GLOVES] Both axes shimmer with divine power as Jack's Magic Gloves enhance them - DIVINE RETURNING AXES!")
                elif "Cannonball" in weapon_name:
                    print(
                        f"⚡ [MAGIC GLOVES] The cannonball glows with golden light - now a DIVINE EXPLOSIVE PROJECTILE!")
                elif "Grappling" in weapon_name:
                    print(
                        f"⚡ [MAGIC GLOVES] The grappling hook transforms, now able to catch even divine beings - a DIVINE CATCHING TOOL!")

                print(f"📦 {weapon_name} uses left: {uses_left}/{max_uses}")
            return True
        return False

    def apply_effect(self, effect, target=None):
        if effect == "soul_eye":
            self.add_status_effect(StatusEffect.SOUL_EYE, 3)
            self.add_status_effect(StatusEffect.EMPOWER, 3, 1.2)
            return "👁️ [SOUL EYE] Jack's eyes glow — he sees the target's soul through his Magic Gloves! Next 3 attacks +20% damage."
        elif effect == "environment":
            locations = ["lamppost", "cobblestone", "building", "bridge", "fountain", "big ben"]
            loc = random.choice(locations)
            transforms = {
                "lamppost": "DIVINE SPEAR",
                "cobblestone": "DIVINE BULLETS",
                "building": "DIVINE CRUSHING WALL",
                "bridge": "DIVINE COLLAPSING STRUCTURE",
                "fountain": "DIVINE WATER BLADES",
                "big ben": "DIVINE CLOCK HAND BLADE"
            }
            weapon = transforms[loc]
            self.has_environment_weapon = True
            self.add_status_effect(StatusEffect.ENVIRONMENT, 1)
            return f"⚡ [MAGIC GLOVES] Jack touches the {loc} with his Magic Gloves - it transforms into a {weapon}!"
        elif effect == "arm_extension":
            self.arm_extended = True
            self.add_status_effect(StatusEffect.ARM_EXTENSION, 3)
            return "🦾 [MAGIC GLOVES] Jack's arms extend unnaturally as the Magic Gloves enhance his own body!"
        elif effect == "umbrella_shield":
            self.defending = True
            self.add_status_effect(StatusEffect.DEFEND, 1)
            return "☂️ [UMBRELLA SHIELD] Jack's umbrella deflects incoming attacks!"
        elif effect == "mist":
            self.add_status_effect(StatusEffect.CAMOUFLAGE, 2)
            self.add_status_effect(StatusEffect.EVASION, 2, 0.5)
            return "🌫️ [BLOODY MIST] Jack vanishes into a crimson mist!"
        elif effect == "grapple":
            self.add_status_effect(StatusEffect.GRAPPLE, 1)
            self.add_status_effect(StatusEffect.EVASION, 1, 0.7)
            return "🦯 [GRAPPLING HOOK] Jack swings away to safety! 70% evasion next turn!"
        elif effect == "organ_shift_manual":
            self.add_status_effect(StatusEffect.ORGAN_SHIFT, 3, 0.5)
            return "🫀 [INTERNAL ORGAN SHIFT] Jack manually shifts his organs! Damage reduced by 50% for 3 turns!"
        elif effect == "rondo":
            self.add_status_effect(StatusEffect.EMPOWER, 1, 1.5)
            return "🎪 [RONDO OF BLESSING] Jack's cloak becomes a divine blade, cutting the building!"
        return ""

    def take_damage(self, dmg, ignore_defense=False):
        if self.hp - dmg <= 0 and self.organs_can_shift and not self.organ_shift_used:
            self.organ_shift_used = True
            print(f"  🫀 [ORGAN SHIFT - PASSIVE] Jack shifts his organs to survive! The blow is not fatal!")
            dmg = self.hp - 1
            if dmg < 0:
                dmg = 0
        return super().take_damage(dmg, ignore_defense)

    def get_weapon_status(self):
        print("\n" + "=" * 110)
        print("📦 JACK'S MAGIC POUCHES - WEAPON REMAINING:")
        print("-" * 110)
        print("🔮 [MAGIC GLOVES] Can transform ANY touched object into a Divine Weapon")
        print()

        limited_weapons = []
        for key, ability in self.abilities.items():
            if "uses_left" in ability:
                limited_weapons.append(
                    (ability["name"], ability["uses_left"], ability["max_uses"], ability.get("desc", "")))

        limited_weapons.sort()

        for name, uses, max_uses, desc in limited_weapons:
            bar_len = 20
            if max_uses == float('inf'):
                bar = "█" * bar_len
                percentage = 100
                print(f"  {name:25} |{bar}| Unlimited")
            else:
                filled = int(bar_len * uses / max_uses) if max_uses > 0 else 0
                bar = "█" * filled + "░" * (bar_len - filled)
                percentage = int((uses / max_uses) * 100) if max_uses > 0 else 0
                print(f"  {name:25} |{bar}| {uses:2}/{max_uses} ({percentage}%)")

                if "Knife" in name and "Dear" not in name:
                    print(f"      ↳ [MAGIC GLOVES] Ordinary knife → DIVINE THROWING BLADE")
                elif "Dear Jane" in name:
                    print(f"      ↳ [MAGIC GLOVES] Named knife → DIVINE MOTHER'S BLADE")
                elif "Piano" in name:
                    print(f"      ↳ [MAGIC GLOVES] Piano wire → INVISIBLE DIVINE GARROTE")
                elif "Umbrella" in name:
                    print(f"      ↳ [MAGIC GLOVES] Umbrella → DIVINE SHIELD")
                elif "Scissors" in name:
                    print(f"      ↳ [MAGIC GLOVES] Scissors → DIVINE SEVERING TOOL")
                elif "Switchblade" in name:
                    print(f"      ↳ [MAGIC GLOVES] Switchblade → EXTENDING DIVINE BLADE")
                elif "Axes" in name:
                    print(f"      ↳ [MAGIC GLOVES] Throwing axes → DIVINE RETURNING AXES")
                elif "Cannonball" in name:
                    print(f"      ↳ [MAGIC GLOVES] Cannonball → DIVINE EXPLOSIVE SHOT")
                elif "Grappling" in name:
                    print(f"      ↳ [MAGIC GLOVES] Grappling hook → DIVINE CATCHING TOOL (70% evasion)")

        print("=" * 110)

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "🗡️ DEAR GOD",
                "cost": 200,
                "dmg": (550, 700),
                "type": "damage",
                "desc": "🗡️ [DEAR GOD] Jack's ultimate technique - he turns the entire city of London into his divine weapon. Every building, every street, every shadow becomes a divine tool for murder - all channeled through the Magic Gloves. [TRANSFORMATION: Every building, every street, every shadow becomes a divine tool for murder - all channeled through the Magic Gloves]"
            }
        return self.divine_technique


# ============================================================================
# RAIDEN TAMEEMON - Greatest Sumo Wrestler (FIXED with muscle release)
# ============================================================================

class RaidenTameemon(Character):
    def __init__(self):
        super().__init__(
            "Raiden Tameemon",
            "Greatest Sumo Wrestler • Japan",
            1400, 420,
            [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE]
        )
        self.round = 5
        self.affiliation = "Humanity"
        self.muscle_release = 0
        self.release_available = True

        self.abilities = {
            '1': {"name": "💪 Basic Strike", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "💪 [BASIC STRIKE] A basic sumo strike."}
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.THRUD:
            return f"❌ Raiden can only bond with Thrud!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Supramuscular Exoskeletal Mawashi Belt (超筋骨外骨締廻し)"
        self.add_status_effect(StatusEffect.VOLUNDR, 999)

        self.divine_technique = {
            "name": "💪 YATAGARASU",
            "cost": 200,
            "dmg": (600, 800),
            "type": "damage",
            "desc": "💪 [YATAGARASU] Raiden's ultimate palm strike that removed four of Shiva's arms. All of Raiden's muscle power concentrates into a single devastating palm strike. [TRANSFORMATION: All of Raiden's muscle power concentrates into a single devastating palm strike]"
        }

        self.abilities = {
            '1': {"name": "💪 Basic Strike", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "💪 [BASIC STRIKE] A basic sumo strike."},
            '2': {"name": "🦵 Dropkick", "cost": 20, "dmg": (140, 200), "type": "damage",
                  "desc": "🦵 [DROPKICK] Raiden charges and jumps, delivering a powerful kick with both feet to the opponent's face. Sumo power meets aerial acrobatics. [TRANSFORMATION: Sumo power meets aerial acrobatics]"},
            '3': {"name": "🌼 Kiku-Ichimonji", "cost": 25, "dmg": (160, 220), "type": "damage",
                  "desc": "🌼 [KIKU-ICHIMONJI] 'Chrysanthemum Clothesline' - Raiden lunges with an outstretched arm, launching the opponent spinning into the air before they land face-first. A clothesline that sends opponents flying. [TRANSFORMATION: A clothesline that sends opponents flying]"},
            '4': {"name": "🙏 Jizo's Embrace", "cost": 30, "dmg": (180, 250), "type": "damage",
                  "effect": "stun",
                  "desc": "🙏 [JIZO'S EMBRACE] Raiden grabs the opponent's head and smashes his own into theirs with all his strength. The headbutt of a sumo wrestler - stunning and devastating. [TRANSFORMATION: The headbutt of a sumo wrestler - stunning and devastating]"},
            '5': {"name": "🐗 Wild Boar", "cost": 35, "dmg": (200, 280), "type": "damage",
                  "effect": "bind",
                  "desc": "🐗 [WILD BOAR] Raiden grabs a limb and concentrates all his might, crushing the gripped area. Muscles tighten like a vice - bone-crushing grip. [TRANSFORMATION: Muscles tighten like a vice - bone-crushing grip]"},
            '6': {"name": "🦁 Shishimai", "cost": 40, "dmg": (220, 310), "type": "damage",
                  "desc": "🦁 [SHISHIMAI] 'Lion Dance' - Raiden launches his feet in the air with hands on the ground, delivering a powerful kick with both soles. The lion dance of sumo - unexpected and deadly. [TRANSFORMATION: The lion dance of sumo - unexpected and deadly]"},
            '7': {"name": "⛰️ Miyama", "cost": 25, "dmg": (0, 0), "type": "defense",
                  "effect": "defense",
                  "desc": "⛰️ [MIYAMA] 'Mountain Deeps' - Raiden focuses muscles into both arms, creating an impenetrable wall of flesh. Arms become a mountain - no attack can pass. [TRANSFORMATION: Arms become a mountain - no attack can pass]"},
            '8': {"name": "💪 100% Muscle Release", "cost": 80, "dmg": (0, 0), "type": "buff",
                  "effect": "release",
                  "desc": "💪 [100% MUSCLE RELEASE] Raiden releases all 100 seals on his muscles, unleashing his true power! However, the strain deals 50 damage to himself. [TRANSFORMATION: The final seal breaks - Raiden's true power erupts, but his body pays the price]"},
            '9': {"name": "🐦‍⬛ Yatagarasu", "cost": 120, "dmg": (470, 630), "type": "damage",
                  "desc": "🐦‍⬛ [YATAGARASU] 'Three-Legged Crow' - The ultimate palm strike. Raiden focuses power into his legs, channels it to his hand, and delivers a strike that removed four of Shiva's arms. The three-legged crow's power - a strike that silences the arena. [TRANSFORMATION: The three-legged crow's power - a strike that silences the arena]"}
        }

        print(f"\n⚔️ VÖLUNDR: Raiden x Thrud")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → [TRANSFORMATION: Thrud's power fuses")
        print(f"      with Raiden's muscles, allowing")
        print(f"      him to safely release his 100 Seals]")
        return f"✅ Völundr successfully activated for Raiden Tameemon!"

    def apply_effect(self, effect, target=None):
        if effect == "release":
            if self.release_available:
                self.muscle_release = 100
                self.release_available = False
                recoil_damage = 50
                self.take_damage(recoil_damage)
                self.add_status_effect(StatusEffect.MUSCLE_RELEASE, 5)
                self.add_status_effect(StatusEffect.EMPOWER, 5, 2.0)
                return f"💪 [100% RELEASE] 100% Release! Muscles fully unleashed! But the strain deals {recoil_damage} damage! [TRANSFORMATION: The final seal breaks - Raiden's true power erupts]"
            return "❌ Muscle release already used!"
        elif effect == "stun":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.STUN, 2)
            return "🙏 [JIZO'S EMBRACE] The headbutt connects — target is STUNNED for 2 turns!"
        elif effect == "bind":
            tgt = target if target else self
            tgt.add_status_effect(StatusEffect.BIND, 1)
            return "🐗 [WILD BOAR] Raiden's vice-grip catches the target — they are BOUND!"
        elif effect == "defense":
            self.defending = True
            self.add_status_effect(StatusEffect.DEFEND, 1)
            return "⛰️ [MIYAMA] Raiden creates an impenetrable wall of flesh!"
        return ""

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "💪 YATAGARASU",
                "cost": 200,
                "dmg": (600, 800),
                "type": "damage",
                "desc": "💪 [YATAGARASU] Raiden's ultimate palm strike that removed four of Shiva's arms. All of Raiden's muscle power concentrates into a single devastating palm strike. [TRANSFORMATION: All of Raiden's muscle power concentrates into a single devastating palm strike]"
            }
        return self.divine_technique


# ============================================================================
# BUDDHA - The Enlightened One (FIXED with proper story progression)
# ============================================================================

class Buddha(Character):
    def __init__(self):
        super().__init__(
            "Buddha",
            "The Enlightened One • Former God of Fortune",
            1250, 440,
            [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL]
        )
        self.volund_weapon = "Six Realms Staff (六道の杖)"
        self.round = 6
        self.affiliation = "Humanity"
        self.future_sight_active = True
        self.current_emotion = "serenity"
        self.current_weapon = "Twelve Deva Axe"
        self.zerofuku_fused = False
        self.story_trigger = False

        self.weapons = {
            "serenity": {
                "name": "🪓 Twelve Deva Axe (十二天斧)",
                "dmg": (200, 270),
                "desc": "🪓 [TWELVE DEVA AXE] A massive axe that sweeps through opponents with the serenity of enlightenment. The Six Realms staff transforms into an axe of divine judgment — each blow carries the weight of all creation. [TRANSFORMATION: The Six Realms staff transforms into an axe of divine judgment]"
            },
            "determination": {
                "name": "⚔️ Vajra Short Sword (金剛独鈷剣)",
                "dmg": (180, 250),
                "desc": "⚔️ [VAJRA SHORT SWORD] A short sword that strikes with unwavering determination. The staff becomes a single-pronged vajra sword — its blade cuts through suffering itself. [TRANSFORMATION: The staff becomes a single-pronged vajra sword, cutting through suffering]"
            },
            "aggression": {
                "name": "🔨 Giant Spiked Club (正覚涅槃棒)",
                "dmg": (220, 300),
                "desc": "🔨 [GIANT SPIKED CLUB] A brutal spiked club that crushes evil without mercy. The staff becomes a massive enlightened weapon — the Nirvana Club. [TRANSFORMATION: The staff becomes a massive spiked club of enlightenment]"
            },
            "righteous_anger": {
                "name": "🛡️ Shield of Ahimsa (七難即滅の楯)",
                "dmg": (0, 0),
                "desc": "🛡️ [SHIELD OF AHIMSA] A golden shield capable of blocking any attack. The staff becomes a divine barrier — it can withstand even the strikes of the gods. Grants full defense for 1 turn. [TRANSFORMATION: The staff becomes a golden shield that can withstand any assault]"
            },
            "hatred": {
                "name": "🌾 Warscythe of Salakaya (荒神の戦鎌)",
                "dmg": (210, 290),
                "desc": "🌾 [WARSCYTHE OF SALAKAYA] A warscythe that channels the power of dead souls. The staff becomes a weapon of dark enlightenment — channeling the anguish of all who have suffered. [TRANSFORMATION: The staff becomes a warscythe, channeling the souls of the dead]"
            }
        }

        # FIXED: Full ability kit available from the start — no more 3-ability lock
        self.abilities = {
            '1': {"name": "🧘 Activate Six Realms", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "six_realms",
                  "desc": "🧘 [ACTIVATE SIX REALMS] Buddha cycles through the Six Realms of existence — Hell, Hunger, Animals, Asura, Humanity, Heaven. His weapon transforms to match his current emotional state. Each activation randomly shifts his emotion and equips a new divine weapon. [TRANSFORMATION: The staff transforms based on Buddha's current emotion]"},
            '2': {"name": "👁️ Future Sight", "cost": 25, "dmg": (0, 0), "type": "buff", "effect": "future_sight",
                  "desc": "👁️ [FUTURE SIGHT] Buddha's enlightenment allows him to see a few seconds into the future. While active, he can predict enemy attacks and reduce incoming damage by 50% (30% chance per hit). He does not evade — he simply already knows what is coming. [TRANSFORMATION: Time itself becomes transparent — he sees actions before they happen]"},
            '3': {"name": "🧘 Meditation", "cost": 10, "dmg": (0, 0), "type": "heal", "effect": "meditate",
                  "desc": "🧘 [MEDITATION] Buddha enters a state of perfect inner stillness. Wounds close, mind clears, and the body recovers. Restores 80 HP and grants Regen for 2 turns. [TRANSFORMATION: Buddha enters a state of perfect stillness, wounds healing as he reaches inner peace]"},
            '4': {"name": "🪓 Six Realms Strike", "cost": 45, "dmg": (190, 260), "type": "damage", "effect": "six_realms_strike",
                  "desc": "🪓 [SIX REALMS STRIKE] Buddha attacks with his currently equipped Six Realms weapon. Damage type and properties vary based on his current emotional state and weapon form. Serenity favors power, Determination favors speed, Aggression favors brutality. [TRANSFORMATION: The weapon strikes with the weight of all six realms behind it]"},
            '5': {"name": "🧘 Enlightened Counter", "cost": 35, "dmg": (140, 200), "type": "counter", "effect": "enlightened_counter",
                  "desc": "🧘 [ENLIGHTENED COUNTER] Buddha reads the attack before it lands and responds in kind. Uses his Future Sight to anticipate the strike, countering with a precise blow that carries no anger — only truth. [TRANSFORMATION: Serene awareness transforms incoming force into perfectly redirected energy]"},
            '6': {"name": "🌸 Mahaparinirvana", "cost": 120, "dmg": (380, 500), "type": "damage", "effect": "mahaparinirvana",
                  "desc": "🌸 [MAHAPARINIRVANA] The Great Complete Nirvana — Buddha channels the absolute stillness of enlightenment into a devastating strike. This is his peak technique before the Zerofuku fusion. The blow carries the weight of all existence. [TRANSFORMATION: Buddha channels the absolute stillness of enlightenment — the void between thoughts becomes a weapon]"},
            '7': {"name": "🌀 Zerofuku Fusion", "cost": 80, "dmg": (0, 0), "type": "buff", "effect": "zerofuku_fusion",
                  "desc": "🌀 [ZEROFUKU FUSION] Buddha absorbs the accumulated misfortune and suffering of Zerofuku — the god of misery who was once the god of fortune. All that pain, all that sorrow, transforms into the ultimate divine weapon: the Great Nirvana Sword Zero. Can only be used once. [TRANSFORMATION: Zerofuku's very soul dissolves into light and reforms as a seven-branched divine blade in Buddha's hand]"},
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        return "❌ Buddha is a former god — he walks alone. No Völundr."

    def apply_effect(self, effect, target=None):
        if effect == "six_realms":
            emotions = list(self.weapons.keys())
            self.current_emotion = random.choice(emotions)
            weapon = self.weapons[self.current_emotion]

            # Update the six_realms_strike ability to reflect current weapon
            self.abilities['4'] = {
                "name": f"✨ {weapon['name']}",
                "cost": 45,
                "dmg": weapon['dmg'],
                "type": "damage",
                "effect": "six_realms_strike",
                "desc": weapon['desc'],
                "weapon": self.current_emotion
            }

            if self.current_emotion == "righteous_anger":
                self.defending = True
                self.add_status_effect(StatusEffect.DEFEND, 1)

            emotion_descriptions = {
                "serenity":        "Calm and peaceful   — 🪓 Twelve Deva Axe manifests",
                "determination":   "Focused and resolute — ⚔️ Vajra Short Sword appears",
                "aggression":      "Fierce and unyielding — 🔨 Nirvana Club forms",
                "righteous_anger": "Righteous fury       — 🛡️ Shield of Ahimsa emerges (grants DEFEND)",
                "hatred":          "Dark and wrathful    — 🌾 Salakaya Warscythe materializes"
            }

            return (f"🧘 [SIX REALMS] Emotion shifts to: {self.current_emotion.upper()}\n"
                    f"   {emotion_descriptions[self.current_emotion]}\n"
                    f"   {weapon['desc']}")

        elif effect == "six_realms_strike":
            weapon = self.weapons.get(self.current_emotion)
            if weapon:
                bonus_msg = ""
                if self.current_emotion == "aggression":
                    self.add_status_effect(StatusEffect.EMPOWER, 1, 1.2)
                    bonus_msg = " [AGGRESSION BONUS: +20% damage next turn]"
                elif self.current_emotion == "hatred":
                    tgt = target if target else self
                    tgt.add_status_effect(StatusEffect.BLEED, 2)
                    bonus_msg = " [HATRED BONUS: Target bleeds for 2 turns]"
                return f"✨ [{weapon['name']}] Strikes with the power of the {self.current_emotion} realm!{bonus_msg}"
            return ""

        elif effect == "future_sight":
            self.future_sight_active = True
            self.add_status_effect(StatusEffect.FUTURE_SIGHT, 3)
            return "👁️ [FUTURE SIGHT] Activated for 3 turns! 30% chance to reduce incoming damage by 50%. [TRANSFORMATION: Buddha sees moments before they happen, moving preemptively]"

        elif effect == "meditate":
            self.heal(80)
            self.add_status_effect(StatusEffect.REGEN, 2)
            return "🧘 [MEDITATION] Buddha recovers 80 HP and enters Regen state for 2 turns. [TRANSFORMATION: Wounds close as he reaches inner peace]"

        elif effect == "enlightened_counter":
            self.add_status_effect(StatusEffect.DEFEND, 1)
            self.add_status_effect(StatusEffect.COUNTER_READY, 1)
            return "🧘 [ENLIGHTENED COUNTER] Counter stance ready — next attack is read and returned. [TRANSFORMATION: Serene awareness transforms incoming force into perfectly redirected energy]"

        elif effect == "mahaparinirvana":
            self.add_status_effect(StatusEffect.EMPOWER, 1, 1.4)
            return "🌸 [MAHAPARINIRVANA] The Great Complete Nirvana — absolute stillness becomes absolute force! [TRANSFORMATION: The void between thoughts becomes a weapon of ultimate enlightenment]"

        elif effect == "zerofuku_fusion":
            if not self.zerofuku_fused:
                result = self.gain_great_nirvana_sword()
                return result
            return "❌ Zerofuku has already been absorbed. The Great Nirvana Sword Zero is already with you."

        return ""

    def check_soul_light(self, enemy):
        if hasattr(enemy, 'soul_dark') and enemy.soul_dark:
            self.future_sight_active = False
            self.remove_status_effect(StatusEffect.FUTURE_SIGHT)
            self.add_status_effect(StatusEffect.DARK_SOUL, 999)
            return "⚠️ [DARK SOUL] Buddha's Future Sight FAILS — the enemy's soul has no light! The future is dark. [TRANSFORMATION: The future becomes opaque — Hajun's dark soul cannot be read by enlightenment]"
        return "✨ [SOUL LIGHT] The enemy's soul carries light. Future Sight reads them clearly."

    def gain_great_nirvana_sword(self):
        self.zerofuku_fused = True
        self.story_trigger = True

        self.abilities['8'] = {
            "name": "🗡️ Mahaparinirvana Zero (大円寂刀・零)",
            "cost": 150,
            "dmg": (500, 650),
            "type": "damage",
            "desc": "🗡️ [MAHAPARINIRVANA ZERO] The ultimate divine weapon created from Zerofuku's very soul. All the misfortune, all the suffering, all the sorrow that Zerofuku ever carried — it becomes a seven-branched sword of perfect liberation. The Great Nirvana Sword Zero. [TRANSFORMATION: Zerofuku's soul dissolves and reforms as a radiant seven-branched blade — the apex of Buddha's power]"
        }
        self.divine_technique = self.abilities['8']
        self.add_status_effect(StatusEffect.NIRVANA_SWORD, 999)

        # Hide the fusion ability now that it's been used (consumed)
        if '7' in self.abilities:
            del self.abilities['7']

        return ("✨✨✨ [ZEROFUKU FUSION] ✨✨✨\n"
                "   Zerofuku's soul dissolves into light...\n"
                "   All his misfortune, all his suffering —\n"
                "   Every tear, every failure, every cry for help...\n"
                "   It all becomes ONE seven-branched sword.\n"
                "   🗡️ THE GREAT NIRVANA SWORD ZERO IS BORN! 🗡️\n"
                "   [TRANSFORMATION: Zerofuku's very being becomes a divine blade in Buddha's hands]\n"
                "   → Divine Technique unlocked: Mahaparinirvana Zero")

    def ensure_divine_technique(self):
        # FIXED: If not yet fused in non-tournament modes, give Buddha his full technique
        # so he is not permanently stuck without a divine technique
        if not self.divine_technique:
            if self.zerofuku_fused:
                self.divine_technique = self.abilities.get('8', None)
            else:
                # Provide a base divine technique pre-fusion so he is always playable
                self.divine_technique = {
                    "name": "🌸 MAHAPARINIRVANA: Great Complete Nirvana",
                    "cost": 160,
                    "dmg": (430, 570),
                    "type": "damage",
                    "desc": "🌸 [MAHAPARINIRVANA] Buddha's peak technique before the Zerofuku fusion. The Great Complete Nirvana — absolute stillness, absolute force. He who has transcended all desires strikes with the weight of all existence. Use Zerofuku Fusion first to unlock the true ultimate: Mahaparinirvana Zero. [TRANSFORMATION: The void between all thoughts becomes the sharpest blade]"
                }
        return self.divine_technique

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()

        # Bonus damage when Zerofuku has been fused
        if self.zerofuku_fused:
            mult *= 1.3
            buffs.append("🗡️ NIRVANA SWORD (+30%)")

        # Emotion-based damage modifier
        emotion_bonus = {
            "serenity": 1.0,
            "determination": 1.05,
            "aggression": 1.15,
            "righteous_anger": 0.9,   # defensive stance
            "hatred": 1.2
        }
        emotion_mult = emotion_bonus.get(self.current_emotion, 1.0)
        if emotion_mult != 1.0:
            mult *= emotion_mult
            buffs.append(f"🧘 {self.current_emotion.upper()} REALM")

        return mult, buffs

    def reset_volund(self):
        """FIXED: Buddha override also resets fusion state fully."""
        super().reset_volund()
        self.zerofuku_fused = False
        self.story_trigger = False
        self.divine_technique = None
        # Restore full 7-ability base kit including fusion option
        self.abilities = dict(self._base_abilities)
        # Ensure fusion ability is present (in case base snapshot was taken without it)
        if '7' not in self.abilities:
            self.abilities['7'] = {
                "name": "🌀 Zerofuku Fusion", "cost": 80, "dmg": (0, 0),
                "type": "buff", "effect": "zerofuku_fusion",
                "desc": "🌀 [ZEROFUKU FUSION] Absorb Zerofuku's accumulated misfortune and unlock the Great Nirvana Sword Zero. Can only be used once per battle."
            }
        self.abilities.pop('8', None)  # Remove post-fusion nirvana sword if present


# ============================================================================
# QIN SHI HUANG - First Emperor (FIXED with chi flow mechanics and counter timer)
# ============================================================================

class QinShiHuang(Character):
    def __init__(self):
        super().__init__(
            "Qin Shi Huang",
            "First Emperor • China",
            1280, 430,
            [Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL]
        )
        self.round = 7
        self.affiliation = "Humanity"
        self.armor_form = True
        self.star_eyes_active = False
        self.chi_flow = False
        self.phoenix_active = False
        self.counter_ready = False
        self.counter_timer = 0  # FIXED: Track counter duration

        self.abilities = {
            '1': {"name": "👑 Imperial Strike", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "👑 [IMPERIAL STRIKE] A basic strike from the First Emperor."}
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.ALVITR:
            return f"❌ Qin can only bond with Alvitr!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Pauldron of Divine Embrace / First Emperor's Goujian Sword (神羅鎧袖 / 始皇勾践剣)"
        self.add_status_effect(StatusEffect.VOLUNDR, 999)

        self.divine_technique = {
            "name": "👑 FIRST EMPEROR'S POWER EMBRACE - SWALLOW SLASH",
            "cost": 190,
            "dmg": (580, 750),
            "type": "damage",
            "desc": "👑 [FIRST EMPEROR'S POWER EMBRACE - SWALLOW SLASH] Qin's ultimate technique combining all five Chiyou styles into one devastating counter. The Pauldron of Divine Embrace transforms into the First Emperor's Goujian Sword for this ultimate strike. [TRANSFORMATION: The Pauldron of Divine Embrace transforms into the First Emperor's Goujian Sword for this ultimate strike]"
        }

        self.abilities = {
            '1': {"name": "👑 Imperial Strike", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "👑 [IMPERIAL STRIKE] A basic strike from the First Emperor."},
            '2': {"name": "👁️ Remove Blindfold", "cost": 15, "dmg": (0, 0), "type": "buff",
                  "effect": "blindfold",
                  "desc": "👁️ [REMOVE BLINDFOLD] Qin removes his blindfold, revealing his star-like eyes. The blindfold falls, revealing eyes that can see the flow of Chi itself. [TRANSFORMATION: The blindfold falls, revealing eyes that can see the flow of Chi itself]"},
            '3': {"name": "🐉 Mount Tai Dragon Claw", "cost": 45, "dmg": (240, 320), "type": "damage",
                  "desc": "🐉 [MOUNT TAI DRAGON CLAW] Chiyou Spear Style - Qin pierces through the opponent with zhijiatao on his fingers. Qi flows through fingers, turning them into piercing dragon claws. [TRANSFORMATION: Qi flows through fingers, turning them into piercing dragon claws]"},
            '4': {"name": "🐢 Drifting Tortoise", "cost": 35, "dmg": (0, 0), "type": "utility",
                  "effect": "drifting_tortoise",
                  "desc": "🐢 [DRIFTING TORTOISE] Chiyou Crossbow Style - Qin fires an invisible air bullet from his mouth to strike the cruxes of Chi flow. Compressed air becomes an invisible bullet that disrupts enemy techniques. [TRANSFORMATION: Compressed air becomes an invisible bullet that disrupts enemy techniques]"},
            '5': {"name": "🐅 White Tiger Moon Arc", "cost": 40, "dmg": (210, 290), "type": "damage",
                  "desc": "🐅 [WHITE TIGER MOON ARC] Chiyou Halberd Style - Qin lifts his leg and swings in a crescent arc. This kick blew back Hades and tore his arm. The leg becomes a halberd - crescent moon of destruction. [TRANSFORMATION: The leg becomes a halberd - crescent moon of destruction]"},
            '6': {"name": "🐦 First Emperor's Swallow Slash", "cost": 100, "dmg": (470, 610), "type": "damage",
                  "desc": "🐦 [FIRST EMPEROR'S SWALLOW SLASH] Chiyou Sword Style - Qin unleashes a simple forward slash containing all his power. All five martial arts flow into one devastating slash. [TRANSFORMATION: All five martial arts flow into one devastating slash]"},
            '7': {"name": "🔥 Heavenly Phoenix's Power Embrace", "cost": 50, "dmg": (0, 0), "type": "counter",
                  "effect": "phoenix_embrace",
                  "desc": "🔥 [HEAVENLY PHOENIX'S POWER EMBRACE] Chiyou Armor Style - Qin intercepts an attack and absorbs its energy, redirecting it back at the opponent. The phoenix's wings embrace incoming force and return it multiplied. [TRANSFORMATION: The phoenix's wings embrace incoming force and return it multiplied]"}
        }

        print(f"\n⚔️ VÖLUNDR: Qin x Alvitr")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → [TRANSFORMATION: Alvitr's power")
        print(f"      manifests as golden armor - can")
        print(f"      transform into the First Emperor's")
        print(f"      Goujian Sword]")
        return f"✅ Völundr successfully activated for Qin Shi Huang!"

    def take_damage(self, dmg, ignore_defense=False):
        if self.armor_form and not ignore_defense:
            reduced = int(dmg * 0.75)  # 25% damage reduction while armor is active
            result = super().take_damage(reduced, ignore_defense)
            return result
        return super().take_damage(dmg, ignore_defense)

    def apply_effect(self, effect, target=None):
        if effect == "blindfold":
            self.star_eyes_active = True
            self.chi_flow = True
            self.armor_form = False  # Removing blindfold sheds the armor form
            self.add_status_effect(StatusEffect.STAR_EYES, 999)
            self.add_status_effect(StatusEffect.CHI_FLOW, 999)
            return "👁️ [STAR EYES] Qin removes blindfold - can see Chi flow! Armor form released. [TRANSFORMATION: His eyes reveal the flow of Qi in all living things - he can see the cruxes of power]"
        elif effect == "drifting_tortoise":
            self.add_status_effect(StatusEffect.CHI_CRUX, 1)
            return "🐢 [DRIFTING TORTOISE] Air bullet fired! Enemy technique weakened! [TRANSFORMATION: The crux of Chi has been struck - their technique falters]"
        elif effect == "phoenix_embrace":
            self.defending = True
            self.phoenix_active = True
            self.counter_ready = True
            self.counter_timer = 2  # Lasts 2 turns
            self.add_status_effect(StatusEffect.PHOENIX, 1)
            self.add_status_effect(StatusEffect.COUNTER_READY, 2)
            self.add_status_effect(StatusEffect.DEFEND, 1)
            return "🔥 [HEAVENLY PHOENIX] Power absorbed! Next attack within 2 turns will be countered! [TRANSFORMATION: The phoenix's wings embrace the incoming attack, preparing to return it]"
        return ""

    def update_status_effects(self):
        super().update_status_effects()
        if self.counter_timer > 0:
            self.counter_timer -= 1
            if self.counter_timer <= 0:
                self.counter_ready = False
                self.remove_status_effect(StatusEffect.COUNTER_READY)

    def counter_attack(self, incoming_damage, attacker):
        if self.counter_ready:
            self.counter_ready = False
            self.counter_timer = 0
            self.remove_status_effect(StatusEffect.COUNTER_READY)
            counter_damage = int(incoming_damage * 1.5)
            attacker.take_damage(counter_damage, ignore_defense=True)
            return f"🔥 [PHOENIX COUNTER] Qin redirects the attack for {counter_damage} damage!"
        return None

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "👑 FIRST EMPEROR'S POWER EMBRACE - SWALLOW SLASH",
                "cost": 190,
                "dmg": (580, 750),
                "type": "damage",
                "desc": "👑 [FIRST EMPEROR'S POWER EMBRACE - SWALLOW SLASH] Qin's ultimate technique combining all five Chiyou styles into one devastating counter. The Pauldron of Divine Embrace transforms into the First Emperor's Goujian Sword for this ultimate strike. [TRANSFORMATION: The Pauldron of Divine Embrace transforms into the First Emperor's Goujian Sword for this ultimate strike]"
            }
        return self.divine_technique


# ============================================================================
# NIKOLA TESLA - Greatest Inventor (FIXED with movement mechanics)
# ============================================================================

class NikolaTesla(Character):
    def __init__(self):
        super().__init__(
            "Nikola Tesla",
            "Greatest Inventor • Serbia",
            1220, 440,
            [Realm.GODLY_TECHNIQUE]
        )
        self.round = 8
        self.affiliation = "Humanity"
        self.teleport_charges = 3
        self.gematria_zone_active = False
        self.zero_max = False
        self.tesla_step = False

        self.abilities = {
            '1': {"name": "⚡ Basic Punch", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "⚡ [BASIC PUNCH] A basic punch."}
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.GÖNDUL:
            return f"❌ Tesla can only bond with Göndul!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Super Automaton Beta (超人自動機械β)"
        self.add_status_effect(StatusEffect.VOLUNDR, 999)

        self.divine_technique = {
            "name": "⚡ PLASMA PULSE PUNCH CROSS (PPPX)",
            "cost": 200,
            "dmg": (600, 780),
            "type": "damage",
            "desc": "⚡ [PLASMA PULSE PUNCH CROSS] Tesla's ultimate technique. He feigns an attack with one fist while teleporting the other. Tesla Warp synchronizes with a feint - one fist attacks from the front while the other teleports behind. [TRANSFORMATION: Tesla Warp synchronizes with a feint - one fist attacks from the front while the other teleports behind]"
        }

        self.abilities = {
            '1': {"name": "⚡ Basic Punch", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "⚡ [BASIC PUNCH] A basic punch."},
            '2': {"name": "⚡ Plasma Pulse Punch (PPP)", "cost": 25, "dmg": (160, 220), "type": "damage",
                  "desc": "⚡ [PPP] Tesla converts Göndul's life energy into ultra-high voltage within Super Automaton Beta, concentrating all of this power in his fist and releasing it instantaneously. Electrical energy explodes on impact, splitting the ground. [TRANSFORMATION: Electrical energy explodes on impact, splitting the ground]"},
            '3': {"name": "⚡ Plasma Pulse Jet Punch (PPJP)", "cost": 30, "dmg": (180, 250), "type": "damage",
                  "desc": "⚡ [PPJP] Tesla puts his left hand behind him and releases a large amount of electricity to close the distance between him and his opponent. He then strikes his opponent in the head with his right fist, releasing electricity at the same time. Jet propulsion from electrical discharge creates a rocket punch. [TRANSFORMATION: Jet propulsion from electrical discharge creates a rocket punch]"},
            '4': {"name": "⚡ Plasma Pulse Punch Twin (PPPT)", "cost": 35, "dmg": (210, 290), "type": "damage",
                  "desc": "⚡ [PPPT] Tesla releases electricity while putting both fists together. He then strikes using both of his fists at the same time. Twin plasma fists - double the impact. [TRANSFORMATION: Twin plasma fists - double the impact]"},
            '5': {"name": "⚡ Plasma Pulse Punch Surprise (PPPS)", "cost": 40, "dmg": (240, 330), "type": "damage",
                  "desc": "⚡ [PPPS] While floating in Gematria Zone, Tesla leans back nearly touching the ground, spins continuously, and leaps while releasing PPP. A spinning drill of plasma from an unexpected angle. [TRANSFORMATION: A spinning drill of plasma from an unexpected angle]"},
            '6': {"name": "⚡ Plasma Pulse Punch Mobius (PPP∞)", "cost": 60, "dmg": (300, 400), "type": "damage",
                  "desc": "⚡ [PPP MOBIUS] Tesla unleashes an endless onslaught of punches so fast it's impossible to see where one ends and the next begins. Infinite loop of plasma punches - the Mobius strip of destruction. [TRANSFORMATION: Infinite loop of plasma punches - the Mobius strip of destruction]"},
            '7': {"name": "⚡ Plasma Pulse Punch Jet (PPPJ)", "cost": 35, "dmg": (200, 280), "type": "damage",
                  "desc": "⚡ [PPPJ] If falling back, Tesla puts one hand on the ground and releases electricity to propel himself back up at high speed. Ground becomes a launchpad - rising plasma fist. [TRANSFORMATION: Ground becomes a launchpad - rising plasma fist]"},
            '8': {"name": "⚡ Plasma Pulse Punch Cross (PPPX)", "cost": 120, "dmg": (500, 650), "type": "damage",
                  "desc": "⚡ [PPP CROSS] Tesla feigns attack with one fist while using Tesla Warp to teleport the other behind the opponent. Pincer attack from front and back simultaneously. [TRANSFORMATION: Pincer attack from front and back simultaneously]"},
            '9': {"name": "🔬 Gematria Zone", "cost": 50, "dmg": (0, 0), "type": "buff",
                  "effect": "gematria",
                  "desc": "🔬 [GEMATRIA ZONE] Tesla creates a zone of altered space-time. Super Tesla Particles fill a 9.63m by 9.63m cage, creating a space where physics bend to Tesla's will. [TRANSFORMATION: Super Tesla Particles fill a 9.63m by 9.63m cage, creating a space where physics bend to Tesla's will]"},
            '10': {"name": "⚡ Tesla Warp", "cost": 60, "dmg": (0, 0), "type": "utility",
                   "effect": "teleport",
                   "desc": "⚡ [TESLA WARP] Tesla warps through space. 3 uses. The Super Tesla Coil synchronizes with particle-dense areas, allowing instantaneous teleportation. [TRANSFORMATION: The Super Tesla Coil synchronizes with particle-dense areas, allowing instantaneous teleportation]"},
            '11': {"name": "⚡ Zero Max", "cost": 0, "dmg": (0, 0), "type": "passive",
                   "effect": "zero_max",
                   "desc": "⚡ [ZERO MAX] Within Gematria Zone, Tesla's anti-gravity system allows him to reach maximum speed in just the first stride. Super Tesla Particles eliminate inertia - from zero to max in an instant. [TRANSFORMATION: Super Tesla Particles eliminate inertia - from zero to max in an instant]"},
            '12': {"name": "⚡ Tesla Step", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "tesla_step",
                   "desc": "⚡ [TESLA STEP] Tesla floats and moves in unpredictable patterns within Gematria Zone. Tesla Step Wonderful creates numerous afterimages. Super Tesla Particles allow three-dimensional movement - gravity is optional. [TRANSFORMATION: Super Tesla Particles allow three-dimensional movement - gravity is optional]"}
        }

        print(f"\n⚔️ VÖLUNDR: Tesla x Göndul")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → [TRANSFORMATION: Göndul's magic fuses")
        print(f"      with Tesla's technology - a suit")
        print(f"      that can manipulate space-time")
        print(f"      itself]")
        return f"✅ Völundr successfully activated for Nikola Tesla!"

    def apply_effect(self, effect, target=None):
        if effect == "gematria":
            self.gematria_zone_active = True
            self.zero_max = True
            self.add_status_effect(StatusEffect.GEMATRIA_ZONE, 5)
            self.add_status_effect(StatusEffect.ZERO_MAX, 5)
            return "🔬 [GEMATRIA ZONE] Gematria Zone activated! [TRANSFORMATION: Super Tesla Particles fill the area - Tesla can now float and teleport within this 9.63m cage]"
        elif effect == "teleport":
            if self.teleport_charges > 0 and self.gematria_zone_active:
                self.teleport_charges -= 1
                self.add_status_effect(StatusEffect.TESLA_WARP, 1)
                self.add_status_effect(StatusEffect.EVASION, 1, 0.9)
                return f"⚡ [TESLA WARP] Tesla Warp! {self.teleport_charges} charges remaining [TRANSFORMATION: The Super Tesla Coil glows brightly as Tesla instantaneously repositions through space]"
            return "❌ Cannot teleport! [Gematria Zone must be active and charges remaining]"
        elif effect == "tesla_step":
            self.tesla_step = True
            self.add_status_effect(StatusEffect.TESLA_STEP, 3)
            self.add_status_effect(StatusEffect.EVASION, 3, 0.3)
            return "⚡ [TESLA STEP] Tesla moves with unpredictable three-dimensional steps! [TRANSFORMATION: Super Tesla Particles allow levitation and impossible movement patterns]"
        elif effect == "zero_max":
            # FIXED: Also applies ZERO_MAX status (was only granting HASTE)
            self.add_status_effect(StatusEffect.HASTE, 2)
            self.add_status_effect(StatusEffect.ZERO_MAX, 2)
            return "⚡ [ZERO MAX] Tesla reaches ZERO MAX — absolute maximum speed! [TRANSFORMATION: Every neuron fires simultaneously — Tesla becomes a blur even gods cannot track]"
        return ""

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "⚡ PLASMA PULSE PUNCH CROSS (PPPX)",
                "cost": 200,
                "dmg": (600, 780),
                "type": "damage",
                "desc": "⚡ [PLASMA PULSE PUNCH CROSS] Tesla's ultimate technique. He feigns an attack with one fist while teleporting the other. Tesla Warp synchronizes with a feint - one fist attacks from the front while the other teleports behind. [TRANSFORMATION: Tesla Warp synchronizes with a feint - one fist attacks from the front while the other teleports behind]"
            }
        return self.divine_technique


# ============================================================================
# LEONIDAS - King of Sparta (FIXED with form checks)
# ============================================================================

class Leonidas(Character):
    def __init__(self):
        super().__init__(
            "Leonidas",
            "King of Sparta • Greece",
            1350, 430,
            [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE]
        )
        self.round = 9
        self.affiliation = "Humanity"
        self.shield_form = "base"

        self.abilities = {
            '1': {"name": "🛡️ Spartan Kick", "cost": 15, "dmg": (140, 190), "type": "damage",
                  "desc": "🛡️ [SPARTAN KICK] The iconic Spartan kick."}
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.GEIRÖLUL:
            return f"❌ Leonidas can only bond with Geirölul!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Aspis Shield (アスピス)"
        self.add_status_effect(StatusEffect.VOLUNDR, 999)

        self.divine_technique = {
            "name": "🛡️ PHALANX LAMBDA",
            "cost": 180,
            "dmg": (580, 750),
            "type": "damage",
            "desc": "🛡️ [PHALANX LAMBDA] Leonidas's ultimate technique - a straightforward charge that embodies the Spartan phalanx. The shield becomes an unstoppable battering ram, embodying the spirit of Sparta. [TRANSFORMATION: The shield becomes an unstoppable battering ram, embodying the spirit of Sparta]"
        }

        self.abilities = {
            '1': {"name": "🛡️ Spartan Kick", "cost": 15, "dmg": (140, 190), "type": "damage",
                  "desc": "🛡️ [SPARTAN KICK] The iconic Spartan kick."},
            '2': {"name": "🛡️ Aspis Shield", "cost": 25, "dmg": (150, 210), "type": "damage",
                  "desc": "🛡️ [ASPIS SHIELD] Leonidas uses his shield as both defense and offense. The shield can be used for devastating bashes. [TRANSFORMATION: The shield can be used for devastating bashes]"},
            '3': {"name": "🛡️ Saw Form", "cost": 40, "dmg": (220, 300), "type": "damage",
                  "effect": "saw_form",
                  "desc": "🛡️ [SAW FORM] Geirölul transforms into a saw blade. The shield's center rises, revealing spinning blades - now a DIVINE SAW. [TRANSFORMATION: The shield's center rises, revealing spinning blades - now a DIVINE SAW]"},
            '4': {"name": "🔨 Hammer Form", "cost": 50, "dmg": (290, 370), "type": "damage",
                  "effect": "hammer_form",
                  "desc": "🔨 [HAMMER FORM] Geirölul transforms into a massive hammer. The shield splits into six legs that form a massive hammer head - now a DIVINE HAMMER. [TRANSFORMATION: The shield splits into six legs that form a massive hammer head - now a DIVINE HAMMER]"},
            '5': {"name": "🛡️ Phalanx Lambda", "cost": 100, "dmg": (470, 610), "type": "damage",
                  "desc": "🛡️ [PHALANX LAMBDA] Leonidas's ultimate technique. The Aletheia Sparta - the shield's true form revealed, charging forward with the weight of Spartan history. [TRANSFORMATION: The Aletheia Sparta - the shield's true form revealed, charging forward with the weight of Spartan history]"},
            '6': {"name": "🛡️ Phalanx Asanatos", "cost": 30, "dmg": (170, 240), "type": "damage",
                  "desc": "🛡️ [PHALANX ASANATOS] Leonidas extends his shield by a chain and launches it in rapid succession, leaving afterimages. The shield becomes a meteor on a chain. [TRANSFORMATION: The shield becomes a meteor on a chain]"},
            '7': {"name": "🛡️ Phalanx Enochos", "cost": 45, "dmg": (240, 320), "type": "damage", "saw_only": True,
                  "desc": "🛡️ [PHALANX ENOCHOS] In Saw Form, Leonidas launches the spinning blades at his opponent. Even Apollo couldn't hold it back. A divine saw blade on a chain - it WILL cut through. [TRANSFORMATION: A divine saw blade on a chain - it WILL cut through]"},
            '8': {"name": "🛡️ Phalanx Enochos: Prodevo", "cost": 55, "dmg": (280, 370), "type": "damage",
                  "saw_only": True,
                  "desc": "🛡️ [PHALANX ENOCHOS: PRODEVŌ] Leonidas embeds the spinning blades into the ground behind him and drags them forward toward his opponent. The ground itself is torn apart as divine saws carve through. [TRANSFORMATION: The ground itself is torn apart as divine saws carve through]"},
            '9': {"name": "🔨 Phalanx Nemesis", "cost": 80, "dmg": (400, 520), "type": "damage", "hammer_only": True,
                  "desc": "🔨 [PHALANX NEMESIS] In Hammer Form, Leonidas lifts his hammer back and swings it down with enough force to shatter the entire arena floor. The hammer of Nemesis - divine punishment incarnate. [TRANSFORMATION: The hammer of Nemesis - divine punishment incarnate]"}
        }

        print(f"\n⚔️ VÖLUNDR: Leonidas x Geirölul")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → [TRANSFORMATION: Geirölul fuses")
        print(f"      with his shield, allowing it to")
        print(f"      transform between base, saw, and")
        print(f"      hammer forms]")
        return f"✅ Völundr successfully activated for Leonidas!"

    def apply_effect(self, effect, target=None):
        if effect == "phalanx":
            self.defending = True
            self.add_status_effect(StatusEffect.PHALANX, 1)
            self.add_status_effect(StatusEffect.DEFEND, 1)
            self.add_status_effect(StatusEffect.SHIELD, 1, 0.5)
            return "🛡️ [PHALANX] Leonidas raises his shield — the Spartan phalanx holds! 50% damage reduction this turn."
        elif effect == "shield_form":
            self.shield_form = "base"
            self.add_status_effect(StatusEffect.SHIELD_FORM, 3)
            return "🛡️ [SHIELD FORM] Geirölul returns to its base shield configuration — pure Spartan defense."
        elif effect == "saw_form":
            self.shield_form = "saw"
            self.add_status_effect(StatusEffect.SAW_FORM, 5)
            return "🛡️ [SAW FORM] Shield transforms into Saw Form! [TRANSFORMATION: Spinning blades emerge from the shield's center - it can now tear through divine flesh]"
        elif effect == "hammer_form":
            self.shield_form = "hammer"
            self.add_status_effect(StatusEffect.HAMMER_FORM, 5)
            return "🔨 [HAMMER FORM] Shield transforms into Hammer Form! [TRANSFORMATION: The shield splits and reforms into a massive divine hammer - capable of crushing gods]"
        return ""

    def can_use_ability(self, ability=None):
        if ability and ability.get("saw_only") and self.shield_form != "saw":
            return False, "❌ This ability requires Saw Form!"
        if ability and ability.get("hammer_only") and self.shield_form != "hammer":
            return False, "❌ This ability requires Hammer Form!"
        return True, ""

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()

        if self.shield_form == "saw":
            mult *= 1.3
            buffs.append("⚙️ SAW FORM")
        elif self.shield_form == "hammer":
            mult *= 1.5
            buffs.append("🔨 HAMMER FORM")

        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "🛡️ PHALANX LAMBDA",
                "cost": 180,
                "dmg": (580, 750),
                "type": "damage",
                "desc": "🛡️ [PHALANX LAMBDA] Leonidas's ultimate technique - a straightforward charge that embodies the Spartan phalanx. The shield becomes an unstoppable battering ram, embodying the spirit of Sparta. [TRANSFORMATION: The shield becomes an unstoppable battering ram, embodying the spirit of Sparta]"
            }
        return self.divine_technique


# ============================================================================
# SOJI OKITA - Captain of Shinsengumi (FIXED with multi-hit and illness as HP damage)
# ============================================================================

class SojiOkita(Character):
    def __init__(self):
        super().__init__(
            "Soji Okita",
            "Captain of Shinsengumi • Japan",
            1250, 420,
            [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE]
        )
        self.round = 10
        self.affiliation = "Humanity"
        self.demon_child_active = False
        self.demon_child_release = False
        self.illness_effect = 0
        self.illness_timer = 0
        self.demon_available = True

        self.abilities = {
            '1': {"name": "⚔️ Quick Draw", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "⚔️ [QUICK DRAW] A quick sword draw."}
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.SKALMÖLD:
            return f"❌ Soji can only bond with Skalmöld!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Divine Katana (神器刀)"
        self.add_status_effect(StatusEffect.VOLUNDR, 999)

        self.divine_technique = {
            "name": "⚔️ ENPI REITEN",
            "cost": 220,
            "dmg": (650, 850),
            "type": "damage",
            "desc": "⚔️ [ENPI REITEN] Soji's ultimate technique - over 80 sword techniques in rapid succession. Every sword technique Soji ever conceived flows into one endless onslaught - past, present, and future techniques combined. [TRANSFORMATION: Every sword technique Soji ever conceived flows into one endless onslaught - past, present, and future techniques combined]"
        }

        self.abilities = {
            '1': {"name": "⚔️ Quick Draw", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "⚔️ [QUICK DRAW] A quick sword draw."},
            '2': {"name": "⚔️ Three-Stage Thrust", "cost": 40, "dmg": (220, 290), "type": "damage",
                  "hits": 3,
                  "desc": "⚔️ [THREE-STAGE THRUST] 'Sandanzuki' - Three thrusts delivered in the time it takes most to deliver one. Godspeed thrusts - three strikes in the span of one. [TRANSFORMATION: Godspeed thrusts - three strikes in the span of one]"},
            '3': {"name": "👹 Demon Child Awakening", "cost": 50, "dmg": (0, 0), "type": "buff",
                  "effect": "demon_child",
                  "desc": "👹 [DEMON CHILD AWAKENING] Soji awakens the demon child within. His heart pumps three times more blood - muscle cells awaken, eyes glow red. [TRANSFORMATION: His heart pumps three times more blood - muscle cells awaken, eyes glow red]"},
            '4': {"name": "👹 Demon Child Release", "cost": 100, "dmg": (0, 0), "type": "buff",
                  "effect": "demon_release",
                  "desc": "👹 [DEMON CHILD RELEASE] Soji fully releases the demon child. The demon within fully awakens - sclera turn red, dark red aura emanates, power beyond human limits. [TRANSFORMATION: The demon within fully awakens - sclera turn red, dark red aura emanates, power beyond human limits]"},
            '5': {"name": "⚔️ Enpi Reiten", "cost": 150, "dmg": (550, 730), "type": "damage",
                  "hits": 8,
                  "desc": "⚔️ [ENPI REITEN] 'Black Kite's Heavenly Return' - Eighty techniques flowing as one. Over 80 sword techniques from the Ten'nen Rishin Style flow together in an endless onslaught. [TRANSFORMATION: Over 80 sword techniques from the Ten'nen Rishin Style flow together in an endless onslaught]"},
            '6': {"name": "⚔️ Ryuubiken", "cost": 35, "dmg": (180, 250), "type": "damage",
                  "desc": "⚔️ [RYUUBIKEN] 'Dragon Tail's Sword' - Soji swings his katana downward, then instantly changes direction and swings upward from a lower level, aiming for the opponent's torso. The blade becomes like a dragon's tail - unpredictable and devastating. [TRANSFORMATION: The blade becomes like a dragon's tail - unpredictable and devastating]"},
            '7': {"name": "⚔️ Kisousandanzuki", "cost": 60, "dmg": (330, 410), "type": "damage",
                  "hits": 3,
                  "desc": "⚔️ [KISOUSANDANZUKI] 'Demon's Claw Three Stage Thrust' - A crouched stance with katana held upside-down above the head. Performs Kisoutotsu with the mechanics of Three Stage Thrust. Surpasses 'godspeed' itself. The Demon Child fully awakens - this attack pierces the boundary between humanity and divinity. [TRANSFORMATION: The Demon Child fully awakens - this attack pierces the boundary between humanity and divinity]"},
            '8': {"name": "⚔️ Tenshou Sandanzuki", "cost": 80, "dmg": (400, 520), "type": "damage",
                  "hits": 3, "range": "extended",
                  "desc": "⚔️ [TENSHOU SANDANZUKI] 'Heavenly Flight Three Stage Thrust' - An advanced version where Soji lunges forward and delivers three thrusts projected beyond the katana's range, targeting vital points. The same concept as Susano'o's Ama no Magaeshi. The blade 'flies' - sword energy extends beyond physical reach to strike from impossible distances. [TRANSFORMATION: The blade 'flies' - sword energy extends beyond physical reach to strike from impossible distances]"}
        }

        print(f"\n⚔️ VÖLUNDR: Soji x Skalmöld")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → [TRANSFORMATION: Skalmöld draws out")
        print(f"      Soji's past, present, and future")
        print(f"      potential - all his sword ability")
        print(f"      condensed into this moment]")
        return f"✅ Völundr successfully activated for Soji Okita!"

    def apply_effect(self, effect, target=None):
        if effect == "demon_child":
            if self.demon_available:
                self.demon_child_active = True
                self.illness_effect += 10
                self.illness_timer = 5
                self.add_status_effect(StatusEffect.DEMON_CHILD, 5)
                self.add_status_effect(StatusEffect.EMPOWER, 5, 1.5)
                self.add_status_effect(StatusEffect.ILLNESS, 999, stacks=self.illness_effect)  # Managed manually
                return f"👹 [DEMON CHILD] Demon Child awakened! Illness: {self.illness_effect}% [TRANSFORMATION: Blood pumps faster, muscles awaken - but the illness that killed him stirs as well]"
            return "❌ Demon Child cannot be awakened again!"
        elif effect == "demon_release":
            if self.demon_child_active and self.demon_available:
                self.demon_child_release = True
                self.demon_available = False
                self.divine_mode = True
                self.divine_timer = 3
                self.add_status_effect(StatusEffect.DEMON_RELEASE, 3)
                self.add_status_effect(StatusEffect.EMPOWER, 3, 2.5)
                return "👹 [DEMON CHILD RELEASE] DEMON CHILD RELEASE! Soji surpasses all limits! [TRANSFORMATION: The demon within fully awakens - eyes and aura turn crimson, power skyrocketing beyond humanity]"
            return "❌ Cannot release Demon Child without awakening!"
        return ""

    def update_status_effects(self):
        super().update_status_effects()
        if self.illness_timer > 0 and self.has_status_effect(StatusEffect.ILLNESS):
            illness_damage = 15 + int(self.illness_effect * 1.5)
            self.take_damage(illness_damage, ignore_defense=True)
            print(f"  🤒 [ILLNESS] Soji takes {illness_damage} damage from his illness!")
            self.illness_timer -= 1
            if self.illness_timer <= 0:
                self.remove_status_effect(StatusEffect.ILLNESS)
                print(f"  🤒 Soji's illness stabilizes.")

    def get_damage_multiplier(self):
        mult, buffs = super().get_damage_multiplier()
        return mult, buffs

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "⚔️ ENPI REITEN",
                "cost": 220,
                "dmg": (650, 850),
                "type": "damage",
                "desc": "⚔️ [ENPI REITEN] Soji's ultimate technique - over 80 sword techniques in rapid succession. Every sword technique Soji ever conceived flows into one endless onslaught - past, present, and future techniques combined. [TRANSFORMATION: Every sword technique Soji ever conceived flows into one endless onslaught - past, present, and future techniques combined]"
            }
        return self.divine_technique


# ============================================================================
# SIMO HÄYHÄ - White Death (FIXED with organ sacrifice for all abilities)
# ============================================================================

class SimoHayha(Character):
    def __init__(self):
        super().__init__(
            "Simo Häyhä",
            "White Death • Finland",
            1200, 410,
            [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE]
        )
        self.round = 11
        self.affiliation = "Humanity"
        self.organ_sacrifice = 0
        self.organs = ["kidney (right)", "kidney (left)", "liver", "spleen", "pancreas", "appendix"]
        self.organs_used = []
        self.camouflage_active = False

        self.abilities = {
            '1': {"name": "❄️ Rifle Shot", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "❄️ [RIFLE SHOT] A precise rifle shot."}
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.RÁÐGRÍÐR:
            return f"❌ Simo can only bond with Ráðgríðr!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "M28-30 Rifle (モシン・ナガンM28-30)"
        self.add_status_effect(StatusEffect.VOLUNDR, 999)

        self.divine_technique = {
            "name": "❄️ UKONVASARA",
            "cost": 250,
            "dmg": (700, 900),
            "type": "damage",
            "desc": "❄️ [UKONVASARA] Simo's ultimate shot. He sacrifices his pancreas to fire a bullet of pure white death. His pancreas becomes the bullet - the Hammer of Ukko, the supreme god of Finnish mythology, manifested as a sniper round. [TRANSFORMATION: His pancreas becomes the bullet - the Hammer of Ukko, the supreme god of Finnish mythology, manifested as a sniper round]"
        }

        self.abilities = {
            '1': {"name": "❄️ Rifle Shot", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "❄️ [RIFLE SHOT] A precise rifle shot."},
            '2': {"name": "❄️ White Death Shot", "cost": 25, "dmg": (170, 230), "type": "damage",
                  "desc": "❄️ [WHITE DEATH SHOT] A precision rifle shot from the White Death himself. Each shot carries the chill of the Finnish winter. [TRANSFORMATION: Each shot carries the chill of the Finnish winter]"},
            '3': {"name": "❄️ Camouflage", "cost": 20, "dmg": (0, 0), "type": "buff",
                  "effect": "camouflage",
                  "desc": "❄️ [CAMOUFLAGE] Simo disappears into the snow. 80% evasion for 2 turns. He becomes one with the white landscape - invisible even to gods. [TRANSFORMATION: He becomes one with the white landscape - invisible even to gods]"},
            '4': {"name": "💀 Isänmaalle (Kidney)", "cost": 40, "dmg": (270, 340), "type": "damage",
                  "organ": True, "effect": "organ",
                  "desc": "💀 [ISÄNMAALLE] 'For the Fatherland' - Simo sacrifices a kidney to power a shot. His kidney becomes the bullet - a piece of himself, offered for Finland. [TRANSFORMATION: His kidney becomes the bullet - a piece of himself, offered for Finland]"},
            '5': {"name": "❄️ Ukonvasara", "cost": 150, "dmg": (600, 800), "type": "damage",
                  "desc": "❄️ [UKONVASARA] 'Hammer of Ukko' - The hammer of the thunder god - Simo's ultimate shot. The ultimate sacrifice - his pancreas becomes the Hammer of Ukko, the supreme god's weapon. [TRANSFORMATION: The ultimate sacrifice - his pancreas becomes the Hammer of Ukko, the supreme god's weapon]"},
            '6': {"name": "🌸 Ilmatar", "cost": 45, "dmg": (280, 360), "type": "damage",
                  "organ": True, "effect": "organ",
                  "desc": "🌸 [ILMATAR] 'Profusion of Flowers' - Simo fires a bullet that scatters into countless projectiles midair, mowing down entire armies. Twice the speed of sound. One bullet becomes a thousand - flower petals of death. [TRANSFORMATION: One bullet becomes a thousand - flower petals of death]"},
            '7': {"name": "🦢 Lemminkäinen", "cost": 55, "dmg": (330, 430), "type": "damage",
                  "organ": True, "effect": "organ", "blockable": False,
                  "desc": "🦢 [LEMMINKÄINEN] 'Heaven-Piercing Swan' - A powerful rotating bullet that pierces through anything. Went through Odin, Thor, and Heracles clones plus the Shield of Skuld. The white swan of Finnish myth - piercing heaven itself. [TRANSFORMATION: The white swan of Finnish myth - piercing heaven itself]"},
            '8': {"name": "🌬️ Mielikki", "cost": 50, "dmg": (300, 390), "type": "damage",
                  "organ": True, "effect": "organ",
                  "desc": "🌬️ [MIELIKKI] 'Breath of the Spirit' - An extremely fast bullet that reaches 'godspeed,' piercing the target in a split second before they can react. The breath of the forest goddess - silent and deadly. [TRANSFORMATION: The breath of the forest goddess - silent and deadly]"}
        }

        print(f"\n⚔️ VÖLUNDR: Simo x Ráðgríðr")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → [TRANSFORMATION: Ráðgríðr fuses")
        print(f"      with his Mosin-Nagant - a divine")
        print(f"      rifle that can trade organs for")
        print(f"      god-slaying bullets]")
        return f"✅ Völundr successfully activated for Simo Häyhä!"

    def apply_effect(self, effect, target=None):
        if effect == "camouflage":
            self.camouflage_active = True
            self.add_status_effect(StatusEffect.CAMOUFLAGE, 2)
            self.add_status_effect(StatusEffect.EVASION, 2, 0.8)
            return "❄️ [CAMOUFLAGE] Camouflage activated! 80% evasion for 2 turns. [TRANSFORMATION: Simo becomes one with the snow - invisible to all]"
        elif effect == "organ":
            if len(self.organs_used) < len(self.organs):
                organ = self.organs[len(self.organs_used)]
                self.organs_used.append(organ)
                self.organ_sacrifice += 1
                damage_taken = 30
                print(f"  💥 [ORGAN SACRIFICE] Simo takes {damage_taken} damage from sacrificing his {organ}!")
                self.take_damage(damage_taken)
                self.add_status_effect(StatusEffect.ORGAN_SAC, 1, stacks=len(self.organs_used))
                organs_left = len(self.organs) - len(self.organs_used)
                return f"💀 [ISÄNMAALLE] {organ} becomes a divine bullet! Organs left: {organs_left}"
            return "❌ Cannot sacrifice more organs!"
        return ""

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "❄️ UKONVASARA",
                "cost": 250,
                "dmg": (700, 900),
                "type": "damage",
                "desc": "❄️ [UKONVASARA] Simo's ultimate shot. He sacrifices his pancreas to fire a bullet of pure white death. His pancreas becomes the bullet - the Hammer of Ukko, the supreme god of Finnish mythology, manifested as a sniper round. [TRANSFORMATION: His pancreas becomes the bullet - the Hammer of Ukko, the supreme god of Finnish mythology, manifested as a sniper round]"
            }
        return self.divine_technique


# ============================================================================
# SAKATA KINTOKI - Golden Hero (FIXED with double strike and Rune requirement)
# ============================================================================

class SakataKintoki(Character):
    def __init__(self):
        super().__init__(
            "Sakata Kintoki",
            "Golden Hero • Japan",
            1300, 430,
            [Realm.GODLY_STRENGTH, Realm.GODLY_WILL]
        )
        self.round = 12
        self.affiliation = "Humanity"
        self.rune_of_eirin_active = False
        self.rune_cooldown = 0

        self.abilities = {
            '1': {"name": "🐻 Axe Swing", "cost": 15, "dmg": (140, 190), "type": "damage",
                  "desc": "🐻 [AXE SWING] A basic axe swing."}
        }
        self._base_abilities = dict(self.abilities)

    def activate_volund(self, valkyrie):
        if valkyrie != Valkyrie.SKEGGJÖLD:
            return f"❌ Kintoki can only bond with Skeggjöld!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Divine Battle Axe (神器斧)"
        self.add_status_effect(StatusEffect.VOLUNDR, 999)

        self.divine_technique = {
            "name": "🐻 GOLDEN LIGHTNING AXE - FURIOUS FLASH",
            "cost": 180,
            "dmg": (580, 750),
            "type": "damage",
            "desc": "🐻 [GOLDEN LIGHTNING AXE - FURIOUS FLASH] Kintoki's ultimate technique. He channels the power of Raijin through his golden axe. The Rune of Eirin activates, coating the axe in golden lightning - a double strike that flashes with the speed of thunder. [TRANSFORMATION: The Rune of Eirin activates, coating the axe in golden lightning - a double strike that flashes with the speed of thunder]"
        }

        self.abilities = {
            '1': {"name": "🐻 Axe Swing", "cost": 15, "dmg": (140, 190), "type": "damage",
                  "desc": "🐻 [AXE SWING] A basic axe swing."},
            '2': {"name": "🐻 Golden Axe Swing", "cost": 30, "dmg": (170, 230), "type": "damage",
                  "desc": "🐻 [GOLDEN AXE SWING] A basic swing of Kintoki's golden axe. The axe glows with golden light - the first hint of divine power. [TRANSFORMATION: The axe glows with golden light - the first hint of divine power]"},
            '3': {"name": "⚡ Raijin's Power", "cost": 40, "dmg": (220, 290), "type": "damage",
                  "effect": "empower",
                  "desc": "⚡ [RAIJIN'S POWER] Kintoki channels the power of Raijin. Lightning crackles around the axe - the thunder god's power awakens. [TRANSFORMATION: Lightning crackles around the axe - the thunder god's power awakens]"},
            '4': {"name": "✨ Rune of Eirin", "cost": 35, "dmg": (0, 0), "type": "buff", "effect": "rune",
                  "desc": "✨ [RUNE OF EIRIN] Kintoki activates the ancient Rune of Eirin. The Dagaz rune on his palm glows - the primordial power of his ancestor awakens. Cannot be used again for 5 turns. [TRANSFORMATION: The Dagaz rune on his palm glows - the primordial power of his ancestor awakens]"},
            '5': {"name": "🐻 Golden Lightning Axe", "cost": 100, "dmg": (470, 610), "type": "damage",
                  "effect": "flash", "hits": 2,
                  "desc": "🐻 [GOLDEN LIGHTNING AXE] Kintoki transforms his axe into pure lightning. The axe becomes living lightning - a double strike that flashes faster than the eye can follow. [TRANSFORMATION: The axe becomes living lightning - a double strike that flashes faster than the eye can follow]"}
        }

        print(f"\n⚔️ VÖLUNDR: Kintoki x Skeggjöld")
        print(f"   → {wrap_text(self.volund_weapon, 60)}")
        print(f"   → [TRANSFORMATION: Skeggjöld fuses")
        print(f"      with his axe - the weapon 'breaks'")
        print(f"      like a shell, revealing its true")
        print(f"      divine form]")
        return f"✅ Völundr successfully activated for Sakata Kintoki!"

    def apply_effect(self, effect, target=None):
        if effect == "rune":
            if self.rune_cooldown <= 0:
                self.rune_of_eirin_active = True
                self.rune_cooldown = 5
                self.add_status_effect(StatusEffect.RUNE_OF_EIRIN, 5)
                self.add_status_effect(StatusEffect.EMPOWER, 5, 1.5)
                return "✨ [RUNE OF EIRIN] RUNE OF EIRIN ACTIVATED! [TRANSFORMATION: The ancient rune of the Primordial Gods glows on Kintoki's palm - golden light envelops him]"
            return f"❌ Rune of Eirin is on cooldown for {self.rune_cooldown} more turns!"
        elif effect == "flash":
            if self.rune_of_eirin_active:
                self.add_status_effect(StatusEffect.GOLDEN_LIGHTNING, 1)
                self.add_status_effect(StatusEffect.FURIOUS_FLASH, 1)
                return "🐻 [FURIOUS FLASH] GOLDEN LIGHTNING AXE - FURIOUS FLASH! Lightning erupts! [TRANSFORMATION: The axe becomes pure lightning - first strike sends a golden arc flying, second strike follows with electrified blade]"
            return "❌ [RUNE NEEDED] Need to activate Rune of Eirin first!"
        elif effect == "empower":
            self.add_status_effect(StatusEffect.EMPOWER, 1, 1.3)
            return "⚡ [RAIJIN'S POWER] Lightning crackles around the axe!"
        return ""

    def update_status_effects(self):
        super().update_status_effects()
        if self.rune_cooldown > 0:
            self.rune_cooldown -= 1
            if self.rune_cooldown == 0:
                print(f"  ⚡ Rune of Eirin is ready to use again!")

    def ensure_divine_technique(self):
        if not self.divine_technique and self.volund_active:
            self.divine_technique = {
                "name": "🐻 GOLDEN LIGHTNING AXE - FURIOUS FLASH",
                "cost": 180,
                "dmg": (580, 750),
                "type": "damage",
                "desc": "🐻 [GOLDEN LIGHTNING AXE - FURIOUS FLASH] Kintoki's ultimate technique. He channels the power of Raijin through his golden axe. The Rune of Eirin activates, coating the axe in golden lightning - a double strike that flashes with the speed of thunder. [TRANSFORMATION: The Rune of Eirin activates, coating the axe in golden lightning - a double strike that flashes with the speed of thunder]"
            }
        return self.divine_technique


# ============================================================================
# ENEMY CREATION FUNCTIONS (FIXED with varied AI patterns)
# ============================================================================

def create_enemy_god_servant():
    abilities = {'1': {"name": "Divine Fist", "dmg": (40, 65), "cost": 15, "type": "damage"}}
    enemy = Enemy("Einherjar Soldier", "Divine Servant", 250, 150, abilities, 50, "Valhalla")
    enemy.ai_pattern = ['1']
    return enemy


def create_enemy_valkyrie_trainee():
    abilities = {'1': {"name": "Völundr Strike", "dmg": (50, 80), "cost": 20, "type": "damage"}}
    enemy = Enemy("Valkyrie Trainee", "Sister of Battle", 280, 160, abilities, 40, "Valkyries")
    enemy.ai_pattern = ['1']
    return enemy


def create_enemy_demon():
    abilities = {
        '1': {"name": "Demon Claw", "dmg": (60, 90), "cost": 20, "type": "damage"},
        '2': {"name": "Hellfire", "dmg": (75, 110), "cost": 30, "type": "damage"}
    }
    enemy = Enemy("Helheim Demon", "Lesser Demon", 320, 170, abilities, 30, "Helheim")
    enemy.ai_pattern = ['1', '2']
    return enemy


def create_enemy_thor():
    abilities = {
        '1': {"name": "⚡ Mjolnir Strike", "dmg": (130, 190), "cost": 30, "type": "damage", "divine": True},
        '2': {"name": "⚡ Thor's Hammer", "dmg": (190, 260), "cost": 45, "type": "damage", "divine": True},
        '3': {"name": "⚡ Geirröd's Power", "dmg": (280, 370), "cost": 70, "type": "damage", "divine": True}
    }
    enemy = Enemy("Thor", "God of Thunder", 1250, 400, abilities, 1, "Norse Gods", 1,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE])
    enemy.divine_technique = {
        "name": "⚡ GEIRRÖD THOR'S HAMMER",
        "cost": 180,
        "dmg": (550, 750),
        "type": "damage",
        "desc": "⚡ [GEIRRÖD THOR'S HAMMER] Thor's ultimate technique combining Thor's Hammer and Awakened Thunder Hammer."
    }
    enemy.ai_pattern = ['1', '2', '3', '2', '1']
    return enemy


def create_enemy_zeus():
    abilities = {
        '1': {"name": "👊 Divine Punch", "dmg": (160, 220), "cost": 35, "type": "damage", "divine": True},
        '2': {"name": "⚡ Meteor Jab", "dmg": (220, 290), "cost": 50, "type": "damage", "divine": True},
        '3': {"name": "👴 True God's Form", "dmg": (320, 410), "cost": 80, "type": "damage", "divine": True}
    }
    enemy = Enemy("Zeus", "Godfather", 1300, 450, abilities, 2, "Greek Gods", 2,
                  [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE])
    enemy.divine_technique = {
        "name": "👊 FIST THAT SURPASSED TIME",
        "cost": 200,
        "dmg": (600, 800),
        "type": "damage",
        "desc": "👊 [TIME SURPASSING FIST] Zeus's ultimate technique. A punch so impossibly fast that it transcends time itself."
    }
    enemy.ai_pattern = ['1', '2', '1', '3', '2']
    return enemy


def create_enemy_poseidon():
    abilities = {
        '1': {"name": "🌊 Trident Thrust", "dmg": (160, 220), "cost": 35, "type": "damage", "divine": True},
        '2': {"name": "🌊 40-Day Flood", "dmg": (350, 450), "cost": 80, "type": "damage", "divine": True}
    }
    enemy = Enemy("Poseidon", "God of Seas", 1200, 410, abilities, 3, "Greek Gods", 3,
                  [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE])
    enemy.divine_technique = {
        "name": "🌊 40 DAYS AND 40 NIGHTS OF FLOOD",
        "cost": 180,
        "dmg": (550, 750),
        "type": "damage",
        "desc": "🌊 [FORTY DAY FLOOD] Poseidon's ultimate technique. A relentless assault of 40 consecutive trident thrusts."
    }
    enemy.ai_pattern = ['1', '2', '1']
    return enemy


def create_enemy_heracles():
    abilities = {
        '1': {"name": "🦁 Nemean Lion", "dmg": (170, 230), "cost": 30, "type": "damage", "divine": True},
        '2': {"name": "🐍 Lernaean Hydra", "dmg": (190, 250), "cost": 35, "type": "damage", "divine": True},
        '3': {"name": "🐕 Cerberus", "dmg": (400, 500), "cost": 100, "type": "damage", "divine": True}
    }
    enemy = Enemy("Heracles", "God of Fortitude", 1350, 430, abilities, 4, "Greek Gods", 4,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE])
    enemy.divine_technique = {
        "name": "🦁 CERBERUS: Hound of Hades",
        "cost": 180,
        "dmg": (520, 680),
        "type": "damage",
        "desc": "🦁 [CERBERUS FUSION] Heracles fuses with Cerberus, the three-headed hound of Hades."
    }
    enemy.ai_pattern = ['1', '2', '1', '3']
    return enemy


def create_enemy_shiva():
    abilities = {
        '1': {"name": "🔥 Four Arms Strike", "dmg": (180, 240), "cost": 35, "type": "damage", "divine": True},
        '2': {"name": "🔥 Tandava", "dmg": (280, 360), "cost": 60, "type": "damage", "divine": True},
        '3': {"name": "🔥 Deva Loka", "dmg": (400, 500), "cost": 90, "type": "damage", "divine": True}
    }
    enemy = Enemy("Shiva", "God of Destruction", 1280, 400, abilities, 5, "Hindu Gods", 5,
                  [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE])
    enemy.divine_technique = {
        "name": "🔥 DEVA LOKA",
        "cost": 190,
        "dmg": (580, 750),
        "type": "damage",
        "desc": "🔥 [DEVA LOKA] Shiva's ultimate spinning heel kick performed in Tandava Karma state."
    }
    enemy.ai_pattern = ['1', '2', '1', '3', '2']
    return enemy


def create_enemy_zerofuku():
    abilities = {
        '1': {"name": "🎋 Misery Cleaver", "dmg": (150, 210), "cost": 25, "type": "damage", "divine": True},
        '2': {"name": "🌪️ Storm Form", "dmg": (400, 500), "cost": 100, "type": "damage", "divine": True},
        '3': {"name": "🎋 Seven Lucky Gods Union", "dmg": (470, 590), "cost": 120, "type": "damage", "divine": True}
    }
    enemy = Enemy("Zerofuku", "God of Misfortune", 1150, 410, abilities, 6, "Seven Lucky Gods", 6,
                  [Realm.GODLY_STRENGTH])
    enemy.divine_technique = {
        "name": "🎋 MISERY CLEAVER - STORM FORM",
        "cost": 170,
        "dmg": (500, 650),
        "type": "damage",
        "desc": "🎋 [MISERY STORM] Zerofuku transforms his Misery Cleaver into a storm of countless black blades."
    }
    enemy.ai_pattern = ['1', '2', '1', '3']
    return enemy


def create_enemy_hajun():
    abilities = {
        '1': {"name": "👹 Demon Strike", "dmg": (200, 270), "cost": 35, "type": "damage", "divine": True},
        '2': {"name": "👹 Helheim's Wrath", "dmg": (300, 380), "cost": 55, "type": "damage", "divine": True},
        '3': {"name": "👹 Demon King's Wrath", "dmg": (500, 650), "cost": 100, "type": "damage", "divine": True}
    }
    enemy = Enemy("Hajun", "Demon King", 1600, 450, abilities, 6, "Helheim", 6,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE, Realm.GODLY_WILL], soul_dark=True)
    enemy.divine_technique = {
        "name": "👹 DEMON KING'S WRATH",
        "cost": 220,
        "dmg": (650, 850),
        "type": "damage",
        "desc": "👹 [DEMON KING'S WRATH] The attack that destroyed half of Helheim."
    }
    enemy.ai_pattern = ['1', '2', '3', '2', '1']
    return enemy


def create_enemy_hades():
    abilities = {
        '1': {"name": "💀 Bident Thrust", "dmg": (170, 230), "cost": 25, "type": "damage", "divine": True},
        '2': {"name": "💀 Ichor-Eos", "dmg": (400, 500), "cost": 80, "type": "damage", "divine": True},
        '3': {"name": "⚔️ Ichor Desmos", "dmg": (600, 780), "cost": 200, "type": "damage", "divine": True}
    }
    enemy = Enemy("Hades", "God of Underworld", 1400, 460, abilities, 7, "Greek Gods", 7,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE])
    enemy.divine_technique = {
        "name": "💀 ICHOR DESMOS",
        "cost": 200,
        "dmg": (600, 780),
        "type": "damage",
        "desc": "💀 [ICHOR DESMOS] Hades's ultimate technique. He infuses his bident with his own divine blood (ichor)."
    }
    enemy.ai_pattern = ['1', '2', '1', '3']
    return enemy


def create_enemy_beelzebub():
    abilities = {
        '1': {"name": "🦟 Palmyra", "dmg": (180, 240), "cost": 30, "type": "damage", "divine": True},
        '2': {"name": "🦟 Sorath Resh", "dmg": (430, 530), "cost": 85, "type": "damage", "divine": True},
        '3': {"name": "🦟 CHAOS", "dmg": (550, 700), "cost": 150, "type": "damage", "divine": True}
    }
    enemy = Enemy("Beelzebub", "Lord of the Flies", 1250, 450, abilities, 8, "Gods", 8,
                  [Realm.GODLY_TECHNIQUE])
    enemy.divine_technique = {
        "name": "🦟 ORIGINAL SIN: CHAOS",
        "cost": 250,
        "dmg": (700, 900),
        "type": "damage",
        "desc": "🦟 [ORIGINAL SIN] Beelzebub's forbidden technique. He creates a black sphere of absolute annihilation."
    }
    enemy.ai_pattern = ['1', '2', '1', '3']
    return enemy


def create_enemy_apollo():
    abilities = {
        '1': {"name": "🎯 Silver Bow Shot", "dmg": (160, 220), "cost": 25, "type": "damage", "divine": True},
        '2': {"name": "🎯 Apollo Epicurious", "dmg": (270, 340), "cost": 55, "type": "damage", "divine": True},
        '3': {"name": "🎯 Argyrotoxos", "dmg": (470, 600), "cost": 100, "type": "damage", "divine": True}
    }
    enemy = Enemy("Apollo", "God of the Sun", 1180, 440, abilities, 9, "Greek Gods", 9,
                  [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE])
    enemy.divine_technique = {
        "name": "🎯 ARGYROTOXOS",
        "cost": 190,
        "dmg": (600, 780),
        "type": "damage",
        "desc": "🎯 [ARGYROTOXOS] Apollo's ultimate technique. He launches himself like a silver arrow."
    }
    enemy.ai_pattern = ['1', '2', '1', '3']
    return enemy


def create_enemy_susanoo():
    abilities = {
        '1': {"name": "🌪️ Storm's Wrath", "dmg": (180, 240), "cost": 30, "type": "damage", "divine": True},
        '2': {"name": "🌪️ Ama no Magaeshi", "dmg": (330, 410), "cost": 60, "type": "damage", "divine": True},
        '3': {"name": "⚔️ Musouken", "dmg": (550, 700), "cost": 150, "type": "damage", "divine": True}
    }
    enemy = Enemy("Susano'o no Mikoto", "God of Storms", 1280, 450, abilities, 10, "Japanese Gods", 10,
                  [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH])
    enemy.divine_technique = {
        "name": "🌪️ MUSOUKEN: Unarmed Sword",
        "cost": 250,
        "dmg": (700, 900),
        "type": "damage",
        "desc": "🌪️ [MUSOUKEN] Susano'o's ultimate technique. He creates an invisible blade of nothingness that cuts only the INSIDE of the body."
    }
    enemy.ai_pattern = ['1', '2', '1', '3']
    return enemy


def create_enemy_loki():
    abilities = {
        '1': {"name": "🎭 Illusion Strike", "dmg": (150, 210), "cost": 25, "type": "damage", "divine": True},
        '2': {"name": "🎭 Trickster's Gambit", "dmg": (330, 410), "cost": 70, "type": "damage", "divine": True},
        '3': {"name": "🎭 HEIMSKRINGLA", "dmg": (550, 700), "cost": 200, "type": "damage", "divine": True}
    }
    enemy = Enemy("Loki", "God of Mischief", 1220, 440, abilities, 11, "Norse Gods", 11,
                  [Realm.GODLY_TECHNIQUE])
    enemy.divine_technique = {
        "name": "🎭 HEIMSKRINGLA: Endurlífa",
        "cost": 200,
        "dmg": (550, 700),
        "type": "damage",
        "desc": "🎭 [HEIMSKRINGLA] Loki's ultimate trick. He creates a perfect clone and can swap positions at will."
    }
    enemy.ai_pattern = ['1', '2', '1', '3']
    return enemy


def create_enemy_odin():
    abilities = {
        '1': {"name": "🔱 Gungnir Thrust", "dmg": (200, 270), "cost": 35, "type": "damage", "divine": True},
        '2': {"name": "🔮 Vindsskuggr", "dmg": (370, 470), "cost": 70, "type": "damage", "divine": True},
        '3': {"name": "🔱 Absolute Certainty", "dmg": (550, 700), "cost": 150, "type": "damage", "divine": True}
    }
    enemy = Enemy("Odin", "All-Father", 1500, 470, abilities, 12, "Norse Gods", 12,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL])
    enemy.divine_technique = {
        "name": "🔱 GUNGNIR: Absolute Certainty",
        "cost": 220,
        "dmg": (650, 850),
        "type": "damage",
        "desc": "🔱 [GUNGNIR] Odin throws Gungnir, the spear that never misses."
    }
    enemy.ai_pattern = ['1', '2', '1', '3']
    return enemy


def create_enemy_lu_bu():
    abilities = {
        '1': {"name": "🏹 Sky Piercer", "dmg": (160, 220), "cost": 30, "type": "damage"},
        '2': {"name": "🐎 Red Hare Charge", "dmg": (190, 260), "cost": 35, "type": "damage"},
        '3': {"name": "🏹 Sky Eater", "dmg": (430, 550), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Lü Bu", "Flying General", 1250, 380, abilities, 1, "Humanity", 1,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_WILL])
    enemy.ai_pattern = ['1', '2', '3', '2']
    return enemy


def create_enemy_adam():
    abilities = {
        '1': {"name": "👁️ Divine Replication", "dmg": (150, 210), "cost": 30, "type": "damage"},
        '2': {"name": "👁️ Meteor Jab", "dmg": (190, 260), "cost": 40, "type": "damage"},
        '3': {"name": "👁️ Time Transcending Fist", "dmg": (450, 600), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Adam", "Father of Humanity", 1300, 390, abilities, 2, "Humanity", 2,
                  [Realm.GODLY_SPEED, Realm.GODLY_WILL])
    enemy.ai_pattern = ['1', '2', '1', '3']
    return enemy


def create_enemy_kojiro():
    abilities = {
        '1': {"name": "⚔️ Tsubame Gaeshi", "dmg": (200, 270), "cost": 40, "type": "damage"},
        '2': {"name": "⚔️ Sōenzanko", "dmg": (430, 550), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Kojiro Sasaki", "History's Greatest Loser", 1180, 370, abilities, 3, "Humanity", 3,
                  [Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['1', '2', '1']
    return enemy


def create_enemy_jack():
    abilities = {
        '1': {"name": "🗡️ Dear Jane", "dmg": (130, 190), "cost": 25, "type": "damage"},
        '2': {"name": "🎪 Dear God", "dmg": (430, 550), "cost": 120, "type": "damage"}
    }
    enemy = Enemy("Jack the Ripper", "Whitechapel Demon", 1150, 350, abilities, 4, "Humanity", 4,
                  [Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['1', '2', '1']
    return enemy


def create_enemy_raiden():
    abilities = {
        '1': {"name": "💪 Muscle Control", "dmg": (160, 220), "cost": 25, "type": "damage"},
        '2': {"name": "💪 Yatagarasu", "dmg": (470, 630), "cost": 120, "type": "damage"}
    }
    enemy = Enemy("Raiden Tameemon", "Greatest Sumo Wrestler", 1400, 370, abilities, 5, "Humanity", 5,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE])
    enemy.ai_pattern = ['1', '2', '1']
    return enemy


def create_enemy_buddha():
    abilities = {
        '1': {"name": "🧘 Six Realms Staff", "dmg": (180, 250), "cost": 35, "type": "damage"},
        '2': {"name": "👁️ Future Sight", "dmg": (0, 0), "cost": 40, "type": "buff"},
        '3': {"name": "🌸 Mahaparinirvana", "dmg": (500, 650), "cost": 150, "type": "damage"}
    }
    enemy = Enemy("Buddha", "Enlightened One", 1250, 390, abilities, 6, "Humanity", 6,
                  [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL])
    enemy.divine_technique = {
        "name": "🌸 Mahaparinirvana Zero",
        "cost": 150,
        "dmg": (500, 650),
        "type": "damage",
        "desc": "🌸 [MAHAPARINIRVANA ZERO] The ultimate divine weapon created from Zerofuku's soul."
    }
    enemy.ai_pattern = ['1', '2', '1', '3']
    return enemy


def create_enemy_qin():
    abilities = {
        '1': {"name": "👑 Chiyou Style", "dmg": (240, 320), "cost": 45, "type": "damage"},
        '2': {"name": "👑 Emperor's Will", "dmg": (470, 610), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Qin Shi Huang", "First Emperor", 1280, 380, abilities, 7, "Humanity", 7,
                  [Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL])
    enemy.ai_pattern = ['1', '2', '1']
    return enemy


def create_enemy_tesla():
    abilities = {
        '1': {"name": "⚡ PPP", "dmg": (160, 220), "cost": 25, "type": "damage"},
        '2': {"name": "⚡ PPPX", "dmg": (500, 650), "cost": 120, "type": "damage"}
    }
    enemy = Enemy("Nikola Tesla", "Greatest Inventor", 1220, 390, abilities, 8, "Humanity", 8,
                  [Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['1', '2', '1']
    return enemy


def create_enemy_leonidas():
    abilities = {
        '1': {"name": "🛡️ Spartan Kick", "dmg": (170, 230), "cost": 30, "type": "damage"},
        '2': {"name": "🛡️ Phalanx Lambda", "dmg": (470, 610), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Leonidas", "King of Sparta", 1350, 380, abilities, 9, "Humanity", 9,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE])
    enemy.ai_pattern = ['1', '2', '1']
    return enemy


def create_enemy_okita():
    abilities = {
        '1': {"name": "⚔️ Three-Stage Thrust", "dmg": (220, 290), "cost": 40, "type": "damage"},
        '2': {"name": "⚔️ Enpi Reiten", "dmg": (550, 730), "cost": 150, "type": "damage"}
    }
    enemy = Enemy("Soji Okita", "Captain of Shinsengumi", 1250, 370, abilities, 10, "Humanity", 10,
                  [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['1', '2', '1']
    return enemy


def create_enemy_simo():
    abilities = {
        '1': {"name": "❄️ White Death", "dmg": (170, 230), "cost": 25, "type": "damage"},
        '2': {"name": "❄️ Ukonvasara", "dmg": (600, 800), "cost": 150, "type": "damage"}
    }
    enemy = Enemy("Simo Häyhä", "White Death", 1200, 360, abilities, 11, "Humanity", 11,
                  [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['1', '2', '1']
    return enemy


def create_enemy_kintoki():
    abilities = {
        '1': {"name": "🐻 Golden Axe", "dmg": (170, 230), "cost": 30, "type": "damage"},
        '2': {"name": "🐻 Furious Flash", "dmg": (470, 610), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Sakata Kintoki", "Golden Hero", 1300, 380, abilities, 12, "Humanity", 12,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_WILL])
    enemy.ai_pattern = ['1', '2', '1']
    return enemy


# ============================================================================
# VÖLUNDR ACTIVATION FUNCTIONS (FIXED with mode tracking)
# ============================================================================

def activate_volund_for_character(character, game):
    if character.volund_active:
        return False

    if character.name == "Buddha":
        return False

    if character.name in game.canon_pairings:
        pairing_data = game.canon_pairings[character.name]
        expected_name = pairing_data["valkyrie_name"]
        expected_enum = pairing_data.get("valkyrie_enum", "")

        if game.check_valkyrie_available(expected_name):
            valkyrie = None

            if expected_enum:
                valkyrie = Valkyrie.get_by_name(expected_enum)
            if not valkyrie:
                valkyrie = Valkyrie.get_by_display_name(expected_name)
            if not valkyrie:
                valkyrie = Valkyrie.get_by_index(pairing_data["valkyrie_index"])

            if valkyrie:
                character.activate_volund(valkyrie)
                character.valkyrie_index = valkyrie.index
                if hasattr(game, 'current_mode') and game.current_mode == "tournament":
                    game.mark_valkyrie_fallen(expected_name)
                return True
    return False


def activate_volund_for_party(party, game):
    count = 0
    for character in party:
        if activate_volund_for_character(character, game):
            count += 1
    return count


# ============================================================================
# SURVIVAL MODE
# ============================================================================

class SurvivalMode:
    def __init__(self, game):
        self.game = game
        self.wave = 0
        self.score = 0
        self.party = []
        self.consecutive_wins = 0
        self.boss_waves = [10, 20, 30, 50, 75, 100]

    def run(self):
        self.game.current_mode = "survival"

        clear_screen()
        print("\n" + "=" * 110)
        slow_print("♾️♾️♾️ ENDLESS SURVIVAL MODE ♾️♾️♾️", 0.03)
        print("=" * 110)
        slow_print("Fight wave after wave of increasingly powerful enemies.", 0.02)
        slow_print("No rest between waves - only survival.", 0.02)
        slow_print("Special boss waves every 10th wave!", 0.02)
        print("=" * 110)

        print("\nSelect your champions for survival mode:")
        self.party = self.game.select_party(4)
        if not self.party:
            print("❌ No party selected. Returning to menu...")
            time.sleep(2)
            return

        count = activate_volund_for_party(self.party, self.game)
        if count > 0:
            print(f"   → Völundr activated for {count} champion(s)")

        print(f"\nYour party: {', '.join([c.name for c in self.party])}")
        print("This party will fight ALL waves. There is no changing members.")
        confirm = input("\nAre you ready to begin? (y/n): ").lower()
        if confirm != 'y':
            print("Returning to menu...")
            return

        while True:
            self.wave += 1
            is_boss_wave = self.wave in self.boss_waves

            clear_screen()
            print("\n" + "🔥" * 110)
            slow_print(f"🔥 WAVE {self.wave} 🔥", 0.05)
            if is_boss_wave:
                slow_print(f"🌟🌟🌟 BOSS WAVE! 🌟🌟🌟", 0.04)
            print("🔥" * 110)
            print(f"Current Score: {self.score}")
            print(f"Consecutive Wins: {self.consecutive_wins}")
            print("-" * 110)

            enemies = self.generate_wave()

            print("\nEnemies approaching:")
            for i, enemy in enumerate(enemies):
                boss_tag = " [BOSS]" if (is_boss_wave and i == 0) else ""
                print(f"  {i + 1}. {enemy.name} - {enemy.title}{boss_tag}")

            print("\n" + "-" * 110)
            input("Press Enter to face the wave...")

            victory = self.game.battle(enemies, self.party)

            if victory:
                wave_bonus = self.wave * 100
                boss_bonus = 500 if is_boss_wave else 0
                consecutive_bonus = self.consecutive_wins * 50

                self.score += wave_bonus + boss_bonus + consecutive_bonus
                self.consecutive_wins += 1

                print(f"\n✨ WAVE {self.wave} CLEARED! ✨")
                print(f"  Base: +{wave_bonus}")
                if boss_bonus:
                    print(f"  Boss Bonus: +{boss_bonus}")
                if consecutive_bonus:
                    print(f"  Consecutive Bonus: +{consecutive_bonus}")
                print(f"  Total Score: {self.score}")

                for char in self.party:
                    if char.is_alive():
                        char.hp = min(char.max_hp, char.hp + int(char.max_hp * 0.2))
                        char.energy = min(char.max_energy, char.energy + int(char.max_energy * 0.2))

                print("\n🩹 Your party recovers 20% HP and Energy.")
                time.sleep(2)

                if not all(c.is_alive() for c in self.party):
                    print("\n⚠️ Some of your champions have fallen!")
                    if not any(c.is_alive() for c in self.party):
                        print("💀 Your entire party has been defeated!")
                        break

                if self.wave % 5 == 0:
                    print(f"\nYou have cleared {self.wave} waves with score {self.score}.")
                    withdraw = input("Withdraw and cash out? (y/n): ").lower()
                    if withdraw == 'y':
                        print(f"\n🏆 FINAL SCORE: {self.score}")
                        print(f"Waves Cleared: {self.wave}")
                        self.game.save_game()
                        input("Press Enter to return to menu...")
                        return
            else:
                print("\n" + "💀" * 55)
                slow_print(f"💀 DEFEATED AT WAVE {self.wave} 💀", 0.04)
                print("💀" * 55)
                print(f"Final Score: {self.score}")
                print(f"Waves Cleared: {self.wave - 1}")

                self.save_high_score()
                input("\nPress Enter to return to menu...")
                break

        self.game.current_mode = "menu"

    def generate_wave(self):
        enemies = []
        is_boss_wave = self.wave in self.boss_waves

        if is_boss_wave:
            num_enemies = 1
        else:
            if self.wave < 5:
                num_enemies = random.randint(1, 2)
            elif self.wave < 10:
                num_enemies = random.randint(2, 3)
            elif self.wave < 20:
                num_enemies = random.randint(2, 4)
            else:
                num_enemies = random.randint(3, 4)

        enemy_pool = []

        if self.wave < 5:
            enemy_pool = [
                create_enemy_god_servant,
                create_enemy_valkyrie_trainee,
                create_enemy_demon
            ]
        elif self.wave < 10:
            enemy_pool = [
                create_enemy_god_servant,
                create_enemy_valkyrie_trainee,
                create_enemy_demon,
                create_enemy_thor,
                create_enemy_lu_bu
            ]
        elif self.wave < 20:
            enemy_pool = [
                create_enemy_thor, create_enemy_zeus, create_enemy_poseidon,
                create_enemy_heracles, create_enemy_shiva, create_enemy_zerofuku,
                create_enemy_lu_bu, create_enemy_adam, create_enemy_kojiro,
                create_enemy_jack, create_enemy_raiden
            ]
        else:
            enemy_pool = [
                create_enemy_thor, create_enemy_zeus, create_enemy_poseidon,
                create_enemy_heracles, create_enemy_shiva, create_enemy_zerofuku,
                create_enemy_hajun, create_enemy_hades, create_enemy_beelzebub,
                create_enemy_apollo, create_enemy_susanoo, create_enemy_loki,
                create_enemy_odin, create_enemy_lu_bu, create_enemy_adam,
                create_enemy_kojiro, create_enemy_jack, create_enemy_raiden,
                create_enemy_buddha, create_enemy_qin, create_enemy_tesla,
                create_enemy_leonidas, create_enemy_okita, create_enemy_simo,
                create_enemy_kintoki
            ]

        if is_boss_wave:
            boss_pool = {
                10: [create_enemy_zeus, create_enemy_odin],
                20: [create_enemy_hajun, create_enemy_hades],
                30: [create_enemy_shiva, create_enemy_beelzebub],
                50: [create_enemy_zeus, create_enemy_odin, create_enemy_hajun],
                75: [create_enemy_zeus, create_enemy_odin, create_enemy_hajun, create_enemy_hades],
                100: [create_enemy_zeus, create_enemy_odin, create_enemy_hajun,
                      create_enemy_hades, create_enemy_beelzebub]
            }

            if self.wave in boss_pool:
                boss_func = random.choice(boss_pool[self.wave])
                boss = boss_func()

                boss.max_hp = int(boss.max_hp * (1 + (self.wave / 50)))
                boss.hp = boss.max_hp
                boss.max_energy = int(boss.max_energy * (1 + (self.wave / 50)))
                boss.energy = boss.max_energy

                enemies.append(boss)
            else:
                boss_func = random.choice([create_enemy_zeus, create_enemy_odin, create_enemy_hajun])
                boss = boss_func()
                boss.max_hp = int(boss.max_hp * 1.5)
                boss.hp = boss.max_hp
                enemies.append(boss)
        else:
            for _ in range(num_enemies):
                enemy_func = random.choice(enemy_pool)
                enemy = enemy_func()

                scale = 1 + (self.wave * 0.05)
                enemy.max_hp = int(enemy.max_hp * scale)
                enemy.hp = enemy.max_hp
                enemy.max_energy = int(enemy.max_energy * scale)
                enemy.energy = enemy.max_energy

                enemies.append(enemy)

        return enemies

    def save_high_score(self):
        try:
            high_scores = {}
            if os.path.exists("survival_scores.json"):
                with open("survival_scores.json", 'r') as f:
                    high_scores = json.load(f)

            party_names = [c.name for c in self.party if c.is_alive()]

            score_entry = {
                "score": self.score,
                "wave": self.wave - 1,
                "party": party_names,
                "date": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            if "scores" not in high_scores:
                high_scores["scores"] = []

            high_scores["scores"].append(score_entry)
            high_scores["scores"].sort(key=lambda x: x["score"], reverse=True)
            high_scores["scores"] = high_scores["scores"][:10]

            with open("survival_scores.json", 'w') as f:
                json.dump(high_scores, f, indent=4)

            print("\n🏆 High score saved!")

        except Exception as e:
            print(f"❌ Could not save high score: {e}")


# ============================================================================
# BOSS RUSH MODE
# ============================================================================

class BossRushMode:
    def __init__(self, game):
        self.game = game
        self.bosses = [
            ("Thor", create_enemy_thor),
            ("Zeus", create_enemy_zeus),
            ("Poseidon", create_enemy_poseidon),
            ("Heracles", create_enemy_heracles),
            ("Shiva", create_enemy_shiva),
            ("Zerofuku", create_enemy_zerofuku),
            ("Hajun", create_enemy_hajun),
            ("Hades", create_enemy_hades),
            ("Beelzebub", create_enemy_beelzebub),
            ("Apollo", create_enemy_apollo),
            ("Susano'o", create_enemy_susanoo),
            ("Loki", create_enemy_loki),
            ("Odin", create_enemy_odin)
        ]

    def run(self):
        self.game.current_mode = "boss_rush"

        clear_screen()
        print("\n" + "=" * 110)
        slow_print("👑👑👑 BOSS RUSH MODE 👑👑👑", 0.03)
        print("=" * 110)
        slow_print("Fight all 13 gods in sequence!", 0.02)
        slow_print("No rest between battles - only the strong survive.", 0.02)
        print("=" * 110)

        print("\nSelect your champions for boss rush:")
        self.party = self.game.select_party(3)
        if not self.party:
            print("❌ No party selected. Returning to menu...")
            time.sleep(2)
            return

        count = activate_volund_for_party(self.party, self.game)
        if count > 0:
            print(f"   → Völundr activated for {count} champion(s)")

        print(f"\nYour party: {', '.join([c.name for c in self.party])}")
        print("This party will fight ALL 13 bosses. There is no changing members.")
        confirm = input("\nAre you ready to begin? (y/n): ").lower()
        if confirm != 'y':
            print("Returning to menu...")
            return

        current_boss = 0
        victory = False
        total_bosses = len(self.bosses)

        for i, (boss_name, boss_func) in enumerate(self.bosses):
            current_boss = i + 1

            clear_screen()
            print("\n" + "🔥" * 110)
            slow_print(f"🔥 BOSS {current_boss}/{total_bosses}: {boss_name} 🔥", 0.05)
            print("🔥" * 110)

            if not any(c.is_alive() for c in self.party):
                print("\n💀 Your party has been wiped out!")
                break

            boss = boss_func()

            if i > 0:
                for char in self.party:
                    if char.is_alive():
                        char.hp = min(char.max_hp, char.hp + int(char.max_hp * 0.1))
                        char.energy = min(char.max_energy, char.energy + int(char.max_energy * 0.1))
                print("\n🩹 Your party recovers 10% HP and Energy between bosses.")

            print(f"\nFighting {boss_name}...")
            input("Press Enter to begin the battle!")

            victory = self.game.battle([boss], self.party)

            if not victory:
                print(f"\n💀 Defeated by {boss_name} at boss {current_boss}/{total_bosses}")
                break
            else:
                print(f"\n✨ {boss_name} DEFEATED! ✨")
                time.sleep(2)

        bosses_defeated = current_boss if victory else current_boss - 1

        print("\n" + "=" * 110)
        if bosses_defeated == total_bosses:
            slow_print("🏆🏆🏆 PERFECT VICTORY! ALL BOSSES DEFEATED! 🏆🏆🏆", 0.04)
        else:
            slow_print(f"📊 BOSS RUSH COMPLETED: {bosses_defeated}/{total_bosses} bosses defeated", 0.03)
        print("=" * 110)

        self.save_record(bosses_defeated)
        self.game.current_mode = "menu"
        input("\nPress Enter to return to menu...")

    def save_record(self, bosses_defeated):
        try:
            records = {}
            if os.path.exists("boss_rush_records.json"):
                with open("boss_rush_records.json", 'r') as f:
                    records = json.load(f)

            party_names = [c.name for c in self.party if c.is_alive()]

            record_entry = {
                "bosses_defeated": bosses_defeated,
                "party": party_names,
                "date": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            if "records" not in records:
                records["records"] = []

            records["records"].append(record_entry)
            records["records"].sort(key=lambda x: x["bosses_defeated"], reverse=True)
            records["records"] = records["records"][:10]

            with open("boss_rush_records.json", 'w') as f:
                json.dump(records, f, indent=4)

            print("\n🏆 Boss rush record saved!")

        except Exception as e:
            print(f"❌ Could not save record: {e}")


# ============================================================================
# GAUNTLET MODE
# ============================================================================

class GauntletMode:
    def __init__(self, game):
        self.game = game

    def run(self):
        self.game.current_mode = "gauntlet"

        clear_screen()
        print("\n" + "=" * 110)
        slow_print("⚔️⚔️⚔️ GAUNTLET MODE ⚔️⚔️⚔️", 0.03)
        print("=" * 110)
        slow_print("Fight through ALL 25 fighters in random order!", 0.02)
        slow_print("Each victory grants a small heal. Can you defeat them all?", 0.02)
        print("=" * 110)

        print("\nSelect your champion for the gauntlet:")
        print("Note: Gauntlet is 1v1 - choose ONE fighter to face all 26!")

        party = self.game.select_party(1)
        if not party:
            print("❌ No fighter selected. Returning to menu...")
            time.sleep(2)
            return

        champion = party[0]

        if activate_volund_for_character(champion, self.game):
            print(f"   → Völundr activated for {champion.name}")

        print(f"\nYour champion: {champion.name}")
        print(f"They will face ALL 25 fighters in sequence!")
        confirm = input("\nAre you ready to begin? (y/n): ").lower()
        if confirm != 'y':
            print("Returning to menu...")
            return

        fighter_creators = [
            ("Thor", create_enemy_thor),
            ("Zeus", create_enemy_zeus),
            ("Poseidon", create_enemy_poseidon),
            ("Heracles", create_enemy_heracles),
            ("Shiva", create_enemy_shiva),
            ("Zerofuku", create_enemy_zerofuku),
            ("Hajun", create_enemy_hajun),
            ("Hades", create_enemy_hades),
            ("Beelzebub", create_enemy_beelzebub),
            ("Apollo", create_enemy_apollo),
            ("Susano'o", create_enemy_susanoo),
            ("Loki", create_enemy_loki),
            ("Odin", create_enemy_odin),
            ("Lü Bu", create_enemy_lu_bu),
            ("Adam", create_enemy_adam),
            ("Kojiro Sasaki", create_enemy_kojiro),
            ("Jack the Ripper", create_enemy_jack),
            ("Raiden Tameemon", create_enemy_raiden),
            ("Buddha", create_enemy_buddha),
            ("Qin Shi Huang", create_enemy_qin),
            ("Nikola Tesla", create_enemy_tesla),
            ("Leonidas", create_enemy_leonidas),
            ("Soji Okita", create_enemy_okita),
            ("Simo Häyhä", create_enemy_simo),
            ("Sakata Kintoki", create_enemy_kintoki)
        ]

        random.shuffle(fighter_creators)
        total_fighters = len(fighter_creators)

        victories = 0

        for i, (fighter_name, fighter_func) in enumerate(fighter_creators):
            current = i + 1

            clear_screen()
            print("\n" + "🔥" * 110)
            slow_print(f"🔥 FIGHT {current}/{total_fighters}: {fighter_name} 🔥", 0.05)
            print("🔥" * 110)

            if not champion.is_alive():
                print("\n💀 Your champion has fallen!")
                break

            opponent = fighter_func()

            print(f"\n{champion.name} vs {fighter_name}")
            print(f"Current streak: {victories} victories")
            input("\nPress Enter to begin the fight!")

            victory = self.game.battle([opponent], [champion])

            if victory:
                victories += 1
                print(f"\n✨ VICTORY! {fighter_name} defeated! ✨")

                heal_amount = int(champion.max_hp * 0.15)
                champion.hp = min(champion.max_hp, champion.hp + heal_amount)
                champion.energy = min(champion.max_energy, champion.energy + int(champion.max_energy * 0.15))

                print(f"🩹 Champion recovers 15% HP and Energy.")
                time.sleep(2)
            else:
                print(f"\n💀 Defeated by {fighter_name} at fight {current}/{total_fighters}")
                break

        print("\n" + "=" * 110)
        if victories == total_fighters:
            slow_print("🏆🏆🏆 PERFECT GAUNTLET! ALL 25 DEFEATED! 🏆🏆🏆", 0.04)
        else:
            slow_print(f"📊 GAUNTLET COMPLETED: {victories}/{total_fighters} fighters defeated", 0.03)
        print("=" * 110)

        self.save_record(champion.name, victories, total_fighters)
        self.game.current_mode = "menu"
        input("\nPress Enter to return to menu...")

    def save_record(self, champion_name, victories, total):
        try:
            records = {}
            if os.path.exists("gauntlet_records.json"):
                with open("gauntlet_records.json", 'r') as f:
                    records = json.load(f)

            record_entry = {
                "champion": champion_name,
                "victories": victories,
                "total": total,
                "percentage": f"{(victories / total) * 100:.1f}%",
                "date": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            if "records" not in records:
                records["records"] = []

            records["records"].append(record_entry)
            records["records"].sort(key=lambda x: x["victories"], reverse=True)
            records["records"] = records["records"][:10]

            with open("gauntlet_records.json", 'w') as f:
                json.dump(records, f, indent=4)

            print("\n🏆 Gauntlet record saved!")

        except Exception as e:
            print(f"❌ Could not save record: {e}")


# ============================================================================
# CHAOS MODE (FIXED - no permanent stat changes)
# ============================================================================

class ChaosMode:
    def __init__(self, game):
        self.game = game

    def run(self):
        self.game.current_mode = "chaos"

        clear_screen()
        print("\n" + "=" * 110)
        slow_print("🌀🌀🌀 CHAOS MODE 🌀🌀🌀", 0.03)
        print("=" * 110)
        slow_print("Everything is randomized!", 0.02)
        slow_print("- Random party members", 0.02)
        slow_print("- Random enemies", 0.02)
        slow_print("- Random buffs and debuffs", 0.02)
        slow_print("- Anything can happen!", 0.02)
        print("=" * 110)

        input("\nPress Enter to embrace the chaos...")

        rounds = 0
        victories = 0

        original_stats = {}
        for char in self.game.all_characters:
            original_stats[char.name] = {
                'max_hp': char.max_hp,
                'hp': char.hp,
                'max_energy': char.max_energy,
                'energy': char.energy
            }

        while True:
            rounds += 1

            clear_screen()
            print("\n" + "🌀" * 110)
            slow_print(f"🌀 CHAOS ROUND {rounds} 🌀", 0.05)
            print("🌀" * 110)

            party_size = random.randint(1, 4)
            party = []

            for char in self.game.all_characters:
                if char.name in original_stats:
                    stats = original_stats[char.name]
                    char.max_hp = stats['max_hp']
                    char.hp = stats['hp']
                    char.max_energy = stats['max_energy']
                    char.energy = stats['energy']

            available_chars = [c for c in self.game.all_characters if c.is_alive()]
            if not available_chars:
                print("No characters available! Game over.")
                break

            random.shuffle(available_chars)
            for i in range(min(party_size, len(available_chars))):
                char = available_chars[i]
                if random.random() < 0.3:
                    char.max_hp = int(char.max_hp * random.uniform(0.5, 2.0))
                    char.hp = char.max_hp
                party.append(char)

            count = 0
            for champion in party:
                if champion.name in self.game.canon_pairings and random.random() < 0.5:
                    if activate_volund_for_character(champion, self.game):
                        count += 1
            if count > 0:
                print(f"🌀 [CHAOS] Chaos grants Völundr to {count} champion(s)!")

            print(f"\nYour chaotic party: {', '.join([c.name for c in party])}")

            enemy_size = random.randint(1, 4)
            enemies = []

            enemy_creators = [
                create_enemy_god_servant, create_enemy_valkyrie_trainee, create_enemy_demon,
                create_enemy_thor, create_enemy_zeus, create_enemy_poseidon,
                create_enemy_heracles, create_enemy_shiva, create_enemy_zerofuku,
                create_enemy_hajun, create_enemy_hades, create_enemy_beelzebub,
                create_enemy_apollo, create_enemy_susanoo, create_enemy_loki,
                create_enemy_odin, create_enemy_lu_bu, create_enemy_adam,
                create_enemy_kojiro, create_enemy_jack, create_enemy_raiden,
                create_enemy_buddha, create_enemy_qin, create_enemy_tesla,
                create_enemy_leonidas, create_enemy_okita, create_enemy_simo,
                create_enemy_kintoki
            ]

            for _ in range(enemy_size):
                creator = random.choice(enemy_creators)
                enemy = creator()

                if random.random() < 0.5:
                    enemy.max_hp = int(enemy.max_hp * random.uniform(0.3, 3.0))
                    enemy.hp = enemy.max_hp

                enemies.append(enemy)

            print(f"\nChaotic enemies: {', '.join([e.name for e in enemies])}")

            self.random_event(party, enemies)

            input("\nPress Enter to battle!")

            victory = self.game.battle(enemies, party)

            if victory:
                victories += 1
                print(f"\n✨ CHAOS ROUND {rounds} VICTORIOUS! ✨")

                self.random_reward(party)
            else:
                print(f"\n💀 CHAOS CLAIMS YOUR SOUL AT ROUND {rounds} 💀")
                break

            print(f"\nRecord: {victories} victories in {rounds} rounds")
            cont = input("\nContinue the chaos? (y/n): ").lower()
            if cont != 'y':
                break

        print("\n" + "=" * 110)
        slow_print(f"🌀 CHAOS MODE COMPLETE: {victories} VICTORIES IN {rounds} ROUNDS 🌀", 0.03)
        print("=" * 110)

        for char in self.game.all_characters:
            if char.name in original_stats:
                stats = original_stats[char.name]
                char.max_hp = stats['max_hp']
                char.hp = stats['hp']
                char.max_energy = stats['max_energy']
                char.energy = stats['energy']

        self.game.current_mode = "menu"
        input("Press Enter to return to menu...")

    def random_event(self, party, enemies):
        events = [
            ("💥 EARTHQUAKE! Everyone takes 50 damage!",
             lambda: [p.take_damage(50) for p in party] + [e.take_damage(50) for e in enemies]),

            ("✨ DIVINE BLESSING! Party heals 100 HP!",
             lambda: [p.heal(100) for p in party]),

            ("💀 CURSED GROUND! Enemies gain 50% more HP!",
             lambda: [setattr(e, 'max_hp', int(e.max_hp * 1.5)) or setattr(e, 'hp', e.max_hp) for e in enemies]),

            ("⚡ TIME DISTORTION! Everyone gets an extra turn!",
             None),

            ("🛡️ VALKYRIE'S PROTECTION! Party gains defense!",
             lambda: [p.add_status_effect(StatusEffect.DEFEND, 1) for p in party]),

            ("👁️ ADAM'S EYES GLOW! Copy chance doubled this battle!",
             lambda: [setattr(p, 'temp_copy_boost', True) for p in party if p.name == "Adam"]),

            ("💢 BERSERKER RAGE! Everyone deals double damage but takes double damage!",
             lambda: [p.add_status_effect(StatusEffect.BERSERK, 3) for p in party] +
                     [e.add_status_effect(StatusEffect.BERSERK, 3) for e in enemies]),

            ("🌀 REALM SHIFT! Random realms activate for all!",
             lambda: [p.activate_realm(random.choice(p.realms)) if p.realms else None for p in party] +
                     [e.activate_realm(random.choice(e.realms)) if e.realms else None for e in enemies])
        ]

        event = random.choice(events)
        print(f"\n🌀 RANDOM EVENT: {event[0]}")
        if event[1]:
            event[1]()
        time.sleep(2)

    def random_reward(self, party):
        rewards = [
            ("💪 POWER SURGE", lambda p: setattr(p, 'max_hp', int(p.max_hp * 1.1)) or p.heal(p.max_hp)),
            ("⚡ ENERGY WELL",
             lambda p: setattr(p, 'max_energy', int(p.max_energy * 1.1)) or setattr(p, 'energy', p.max_energy)),
            ("👁️ TECHNIQUE MASTERY", lambda p: setattr(p, 'copy_count', min(p.max_copy, p.copy_count + 1)) if hasattr(p,
                                                                                                                      'copy_count') else None),
            ("🩸 BLOOD OF THE GODS", lambda p: p.heal(200)),
            ("✨ DIVINE AWAKENING",
             lambda p: setattr(p, 'divine_mode', True) or setattr(p, 'divine_timer', 3) or p.add_status_effect(
                 StatusEffect.DIVINE, 3)),
            ("🛡️ VALKYRIE'S FAVOR", lambda p: setattr(p, 'volund_active', True) if not p.volund_active else None)
        ]

        reward = random.choice(rewards)
        print(f"\n✨ CHAOS REWARD: {reward[0]}!")

        for char in party:
            if char.is_alive():
                reward[1](char)

        time.sleep(2)


# ============================================================================
# TRAINING MODE
# ============================================================================

class TrainingMode:
    def __init__(self, game):
        self.game = game

    def run(self):
        self.game.current_mode = "training"

        while True:
            clear_screen()
            print("\n" + "=" * 110)
            slow_print("🥋🥋🥋 TRAINING MODE 🥋🥋🥋", 0.03)
            print("=" * 110)
            print("Choose your training partner:")
            print("-" * 110)

            options = [
                ("1", "Einherjar Soldier (Easy)", create_enemy_god_servant),
                ("2", "Valkyrie Trainee (Easy)", create_enemy_valkyrie_trainee),
                ("3", "Helheim Demon (Easy)", create_enemy_demon),
                ("4", "Thor (Medium)", create_enemy_thor),
                ("5", "Zeus (Medium)", create_enemy_zeus),
                ("6", "Poseidon (Medium)", create_enemy_poseidon),
                ("7", "Heracles (Medium)", create_enemy_heracles),
                ("8", "Shiva (Hard)", create_enemy_shiva),
                ("9", "Hajun (Hard)", create_enemy_hajun),
                ("10", "Hades (Hard)", create_enemy_hades),
                ("11", "Beelzebub (Hard)", create_enemy_beelzebub),
                ("12", "Odin (Very Hard)", create_enemy_odin),
                ("13", "Lü Bu (Medium)", create_enemy_lu_bu),
                ("14", "Adam (Hard)", create_enemy_adam),
                ("15", "Kojiro Sasaki (Medium)", create_enemy_kojiro),
                ("16", "Jack the Ripper (Medium)", create_enemy_jack),
                ("17", "Raiden Tameemon (Hard)", create_enemy_raiden),
                ("18", "Buddha (Hard)", create_enemy_buddha),
                ("19", "Qin Shi Huang (Hard)", create_enemy_qin),
                ("20", "Nikola Tesla (Hard)", create_enemy_tesla),
                ("21", "Leonidas (Medium)", create_enemy_leonidas),
                ("22", "Soji Okita (Hard)", create_enemy_okita),
                ("23", "Simo Häyhä (Very Hard)", create_enemy_simo),
                ("24", "Sakata Kintoki (Hard)", create_enemy_kintoki),
                ("25", "Random Fighter", None),
                ("26", "Random 3 Fighters", None)
            ]

            col1 = options[:9]
            col2 = options[9:18]
            col3 = options[18:]

            for i in range(max(len(col1), len(col2), len(col3))):
                line = ""
                if i < len(col1):
                    line += f"{col1[i][0]:3}. {col1[i][1]:30}"
                else:
                    line += " " * 35

                if i < len(col2):
                    line += f"  {col2[i][0]:3}. {col2[i][1]:30}"
                else:
                    line += " " * 38

                if i < len(col3):
                    line += f"  {col3[i][0]:3}. {col3[i][1]}"

                print(line)

            print("\n" + "-" * 110)
            print("  c. Custom Match (Choose fighters)")
            print("  s. Save Game")
            print("  b. Back to Main Menu")
            print("-" * 110)

            choice = input("> ").strip()

            if choice.lower() == 'b':
                self.game.current_mode = "menu"
                return
            elif choice.lower() == 's':
                self.game.save_game()
                continue
            elif choice.lower() == 'c':
                self.custom_match()
                continue

            enemies = []

            if choice == '25':
                creators = [opt[2] for opt in options if opt[2] is not None]
                enemies = [random.choice(creators)()]
            elif choice == '26':
                creators = [opt[2] for opt in options if opt[2] is not None]
                for _ in range(3):
                    enemies.append(random.choice(creators)())
            else:
                for key, name, func in options:
                    if choice == key and func:
                        enemies = [func()]
                        break

            if enemies:
                # FIXED: rest() before party select so it doesn't wipe freshly activated Völundrs
                self.game.rest()

                party = self.game.select_party(3)
                if not party:
                    continue

                count = activate_volund_for_party(party, self.game)
                if count > 0:
                    print(f"   → Völundr activated for {count} champion(s)")

                self.game.battle(enemies, party)
                input("\nPress Enter to continue...")

    def custom_match(self):
        print("\n" + "=" * 110)
        slow_print("⚙️ CUSTOM MATCH SETUP ⚙️", 0.03)
        print("=" * 110)

        # FIXED: rest() first so it doesn't wipe Völundrs activated during party select
        self.game.rest()

        print("\nChoose your party size (1-4):")
        try:
            party_size = int(input("> ").strip())
            party_size = max(1, min(4, party_size))
        except:
            party_size = 3

        party = self.game.select_party(party_size)
        if not party:
            return

        count = activate_volund_for_party(party, self.game)
        if count > 0:
            print(f"   → Völundr activated for {count} champion(s)")

        print("\nChoose enemy count (1-4):")
        try:
            enemy_size = int(input("> ").strip())
            enemy_size = max(1, min(4, enemy_size))
        except:
            enemy_size = 1

        enemies = []
        print("\nSelect enemies:")
        print("1. Choose individually")
        print("2. Random selection")

        enemy_choice = input("> ").strip()

        if enemy_choice == '1':
            all_enemy_funcs = [
                create_enemy_god_servant, create_enemy_valkyrie_trainee, create_enemy_demon,
                create_enemy_thor, create_enemy_zeus, create_enemy_poseidon,
                create_enemy_heracles, create_enemy_shiva, create_enemy_zerofuku,
                create_enemy_hajun, create_enemy_hades, create_enemy_beelzebub,
                create_enemy_apollo, create_enemy_susanoo, create_enemy_loki,
                create_enemy_odin, create_enemy_lu_bu, create_enemy_adam,
                create_enemy_kojiro, create_enemy_jack, create_enemy_raiden,
                create_enemy_buddha, create_enemy_qin, create_enemy_tesla,
                create_enemy_leonidas, create_enemy_okita, create_enemy_simo,
                create_enemy_kintoki
            ]

            enemy_names = [
                "Einherjar Soldier", "Valkyrie Trainee", "Helheim Demon",
                "Thor", "Zeus", "Poseidon", "Heracles", "Shiva", "Zerofuku",
                "Hajun", "Hades", "Beelzebub", "Apollo", "Susano'o", "Loki", "Odin",
                "Lü Bu", "Adam", "Kojiro Sasaki", "Jack the Ripper", "Raiden Tameemon",
                "Buddha", "Qin Shi Huang", "Nikola Tesla", "Leonidas", "Soji Okita",
                "Simo Häyhä", "Sakata Kintoki"
            ]

            for i in range(enemy_size):
                print(f"\nSelect enemy {i + 1}:")
                for j, name in enumerate(enemy_names):
                    print(f"  {j + 1}. {name}")

                try:
                    idx = int(input("> ").strip()) - 1
                    if 0 <= idx < len(all_enemy_funcs):
                        enemies.append(all_enemy_funcs[idx]())
                except:
                    enemies.append(random.choice(all_enemy_funcs)())
        else:
            all_funcs = [
                create_enemy_god_servant, create_enemy_valkyrie_trainee, create_enemy_demon,
                create_enemy_thor, create_enemy_zeus, create_enemy_poseidon,
                create_enemy_heracles, create_enemy_shiva, create_enemy_zerofuku,
                create_enemy_hajun, create_enemy_hades, create_enemy_beelzebub,
                create_enemy_apollo, create_enemy_susanoo, create_enemy_loki,
                create_enemy_odin, create_enemy_lu_bu, create_enemy_adam,
                create_enemy_kojiro, create_enemy_jack, create_enemy_raiden,
                create_enemy_buddha, create_enemy_qin, create_enemy_tesla,
                create_enemy_leonidas, create_enemy_okita, create_enemy_simo,
                create_enemy_kintoki
            ]
            for _ in range(enemy_size):
                enemies.append(random.choice(all_funcs)())

        print(f"\nCustom Match: Your {party_size} vs {enemy_size} enemies")
        input("Press Enter to begin!")
        self.game.battle(enemies, party)
        input("\nPress Enter to continue...")


# ============================================================================
# MAIN GAME CLASS
# ============================================================================

class RagnarokGame:
    def __init__(self, load_saved=True):
        self.current_mode = "menu"

        self.thor = Thor()
        self.zeus = Zeus()
        self.poseidon = Poseidon()
        self.heracles = Heracles()
        self.shiva = Shiva()
        self.zerofuku = Zerofuku()
        self.hajun = Hajun()
        self.hades = Hades()
        self.beelzebub = Beelzebub()
        self.apollo = Apollo()
        self.susanoo = Susanoo()
        self.loki = Loki()
        self.odin = Odin()

        self.lu_bu = LuBu()
        self.adam = Adam()
        self.kojiro = KojiroSasaki()
        self.jack = JackTheRipper()
        self.raiden = RaidenTameemon()
        self.buddha = Buddha()
        self.qin = QinShiHuang()
        self.tesla = NikolaTesla()
        self.leonidas = Leonidas()
        self.okita = SojiOkita()
        self.simo = SimoHayha()
        self.kintoki = SakataKintoki()

        self.all_gods = [
            self.thor, self.zeus, self.poseidon, self.heracles, self.shiva,
            self.zerofuku, self.hajun, self.hades, self.beelzebub, self.apollo,
            self.susanoo, self.loki, self.odin
        ]

        self.all_humans = [
            self.lu_bu, self.adam, self.kojiro, self.jack, self.raiden,
            self.buddha, self.qin, self.tesla, self.leonidas, self.okita,
            self.simo, self.kintoki
        ]

        self.all_characters = self.all_gods + self.all_humans

        self.valkyries_status = {
            "Hrist": "available", "Thrud": "available", "Randgriz": "available",
            "Geirölul": "available", "Skalmöld": "available", "Reginleif": "available",
            "Ráðgríðr": "available", "Göndul": "available", "Alvitr": "available",
            "Hlökk": "available", "Skeggjöld": "available",
            "Brunhilde": "organizer", "Göll": "assistant"
        }

        self.canon_pairings = {
            "Lü Bu": {"valkyrie_name": "Randgriz", "valkyrie_enum": "RANDGRIZ", "valkyrie_index": 3},
            "Adam": {"valkyrie_name": "Reginleif", "valkyrie_enum": "REGINLEIF", "valkyrie_index": 6},
            "Kojiro Sasaki": {"valkyrie_name": "Hrist", "valkyrie_enum": "HRIST", "valkyrie_index": 1},
            "Jack the Ripper": {"valkyrie_name": "Hlökk", "valkyrie_enum": "HLÖKK", "valkyrie_index": 10},
            "Raiden Tameemon": {"valkyrie_name": "Thrud", "valkyrie_enum": "THRUD", "valkyrie_index": 2},
            "Qin Shi Huang": {"valkyrie_name": "Alvitr", "valkyrie_enum": "ALVITR", "valkyrie_index": 9},
            "Nikola Tesla": {"valkyrie_name": "Göndul", "valkyrie_enum": "GÖNDUL", "valkyrie_index": 8},
            "Leonidas": {"valkyrie_name": "Geirölul", "valkyrie_enum": "GEIRÖLUL", "valkyrie_index": 4},
            "Soji Okita": {"valkyrie_name": "Skalmöld", "valkyrie_enum": "SKALMÖLD", "valkyrie_index": 5},
            "Simo Häyhä": {"valkyrie_name": "Ráðgríðr", "valkyrie_enum": "RÁÐGRÍÐR", "valkyrie_index": 7},
            "Sakata Kintoki": {"valkyrie_name": "Skeggjöld", "valkyrie_enum": "SKEGGJÖLD", "valkyrie_index": 11}
        }

        self.story_progress = {
            "round1_complete": False, "round2_complete": False, "round3_complete": False,
            "round4_complete": False, "round5_complete": False, "round6_complete": False,
            "round7_complete": False, "round8_complete": False, "round9_complete": False,
            "round10_complete": False, "round11_complete": False, "round12_complete": False
        }

        self.humanity_score = 0
        self.gods_score = 0
        self.round_number = 1
        self.party = []
        self.enemies = []
        self.turn_count = 0
        self.victories = 0
        self.total_kills = 0
        self.battle_log = []

        self.survival = SurvivalMode(self)
        self.boss_rush = BossRushMode(self)
        self.gauntlet = GauntletMode(self)
        self.chaos = ChaosMode(self)
        self.training = TrainingMode(self)

        if load_saved:
            self.load_game()

    def check_valkyrie_available(self, valkyrie_name):
        return self.valkyries_status.get(valkyrie_name, "unavailable") == "available"

    def get_valkyrie_partner(self, valkyrie_name):
        for human, data in self.canon_pairings.items():
            if data["valkyrie_name"] == valkyrie_name:
                return human
        return "Unknown"

    def get_valkyrie_by_index(self, index):
        for valkyrie in Valkyrie:
            if valkyrie.index == index:
                return valkyrie
        return None

    def get_human_by_valkyrie_index(self, index):
        for human, data in self.canon_pairings.items():
            if data["valkyrie_index"] == index:
                return human
        return None

    def mark_valkyrie_fallen(self, valkyrie_name):
        if valkyrie_name in self.valkyries_status:
            self.valkyries_status[valkyrie_name] = "fallen"
            print(f"💔 {valkyrie_name} has fallen")

    def valkyrie_management_menu(self):
        # FIXED: recursive returns → while True loop
        while True:
            print("\n" + "=" * 110)
            slow_print("⚔️⚔️⚔️ VALKYRIE MANAGEMENT ⚔️⚔️⚔️", 0.03)
            print("=" * 110)

            available = []
            fallen = []

            for name, status in self.valkyries_status.items():
                if status == "available":
                    available.append(name)
                elif status == "fallen":
                    fallen.append(name)

            if available:
                print("\n✨ AVAILABLE VALKYRIES:")
                for name in available:
                    partner = self.get_valkyrie_partner(name)
                    index = Valkyrie.get_index_by_name(name.upper())
                    print(f"  [{index:2d}] ✅ {name} (Partner: {partner})")

            if fallen:
                print("\n💀 FALLEN VALKYRIES:")
                for name in fallen:
                    partner = self.get_valkyrie_partner(name)
                    index = Valkyrie.get_index_by_name(name.upper())
                    print(f"  [{index:2d}] ❌ {name} (Partner: {partner})")

            print("\nOPTIONS:")
            print("  1. 🔄 Reset ALL fallen Valkyries")
            print("  2. 🔄 Reset specific Valkyrie (by name)")
            print("  3. 🔄 Reset specific Valkyrie (by index)")
            print("  4. 📖 View pairings")
            print("  b. Back")

            choice = input("> ").strip()
            if choice == 'b':
                return
            elif choice == '1':
                if not fallen:
                    print("✅ No fallen Valkyries!")
                    continue
                confirm = input(f"Reset ALL {len(fallen)} fallen Valkyries? (y/n): ").lower()
                if confirm == 'y':
                    count = 0
                    for valk in fallen:
                        self.valkyries_status[valk] = "available"
                        count += 1
                    print(f"✨ {count} Valkyries resurrected!")
                    self.save_game()
                continue
            elif choice == '2':
                if not fallen:
                    print("✅ No fallen Valkyries!")
                    continue
                print("\nSelect Valkyrie by name:")
                for i, name in enumerate(fallen):
                    partner = self.get_valkyrie_partner(name)
                    index = Valkyrie.get_index_by_name(name.upper())
                    print(f"  {i + 1}. {name} (Index: {index}) (Partner: {partner})")
                valk_choice = input("> ").strip()
                try:
                    idx = int(valk_choice) - 1
                    if 0 <= idx < len(fallen):
                        name = fallen[idx]
                        confirm = input(f"Resurrect {name}? (y/n): ").lower()
                        if confirm == 'y':
                            self.valkyries_status[name] = "available"
                            print(f"✨ {name} resurrected!")
                            self.save_game()
                except:
                    pass
                continue
            elif choice == '3':
                if not fallen:
                    print("✅ No fallen Valkyries!")
                    continue
                print("\nEnter Valkyrie index to resurrect:")
                for name in fallen:
                    index = Valkyrie.get_index_by_name(name.upper())
                    partner = self.get_valkyrie_partner(name)
                    print(f"  [{index}] {name} (Partner: {partner})")
                try:
                    index_input = int(input("Index: ").strip())
                    found = None
                    for name in fallen:
                        if Valkyrie.get_index_by_name(name.upper()) == index_input:
                            found = name
                            break
                    if found:
                        confirm = input(f"Resurrect {found}? (y/n): ").lower()
                        if confirm == 'y':
                            self.valkyries_status[found] = "available"
                            print(f"✨ {found} resurrected!")
                            self.save_game()
                    else:
                        print("❌ No fallen Valkyrie with that index!")
                except:
                    print("❌ Invalid input!")
                continue
            elif choice == '4':
                self.show_valkyrie_pairings()
                continue

    def show_valkyrie_pairings(self):
        print("\n" + "=" * 110)
        slow_print("📖 CANON VALKYRIE-HUMAN PAIRINGS", 0.03)
        print("=" * 110)

        pairings_data = [
            ("Round 1", "Randgriz", 3, "Lü Bu"),
            ("Round 2", "Reginleif", 6, "Adam"),
            ("Round 3", "Hrist", 1, "Kojiro Sasaki"),
            ("Round 4", "Hlökk", 10, "Jack the Ripper"),
            ("Round 5", "Thrud", 2, "Raiden Tameemon"),
            ("Round 6", "(Buddha has no Valkyrie)", -1, ""),
            ("Round 7", "Alvitr", 9, "Qin Shi Huang"),
            ("Round 8", "Göndul", 8, "Nikola Tesla"),
            ("Round 9", "Geirölul", 4, "Leonidas"),
            ("Round 10", "Skalmöld", 5, "Soji Okita"),
            ("Round 11", "Ráðgríðr", 7, "Simo Häyhä"),
            ("Round 12", "Skeggjöld", 11, "Sakata Kintoki")
        ]

        print()
        for round_name, valkyrie, index, human in pairings_data:
            if index >= 0:
                print(f"    {round_name}:  {valkyrie:<12} [Index:{index:2d}] ↔  {human}")
            else:
                print(f"    {round_name}:  {valkyrie}")

        input("\nPress Enter to continue...")

    def select_party(self, max_size=3, faction=None):
        # FIXED: faction switching was recursive — now uses while True loop
        while True:
            print("\n" + "=" * 110)
            slow_print("✨✨✨ SELECT YOUR CHAMPIONS ✨✨✨", 0.03)
            print("=" * 110)
            print(f"Choose up to {max_size} fighters:")
            print("-" * 110)

            if faction == "Humans":
                char_list = self.all_humans
                title = "HUMAN CHAMPIONS"
            elif faction == "Gods":
                char_list = self.all_gods
                title = "GODS"
            else:
                char_list = self.all_characters
                title = "ALL FIGHTERS (Humans + Gods)"

            print(f"  {title}:")
            available = []
            for i, char in enumerate(char_list):
                if char.is_alive():
                    valkyrie_info = f" [{char.valkyrie.name}]" if char.valkyrie else ""
                    affil = f" ({char.affiliation})" if char.affiliation else ""
                    weapon_info = f" [{char.volund_weapon}]" if char.volund_weapon else ""

                    valk_available = ""
                    if char.name in self.canon_pairings and not char.volund_active:
                        valk_name = self.canon_pairings[char.name]["valkyrie_name"]
                        if self.check_valkyrie_available(valk_name):
                            valk_available = f" [✨ {valk_name} available]"

                    # FIXED: format_status_bar already includes icons — don't add them again
                    bar = VisualIndicator.format_status_bar(char, 20)
                    print(f"  {i + 1}. {char.name}{affil}{weapon_info}{valkyrie_info}{valk_available} |{bar}")
                    available.append(char)

            print(f"\n  a. Auto-select (first {max_size})")
            print("  g. Switch to Gods")
            print("  h. Switch to Humans")
            print("  c. Cancel")
            print("-" * 110)

            choice = input("> ").strip().lower()
            if choice == 'c':
                return None
            elif choice == 'g':
                faction = "Gods"
                continue  # FIXED: was return self.select_party(max_size, "Gods")
            elif choice == 'h':
                faction = "Humans"
                continue  # FIXED: was return self.select_party(max_size, "Humans")
            elif choice == 'a':
                selected = available[:max_size]
                for char in selected:
                    if char.name in self.canon_pairings and not char.volund_active:
                        activate_volund_for_character(char, self)
                return selected

            selected = []
            while len(selected) < max_size:
                try:
                    idx = int(input(f"Champion {len(selected) + 1}: ")) - 1
                    if 0 <= idx < len(available):
                        char = available[idx]
                        if char not in selected:
                            selected.append(char)
                            print(f"  ✓ Added {char.name}")

                            if char.name in self.canon_pairings and not char.volund_active:
                                if activate_volund_for_character(char, self):
                                    print(f"     ⚔️ Völundr automatically activated with {char.valkyrie.icon_name}!")
                        else:
                            print("  ✗ Already selected")
                    else:
                        print("  ✗ Invalid number")
                except:
                    break

            if not selected:
                selected = available[:max_size]
                for char in selected:
                    if char.name in self.canon_pairings and not char.volund_active:
                        activate_volund_for_character(char, self)

            return selected
    def enemy_turn(self, enemy, current_party=None, current_enemies=None):
        party = current_party if current_party is not None else self.party
        enemies = current_enemies if current_enemies is not None else self.enemies

        if not enemy.is_alive():
            return
        if not any(c.is_alive() for c in party):
            return

        if enemy.stunned:
            print(f"⚡ [STUNNED] {enemy.name} is stunned!")
            enemy.stunned = False
            return

        if enemy.bound:
            print(f"⚪ [BOUND] {enemy.name} is bound!")
            enemy.bound = False
            return

        if hasattr(enemy, 'exhausted') and enemy.exhausted:
            if random.random() < 0.3:
                enemy.exhausted = False
                print(f"  😫 [EXHAUSTED] {enemy.name} recovers from exhaustion!")
            else:
                print(f"  😫 [EXHAUSTED] {enemy.name} is exhausted and cannot act!")
                return

        if hasattr(enemy, 'possessed') and enemy.possessed:
            print(f"  👹 [POSSESSED] {enemy.name} is possessed and cannot act!")
            possession_damage = 25
            enemy.take_damage(possession_damage, ignore_defense=True)
            print(f"     Takes {possession_damage} damage from demonic corruption!")
            return

        enemy.energy = min(enemy.max_energy, enemy.energy + 15)

        adam = None
        for char in party:
            if char.name == "Adam" and char.is_alive() and hasattr(char, 'attempt_copy'):
                adam = char
                break

        buddha = None
        for char in party:
            if char.name == "Buddha" and char.is_alive():
                buddha = char
                if hasattr(enemy, 'soul_dark') and enemy.soul_dark:
                    if buddha.future_sight_active:
                        result = buddha.check_soul_light(enemy)
                        print_ability_result(result)
                break

        # Find Loki for clone targeting
        loki_char = None
        for c in party:
            if c.name == "Loki" and c.is_alive() and hasattr(c, 'clones') and c.clones:
                loki_char = c
                break

        if hasattr(enemy, 'ai_pattern') and enemy.ai_pattern:
            affordable_abilities = []
            for pattern_key in enemy.ai_pattern:
                if pattern_key in enemy.abilities:
                    abil = enemy.abilities[pattern_key]
                    if enemy.energy >= abil.get("cost", 25):
                        affordable_abilities.append(pattern_key)

            if affordable_abilities:
                # Check for clone targeting
                if loki_char and loki_char.clones:
                    active_clones = [cl for cl in loki_char.clones if cl["active"]]
                    if active_clones and random.random() < 0.4:
                        # Clone gets hit instead
                        clone_idx = loki_char.clones.index(random.choice(active_clones))
                        dmg = random.randint(30, 60)  # Base damage for clone hit
                        loki_char.clone_take_damage(clone_idx, dmg)
                        print(f"  👥 The attack hits one of Loki's clones!")
                        return

                # Try to use the next pattern ability in sequence
                for attempt in range(len(enemy.ai_pattern)):
                    idx = (enemy.ai_pattern_index + attempt) % len(enemy.ai_pattern)
                    candidate = enemy.ai_pattern[idx]
                    if candidate in enemy.abilities and enemy.energy >= enemy.abilities[candidate].get("cost", 25):
                        pattern_key = candidate
                        enemy.ai_pattern_index = (idx + 1) % len(enemy.ai_pattern)
                        break
                else:
                    # All pattern abilities unaffordable, pick cheapest available
                    pattern_key = min(affordable_abilities,
                                     key=lambda k: enemy.abilities[k].get("cost", 25))

                abil = enemy.abilities[pattern_key]
                if enemy.energy >= abil.get("cost", 25):
                    enemy.energy -= abil.get("cost", 25)
                    targets = [c for c in party if c.is_alive()]
                    if targets:
                        t = random.choice(targets)

                        dmg = random.randint(abil["dmg"][0], abil["dmg"][1])

                        mult, _ = enemy.get_damage_multiplier()
                        dmg = int(dmg * mult)

                        ignore_defense = abil.get("blockable", True) == False

                        if t.defending and not ignore_defense:
                            dmg = int(dmg * 0.5)
                            t.defending = False

                        if abil.get("bind", False):
                            t.bound = True
                            t.add_status_effect(StatusEffect.BIND, 1)

                        if t.name == "Qin Shi Huang" and hasattr(t, 'counter_ready') and t.counter_ready:
                            counter_result = t.counter_attack(dmg, enemy)
                            if counter_result:
                                print(f"  {counter_result}")
                                dmg = 0

                        t.take_damage(dmg, ignore_defense=ignore_defense)

                        print(f"{enemy.name} uses {abil['name']} for {dmg} damage!")

                        if adam:
                            is_divine = abil.get("divine", False) or "divine" in abil.get("name", "").lower()

                            copy_result = adam.attempt_copy(
                                technique_name=abil['name'],
                                technique_damage=abil['dmg'],
                                target=t,
                                enemy_rank=enemy.rank if hasattr(enemy, 'rank') else 50,
                                is_divine=is_divine
                            )

                            if copy_result:
                                print(f"  👁️ {copy_result}")

                            elif random.random() < 0.1 and adam.technique_view_count.get(abil['name'], 0) > 0:
                                views = adam.technique_view_count[abil['name']]
                                chance = 40 + (views * 15)
                                if chance > 95:
                                    chance = 95
                                print(f"  👁️ [STUDYING] Adam studies {abil['name']}... ({chance}% copy chance)")

                        return

        first_abil = list(enemy.abilities.values())[0]
        if enemy.energy >= first_abil.get("cost", 25):
            enemy.energy -= first_abil.get("cost", 25)
            targets = [c for c in party if c.is_alive()]
            if targets:
                t = random.choice(targets)
                dmg = random.randint(first_abil["dmg"][0], first_abil["dmg"][1])
                mult, _ = enemy.get_damage_multiplier()
                dmg = int(dmg * mult)
                if t.defending:
                    dmg = int(dmg * 0.5)
                    t.defending = False
                t.take_damage(dmg)
                print(f"{enemy.name} uses {first_abil['name']} for {dmg} damage!")

                if adam:
                    is_divine = first_abil.get("divine", False)
                    copy_result = adam.attempt_copy(
                        technique_name=first_abil['name'],
                        technique_damage=first_abil['dmg'],
                        target=t,
                        enemy_rank=enemy.rank if hasattr(enemy, 'rank') else 50,
                        is_divine=is_divine
                    )
                    if copy_result:
                        print(f"  👁️ {copy_result}")

    def use_ability(self, character):
        while True:
            # FIXED: Exhausted check applies to ALL characters (not just Beelzebub)
            if hasattr(character, 'exhausted') and character.exhausted:
                if character.name == "Beelzebub" and hasattr(character, 'can_use_ability'):
                    can_use, msg = character.can_use_ability()
                    if not can_use:
                        print(f"\n{msg}")
                        timer = getattr(character, 'exhausted_timer', 1)
                        print(f"  😫 {character.name} skips the turn (exhausted for {timer} more turns).")
                        time.sleep(1)
                        return True
                else:
                    print(f"\n😫 [EXHAUSTED] {character.name} is too exhausted to act!")
                    character.exhausted = False
                    return True

            print(f"\n" + "=" * 110)
            slow_print(f"✦✦✦ {character.name} [{character.title}] ✦✦✦", 0.03)
            print("=" * 110)

            bar = VisualIndicator.format_status_bar(character, 40)
            _pct = int(100 * character.hp / character.max_hp)
            _hico = "❤️" if _pct > 50 else ("🟡" if _pct > 25 else "🔴")
            print(f"{_hico} HP: {character.hp}/{character.max_hp} ({_pct}%)  ⚡ Energy: {character.energy}/{character.max_energy}")

            if character.valkyrie:
                _vw = character.volund_weapon if character.volund_weapon else character.valkyrie.icon_name
                print(f"⚔️ VÖLUNDR: {_vw}")
            if character.active_realm != Realm.NONE:
                print(f"🔮 REALM: {character.active_realm.value}")

            if character.status_effects:
                effects = []
                for effect in character.status_effects:
                    if effect.effect_type == StatusEffect.VOLUNDR:
                        continue  # FIXED: permanent flag, not a combat status
                    icon, name, _ = effect.effect_type.value
                    if effect.stacks > 1:
                        effects.append(f"{icon}{name}×{effect.stacks} ({effect.duration}t)")
                    else:
                        effects.append(f"{icon}{name} ({effect.duration}t)")
                if effects:
                    print(f"📊 STATUS: {', '.join(effects)}")

            if character.name == "Adam" and hasattr(character, 'copy_count'):
                print(f"👁️ Copied: {character.copy_count}/{character.max_copy} | Blindness: {character.blindness}")

            if character.name == "Jack the Ripper" and hasattr(character, 'get_weapon_status'):
                character.get_weapon_status()

            print("-" * 110)

            available = {}
            for key, abil in list(character.abilities.items()):
                # FIXED: Filter out passive abilities - they cannot be manually activated
                if abil.get("type") == "passive":
                    continue
                cost = abil.get("cost", 0)
                if character.energy >= cost:
                    if "uses_left" in abil and abil["uses_left"] <= 0:
                        continue
                    if hasattr(character, 'can_use_ability') and character.name != "Beelzebub":
                        can_use, _ = character.can_use_ability(abil)
                        if not can_use:
                            continue
                    if abil.get("karma_only") and hasattr(character, 'tandava_karma_active'):
                        if not character.tandava_karma_active:
                            continue
                    # FIXED: Also filter ichor-only abilities when ichor is not active (Hades)
                    if abil.get("ichor_only") and hasattr(character, 'ichor_active') and not character.ichor_active:
                        continue
                    available[key] = abil

            if not available:
                print("❌ No abilities available! Skip turn.")
                time.sleep(1)
                return True

            print("\n📋 AVAILABLE ABILITIES:")
            print("-" * 110)

            damage_abilities = {k: v for k, v in available.items() if v.get("type") == "damage"}
            utility_abilities = {k: v for k, v in available.items() if v.get("type") != "damage"}

            if damage_abilities:
                print("  💢 DAMAGE:")
                for key in sorted(damage_abilities.keys(), key=lambda x: int(x) if x.isdigit() else x):
                    abil = damage_abilities[key]
                    dmg = abil["dmg"]
                    dmg_str = f"{dmg[0]}-{dmg[1]} DMG" if dmg != (0, 0) else ""
                    views = f" [Seen:{abil['views']}x]" if "views" in abil else ""

                    uses_str = ""
                    if "uses_left" in abil:
                        uses_str = f" [{abil['uses_left']}/{abil['max_uses']}]"

                    hits_str = f" [{abil['hits']} hits]" if "hits" in abil else ""

                    print(f"    {key}. {abil['name']:35} | {abil['cost']}E | {dmg_str}{views}{uses_str}{hits_str}")

            if utility_abilities:
                print("\n  🛡️ UTILITY/OTHER:")
                for key in sorted(utility_abilities.keys(), key=lambda x: int(x) if x.isdigit() else x):
                    abil = utility_abilities[key]
                    dmg = abil["dmg"]
                    dmg_str = f"{dmg[0]}-{dmg[1]} DMG" if dmg != (0, 0) else ""

                    uses_str = ""
                    if "uses_left" in abil:
                        uses_str = f" [{abil['uses_left']}/{abil['max_uses']}]"

                    print(f"    {key}. {abil['name']:35} | {abil['cost']}E | {dmg_str}{uses_str}")

            kojiro_dt_locked = (
                character.name == "Kojiro Sasaki"
                and hasattr(character, 'dual_wielding')
                and not character.dual_wielding
            )
            if character.divine_technique and character.energy >= character.divine_technique['cost'] and not kojiro_dt_locked:
                dt = character.divine_technique
                dt_key = None
                for key, abil in list(character.abilities.items()):
                    if abil.get("name") == dt["name"]:
                        dt_key = key
                        break

                if dt_key is None or dt_key not in available:
                    print(f"\n  ✨ DIVINE TECHNIQUE:")
                    print(f"    99. {dt['name']} | {dt['cost']}E | {dt['dmg'][0]}-{dt['dmg'][1]} DMG")
            elif kojiro_dt_locked and character.divine_technique:
                print(f"\n  🔒 LOCKED: {character.divine_technique['name']} (requires Re-Völundr dual wield)")

            passive_names = [ab['name'] for ab in character.abilities.values() if ab.get('type') == 'passive']
            if passive_names:
                print(f"  ── Always active: {' | '.join(passive_names)}")
            print("\n🎮  0.Describe  00.Divine Realm  0000.Skip(+15E)  00000.Back")
            if not character.volund_active and character.name in self.canon_pairings:
                print("     000.Activate Völundr")
            if character.name == "Adam" and hasattr(character, 'get_copy_stats'):
                print("     98.Copy Statistics")
            if character.name == "Jack the Ripper" and hasattr(character, 'get_weapon_status'):
                print("     97.Weapon Supplies")
            print("-" * 110)

            choice = input("> ").strip()

            if choice == '00000':
                return False
            elif choice == '0000':
                print(f"{character.name} skips turn. +15 Energy")
                character.energy = min(character.max_energy, character.energy + 15)
                return True
            elif choice == '000' and not character.volund_active:
                if character.name in self.canon_pairings:
                    activate_volund_for_character(character, self)
                    self.save_game()
                return False
            elif choice == '00':
                if character.realms:
                    print("\n🔮 AVAILABLE REALMS:")
                    for i, realm in enumerate(character.realms):
                        print(f"  {i + 1}. {realm.value}")
                    print("  b. Back")
                    realm_choice = input("> ").strip()
                    if realm_choice.isdigit():
                        idx = int(realm_choice) - 1
                        if 0 <= idx < len(character.realms):
                            result = character.activate_realm(character.realms[idx])
                            print(result)
                else:
                    print(f"{character.name} cannot activate realms.")
                return False
            elif choice == '98' and character.name == "Adam" and hasattr(character, 'get_copy_stats'):
                character.get_copy_stats()
                input("\nPress Enter to continue...")
                return False
            elif choice == '97' and character.name == "Jack the Ripper" and hasattr(character, 'get_weapon_status'):
                character.get_weapon_status()
                input("\nPress Enter to continue...")
                return False
            elif choice == '0':
                print("\n📖 SELECT ABILITY TO DESCRIBE:")
                for key in sorted(available.keys(), key=lambda x: int(x) if x.isdigit() else x):
                    abil = available[key]
                    print(f"  {key}. {abil['name']}")
                print("\n  b. Back")
                desc_choice = input("> ").strip()
                if desc_choice in available:
                    abil = available[desc_choice]
                    print("\n" + "─" * 80)
                    slow_print(f"📖 {abil['name']}", 0.04)
                    print("─" * 80)
                    if "desc" in abil:
                        print_desc(abil['desc'])
                    if "cost" in abil:
                        print(f"\n⚡ Energy Cost: {abil['cost']}")
                    if "dmg" in abil and abil["dmg"] != (0, 0):
                        print(f"💢 Damage: {abil['dmg'][0]}-{abil['dmg'][1]}")
                    if "views" in abil:
                        print(f"👁️ Times seen: {abil['views']}")
                    if "uses_left" in abil:
                        print(f"📦 Uses left: {abil['uses_left']}/{abil['max_uses']}")
                    print("─" * 80)
                    input("\nPress Enter to continue...")
                return False
            elif choice == '99' and character.divine_technique and character.energy >= character.divine_technique[
                'cost'] and not (character.name == "Kojiro Sasaki" and hasattr(character, 'dual_wielding') and not character.dual_wielding):
                # FIXED: Confirmation before using divine technique (high cost)
                dt = character.divine_technique
                print(f"\n✨ DIVINE TECHNIQUE: {dt['name']}")
                print(f"   Cost: {dt['cost']}E | Damage: {dt['dmg'][0]}-{dt['dmg'][1]}")
                print_desc(dt.get('desc', ''))
                confirm = input("\nUse this Divine Technique? (y/n): ").strip().lower()
                if confirm != 'y':
                    return False
                character.energy -= character.divine_technique['cost']
                target = self.select_target()
                if target:
                    dmg = random.randint(character.divine_technique['dmg'][0], character.divine_technique['dmg'][1])
                    mult, buffs = character.get_damage_multiplier()
                    dmg = int(dmg * mult)

                    ignore_defense = character.divine_technique.get("blockable", True) == False

                    target.take_damage(dmg, ignore_defense=ignore_defense)

                    print("\n" + "✨" * 55)
                    slow_print(f"✨✨✨ {character.divine_technique['name']} ✨✨✨", 0.05)
                    print("✨" * 55)

                    print(f"{character.name} unleashes DIVINE TECHNIQUE for {dmg} damage!")

                return True
            elif choice in available:
                ability = available[choice]

                if character.name == "Leonidas" and hasattr(character, 'can_use_ability'):
                    can_use, message = character.can_use_ability(ability)
                    if not can_use:
                        print(message)
                        return False

                # Pre-check for Kintoki's flash
                if ability.get("effect") == "flash" and hasattr(character, 'rune_of_eirin_active'):
                    if not character.rune_of_eirin_active:
                        print(f"❌ [RUNE NEEDED] {character.name} needs to activate Rune of Eirin first!")
                        character.energy += ability["cost"]
                        return False

                if hasattr(character, 'use_ability'):
                    if not character.use_ability(choice):
                        if character.name == "Poseidon":
                            cost = ability.get("cost", 0)
                            character.energy = max(0, character.energy - cost)
                            print(f"{character.name}'s pride wastes the turn! (-{cost}E)")
                        return True

                character.energy -= ability["cost"]

                if ability.get("type") == "damage":
                    target = self.select_target()
                    if target:
                        dmg = random.randint(ability["dmg"][0], ability["dmg"][1])
                        mult, buffs = character.get_damage_multiplier()
                        dmg = int(dmg * mult)

                        hits = ability.get("hits", 1)
                        if hits > 1:
                            total_dmg = 0
                            for hit in range(hits):
                                hit_dmg = random.randint(ability["dmg"][0] // hits, ability["dmg"][1] // hits)
                                hit_dmg = int(hit_dmg * mult)
                                target.take_damage(hit_dmg, ignore_defense=ability.get("blockable", True) == False)
                                total_dmg += hit_dmg
                            print(
                                f"{character.name} uses {ability['name']} for {total_dmg} total damage across {hits} hits!")
                        else:
                            ignore_defense = ability.get("blockable", True) == False

                            if ability.get("armor_break"):
                                print("⚔️ Armor break!")

                            if ability.get("bind", False):
                                target.bound = True
                                target.add_status_effect(StatusEffect.BIND, 1)
                                print(f"  🔗 {target.name} is bound!")

                            # Store target for Loki's clone attacks (Trickster's Gambit)
                            if character.name == "Loki" and ability.get("effect") == "gambit":
                                if hasattr(character, '_set_gambit_target'):
                                    character._set_gambit_target(target)

                            if ability.get("effect") == "hymn_wolves":
                                bite1 = dmg // 2
                                bite2 = dmg - bite1
                                target.take_damage(bite1)
                                target.take_damage(bite2)
                                print(f"  🐺 Geri bites for {bite1}! Freki bites for {bite2}!")
                                print(f"{character.name} uses {ability['name']} for {bite1 + bite2} total damage!")
                            else:
                                target.take_damage(dmg, ignore_defense=ignore_defense)
                                print(f"{character.name} uses {ability['name']} for {dmg} damage!")

                            # Post-damage hook (e.g. Odin's Yggdrasil life drain)
                            if hasattr(character, 'post_damage_hook') and "effect" in ability:
                                character.post_damage_hook(dmg, ability["effect"])

                        if "effect" in ability and ability["effect"] not in ["bind", "hymn_wolves"]:
                            if hasattr(character, 'apply_effect'):
                                result = character.apply_effect(ability["effect"], target=target)
                                if result:
                                    print_ability_result(result)

                        if hasattr(target, 'check_lilith_mark'):
                            if target.hp <= 0:
                                result = target.check_lilith_mark()
                                if result:
                                    print_ability_result(result)

                        if character.name == "Hajun" and ability.get("effect") == "possess":
                            if hasattr(target, 'possessed'):
                                result = character.use_possession(target)
                                if result:
                                    print_ability_result(result)

                        if character.name == "Heracles" and ability.get("labor"):
                            result = character.use_labor(ability["labor"])
                            if result:
                                print_ability_result(result)

                elif ability.get("type") == "clone":
                    # Loki's clone-creation abilities (Copy, Hveðrung)
                    if "effect" in ability:
                        if hasattr(character, 'apply_effect'):
                            result = character.apply_effect(ability["effect"])
                            if result:
                                print_ability_result(result)
                            else:
                                print(f"{character.name} uses {ability['name']}!")
                    else:
                        print(f"{character.name} uses {ability['name']}!")

                elif ability.get("type") in ["buff", "heal", "defense", "utility", "counter"]:

                    if "effect" in ability:
                        if hasattr(character, 'apply_effect'):
                            # FIXED: Some buff/utility effects debuff the enemy via tgt-routing.
                            # Without target=, tgt defaults to self. Pass a target for those effects.
                            _DEBUFF_EFFECTS = {"threads", "hymn_illusion"}
                            _tgt = self.select_target() if ability["effect"] in _DEBUFF_EFFECTS else None
                            result = character.apply_effect(ability["effect"], target=_tgt)
                            if result:
                                print_ability_result(result)
                            else:
                                print(f"{character.name} uses {ability['name']}!")
                    else:
                        print(f"{character.name} uses {ability['name']}!")

                    if ability.get("dmg") != (0, 0):
                        target = self.select_target()
                        if target:
                            dmg = random.randint(ability["dmg"][0], ability["dmg"][1])
                            mult, buffs = character.get_damage_multiplier()
                            dmg = int(dmg * mult)
                            target.take_damage(dmg)
                            print(f"  {ability['name']} deals {dmg} damage!")

                    # Handle Hajun's possession in utility branch
                    if character.name == "Hajun" and ability.get("effect") == "possess":
                        target = self.select_target()
                        if target:
                            result = character.use_possession(target)
                            if result:
                                print_ability_result(result)

                return True
            else:
                print("❌ Invalid choice.")
                return False

    def select_target(self, allies=False):
        if allies:
            targets = [c for c in self.party if c.is_alive()]
            if not targets:
                return None
            print("\n✨ ALLY TARGETS:")
        else:
            targets = [e for e in self.enemies if e.is_alive()]
            if not targets:
                return None
            print("\n💀 ENEMY TARGETS:")

        for i, t in enumerate(targets):
            bar = VisualIndicator.format_status_bar(t, 20)
            print(f"  {i + 1}. {t.name} |{bar}")

        while True:
            try:
                choice = int(input("> ")) - 1
                if 0 <= choice < len(targets):
                    return targets[choice]
                print("❌ Invalid target.")
            except:
                print("❌ Enter a number.")

    def display_health_bars(self, current_party=None, current_enemies=None):
        party = current_party if current_party is not None else self.party
        enemies = current_enemies if current_enemies is not None else self.enemies

        print("\n" + "=" * 110)
        print("✨✨✨ YOUR CHAMPIONS ✨✨✨")
        print("-" * 110)
        alive_members = [m for m in party if m.is_alive()]
        if not alive_members:
            print("  💀 All champions have fallen...")
        for member in party:
            if member.is_alive():
                bar = VisualIndicator.format_status_bar(member, 40)

                weapon_info = f" [{member.volund_weapon}]" if member.volund_weapon else ""

                energy_bar_len = 20
                energy_filled = int(energy_bar_len * member.energy / member.max_energy)
                energy_bar = "█" * energy_filled + "░" * (energy_bar_len - energy_filled)

                print(f"{member.name}{weapon_info:25} |{bar} ⚡{energy_bar}| {member.energy:3}E")

        print("\n" + "=" * 110)
        print("💀💀💀 ENEMIES 💀💀💀")
        print("-" * 110)
        for enemy in enemies:
            if enemy.is_alive():
                bar = VisualIndicator.format_status_bar(enemy, 40)

                affil = f" [{enemy.affiliation}]" if enemy.affiliation else ""
                rank_display = f" [Rank:{enemy.rank}]" if hasattr(enemy, 'rank') else ""

                print(f"{enemy.name:25} |{bar}{affil}{rank_display}")
        print("=" * 110)

    def add_log(self, message):
        self.battle_log.append(f"[T{self.turn_count}] {message}")
        print(f"[T{self.turn_count}] ", end='')
        slow_print(message, 0.02)

    def battle(self, enemies, party=None):
        current_enemies = enemies
        current_party = party if party else self.select_party()
        if not current_party:
            return False

        for char in current_party:
            if hasattr(char, 'ensure_divine_technique'):
                char.ensure_divine_technique()
        for enemy in current_enemies:
            if hasattr(enemy, 'ensure_divine_technique') and not enemy.divine_technique:
                enemy.ensure_divine_technique()

        turn_count = 0
        battle_log = []

        print("\n" + "=" * 110)
        slow_print("⚔️⚔️⚔️ RAGNAROK BATTLE ⚔️⚔️⚔️", 0.04)
        print("=" * 110)
        print(f"✨ CHAMPIONS: {', '.join([c.name for c in current_party])}")
        print(f"💀 ENEMIES: {', '.join([e.name for e in current_enemies])}")
        print("=" * 110)
        time.sleep(BATTLE_START_DELAY)

        # Set party and enemies once for the whole battle
        self.party = current_party
        self.enemies = current_enemies

        while True:
            turn_count += 1
            print(f"\n" + "═" * 110)
            print(f"  ⚔️  TURN {turn_count:3}  ⚔️   |   Humanity: {self.humanity_score}  |  Gods: {self.gods_score}")
            print("═" * 110)
            print(f"⚡ [ENERGY] All champions recover +20 energy!")

            for char in current_party:
                if char.is_alive():
                    char.energy = min(char.max_energy, char.energy + 20)
                    action = False
                    while not action:
                        self.display_health_bars(current_party, current_enemies)
                        action = self.use_ability(char)
                    if not any(e.is_alive() for e in current_enemies):
                        break

            if not any(e.is_alive() for e in current_enemies):
                break

            if not any(c.is_alive() for c in current_party):
                break

            print("\n" + "💀💀💀 ENEMY PHASE 💀💀💀")
            for enemy in current_enemies:
                if enemy.is_alive():
                    self.enemy_turn(enemy, current_party, current_enemies)

            for char in current_party:
                if char.name == "Odin" and hasattr(char, 'life_theft_active') and char.life_theft_active and char.drain_timer > 0:
                    for enemy in [e for e in current_enemies if e.is_alive()]:
                        drain_damage = 10
                        enemy.take_damage(drain_damage, ignore_defense=True)
                        print(f"  🌿 [LIFE THEFT] Odin's aura drains {drain_damage} HP from {enemy.name}!")

            for char in current_party:
                if char.name == "Loki" and hasattr(char, 'clones') and char.clones:
                    for i, clone in enumerate(char.clones):
                        if clone["active"] and random.random() < 0.5:
                            targets = [e for e in current_enemies if e.is_alive()]
                            if targets:
                                target = random.choice(targets)
                                char.clone_attack(i, target)

            for character in current_party + current_enemies:
                if character.name == "Beelzebub" and hasattr(character, 'check_lilith_mark'):
                    if character.hp <= 0:
                        result = character.check_lilith_mark()
                        if result:
                            print_ability_result(result)

            for char in current_party:
                if char.name == "Kojiro Sasaki" and hasattr(char, 'check_weapon_break'):
                    result = char.check_weapon_break()
                    if result:
                        print_ability_result(result)

            for char in current_party + current_enemies:
                if hasattr(char, 'possessed') and char.possessed:
                    if not char.has_status_effect(StatusEffect.POSSESSED):
                        char.possessed = False
                        print(f"  👹 {char.name} breaks free from possession!")

            self.cleanup(current_party, current_enemies)

            print("\n⏳ [STATUS] Updating effect durations...")
            for c in current_party + current_enemies:
                c.update_status_effects()

        self.display_health_bars(current_party, current_enemies)

        if any(e.is_alive() for e in current_enemies):
            print("\n" + "=" * 110)
            slow_print("💀💀💀 DEFEAT... 💀💀💀", 0.05)
            print("=" * 110)
            return False
        else:
            print("\n" + "=" * 110)
            slow_print("✨✨✨ VICTORY! ✨✨✨", 0.05)
            print("=" * 110)
            self.victories += 1
            self.total_kills += len([e for e in current_enemies if not e.is_alive()])

            if self.adam.is_alive() and self.adam.copy_count > 0:
                print(f"\n👁️ [ADAM] Adam ends the battle with {self.adam.copy_count} copied techniques!")

            return True

    def cleanup(self, party, enemies):
        for c in party + enemies:
            c.defending = False
            if hasattr(c, 'realm_timer') and c.realm_timer > 0:
                c.realm_timer -= 1
                if c.realm_timer <= 0:
                    c.active_realm = Realm.NONE
                    print(f"  ⏳ {c.name}'s realm effect fades.")
            if hasattr(c, 'divine_mode') and c.divine_mode:
                if hasattr(c, 'divine_timer'):
                    c.divine_timer -= 1
                    if c.divine_timer <= 0:
                        c.divine_mode = False
                        print(f"  ⏳ {c.name}'s divine mode fades.")
            if c.stunned and random.random() < 0.3:
                c.stunned = False
                print(f"  ⚡ {c.name} recovers from stun!")
            if c.bound and random.random() < 0.3:
                c.bound = False
                print(f"  🔗 {c.name} breaks free from binds!")

    def rest(self):
        print("\n" + "=" * 110)
        slow_print("🛌🛌🛌 VALHALLA RESTING 🛌🛌🛌", 0.04)
        print("=" * 110)

        for char in self.all_characters:
            char.hp = char.max_hp
            char.energy = char.max_energy
            char.defending = False
            char.active_realm = Realm.NONE
            char.stunned = False
            char.bound = False
            char.exhausted = False
            char.divine_mode = False
            char.divine_timer = 0
            char.status_effects = []
            char.possessed = False

            # FIXED: Reset Völundr after every battle — activated fresh each match
            char.reset_volund()

            if char.name == "Adam":
                char.copy_count = 0
                char.copied_techniques = []
                char.copied_techniques_data = {}
                char.technique_view_count = {}
                char.blindness = 0
                char.death_activated = False
                keys_to_remove = [k for k in char.abilities if k.isdigit() and int(k) >= 11]
                for k in keys_to_remove:
                    del char.abilities[k]
                print(f"  ✦ [ADAM] Sight restored. Copy slate cleared — Adam begins fresh.")
            elif char.name == "Kojiro Sasaki":
                char.scan_progress = 0
                char.simulations_complete = 0
                char.weapon_broken = False
                char.dual_wielding = False
                char.manju_muso = False
                char.damage_pressure = 0
            elif char.name == "Heracles":
                char.labors_used = 0
                if self.current_mode != "tournament":
                    char.tattoo_progress = 0
                char.cerberus_active = False
            elif char.name == "Raiden Tameemon":
                char.muscle_release = 0
                char.release_available = True
            elif char.name == "Nikola Tesla":
                char.teleport_charges = 3
                char.gematria_zone_active = False
                char.zero_max = False
                char.tesla_step = False
            elif char.name == "Simo Häyhä":
                char.organs_used = []
                char.organ_sacrifice = 0
                char.camouflage_active = False
            elif char.name == "Jack the Ripper":
                char.magic_pouches = {
                    "knives": 50, "piano_wires": 10, "umbrellas": 2, "scissors": 1,
                    "switchblade": 1, "grappling_hook": 1, "throwing_axes": 2, "cannonball": 1
                }
                char.environment_weapons = []
                char.arm_extended = False
                char.has_environment_weapon = False
                char.organ_shift_used = False
                if char.volund_active:
                    for key, ability in char.abilities.items():
                        if "uses_left" in ability:
                            ability["uses_left"] = ability["max_uses"]
            elif char.name == "Thor":
                if self.current_mode == "tournament":
                    char.teleport_uses = char.tournament_teleport_uses
                else:
                    char.teleport_uses = 3
                char.járngreipr_active = True
                char.mjolnir_awakened = False
                char.gloves_damage_timer = 0
            elif char.name == "Zeus":
                char.form = "Normal"
                char.adamas_timer = 0
                char.neck_fix_available = True
                char.meteor_jab_count = 0
                char.footwork_active = False
            elif char.name == "Poseidon":
                char.used_moves = []
                char.water_level = 100
                char.water_regen_timer = 0
            elif char.name == "Shiva":
                if self.current_mode != "tournament" or not char.permanent_arm_loss:
                    char.arms_remaining = 4
                    char.permanent_arm_loss = False
                char.tandava_level = 0
                char.tandava_karma_active = False
            elif char.name == "Zerofuku":
                char.misery_level = 0
                char.cleaver_heads = 1
            elif char.name == "Hades":
                char.ichor_active = False
                char.desmos_active = False
                char.drain_timer = 0
            elif char.name == "Beelzebub":
                char.chaos_used = False
                char.lilith_mark_used = False
                char.exhausted = False
                char.exhausted_timer = 0
                # Restore full ability kit (staff is rebuilt between battles)
                if hasattr(char, '_base_abilities'):
                    char.abilities = dict(char._base_abilities)
            elif char.name == "Apollo":
                char.expectation_bonus = 0
                char.threads_active = False
                char.thread_shield_active = False
                char.next_attack_multiplier = 1.0
            elif char.name == "Susano'o":
                char.musouken_used = 0
                char.yatagarasu_form = False
                char.musouken_active = False
                char.weapon_form = "onikiri"
            elif char.name == "Loki":
                char.clones = []
                char.perfect_clone = None
                char.andvaranaut_active = False
                char.shared_vision = False
            elif char.name == "Odin":
                char.form = "Old"
                char.life_theft_active = False
                char.active_treasures = set()
                char.treasure_timers = {}
                char.yggdrasil_awakening = False
                char.drain_timer = 0
            elif char.name == "Buddha":
                char.current_emotion = "serenity"
                char.current_weapon = "Twelve Deva Axe"
                char.future_sight_active = True
                char.zerofuku_fused = False
                char.story_trigger = False
                char.divine_technique = None
                # Restore full ability kit (remove fusion result, restore fusion option)
                char.abilities.pop('8', None)
                char.abilities['4'] = {
                    "name": "🪓 Six Realms Strike", "cost": 45, "dmg": (190, 260),
                    "type": "damage", "effect": "six_realms_strike",
                    "desc": "🪓 [SIX REALMS STRIKE] Buddha attacks with his currently equipped Six Realms weapon. Use Activate Six Realms first to select a weapon form. [TRANSFORMATION: The weapon strikes with the weight of all six realms behind it]"
                }
                char.abilities['7'] = {
                    "name": "🌀 Zerofuku Fusion", "cost": 80, "dmg": (0, 0),
                    "type": "buff", "effect": "zerofuku_fusion",
                    "desc": "🌀 [ZEROFUKU FUSION] Absorb Zerofuku's accumulated misfortune and unlock the Great Nirvana Sword Zero. Can only be used once per battle. [TRANSFORMATION: Zerofuku's soul becomes a seven-branched divine blade]"
                }
            elif char.name == "Qin Shi Huang":
                char.armor_form = True
                char.star_eyes_active = False
                char.chi_flow = False
                char.phoenix_active = False
                char.counter_ready = False
                char.counter_timer = 0
            elif char.name == "Leonidas":
                char.shield_form = "base"
            elif char.name == "Soji Okita":
                char.demon_child_active = False
                char.demon_child_release = False
                char.illness_effect = 0
                char.illness_timer = 0
                char.demon_available = True
            elif char.name == "Sakata Kintoki":
                char.rune_of_eirin_active = False
                char.rune_cooldown = 0

            print(f"  ✦ {char.name} recovered!")
        print("\n✨ Champions fully healed!")
        self.save_game()

    def ragnarok_tournament(self):
        self.current_mode = "tournament"

        print("\n" + "=" * 110)
        slow_print("🏆🏆🏆 RAGNAROK TOURNAMENT 🏆🏆🏆", 0.03)
        print("=" * 110)
        slow_print("First to 7 victories decides humanity's fate.", 0.02)
        print("=" * 110)

        rounds = [
            ("ROUND 1: Thor vs Lü Bu", [create_enemy_thor()], [self.lu_bu], "round1_complete"),
            ("ROUND 2: Zeus vs Adam", [create_enemy_zeus()], [self.adam], "round2_complete"),
            ("ROUND 3: Poseidon vs Kojiro Sasaki", [create_enemy_poseidon()], [self.kojiro], "round3_complete"),
            ("ROUND 4: Heracles vs Jack the Ripper", [create_enemy_heracles()], [self.jack], "round4_complete"),
            ("ROUND 5: Shiva vs Raiden Tameemon", [create_enemy_shiva()], [self.raiden], "round5_complete"),
            ("ROUND 6: Buddha vs Hajun", [create_enemy_hajun()], [self.buddha], "round6_complete"),
            ("ROUND 7: Hades vs Qin Shi Huang", [create_enemy_hades()], [self.qin], "round7_complete"),
            ("ROUND 8: Beelzebub vs Nikola Tesla", [create_enemy_beelzebub()], [self.tesla], "round8_complete"),
            ("ROUND 9: Apollo vs Leonidas", [create_enemy_apollo()], [self.leonidas], "round9_complete"),
            ("ROUND 10: Susano'o vs Soji Okita", [create_enemy_susanoo()], [self.okita], "round10_complete"),
            ("ROUND 11: Loki vs Simo Häyhä", [create_enemy_loki()], [self.simo], "round11_complete"),
            ("ROUND 12: Odin vs Sakata Kintoki", [create_enemy_odin()], [self.kintoki], "round12_complete")
        ]

        humanity_wins = self.humanity_score
        gods_wins = self.gods_score

        for round_name, enemies, recommended, progress_key in rounds:
            if self.story_progress.get(progress_key, False):
                print(f"\n✅ {round_name} - COMPLETED")
                self.round_number += 1
                continue

            print("\n" + "🔥" * 110)
            slow_print(f"🔥 {round_name} 🔥", 0.03)
            print("🔥" * 110)
            print(f"Score - Humanity: {humanity_wins} | Gods: {gods_wins}")

            print(f"\nRecommended: {recommended[0].name}")
            party = self.select_party(1, "Humans") or recommended
            champion = party[0]

            if activate_volund_for_character(champion, self):
                print(f"   → Völundr activated for {champion.name}")

            if champion.name == "Adam" and "Zeus" in round_name:
                print("\n" + "👁️" * 55)
                slow_print("ADAM VS ZEUS - THE FATHER VS THE GODFATHER", 0.03)
                slow_print("The Eyes of the Lord vs The Fist That Surpassed Time", 0.03)
                print("👁️" * 55)
                time.sleep(2)

            input("\nPress Enter to begin...")

            if not self.battle(enemies, party):
                print(f"\n💀 {champion.name} defeated!")
                gods_wins += 1
                self.gods_score += 1
                if champion.name in self.canon_pairings:
                    self.mark_valkyrie_fallen(self.canon_pairings[champion.name]["valkyrie_name"])

                if gods_wins >= 7:
                    print("\n💀 HUMANITY HAS FALLEN!")
                    return False
            else:
                print(f"\n✨ {champion.name} victorious!")
                humanity_wins += 1
                self.humanity_score += 1

                if champion.name == "Adam" and "Zeus" in round_name:
                    print("\n" + "👁️" * 55)
                    slow_print("ADAM PROVES THAT A FATHER'S LOVE TRANSCENDS EVEN THE GODS!", 0.04)
                    print("👁️" * 55)

                if progress_key == "round6_complete" and champion.name == "Buddha":
                    print(self.buddha.gain_great_nirvana_sword())
                self.story_progress[progress_key] = True

                if humanity_wins >= 7:
                    print("\n✨ HUMANITY SURVIVES!")
                    return True

            self.save_game()
            self.round_number += 1
            if humanity_wins < 7 and gods_wins < 7:
                self.rest()

        print("\n" + "=" * 110)
        slow_print("🏆 TOURNAMENT COMPLETE 🏆", 0.04)
        print("=" * 110)
        print(f"Final Score - Humanity: {humanity_wins} | Gods: {gods_wins}")

        self.current_mode = "menu"
        return humanity_wins >= 7

    def stats_mode(self):
        print("\n" + "=" * 110)
        slow_print("📊 VALHALLA RECORDS 📊", 0.04)
        print("=" * 110)

        print(f"🏆 Humanity Victories: {self.humanity_score}")
        print(f"💀 Gods' Victories: {self.gods_score}")
        print(f"⚔️ Total Battles: {self.victories}")
        print(f"💢 Enemies Defeated: {self.total_kills}")

        if hasattr(self.adam, 'copy_count'):
            print(f"👁️ Adam's Copied Techniques: {self.adam.copy_count}/{self.adam.max_copy}")
            print(f"🕶️ Adam's Blindness Level: {self.adam.blindness}")
            if self.adam.copied_techniques:
                print(f"📚 Techniques copied: {', '.join(self.adam.copied_techniques[:5])}")
                if len(self.adam.copied_techniques) > 5:
                    print(f"   ... and {len(self.adam.copied_techniques) - 5} more")
        print()

        print("✦ VALKYRIE STATUS:")
        for name, status in self.valkyries_status.items():
            index = Valkyrie.get_index_by_name(name.upper())
            if status == "available":
                partner = self.get_valkyrie_partner(name)
                print(f"  [{index:2d}] ✅ {name} - Available (Partner: {partner})")
            elif status == "fallen":
                partner = self.get_valkyrie_partner(name)
                print(f"  [{index:2d}] ❌ {name} - Fallen (Partner: {partner})")
            elif status in ["organizer", "assistant"]:
                print(f"  [{index:2d}] 👑 {name} - {status.title()}")

        print("\n✦ ROUND PROGRESS:")
        for i in range(1, 13):
            status = "✅" if self.story_progress.get(f"round{i}_complete", False) else "⏳"
            print(f"  {status} Round {i}")

        print("\n📁 HIGH SCORES:")
        if os.path.exists("survival_scores.json"):
            print("  • Survival Mode scores exist")
        if os.path.exists("boss_rush_records.json"):
            print("  • Boss Rush records exist")
        if os.path.exists("gauntlet_records.json"):
            print("  • Gauntlet records exist")

        input("\nPress Enter to continue...")

    def save_game(self):
        jack_weapon_data = None
        if self.jack.volund_active and hasattr(self.jack, 'abilities'):
            jack_weapon_data = {}
            for key, ability in self.jack.abilities.items():
                if "uses_left" in ability:
                    jack_weapon_data[key] = ability["uses_left"]

        character_data = {}
        important_chars = ["thor", "zeus", "poseidon", "heracles", "shiva", "zerofuku",
                           "hajun", "hades", "beelzebub", "apollo", "susanoo", "loki", "odin",
                           "lu_bu", "adam", "kojiro", "jack", "raiden", "buddha", "qin",
                           "tesla", "leonidas", "okita", "simo", "kintoki"]

        for char_name in important_chars:
            if hasattr(self, char_name):
                char = getattr(self, char_name)
                character_data[char_name] = {
                    'hp': char.hp,
                    'energy': char.energy,
                    # NOTE: volund_active and valkyrie_index are NOT saved —
                    # Völundr resets between battles and is activated fresh each match
                }
                if char_name == "adam":
                    character_data[char_name]['blindness'] = char.blindness
                    character_data[char_name]['death_activated'] = char.death_activated
                elif char_name == "thor":
                    character_data[char_name]['teleport_uses'] = char.teleport_uses
                    character_data[char_name]['tournament_teleport_uses'] = char.tournament_teleport_uses
                elif char_name == "zeus":
                    character_data[char_name]['adamas_timer'] = char.adamas_timer
                    character_data[char_name]['neck_fix_available'] = char.neck_fix_available
                elif char_name == "shiva":
                    character_data[char_name]['arms_remaining'] = char.arms_remaining
                    character_data[char_name]['permanent_arm_loss'] = char.permanent_arm_loss
                elif char_name == "simo":
                    character_data[char_name]['organs_used'] = char.organs_used
                elif char_name == "jack":
                    character_data[char_name]['organ_shift_used'] = char.organ_shift_used
                    character_data[char_name]['magic_pouches'] = char.magic_pouches
                elif char_name == "okita":
                    character_data[char_name]['illness_effect'] = char.illness_effect
                    character_data[char_name]['illness_timer'] = char.illness_timer
                elif char_name == "apollo":
                    character_data[char_name]['expectation_bonus'] = char.expectation_bonus
                    character_data[char_name]['next_attack_multiplier'] = char.next_attack_multiplier
                elif char_name == "heracles":
                    character_data[char_name]['tattoo_progress'] = char.tattoo_progress
                elif char_name == "qin":
                    character_data[char_name]['counter_timer'] = char.counter_timer
                elif char_name == "kintoki":
                    character_data[char_name]['rune_cooldown'] = char.rune_cooldown

        game_state = {
            'valkyries_status': self.valkyries_status,
            'story_progress': self.story_progress,
            'victories': self.victories,
            'total_kills': self.total_kills,
            'humanity_score': self.humanity_score,
            'gods_score': self.gods_score,
            'round_number': self.round_number,
            'adam_copy_data': self.adam.to_dict() if hasattr(self, 'adam') else None,
            'jack_weapon_data': jack_weapon_data,
            'character_data': character_data
        }
        if SaveSystem.save_game(game_state):
            print("\n💾 Game saved!")
            return True
        return False

    def load_game(self):
        game_state = SaveSystem.load_game()
        if not game_state:
            return False
        self.valkyries_status = game_state.get('valkyries_status', self.valkyries_status)
        self.story_progress = game_state.get('story_progress', self.story_progress)
        self.victories = game_state.get('victories', 0)
        self.total_kills = game_state.get('total_kills', 0)
        self.humanity_score = game_state.get('humanity_score', 0)
        self.gods_score = game_state.get('gods_score', 0)
        self.round_number = game_state.get('round_number', 1)

        adam_data = game_state.get('adam_copy_data')
        if adam_data and hasattr(self, 'adam'):
            self.adam.from_dict(adam_data)

        jack_weapon_data = game_state.get('jack_weapon_data')
        if jack_weapon_data and self.jack.volund_active:
            for key, uses_left in jack_weapon_data.items():
                if key in self.jack.abilities and "uses_left" in self.jack.abilities[key]:
                    self.jack.abilities[key]["uses_left"] = uses_left

        character_data = game_state.get('character_data', {})
        for char_name, data in character_data.items():
            if hasattr(self, char_name):
                char = getattr(self, char_name)
                char.hp = data.get('hp', char.max_hp)
                char.energy = data.get('energy', char.max_energy)
                # NOTE: volund_active and valkyrie_index are not restored from save —
                # Völundr is always reset and reactivated fresh each battle

                if char_name == "adam":
                    char.blindness = data.get('blindness', char.blindness)
                    char.death_activated = data.get('death_activated', char.death_activated)
                elif char_name == "thor":
                    char.teleport_uses = data.get('teleport_uses', char.teleport_uses)
                    char.tournament_teleport_uses = data.get('tournament_teleport_uses', char.tournament_teleport_uses)
                elif char_name == "zeus":
                    char.adamas_timer = data.get('adamas_timer', char.adamas_timer)
                    char.neck_fix_available = data.get('neck_fix_available', char.neck_fix_available)
                elif char_name == "shiva":
                    char.arms_remaining = data.get('arms_remaining', char.arms_remaining)
                    char.permanent_arm_loss = data.get('permanent_arm_loss', char.permanent_arm_loss)
                elif char_name == "simo":
                    char.organs_used = data.get('organs_used', char.organs_used)
                elif char_name == "jack":
                    char.organ_shift_used = data.get('organ_shift_used', char.organ_shift_used)
                    char.magic_pouches = data.get('magic_pouches', char.magic_pouches)
                elif char_name == "okita":
                    char.illness_effect = data.get('illness_effect', char.illness_effect)
                    char.illness_timer = data.get('illness_timer', char.illness_timer)
                elif char_name == "apollo":
                    char.expectation_bonus = data.get('expectation_bonus', char.expectation_bonus)
                    char.next_attack_multiplier = data.get('next_attack_multiplier', 1.0)
                elif char_name == "heracles":
                    char.tattoo_progress = data.get('tattoo_progress', char.tattoo_progress)
                elif char_name == "qin":
                    char.counter_timer = data.get('counter_timer', 0)
                elif char_name == "kintoki":
                    char.rune_cooldown = data.get('rune_cooldown', 0)

        return True

    def save_load_menu(self):
        while True:
            clear_screen()
            print("\n" + "=" * 110)
            slow_print("💾💾💾 SAVE/LOAD MANAGEMENT 💾💾💾", 0.03)
            print("=" * 110)
            print("  1. 💾 Save Game")
            print("  2. 📂 Load Game")
            print("  3. 🗑️ Delete Save")
            print("  4. 🔙 Back")
            print("-" * 110)

            choice = input("> ").strip()

            if choice == "1":
                self.save_game()
                input("\nPress Enter to continue...")
            elif choice == "2":
                if self.load_game():
                    print("✅ Game loaded successfully!")
                    if self.adam.copy_count > 0:
                        print(f"👁️ Adam has {self.adam.copy_count} copied techniques")
                else:
                    print("❌ No save file found!")
                input("\nPress Enter to continue...")
            elif choice == "3":
                confirm = input("Are you sure you want to delete your save? (y/n): ").lower()
                if confirm == 'y':
                    if SaveSystem.delete_save():
                        print("🗑️ Save file deleted!")
                        self.__init__(load_saved=False)
                    else:
                        print("❌ No save file found!")
                input("\nPress Enter to continue...")
            elif choice == "4":
                return
            else:
                print("❌ Invalid choice.")
                time.sleep(1)

    def main_menu(self):
        while True:
            clear_screen()
            print("\n" + "═" * 110)
            slow_print("    ⚔️⚔️⚔️  RECORD OF RAGNAROK: RAGNAROK'S CALL  ⚔️⚔️⚔️", 0.02)
            print("    25 FIGHTERS (13 Gods + 12 Humans) — 100% CANON ABILITIES")
            print("    310 TOTAL ABILITIES  •  CLEAN EDITION v2.0  •  ALL BUGS FIXED")
            print("    ENHANCED COPY MECHANICS FOR ADAM  •  COMPLETE STATUS INDICATORS")
            print("═" * 110)

            print(f"\n  🏆 Humanity Score: {self.humanity_score}   |   💀 Gods Score: {self.gods_score}   |   ⚔️ Battles: {self.victories}")
            if self.adam.copy_count > 0:
                print(f"  👁️ Adam's Copied Techniques: {self.adam.copy_count}/{self.adam.max_copy}")

            print("\n  🎮 GAME MODES:")
            print("  " + "─" * 106)
            print("  1. 🏆  Ragnarok Tournament  — The canonical 12-round tournament (1v1 per round)")
            print("  2. ♾️   Survival Mode        — Endless waves of enemies, no rest between waves")
            print("  3. 👑  Boss Rush            — Fight all 13 gods back-to-back with a party")
            print("  4. ⚔️   Gauntlet             — 1v25 challenge: can you defeat every fighter?")
            print("  5. 🌀  Chaos Mode           — Randomized matchups, abilities, and modifiers")
            print("  6. 🥋  Training Mode        — Practice freely against any fighter")
            print("  " + "─" * 106)
            print("  7. ⚔️   Valkyrie Management — View and manage Valkyrie statuses")
            print("  8. 📊  Statistics           — View your records and progress")
            print("  9. 💾  Save / Load          — Manage your save file")
            print(" 10. ❌  Exit")
            print("  " + "─" * 106)

            choice = input("> ").strip()

            if choice == "1":
                self.ragnarok_tournament()
            elif choice == "2":
                self.survival.run()
            elif choice == "3":
                self.boss_rush.run()
            elif choice == "4":
                self.gauntlet.run()
            elif choice == "5":
                self.chaos.run()
            elif choice == "6":
                self.training.run()
            elif choice == "7":
                self.valkyrie_management_menu()
            elif choice == "8":
                self.stats_mode()
            elif choice == "9":
                self.save_load_menu()
            elif choice == "10":
                self.exit_game()
            else:
                print("❌ Invalid choice.")
                time.sleep(1)

    def exit_game(self):
        print("\n" + "=" * 110)
        save_choice = input("Save before exiting? (y/n): ").lower()
        if save_choice == 'y':
            self.save_game()

        print("\n" + "=" * 110)
        slow_print("Thank you for playing Record of Ragnarok!", 0.03)
        slow_print("May the Father of Humanity guide your path.", 0.03)
        print("=" * 110)
        sys.exit(0)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    try:
        save_exists = os.path.exists(SAVE_FILE)

        game = RagnarokGame(load_saved=save_exists)

        if save_exists:
            print("\n💾 Save file found! Loading...")
            if game.adam.copy_count > 0:
                print(f"👁️ Adam has {game.adam.copy_count} copied techniques from previous sessions!")
            time.sleep(2)

        game.main_menu()

    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please report this issue.")
        sys.exit(1)


if __name__ == "__main__":
    main()