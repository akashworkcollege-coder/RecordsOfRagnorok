#!/usr/bin/env python3
"""
RECORD OF RAGNAROK: RAGNAROK'S CALL - COMPLETE WIKI ACCURATE EDITION
All 26 Fighters (13 Gods + 13 Humans) including Hajun
100% Canon Abilities - ALL 269 ABILITIES IMPLEMENTED
ENHANCED COPY MECHANICS FOR ADAM - Father of Humanity's Divine Replication
COMPLETE GAME MODES - Tournament, Survival, Boss Rush, Training, Gauntlet, Chaos Mode
DETAILED MOVE DESCRIPTIONS - Every ability explained in full canon detail
FIXED: All missing abilities from text files added
FIXED: All technique variations implemented
FIXED: Transformation descriptions for EVERY ability
"""

import random
import time
import sys
import json
import os
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

TEXT_SPEED = 0.03
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
# VALKYRIE ENUM - WITH INTEGER INDICES AND IMPROVED LOOKUP
# ============================================================================

class Valkyrie(Enum):
    # All 13 Valkyrie Sisters in canon order with indices
    BRUNHILDE = (0, "👑 Brunhilde", "The Eldest - Tournament Organizer", "organizer", False)
    HRIST = (1, "🌪️ Hrist", "The Quaking (Bipolar Personality) - Kojiro's Partner", "available", True)
    THRUD = (2, "💪 Thrud", "The Strong One - Raiden's Partner (Fell in love)", "available", True)
    RANDGRIZ = (3, "🛡️ Randgriz", "Shield Breaker - Lü Bu's Partner", "available", True)
    GEIROLUL = (4, "⚔️ Geirölul", "The One Charging Forth - Leonidas' Partner", "available", True)
    SKALMOLD = (5, "⚡ Skalmöld", "Sword Time - Soji Okita's Partner", "available", True)
    REGINLEIF = (6, "✨ Reginleif", "Daughter of the Gods - Adam's Partner", "available", True)
    RADGRIDR = (7, "🎯 Ráðgríðr", "Plan Breaker - Simo Häyhä's Partner", "available", True)
    GONDUL = (8, "🔮 Göndul", "The Magic Wielder - Tesla's Partner", "available", True)
    ALVITR = (9, "🛡️ Alvitr", "Host-Guard - Qin Shi Huang's Partner", "available", True)
    HLOKK = (10, "🔥 Hlökk", "The Battle Cry - Jack's Partner (Forced Volund)", "available", True)
    SKEGGJOLD = (11, "🪓 Skeggjöld", "Axe Age - Kintoki's Partner (Fuses with axe)", "available", True)
    GOLL = (12, "💫 Göll", "The Youngest - Brunhilde's Assistant", "assistant", False)

    def __init__(self, index, icon_name, desc, default_status, can_fight):
        self.index = index
        self.icon_name = icon_name
        self.desc = desc
        self.default_status = default_status
        self.can_fight = can_fight

    @property
    def display_name(self):
        return f"{self.icon_name} - {self.desc}"

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
            if len(parts) > 1:
                if parts[1] == display_name:
                    return valkyrie
        for valkyrie in cls:
            if valkyrie.name.lower() == display_name.lower():
                return valkyrie
        return None

    @classmethod
    def get_index_by_name(cls, name):
        """Get index by Valkyrie name"""
        valkyrie = cls.get_by_name(name)
        return valkyrie.index if valkyrie else -1


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
# REALM SYSTEM (Divine States)
# ============================================================================

class Realm(Enum):
    NONE = "⚪ Normal State"
    GODLY_SPEED = "🔵 Godly Speed"
    GODLY_STRENGTH = "🔴 Godly Strength"
    GODLY_ENDURANCE = "🟢 Godly Endurance"
    GODLY_TECHNIQUE = "🩷 Godly Technique"
    GODLY_WILL = "🟣 Godly Will"


# ============================================================================
# ENHANCED COPY MECHANICS FOR ADAM
# ============================================================================

class AdamCopyMechanics:
    """Enhanced copy mechanics specifically for Adam - Father of Humanity"""

    @staticmethod
    def calculate_copy_chance(adam, technique_name, target, enemy_rank, is_divine_technique=False):
        """
        Calculate Adam's copy chance based on multiple factors
        """
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
            factors.append("Volund active (+15%)")

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
        """
        Improve a copied technique based on additional viewings
        """
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

        return f"👁️✨ Adam perfects {technique_name}! (Now seen {new_views} times, +{dmg_increase} damage)"

    @staticmethod
    def get_copy_stats(adam):
        """Display Adam's copy statistics"""
        print("\n" + "=" * 110)
        slow_print("👁️👁️👁️ ADAM'S DIVINE REPLICATION STATISTICS 👁️👁️👁️", 0.03)
        print("=" * 110)
        print(f"   • Techniques Copied: {adam.copy_count}/{adam.max_copy}")
        print(f"   • Blindness Level: {adam.blindness}")
        print(f"   • Volund Active: {'✅' if adam.volund_active else '❌'}")
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
                    if chance > 100:
                        chance = 95
                    print(f"      • {technique}: Seen {views}x ({chance}% copy chance)")

        print("=" * 110)


# ============================================================================
# BASE CHARACTER CLASS - UPDATED WITH VALKYRIE INDEX
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

        # Battle status
        self.defending = False
        self.stunned = False
        self.bound = False
        self.exhausted = False

        # Special mode flags
        self.divine_mode = False
        self.divine_timer = 0

        # Character-specific flags
        self.soul_dark = False

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        if self.active_realm == Realm.GODLY_ENDURANCE:
            dmg = int(dmg * 0.5)
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def activate_realm(self, realm):
        if realm not in self.realms:
            return f"{self.name} cannot use {realm.value}!"
        self.active_realm = realm
        self.realm_timer = 5
        return f"\n✨ {realm.value} ACTIVATED!\n"

    def activate_volund(self, valkyrie):
        """Base volund activation - to be overridden"""
        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index if valkyrie else -1
        self.volund_active = True
        return f"\n⚔️ VOLUND: {self.name} x {valkyrie.icon_name}\n"

    def get_damage_multiplier(self):
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

        return mult, buffs

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
# ENHANCED ADAM CLASS WITH FULL COPY MECHANICS
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
                  "desc": "👁️ [EYES OF THE LORD] Adam's eyes can copy any divine technique he witnesses. Success chance increases with each viewing. [TRANSFORMATION: Divine energy flows through Adam's eyes, allowing him to perfectly replicate any technique he sees]"},
            '2': {"name": "👊 Basic Strike", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "👊 [BASIC PUNCH] A basic attack from the Father of Humanity. [TRANSFORMATION: Pure paternal love manifests as raw physical force]"},
            '3': {"name": "👁️ Father's Love", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "effect": "fight_on_death",
                  "desc": "👁️ [FATHER'S SACRIFICE] Even after death, Adam fights on for his children. [TRANSFORMATION: Love transcends mortality itself - Adam's spirit refuses to fade]"},
            '4': {"name": "🐍 The Serpent's Claws", "cost": 40, "dmg": (190, 260), "type": "damage",
                  "desc": "🐍 [SERPENT'S CLAWS] Adam copies the Serpent's attack that once assaulted Eve. His hands grow three times in size with black-green scales and sharp bone claws. [TRANSFORMATION: Adam's biology morphs - hands become draconic claws capable of rending divine flesh]"},
        }

        self.abilities['98'] = {"name": "📊 View Copy Statistics", "cost": 0, "dmg": (0, 0), "type": "utility",
                                "desc": "📊 [COPY ANALYSIS] View detailed statistics about Adam's copied techniques."}

    def activate_volund(self, valkyrie):
        """Adam's Volund activation - Reginleif → Brass Knuckles"""
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
            "desc": "👁️ [ULTIMATE COPY] Adam's ultimate technique - combines all copied techniques into one devastating attack. [TRANSFORMATION: Every technique Adam has ever witnessed flows through him simultaneously]"
        }

        self.abilities['1']["desc"] += " [VOLUND BOOST: Reginleif's power increases copy chance by +15%]"

        print(f"\n⚔️⚔️⚔️ VOLUND: Adam x Reginleif ⚔️⚔️⚔️")
        print(
            f"✅ Adam awakens the {self.volund_weapon}! [TRANSFORMATION: Reginleif's divine power crystallizes into brass knuckles around Adam's fist]")
        print(f"   Copy chance +15%")
        return f"✅ Volund successfully activated for Adam!"

    def apply_effect(self, effect):
        if effect == "fight_on_death" and not self.death_activated:
            self.death_activated = True
            self.hp = 1
            self.divine_mode = True
            self.divine_timer = 3
            return "👁️ [FATHER'S LOVE] Adam fights even AFTER DEATH! The Father of Humanity will not abandon his children! [TRANSFORMATION: Adam's soul burns brighter than ever, defying death itself]"
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
            "desc": f"👁️ [COPIED TECHNIQUE] Adam's replication of {technique_name}. Seen {views} times. [TRANSFORMATION: Through the Eyes of the Lord, Adam perfectly reproduces this divine technique]"
        }

        self.copied_techniques_data[technique_name] = {
            "key": new_key,
            "views": views,
            "damage": (total_min_dmg, total_max_dmg)
        }

        self.blindness += 1
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

    def to_dict(self):
        data = super().to_dict()
        data['copy_count'] = self.copy_count
        data['blindness'] = self.blindness
        data['copied_techniques'] = self.copied_techniques
        data['technique_view_count'] = self.technique_view_count
        data['death_activated'] = self.death_activated
        return data

    def from_dict(self, data):
        super().from_dict(data)
        self.copy_count = data.get('copy_count', 0)
        self.blindness = data.get('blindness', 0)
        self.copied_techniques = data.get('copied_techniques', [])
        self.technique_view_count = data.get('technique_view_count', {})
        self.death_activated = data.get('death_activated', False)


# ============================================================================
# ENEMY CLASS
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
                "divine": abil.get("divine", False)
            }
        self.rank = rank
        self.affiliation = affiliation
        self.round = round_num
        self.ai_pattern = []
        self.soul_dark = soul_dark


# ============================================================================
# VOLUND ACTIVATION FUNCTIONS - CLEANED VERSION
# ============================================================================

def activate_volund_for_character(character, game):
    """
    Activate Volund for a character if they have a Valkyrie partner
    """
    if character.volund_active:
        return False

    if character.name == "Buddha":
        print(f"  Skipping Buddha (no Valkyrie needed)")
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
                result = character.activate_volund(valkyrie)
                print(result)
                character.valkyrie_index = valkyrie.index
                return True
    return False


def activate_volund_for_party(party, game):
    """
    Activate Volund for all eligible characters in a party
    """
    count = 0
    print("\n⚡ Checking for Volund activation...")
    for character in party:
        if activate_volund_for_character(character, game):
            count += 1

    if count == 0:
        print("  ⚠️ No eligible champions for Volund at this time.")
    else:
        print(f"  ✅ Volund activated for {count} champion(s).")
    return count


# ============================================================================
# GOD CHARACTERS - Complete with all abilities and descriptions
# ============================================================================

class Thor(Character):
    def __init__(self):
        super().__init__(
            "Thor",
            "God of Thunder • Norse Pantheon",
            1250, 450,
            [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE]
        )
        self.round = 1
        self.affiliation = "Gods"
        self.járngreipr_active = True
        self.mjolnir_awakened = False
        self.teleport_uses = 3

        self.divine_technique = {
            "name": "⚡ GEIRRÖD THOR'S HAMMER",
            "cost": 180,
            "dmg": (550, 750),
            "type": "damage",
            "desc": "⚡ [ULTIMATE THUNDER] Thor's ultimate technique. By channeling the power of the giant Geirröd through Mjolnir, Thor unleashes a thunderous strike that splits the heavens. [TRANSFORMATION: Mjolnir becomes engulfed in the lightning of a thousand storms]"
        }

        self.abilities = {
            '1': {"name": "⚡ Mjolnir Strike", "cost": 25, "dmg": (150, 210), "type": "damage", "divine": True,
                  "desc": "⚡ [HAMMER STRIKE] A basic strike with the divine hammer Mjolnir. [TRANSFORMATION: Forged by dwarven brothers, Mjolnir channels Thor's divine power into each swing]"},
            '2': {"name": "⚡ Thor's Hammer", "cost": 45, "dmg": (220, 290), "type": "damage", "divine": True,
                  "desc": "⚡ [THROWN HAMMER] Thor winds up Mjolnir and hurls it with tremendous force. [TRANSFORMATION: Mjolnir becomes a projectile of pure thunder, returning to Thor's hand after striking]"},
            '3': {"name": "🧤 Remove Járngreipr", "cost": 30, "dmg": (0, 0), "type": "buff",
                  "effect": "remove_gloves",
                  "desc": "🧤 [GAUNTLET REMOVAL] Thor removes his iron gauntlets Járngreipr. [TRANSFORMATION: Without the gauntlets, Mjolnir's true power awakens, though Thor's grip becomes dangerously hot]"},
            '4': {"name": "⚡ Awakened Mjolnir", "cost": 70, "dmg": (320, 400), "type": "damage", "divine": True,
                  "desc": "⚡ [AWAKENED HAMMER] Thor awakens Mjolnir's true power. [TRANSFORMATION: The hammer crackles with divine lightning, veins of power pulsing across its surface]"},
            '5': {"name": "⚡ Geirröd's Power", "cost": 100, "dmg": (450, 550), "type": "damage", "divine": True,
                  "blockable": False,
                  "desc": "⚡ [GIANT'S POWER] Thor channels the power of the giant Geirröd. [TRANSFORMATION: Lightning becomes unblockable - it WILL find its mark]"},
            '6': {"name": "⚡ Teleport", "cost": 40, "dmg": (0, 0), "type": "utility", "effect": "teleport",
                  "desc": "⚡ [LIGHTNING TELEPORT] Thor teleports using Mjolnir's connection to lightning. 3 uses per battle. [TRANSFORMATION: Thor becomes one with lightning, instantaneously repositioning]"},
            '7': {"name": "👁️ Menacing Aura", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "👁️ [GODLY PRESENCE] Thor's mere presence radiates divine intimidation. [TRANSFORMATION: The air crackles with electricity, making lesser beings tremble]"}
        }

    def apply_effect(self, effect):
        if effect == "remove_gloves":
            self.járngreipr_active = False
            self.take_damage(20)
            return "🧤 [GAUNTLET REMOVAL] Thor removes iron gloves! [TRANSFORMATION: Mjolnir's power increases but the heat deals 20 damage to Thor]"
        elif effect == "teleport":
            if self.teleport_uses > 0:
                self.teleport_uses -= 1
                self.defending = True
                return f"⚡ [LIGHTNING TELEPORT] Thor teleports! {self.teleport_uses} uses remaining. [TRANSFORMATION: Thor dissolves into lightning and reforms elsewhere]"
            return "❌ No teleport uses remaining!"
        return ""


class Zeus(Character):
    def __init__(self):
        super().__init__(
            "Zeus",
            "Godfather of the Cosmos • Greek Pantheon",
            1300, 500,
            [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE]
        )
        self.round = 2
        self.affiliation = "Gods"
        self.form = "Normal"
        self.adamas_timer = 0
        self.neck_fix_available = True
        self.meteor_jab_count = 0

        self.divine_technique = {
            "name": "👊 FIST THAT TRANSCENDS TIME",
            "cost": 200,
            "dmg": (600, 800),
            "type": "damage",
            "desc": "👊 [TIME SURPASSING FIST] Zeus's ultimate technique. A punch so impossibly fast that it transcends time itself. [TRANSFORMATION: The fist moves before the concept of 'before' exists - by the time you see it, you've already been hit]"
        }

        self.abilities = {
            '1': {"name": "👊 Divine Punch", "cost": 25, "dmg": (160, 220), "type": "damage", "divine": True,
                  "desc": "👊 [DIVINE STRIKE] A basic punch from the Godfather of the Cosmos. [TRANSFORMATION: Divine authority crystallizes into raw force with each strike]"},
            '2': {"name": "⚡ Meteor Jab", "cost": 35, "dmg": (190, 260), "type": "damage", "effect": "meteor_jab",
                  "divine": True,
                  "desc": "⚡ [METEOR JAB] Zeus's signature meteor jabs. Each successive jab deals increased damage. [TRANSFORMATION: Speed multiplies exponentially - first jab is fast, tenth moves at light speed]"},
            '3': {"name": "🦵 Divine Axe Kick", "cost": 40, "dmg": (220, 300), "type": "damage", "divine": True,
                  "desc": "🦵 [AXE KICK] Zeus brings his leg down like a divine axe. [TRANSFORMATION: The leg becomes a weapon that can split mountains]"},
            '4': {"name": "👣 Zeus' Footwork", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "footwork",
                  "desc": "👣 [AFTERIMAGE STEP] Zeus employs his strange, unpredictable footwork. 40% evasion next turn. [TRANSFORMATION: Afterimages confuse opponents, making Zeus appear to be everywhere at once]"},
            '5': {"name": "💪 True God's Form (Muscle)", "cost": 50, "dmg": (0, 0), "type": "buff",
                  "effect": "muscle_form",
                  "desc": "💪 [MUSCLE FORM] Zeus transforms into his muscle form for 3 turns. [TRANSFORMATION: His body bulges with divine power, muscles swelling to impossible proportions]"},
            '6': {"name": "👑 Adamas Form", "cost": 100, "dmg": (0, 0), "type": "buff", "effect": "adamas_form",
                  "desc": "👑 [ADAMAS FORM] Zeus assumes his ultimate Adamas form. 70% damage reduction for 5 turns. [TRANSFORMATION: His body hardens to diamond-like density, becoming virtually indestructible]"},
            '7': {"name": "👊 True God's Right", "cost": 60, "dmg": (300, 370), "type": "damage", "divine": True,
                  "desc": "👊 [DIVINE RIGHT CROSS] Zeus's divine right cross. [TRANSFORMATION: The authority of the King of Olympus manifests in this strike]"},
            '8': {"name": "👊 Time Transcending Fist", "cost": 150, "dmg": (500, 650), "type": "damage", "divine": True,
                  "desc": "👊 [TIME STOP PUNCH] A prelude to Zeus's ultimate technique. [TRANSFORMATION: Time seems to stop as the fist travels]"},
            '9': {"name": "🩸 Fix Broken Neck", "cost": 0, "dmg": (0, 0), "type": "heal", "effect": "fix_neck",
                  "desc": "🩸 [NECK FIX] Zeus forcibly realigns his vertebrae. Heals 150 HP. Once per battle. [TRANSFORMATION: Even with a broken neck, Zeus's vitality allows him to continue fighting]"},
            '10': {"name": "👊 The Fist That Surpassed Time", "cost": 200, "dmg": (650, 850), "type": "damage", "divine": True,
                  "desc": "👊 [KRONOS' FINAL STRIKE] Kronos' final strike which Zeus burnt into his body. A punch so fast that time itself seems to halt. [TRANSFORMATION: Time becomes frozen - the fist moves before the concept of 'before' exists]"}
        }

    def apply_effect(self, effect):
        if effect == "meteor_jab":
            self.meteor_jab_count += 1
            return f"⚡ [METEOR JAB] Meteor Jab at {10 ** self.meteor_jab_count}x speed! [TRANSFORMATION: Speed increases exponentially]"
        elif effect == "footwork":
            return "👣 [AFTERIMAGE STEP] Strange footwork with afterimages! 40% evasion next turn."
        elif effect == "muscle_form":
            self.form = "Muscle"
            self.divine_mode = True
            self.divine_timer = 3
            return "💪 [MUSCLE FORM] ZEUS TRANSFORMS! His muscles bulge with divine power! [TRANSFORMATION: Zeus's body swells with godly muscle mass]"
        elif effect == "adamas_form":
            self.form = "Adamas"
            self.divine_mode = True
            self.divine_timer = 5
            self.adamas_timer = 5
            return "👑 [ADAMAS FORM] ADAMAS FORM! Virtually indestructible! But this form destroys his body... [TRANSFORMATION: Zeus's body compresses to diamond-like density, muscles turning inside out]"
        elif effect == "fix_neck":
            if self.neck_fix_available:
                self.neck_fix_available = False
                self.heal(150)
                return "🩸 [NECK FIX] Zeus fixes his own broken neck! Heals 150 HP. [TRANSFORMATION: Zeus forcibly realigns his vertebrae with his bare hands]"
            return "❌ Neck fix already used!"
        return ""

    def take_damage(self, dmg):
        if self.form == "Adamas":
            dmg = int(dmg * 0.3)
        super().take_damage(dmg)


class Poseidon(Character):
    def __init__(self):
        super().__init__(
            "Poseidon",
            "God of the Seas • Greek Pantheon",
            1200, 460,
            [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE]
        )
        self.round = 3
        self.affiliation = "Gods"
        self.used_moves = []
        self.water_level = 100

        self.divine_technique = {
            "name": "🌊 40 DAYS AND 40 NIGHTS OF FLOOD",
            "cost": 180,
            "dmg": (550, 750),
            "type": "damage",
            "desc": "🌊 [FORTY DAY FLOOD] Poseidon's ultimate technique. A relentless assault of 40 consecutive trident thrusts. [TRANSFORMATION: Like the great flood that drowned the world, this technique is inescapable and overwhelming]"
        }

        self.abilities = {
            '1': {"name": "🌊 Trident Thrust", "cost": 25, "dmg": (160, 220), "type": "damage", "divine": True,
                  "desc": "🌊 [BASIC THRUST] A basic thrust of Poseidon's divine trident. [TRANSFORMATION: Sea foam crystallizes into the divine trident with each thrust]"},
            '2': {"name": "🌊 Divine Speed", "cost": 30, "dmg": (190, 250), "type": "damage", "divine": True,
                  "desc": "🌊 [DIVINE SPEED] Poseidon attacks with the speed of a raging sea. [TRANSFORMATION: The trident becomes a blur, striking faster than the eye can follow]"},
            '3': {"name": "🌊 Amphitrite", "cost": 40, "dmg": (220, 290), "type": "damage", "divine": True,
                  "desc": "🌊 [AMPHITRITE] Named after Poseidon's queen, this thrust flows like water around defenses. [TRANSFORMATION: The trident becomes fluid, finding gaps where none should exist]"},
            '4': {"name": "🌊 Chione Tyro Demeter", "cost": 55, "dmg": (270, 340), "type": "damage", "divine": True,
                  "desc": "🌊 [TRIPLE GODDESS] A threefold thrust combining the powers of snow, fertility, and the harvest. [TRANSFORMATION: Three divine aspects merge into one devastating strike]"},
            '5': {"name": "🌊 Medusa Alope Demeter", "cost": 75, "dmg": (350, 430), "type": "damage", "divine": True,
                  "desc": "🌊 [GORGON FLOOD] A devastating combination that turns opponents to stone and drowns them. [TRANSFORMATION: The trident strikes with the petrifying power of Medusa and the drowning force of the sea]"},
            '6': {"name": "🌊 Hydrokinesis", "cost": 35, "dmg": (0, 0), "type": "utility", "effect": "hydrokinesis",
                  "desc": "🌊 [WATER BARRIER] Poseidon manipulates water to create defensive barriers. [TRANSFORMATION: Water rises from the ground, forming a protective wall]"},
            '7': {"name": "✨ Materialize Trident", "cost": 15, "dmg": (0, 0), "type": "buff", "effect": "materialize",
                  "desc": "✨ [TRIDENT MATERIALIZATION] Poseidon materializes his divine trident from sea foam, +20 energy. [TRANSFORMATION: Sea foam crystallizes into the divine trident]"},
            '8': {"name": "👑 Pride of the Seas", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "👑 [DIVINE PRIDE] Poseidon's divine pride makes him refuse to acknowledge any opponent as worthy. [PASSIVE: This arrogance is both his greatest strength and weakness]"}
        }

    def apply_effect(self, effect):
        if effect == "hydrokinesis":
            if self.water_level >= 10:
                self.water_level -= 10
                self.defending = True
                return f"🌊 [WATER BARRIER] Water barrier created. Water level: {self.water_level}% [TRANSFORMATION: Ocean water forms a protective barrier around Poseidon]"
            return "❌ Water level too low!"
        elif effect == "materialize":
            self.energy = min(self.max_energy, self.energy + 20)
            return "✨ [TRIDENT MATERIALIZATION] Poseidon materializes his trident! +20 energy. [TRANSFORMATION: Sea foam condenses into the divine trident]"
        return ""


class Heracles(Character):
    def __init__(self):
        super().__init__(
            "Heracles",
            "God of Fortitude • Greek Pantheon",
            1350, 430,
            [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE]
        )
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
            "desc": "🦁 [CERBERUS FUSION] Heracles fuses with Cerberus, the three-headed hound of Hades. [TRANSFORMATION: Heracles gains claws, fangs, and demonic power, becoming a beast that rivals the monsters he once defeated]"
        }

        self.abilities = {
            '1': {"name": "🦁 1st Labor: Nemean Lion", "cost": 30, "dmg": (170, 230), "type": "damage", "labor": 1,
                  "desc": "🦁 [NEMEAN LION] Heracles uses the pelt of the Nemean Lion. [TRANSFORMATION: The lion's invulnerable hide manifests around Heracles' strike]"},
            '2': {"name": "🐍 2nd Labor: Lernaean Hydra", "cost": 35, "dmg": (190, 250), "type": "damage", "labor": 2,
                  "desc": "🐍 [HYDRA STRIKE] Heracles channels the Hydra's regenerative power. [TRANSFORMATION: Each strike seems to multiply, like the heads of the Hydra]"},
            '3': {"name": "🦌 3rd Labor: Ceryneian Hind", "cost": 30, "dmg": (180, 240), "type": "damage", "labor": 3,
                  "desc": "🦌 [GOLDEN HIND] Heracles moves with the speed of the golden-horned hind. [TRANSFORMATION: Swift and precise as the sacred animal of Artemis]"},
            '4': {"name": "🐗 4th Labor: Erymanthian Boar", "cost": 40, "dmg": (210, 280), "type": "damage", "labor": 4,
                  "desc": "🐗 [BOAR CHARGE] Heracles charges with the unstoppable force of the Erymanthian Boar. [TRANSFORMATION: Trampling everything in his path]"},
            '5': {"name": "💧 5th Labor: Augean Stables", "cost": 35, "dmg": (200, 260), "type": "damage", "labor": 5,
                  "desc": "💧 [RIVER STRIKE] Heracles diverts rivers of power into his attacks. [TRANSFORMATION: Overwhelming opponents with sheer volume]"},
            '6': {"name": "🐦 6th Labor: Stymphalian Birds", "cost": 40, "dmg": (220, 290), "type": "damage", "labor": 6,
                  "desc": "🐦 [BRONZE BIRDS] Heracles launches rapid strikes like the bronze-feathered birds. [TRANSFORMATION: Each strike sharp as a blade]"},
            '7': {"name": "🐂 7th Labor: Cretan Bull", "cost": 45, "dmg": (240, 310), "type": "damage", "labor": 7,
                  "desc": "🐂 [CRETAN BULL] Heracles wrestles with the power of the Cretan Bull. [TRANSFORMATION: Using the bull's own strength against it]"},
            '8': {"name": "🐴 8th Labor: Mares of Diomedes", "cost": 35, "dmg": (210, 270), "type": "damage", "labor": 8,
                  "desc": "🐴 [MAN-EATING MARES] Heracles unleashes the man-eating fury of Diomedes' mares. [TRANSFORMATION: Savage and relentless]"},
            '9': {"name": "👑 9th Labor: Hippolyta's Belt", "cost": 40, "dmg": (230, 300), "type": "damage", "labor": 9,
                  "desc": "👑 [AMAZON BELT] Heracles strikes with the authority of the Amazon queen. [TRANSFORMATION: Precise and deadly]"},
            '10': {"name": "🐮 10th Labor: Geryon's Cattle", "cost": 45, "dmg": (250, 320), "type": "damage",
                   "labor": 10,
                   "desc": "🐮 [THREE-BODIED GIANT] Heracles drives forward like the cattle of the three-bodied giant. [TRANSFORMATION: Multiple impacts overwhelm the opponent]"},
            '11': {"name": "🍎 11th Labor: Apples of Hesperides", "cost": 50, "dmg": (0, 0), "type": "heal", "labor": 11,
                   "desc": "🍎 [GOLDEN APPLES] Heracles reaches for the golden apples of immortality. [TRANSFORMATION: Divine essence restores health]"},
            '12': {"name": "🐕 12th Labor: Cerberus", "cost": 100, "dmg": (400, 500), "type": "damage", "labor": 12,
                   "effect": "cerberus",
                   "desc": "🐕 [CERBERUS SUBJUGATION] Heracles subdues Cerberus, the three-headed hound of Hades. [TRANSFORMATION: This ultimate labor allows him to tap into the beast's power]"},
            '13': {"name": "🐾 Claw of Heracles", "cost": 60, "dmg": (320, 410), "type": "damage", "cerberus_only": True,
                   "desc": "🐾 [CERBERUS CLAW] Only available in Cerberus form. Heracles slashes with claws that rend souls. [TRANSFORMATION: Cerberus' power manifests as invisible claws - each attack creates giant cuts in synchrony with Heracles' movements. The air itself is torn by demonic energy]"}
        }

    def apply_effect(self, effect):
        if effect == "cerberus":
            self.cerberus_active = True
            self.divine_mode = True
            self.divine_timer = 5
            return "🐕 [CERBERUS FUSION] HERACLES FUSES WITH CERBERUS! [TRANSFORMATION: Gains claws, fangs, and demonic power! His tattoo glows crimson]"
        return ""

    def use_labor(self, labor_num):
        self.labors_used += 1
        self.tattoo_progress += 8
        damage_taken = 10 + (self.tattoo_progress // 2)
        self.take_damage(damage_taken)
        if self.tattoo_progress >= 100:
            self.hp = 0
            return "💀 [TATTOO COMPLETE] The tattoo covers Heracles' entire body. He falls. [TRANSFORMATION: The divine tattoo finally consumes him entirely]"
        return f"🩸 [TATTOO SPREAD] Tattoo spreads! Heracles takes {damage_taken} damage. Tattoo: {self.tattoo_progress}% [TRANSFORMATION: The labors scar his body, each one bringing him closer to death]"


class Shiva(Character):
    def __init__(self):
        super().__init__(
            "Shiva",
            "God of Destruction • Hindu Pantheon",
            1280, 450,
            [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE]
        )
        self.round = 5
        self.affiliation = "Gods"
        self.arms_remaining = 4
        self.tandava_level = 0
        self.tandava_karma_active = False

        self.divine_technique = {
            "name": "🔥 DEVA LOKA",
            "cost": 190,
            "dmg": (580, 750),
            "type": "damage",
            "desc": "🔥 [DEVA LOKA] Shiva's ultimate spinning heel kick performed in Tandava Karma state. [TRANSFORMATION: With his heart accelerated to divine speeds, he becomes a whirlwind of destruction]"
        }

        self.abilities = {
            '1': {"name": "🔥 Four Arms Strike", "cost": 30, "dmg": (180, 240), "type": "damage", "multi": 4,
                  "desc": "🔥 [FOUR ARMS] Shiva attacks with all four arms simultaneously. [TRANSFORMATION: A barrage of blows from multiple angles]"},
            '2': {"name": "💃 Tandava Dance", "cost": 50, "dmg": (240, 320), "type": "damage", "effect": "tandava",
                  "desc": "💃 [TANDAVA DANCE] Shiva begins his cosmic dance of destruction. [TRANSFORMATION: Each movement flows into the next, building power and momentum]"},
            '3': {"name": "🔥 Krittivasa", "cost": 45, "dmg": (230, 300), "type": "damage",
                  "desc": "🔥 [KRITTIVASA] Named after Shiva's form 'clad in skin,' this technique strips away defenses. [TRANSFORMATION: Devastating palm strikes that bypass protection]"},
            '4': {"name": "💓 Tandava Karma", "cost": 100, "dmg": (0, 0), "type": "buff", "effect": "karma",
                  "desc": "💓 [TANDAVA KARMA] Shiva accelerates his heartbeat to divine speeds. [TRANSFORMATION: Massive power boost for 5 turns, but the strain on his body is immense. Blue flames consume his body]"},
            '5': {"name": "🕉️ Deva Loka", "cost": 70, "dmg": (350, 450), "type": "damage", "karma_only": True,
                  "desc": "🕉️ [DEVA LOKA KICK] Shiva's spinning heel kick, delivered from the realm of the gods. [TRANSFORMATION: Each rotation generates enough force to shatter divine weapons]"},
            '6': {"name": "🔄 Unpredictable Rhythm", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "🔄 [COSMIC RHYTHM] Shiva's dance follows no predictable pattern. [PASSIVE: His movements seem chaotic but follow the divine rhythm of destruction itself]"}
        }

    def apply_effect(self, effect):
        if effect == "tandava":
            self.tandava_level = 1
            return "💃 [TANDAVA DANCE] SHIVA BEGINS THE TANDAVA! [TRANSFORMATION: Power increases each turn as his dance grows more intense]"
        elif effect == "karma":
            self.tandava_karma_active = True
            self.divine_mode = True
            self.divine_timer = 5
            return "💓 [TANDAVA KARMA] SHIVA'S HEART ACCELERATES! [TRANSFORMATION: Blue flames consume his body - massive power boost but he slowly burns]"
        return ""

    def take_damage(self, dmg):
        super().take_damage(dmg)
        if self.arms_remaining > 1 and random.random() < 0.1 and dmg > 50:
            self.arms_remaining -= 1
            return f"🔥 [ARM LOST] Shiva loses an arm! {self.arms_remaining} arms remaining. [TRANSFORMATION: The divine tattoo fades from one of his arms]"
        return None


class Zerofuku(Character):
    def __init__(self):
        super().__init__(
            "Zerofuku",
            "God of Misfortune • Seven Lucky Gods",
            1150, 410,
            [Realm.GODLY_STRENGTH]
        )
        self.round = 6
        self.affiliation = "Gods"
        self.misery_level = 0
        self.cleaver_heads = 1

        self.divine_technique = {
            "name": "🎋 MISERY CLEAVER - STORM FORM",
            "cost": 170,
            "dmg": (500, 650),
            "type": "damage",
            "desc": "🎋 [MISERY STORM] Zerofuku transforms his Misery Cleaver into a storm of countless black blades. [TRANSFORMATION: The accumulated misfortune of all humanity manifests as an inescapable rain of destruction]"
        }

        self.abilities = {
            '1': {"name": "🎋 Misery Cleaver", "cost": 25, "dmg": (150, 210), "type": "damage",
                  "desc": "🎋 [MISERY CLEAVER] Zerofuku's divine weapon, formed from accumulated misfortune. [TRANSFORMATION: Misfortune crystallizes into a physical blade]"},
            '2': {"name": "😢 Absorb Misfortune", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "absorb",
                  "desc": "😢 [MISFORTUNE ABSORPTION] Zerofuku absorbs misfortune, increasing the power of his cleaver. [TRANSFORMATION: Negative energy flows into the blade, making it grow]"},
            '3': {"name": "🎋 Six-Headed Form", "cost": 60, "dmg": (300, 380), "type": "damage",
                  "desc": "🎋 [SIX HEADS] The Misery Cleaver splits into six separate blades. [TRANSFORMATION: Each head seeks out different parts of the opponent's body]"},
            '4': {"name": "⚔️ Sword Transformation", "cost": 50, "dmg": (240, 330), "type": "damage",
                  "desc": "⚔️ [WEAPON SHIFT] Zerofuku reshapes his cleaver into different weapon forms. [TRANSFORMATION: The blade adapts to the flow of battle]"},
            '5': {"name": "🌪️ Storm Form", "cost": 100, "dmg": (400, 500), "type": "damage",
                  "desc": "🌪️ [STORM FORM] The Misery Cleaver transforms into a whirlwind of blades. [TRANSFORMATION: Attacks from all directions at once]"},
            '6': {"name": "🎋 Seven Lucky Gods Union", "cost": 120, "dmg": (470, 590), "type": "damage",
                  "desc": "🎋 [SEVEN GODS UNION] Zerofuku channels the power of all Seven Lucky Gods. [TRANSFORMATION: Each deity adds their unique blessing to his attack]"}
        }

    def apply_effect(self, effect):
        if effect == "absorb":
            self.misery_level += 1
            self.cleaver_heads = min(7, 1 + self.misery_level)
            return f"😢 [MISFORTUNE ABSORPTION] Misfortune absorbed! Cleaver now has {self.cleaver_heads} heads. [TRANSFORMATION: The blade grows more monstrous with each absorption]"
        return ""


class Hades(Character):
    def __init__(self):
        super().__init__(
            "Hades",
            "God of the Underworld • Greek Pantheon",
            1400, 460,
            [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE]
        )
        self.round = 7
        self.affiliation = "Gods"
        self.ichor_active = False
        self.desmos_active = False

        self.divine_technique = {
            "name": "💀 ICHOR DESMOS",
            "cost": 200,
            "dmg": (600, 780),
            "type": "damage",
            "desc": "💀 [ICHOR DESMOS] Hades's ultimate technique. He infuses his bident with his own divine blood (ichor). [TRANSFORMATION: The bident becomes a LIVING SPEAR, moving with a will of its own]"
        }

        self.abilities = {
            '1': {"name": "💀 Bident Thrust", "cost": 25, "dmg": (170, 230), "type": "damage",
                  "desc": "💀 [BIDENT THRUST] A basic thrust of Hades's divine bident. [TRANSFORMATION: Clean, dignified, and utterly lethal]"},
            '2': {"name": "💀 Persephone-Kallichoron", "cost": 45, "dmg": (240, 320), "type": "damage",
                  "desc": "💀 [PERSEPHONE'S WELL] Named after the sacred well of Persephone. [TRANSFORMATION: Flows like water, finding cracks in any defense]"},
            '3': {"name": "💀 Persephone-Lore", "cost": 55, "dmg": (290, 370), "type": "damage",
                  "desc": "💀 [PERSEPHONE'S WISDOM] A thrust that carries the weight of Persephone's wisdom. [TRANSFORMATION: Strikes at the exact moment an opponent's guard drops]"},
            '4': {"name": "💀 Persephone-Titan", "cost": 60, "dmg": (330, 410), "type": "damage",
                  "desc": "💀 [TITAN POWER] Hades channels the power of the Titans through his bident. [TRANSFORMATION: An earth-shattering thrust]"},
            '5': {"name": "🦵 Cornucopia", "cost": 40, "dmg": (230, 310), "type": "damage",
                  "desc": "🦵 [CORNUCOPIA] A sweeping kick that embodies the abundance of the underworld. [TRANSFORMATION: A kick that carries the weight of countless souls]"},
            '6': {"name": "💧 Ichor Activation", "cost": 40, "dmg": (0, 0), "type": "buff", "effect": "ichor",
                  "desc": "💧 [ICHOR ACTIVATION] Hades activates the ichor flowing through his veins. [TRANSFORMATION: Divine blood begins to flow, enhancing attacks but draining life]"},
            '7': {"name": "💀 Ichor-Eos", "cost": 80, "dmg": (400, 500), "type": "damage", "ichor_only": True,
                  "desc": "💀 [ICHOR DAWN] The dawn of destruction - Hades's bident glows with divine blood. [TRANSFORMATION: The bident pulses with living crimson energy]"},
            '8': {"name": "⚔️ Ichor Desmos", "cost": 120, "dmg": (0, 0), "type": "buff", "effect": "desmos",
                  "desc": "⚔️ [ICHOR DESMOS FORM] Hades's ultimate form - his bident becomes a living spear. +100% damage but drains 25 HP per turn. [TRANSFORMATION: The bident writhes with life, becoming an extension of Hades' very soul]"}
        }

    def apply_effect(self, effect):
        if effect == "ichor":
            self.ichor_active = True
            return "💧 [ICHOR ACTIVATION] HADES ACTIVATES ICHOR! [TRANSFORMATION: His divine blood enhances his attacks but DRAINS HIS LIFE! Crimson energy flows through his veins]"
        elif effect == "desmos":
            self.desmos_active = True
            self.divine_mode = True
            self.divine_timer = 5
            return "⚔️ [ICHOR DESMOS] ICHOR DESMOS ACTIVATED! Living spear form! [TRANSFORMATION: The bident becomes a writhing, living extension of Hades himself! +100% damage but drains 25 HP per turn]"
        return ""


class Beelzebub(Character):
    def __init__(self):
        super().__init__(
            "Beelzebub",
            "Lord of the Flies",
            1250, 450,
            [Realm.GODLY_TECHNIQUE]
        )
        self.round = 8
        self.affiliation = "Gods"
        self.chaos_used = False
        self.lilith_mark = True
        self.lilith_mark_used = False

        self.divine_technique = {
            "name": "🦟 ORIGINAL SIN: CHAOS",
            "cost": 250,
            "dmg": (700, 900),
            "type": "damage",
            "desc": "🦟 [ORIGINAL SIN] Beelzebub's forbidden technique. He creates a black sphere of absolute annihilation. [TRANSFORMATION: The Staff of Apomyius consumes itself, creating a void that erases everything it touches]"
        }

        self.abilities = {
            '1': {"name": "🦟 Palmyra", "cost": 30, "dmg": (180, 240), "type": "damage",
                  "desc": "🦟 [PALMYRA] Beelzebub summons a swarm of divine flies. [TRANSFORMATION: His right hand vibrates at high frequency, summoning flies from the void]"},
            '2': {"name": "🛡️ Sorath Samekh", "cost": 25, "dmg": (0, 0), "type": "defense",
                  "desc": "🛡️ [SORATH SAMEKH] A defensive glyph that creates barriers of pure darkness. [TRANSFORMATION: Left hand resonances create an impenetrable dark barrier]"},
            '3': {"name": "🦟 Sorath Vav", "cost": 55, "dmg": (280, 350), "type": "damage",
                  "desc": "🦟 [SORATH VAV] The sixth glyph of power - Beelzebub manifests hooks of darkness. [TRANSFORMATION: Right hand resonances condense into hooks that tear at the soul]"},
            '4': {"name": "🦟 Sorath Tau", "cost": 70, "dmg": (350, 430), "type": "damage",
                  "desc": "🦟 [SORATH TAU] The final glyph - a cross of pure darkness. [TRANSFORMATION: Dark energy crucifies opponents with shadows]"},
            '5': {"name": "🦟 Sorath Resh", "cost": 85, "dmg": (430, 530), "type": "damage",
                  "desc": "🦟 [SORATH RESH] The head glyph - Beelzebub creates a massive sphere of compressed darkness. [TRANSFORMATION: A sphere of pure annihilation forms in his palm]"},
            '6': {"name": "💀 Lilith's Mark", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "💀 [LILITH'S MARK] The mark of Lilith allows Beelzebub to cheat death once per battle. [TRANSFORMATION: The rose tattoo on his chest glows, refusing to let him die]"},
            '7': {"name": "🦟 CHAOS", "cost": 150, "dmg": (550, 700), "type": "damage", "taboo": True,
                  "effect": "chaos",
                  "desc": "🦟 [CHAOS] A forbidden technique that creates a sphere of annihilation. [TRANSFORMATION: Both hands resonate together, creating a black hole that consumes all]"}
        }

    def apply_effect(self, effect):
        if effect == "chaos":
            self.chaos_used = True
            self.exhausted = True
            return "🦟 [CHAOS] CHAOS UNLEASHED! A black sphere of annihilation forms! [TRANSFORMATION: The Staff of Apomyius is consumed, creating a void that erases reality]"
        return ""

    def check_lilith_mark(self):
        if self.hp <= 0 and self.lilith_mark and not self.lilith_mark_used:
            self.lilith_mark_used = True
            self.hp = 1
            return "🌹 [LILITH'S MARK] LILITH'S MARK ACTIVATES! Beelzebub cheats death! [TRANSFORMATION: The rose tattoo blooms, vines reaching out to pull him back from the abyss]"
        return None


class Apollo(Character):
    def __init__(self):
        super().__init__(
            "Apollo",
            "God of the Sun • Greek Pantheon",
            1180, 440,
            [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE]
        )
        self.round = 9
        self.affiliation = "Gods"
        self.expectation_bonus = 0

        self.divine_technique = {
            "name": "🎯 ARGYROTOXOS",
            "cost": 190,
            "dmg": (600, 780),
            "type": "damage",
            "desc": "🎯 [ARGYROTOXOS] Apollo's ultimate technique. He launches himself like a silver arrow. [TRANSFORMATION: Apollo's entire body becomes the arrow, covered in blinding light]"
        }

        self.abilities = {
            '1': {"name": "🎯 Silver Bow Shot", "cost": 25, "dmg": (160, 220), "type": "damage",
                  "desc": "🎯 [SILVER ARROW] Apollo fires an arrow of pure light from his silver bow. [TRANSFORMATION: Light condenses into a physical arrow, moving faster than sound]"},
            '2': {"name": "🧵 Threads of Light", "cost": 30, "dmg": (0, 0), "type": "buff",
                  "desc": "🧵 [LIGHT THREADS] Apollo weaves threads of sunlight into invisible snares. [TRANSFORMATION: Sunbeams become physical threads, weaving traps]"},
            '3': {"name": "🎸 Phoebus' Lyre", "cost": 35, "dmg": (0, 0), "type": "buff",
                  "desc": "🎸 [PHOEBUS LYRE] Apollo plays his divine lyre, creating melodies that inspire him. [TRANSFORMATION: Threads of light form a lyre, music empowering Apollo]"},
            '4': {"name": "🎯 Artemis Elenchos", "cost": 40, "dmg": (190, 250), "type": "damage", "bind": True,
                  "desc": "🎯 [SHINING DOMINATION] Apollo wraps his threads around the opponent's limb to immobilize them. [TRANSFORMATION: Threads of light become unbreakable chains, binding the target's movements. The target cannot move next turn!]"},
            '5': {"name": "☀️ Embrace of Eternal Midnight Sun", "cost": 60, "dmg": (0, 0), "type": "buff",
                  "effect": "expectations",
                  "desc": "☀️ [ETERNAL SUN] Apollo basks in the expectations of his fans. Damage +5% each use. [TRANSFORMATION: Light radiates from Apollo, growing brighter with each expectation]"},
            '6': {"name": "🎯 Apollo Epicurious", "cost": 55, "dmg": (270, 340), "type": "damage",
                  "desc": "🎯 [EPICUREAN SHOT] A luxurious attack that flows like fine wine. [TRANSFORMATION: A volley of golden arrows, each one a work of art]"},
            '7': {"name": "🌙 Moonlight of Artemis", "cost": 80, "dmg": (0, 0), "type": "buff", "effect": "moonlight",
                  "desc": "🌙 [ARTEMIS MOON] Apollo channels the power of his sister Artemis. Next attack double damage. [TRANSFORMATION: A giant statue of Artemis rises, moonlight bathing the battlefield]"},
            '8': {"name": "🛡️ Thread Shield", "cost": 30, "dmg": (0, 0), "type": "defense", "effect": "shield",
                  "desc": "🛡️ [THREAD SHIELD] Apollo weaves threads of light into a defensive barrier. [TRANSFORMATION: Light threads weave into an impenetrable shield]"},
            '9': {"name": "🎯 Argyrotoxos", "cost": 100, "dmg": (470, 600), "type": "damage",
                  "desc": "🎯 [SILVER BOW] Apollo transforms into a living arrow of silver light. [TRANSFORMATION: Apollo himself becomes the arrow, launching at the speed of light]"}
        }

    def apply_effect(self, effect):
        if effect == "expectations":
            self.expectation_bonus += 5
            return f"☀️ [EXPECTATIONS] Expectations fuel Apollo! Damage +{self.expectation_bonus}% [TRANSFORMATION: Light grows brighter as the crowd's expectations rise]"
        elif effect == "moonlight":
            return "🌙 [ARTEMIS MOON] Moonlight of Artemis summoned! Next attack deals double damage! [TRANSFORMATION: A giant statue of Artemis rises, aiming her bow at the target]"
        elif effect == "shield":
            self.defending = True
            return "🛡️ [THREAD SHIELD] Thread shield created! [TRANSFORMATION: Light threads weave into a protective barrier around Apollo]"
        return ""


class Susanoo(Character):
    def __init__(self):
        super().__init__(
            "Susano'o no Mikoto",
            "God of Storms • Japanese Pantheon",
            1280, 450,
            [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH]
        )
        self.round = 10
        self.affiliation = "Gods"
        self.musouken_used = 0
        self.max_musouken = 2
        self.yatagarasu_form = False
        self.weapon_form = "onikiri"

        self.divine_technique = {
            "name": "🌪️ MUSOUKEN: Unarmed Sword",
            "cost": 250,
            "dmg": (700, 900),
            "type": "damage",
            "desc": "🌪️ [UNARMED SWORD] Susano'o's ultimate technique. He creates an invisible blade of nothingness that cuts only the INSIDE of the body. [TRANSFORMATION: Nothingness itself becomes a blade, cutting internal organs while leaving the outside untouched]"
        }

        self.abilities = {
            '1': {"name": "🌪️ Storm's Wrath", "cost": 30, "dmg": (180, 240), "type": "damage",
                  "desc": "🌪️ [STORM WRATH] Susano'o channels the fury of the storm into his strikes. [TRANSFORMATION: Each blow carries the force of hurricane winds]"},
            '2': {"name": "⚔️ Divine Lightning", "cost": 35, "dmg": (200, 270), "type": "damage",
                  "desc": "⚔️ [DIVINE LIGHTNING] Susano'o calls down lightning from the heavens. [TRANSFORMATION: Lightning channels through his blade for devastating effect]"},
            '3': {"name": "👁️ Shinra Yaoyorozu", "cost": 40, "dmg": (0, 0), "type": "buff", "effect": "shinra",
                  "desc": "👁️ [SHINRA YAOYOROZU] Susano'o awakens the eight million gods within him. [TRANSFORMATION: Countless divine spirits manifest around him, ready to counter any sword attack]"},
            '4': {"name": "🌪️ Ama no Magaeshi", "cost": 60, "dmg": (330, 410), "type": "damage",
                  "desc": "🌪️ [HEAVENLY REVERSE] The heavenly reverse - turns opponent's strength against them. [TRANSFORMATION: Air itself is cut, creating a vacuum blade that flies forward]"},
            '5': {"name": "🌪️ Ama no Magaeshi: Avici", "cost": 50, "dmg": (290, 360), "type": "damage",
                  "desc": "🌪️ [HELL REVERSE] A version that sends opponents to the deepest hell. [TRANSFORMATION: Faster but weaker vacuum blade]"},
            '6': {"name": "🌪️ Ama no Magaeshi: Yakumo", "cost": 70, "dmg": (370, 470), "type": "damage",
                  "desc": "🌪️ [EIGHT CLOUDS] A multi-layered heavenly reverse. [TRANSFORMATION: Eight clouds of destruction form around the opponent]"},
            '7': {"name": "⚔️ Musouken", "cost": 150, "dmg": (550, 700), "type": "damage", "invisible": True,
                  "effect": "musouken",
                  "desc": "⚔️ [UNARMED SWORD] The unarmed sword - an invisible blade that cuts only the inside. Can only be used twice. [TRANSFORMATION: Nothingness itself becomes a blade, visible only to those who have reached the peak of swordsmanship]"},
            '8': {"name": "🐦‍⬛ Yatagarasu Form", "cost": 40, "dmg": (0, 0), "type": "buff", "effect": "yatagarasu",
                  "desc": "🐦‍⬛ [YATAGARASU] Susano'o transforms into the three-legged crow Yatagarasu. 80% evasion for 2 turns. [TRANSFORMATION: Susano'o becomes the divine crow, watching all swordsmen throughout history]"},
            '9': {"name": "⚔️ Switch Weapon", "cost": 15, "dmg": (0, 0), "type": "buff", "effect": "switch_weapon",
                  "desc": "⚔️ [SWITCH SWORD] Susano'o switches between his divine swords. [TRANSFORMATION: The blade transforms between Onikiri, Ame-no-Murakumo, and Totsuka]"}
        }

    def apply_effect(self, effect):
        if effect == "musouken":
            if self.musouken_used < self.max_musouken:
                self.musouken_used += 1
                self.take_damage(50)
                return f"⚔️ [MUSOUKEN] MUSOUKEN ACTIVATED! {self.max_musouken - self.musouken_used} uses remaining [TRANSFORMATION: An invisible blade of nothingness forms - it cuts only the inside, leaving the outside untouched]"
            return "❌ Cannot use Musouken again!"
        elif effect == "yatagarasu":
            self.yatagarasu_form = True
            self.divine_mode = True
            self.divine_timer = 2
            return "🐦‍⬛ [YATAGARASU] SUSANO'O TRANSFORMS INTO YATAGARASU! 80% evasion for 2 turns! [TRANSFORMATION: He becomes the three-legged crow, watching from above]"
        elif effect == "switch_weapon":
            weapons = ["onikiri", "ame-no-murakumo", "totsuka"]
            current_idx = weapons.index(self.weapon_form)
            self.weapon_form = weapons[(current_idx + 1) % 3]
            weapon_names = {"onikiri": "Demon-Slaying Sword", "ame-no-murakumo": "Heavenly Sword of Gathering Clouds",
                            "totsuka": "Ten-Hand Sword"}
            return f"⚔️ [SWITCH] Switched to {weapon_names[self.weapon_form]}! [TRANSFORMATION: The blade's form shifts to a different divine sword]"
        elif effect == "shinra":
            return "👁️ [SHINRA YAOYOROZU] Shinra Yaoyorozu activated! Can counter any sword attack! [TRANSFORMATION: Eight million gods manifest around Susano'o, ready to parry]"
        return ""


class Loki(Character):
    def __init__(self):
        super().__init__(
            "Loki",
            "God of Mischief • Norse Pantheon",
            1220, 440,
            [Realm.GODLY_TECHNIQUE]
        )
        self.round = 11
        self.affiliation = "Gods"
        self.clones = []
        self.max_clones = 5
        self.perfect_clone = None
        self.andvaranaut_active = False

        self.divine_technique = {
            "name": "🎭 HEIMSKRINGLA: Endurlífa",
            "cost": 200,
            "dmg": (550, 700),
            "type": "damage",
            "desc": "🎭 [HEIMSKRINGLA] Loki's ultimate trick. He creates a perfect clone and can swap positions at will. [TRANSFORMATION: Reality itself bends as Loki creates an indistinguishable copy, then swaps places through space]"
        }

        self.abilities = {
            '1': {"name": "🎭 Illusion Strike", "cost": 25, "dmg": (150, 210), "type": "damage",
                  "desc": "🎭 [ILLUSION STRIKE] Loki strikes from behind an illusion. [TRANSFORMATION: An illusion of Loki distracts while the real one attacks from behind]"},
            '2': {"name": "🎭 Shapeshift", "cost": 30, "dmg": (0, 0), "type": "buff",
                  "desc": "🎭 [SHAPESHIFT] Loki shifts his form, becoming harder to predict. [TRANSFORMATION: Loki's appearance flickers between forms, confusing enemies]"},
            '3': {"name": "🔗 Dual-Chained Hooks", "cost": 35, "dmg": (190, 260), "type": "damage",
                  "desc": "🔗 [CHAIN HOOKS] Loki throws his chained hooks, binding opponents. [TRANSFORMATION: Chains extend from his palms, seeking targets]"},
            '4': {"name": "🔄 Heimskringla: Copy", "cost": 40, "dmg": (0, 0), "type": "clone", "effect": "copy",
                  "desc": "🔄 [CLONE] Loki creates a copy of himself. [TRANSFORMATION: Dark mist coalesces into an identical copy]"},
            '5': {"name": "👤 Hveðrung", "cost": 60, "dmg": (0, 0), "type": "clone", "effect": "hvedrung",
                  "desc": "👤 [FALSE DIVINE SHADOW] Loki creates a perfect clone that shares his full power, personality, and knowledge. This clone can work autonomously and even use Heimskringla independently. [TRANSFORMATION: Dark mist from Loki's palm coalesces into an indistinguishable duplicate - same power, same mind, same will]"},
            '6': {"name": "👁️ Níu Heimr Auga", "cost": 35, "dmg": (0, 0), "type": "buff", "effect": "share_vision",
                  "desc": "👁️ [PEEPHOLE OF THE NINE WORLDS] Loki shares his vision with all clones by connecting his consciousness to theirs. His pupils visibly dilate as he sees through every clone's eyes simultaneously. [TRANSFORMATION: Nine realms of vision merge - Loki perceives the battlefield from every angle at once]"},
            '7': {"name": "🔄 Endurlífa", "cost": 50, "dmg": (0, 0), "type": "utility", "effect": "endurlifa",
                  "desc": "🔄 [GATE OF RESURRECTION] Loki instantly swaps positions with any of his clones. The target copy dissolves in the process. [TRANSFORMATION: Space itself warps - Loki and his clone exchange places through a dimensional gate]"},
            '8': {"name": "💍 Andvaranaut", "cost": 80, "dmg": (0, 0), "type": "buff", "effect": "andvaranaut",
                  "desc": "💍 [ANDVARANAUT] Loki activates the cursed ring Andvaranaut, removing his clone limit for 3 turns. [TRANSFORMATION: The silver ring glows with cursed power, removing all limits on cloning]"},
            '9': {"name": "🎭 Trickster's Gambit", "cost": 70, "dmg": (330, 410), "type": "damage",
                  "desc": "🎭 [TRICKSTER'S GAMBIT] Loki's ultimate trick - he attacks from one direction while striking from another. [TRANSFORMATION: Multiple Lokis appear from all directions]"},
            '10': {"name": "🛡️ Shield of Skuld", "cost": 35, "dmg": (0, 0), "type": "defense",
                   "desc": "🛡️ [SHIELD OF SKULD] Loki conjures a piece of stone wall with an ornate wooden door. Created by Heimskringla, it can halt even powerful piercing attacks for a few seconds. [TRANSFORMATION: Dark mist from Loki's palm solidifies into an ancient stone barrier - the door of fate itself blocks the attack]"}
        }

    def apply_effect(self, effect):
        if effect == "copy":
            if len(self.clones) < self.max_clones or self.andvaranaut_active:
                base_power = 100 // (len(self.clones) + 2)
                self.clones.append({"power": base_power, "active": True})
                return f"✅ [CLONE] Clone created! Total clones: {len(self.clones)} [TRANSFORMATION: Dark mist from Loki's palm forms a copy, though weaker with each additional clone]"
            return "❌ Maximum clones reached!"
        elif effect == "hvedrung":
            if len(self.clones) < self.max_clones or self.andvaranaut_active:
                self.perfect_clone = {"power": 100, "active": True}
                self.clones.append(self.perfect_clone)
                return f"✅ [PERFECT CLONE] Perfect clone created! [TRANSFORMATION: A perfect duplicate emerges, sharing Loki's full power and consciousness]"
            return "❌ Maximum clones reached!"
        elif effect == "share_vision":
            return "👁️ [SHARED VISION] Vision shared with all clones! [TRANSFORMATION: Loki's eyes glow as he sees through every clone simultaneously]"
        elif effect == "endurlifa":
            if self.clones:
                return "🔄 [SWAP] Loki swaps positions with a clone! [TRANSFORMATION: Loki and his clone instantaneously exchange places through a spatial gate]"
            return "❌ No clones to swap with!"
        elif effect == "andvaranaut":
            self.andvaranaut_active = True
            return "💍 [ANDVARANAUT] Andvaranaut activated! Clone limit removed for 3 turns! [TRANSFORMATION: The silver ring multiplies, its cursed power breaking all limits]"
        return ""


class Odin(Character):
    def __init__(self):
        super().__init__(
            "Odin",
            "All-Father • Norse Pantheon",
            1500, 520,
            [Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL]
        )
        self.round = 12
        self.affiliation = "Gods"
        self.form = "Old"
        self.life_theft_active = False
        self.active_treasure = None
        self.treasure_timer = 0

        self.divine_technique = {
            "name": "🔱 GUNGNIR: Absolute Certainty",
            "cost": 220,
            "dmg": (650, 850),
            "type": "damage",
            "desc": "🔱 [GUNGNIR] Odin throws Gungnir, the spear that never misses. The spear's trajectory is absolute and unavoidable. [TRANSFORMATION: Gungnir becomes one with fate itself - once thrown, it WILL hit its target no matter what]"
        }

        self.abilities = {
            '1': {"name": "🔱 Gungnir Thrust", "cost": 35, "dmg": (200, 270), "type": "damage",
                  "desc": "🔱 [GUNGNIR THRUST] A thrust of the legendary spear Gungnir. [TRANSFORMATION: The spear of destiny manifests in Odin's hand, its aim true]"},
            '2': {"name": "🐦‍⬛ Huginn's Sight", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "huginn",
                  "desc": "🐦‍⬛ [HUGINN] Odin sends Huginn (Thought) across the battlefield. 50% dodge next turn. [TRANSFORMATION: Thought itself becomes a raven, revealing enemy movements]"},
            '3': {"name": "🐦‍⬛ Muninn's Memory", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "muninn",
                  "desc": "🐦‍⬛ [MUNINN] Odin sends Muninn (Memory) through time. Next attack deals double damage. [TRANSFORMATION: Memory becomes a raven, recalling enemy weaknesses from the past]"},
            '4': {"name": "🔮 6th Cursed Hymn: Hel Víta", "cost": 45, "dmg": (240, 320), "type": "damage",
                  "desc": "🔮 [HEL'S CURSE] Odin chants a cursed hymn that drains the life force from his opponent. [TRANSFORMATION: Dark runes form in the air, each one draining vitality]"},
            '5': {"name": "🔮 9th Cursed Hymn: Vindsskuggr", "cost": 70, "dmg": (370, 470), "type": "damage",
                  "desc": "🔮 [WIND SHADOW] The ninth cursed hymn - Odin summons blades of darkness. [TRANSFORMATION: Shadows of the wind become physical blades]"},
            '6': {"name": "🔮 5th Cursed Hymn: Fafnir", "cost": 60, "dmg": (330, 410), "type": "damage",
                  "desc": "🔮 [FAFNIR'S GREED] Odin channels the greed and power of the dragon Fafnir. [TRANSFORMATION: Dragon energy coalesces, striking with avaricious fury]"},
            '7': {"name": "🌿 Life Theft", "cost": 40, "dmg": (0, 0), "type": "buff", "effect": "life_theft",
                  "desc": "🌿 [LIFE THEFT] Odin drains the life energy from all enemies for 3 turns. [TRANSFORMATION: A dark aura extends from Odin, siphoning vitality]"},
            '8': {"name": "✨ Matter Manipulation", "cost": 40, "dmg": (0, 0), "type": "buff", "effect": "matter",
                  "desc": "✨ [MATTER MANIPULATION] Odin shapes reality around him. Next attack ignores defenses. Can also create matter from nothing - hiding his true appearance under facades, creating Gram from his flesh. [TRANSFORMATION: Reality bends to Odin's will - matter itself obeys his command. The crystal ornament Gungnir reshapes into its spear form]"},
            '9': {"name": "🗡️ Manifest Gram", "cost": 50, "dmg": (0, 0), "type": "buff", "effect": "gram",
                  "desc": "🗡️ [MANIFEST GRAM] Odin manifests Gram, the legendary sword of Sigurd. +50% damage. [TRANSFORMATION: The sword containing the soul of the Primordial Odin materializes from his flesh]"},
            '10': {"name": "💍 Manifest Draupnir", "cost": 50, "dmg": (0, 0), "type": "buff", "effect": "draupnir",
                   "desc": "💍 [MANIFEST DRAUPNIR] Odin manifests Draupnir, the self-multiplying ring. [TRANSFORMATION: The ring of Chaos multiplies endlessly, each duplicate a weapon]"},
            '11': {"name": "⛑️ Manifest Egil", "cost": 50, "dmg": (0, 0), "type": "buff", "effect": "egil",
                   "desc": "⛑️ [MANIFEST EGIL] Odin manifests the helmet Egil, focusing dark energy. [TRANSFORMATION: The helmet of Satan forms, dark energy concentrating]"},
            '12': {"name": "📿 Manifest Brisingamen", "cost": 50, "dmg": (0, 0), "type": "buff", "effect": "brisingamen",
                   "desc": "📿 [MANIFEST BRISINGAMEN] Odin manifests the necklace Brisingamen, channeling frost. [TRANSFORMATION: The necklace of Ymir appears, radiating primordial cold]"},
            '13': {"name": "👤 Battle Form", "cost": 80, "dmg": (0, 0), "type": "buff", "effect": "battle_form",
                   "desc": "👤 [BATTLE FORM] Odin's true warrior form - his aged facade disintegrates to ash, revealing the young god beneath. Black hair with white accents, six marks around his eye crackling with power. Gods instinctively understand that this form is supreme, sacred, and inviolable. [TRANSFORMATION: The Supreme God sheds his mortal guise - gods and humans tremble before this sacred, inviolable form]"},
            '14': {"name": "🔱 Gungnir: Absolute Certainty", "cost": 150, "dmg": (550, 700), "type": "damage",
                   "desc": "🔱 [ABSOLUTE CERTAINTY] Odin throws Gungnir with absolute certainty. [TRANSFORMATION: Gungnir becomes one with fate - its trajectory is absolute]"},
            '15': {"name": "🌿 Life Theft/Decay", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "🌿 [LIFE THEFT] When Odin experiences strong emotions, nearby life withers and dies. Passive aura drains 5 HP from all enemies each turn when Odin's excitement rises. [TRANSFORMATION: Divine excitement causes flowers to wilt and life energy to fade - even the arena's plants crumble to ash]"}
        }

    def apply_effect(self, effect):
        if effect == "huginn":
            return "🐦‍⬛ [HUGINN] Huginn reveals enemy's next move! 50% dodge next turn. [TRANSFORMATION: Thought becomes a raven, whispering enemy movements]"
        elif effect == "muninn":
            return "🐦‍⬛ [MUNINN] Muninn reveals enemy's weakness! Next attack deals double damage! [TRANSFORMATION: Memory becomes a raven, recalling past weaknesses]"
        elif effect == "life_theft":
            self.life_theft_active = True
            return "🌿 [LIFE THEFT] Life energy drained from all enemies for 3 turns! [TRANSFORMATION: Dark tendrils extend from Odin, siphoning vitality]"
        elif effect == "matter":
            return "✨ [MATTER MANIPULATION] Matter manipulation active! Next attack ignores defenses. [TRANSFORMATION: Reality itself bends to Odin's will]"
        elif effect == "gram":
            self.active_treasure = "gram"
            self.treasure_timer = 3
            return "🗡️ [MANIFEST GRAM] Gram manifested! The legendary sword of Sigurd appears! +50% damage [TRANSFORMATION: The blade containing the soul of the Primordial Odin materializes from his flesh]"
        elif effect == "draupnir":
            self.active_treasure = "draupnir"
            self.treasure_timer = 3
            return "💍 [MANIFEST DRAUPNIR] Draupnir manifested! The self-multiplying ring of Chaos! [TRANSFORMATION: The ring multiplies endlessly, each duplicate a weapon]"
        elif effect == "egil":
            self.active_treasure = "egil"
            self.treasure_timer = 3
            return "⛑️ [MANIFEST EGIL] Egil manifested! The helmet of Satan focuses dark energy! [TRANSFORMATION: The cursed helmet forms, dark energy concentrating]"
        elif effect == "brisingamen":
            self.active_treasure = "brisingamen"
            self.treasure_timer = 3
            return "📿 [MANIFEST BRISINGAMEN] Brisingamen manifested! The necklace of Ymir channels primordial frost! [TRANSFORMATION: Ancient frost radiates from the divine necklace]"
        elif effect == "battle_form":
            self.form = "Young"
            self.divine_mode = True
            self.divine_timer = 5
            self.max_hp += 200
            self.hp += 200
            return "👤 [BATTLE FORM] ODIN REVEALS HIS BATTLE FORM! [TRANSFORMATION: His aged form disintegrates to ash, revealing the young warrior god beneath - black hair with white accents, six marks around his eye crackling with power]"
        return ""


class Hajun(Character):
    def __init__(self):
        super().__init__(
            "Hajun",
            "Demon King of Sixth Heaven",
            1600, 500,
            [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE, Realm.GODLY_WILL]
        )
        self.round = 6
        self.affiliation = "Helheim"
        self.soul_dark = True

        self.divine_technique = {
            "name": "👹 DEMON KING'S WRATH",
            "cost": 220,
            "dmg": (650, 850),
            "type": "damage",
            "desc": "👹 [DEMON KING'S WRATH] The attack that destroyed half of Helheim. Hajun unleashes his full demonic power. [TRANSFORMATION: Pure demonic energy erupts, erasing everything in its path]"
        }

        self.abilities = {
            '1': {"name": "👹 Demon Strike", "cost": 35, "dmg": (200, 270), "type": "damage",
                  "desc": "👹 [DEMON STRIKE] A basic strike from the Demon King. [TRANSFORMATION: Demonic energy coats each strike, carrying the weight of slaughtered souls]"},
            '2': {"name": "👹 Helheim's Wrath", "cost": 55, "dmg": (300, 380), "type": "damage",
                  "desc": "👹 [HELHEIM'S WRATH] Hajun channels the rage of Helheim itself. [TRANSFORMATION: The fury of an entire realm manifests in each attack]"},
            '3': {"name": "👹 Dark Soul", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "👹 [DARK SOUL] Hajun's soul radiates pure darkness. Techniques that rely on seeing the soul's light cannot perceive his attacks. [PASSIVE: Buddha's future sight and similar abilities fail against him]"},
            '4': {"name": "👹 Demon King's Domain", "cost": 70, "dmg": (350, 450), "type": "damage",
                  "desc": "👹 [DEMON DOMAIN] Hajun expands his demonic aura, amplifying all attacks. [TRANSFORMATION: Demonic energy expands, creating a domain where all attacks are amplified]"},
            '5': {"name": "👹 Destruction of Helheim", "cost": 100, "dmg": (500, 650), "type": "damage",
                  "desc": "👹 [HELHEIM DESTRUCTION] Hajun replicates the attack that destroyed half of Helheim. [TRANSFORMATION: Pure annihilation - the same power that devastated a realm]"}
        }


# ============================================================================
# HUMAN CHARACTERS - WITH CANON DIVINE WEAPON NAMES
# ============================================================================

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

        self.abilities = {
            '1': {"name": "🏹 Sky Piercer", "cost": 30, "dmg": (160, 220), "type": "damage",
                  "desc": "🏹 [SKY PIERCER] Lü Bu thrusts his spear with enough force to pierce the heavens. [TRANSFORMATION: Raw power alone creates a shockwave that reaches the sky]"},
            '2': {"name": "🐎 Red Hare Charge", "cost": 35, "dmg": (190, 260), "type": "damage",
                  "desc": "🐎 [RED HARE] Lü Bu charges forward on his legendary steed Red Hare. [TRANSFORMATION: Man and horse become one, moving as a single unstoppable force]"},
            '3': {"name": "🏹 Basic Strike", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "🏹 [BASIC STRIKE] A basic attack from the Flying General."}
        }

    def activate_volund(self, valkyrie):
        """Lü Bu's Volund activation - Randgriz → Fang Tian Ji"""
        if valkyrie != Valkyrie.RANDGRIZ:
            return f"❌ Lü Bu can only bond with Randgriz!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Fang Tian Ji (方天画戟)"

        self.divine_technique = {
            "name": "🏹 SKY EATER",
            "cost": 180,
            "dmg": (550, 700),
            "type": "damage",
            "desc": "🏹 [SKY EATER] Lü Bu's ultimate technique with Randgriz. He channels all his strength into a single strike that splits the sky itself. [TRANSFORMATION: The halberd becomes an extension of Lü Bu's very soul, capable of tearing the heavens asunder]"
        }

        self.abilities = {
            '1': {"name": "🏹 Sky Piercer", "cost": 30, "dmg": (160, 220), "type": "damage",
                  "desc": "🏹 [SKY PIERCER] Lü Bu thrusts his spear with enough force to pierce the heavens. [TRANSFORMATION: Raw power alone creates a shockwave that reaches the sky]"},
            '2': {"name": "🐎 Red Hare Charge", "cost": 35, "dmg": (190, 260), "type": "damage",
                  "desc": "🐎 [RED HARE] Lü Bu charges forward on his legendary steed Red Hare. [TRANSFORMATION: Man and horse become one, moving as a single unstoppable force]"},
            '3': {"name": "🏹 Basic Strike", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "🏹 [BASIC STRIKE] A basic attack from the Flying General."},
            '4': {"name": "🏹 Incomplete Sky Eater", "cost": 50, "dmg": (270, 340), "type": "damage",
                  "desc": "🏹 [INCOMPLETE SKY EATER] A preliminary version of Sky Eater. [TRANSFORMATION: The first hints of heaven-rending power]"},
            '5': {"name": "🏹 Sky Eater", "cost": 100, "dmg": (430, 550), "type": "damage",
                  "desc": "🏹 [SKY EATER] The technique that defines Lü Bu. [TRANSFORMATION: The sky itself trembles before this strike]"},
            '6': {"name": "🦯 Broken Legs Fighting", "cost": 40, "dmg": (220, 290), "type": "damage",
                  "effect": "break_legs",
                  "desc": "🦯 [BROKEN LEGS] Even with broken legs, Lü Bu continues to fight. [TRANSFORMATION: Pain becomes power - even crippled, he stands]"}
        }

        print(f"\n⚔️⚔️⚔️ VOLUND: Lü Bu x Randgriz ⚔️⚔️⚔️")
        print(
            f"✅ Lü Bu awakens the {self.volund_weapon}! [TRANSFORMATION: Randgriz fuses with his halberd, creating a weapon that can shatter any defense]")
        print(f"   Now has {len(self.abilities)} abilities!")
        return f"✅ Volund successfully activated for Lü Bu!"

    def apply_effect(self, effect):
        if effect == "break_legs":
            self.legs_broken = True
            self.red_hare_active = True
            return "🦯 [BROKEN LEGS] Lü Bu fights with broken legs! [TRANSFORMATION: Pain becomes fuel - even with shattered legs, he stands and fights]"
        return ""


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

        self.abilities = {
            '1': {"name": "⚔️ Scanning", "cost": 20, "dmg": (0, 0), "type": "buff", "effect": "scan",
                  "desc": "⚔️ [SCANNING] Kojiro scans his opponent, analyzing their movements. [TRANSFORMATION: Thousands of simulations run in his mind with each scan]"},
            '2': {"name": "⚔️ Basic Slash", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "⚔️ [BASIC SLASH] A basic sword slash."}
        }

    def activate_volund(self, valkyrie):
        """Kojiro's Volund activation - Hrist → Bizen Nagamitsu / Monohoshizao"""
        if valkyrie != Valkyrie.HRIST:
            return f"❌ Kojiro can only bond with Hrist!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Bizen Nagamitsu / Monohoshizao (備前長光 / 物干竿)"

        self.divine_technique = {
            "name": "⚔️ SŌENZANKO BANJINRYŌRAN",
            "cost": 180,
            "dmg": (550, 700),
            "type": "damage",
            "desc": "⚔️ [TEN THOUSAND TIGER-SLAYING BLADE] Kojiro's ultimate technique combining Tsubame Gaeshi and Torakiri with both swords. [TRANSFORMATION: Two swords become one technique, each strike flowing into the next]"
        }

        self.abilities = {
            '1': {"name": "⚔️ Scanning", "cost": 20, "dmg": (0, 0), "type": "buff", "effect": "scan",
                  "desc": "⚔️ [SCANNING] Kojiro scans his opponent, analyzing their movements. [TRANSFORMATION: Thousands of simulations run in his mind with each scan]"},
            '2': {"name": "⚔️ Basic Slash", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "⚔️ [BASIC SLASH] A basic sword slash."},
            '3': {"name": "⚔️ Tsubame Gaeshi", "cost": 40, "dmg": (200, 270), "type": "damage",
                  "desc": "⚔️ [SWALLOW REVERSAL] The legendary swallow reversal. [TRANSFORMATION: The blade stops mid-descent and reverses direction, catching even swallows]"},
            '4': {"name": "⚔️ Torakiri", "cost": 35, "dmg": (180, 250), "type": "damage",
                  "desc": "⚔️ [TIGER CLAW] A horizontal slash that flows like water. [TRANSFORMATION: The blade shifts to a reverse grip, striking from unexpected angles]"},
            '5': {"name": "⚔️ Sōenzanko", "cost": 100, "dmg": (430, 550), "type": "damage",
                  "desc": "⚔️ [TWIN SWALLOW TIGER] The ultimate combination technique. [TRANSFORMATION: Tsubame Gaeshi and Torakiri merge into one devastating combo]"},
            '6': {"name": "👁️ Manju Muso", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "👁️ [ULTIMATE VISION] Kojiro's Senju Muso evolves to its peak. He can now analyze not just opponents but also vibrations traveling through air and ground, predicting movements with absolute precision. [TRANSFORMATION: The world itself becomes readable - every vibration tells him where the enemy will strike]"}
        }

        print(f"\n⚔️⚔️⚔️ VOLUND: Kojiro x Hrist ⚔️⚔️⚔️")
        print(
            f"✅ Kojiro awakens the {self.volund_weapon}! [TRANSFORMATION: Hrist's dual nature manifests in the blade - it can split into two when broken]")
        print(f"   Now has {len(self.abilities)} abilities!")
        return f"✅ Volund successfully activated for Kojiro Sasaki!"

    def apply_effect(self, effect):
        if effect == "scan":
            self.scan_progress += 1
            self.simulations_complete += 1000
            evasion = min(0.8, self.scan_progress * 0.1)
            crit = min(0.5, self.scan_progress * 0.05)
            return f"🔍 [SCAN] Scan {self.scan_progress}: {evasion * 100}% evasion, {crit * 100}% crit. [TRANSFORMATION: {self.simulations_complete} simulations complete - every possible move calculated]"
        return ""

    def check_weapon_break(self):
        if not self.weapon_broken and random.random() < 0.15:
            self.weapon_broken = True
            self.dual_wielding = True
            return "💥 [RE-VÖLUNDR] Monohoshizao SHATTERS! Re-Völundr activates! Kojiro now wields TWO SWORDS! [TRANSFORMATION: Hrist's dual nature emerges - one blade becomes two]"
        return None


# ============================================================================
# FIXED JACK THE RIPPER WITH LIMITED WEAPON USES AND TRANSFORMATION DESCRIPTIONS
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
                  "weapon": "Knife Strike", "max_uses": 50,
                  "desc": "🗡️ [KNIFE] A quick knife attack. Jack carries 50 knives in his magic pouches. [MAGIC GLOVES: Turns ordinary knife into DIVINE THROWING BLADE]"},
            '2': {"name": "👁️ Soul Eye", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "weapon": "Soul Eye", "max_uses": float('inf'),
                  "desc": "👁️ [SOUL EYE] Jack can see the 'color' of people's souls. [PASSIVE ABILITY - NOT A WEAPON]"}
        }

    def activate_volund(self, valkyrie):
        """Jack's Volund activation - Hlökk → Magic Gloves"""
        if valkyrie != Valkyrie.HLOKK:
            return f"❌ Jack can only bond with Hlökk!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Magic Gloves (能力: あらゆるものを神器化)"

        self.divine_technique = {
            "name": "🗡️ DEAR GOD",
            "cost": 200,
            "dmg": (550, 700),
            "type": "damage",
            "desc": "🗡️ [DEAR GOD] Jack's ultimate technique - he turns the entire city of London into his divine weapon. [TRANSFORMATION: Every building, every street, every shadow becomes a divine tool for murder - all channeled through the Magic Gloves]"
        }

        self.abilities = {
            '1': {"name": "🗡️ Knife Strike", "cost": 15, "dmg": (110, 160), "type": "damage",
                  "weapon": "Knife Strike", "max_uses": 50, "uses_left": 50,
                  "desc": "🗡️ [KNIFE] A quick knife attack. Jack carries 50 knives in his magic pouches. [MAGIC GLOVES: Turns ordinary knife into DIVINE THROWING BLADE]"},
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
            '10': {"name": "🏙️ Environment Weapon", "cost": 35, "dmg": (160, 230), "type": "damage",
                   "weapon": "Environment Weapon", "max_uses": float('inf'),
                   "effect": "environment",
                   "desc": "🏙️ [ENVIRONMENT WEAPON] Jack turns his surroundings into weapons - lampposts become spears, cobblestones become bullets. [MAGIC GLOVES: Turns ENVIRONMENT into DIVINE WEAPONS] Unlimited."},
            '11': {"name": "🌫️ Bloody Mist", "cost": 40, "dmg": (0, 0), "type": "buff",
                   "weapon": "Bloody Mist", "max_uses": float('inf'),
                   "desc": "🌫️ [BLOODY MIST] Jack creates a mist of blood that conceals his movements. [MAGIC GLOVES: Turns BLOOD into DIVINE CONCEALING MIST]"},
            '12': {"name": "🎪 Rondo of Blessing", "cost": 60, "dmg": (300, 380), "type": "damage",
                   "weapon": "Rondo of Blessing", "max_uses": float('inf'),
                   "desc": "🎪 [RONDO OF BLESSING] A graceful dance of death. Jack uses his cloak as a Divine Weapon, cutting an entire building to collapse onto his enemy. [TRANSFORMATION: Magic Gloves turn his cloak into a DIVINE BLADED CLOAK - the building becomes a DIVINE CRUSHING STRUCTURE]"},
            '13': {"name": "🦯 Grappling Hook", "cost": 20, "dmg": (0, 0), "type": "utility",
                   "weapon": "Grappling Hook", "max_uses": 1, "uses_left": 1,
                   "desc": "🦯 [GRAPPLING HOOK] Jack uses a grappling hook to reposition instantly. One-time. [MAGIC GLOVES: Turns grappling hook into DIVINE CATCHING TOOL]"},
            '14': {"name": "🦾 Arm Extension", "cost": 30, "dmg": (0, 0), "type": "buff",
                   "weapon": "Arm Extension", "max_uses": float('inf'),
                   "effect": "arm_extension",
                   "desc": "🦾 [ARM EXTENSION] Jack's arms extend unnaturally. [MAGIC GLOVES: Enhances his own BODY, allowing limbs to stretch]"},
            '15': {"name": "🗡️ Guidance of the Nocturne", "cost": 55, "dmg": (260, 330), "type": "damage",
                   "weapon": "Guidance of the Nocturne", "max_uses": float('inf'),
                   "desc": "🗡️ [GUIDANCE OF THE NOCTURNE] Jack strikes from the shadows. [MAGIC GLOVES: Turns SHADOWS into DIVINE SHADOW BLADES]"},
            '16': {"name": "🫀 Internal Organ Shift", "cost": 0, "dmg": (0, 0), "type": "passive",
                   "weapon": "Internal Organ Shift", "max_uses": float('inf'),
                   "desc": "🫀 [INTERNAL ORGAN SHIFT] Jack can shift his internal organs to avoid fatal blows. [PASSIVE - SELF TRANSFORMATION]"},
        }

        print(f"\n⚔️⚔️⚔️ VOLUND: Jack x Hlökk (FORCED) ⚔️⚔️⚔️")
        print(f"✅ Jack awakens the {self.volund_weapon}! Now has {len(self.abilities)} weapons!")
        print(
            f"📦 Limited weapons: Knives(50), Piano Wire(10), Umbrella(2), Scissors(1), Switchblade(1), Grappling Hook(1), Axes(2), Cannonball(1)")
        print(f"\n🔍 [MAGIC GLOVES] Jack's gloves can turn ANY object he touches into a Divine Weapon!")
        print(f"   - Items from pouches → Divine weapons")
        print(f"   - Environment → Divine environment weapons")
        print(f"   - Own body → Enhanced divine body parts")
        print(f"   - Shadows/Blood/Cloak → Abstract divine weapons")
        return f"✅ Volund successfully activated for Jack the Ripper!"

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

                # Add flavor text showing the transformation
                if "Knife" in weapon_name:
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

    def apply_effect(self, effect):
        if effect == "environment":
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
            return f"⚡ [MAGIC GLOVES] Jack touches the {loc} with his Magic Gloves - it transforms into a {weapon}!"
        elif effect == "arm_extension":
            return "🦾 [MAGIC GLOVES] Jack's arms extend unnaturally as the Magic Gloves enhance his own body!"
        return ""

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
            filled = int(bar_len * uses / max_uses) if max_uses != float('inf') else bar_len
            bar = "█" * filled + "░" * (bar_len - filled)
            if max_uses != float('inf'):
                percentage = int((uses / max_uses) * 100)
                print(f"  {name:25} |{bar}| {uses:2}/{max_uses} ({percentage}%)")

                # Show what each item transforms into
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
                    print(f"      ↳ [MAGIC GLOVES] Grappling hook → DIVINE CATCHING TOOL")
            else:
                print(f"  {name:25} |{bar}| Unlimited")
                if "Environment" in name:
                    print(f"      ↳ [MAGIC GLOVES] Surroundings → DIVINE ENVIRONMENT WEAPONS")
                elif "Rondo" in name:
                    print(f"      ↳ [MAGIC GLOVES] Cloak → DIVINE BLADED CLOAK")
                elif "Guidance" in name:
                    print(f"      ↳ [MAGIC GLOVES] Shadows → DIVINE SHADOW BLADES")
                elif "Arm" in name:
                    print(f"      ↳ [MAGIC GLOVES] Body → EXTENDED DIVINE REACH")
                elif "Bloody" in name:
                    print(f"      ↳ [MAGIC GLOVES] Blood → DIVINE CONCEALING MIST")
                elif "Internal" in name:
                    print(f"      ↳ [PASSIVE] Self → DIVINE ORGAN SHIFTING")

        print("=" * 110)


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

        self.abilities = {
            '1': {"name": "💪 Basic Strike", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "💪 [BASIC STRIKE] A basic sumo strike."}
        }

    def activate_volund(self, valkyrie):
        """Raiden's Volund activation - Thrud → Supramuscular Exoskeletal Mawashi Belt"""
        if valkyrie != Valkyrie.THRUD:
            return f"❌ Raiden can only bond with Thrud!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Supramuscular Exoskeletal Mawashi Belt (超筋骨外骨締廻し)"

        self.divine_technique = {
            "name": "💪 YATAGARASU",
            "cost": 200,
            "dmg": (600, 800),
            "type": "damage",
            "desc": "💪 [YATAGARASU] Raiden's ultimate palm strike that removed four of Shiva's arms. [TRANSFORMATION: All of Raiden's muscle power concentrates into a single devastating palm strike]"
        }

        self.abilities = {
            '1': {"name": "💪 Basic Strike", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "💪 [BASIC STRIKE] A basic sumo strike."},
            '2': {"name": "💪 Muscle Control - 70%", "cost": 25, "dmg": (160, 220), "type": "damage",
                  "release": 70,
                  "desc": "💪 [70% RELEASE] Raiden releases 70% of his muscle control. [TRANSFORMATION: Muscles begin to swell as the first seals break]"},
            '3': {"name": "💪 Muscle Control - 80%", "cost": 35, "dmg": (200, 270), "type": "damage",
                  "release": 80,
                  "desc": "💪 [80% RELEASE] Raiden releases 80% of his muscle control. [TRANSFORMATION: Muscle fibers expand further, power increasing]"},
            '4': {"name": "💪 Muscle Control - 90%", "cost": 45, "dmg": (250, 330), "type": "damage",
                  "release": 90,
                  "desc": "💪 [90% RELEASE] Raiden releases 90% of his muscle control. [TRANSFORMATION: Only the final seal remains - power is almost fully unleashed]"},
            '5': {"name": "💪 Yatagarasu", "cost": 120, "dmg": (470, 630), "type": "damage",
                  "desc": "💪 [YATAGARASU] The ultimate palm strike. [TRANSFORMATION: All released muscle power flows into a single devastating palm strike - named after the three-legged crow]"}
        }

        print(f"\n⚔️⚔️⚔️ VOLUND: Raiden x Thrud ⚔️⚔️⚔️")
        print(
            f"✅ Raiden awakens the {self.volund_weapon}! [TRANSFORMATION: Thrud's power fuses with Raiden's muscles, allowing him to safely release his 100 Seals]")
        print(f"   Now has {len(self.abilities)} abilities!")
        return f"✅ Volund successfully activated for Raiden Tameemon!"

    def apply_effect(self, effect):
        if effect == "release":
            self.muscle_release = 100
            return "💪 [100% RELEASE] 100% Release! Muscles fully unleashed! [TRANSFORMATION: The final seal breaks - Raiden's true power erupts]"
        return ""


class Buddha(Character):
    def __init__(self):
        super().__init__(
            "Buddha",
            "The Enlightened One",
            1250, 440,
            [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL]
        )
        self.round = 6
        self.affiliation = "Humanity"
        self.future_sight_active = True
        self.current_emotion = "serenity"
        self.current_weapon = "Twelve Deva Axe"
        self.zerofuku_fused = False

        self.weapons = {
            "serenity": {
                "name": "🪓 Twelve Deva Axe (十二天斧)",
                "dmg": (200, 270),
                "desc": "🪓 [TWELVE DEVA AXE] A massive axe that sweeps through opponents with the serenity of enlightenment. [TRANSFORMATION: The Six Realms staff transforms into an axe of divine judgment]"
            },
            "determination": {
                "name": "⚔️ Vajra Short Sword (金剛独鈷剣)",
                "dmg": (180, 250),
                "desc": "⚔️ [VAJRA SWORD] A short sword that strikes with determination. [TRANSFORMATION: The staff becomes a single-pronged vajra sword, cutting through suffering]"
            },
            "aggression": {
                "name": "🔨 Giant Spiked Club (正覚涅槃棒)",
                "dmg": (220, 300),
                "desc": "🔨 [NIRVANA CLUB] A brutal club that crushes evil. [TRANSFORMATION: The staff becomes a massive spiked club of enlightenment]"
            },
            "righteous_anger": {
                "name": "🛡️ Shield of Ahimsa (七難即滅の楯)",
                "dmg": (0, 0),
                "desc": "🛡️ [SHIELD OF AHIMSA] A shield that blocks any attack. [TRANSFORMATION: The staff becomes a golden shield that can withstand any assault]"
            },
            "hatred": {
                "name": "🌾 Warscythe of Salakaya (荒神の戦鎌)",
                "dmg": (210, 290),
                "desc": "🌾 [SALAKAYA SCYTHE] A scythe that channels dead souls. [TRANSFORMATION: The staff becomes a warscythe, channeling the souls of the dead]"
            }
        }

        self.abilities = {
            '1': {"name": "🧘 Activate Six Realms", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "six_realms",
                  "desc": "🧘 [SIX REALMS] Buddha cycles through the Six Realms, his weapon adapting accordingly. [TRANSFORMATION: The staff transforms based on Buddha's current emotion]"},
            '2': {"name": "👁️ Future Sight", "cost": 25, "dmg": (0, 0), "type": "buff", "effect": "future_sight",
                  "desc": "👁️ [FUTURE SIGHT] Buddha's enlightenment allows him to see a few seconds into the future. [TRANSFORMATION: Time itself becomes transparent - he sees actions before they happen]"},
            '3': {"name": "🧘 Meditation", "cost": 10, "dmg": (0, 0), "type": "heal", "effect": "meditate",
                  "desc": "🧘 [MEDITATION] Buddha meditates, restoring his HP. [TRANSFORMATION: Buddha enters a state of perfect stillness, wounds healing]"},
        }

    def activate_volund(self, valkyrie):
        """Buddha doesn't need a Valkyrie"""
        return f"❌ Buddha is a former god and doesn't need a Valkyrie."

    def apply_effect(self, effect):
        if effect == "six_realms":
            emotions = list(self.weapons.keys())
            self.current_emotion = random.choice(emotions)
            weapon = self.weapons[self.current_emotion]

            weapon_key = '6'
            self.abilities[weapon_key] = {
                "name": f"✨ {weapon['name']}",
                "cost": 40,
                "dmg": weapon['dmg'],
                "type": "damage",
                "desc": weapon['desc'],
                "weapon": self.current_emotion
            }

            if self.current_emotion == "righteous_anger":
                self.defending = True

            emotion_descriptions = {
                "serenity": "Calm and peaceful - the Axe of the Twelve Devas manifests",
                "determination": "Focused and resolute - the Vajra Short Sword appears",
                "aggression": "Fierce and unyielding - the Nirvana Club forms",
                "righteous_anger": "Righteous fury - the Shield of Ahimsa emerges",
                "hatred": "Dark and wrathful - the Salakaya Warscythe materializes"
            }

            return f"🧘 [SIX REALMS] Buddha's emotion: {self.current_emotion} - {emotion_descriptions[self.current_emotion]}\nWeapon: {weapon['name']}\n{weapon['desc']}"
        elif effect == "future_sight":
            self.future_sight_active = True
            return "👁️ [FUTURE SIGHT] Future sight activated! 50% evasion next turn. [TRANSFORMATION: Buddha sees moments before they happen, moving preemptively]"
        elif effect == "meditate":
            self.heal(50)
            return "🧘 [MEDITATION] Buddha meditates and recovers 50 HP. [TRANSFORMATION: Wounds close as he reaches inner peace]"
        return ""

    def check_soul_light(self, enemy):
        if hasattr(enemy, 'soul_dark') and enemy.soul_dark:
            self.future_sight_active = False
            return "⚠️ [DARK SOUL] Buddha's future sight fails! The enemy's soul has no light! [TRANSFORMATION: The future becomes opaque - Hajun's dark soul cannot be read]"
        return "✨ [SOUL LIGHT] The enemy's soul has light."

    def gain_great_nirvana_sword(self):
        self.zerofuku_fused = True
        self.abilities['99'] = {
            "name": "🗡️ Mahaparinirvana Zero (大円寂刀・零)",
            "cost": 150,
            "dmg": (500, 650),
            "type": "damage",
            "desc": "🗡️ [MAHAPARINIRVANA ZERO] The ultimate divine weapon created from Zerofuku's soul. [TRANSFORMATION: Zerofuku's very being becomes a seven-branched sword - the Great Nirvana Sword Zero]"
        }
        return "✨ [NIRVANA SWORD] Great Nirvana Sword Zero awakened! [TRANSFORMATION: Zerofuku's soul fuses with Buddha's compassion, creating the ultimate divine weapon]"


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

        self.abilities = {
            '1': {"name": "👑 Imperial Strike", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "👑 [IMPERIAL STRIKE] A basic strike from the First Emperor."}
        }

    def activate_volund(self, valkyrie):
        """Qin's Volund activation - Alvitr → Pauldron of Divine Embrace / First Emperor's Goujian Sword"""
        if valkyrie != Valkyrie.ALVITR:
            return f"❌ Qin can only bond with Alvitr!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Pauldron of Divine Embrace / First Emperor's Goujian Sword (神羅鎧袖 / 始皇勾践剣)"

        self.divine_technique = {
            "name": "👑 FIRST EMPEROR'S POWER EMBRACE - SWALLOW SLASH",
            "cost": 190,
            "dmg": (580, 750),
            "type": "damage",
            "desc": "👑 [EMPEROR'S SWALLOW SLASH] Qin's ultimate technique combining all five Chiyou styles into one devastating counter. [TRANSFORMATION: The Pauldron of Divine Embrace transforms into the First Emperor's Goujian Sword for this ultimate strike]"
        }

        self.abilities = {
            '1': {"name": "👑 Imperial Strike", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "👑 [IMPERIAL STRIKE] A basic strike from the First Emperor."},
            '2': {"name": "👁️ Remove Blindfold", "cost": 15, "dmg": (0, 0), "type": "buff",
                  "effect": "blindfold",
                  "desc": "👁️ [REMOVE BLINDFOLD] Qin removes his blindfold, revealing his star-like eyes. [TRANSFORMATION: The blindfold falls, revealing eyes that can see the flow of Chi itself]"},
            '3': {"name": "🐉 Mount Tai Dragon Claw", "cost": 45, "dmg": (240, 320), "type": "damage",
                  "desc": "🐉 [DRAGON CLAW] Qin's fingers become like dragon claws. [TRANSFORMATION: Qi flows through his fingers, turning them into piercing dragon claws]"},
            '4': {"name": "👑 Emperor's Swallow Slash", "cost": 100, "dmg": (470, 610), "type": "damage",
                  "desc": "👑 [SWALLOW SLASH] The ultimate combination of all five Chiyou styles. [TRANSFORMATION: All five martial arts flow into one devastating slash]"}
        }

        print(f"\n⚔️⚔️⚔️ VOLUND: Qin x Alvitr ⚔️⚔️⚔️")
        print(
            f"✅ Qin awakens the {self.volund_weapon}! [TRANSFORMATION: Alvitr's power manifests as golden armor - the Pauldron of Divine Embrace, which can transform into the First Emperor's Goujian Sword]")
        print(f"   Now has {len(self.abilities)} abilities!")
        return f"✅ Volund successfully activated for Qin Shi Huang!"

    def apply_effect(self, effect):
        if effect == "blindfold":
            self.star_eyes_active = True
            return "👁️ [STAR EYES] Qin removes blindfold - can see Chi flow! [TRANSFORMATION: His eyes reveal the flow of Qi in all living things - he can see the cruxes of power]"
        return ""


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

        self.abilities = {
            '1': {"name": "⚡ Basic Punch", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "⚡ [BASIC PUNCH] A basic punch."}
        }

    def activate_volund(self, valkyrie):
        """Tesla's Volund activation - Göndul → Super Automaton Beta"""
        if valkyrie != Valkyrie.GONDUL:
            return f"❌ Tesla can only bond with Göndul!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Super Automaton Beta (超人自動機械β)"

        self.divine_technique = {
            "name": "⚡ PLASMA PULSE PUNCH CROSS (PPPX)",
            "cost": 200,
            "dmg": (600, 780),
            "type": "damage",
            "desc": "⚡ [PPP CROSS] Tesla's ultimate technique. He feigns an attack with one fist while teleporting the other. [TRANSFORMATION: Tesla Warp synchronizes with a feint - one fist attacks from the front while the other teleports behind]"
        }

        self.abilities = {
            '1': {"name": "⚡ Basic Punch", "cost": 15, "dmg": (120, 170), "type": "damage",
                  "desc": "⚡ [BASIC PUNCH] A basic punch."},
            '2': {"name": "⚡ Plasma Pulse Punch (PPP)", "cost": 25, "dmg": (160, 220), "type": "damage",
                  "desc": "⚡ [PPP] A basic plasma-enhanced punch. [TRANSFORMATION: Electrical energy concentrates in Tesla's fist, releasing in a plasma burst]"},
            '3': {"name": "🔬 Gematria Zone", "cost": 50, "dmg": (0, 0), "type": "buff",
                  "effect": "gematria",
                  "desc": "🔬 [GEMATRIA ZONE] Tesla creates a zone of altered space-time. [TRANSFORMATION: Super Tesla Particles fill a 9.63m by 9.63m cage, creating a space where physics bend to Tesla's will]"},
            '4': {"name": "⚡ Tesla Warp", "cost": 60, "dmg": (0, 0), "type": "utility",
                  "effect": "teleport",
                  "desc": "⚡ [TESLA WARP] Tesla warps through space. 3 uses. [TRANSFORMATION: The Super Tesla Coil synchronizes with particle-dense areas, allowing instantaneous teleportation]"},
            '5': {"name": "⚡ Plasma Pulse Punch Cross (PPPX)", "cost": 120, "dmg": (500, 650),
                  "type": "damage",
                  "desc": "⚡ [PPP CROSS] The ultimate technique - Tesla feints with one fist while teleporting the other. [TRANSFORMATION: Tesla Warp combines with PPP - a pincer attack from front and back simultaneously]"},
            '6': {"name": "⚡ Zero Max", "cost": 0, "dmg": (0, 0), "type": "passive",
                  "desc": "⚡ [ZERO MAX] Within Gematria Zone, Tesla's anti-gravity system allows him to reach maximum speed in just the first stride. [TRANSFORMATION: Super Tesla Particles eliminate inertia - from zero to max in an instant]"},
            '7': {"name": "⚡ Tesla Step", "cost": 30, "dmg": (0, 0), "type": "buff", "effect": "tesla_step",
                  "desc": "⚡ [TESLA STEP] Tesla floats and moves in unpredictable patterns within Gematria Zone. Tesla Step Wonderful creates numerous afterimages. [TRANSFORMATION: Super Tesla Particles allow three-dimensional movement - gravity is optional]"}
        }

        print(f"\n⚔️⚔️⚔️ VOLUND: Tesla x Göndul ⚔️⚔️⚔️")
        print(
            f"✅ Tesla awakens the {self.volund_weapon}! [TRANSFORMATION: Göndul's magic fuses with Tesla's technology, creating the Super Automaton Beta - a suit that can manipulate space-time itself]")
        print(f"   Now has {len(self.abilities)} abilities!")
        return f"✅ Volund successfully activated for Nikola Tesla!"

    def apply_effect(self, effect):
        if effect == "gematria":
            self.gematria_zone_active = True
            return "🔬 [GEMATRIA ZONE] Gematria Zone activated! [TRANSFORMATION: Super Tesla Particles fill the area - Tesla can now float and teleport within this 9.63m cage]"
        elif effect == "teleport":
            if self.teleport_charges > 0 and self.gematria_zone_active:
                self.teleport_charges -= 1
                return f"⚡ [TESLA WARP] Tesla Warp! {self.teleport_charges} charges remaining [TRANSFORMATION: The Super Tesla Coil glows brightly as Tesla instantaneously repositions through space]"
            return "❌ Cannot teleport! [Gematria Zone must be active and charges remaining]"
        elif effect == "tesla_step":
            return "⚡ [TESLA STEP] Tesla moves with unpredictable three-dimensional steps! [TRANSFORMATION: Super Tesla Particles allow levitation and impossible movement patterns]"
        return ""


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

    def activate_volund(self, valkyrie):
        """Leonidas' Volund activation - Geirölul → Aspis Shield"""
        if valkyrie != Valkyrie.GEIROLUL:
            return f"❌ Leonidas can only bond with Geirölul!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Aspis Shield (アスピス)"

        self.divine_technique = {
            "name": "🛡️ PHALANX LAMBDA",
            "cost": 180,
            "dmg": (580, 750),
            "type": "damage",
            "desc": "🛡️ [PHALANX LAMBDA] Leonidas's ultimate technique - a straightforward charge that embodies the Spartan phalanx. [TRANSFORMATION: The shield becomes an unstoppable battering ram, embodying the spirit of Sparta]"
        }

        self.abilities = {
            '1': {"name": "🛡️ Spartan Kick", "cost": 15, "dmg": (140, 190), "type": "damage",
                  "desc": "🛡️ [SPARTAN KICK] The iconic Spartan kick."},
            '2': {"name": "🛡️ Aspis Shield", "cost": 25, "dmg": (150, 210), "type": "damage",
                  "desc": "🛡️ [ASPIS SHIELD] Leonidas uses his shield as both defense and offense. [TRANSFORMATION: The shield can be used for devastating bashes]"},
            '3': {"name": "🛡️ Saw Form", "cost": 40, "dmg": (220, 300), "type": "damage",
                  "effect": "saw_form",
                  "desc": "🛡️ [SAW FORM] Geirölul transforms into a saw blade. [TRANSFORMATION: The shield's center rises, revealing spinning blades - now a DIVINE SAW]"},
            '4': {"name": "🔨 Hammer Form", "cost": 50, "dmg": (290, 370), "type": "damage",
                  "effect": "hammer_form",
                  "desc": "🔨 [HAMMER FORM] Geirölul transforms into a massive hammer. [TRANSFORMATION: The shield splits into six legs that form a massive hammer head - now a DIVINE HAMMER]"},
            '5': {"name": "🛡️ Phalanx Lambda", "cost": 100, "dmg": (470, 610), "type": "damage",
                  "desc": "🛡️ [PHALANX LAMBDA] Leonidas's ultimate technique. [TRANSFORMATION: The Aletheia Sparta - the shield's true form revealed, charging forward with the weight of Spartan history]"}
        }

        print(f"\n⚔️⚔️⚔️ VOLUND: Leonidas x Geirölul ⚔️⚔️⚔️")
        print(
            f"✅ Leonidas awakens the {self.volund_weapon}! [TRANSFORMATION: Geirölul fuses with his shield, allowing it to transform between base, saw, and hammer forms]")
        print(f"   Now has {len(self.abilities)} abilities!")
        return f"✅ Volund successfully activated for Leonidas!"

    def apply_effect(self, effect):
        if effect == "saw_form":
            self.shield_form = "saw"
            return "🛡️ [SAW FORM] Shield transforms into Saw Form! [TRANSFORMATION: Spinning blades emerge from the shield's center - it can now tear through divine flesh]"
        elif effect == "hammer_form":
            self.shield_form = "hammer"
            return "🔨 [HAMMER FORM] Shield transforms into Hammer Form! [TRANSFORMATION: The shield splits and reforms into a massive divine hammer - capable of crushing gods]"
        return ""


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

        self.abilities = {
            '1': {"name": "⚔️ Quick Draw", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "⚔️ [QUICK DRAW] A quick sword draw."}
        }

    def activate_volund(self, valkyrie):
        """Soji's Volund activation - Skalmöld → Divine Katana"""
        if valkyrie != Valkyrie.SKALMOLD:
            return f"❌ Soji can only bond with Skalmöld!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Divine Katana (神器刀)"

        self.divine_technique = {
            "name": "⚔️ ENPI REITEN",
            "cost": 220,
            "dmg": (650, 850),
            "type": "damage",
            "desc": "⚔️ [ENPI REITEN] Soji's ultimate technique - over 80 sword techniques in rapid succession. [TRANSFORMATION: Every sword technique Soji ever conceived flows into one endless onslaught - past, present, and future techniques combined]"
        }

        self.abilities = {
            '1': {"name": "⚔️ Quick Draw", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "⚔️ [QUICK DRAW] A quick sword draw."},
            '2': {"name": "⚔️ Three-Stage Thrust", "cost": 40, "dmg": (220, 290), "type": "damage",
                  "desc": "⚔️ [THREE-STAGE THRUST] Three thrusts delivered in the time it takes most to deliver one. [TRANSFORMATION: Godspeed thrusts - three strikes in the span of one]"},
            '3': {"name": "👹 Demon Child Awakening", "cost": 50, "dmg": (0, 0), "type": "buff",
                  "effect": "demon_child",
                  "desc": "👹 [DEMON CHILD] Soji awakens the demon child within. [TRANSFORMATION: His heart pumps three times more blood - muscle cells awaken, eyes glow red]"},
            '4': {"name": "👹 Demon Child Release", "cost": 100, "dmg": (0, 0), "type": "buff",
                  "effect": "demon_release",
                  "desc": "👹 [DEMON RELEASE] Soji fully releases the demon child. [TRANSFORMATION: The demon within fully awakens - sclera turn red, dark red aura emanates, power beyond human limits]"},
            '5': {"name": "⚔️ Enpi Reiten", "cost": 150, "dmg": (550, 730), "type": "damage",
                  "desc": "⚔️ [ENPI REITEN] Eighty techniques flowing as one. [TRANSFORMATION: Over 80 sword techniques from the Ten'nen Rishin Style flow together in an endless onslaught]"},
            '6': {"name": "⚔️ Ryuubiken", "cost": 35, "dmg": (180, 250), "type": "damage",
                  "desc": "⚔️ [DRAGON TAIL'S SWORD] Soji swings his katana downward, then instantly changes direction and swings upward from a lower level, aiming for the opponent's torso. [TRANSFORMATION: The blade becomes like a dragon's tail - unpredictable and devastating]"},
            '7': {"name": "⚔️ Kisousandanzuki", "cost": 60, "dmg": (330, 410), "type": "damage",
                  "desc": "⚔️ [DEMON'S CLAW THREE STAGE THRUST] A crouched stance with katana held upside-down above the head. Performs Kisoutotsu with the mechanics of Three Stage Thrust. Surpasses 'godspeed' itself. [TRANSFORMATION: The Demon Child fully awakens - this attack pierces the boundary between humanity and divinity]"},
            '8': {"name": "⚔️ Tenshou Sandanzuki", "cost": 80, "dmg": (400, 520), "type": "damage",
                  "desc": "⚔️ [HEAVENLY FLIGHT THREE STAGE THRUST] An advanced version where Soji lunges forward and delivers three thrusts projected beyond the katana's range, targeting vital points. The same concept as Susano'o's Ama no Magaeshi. [TRANSFORMATION: The blade 'flies' - sword energy extends beyond physical reach to strike from impossible distances]"}
        }

        print(f"\n⚔️⚔️⚔️ VOLUND: Soji x Skalmöld ⚔️⚔️⚔️")
        print(
            f"✅ Soji awakens the {self.volund_weapon}! [TRANSFORMATION: Skalmöld draws out Soji's past, present, and future potential - all his sword ability condensed into this moment]")
        print(f"   Now has {len(self.abilities)} abilities!")
        return f"✅ Volund successfully activated for Soji Okita!"

    def apply_effect(self, effect):
        if effect == "demon_child":
            self.demon_child_active = True
            self.illness_effect += 10
            return f"👹 [DEMON CHILD] Demon Child awakened! Illness: {self.illness_effect}% [TRANSFORMATION: Blood pumps faster, muscles awaken - but the illness that killed him stirs as well]"
        elif effect == "demon_release":
            self.demon_child_release = True
            self.divine_mode = True
            self.divine_timer = 3
            return "👹 [DEMON RELEASE] DEMON CHILD RELEASE! Soji surpasses all limits! [TRANSFORMATION: The demon within fully awakens - eyes and aura turn crimson, power skyrocketing beyond humanity]"
        return ""


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

    def activate_volund(self, valkyrie):
        """Simo's Volund activation - Ráðgríðr → M28-30 Rifle"""
        if valkyrie != Valkyrie.RADGRIDR:
            return f"❌ Simo can only bond with Ráðgríðr!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "M28-30 Rifle (モシン・ナガンM28-30)"

        self.divine_technique = {
            "name": "❄️ UKONVASARA",
            "cost": 250,
            "dmg": (700, 900),
            "type": "damage",
            "desc": "❄️ [UKONVASARA] Simo's ultimate shot. He sacrifices his pancreas to fire a bullet of pure white death. [TRANSFORMATION: His pancreas becomes the bullet - the Hammer of Ukko, the supreme god of Finnish mythology, manifested as a sniper round]"
        }

        self.abilities = {
            '1': {"name": "❄️ Rifle Shot", "cost": 15, "dmg": (130, 180), "type": "damage",
                  "desc": "❄️ [RIFLE SHOT] A precise rifle shot."},
            '2': {"name": "❄️ White Death Shot", "cost": 25, "dmg": (170, 230), "type": "damage",
                  "desc": "❄️ [WHITE DEATH] A precision rifle shot from the White Death himself. [TRANSFORMATION: Each shot carries the chill of the Finnish winter]"},
            '3': {"name": "❄️ Camouflage", "cost": 20, "dmg": (0, 0), "type": "buff",
                  "effect": "camouflage",
                  "desc": "❄️ [CAMOUFLAGE] Simo disappears into the snow. 80% evasion for 2 turns. [TRANSFORMATION: He becomes one with the white landscape - invisible even to gods]"},
            '4': {"name": "💀 Isänmaalle (Kidney)", "cost": 40, "dmg": (270, 340), "type": "damage",
                  "organ": True,
                  "effect": "organ",
                  "desc": "💀 [ISÄNMAALLE] 'For the Fatherland' - Simo sacrifices a kidney to power a shot. [TRANSFORMATION: His kidney becomes the bullet - a piece of himself, offered for Finland]"},
            '5': {"name": "❄️ Ukonvasara", "cost": 150, "dmg": (600, 800), "type": "damage",
                  "desc": "❄️ [UKONVASARA] The hammer of the thunder god - Simo's ultimate shot. [TRANSFORMATION: The ultimate sacrifice - his pancreas becomes the Hammer of Ukko, the supreme god's weapon]"}
        }

        print(f"\n⚔️⚔️⚔️ VOLUND: Simo x Ráðgríðr ⚔️⚔️⚔️")
        print(
            f"✅ Simo awakens the {self.volund_weapon}! [TRANSFORMATION: Ráðgríðr fuses with his Mosin-Nagant - now a divine rifle that can trade organs for god-slaying bullets]")
        print(f"   Now has {len(self.abilities)} abilities!")
        return f"✅ Volund successfully activated for Simo Häyhä!"

    def apply_effect(self, effect):
        if effect == "camouflage":
            self.camouflage_active = True
            return "❄️ [CAMOUFLAGE] Camouflage activated! 80% evasion for 2 turns. [TRANSFORMATION: Simo becomes one with the snow - invisible to all]"
        elif effect == "organ":
            if len(self.organs_used) < len(self.organs):
                organ = self.organs[len(self.organs_used)]
                self.organs_used.append(organ)
                self.organ_sacrifice += 1
                damage_taken = 30 * self.organ_sacrifice
                self.take_damage(damage_taken)
                return f"💥 [ORGAN SACRIFICE] {organ} sacrificed! Takes {damage_taken} damage. Organs left: {len(self.organs) - len(self.organs_used)} [TRANSFORMATION: The {organ} becomes a divine bullet - a piece of himself, fired for his country]"
            return "❌ Cannot sacrifice more organs!"
        return ""


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

        self.abilities = {
            '1': {"name": "🐻 Axe Swing", "cost": 15, "dmg": (140, 190), "type": "damage",
                  "desc": "🐻 [AXE SWING] A basic axe swing."}
        }

    def activate_volund(self, valkyrie):
        """Kintoki's Volund activation - Skeggjöld → Divine Battle Axe"""
        if valkyrie != Valkyrie.SKEGGJOLD:
            return f"❌ Kintoki can only bond with Skeggjöld!"

        self.valkyrie = valkyrie
        self.valkyrie_index = valkyrie.index
        self.volund_active = True
        self.volund_weapon = "Divine Battle Axe (神器斧)"

        self.divine_technique = {
            "name": "🐻 GOLDEN LIGHTNING AXE - FURIOUS FLASH",
            "cost": 180,
            "dmg": (580, 750),
            "type": "damage",
            "desc": "🐻 [GOLDEN LIGHTNING AXE] Kintoki's ultimate technique. He channels the power of Raijin through his golden axe. [TRANSFORMATION: The Rune of Eirin activates, coating the axe in golden lightning - a double strike that flashes with the speed of thunder]"
        }

        self.abilities = {
            '1': {"name": "🐻 Axe Swing", "cost": 15, "dmg": (140, 190), "type": "damage",
                  "desc": "🐻 [AXE SWING] A basic axe swing."},
            '2': {"name": "🐻 Golden Axe Swing", "cost": 30, "dmg": (170, 230), "type": "damage",
                  "desc": "🐻 [GOLDEN AXE] A basic swing of Kintoki's golden axe. [TRANSFORMATION: The axe glows with golden light - the first hint of divine power]"},
            '3': {"name": "⚡ Raijin's Power", "cost": 40, "dmg": (220, 290), "type": "damage",
                  "desc": "⚡ [RAIJIN'S POWER] Kintoki channels the power of Raijin. [TRANSFORMATION: Lightning crackles around the axe - the thunder god's power awakens]"},
            '4': {"name": "✨ Rune of Eirin", "cost": 35, "dmg": (0, 0), "type": "buff", "effect": "rune",
                  "desc": "✨ [RUNE OF EIRIN] Kintoki activates the ancient Rune of Eirin. [TRANSFORMATION: The Dagaz rune on his palm glows - the primordial power of his ancestor awakens]"},
            '5': {"name": "🐻 Golden Lightning Axe", "cost": 100, "dmg": (470, 610), "type": "damage",
                  "effect": "flash",
                  "desc": "🐻 [GOLDEN LIGHTNING AXE] Kintoki transforms his axe into pure lightning. [TRANSFORMATION: The axe becomes living lightning - a double strike that flashes faster than the eye can follow]"}
        }

        print(f"\n⚔️⚔️⚔️ VOLUND: Kintoki x Skeggjöld ⚔️⚔️⚔️")
        print(
            f"✅ Kintoki awakens the {self.volund_weapon}! [TRANSFORMATION: Skeggjöld fuses with his axe - the weapon 'breaks' like a shell, revealing its true divine form]")
        print(f"   Now has {len(self.abilities)} abilities!")
        return f"✅ Volund successfully activated for Sakata Kintoki!"

    def apply_effect(self, effect):
        if effect == "rune":
            self.rune_of_eirin_active = True
            return "✨ [RUNE OF EIRIN] RUNE OF EIRIN ACTIVATED! [TRANSFORMATION: The ancient rune of the Primordial Gods glows on Kintoki's palm - golden light envelops him]"
        elif effect == "flash":
            if self.rune_of_eirin_active:
                return "🐻 [FURIOUS FLASH] GOLDEN LIGHTNING AXE - FURIOUS FLASH! Lightning erupts! [TRANSFORMATION: The axe becomes pure lightning - first strike sends a golden arc flying, second strike follows with electrified blade]"
            return "❌ [RUNE NEEDED] Need to activate Rune of Eirin first!"
        return ""


# ============================================================================
# ENEMY CREATION FUNCTIONS
# ============================================================================

def create_enemy_god_servant():
    abilities = {'1': {"name": "Divine Fist", "dmg": (40, 65), "cost": 15, "type": "damage"}}
    enemy = Enemy("Einherjar Soldier", "Divine Servant", 250, 150, abilities, 50, "Valhalla")
    enemy.ai_pattern = ['1']
    return enemy


def create_enemy_valkyrie_trainee():
    abilities = {'1': {"name": "Volund Strike", "dmg": (50, 80), "cost": 20, "type": "damage"}}
    enemy = Enemy("Valkyrie Trainee", "Sister of Battle", 280, 160, abilities, 40, "Valkyries")
    enemy.ai_pattern = ['1']
    return enemy


def create_enemy_demon():
    abilities = {
        '1': {"name": "Demon Claw", "dmg": (60, 90), "cost": 20, "type": "damage"},
        '2': {"name": "Hellfire", "dmg": (75, 110), "cost": 30, "type": "damage"}
    }
    enemy = Enemy("Helheim Demon", "Lesser Demon", 320, 170, abilities, 30, "Helheim")
    enemy.ai_pattern = ['2', '1']
    return enemy


def create_enemy_thor():
    abilities = {
        '1': {"name": "⚡ Mjolnir Strike", "dmg": (130, 190), "cost": 30, "type": "damage", "divine": True},
        '2': {"name": "⚡ Thor's Hammer", "dmg": (190, 260), "cost": 45, "type": "damage", "divine": True},
        '3': {"name": "⚡ Geirröd's Power", "dmg": (280, 370), "cost": 70, "type": "damage", "divine": True}
    }
    enemy = Enemy("Thor", "God of Thunder", 1250, 400, abilities, 1, "Norse Gods", 1,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_zeus():
    abilities = {
        '1': {"name": "👊 Divine Punch", "dmg": (160, 220), "cost": 35, "type": "damage", "divine": True},
        '2': {"name": "⚡ Meteor Jab", "dmg": (220, 290), "cost": 50, "type": "damage", "divine": True},
        '3': {"name": "👴 True God's Form", "dmg": (320, 410), "cost": 80, "type": "damage", "divine": True}
    }
    enemy = Enemy("Zeus", "Godfather", 1300, 450, abilities, 2, "Greek Gods", 2,
                  [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_poseidon():
    abilities = {
        '1': {"name": "🌊 Trident Thrust", "dmg": (160, 220), "cost": 35, "type": "damage", "divine": True},
        '2': {"name": "🌊 40-Day Flood", "dmg": (350, 450), "cost": 80, "type": "damage", "divine": True}
    }
    enemy = Enemy("Poseidon", "God of Seas", 1200, 410, abilities, 3, "Greek Gods", 3,
                  [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['2', '1']
    return enemy


def create_enemy_heracles():
    abilities = {
        '1': {"name": "🦁 Nemean Lion", "dmg": (170, 230), "cost": 30, "type": "damage", "divine": True},
        '2': {"name": "🐍 Lernaean Hydra", "dmg": (190, 250), "cost": 35, "type": "damage", "divine": True},
        '3': {"name": "🐕 Cerberus", "dmg": (400, 500), "cost": 100, "type": "damage", "divine": True}
    }
    enemy = Enemy("Heracles", "God of Fortitude", 1350, 430, abilities, 4, "Greek Gods", 4,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_shiva():
    abilities = {
        '1': {"name": "🔥 Four Arms Strike", "dmg": (180, 240), "cost": 35, "type": "damage", "divine": True},
        '2': {"name": "🔥 Tandava", "dmg": (280, 360), "cost": 60, "type": "damage", "divine": True},
        '3': {"name": "🔥 Deva Loka", "dmg": (400, 500), "cost": 90, "type": "damage", "divine": True}
    }
    enemy = Enemy("Shiva", "God of Destruction", 1280, 400, abilities, 5, "Hindu Gods", 5,
                  [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_zerofuku():
    abilities = {
        '1': {"name": "🎋 Misery Cleaver", "dmg": (150, 210), "cost": 25, "type": "damage", "divine": True},
        '2': {"name": "🌪️ Storm Form", "dmg": (400, 500), "cost": 100, "type": "damage", "divine": True},
        '3': {"name": "🎋 Seven Lucky Gods Union", "dmg": (470, 590), "cost": 120, "type": "damage", "divine": True}
    }
    enemy = Enemy("Zerofuku", "God of Misfortune", 1150, 410, abilities, 6, "Seven Lucky Gods", 6,
                  [Realm.GODLY_STRENGTH])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_hajun():
    abilities = {
        '1': {"name": "👹 Demon Strike", "dmg": (200, 270), "cost": 35, "type": "damage", "divine": True},
        '2': {"name": "👹 Helheim's Wrath", "dmg": (300, 380), "cost": 55, "type": "damage", "divine": True},
        '3': {"name": "👹 Demon King's Wrath", "dmg": (500, 650), "cost": 100, "type": "damage", "divine": True}
    }
    enemy = Enemy("Hajun", "Demon King", 1600, 450, abilities, 6, "Helheim", 6,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE, Realm.GODLY_WILL], soul_dark=True)
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_hades():
    abilities = {
        '1': {"name": "💀 Bident Thrust", "dmg": (170, 230), "cost": 25, "type": "damage", "divine": True},
        '2': {"name": "💀 Ichor-Eos", "dmg": (400, 500), "cost": 80, "type": "damage", "divine": True},
        '3': {"name": "⚔️ Ichor Desmos", "dmg": (600, 780), "cost": 200, "type": "damage", "divine": True}
    }
    enemy = Enemy("Hades", "God of Underworld", 1400, 460, abilities, 7, "Greek Gods", 7,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_beelzebub():
    abilities = {
        '1': {"name": "🦟 Palmyra", "dmg": (180, 240), "cost": 30, "type": "damage", "divine": True},
        '2': {"name": "🦟 Sorath Resh", "dmg": (430, 530), "cost": 85, "type": "damage", "divine": True},
        '3': {"name": "🦟 CHAOS", "dmg": (550, 700), "cost": 150, "type": "damage", "divine": True}
    }
    enemy = Enemy("Beelzebub", "Lord of the Flies", 1250, 450, abilities, 8, "Gods", 8,
                  [Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_apollo():
    abilities = {
        '1': {"name": "🎯 Silver Bow Shot", "dmg": (160, 220), "cost": 25, "type": "damage", "divine": True},
        '2': {"name": "🎯 Apollo Epicurious", "dmg": (270, 340), "cost": 55, "type": "damage", "divine": True},
        '3': {"name": "🎯 Argyrotoxos", "dmg": (470, 600), "cost": 100, "type": "damage", "divine": True}
    }
    enemy = Enemy("Apollo", "God of the Sun", 1180, 440, abilities, 9, "Greek Gods", 9,
                  [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_susanoo():
    abilities = {
        '1': {"name": "🌪️ Storm's Wrath", "dmg": (180, 240), "cost": 30, "type": "damage", "divine": True},
        '2': {"name": "🌪️ Ama no Magaeshi", "dmg": (330, 410), "cost": 60, "type": "damage", "divine": True},
        '3': {"name": "⚔️ Musouken", "dmg": (550, 700), "cost": 150, "type": "damage", "divine": True}
    }
    enemy = Enemy("Susano'o no Mikoto", "God of Storms", 1280, 450, abilities, 10, "Japanese Gods", 10,
                  [Realm.GODLY_SPEED, Realm.GODLY_STRENGTH])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_loki():
    abilities = {
        '1': {"name": "🎭 Illusion Strike", "dmg": (150, 210), "cost": 25, "type": "damage", "divine": True},
        '2': {"name": "🎭 Trickster's Gambit", "dmg": (330, 410), "cost": 70, "type": "damage", "divine": True},
        '3': {"name": "🎭 HEIMSKRINGLA", "dmg": (550, 700), "cost": 200, "type": "damage", "divine": True}
    }
    enemy = Enemy("Loki", "God of Mischief", 1220, 440, abilities, 11, "Norse Gods", 11,
                  [Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_odin():
    abilities = {
        '1': {"name": "🔱 Gungnir Thrust", "dmg": (200, 270), "cost": 35, "type": "damage", "divine": True},
        '2': {"name": "🔮 Vindsskuggr", "dmg": (370, 470), "cost": 70, "type": "damage", "divine": True},
        '3': {"name": "🔱 Absolute Certainty", "dmg": (550, 700), "cost": 150, "type": "damage", "divine": True}
    }
    enemy = Enemy("Odin", "All-Father", 1500, 470, abilities, 12, "Norse Gods", 12,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_lu_bu():
    abilities = {
        '1': {"name": "🏹 Sky Piercer", "dmg": (160, 220), "cost": 30, "type": "damage"},
        '2': {"name": "🐎 Red Hare Charge", "dmg": (190, 260), "cost": 35, "type": "damage"},
        '3': {"name": "🏹 Sky Eater", "dmg": (430, 550), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Lü Bu", "Flying General", 1250, 380, abilities, 1, "Humanity", 1,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_WILL])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_adam():
    abilities = {
        '1': {"name": "👁️ Divine Replication", "dmg": (150, 210), "cost": 30, "type": "damage"},
        '2': {"name": "👁️ Meteor Jab", "dmg": (190, 260), "cost": 40, "type": "damage"},
        '3': {"name": "👁️ Time Transcending Fist", "dmg": (450, 600), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Adam", "Father of Humanity", 1300, 390, abilities, 2, "Humanity", 2,
                  [Realm.GODLY_SPEED, Realm.GODLY_WILL])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_kojiro():
    abilities = {
        '1': {"name": "⚔️ Tsubame Gaeshi", "dmg": (200, 270), "cost": 40, "type": "damage"},
        '2': {"name": "⚔️ Sōenzanko", "dmg": (430, 550), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Kojiro Sasaki", "History's Greatest Loser", 1180, 370, abilities, 3, "Humanity", 3,
                  [Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['2', '1']
    return enemy


def create_enemy_jack():
    abilities = {
        '1': {"name": "🗡️ Dear Jane", "dmg": (130, 190), "cost": 25, "type": "damage"},
        '2': {"name": "🎪 Dear God", "dmg": (430, 550), "cost": 120, "type": "damage"}
    }
    enemy = Enemy("Jack the Ripper", "Whitechapel Demon", 1150, 350, abilities, 4, "Humanity", 4,
                  [Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['2', '1']
    return enemy


def create_enemy_raiden():
    abilities = {
        '1': {"name": "💪 Muscle Control", "dmg": (160, 220), "cost": 25, "type": "damage"},
        '2': {"name": "💪 Yatagarasu", "dmg": (470, 630), "cost": 120, "type": "damage"}
    }
    enemy = Enemy("Raiden Tameemon", "Greatest Sumo Wrestler", 1400, 370, abilities, 5, "Humanity", 5,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE])
    enemy.ai_pattern = ['2', '1']
    return enemy


def create_enemy_buddha():
    abilities = {
        '1': {"name": "🧘 Six Realms Staff", "dmg": (180, 250), "cost": 35, "type": "damage"},
        '2': {"name": "👁️ Future Sight", "dmg": (0, 0), "cost": 40, "type": "buff"},
        '3': {"name": "🌸 Mahaparinirvana", "dmg": (500, 650), "cost": 150, "type": "damage"}
    }
    enemy = Enemy("Buddha", "Enlightened One", 1250, 390, abilities, 6, "Humanity", 6,
                  [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL])
    enemy.ai_pattern = ['3', '2', '1']
    return enemy


def create_enemy_qin():
    abilities = {
        '1': {"name": "👑 Chiyou Style", "dmg": (240, 320), "cost": 45, "type": "damage"},
        '2': {"name": "👑 Emperor's Will", "dmg": (470, 610), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Qin Shi Huang", "First Emperor", 1280, 380, abilities, 7, "Humanity", 7,
                  [Realm.GODLY_TECHNIQUE, Realm.GODLY_WILL])
    enemy.ai_pattern = ['2', '1']
    return enemy


def create_enemy_tesla():
    abilities = {
        '1': {"name": "⚡ PPP", "dmg": (160, 220), "cost": 25, "type": "damage"},
        '2': {"name": "⚡ PPPX", "dmg": (500, 650), "cost": 120, "type": "damage"}
    }
    enemy = Enemy("Nikola Tesla", "Greatest Inventor", 1220, 390, abilities, 8, "Humanity", 8,
                  [Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['2', '1']
    return enemy


def create_enemy_leonidas():
    abilities = {
        '1': {"name": "🛡️ Spartan Kick", "dmg": (170, 230), "cost": 30, "type": "damage"},
        '2': {"name": "🛡️ Phalanx Lambda", "dmg": (470, 610), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Leonidas", "King of Sparta", 1350, 380, abilities, 9, "Humanity", 9,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_ENDURANCE])
    enemy.ai_pattern = ['2', '1']
    return enemy


def create_enemy_okita():
    abilities = {
        '1': {"name": "⚔️ Three-Stage Thrust", "dmg": (220, 290), "cost": 40, "type": "damage"},
        '2': {"name": "⚔️ Enpi Reiten", "dmg": (550, 730), "cost": 150, "type": "damage"}
    }
    enemy = Enemy("Soji Okita", "Captain of Shinsengumi", 1250, 370, abilities, 10, "Humanity", 10,
                  [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['2', '1']
    return enemy


def create_enemy_simo():
    abilities = {
        '1': {"name": "❄️ White Death", "dmg": (170, 230), "cost": 25, "type": "damage"},
        '2': {"name": "❄️ Ukonvasara", "dmg": (600, 800), "cost": 150, "type": "damage"}
    }
    enemy = Enemy("Simo Häyhä", "White Death", 1200, 360, abilities, 11, "Humanity", 11,
                  [Realm.GODLY_SPEED, Realm.GODLY_TECHNIQUE])
    enemy.ai_pattern = ['2', '1']
    return enemy


def create_enemy_kintoki():
    abilities = {
        '1': {"name": "🐻 Golden Axe", "dmg": (170, 230), "cost": 30, "type": "damage"},
        '2': {"name": "🐻 Furious Flash", "dmg": (470, 610), "cost": 100, "type": "damage"}
    }
    enemy = Enemy("Sakata Kintoki", "Golden Hero", 1300, 380, abilities, 12, "Humanity", 12,
                  [Realm.GODLY_STRENGTH, Realm.GODLY_WILL])
    enemy.ai_pattern = ['2', '1']
    return enemy


# ============================================================================
# SURVIVAL MODE
# ============================================================================

class SurvivalMode:
    """Endless survival mode with increasing difficulty"""

    def __init__(self, game):
        self.game = game
        self.wave = 0
        self.score = 0
        self.party = []
        self.consecutive_wins = 0
        self.boss_waves = [10, 20, 30, 50, 75, 100]

    def run(self):
        """Run the survival mode"""
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

        activate_volund_for_party(self.party, self.game)

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

    def generate_wave(self):
        """Generate enemies for the current wave"""
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
        """Save high score to file"""
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
    """Fight all gods in sequence"""

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
        """Run boss rush mode"""
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

        activate_volund_for_party(self.party, self.game)

        print(f"\nYour party: {', '.join([c.name for c in self.party])}")
        print("This party will fight ALL 13 bosses. There is no changing members.")
        confirm = input("\nAre you ready to begin? (y/n): ").lower()
        if confirm != 'y':
            print("Returning to menu...")
            return

        current_boss = 0
        victory = False

        for i, (boss_name, boss_func) in enumerate(self.bosses):
            current_boss = i + 1
            total_bosses = len(self.bosses)

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
        input("\nPress Enter to return to menu...")

    def save_record(self, bosses_defeated):
        """Save boss rush record"""
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
    """Fight through all 26 fighters in random order"""

    def __init__(self, game):
        self.game = game

    def run(self):
        """Run gauntlet mode"""
        clear_screen()
        print("\n" + "=" * 110)
        slow_print("⚔️⚔️⚔️ GAUNTLET MODE ⚔️⚔️⚔️", 0.03)
        print("=" * 110)
        slow_print("Fight through ALL 26 fighters in random order!", 0.02)
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

        activate_volund_for_character(champion, self.game)

        print(f"\nYour champion: {champion.name}")
        print(f"They will face ALL 26 fighters in sequence!")
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

        victories = 0

        for i, (fighter_name, fighter_func) in enumerate(fighter_creators):
            current = i + 1
            total = len(fighter_creators)

            clear_screen()
            print("\n" + "🔥" * 110)
            slow_print(f"🔥 FIGHT {current}/{total}: {fighter_name} 🔥", 0.05)
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
                print(f"\n💀 Defeated by {fighter_name} at fight {current}/{total}")
                break

        print("\n" + "=" * 110)
        if victories == total:
            slow_print("🏆🏆🏆 PERFECT GAUNTLET! ALL 26 DEFEATED! 🏆🏆🏆", 0.04)
        else:
            slow_print(f"📊 GAUNTLET COMPLETED: {victories}/{total} fighters defeated", 0.03)
        print("=" * 110)

        self.save_record(champion.name, victories, total)
        input("\nPress Enter to return to menu...")

    def save_record(self, champion_name, victories, total):
        """Save gauntlet record"""
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
# CHAOS MODE
# ============================================================================

class ChaosMode:
    """Random chaos - everything is randomized"""

    def __init__(self, game):
        self.game = game

    def run(self):
        """Run chaos mode"""
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

        while True:
            rounds += 1

            clear_screen()
            print("\n" + "🌀" * 110)
            slow_print(f"🌀 CHAOS ROUND {rounds} 🌀", 0.05)
            print("🌀" * 110)

            party_size = random.randint(1, 4)
            party = []

            available_chars = [c for c in self.game.all_characters if c.is_alive()]
            if not available_chars:
                print("No characters available! Resetting...")
                self.game.rest()
                available_chars = self.game.all_characters

            random.shuffle(available_chars)
            for i in range(min(party_size, len(available_chars))):
                char = available_chars[i]
                if random.random() < 0.3:
                    char.max_hp = int(char.max_hp * random.uniform(0.5, 2.0))
                    char.hp = char.max_hp
                party.append(char)

            for champion in party:
                if champion.name in self.game.canon_pairings and random.random() < 0.5:
                    if activate_volund_for_character(champion, self.game):
                        print(f"🌀 [CHAOS] Chaos grants Volund to {champion.name}!")

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
        input("Press Enter to return to menu...")

    def random_event(self, party, enemies):
        """Random event before battle"""
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
             lambda: [setattr(p, 'defending', True) for p in party]),

            ("👁️ ADAM'S EYES GLOW! Copy chance doubled this battle!",
             lambda: [setattr(p, 'temp_copy_boost', True) for p in party if p.name == "Adam"]),

            ("💢 BERSERKER RAGE! Everyone deals double damage but takes double damage!",
             None),

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
        """Random reward after victory"""
        rewards = [
            ("💪 POWER SURGE", lambda p: setattr(p, 'max_hp', int(p.max_hp * 1.1)) or p.heal(p.max_hp)),
            ("⚡ ENERGY WELL",
             lambda p: setattr(p, 'max_energy', int(p.max_energy * 1.1)) or setattr(p, 'energy', p.max_energy)),
            ("👁️ TECHNIQUE MASTERY", lambda p: setattr(p, 'copy_count', min(p.max_copy, p.copy_count + 1)) if hasattr(p,
                                                                                                                      'copy_count') else None),
            ("🩸 BLOOD OF THE GODS", lambda p: p.heal(200)),
            ("✨ DIVINE AWAKENING", lambda p: setattr(p, 'divine_mode', True) or setattr(p, 'divine_timer', 3)),
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
    """Practice against any fighter"""

    def __init__(self, game):
        self.game = game

    def run(self):
        """Run training mode"""
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
                party = self.game.select_party(3)
                if not party:
                    continue

                activate_volund_for_party(party, self.game)

                self.game.rest()

                self.game.battle(enemies, party)
                input("\nPress Enter to continue...")

    def custom_match(self):
        """Create a custom match"""
        print("\n" + "=" * 110)
        slow_print("⚙️ CUSTOM MATCH SETUP ⚙️", 0.03)
        print("=" * 110)

        print("\nChoose your party size (1-4):")
        try:
            party_size = int(input("> ").strip())
            party_size = max(1, min(4, party_size))
        except:
            party_size = 3

        party = self.game.select_party(party_size)
        if not party:
            return

        activate_volund_for_party(party, self.game)

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

        self.game.rest()

        print(f"\nCustom Match: Your {party_size} vs {enemy_size} enemies")
        input("Press Enter to begin!")
        self.game.battle(enemies, party)
        input("\nPress Enter to continue...")


# ============================================================================
# MAIN GAME CLASS - UPDATED WITH INDEX-BASED PAIRINGS
# ============================================================================

class RagnarokGame:
    def __init__(self, load_saved=True):
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
            "Jack the Ripper": {"valkyrie_name": "Hlökk", "valkyrie_enum": "HLOKK", "valkyrie_index": 10},
            "Raiden Tameemon": {"valkyrie_name": "Thrud", "valkyrie_enum": "THRUD", "valkyrie_index": 2},
            "Qin Shi Huang": {"valkyrie_name": "Alvitr", "valkyrie_enum": "ALVITR", "valkyrie_index": 9},
            "Nikola Tesla": {"valkyrie_name": "Göndul", "valkyrie_enum": "GONDUL", "valkyrie_index": 8},
            "Leonidas": {"valkyrie_name": "Geirölul", "valkyrie_enum": "GEIROLUL", "valkyrie_index": 4},
            "Soji Okita": {"valkyrie_name": "Skalmöld", "valkyrie_enum": "SKALMOLD", "valkyrie_index": 5},
            "Simo Häyhä": {"valkyrie_name": "Ráðgríðr", "valkyrie_enum": "RADGRIDR", "valkyrie_index": 7},
            "Sakata Kintoki": {"valkyrie_name": "Skeggjöld", "valkyrie_enum": "SKEGGJOLD", "valkyrie_index": 11}
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

    # ============================================================================
    # BATTLE METHODS
    # ============================================================================

    def enemy_turn(self, enemy):
        """Enemy turn with Adam copy mechanics integration"""
        if not enemy.is_alive():
            return
        if not any(c.is_alive() for c in self.party):
            return

        if enemy.stunned:
            self.add_log(f"⚡ [STUNNED] {enemy.name} is stunned!")
            enemy.stunned = False
            return
        if enemy.bound:
            self.add_log(f"⚪ [BOUND] {enemy.name} is bound!")
            enemy.bound = False
            return

        enemy.energy = min(enemy.max_energy, enemy.energy + 15)

        adam = None
        for char in self.party:
            if char.name == "Adam" and char.is_alive() and hasattr(char, 'attempt_copy'):
                adam = char
                break

        if hasattr(enemy, 'ai_pattern') and enemy.ai_pattern:
            for pattern_key in enemy.ai_pattern:
                if pattern_key in enemy.abilities:
                    abil = enemy.abilities[pattern_key]
                    if enemy.energy >= abil.get("cost", 25):
                        enemy.energy -= abil.get("cost", 25)
                        targets = [c for c in self.party if c.is_alive()]
                        if targets:
                            t = random.choice(targets)
                            dmg = random.randint(abil["dmg"][0], abil["dmg"][1])
                            mult, _ = t.get_damage_multiplier()
                            dmg = int(dmg * mult)
                            if t.defending:
                                dmg = int(dmg * 0.5)
                                t.defending = False
                            t.take_damage(dmg)

                            self.add_log(f"{enemy.name} uses {abil['name']} for {dmg} damage!")

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
                                    self.add_log(f"👁️ {copy_result}")

                                elif random.random() < 0.1 and adam.technique_view_count.get(abil['name'], 0) > 0:
                                    views = adam.technique_view_count[abil['name']]
                                    chance = 40 + (views * 15)
                                    if chance > 95:
                                        chance = 95
                                    self.add_log(
                                        f"👁️ [STUDYING] Adam studies {abil['name']}... ({chance}% copy chance)")

                            return

            first_abil = list(enemy.abilities.values())[0]
            if enemy.energy >= first_abil.get("cost", 25):
                enemy.energy -= first_abil.get("cost", 25)
                targets = [c for c in self.party if c.is_alive()]
                if targets:
                    t = random.choice(targets)
                    dmg = random.randint(first_abil["dmg"][0], first_abil["dmg"][1])
                    mult, _ = t.get_damage_multiplier()
                    dmg = int(dmg * mult)
                    if t.defending:
                        dmg = int(dmg * 0.5)
                        t.defending = False
                    t.take_damage(dmg)
                    self.add_log(f"{enemy.name} uses {first_abil['name']} for {dmg} damage!")

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
                            self.add_log(f"👁️ {copy_result}")

    def use_ability(self, character):
        """Use an ability - enhanced for Adam's copy stats and Jack's limited weapons"""
        while True:
            print(f"\n" + "=" * 110)
            slow_print(f"✦✦✦ {character.name} [{character.title}] ✦✦✦", 0.03)
            print("=" * 110)
            print(f"❤️ HP: {character.hp}/{character.max_hp}  ⚡ Energy: {character.energy}/{character.max_energy}")
            if character.valkyrie:
                print(f"⚔️ VOLUND: {character.valkyrie.icon_name} - {character.volund_weapon}")
            if character.active_realm != Realm.NONE:
                print(f"🔮 REALM: {character.active_realm.value}")

            if character.name == "Adam" and hasattr(character, 'copy_count'):
                print(f"👁️ Copied: {character.copy_count}/{character.max_copy} | Blindness: {character.blindness}")

            if character.name == "Jack the Ripper" and hasattr(character, 'get_weapon_status'):
                character.get_weapon_status()

            print("-" * 110)

            available = {}
            for key, abil in character.abilities.items():
                cost = abil.get("cost", 0)
                if character.energy >= cost:
                    if "uses_left" in abil and abil["uses_left"] <= 0:
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
                for key in sorted(damage_abilities.keys(), key=lambda x: int(x)):
                    abil = damage_abilities[key]
                    dmg = abil["dmg"]
                    dmg_str = f"{dmg[0]}-{dmg[1]} DMG" if dmg != (0, 0) else ""
                    views = f" [Seen:{abil['views']}x]" if "views" in abil else ""

                    uses_str = ""
                    if "uses_left" in abil:
                        uses_str = f" [{abil['uses_left']}/{abil['max_uses']}]"

                    print(f"    {key}. {abil['name']:35} | {abil['cost']}E | {dmg_str}{views}{uses_str}")

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

            if character.divine_technique and character.energy >= character.divine_technique['cost']:
                dt = character.divine_technique
                print(f"\n  ✨ DIVINE TECHNIQUE:")
                print(f"    99. {dt['name']} | {dt['cost']}E | {dt['dmg'][0]}-{dt['dmg'][1]} DMG")

            print("\n" + "🎮 COMMANDS:")
            print("  0. Describe Ability (does NOT consume turn)")
            print("  00. Activate Divine Realm (if available)")
            if not character.volund_active and character.name in self.canon_pairings:
                print("  000. Activate Volund (does NOT consume turn)")

            if character.name == "Adam" and hasattr(character, 'get_copy_stats'):
                print("  98. View Copy Statistics (does NOT consume turn)")

            if character.name == "Jack the Ripper" and hasattr(character, 'get_weapon_status'):
                print("  97. 📦 Check Weapon Supplies (does NOT consume turn)")

            print("  0000. Skip Turn (+15E)")
            print("  00000. Back")
            print("-" * 110)

            choice = input("> ").strip()

            if choice == '00000':
                return False
            elif choice == '0000':
                self.add_log(f"{character.name} skips turn. +15 Energy")
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
                            self.add_log(character.activate_realm(character.realms[idx]))
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
                        slow_print(abil['desc'], 0.02)
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
                'cost']:
                character.energy -= character.divine_technique['cost']
                target = self.select_target()
                if target:
                    dmg = random.randint(character.divine_technique['dmg'][0], character.divine_technique['dmg'][1])
                    mult, buffs = character.get_damage_multiplier()
                    dmg = int(dmg * mult)
                    target.take_damage(dmg)

                    print("\n" + "✨" * 55)
                    slow_print(f"✨✨✨ {character.divine_technique['name']} ✨✨✨", 0.05)
                    print("✨" * 55)

                    self.add_log(f"{character.name} unleashes DIVINE TECHNIQUE for {dmg} damage!")

                return True
            elif choice in available:
                ability = available[choice]

                if hasattr(character, 'use_ability'):
                    if not character.use_ability(choice):
                        return False

                character.energy -= ability["cost"]

                if ability.get("type") == "damage":
                    target = self.select_target()
                    if target:
                        dmg = random.randint(ability["dmg"][0], ability["dmg"][1])
                        mult, buffs = character.get_damage_multiplier()
                        dmg = int(dmg * mult)
                        if ability.get("armor_break"):
                            self.add_log("⚔️ Armor break!")
                        target.take_damage(dmg)
                        self.add_log(f"{character.name} uses {ability['name']} for {dmg} damage!")

                        if character.name == "Heracles" and ability.get("labor"):
                            self.add_log(character.use_labor(ability["labor"]))

                elif ability.get("type") in ["buff", "heal", "defense", "utility"]:
                    if "effect" in ability:
                        if hasattr(character, 'apply_effect'):
                            result = character.apply_effect(ability["effect"])
                            if result:
                                self.add_log(result)
                            else:
                                self.add_log(f"{character.name} uses {ability['name']}!")
                    else:
                        self.add_log(f"{character.name} uses {ability['name']}!")

                return True
            else:
                print("❌ Invalid choice.")
                return False

    def select_target(self, allies=False):
        """Select a target"""
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
            print(f"  {i + 1}. {t.name} ({t.hp}/{t.max_hp} HP)")

        while True:
            try:
                choice = int(input("> ")) - 1
                if 0 <= choice < len(targets):
                    return targets[choice]
                print("❌ Invalid target.")
            except:
                print("❌ Enter a number.")

    def display_health_bars(self):
        """Display health bars with Adam copy info"""
        print("\n" + "=" * 110)
        print("✨✨✨ YOUR CHAMPIONS ✨✨✨")
        print("-" * 110)
        for member in self.party:
            if member.is_alive():
                bar_len = 40
                filled = int(bar_len * member.hp / member.max_hp)
                bar = "█" * filled + "░" * (bar_len - filled)
                status = []
                if member.divine_mode:
                    status.append("✨DIVINE")
                if member.volund_active:
                    status.append("⚔️VOLUND")
                if member.active_realm != Realm.NONE:
                    realm_icons = {
                        Realm.GODLY_SPEED: "🔵",
                        Realm.GODLY_STRENGTH: "🔴",
                        Realm.GODLY_ENDURANCE: "🟢",
                        Realm.GODLY_TECHNIQUE: "🩷",
                        Realm.GODLY_WILL: "🟣"
                    }
                    status.append(f"{realm_icons.get(member.active_realm, '')}REALM")

                if member.name == "Adam" and hasattr(member, 'copy_count') and member.copy_count > 0:
                    status.append(f"👁️{member.copy_count}")
                if member.name == "Adam" and member.blindness > 0:
                    status.append(f"🕶️{member.blindness}")

                status_str = " | ".join(status) if status else ""
                weapon_info = f" [{member.volund_weapon}]" if member.volund_weapon else ""
                print(
                    f"{member.name}{weapon_info:25} |{bar}| {member.hp:3}/{member.max_hp:3} HP {member.energy:3}E  {status_str}")

        print("\n" + "=" * 110)
        print("💀💀💀 ENEMIES 💀💀💀")
        print("-" * 110)
        for enemy in self.enemies:
            if enemy.is_alive():
                bar_len = 40
                filled = int(bar_len * enemy.hp / enemy.max_hp)
                bar = "█" * filled + "░" * (bar_len - filled)
                debuff = []
                if enemy.stunned:
                    debuff.append("⚡STUN")
                if enemy.bound:
                    debuff.append("⚪BOUND")
                debuff_str = " | ".join(debuff) if debuff else ""
                rank_display = f" [Rank:{enemy.rank}]" if hasattr(enemy, 'rank') else ""
                affil = f" [{enemy.affiliation}]" if enemy.affiliation else ""
                print(f"{enemy.name:25} |{bar}| {enemy.hp:3}/{enemy.max_hp:3} HP{affil}{rank_display} {debuff_str}")
        print("=" * 110)

    def add_log(self, message):
        """Add message to battle log"""
        self.battle_log.append(f"[T{self.turn_count}] {message}")
        print(f"[T{self.turn_count}] ", end='')
        slow_print(message, 0.02)

    def select_party(self, max_size=3, faction=None):
        """Select party members - can choose humans, gods, or all"""
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
                copy_info = f" [👁️{char.copy_count}]" if char.name == "Adam" and hasattr(char,
                                                                                         'copy_count') and char.copy_count > 0 else ""
                print(
                    f"  {i + 1}. {char.name}{affil}{weapon_info}{valkyrie_info}{copy_info} - {char.hp}/{char.max_hp} HP")
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
            return self.select_party(max_size, "Gods")
        elif choice == 'h':
            return self.select_party(max_size, "Humans")
        elif choice == 'a':
            return available[:max_size]

        selected = []
        while len(selected) < max_size:
            try:
                idx = int(input(f"Champion {len(selected) + 1}: ")) - 1
                if 0 <= idx < len(available):
                    char = available[idx]
                    if char not in selected:
                        selected.append(char)
                        print(f"  ✓ Added {char.name}")
                    else:
                        print("  ✗ Already selected")
                else:
                    print("  ✗ Invalid number")
            except:
                break

        return selected if selected else available[:max_size]

    def battle(self, enemies, party=None):
        """Battle system with Adam copy mechanics"""
        self.enemies = enemies
        self.party = party if party else self.select_party()
        if not self.party:
            return False

        self.turn_count = 0
        self.battle_log = []

        print("\n" + "=" * 110)
        slow_print("⚔️⚔️⚔️ RAGNAROK BATTLE ⚔️⚔️⚔️", 0.04)
        print("=" * 110)
        print(f"✨ CHAMPIONS: {', '.join([c.name for c in self.party])}")
        print(f"💀 ENEMIES: {', '.join([e.name for e in self.enemies])}")
        print("=" * 110)
        time.sleep(BATTLE_START_DELAY)

        while True:
            self.turn_count += 1
            print(f"\n{'=' * 55} TURN {self.turn_count} {'=' * 55}")

            for char in self.party:
                if char.is_alive():
                    char.energy = min(char.max_energy, char.energy + 20)
                    action = False
                    while not action:
                        self.display_health_bars()
                        action = self.use_ability(char)
                    if not any(e.is_alive() for e in self.enemies):
                        break

            if not any(e.is_alive() for e in self.enemies):
                break
            if not any(c.is_alive() for c in self.party):
                break

            print("\n" + "💀💀💀 ENEMY PHASE 💀💀💀")
            for enemy in self.enemies:
                if enemy.is_alive():
                    self.enemy_turn(enemy)

            self.cleanup()

        self.display_health_bars()

        if any(e.is_alive() for e in self.enemies):
            print("\n" + "=" * 110)
            slow_print("💀💀💀 DEFEAT... 💀💀💀", 0.05)
            print("=" * 110)
            return False
        else:
            print("\n" + "=" * 110)
            slow_print("✨✨✨ VICTORY! ✨✨✨", 0.05)
            print("=" * 110)
            self.victories += 1
            self.total_kills += len([e for e in self.enemies if not e.is_alive()])

            if self.adam.is_alive() and self.adam.copy_count > 0:
                print(f"\n👁️ [ADAM] Adam ends the battle with {self.adam.copy_count} copied techniques!")

            return True

    def cleanup(self):
        """Clean up after turn"""
        for c in self.party + self.enemies:
            c.defending = False
            if hasattr(c, 'realm_timer') and c.realm_timer > 0:
                c.realm_timer -= 1
                if c.realm_timer <= 0:
                    c.active_realm = Realm.NONE
            if hasattr(c, 'divine_mode') and c.divine_mode:
                if hasattr(c, 'divine_timer'):
                    c.divine_timer -= 1
                    if c.divine_timer <= 0:
                        c.divine_mode = False
            if c.stunned and random.random() < 0.3:
                c.stunned = False
            if c.bound and random.random() < 0.3:
                c.bound = False

    # ============================================================================
    # REST METHOD
    # ============================================================================

    def rest(self):
        """Rest and recover all characters - with Adam reset"""
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

            if char.name == "Adam":
                char.blindness = 0
                char.death_activated = False
                print(f"  ✦ [ADAM] {char.name} recovers sight! Copied techniques: {char.copy_count}")
            elif char.name == "Kojiro Sasaki":
                char.scan_progress = 0
                char.simulations_complete = 0
                char.weapon_broken = False
                char.dual_wielding = False
            elif char.name == "Heracles":
                char.labors_used = 0
                char.tattoo_progress = 0
                char.cerberus_active = False
            elif char.name == "Raiden Tameemon":
                char.muscle_release = 0
            elif char.name == "Nikola Tesla":
                char.teleport_charges = 3
                char.gematria_zone_active = False
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
                if char.volund_active:
                    for key, ability in char.abilities.items():
                        if "uses_left" in ability:
                            ability["uses_left"] = ability["max_uses"]
            elif char.name == "Thor":
                char.teleport_uses = 3
                char.járngreipr_active = True
                char.mjolnir_awakened = False
            elif char.name == "Zeus":
                char.form = "Normal"
                char.adamas_timer = 0
                char.neck_fix_available = True
                char.meteor_jab_count = 0
            elif char.name == "Poseidon":
                char.used_moves = []
                char.water_level = 100
            elif char.name == "Shiva":
                char.arms_remaining = 4
                char.tandava_level = 0
                char.tandava_karma_active = False
            elif char.name == "Zerofuku":
                char.misery_level = 0
                char.cleaver_heads = 1
            elif char.name == "Hades":
                char.ichor_active = False
                char.desmos_active = False
            elif char.name == "Beelzebub":
                char.chaos_used = False
                char.lilith_mark_used = False
            elif char.name == "Apollo":
                char.expectation_bonus = 0
            elif char.name == "Susano'o":
                char.musouken_used = 0
                char.yatagarasu_form = False
            elif char.name == "Loki":
                char.clones = []
                char.perfect_clone = None
                char.andvaranaut_active = False
            elif char.name == "Odin":
                char.form = "Old"
                char.life_theft_active = False
                char.active_treasure = None
                char.treasure_timer = 0
            elif char.name == "Buddha":
                char.current_emotion = "serenity"
                char.current_weapon = "Twelve Deva Axe"
                char.future_sight_active = True
                char.zerofuku_fused = False
            elif char.name == "Qin Shi Huang":
                char.armor_form = True
                char.star_eyes_active = False
            elif char.name == "Leonidas":
                char.shield_form = "base"
            elif char.name == "Soji Okita":
                char.demon_child_active = False
                char.demon_child_release = False
                char.illness_effect = 0
            elif char.name == "Sakata Kintoki":
                char.rune_of_eirin_active = False

            print(f"  ✦ {char.name} recovered!")
        print("\n✨ Champions fully healed!")
        self.save_game()

    # ============================================================================
    # VALKYRIE MANAGEMENT METHODS - UPDATED WITH INDICES
    # ============================================================================

    def check_valkyrie_available(self, valkyrie_name):
        return self.valkyries_status.get(valkyrie_name, "unavailable") == "available"

    def get_valkyrie_partner(self, valkyrie_name):
        """Get human partner for a Valkyrie using index lookup"""
        for human, data in self.canon_pairings.items():
            if data["valkyrie_name"] == valkyrie_name:
                return human
        return "Unknown"

    def get_valkyrie_by_index(self, index):
        """Get Valkyrie info by index"""
        for valkyrie in Valkyrie:
            if valkyrie.index == index:
                return valkyrie
        return None

    def get_human_by_valkyrie_index(self, index):
        """Get human partner by Valkyrie index"""
        for human, data in self.canon_pairings.items():
            if data["valkyrie_index"] == index:
                return human
        return None

    def mark_valkyrie_fallen(self, valkyrie_name):
        if valkyrie_name in self.valkyries_status:
            self.valkyries_status[valkyrie_name] = "fallen"
            print(f"💔 {valkyrie_name} has fallen")

    def valkyrie_management_menu(self):
        """Valkyrie management menu with indices"""
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
                return self.valkyrie_management_menu()
            confirm = input(f"Reset ALL {len(fallen)} fallen Valkyries? (y/n): ").lower()
            if confirm == 'y':
                count = 0
                for valk in fallen:
                    self.valkyries_status[valk] = "available"
                    count += 1
                print(f"✨ {count} Valkyries resurrected!")
                self.save_game()
            return self.valkyrie_management_menu()
        elif choice == '2':
            if not fallen:
                print("✅ No fallen Valkyries!")
                return self.valkyrie_management_menu()
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
            return self.valkyrie_management_menu()
        elif choice == '3':
            if not fallen:
                print("✅ No fallen Valkyries!")
                return self.valkyrie_management_menu()
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
            return self.valkyrie_management_menu()
        elif choice == '4':
            self.show_valkyrie_pairings()
            return self.valkyrie_management_menu()

    def show_valkyrie_pairings(self):
        """Show canonical Valkyrie pairings with indices"""
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

    # ============================================================================
    # RAGNAROK TOURNAMENT
    # ============================================================================

    def ragnarok_tournament(self):
        """Ragnarok tournament with enhanced Adam mechanics"""
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

            activate_volund_for_character(champion, self)

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
        return humanity_wins >= 7

    # ============================================================================
    # STATISTICS MODE
    # ============================================================================

    def stats_mode(self):
        """Statistics and Records mode"""
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

    # ============================================================================
    # SAVE/LOAD METHODS
    # ============================================================================

    def save_game(self):
        """Save game with Adam's copy data and Jack's weapon uses"""
        jack_weapon_data = None
        if self.jack.volund_active and hasattr(self.jack, 'abilities'):
            jack_weapon_data = {}
            for key, ability in self.jack.abilities.items():
                if "uses_left" in ability:
                    jack_weapon_data[key] = ability["uses_left"]

        game_state = {
            'valkyries_status': self.valkyries_status,
            'story_progress': self.story_progress,
            'victories': self.victories,
            'total_kills': self.total_kills,
            'humanity_score': self.humanity_score,
            'gods_score': self.gods_score,
            'round_number': self.round_number,
            'adam_copy_data': self.adam.to_dict() if hasattr(self, 'adam') else None,
            'jack_weapon_data': jack_weapon_data
        }
        if SaveSystem.save_game(game_state):
            print("\n💾 Game saved!")
            return True
        return False

    def load_game(self):
        """Load game with Adam's copy data and Jack's weapon uses"""
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

        return True

    def save_load_menu(self):
        """Save/load management menu"""
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

    # ============================================================================
    # MAIN MENU
    # ============================================================================

    def main_menu(self):
        """Display main menu"""
        while True:
            clear_screen()
            print("\n" + "=" * 110)
            slow_print("    ⚔️⚔️⚔️ RECORD OF RAGNAROK: RAGNAROK'S CALL ⚔️⚔️⚔️", 0.02)
            print("    26 FIGHTERS (13 Gods + 13 Humans) - 100% CANON")
            print("    ALL 269 ABILITIES IMPLEMENTED - COMPLETE WIKI ACCURATE EDITION")
            print("    ENHANCED COPY MECHANICS FOR ADAM")
            print("=" * 110)

            print(f"\n🏆 Humanity: {self.humanity_score}  |  💀 Gods: {self.gods_score}")
            if self.adam.copy_count > 0:
                print(f"👁️ Adam's Copied Techniques: {self.adam.copy_count}")

            print("\n" + "🎮 GAME MODES:")
            print("=" * 110)
            print("  1. 🏆 Ragnarok Tournament - The canonical tournament")
            print("  2. ♾️ Survival Mode - Endless waves of enemies")
            print("  3. 👑 Boss Rush - Fight all 13 gods")
            print("  4. ⚔️ Gauntlet - 1v26 challenge")
            print("  5. 🌀 Chaos Mode - Everything is random")
            print("  6. 🥋 Training Mode - Practice against any fighter")
            print("  7. ⚔️ Valkyrie Management")
            print("  8. 📊 Statistics")
            print("  9. 💾 Save/Load")
            print("  10. ❌ Exit")
            print("-" * 110)

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
        """Exit the game"""
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
    """Main entry point"""
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