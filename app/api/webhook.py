from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..crud import webhook as crud_webhook
from ..schemas import webhook as schema_webhook
from ..core.database import get_db

router = APIRouter(
    tags=["webhooks"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schema_webhook.Webhook, status_code=201)
async def create_webhook(
    webhook: schema_webhook.WebhookCreate, db: AsyncSession = Depends(get_db)
):
    try: 
        created_webhook = await crud_webhook.create_webhook(db, webhook)
        return created_webhook
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Add some optional params, such that the webhook can be filtered,
#  not just by the id
# but also byt other fields

@router.get("/", response_model=List[schema_webhook.Webhook])
async def get_webhooks(
    field: Optional[str] = None,
    value = None,
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db),
):     
    if field:
        return await get_by_fields(db, skip, limit, field, value)

    return await crud_webhook.get_webhooks(db, skip, limit) 


# Function to handle optional fields
async def get_by_fields(db: AsyncSession, skip: int, limit: int, field: str, value):
    field = field.lower()
    # Create an array of all the model fields
    model_dict = schema_webhook.Webhook.__dict__.items()
    model_fields = {key: value for key, value in model_dict if not key.startswith('__')}
    model_fields = model_fields['model_fields'].keys()
    
    if field not in model_fields:
        raise HTTPException(status_code=404, detail=f"Provided field, {field} is not found")  
    
    status, webhooks = await crud_webhook.get_filtered_webhooks(db, field, value, skip, limit)
    if not status:
        raise HTTPException(status_code=404, detail=f"No such record found: {webhooks}")  

    return webhooks


@router.get("/{webhook_id}", response_model=schema_webhook.Webhook)
async def get_webhook(webhook_id: str, db: AsyncSession = Depends(get_db)):
    webhook = await crud_webhook.get_webhook(db, webhook_id)
    if webhook is None:
        raise HTTPException(status_code=404, detail="webhook not found")
    return webhook


@router.patch("/{webhook_id}", response_model=schema_webhook.Webhook, status_code=200)
async def update_webhook(
    webhook_id: str,
    webhook: schema_webhook.WebhookUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_webhook = await crud_webhook.update_webhook(db, webhook_id, webhook)
    return updated_webhook


@router.delete("/{webhook_id}", response_model=schema_webhook.Webhook)
async def delete_webhook(webhook_id: str, db: AsyncSession = Depends(get_db)):
    deleted_webhook = await crud_webhook.delete_webhook(db, webhook_id)
    return deleted_webhook


# Delete all webhooks
@router.delete("/", response_model=schema_webhook.Webhook)
async def delete_all(db: AsyncSession = Depends(get_db)):
    deleted_webhook = await crud_webhook.delete_webhooks(db)
    return deleted_webhook