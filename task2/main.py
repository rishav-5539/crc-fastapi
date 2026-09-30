from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Session, select

from database import engine
from models import Event, Reservation


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Campus Event Seat Reservation API",
    description="API for managing college events and student reservations",
    version="1.0.0",
    lifespan=lifespan
)


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():
    return {
        "message": "Campus Event Seat Reservation API is running"
    }


# ==================================================
# EVENT APIs
# ==================================================

# CREATE EVENT
@app.post("/events")
def create_event(event: Event):

    if event.capacity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Capacity must be greater than 0"
        )

    if event.status not in ["Open", "Closed"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be Open or Closed"
        )

    with Session(engine) as session:

        session.add(event)
        session.commit()
        session.refresh(event)

        return event


# GET ALL EVENTS
@app.get("/events")
def get_events():

    with Session(engine) as session:

        events = session.exec(
            select(Event)
        ).all()

        return events


# GET SINGLE EVENT
@app.get("/events/{event_id}")
def get_event(event_id: int):

    with Session(engine) as session:

        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        return event


# UPDATE EVENT
@app.put("/events/{event_id}")
def update_event(event_id: int, updated_event: Event):

    if updated_event.capacity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Capacity must be greater than 0"
        )

    if updated_event.status not in ["Open", "Closed"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be Open or Closed"
        )

    with Session(engine) as session:

        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        event.title = updated_event.title
        event.venue = updated_event.venue
        event.capacity = updated_event.capacity
        event.organizer = updated_event.organizer
        event.status = updated_event.status

        session.add(event)
        session.commit()
        session.refresh(event)

        return event


# DELETE EVENT
@app.delete("/events/{event_id}")
def delete_event(event_id: int):

    with Session(engine) as session:

        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        session.delete(event)
        session.commit()

        return {
            "message": "Event deleted successfully"
        }


# ==================================================
# RESERVATION APIs
# ==================================================

# CREATE RESERVATION
@app.post("/events/{event_id}/reserve")
def create_reservation(
    event_id: int,
    reservation: Reservation
):

    with Session(engine) as session:

        # Check whether event exists
        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        # Check whether event is open
        if event.status != "Open":
            raise HTTPException(
                status_code=400,
                detail="Event is closed"
            )

        # Make sure reservation uses correct event ID
        reservation.event_id = event_id

        # Count existing reservations
        statement = select(Reservation).where(
            Reservation.event_id == event_id
        )

        existing_reservations = session.exec(
            statement
        ).all()

        booked = len(existing_reservations)

        # Check whether event is full
        if booked >= event.capacity:
            raise HTTPException(
                status_code=400,
                detail="Event is full"
            )

        # Create reservation
        session.add(reservation)
        session.commit()
        session.refresh(reservation)

        return reservation


# GET EVENT RESERVATIONS
@app.get("/events/{event_id}/reservations")
def get_event_reservations(event_id: int):

    with Session(engine) as session:

        # Check event exists
        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        statement = select(Reservation).where(
            Reservation.event_id == event_id
        )

        reservations = session.exec(
            statement
        ).all()

        return reservations


# DELETE RESERVATION
@app.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int):

    with Session(engine) as session:

        reservation = session.get(
            Reservation,
            reservation_id
        )

        if not reservation:
            raise HTTPException(
                status_code=404,
                detail="Reservation not found"
            )

        session.delete(reservation)
        session.commit()

        return {
            "message": "Reservation cancelled successfully"
        }


# GET EVENT AVAILABILITY
@app.get("/events/{event_id}/availability")
def get_availability(event_id: int):

    with Session(engine) as session:

        # Check event exists
        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        # Get reservations
        statement = select(Reservation).where(
            Reservation.event_id == event_id
        )

        reservations = session.exec(
            statement
        ).all()

        booked = len(reservations)

        remaining = event.capacity - booked

        return {
            "capacity": event.capacity,
            "booked": booked,
            "remaining": remaining
        }