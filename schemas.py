from enum import Enum
from pydantic import BaseModel
from typing import Optional, List

class AcademicBase(str, Enum):
    FULL = 'FULL'            # на базе 9 классов
    NOT_FULL = 'NOT_FULL'    # на базе 11 классов


class GroupType(str, Enum):
    FREE = 'FREE'              # бюджет
    COMMERCIAL = 'COMMERCIAL'  # коммерция
    EXTRAMURAL = 'EXTRAMURAL'  # заочная

class Qualification(str, Enum):
    SPECIALTY = 'SPECIALTY'    # специальность СПО
    PROFESSION = 'PROFESSION'  # профессия СПО


# ответ API
class SpecialtySchema(BaseModel):
    code: str
    name: str
    description: List[str]
    base: AcademicBase
    group_type: GroupType
    duration_years: int
    places: int
    cost: Optional[int] = None
    min_score: Optional[float] = None

    class Config:
        from_attributes = True

class SpecialtyRatingSchema(BaseModel):
    code: str
    name: str
    plan: int
    statement_quantity: int
    competition: float
    base: AcademicBase
    skill: Qualification

class EducationalLoanSchema(BaseModel):
    loan_text: List[str]