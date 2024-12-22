from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ..crud import source as crud_source
from ..schemas import source as schema_source
# get a database session
from ..core.database import get_db

router = APIRouter(
    tags=["sources"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schema_source.Source, status_code=201)
async def create_source(
    source: schema_source.SourceCreate, db: AsyncSession = Depends(get_db)
):
    try: 
        created_source = await crud_source.create_source(db, source)
        return created_source
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Add some optional params, such that the source can be filtered,
#  not just by the id
# but also by other fields

@router.get("/")
async def get_sources(
    field: Optional[str] = None,
    value = None,
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db),
):   
    """handle the inputed fields"""
    if field:
       return await get_by_fields(db, skip, limit, field, value)

    return await crud_source.get_sources(db, skip, limit)


# Function to handle optional fields
async def get_by_fields(db: AsyncSession, skip: int, limit: int, field: str, value):

    field = field.lower()
    # Create an array of all the model fields
    model_dict = schema_source.Source.__dict__.items()
    model_fields = {key: value for key, value in model_dict if not key.startswith('__')}
    model_fields = model_fields['model_fields'].keys()
    
    if field not in model_fields:
        raise HTTPException(status_code=404, detail=f"Provided field, {field} is not found")  
    
    status, sources = await crud_source.get_filtered_sources(db, field, value, skip, limit)
    if not status:
        raise HTTPException(status_code=404, detail=f"No such record found: {sources}")  

    return sources


@router.get("/{source_id}", response_model=schema_source.Source)
async def get_source(source_id: int, db: AsyncSession = Depends(get_db)):
    source = await crud_source.get_source(db, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.patch("/{source_id}", response_model=schema_source.Source, status_code=200)
async def update_source(
    source_id: int,
    source: schema_source.SourceUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_source = await crud_source.update_source(db, source_id, source)
    return updated_source


# Delete all sources
@router.delete("/", response_model=schema_source.Source)
async def delete_sources(db: AsyncSession = Depends(get_db)):
    deleted_sources = await crud_source.delete_sources(db)
    return deleted_sources


@router.delete("/{source_id}", response_model=schema_source.Source)
async def delete_source(source_id: int, db: AsyncSession = Depends(get_db)):
    deleted_source = await crud_source.delete_source(db, source_id)
    return deleted_source
