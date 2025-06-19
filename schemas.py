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

class GroupTypeSpec(BaseModel):
    type: GroupType
    base: AcademicBase
    years: int
    places: int
    cost: Optional[int] = None
    minScore: Optional[float] = None


# ответ API
class SpecialtySchema(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    prefix: Optional[str] = None
    code: str
    # fullYears: Optional[int] = None
    # notFullYears: Optional[int] = None
    groupTypes: List[GroupTypeSpec]
    

    class Config:
        from_attributes = True

class SpecialtyRatingSchema(BaseModel):
    code: str
    name: str
    plan: int
    statementQuantity: int
    competition: float
    base: AcademicBase
    skill: Qualification

class EducationalLoanSchema(BaseModel):
    loanText: str