from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.database import DatabaseConnectionError, connect_to_database, disconnect_from_database

app = FastAPI()


@app.exception_handler(DatabaseConnectionError)
async def database_connection_exception_handler(
    request: Request, exc: DatabaseConnectionError
):
    return JSONResponse(
        status_code=500,
        content={"message": "Database connection failed", "details": exc.message},
    )


@app.on_event("startup")
async def startup():
    try:
        await connect_to_database()
        print("connection is live")
    except Exception as e:
        raise e


@app.on_event("shutdown")
async def shutdown():
    await disconnect_from_database()


@app.get("/")
async def read_root():
    return {"Hello": "World"}
