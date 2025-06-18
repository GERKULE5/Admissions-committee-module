from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from typing import Optional
import os
from dotenv import load_dotenv
import asyncio


load_dotenv()


app = FastAPI()
security_scheme = HTTPBearer()


TOKEN = os.getenv("TOKEN")


def verify_static_token(request: Request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
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



from schemas import AcademicBase, GroupType, Qualification, SpecialtySchema, SpecialtyRatingSchema, EducationalLoanSchema
from parser import parse_all_data, parse_rating, parse_educational_loan

all_data = []
rating_data = []
loan_data = []


@app.on_event("startup")
async def startup_event():
    global all_data, rating_data, loan_data
    print("Start parsing")
    all_data = parse_all_data() 
    rating_data = parse_rating()  
    loan_data = parse_educational_loan()  
    print("Parsing finished")


    asyncio.create_task(background_refresh())


async def background_refresh():
    global all_data
    while True:
        await asyncio.sleep(30 * 60) 
        try:
            print("Refreshing")
            new_data = parse_all_data()
            if new_data:
                all_data = new_data
                print(f"Refreshing successfuly finished")
            else:
                print("Refreshing cant finish")
        except Exception as e:
            print(f"Refreshing error: {e}")



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


@app.get('/educational_loan/', response_model=EducationalLoanSchema, dependencies=[Depends(security_scheme)])
def get_educational_loan(token: str = Depends(verify_static_token)):
    if not loan_data:
        raise HTTPException(status_code=500, detail="No data found")
    
    return {'loan_text': loan_data}