from fastapi import FastAPI, HTTPException
from typing import Optional
from schemas import AcademicBase, GroupType, SpecialtySchema
from parser import all_data


app = FastAPI()


@app.get("/specialties/", response_model=list[SpecialtySchema])
def get_specialties(
    base: Optional[AcademicBase] = None,
    group_type: Optional[GroupType] = None
):
    filtered = all_data
    
    if base:
        filtered = [item for item in filtered if item['base'] == base.value]

    if group_type: 
        filtered = [item for item in filtered if item['group_type'] == group_type.value]

    return filtered

@app.get('/specialties/{specialty_code}', response_model=list[SpecialtySchema])
def get_specialty_by_code(specialty_code: str):

    result = [item for item in all_data if item['code'] == specialty_code]

    if not result:
        raise HTTPException(status_code=400, detail=f"Specialty {specialty_code} not found")

    return result