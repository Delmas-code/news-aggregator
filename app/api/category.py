from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..crud import category as crud_category
from ..schemas import category as schema_category

# get a database session
from ..core.database import get_db

router = APIRouter(
    tags=["categories"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schema_category.Category, status_code=201)
async def create_category(
    category: schema_category.CategoryCreate, db: AsyncSession = Depends(get_db)
):
    try: 
        created_category = await crud_category.create_category(db, category)
        return created_category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Add some optional params, such that the category can be filtered,
#  not just by the id
# but also by other fields

@router.get("/")
async def get_categories(
    field: Optional[str] = None,
    value = None,
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db),
):   
    """handle the inputed fields"""
    if field:
       return await get_by_fields(db, skip, limit, field, value)

    return await crud_category.get_categories(db, skip, limit)


# Function to handle optional fields
async def get_by_fields(db: AsyncSession, skip: int, limit: int, field: str, value):

    field = field.lower()
    # Create an array of all the model fields
    model_dict = schema_category.Category.__dict__.items()
    model_fields = {key: value for key, value in model_dict if not key.startswith('__')}
    model_fields = model_fields['model_fields'].keys()
    
    if field not in model_fields:
        raise HTTPException(status_code=404, detail=f"Provided field, {field} is not found")  
    
    status, categories = await crud_category.get_filtered_categories(db, field, value, skip, limit)
    if not status:
        raise HTTPException(status_code=404, detail=f"No such record found: {categories}")  

    return categories


@router.get("/{category_id}", response_model=schema_category.Category)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await crud_category.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=schema_category.Category, status_code=200)
async def update_category(
    category_id: int,
    category: schema_category.CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_category = await crud_category.update_category(db, category_id, category)
    return updated_category


@router.delete("/{category_id}", response_model=schema_category.Category)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    deleted_category = await crud_category.delete_category(db, category_id)
    return deleted_category


# Delete all categories
@router.delete("/", response_model=schema_category.Category)
async def delete_category(db: AsyncSession = Depends(get_db)):
    deleted_categories = await crud_category.delete_categories(db)
    return deleted_categories