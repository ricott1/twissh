from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .research_group import ResearchGroup

from dataclasses import dataclass
from enum import Enum
from .utils import FEMALE_PORTRAITS, MALE_PORTRAITS, roll
from .city import City
import random
import pygame as pg
import time
import uuid

@dataclass
class Stats:
    creativity: int
    intelligence: int
    charisma: int
    luck: int
    work_ethic: int

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
    id: uuid.UUID
    name: str
    last_name: str
    gender: GENDER
    age: int
    born_in: City
    portrait: pg.Surface
    research_group: ResearchGroup
    contract: Contract
    relations: dict[uuid.UUID, int]
    happiness: int
    fame: int
    stress: int
    stats: Stats
    potential: int
    crackpot: bool = False

    @classmethod
    def generate(cls, born_in: City, role: ROLE, research_group: ResearchGroup | None = None) -> Mathematician:
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
            stats=Stats(
                creativity=roll(1, 100),
                intelligence=roll(1, 100),
                charisma=roll(1, 100),
                luck=roll(1, 100),
                work_ethic=roll(1, 100)
            ),
            potential=roll(1, 100),
            crackpot=False
        )

    @property
    def living_in(self) -> City:
        if self.research_group:
            return self.research_group.city
        return self.born_in

    @property
    def description(self) -> str:
        match self.gender:
            case GENDER.MALE:
                pronoun = "He is"
            case GENDER.FEMALE:
                pronoun = "She is"
            case _:
                pronoun = "They are"

        if self.contract:
            work = f"{pronoun} currently {self.contract.role} at {self.research_group.university.name} in {self.research_group.city.name}, {self.research_group.city.country}. The contract will end on {time.strftime('%d-%m-%Y', time.localtime(self.contract.end_date))}.\n"
        else:
            work = f"{pronoun} currently unemployed.\n"
        # contract = f"{pronoun} is currently under contract until {time.strftime('%Y-%m-%d', time.localtime(self.contract.end_date))}, earning {self.contract.salary} per year.\n"

        match self.happiness:
            case x if x < 20:
                happiness = f"{pronoun} miserable "
            case x if x < 40:
                happiness = f"{pronoun} unhappy "
            case x if x < 60:
                happiness = f"{pronoun} alright "
            case x if x < 80:
                happiness = f"{pronoun} happy "
            case x if x <= 100:
                happiness = f"{pronoun} ecstatic "
            case _:
                happiness = f"{pronoun} in a state of confusion "
        
        match self.fame:
            case x if x < 20:
                fame = f"and unknown.\n"
            case x if x < 40:
                fame = f"and a local celebrity.\n"
            case x if x < 70:
                fame = f"and a national celebrity.\n"
            case x if x < 90:
                fame = f"and a global celebrity.\n"
            case _:
                fame = f"and will be remembered forever.\n"

        return work + happiness + fame

    @property
    def general_info(self) -> str:
        return f"{self.name} {self.last_name} is a {self.age}-year-old from {self.born_in.name}, {self.born_in.country}."
    
    @property
    def stats_description(self) -> str:
        return f"Charisma: {self.stats.charisma}\nCreativity: {self.stats.creativity}\nIntelligence: {self.stats.intelligence}\nLuck: {self.stats.luck}\nWork ethic: {self.stats.work_ethic}"

    def update_relation(self, mathematician: Mathematician, value: int) -> None:
        if mathematician.id in self.relations:
            self.relations[mathematician.id] += value
        else:
            self.relations[mathematician.id] = value
        if self.relations[mathematician.id] == 0:
            del self.relations[mathematician.id]

