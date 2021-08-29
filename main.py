from enum import Enum
from typing import List

import databases
import sqlalchemy
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

DATABASE_URL = "postgresql://postgres:mirniy@localhost:5432/postgres"

database = databases.Database(DATABASE_URL)

# Create table from the metadata object
metadata = sqlalchemy.MetaData()

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("order_id", sqlalchemy.String(5), primary_key=True),
    sqlalchemy.Column("status", sqlalchemy.String(20)),
)

# Create the SQLAlchemy engine
engine = sqlalchemy.create_engine(DATABASE_URL)

metadata.create_all(engine)


class StatusEnum(str, Enum):
    processing = "processing"
    in_progress = "in_progress"
    delivered = "delivered"


# Create Pydantic models that will be used when reading data, when returning it from the API.
class Order(BaseModel):
    """."""

    order_id: str
    status: StatusEnum

    class Config:
        min_anystr_length = 2
        max_anystr_length = 5
        anystr_lower = True


# Create FastAPI application
app = FastAPI()


# Create event handler to connect from the database
@app.on_event("startup")
async def startup():
    await database.connect()


# Create event handler to disconnect from the database
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/orders/", response_model=List[Order])
async def get_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.post("/orders/", response_model=Order)
async def create_order(order: Order):
    order_in_db = orders.select().where(orders.c.order_id == order.order_id)
    if await database.fetch_one(order_in_db):
        update_order = (
            orders.update()
            .where(orders.c.order_id == order.order_id)
            .values(status=order.status)
        )
        await database.execute(update_order)
    else:
        new_order = orders.insert().values(order_id=order.order_id, status=order.status)
        await database.execute(new_order)
    return order.dict()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
