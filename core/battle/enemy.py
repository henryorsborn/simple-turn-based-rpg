from core.battle.attack import Attack
from core.battle.attack_effect import AttackEffect
from yaml import safe_load
import random
import pygame

class Enemy(object):

    def __init__(self, type_: str, class_: str, name: str, path_to_sprite: str, hp: int,
                 mp: int, str_: int, def_: int, mag: int, mgdf: int, spd: int,
                 resist: list, elem_resist: list, elem_absorb: list, elem_weak: list,
                 attacks: list, script: dict):
        self.type_ = type_
        self.class_ = class_
        self.name = name
        self.path_to_sprite = path_to_sprite
        self.max_hp = hp
        self.hp = hp
        self.max_mp = mp
        self.mp = mp
        self.strength = str_
        self.defense = def_
        self.magic = mag
        self.magic_defense = mgdf
        self.speed = spd
        self.resistance = resist if resist is not [] else None
        self.elem_resistance = elem_resist if elem_resist is not [] else None
        self.elem_absorb = elem_absorb if elem_absorb is not [] else None
        self.elem_weak = elem_weak if elem_weak is not [] else None
        self.attacks = attacks
        self.script = script
        self.script_queue = script.copy()

    @staticmethod
    def read_and_deserialize_yml(path: str = ""):
        with open(path) as file:
            content = safe_load(file.read())["monster"]

        attacks = {}
        for attack in content["attacks"]:
            attack = attack["attack"]
            effects = []
            if attack["eff"] != "None":
                for effect in attack["eff"]:
                    effect = effect["effect"]
                    effects.append(AttackEffect(**effect))
                attack["eff"] = effects
            attacks[attack["key"]] = Attack(**attack)
        content["attacks"] = attacks
        content["resist"] = content["resist"].split()
        content["elem_resist"] = content["elem_resist"].split()
        content["elem_absorb"] = content["elem_absorb"].split()
        content["elem_weak"] = content["elem_weak"].split()
        return Enemy(**content)

    def execute_attack(self, key, battle_stats):
        attack: Attack = self.attacks[key]
        self.mp -= attack.cost

        if ((10*attack.accuracy) * battle_stats.player.luck/255) > random.randint(1, 100):
            damage = (self.defense * attack.damage) * battle_stats.player.defense/255
            battle_stats.player.hp -= damage
            battle_stats.message = f"{self.name}'s {attack.name} did {damage} damage!"
        else:
            battle_stats.message = f"{self.name}'s {attack.name} missed!"
        #todo allow for resistance and absorb with attacks

    def run_through_script_helper(self, battle_stats):
        self.run_through_script_rec(self.script_queue, battle_stats)

    def run_through_script_rec(self, steps, battle_stats):
        if len(steps) == 0:
            return
        step = steps.pop(0)["step"]
        if step["type_"] == "while":
            self.run_through_script_rec(step["children"], battle_stats)
        if step["type_"] == "func":
            if step["key"] == "rand_pick":
                fringe = []
                for choice, weight in step["args_"]:
                    fringe.extend([choice] * weight)
                choice = random.choice(fringe)
                self.execute_attack(choice, battle_stats)