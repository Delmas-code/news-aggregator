from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..crud import tag as crud_tag
from ..schemas import tag as schema_tag
from ..core.database import async_session

router = APIRouter(
    tags=["tags"],
    responses={404: {"description": "Not found"}},
)

# get a database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

@router.post("/", response_model=schema_tag.Tag, status_code=201)
async def create_tag(
    tag: schema_tag.TagCreate, db: AsyncSession = Depends(get_db)
):
    try: 
        created_tag = await crud_tag.create_tag(db, tag)
        return created_tag
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Add some optional params, such that the tag can be filtered,
#  not just by the id
# but also by other fields

@router.get("/")
async def get_tags(
    field: Optional[str] = None,
    value = None,
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db),
):   
    """handle the inputed fields"""
    if field:
       return await get_by_fields(db, skip, limit, field, value)

    return await crud_tag.get_tags(db, skip, limit)


# Function to handle optional fields
async def get_by_fields(db: AsyncSession, skip: int, limit: int, field: str, value):

    field = field.lower()
    # Create an array of all the model fields
    model_dict = schema_tag.Tag.__dict__.items()
    model_fields = {key: value for key, value in model_dict if not key.startswith('__')}
    model_fields = model_fields['model_fields'].keys()
    
    if field not in model_fields:
        raise HTTPException(status_code=404, detail=f"Provided field, {field} is not found")  
    
    status, tags = await crud_tag.get_filtered_tags(db, field, value, skip, limit)
    if not status:
        raise HTTPException(status_code=404, detail=f"No such record found: {tags}")  

    return tags


@router.get("/{tag_id}", response_model=schema_tag.Tag)
async def get_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await crud_tag.get_tag(db, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.patch("/{tag_id}", response_model=schema_tag.Tag, status_code=200)
async def update_tag(
    tag_id: int,
    tag: schema_tag.TagUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_tag = await crud_tag.update_tag(db, tag_id, tag)
    return updated_tag


@router.delete("/{tag_id}", response_model=schema_tag.Tag)
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    deleted_tag = await crud_tag.delete_tag(db, tag_id)
    return deleted_tag


# Delete all tags
@router.delete("/", response_model=schema_tag.Tag)
async def delete_tag(db: AsyncSession = Depends(get_db)):
    deleted_tags = await crud_tag.delete_tags(db)
    return deleted_tags