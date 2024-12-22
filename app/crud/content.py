from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.content import Content
from ..schemas.content import ContentCreate, ContentUpdate
from sqlalchemy.exc import IntegrityError
from loguru import logger


async def get_content(db: AsyncSession, content_id: int):
    result = await db.execute(select(Content).where(Content.id == content_id))
    return result.scalars().first()


async def get_contents(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    field: str = None,
    value: str = None,
):
    result = await db.execute(
        select(Content).order_by(desc(Content.created_at)).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_filtered_contents(
    db: AsyncSession, field: str, value, skip: int = 0, limit: int = 10
):
    try:
        value = int(value) if field == "source_id" else value.lower()
        filter_column = getattr(Content, field)
        print(field, value)

        if field == "type" or field == "source_id":
            condition = filter_column == value
            stmt = (
                select(Content)
                .where(condition)
                .order_by(desc(Content.created_at))
                .limit(limit)
                .offset(skip)
            )

        else:
            condition = filter_column.ilike(f"%{value}%")
            stmt = (
                select(Content)
                .where(condition)
                .order_by(desc(Content.created_at))
                .offset(skip)
                .limit(limit)
            )

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
    filter_column = getattr(Content, field)
    if cond_field and cond_value:
        stmt = (
            select(filter_column)
            .where(getattr(Content, cond_field) == cond_value)
            .order_by(desc(Content.created_at))
            .offset(skip)
            .limit(limit)
        )
    else:
        stmt = select(filter_column).offset(skip).limit(limit)
    result = await db.execute(stmt)

    return result.scalars().all()


async def get_source_item_ids(db: AsyncSession, source_id: int, limit: int = None):
    result = await get_specific_column(
        db, field="id", cond_field="source_id", cond_value=source_id
    )
    return result


async def create_content(db: AsyncSession, content: ContentCreate):
    try:
        if isinstance(content, dict):
            db_content = Content(**content)
        else:
            db_content = Content(**content.dict())

        db.add(db_content)
        await db.commit()
        await db.refresh(db_content)
        return db_content
    except IntegrityError as e:
        if "unique constraint" in str(e.orig).lower():
            logger.warning("Duplicate article skipped")
        else:
            logger.error(f"Database integrity error: {e}")
    except Exception as e:
        logger.error(f"Error creating content: {e}")
        await db.rollback()


async def update_content(db: AsyncSession, content_id: int, content: ContentUpdate):
    db_content = await get_content(db, content_id)
    if db_content:
        for key, value in Content.dict().items():
            setattr(db_content, key, value)
        await db.commit()
        return db_content
    else:
        raise Exception(f"content with id {id} not found")


async def delete_content(db: AsyncSession, content_id: int):
    db_content = await get_content(db, content_id)
    if db_content:
        await db.delete(db_content)
        await db.commit()
        return db_content
    else:
        raise Exception(f"content with id {content_id} not found")


async def delete_contents(db: AsyncSession):
    # Delete all contents
    stmt = select(Content)
    result = await db.execute(stmt)
    db_contents = result.scalars().all()

    for db_content in db_contents:
        await db.delete(db_content)

    await db.commit()
    return db_contents
