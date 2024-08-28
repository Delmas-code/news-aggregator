from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..crud import recognition as crud_recognition
from ..schemas import recognition as schema_recognition
from ..core.database import async_session

router = APIRouter(
    tags=["recognitions"],
    responses={404: {"description": "Not found"}},
)

# get a database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

@router.post("/", response_model=schema_recognition.Recognition, status_code=201)
async def create_recognition(
    recognition: schema_recognition.RecognitionCreate, db: AsyncSession = Depends(get_db)
):
    try: 
        created_recognition = await crud_recognition.create_recognition(db, recognition)
        return created_recognition
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Add some optional params, such that the recognition can be filtered,
#  not just by the id
# but also by other fields

@router.get("/")
async def get_recognitions(
    field: Optional[str] = None,
    value = None,
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db),
):   
    """handle the inputed fields"""
    if field:
       return await get_by_fields(db, skip, limit, field, value)

    return await crud_recognition.get_recognitions(db, skip, limit)


# Function to handle optional fields
async def get_by_fields(db: AsyncSession, skip: int, limit: int, field: str, value):

    field = field.lower()
    # Create an array of all the model fields
    model_dict = schema_recognition.Recognition.__dict__.items()
    model_fields = {key: value for key, value in model_dict if not key.startswith('__')}
    model_fields = model_fields['model_fields'].keys()
    
    if field not in model_fields:
        raise HTTPException(status_code=404, detail=f"Provided field, {field} is not found")  
    
    status, recognitions = await crud_recognition.get_filtered_recognitions(db, field, value, skip, limit)
    if not status:
        raise HTTPException(status_code=404, detail=f"No such record found: {recognitions}")  

    return recognitions


@router.get("/{recognition_id}", response_model=schema_recognition.Recognition)
async def get_recognition(recognition_id: int, db: AsyncSession = Depends(get_db)):
    recognition = await crud_recognition.get_recognition(db, recognition_id)
    if recognition is None:
        raise HTTPException(status_code=404, detail="Recognition not found")
    return recognition


@router.patch("/{recognition_id}", response_model=schema_recognition.Recognition, status_code=200)
async def update_recognition(
    recognition_id: int,
    recognition: schema_recognition.RecognitionUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_recognition = await crud_recognition.update_recognition(db, recognition_id, recognition)
    return updated_recognition


@router.delete("/{recognition_id}", response_model=schema_recognition.Recognition)
async def delete_recognition(recognition_id: int, db: AsyncSession = Depends(get_db)):
    deleted_recognition = await crud_recognition.delete_recognition(db, recognition_id)
    return deleted_recognition


# Delete all recognitions
@router.delete("/", response_model=schema_recognition.Recognition)
async def delete_recognition(db: AsyncSession = Depends(get_db)):
    deleted_recognitions = await crud_recognition.delete_recognitions(db)
    return deleted_recognitions