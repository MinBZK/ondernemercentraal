import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.models as models
from app.core.types import AppointmentTypeName


@pytest.fixture(scope="session")
async def case(
    session: AsyncSession,
):
    client = models.Client(
        initials="T",
        last_name="Test",
        company_location="Utrecht",
        residence_location="Utrecht",
        company_name="Test Company",
        kvk_number="12345678",
        bsn="123456789",
        phone_number="0612345678",
        agree_to_share_data=True,
        email="test@test.test",
        email_confirmed=False,
    )
    session.add(client)
    await session.flush()
    case = models.Case(client=client)
    session.add(case)
    await session.flush()
    yield case
    await session.delete(case)
    await session.flush()


@pytest.fixture(scope="session")
async def appointment_type(
    session: AsyncSession,
):
    appointment_type_name: AppointmentTypeName = "Checkgesprek"
    appointment_type = models.AppointmentType(name=appointment_type_name)
    session.add(appointment_type)
    await session.flush()
    yield appointment_type
    await session.delete(appointment_type)
    await session.flush()


@pytest.fixture(scope="session")
async def appointment(
    session: AsyncSession,
    case: models.Case,
    appointment_type: models.AppointmentType,
):
    appointment_types = list(await session.scalars(select(models.AppointmentType)))
    assert len(appointment_types) > 0
    appointment_type = appointment_types[0]

    start_time = datetime.datetime(year=2025, month=6, day=10, hour=10, minute=0)
    end_time = start_time + datetime.timedelta(hours=1)

    appointment = models.Appointment(
        start_time=start_time, end_time=end_time, case=case, appointment_type=appointment_type, status="Open"
    )
    session.add(appointment)
    await session.flush()
    yield appointment
    await session.delete(appointment)
    await session.flush()
