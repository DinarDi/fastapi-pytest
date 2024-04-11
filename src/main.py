from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI

from core import settings
from database import db_manager
from api_v1 import router as router_v1


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db_manager.init_connection(settings.DB_URL)
    yield
    await db_manager.close_connection()


app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix='/api/v1')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
    )
