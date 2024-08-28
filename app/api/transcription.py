from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..crud import transcription as crud_transcription
from ..schemas import transcription as schema_transcription
from ..core.database import async_session

router = APIRouter(
    tags=["transcriptions"],
    responses={404: {"description": "Not found"}},
)

# get a database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

@router.post("/", response_model=schema_transcription.Transcription, status_code=201)
async def create_transcription(
    transcription: schema_transcription.TranscriptionCreate, db: AsyncSession = Depends(get_db)
):
    try: 
        created_transcription = await crud_transcription.create_transcription(db, transcription)
        return created_transcription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Add some optional params, such that the transcription can be filtered,
#  not just by the id
# but also by other fields

@router.get("/")
async def get_transcriptions(
    field: Optional[str] = None,
    value = None,
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db),
):   
    """handle the inputed fields"""
    if field:
       return await get_by_fields(db, skip, limit, field, value)

    return await crud_transcription.get_transcriptions(db, skip, limit)


# Function to handle optional fields
async def get_by_fields(db: AsyncSession, skip: int, limit: int, field: str, value):

    field = field.lower()
    # Create an array of all the model fields
    model_dict = schema_transcription.Transcription.__dict__.items()
    model_fields = {key: value for key, value in model_dict if not key.startswith('__')}
    model_fields = model_fields['model_fields'].keys()
    
    if field not in model_fields:
        raise HTTPException(status_code=404, detail=f"Provided field, {field} is not found")  
    
    status, transcriptions = await crud_transcription.get_filtered_transcriptions(db, field, value, skip, limit)
    if not status:
        raise HTTPException(status_code=404, detail=f"No such record found: {transcriptions}")  

    return transcriptions


@router.get("/{transcription_id}", response_model=schema_transcription.Transcription)
async def get_transcription(transcription_id: int, db: AsyncSession = Depends(get_db)):
    transcription = await crud_transcription.get_transcription(db, transcription_id)
    if transcription is None:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return transcription


@router.patch("/{transcription_id}", response_model=schema_transcription.Transcription, status_code=200)
async def update_transcription(
    transcription_id: int,
    transcription: schema_transcription.TranscriptionUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_transcription = await crud_transcription.update_transcription(db, transcription_id, transcription)
    return updated_transcription


@router.delete("/{transcription_id}", response_model=schema_transcription.Transcription)
async def delete_transcription(transcription_id: int, db: AsyncSession = Depends(get_db)):
    deleted_transcription = await crud_transcription.delete_transcription(db, transcription_id)
    return deleted_transcription


# Delete all transcriptions
@router.delete("/", response_model=schema_transcription.Transcription)
async def delete_transcription(db: AsyncSession = Depends(get_db)):
    deleted_transcriptions = await crud_transcription.delete_transcriptions(db)
    return deleted_transcriptions