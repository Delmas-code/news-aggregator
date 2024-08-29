from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..crud import content as crud_content
from ..schemas import content as schema_content

# get a database session
from ..core.database import get_db

router = APIRouter(
    tags=["contents"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schema_content.Content, status_code=201)
async def create_content(
    content: schema_content.ContentCreate, db: AsyncSession = Depends(get_db)
):
    try: 
        created_content = await crud_content.create_content(db, content)
        return created_content
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Add some optional params, such that the content can be filtered,
#  not just by the id
# but also byt other fields

@router.get("/", response_model=List[schema_content.Content])
async def get_contents(
    field: Optional[str] = None,
    value = None,
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db),
):     
    if field:
        return await get_by_fields(db, field, value, skip, limit)

    return await crud_content.get_contents(db, skip, limit) 


# Function to handle optional fields
async def get_by_fields(db: AsyncSession, field: str, value, skip: int, limit: int):
    field = field.lower()
    # Create an array of all the model fields
    model_dict = schema_content.Content.__dict__.items()
    model_fields = {key: value for key, value in model_dict if not key.startswith('__')}
    model_fields = model_fields['model_fields'].keys()
    
    if field not in model_fields:
        raise HTTPException(status_code=404, detail=f"Provided field, {field} is not found")  
    
    status, contents = await crud_content.get_filtered_contents(db, field, value, skip, limit)
    if not status:
        raise HTTPException(status_code=404, detail=f"No such record found: {contents}")  

    return contents


@router.get("/{content_id}", response_model=schema_content.Content)
async def get_content(content_id: str, db: AsyncSession = Depends(get_db)):

    content = await get_by_fields(db, field = "id", value = content_id, skip = 0, limit = 10)
    if content is None:
        raise HTTPException(status_code=404, detail="content not found")
    return content


@router.patch("/{content_id}", response_model=schema_content.Content, status_code=200)
async def update_content(
    content_id: str,
    content: schema_content.ContentUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_content = await crud_content.update_content(db, content_id, content)
    return updated_content


@router.delete("/{content_id}", response_model=schema_content.Content)
async def delete_content(content_id: str, db: AsyncSession = Depends(get_db)):
    deleted_content = await crud_content.delete_content(db, content_id)
    return deleted_content


# Delete all contents
@router.delete("/", response_model=schema_content.Content)
async def delete_all(db: AsyncSession = Depends(get_db)):
    deleted_content = await crud_content.delete_contents(db)
    return deleted_content