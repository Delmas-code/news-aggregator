from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..crud import content as crud_content
from ..schemas import content as schema_content
from ..core.database import async_session

router = APIRouter(
    tags=["contents"],
    responses={404: {"description": "Not found"}},
)

# get a database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

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
    *,
    field: Optional[str] = None,
    value: Optional[str] = None,
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db),
): 
    # Create an array of all the model fields
    
    if field:
        field = field.lower()
        model_fields = {key: value for key, value in schema_content.Content.__dict__.items() if not key.startswith('__')}['model_fields'].keys()
        
        if field not in model_fields:
            raise HTTPException(status_code=404, detail=f"Provided field, {field} is not found")  

    status, contents = await crud_content.get_contents(db, skip, limit, field, value)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"No such record found: {contents}")  

    return contents 

@router.get("/{content_id}", response_model=schema_content.Content)
async def get_content(content_id: int, db: AsyncSession = Depends(get_db)):
    content = await crud_content.get_content(db, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="content not found")
    return content


@router.patch("/{content_id}", response_model=schema_content.Content, status_code=200)
async def update_content(
    content_id: int,
    content: schema_content.ContentUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_content = await crud_content.update_content(db, content_id, content)
    return updated_content


@router.delete("/{content_id}", response_model=schema_content.Content)
async def delete_content(content_id: int, db: AsyncSession = Depends(get_db)):
    deleted_content = await crud_content.delete_content(db, content_id)
    return deleted_content


# Delete all contents
@router.delete("/", response_model=schema_content.Content)
async def delete_all(db: AsyncSession = Depends(get_db)):
    deleted_content = await crud_content.delete_contents(db)
    return deleted_content