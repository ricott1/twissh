from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .utils import roll

class FieldNames(str, Enum):
    NUMBER_THEORY: str = "number theory"
    ALGEBRA: str = "algebra"
    GEOMETRY: str = "geometry"
    ANALYSIS: str = "analysis"
    DISCRETE_MATH: str = "discrete math"
    LOGIC: str = "logic"

@dataclass
class SubField:
    name: str
    short_name: str
    description: str
    value: int = roll(1, 10)

    @classmethod
    def from_dict(cls, d: dict[str, any]) -> SubField:
        return SubField(
            name=d["name"],
            short_name=d["short_name"],
            description=d["description"]
        )

@dataclass
class Field:
    name: str
    description: str
    subfields: list[SubField]

    def __post_init__(self) -> None:
        for sf in self.subfields:
            setattr(self, sf.short_name, sf)
    
    @classmethod
    def from_dict(cls, d: dict[str, any]) -> Field:
        return Field(
            name=d["name"],
            description=d["description"],
            subfields=[SubField.from_dict(sf) for sf in d["subfields"]]
        )

    @property
    def value(self) -> int:
        return sum([subfield.value for subfield in self.subfields])





    # subfields of ALGEBRA
#     group theory;
#     field theory;
#     vector spaces, whose study is essentially the same as linear algebra;
#     ring theory;
#     commutative algebra, which is the study of commutative rings, includes the study of polynomials, and is a foundational part of algebraic geometry;
#     homological algebra
#     Lie algebra and Lie group theory;
#     Boolean algebra, which is widely used for the study of the logical structure of computers.
#     The study of types of algebraic structures as mathematical objects is the object of universal algebra and category theory.
    
    # subfields of ANALYSIS
#     Multivariable calculus
#     Functional analysis, where variables represent varying functions;
#     Integration, measure theory and potential theory, all strongly related with Probability theory;
#     Ordinary differential equations;
#     Partial differential equations;
#     Numerical analysis, mainly devoted to the computation on computers of solutions of ordinary and partial differential equations that arise in many applications.


    # subfields of Discrete mathematics
#     Combinatorics, the art of enumerating mathematical objects that satisfy some given constraints. Originally, these objects were elements or subsets of a given set; this has been extended to various objects, which establishes a strong link between combinatorics and other parts of discrete mathematics. For example, discrete geometry includes counting configurations of geometric shapes
#     Graph theory and hypergraphs
#     Coding theory, including error correcting codes and a part of cryptography
#     Matroid theory
#     Discrete geometry
#     Discrete probability distributions
#     Game theory (although continuous games are also studied, most common games, such as chess and poker are discrete)
#     Discrete optimization, including combinatorial optimization, integer programming, constraint programming

    # subfields of LOGIC
#     set theory
#     model theory
#     proof theory
#     computability theory



