from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.webhook import Webhook
from ..schemas.webhook import WebhookCreate, WebhookUpdate


async def get_webhook(db: AsyncSession, webhook_id: int):
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    return result.scalars().first()


# modify to filter by given fields and values, if any


async def get_webhooks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    field: str = None,
    value: str = None,
):
    result = await db.execute(select(Webhook).offset(skip).limit(limit))
    return result.scalars().all()


# Function to filter by given fields if
async def get_filtered_webhooks(
    db: AsyncSession, field: str, value, skip: int = 0, limit: int = 10
):
    try:
        filter_column = getattr(Webhook, field)

        condition = filter_column.ilike(f"%{value}%")
        stmt = select(Webhook).where(condition).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return True, result.scalars().all()

    except Exception as e:
        return False, e


"""Get a column, adding this for the ids"""


async def get_specific_column(
    db: AsyncSession,
    field,
    limit: int = None,
    skip: int = 0,
    cond_field=None,
    cond_value=None,
):
    filter_column = getattr(Webhook, field)
    if cond_field and cond_value:
        stmt = (
            select(filter_column)
            .where(getattr(Webhook, cond_field) == cond_value)
            .offset(skip)
            .limit(limit)
        )
    else:
        stmt = select(filter_column).offset(skip).limit(limit)
    result = await db.execute(stmt)

    return result.scalars().all()


async def create_webhook(db: AsyncSession, webhook: WebhookCreate):
    db_webhook = Webhook(url=webhook.url, event=webhook.event)
    db.add(db_webhook)
    await db.commit()
    await db.refresh(db_webhook)
    await db.close()

    return db_webhook


async def update_webhook(db: AsyncSession, webhook_id: int, webhook: WebhookUpdate):
    db_webhook = await get_webhook(db, webhook_id)
    if db_webhook:
        for key, value in webhook.dict().items():
            setattr(db_webhook, key, value)
        await db.commit()
        await db.close()
        return db_webhook
    else:
        raise Exception(f"webhook with id {id} not found")


async def delete_webhook(db: AsyncSession, webhook_id: int):
    db_webhook = await get_webhook(db, webhook_id)
    if db_webhook:
        await db.delete(db_webhook)
        await db.commit()
        await db.close()
        return db_webhook
    else:
        raise Exception(f"webhook with id {webhook_id} not found")


async def delete_webhooks(db: AsyncSession):
    db_webhooks = await get_webhooks(db)

    try:
        if db_webhooks:
            await db.delete(db_webhooks)
            await db.commit()
            await db.close()
            return db_webhooks
        else:
            raise Exception("No webhooks found")

    except Exception as e:
        raise Exception(e)
