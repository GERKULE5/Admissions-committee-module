from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from typing import Optional


import os
from dotenv import load_dotenv



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


app = FastAPI()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/token", response_model=TokenResponse)
def login(
    client_id: str = Form(...),
    client_secret: str = Form(...)
):
    if client_id != CLIENT_ID or client_secret != CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": client_id})
    return {"access_token": token, "token_type": "bearer"}


def get_current_client(token: str = Depends(lambda x: x)):

    auth = token
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.split(" ")[1]
    payload = verify_token(token)
    return payload


from schemas import AcademicBase, GroupType, Qualification, SpecialtySchema, SpecialtyRatingSchema
from parser import all_data, rating_data


@app.get("/specialties/", response_model=list[SpecialtySchema])
def get_specialties(
    base: Optional[AcademicBase] = None,
    group_type: Optional[GroupType] = None,
    _: dict = Depends(get_current_client)
):
    filtered = all_data
    
    if base:
        filtered = [item for item in filtered if item['base'] == base.value]

    if group_type: 
        filtered = [item for item in filtered if item['group_type'] == group_type.value]

    return filtered


@app.get('/specialties/{specialty_code}', response_model=list[SpecialtySchema])
def get_specialty_by_code(specialty_code: str, _: dict = Depends(get_current_client)):

    result = [item for item in all_data if item['code'] == specialty_code]

    if not result:
        raise HTTPException(status_code=400, detail=f"Specialty {specialty_code} not found")

    return result


@app.get('/specialties/rating/', response_model=list[SpecialtyRatingSchema])
def get_specialties_rating(
    base: Optional[AcademicBase] = None,
    current_qualification: Optional[Qualification] = None,
    _: dict = Depends(get_current_client)
):
    filtered_rating = rating_data
    
    if base:
        filtered_rating = [item for item in filtered_rating if item['base'] == base.value]

    if current_qualification: 
        filtered_rating = [item for item in filtered_rating if item['skill'] ==  current_qualification.value]

    return filtered_rating