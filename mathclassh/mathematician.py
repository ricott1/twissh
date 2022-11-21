from __future__ import annotations
from mathclassh.math_skills import FieldNames

from dataclasses import dataclass
from enum import Enum
from .utils import FEMALE_PORTRAITS, MALE_PORTRAITS, roll, roll_stat
import random
import pygame as pg
import time
import uuid


default_stats: dict[str, dict[str, int]] = {
    "base": {
        "intelligence": 10,
        "creativity": 10,
        "social": 10,
        "work_ethic": 10
    },
    "number_theory": {
        "elementary_number_theory": 10,
        "analytic_number_theory": 10,
        "algebraic_number_theory": 10,
        "diophantine_geometry": 10
    },
    "algebra": {
        
    },
    "geometry": {
        
    },
    "analysis": {

    },
    "discrete_math": {
        
    },
    "logic": {
        
    }
}

@dataclass
class Stats:
    creativity: int
    intelligence: int
    charisma: int
    work_ethic: int

@dataclass
class Algebra:
    name: str
    field: FieldNames
    level: int
    experience: int
    next_level_experience: int

class ROLE(str, Enum):
    HEAD = "head"
    PROFESSOR = "professor"
    POSTDOC = "postdoc"
    PHD = "phd"
    MASTER = "master"
    UNDERGRAD = "undergrad"

class GENDER(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

MALE_NAMES = (
    "Samuele",
    "Gundam",
    "Lukiko",
    "Armando",
    "Pancrazio",
    "Tancredi",
    "Swallace",
    "Faminy",
    "Pertis",
    "Pericles",
    "Atheno",
    "Gianfranco",
    "Ciriaco",
    "Harri",
    "Ted",
    "Michele",
    "Pierre",
    "Costantino",
    "Giovanni",
    "Terence"
)

FEMALE_NAMES = (
    "Maria",
    "Beatrice",
    "Pesca",
    "Pantera",
    "Emmy",
    "Allegra",
    "Gianna",
    "Berta",
    "Lena",
    "Strina",
    "Layla"
)

LAST_NAMES = (
    "Fornea",
    "Seguace",
    "Larry",
    "Finile",
    "Ching-chong",
    "Formaggio",
    "Goffi",
    "Tao",
    "Mao",
    "Perelmann",
    "Fermat",
    "Frittura"

)

@dataclass 
class Contract:
    start_date: int
    end_date: int
    salary: int
    role: ROLE

    def length(self):
        return self.end_date - self.start_date

    @classmethod
    def head_contract(cls):
        return cls(
            time.time(),
            time.time() + roll(1, 4) * 365 * 24 * 60 * 60,
            27000 + roll(3, 35) * 1000,
            ROLE.HEAD
        )
    
    @classmethod
    def professor_contract(cls):
        return cls(
            time.time(),
            time.time() + roll(1, 4) * 365 * 24 * 60 * 60,
            23000 + roll(2, 50) * 1000,
            ROLE.PROFESSOR
        )
    
    @classmethod
    def postdoc_contract(cls):
        return cls(
            time.time(),
            time.time() + roll(1, 4) * 365 * 24 * 60 * 60,
            5000 + roll(4, 20) * 100,
            ROLE.POSTDOC
        )
    
    @classmethod
    def phd_contract(cls):
        return cls(
            time.time(),
            time.time() + roll(1, 4) * 365 * 24 * 60 * 60,
            roll(3, 20) * 10,
            ROLE.PHD
        )
    
    @classmethod
    def master_contract(cls):
        return cls(
            time.time(),
            time.time() + roll(1, 4) * 365 * 24 * 60 * 60,
            roll(1, 100) * 5,
            ROLE.MASTER
        )
    
    @classmethod
    def undergrad_contract(cls):
        return cls(
            time.time(),
            time.time() + roll(1, 4) * 365 * 24 * 60 * 60,
            0,
            ROLE.UNDERGRAD
        )

@dataclass
class Mathematician:
    id: bytes
    name: str
    last_name: str
    gender: GENDER
    age: int
    born_in: bytes
    portrait: pg.Surface
    research_group: bytes
    contract: Contract
    relations: dict[bytes, int]
    happiness: int
    fame: int
    stress: int
    stats: dict[str, dict[str, int]]
    potential: int
    crackpot: bool = False

    @classmethod
    def generate(cls, born_in: bytes, role: ROLE, research_group: bytes | None = None) -> Mathematician:
        born_in = born_in
        gender = random.choice(list(GENDER))
        name = random.choice(list(MALE_NAMES)) if gender == GENDER.MALE else random.choice(list(FEMALE_NAMES))
        last_name = random.choice(list(LAST_NAMES))
        match role:
            case ROLE.HEAD:
                contract = Contract.head_contract()
            case ROLE.PROFESSOR:
                contract = Contract.professor_contract()
            case ROLE.POSTDOC:
                contract = Contract.postdoc_contract()
            case ROLE.PHD:
                contract = Contract.phd_contract()
            case ROLE.MASTER:
                contract = Contract.master_contract()
            case ROLE.UNDERGRAD:
                contract = Contract.undergrad_contract()
        
        stats = {k: {k2: roll_stat() for k2 in default_stats[k].keys()} for k in default_stats.keys()}

        return Mathematician(
            id = uuid.uuid4(),
            name = name,
            last_name = last_name,
            gender = gender,
            age = 14 + roll(4, 20),
            born_in=born_in,
            portrait= MALE_PORTRAITS.random() if gender == GENDER.MALE else FEMALE_PORTRAITS.random(),
            research_group = research_group,
            contract=contract,
            relations={},
            happiness=roll(1, 100),
            fame=roll(1, 100),
            stress=roll(1, 100),
            stats=stats,
            potential=roll(1, 100),
            crackpot=False
        )


    def update_relation(self, mathematician: Mathematician, value: int) -> None:
        if mathematician.id in self.relations:
            self.relations[mathematician.id] += value
        else:
            self.relations[mathematician.id] = value
        if self.relations[mathematician.id] == 0:
            del self.relations[mathematician.id]

