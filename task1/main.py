from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select

from database import engine, create_db_and_tables, get_session
from models import Item


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Campus Lost & Found API",
    lifespan=lifespan
)


@app.get("/")
def home():
    return {"message": "Campus Lost & Found API is running"}


# 1. CREATE ITEM
@app.post("/items", response_model=Item, status_code=201)
def create_item(
    item: Item,
    session: Session = Depends(get_session)
):
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


# 2. GET ALL ITEMS
@app.get("/items", response_model=list[Item])
def get_items(
    session: Session = Depends(get_session)
):
    items = session.exec(select(Item)).all()
    return items


# 3. GET ITEM BY ID
@app.get("/items/{item_id}", response_model=Item)
def get_item(
    item_id: int,
    session: Session = Depends(get_session)
):
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return item


# 4. UPDATE ITEM
@app.put("/items/{item_id}", response_model=Item)
def update_item(
    item_id: int,
    updated_item: Item,
    session: Session = Depends(get_session)
):
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    item.title = updated_item.title
    item.description = updated_item.description
    item.category = updated_item.category
    item.location = updated_item.location
    item.reported_by = updated_item.reported_by
    item.status = updated_item.status

    session.add(item)
    session.commit()
    session.refresh(item)

    return item


# 5. DELETE ITEM
@app.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    session: Session = Depends(get_session)
):
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    session.delete(item)
    session.commit()

    return {"message": "Item deleted successfully"}


# 6. FILTER BY STATUS
@app.get("/items/status/{status}", response_model=list[Item])
def get_items_by_status(
    status: str,
    session: Session = Depends(get_session)
):
    status = status.strip().capitalize()

    if status not in ["Lost", "Found", "Returned"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be Lost, Found, or Returned"
        )

    statement = select(Item).where(Item.status == status)
    items = session.exec(statement).all()

    return items


# 7. FILTER BY CATEGORY
@app.get("/items/category/{category}", response_model=list[Item])
def get_items_by_category(
    category: str,
    session: Session = Depends(get_session)
):
    statement = select(Item).where(Item.category == category)
    items = session.exec(statement).all()

    return items