from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from typing import Optional

import os
from dotenv import load_dotenv

# === Загрузка переменных окружения ===
load_dotenv()

# === FastAPI с поддержкой безопасности ===
security_scheme = HTTPBearer()
app = FastAPI()

# === Токен из .env ===
TOKEN = os.getenv("TOKEN")

# === Проверка токена ===
def verify_static_token(request: Request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid token"
        )
    
    token = auth_header.split(" ")[1]
    
    if token != TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Invalid token"
        )
    
    return token

# === Пример маршрута с безопасностью ===
from schemas import AcademicBase, GroupType, Qualification, SpecialtySchema, SpecialtyRatingSchema
from parser import all_data, rating_data


@app.get("/specialties/", response_model=list[SpecialtySchema], dependencies=[Depends(security_scheme)])
def get_specialties(
    base: Optional[AcademicBase] = None,
    group_type: Optional[GroupType] = None,
    token: str = Depends(verify_static_token)
):
    filtered = all_data

    if base:
        filtered = [item for item in filtered if item['base'] == base.value]

    if group_type:
        filtered = [item for item in filtered if item['group_type'] == group_type.value]

    return filtered


@app.get('/specialties/{specialty_code}', response_model=list[SpecialtySchema], dependencies=[Depends(security_scheme)])
def get_specialty_by_code(specialty_code: str, token: str = Depends(verify_static_token)):

    result = [item for item in all_data if item['code'] == specialty_code]

    if not result:
        raise HTTPException(status_code=400, detail=f"Specialty {specialty_code} not found")

    return result


@app.get('/specialties/rating/', response_model=list[SpecialtyRatingSchema], dependencies=[Depends(security_scheme)])
def get_specialties_rating(
    base: Optional[AcademicBase] = None,
    current_qualification: Optional[Qualification] = None,
    token: str = Depends(verify_static_token)
):
    filtered_rating = rating_data

    if base:
        filtered_rating = [item for item in filtered_rating if item['base'] == base.value]

    if current_qualification:
        filtered_rating = [item for item in filtered_rating if item['skill'] == current_qualification.value]

    return filtered_rating