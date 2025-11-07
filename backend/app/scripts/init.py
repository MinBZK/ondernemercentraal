import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import true

import app.controllers.user as user_controller
from app.config import form_schemas, partner_organizations, product_categories, track_types
from app.controllers.product import get_products_by_names
from app.core import settings
from app.core.database import async_session
from app.core.models import (
    AppointmentType,
    AvailabilityDated,
    AvailabilitySlot,
    AvailabilitySlotDefined,
    FormTemplate,
    PartnerOrganization,
    Product,
    ProductCategory,
    Role,
    TrackType,
    User,
)
from app.core.types import AppointmentTypeName, FormNames, RoleNames
from app.schemas.user import UserCreate


async def init_slots(session: AsyncSession):
    availability_dated_existing = await session.scalar(
        select(AvailabilityDated).where(AvailabilityDated.default == true())
    )

    if availability_dated_existing:
        return

    # Init slot
    slot_morning = AvailabilitySlot(hour_start=9, hour_end=12)
    slot_afternoon = AvailabilitySlot(hour_start=13, hour_end=17)
    session.add(slot_morning)
    session.add(slot_afternoon)

    if not availability_dated_existing:
        # Init default defined slots
        session.add(
            AvailabilityDated(
                default=True,
                _availability_slots_defined=[
                    AvailabilitySlotDefined(availability_slot=slot_morning, capacity=1),
                    AvailabilitySlotDefined(availability_slot=slot_afternoon, capacity=1),
                ],
            )
        )


async def init_types(session: AsyncSession):
    appointment_type_names: list[AppointmentTypeName] = ["Checkgesprek", "Toekomstgesprek", "SHVO intake"]
    existing_at = list(await session.scalars(select(AppointmentType)))
    missing_at = [a_t for a_t in appointment_type_names if a_t not in [e_at.name for e_at in existing_at]]
    for a_t in missing_at:
        session.add(AppointmentType(name=a_t))

    existing_track_type = list(await session.scalars(select(TrackType)))
    missing_tt = [tt for tt in track_types if tt not in [tt.name for tt in existing_track_type]]
    for tt in missing_tt:
        session.add(TrackType(name=tt))

    roles: list[RoleNames] = ["adviseur", "beheerder", "partner", "ondernemer", "senioradviseur"]
    existing_roles = list(await session.scalars(select(Role)))
    missing_roles = [r for r in roles if r not in [r.name for r in existing_roles]]
    for r in missing_roles:
        session.add(Role(name=r))

    form_names = form_schemas.keys()
    existing_form_template_names: list[FormNames] = [t.name for t in list(await session.scalars(select(FormTemplate)))]
    missing_form_template_names = set(form_names) - set(existing_form_template_names)
    for n in missing_form_template_names:
        session.add(FormTemplate(name=n))


async def init_users(session: AsyncSession):
    users = list((await session.scalars(select(User))).unique())
    existing_users = [u.name for u in users]

    required_user_role: dict[str, RoleNames] = {
        "admin": "beheerder",
        "adviseur": "adviseur",
        "partner": "partner",
        "ondernemer": "ondernemer",
    }

    required_usernames = required_user_role.keys()

    missing_usernames = set(required_usernames) - set(existing_users)
    for u in missing_usernames:
        required_role_name = required_user_role[u]
        await user_controller.create_user(
            session=session,
            user_new=UserCreate(role_name=required_role_name, partner_organization_name=None, active=True, name=u),
            password_override=u,
        )


async def init_products(session: AsyncSession):
    existing_product_categories = list((await session.scalars(select(ProductCategory))).unique())
    existing_products = list((await session.scalars(select(Product))).unique())

    for pc in product_categories:
        pc_exists = next((e_pc for e_pc in existing_product_categories if e_pc.name == pc["name"]), None)
        if pc_exists:
            continue
        existing_product_names = [e_p.name for e_p in existing_products]
        missing_products = [p for p in pc["products"] if p not in existing_product_names]
        session.add(ProductCategory(name=pc["name"], products=[Product(name=p) for p in missing_products]))

    pc_default_exists = next((e_pc for e_pc in existing_product_categories if e_pc.name == "default"), None)
    if not pc_default_exists:
        session.add(
            ProductCategory(name="default", products=[Product(name=n) for n in settings.REQUIRED_PRODUCT_NAMES])
        )

    # products = list((await session.scalars(select(Product))).unique())
    # existing_product_names = set([p.name for p in products])
    # all_product_names = set(flatten_list([po["products"] for po in partner_organizations]))
    # required_product_names_str = {str(r) for r in settings.REQUIRED_PRODUCT_NAMES} | all_product_names
    # missing_product_names = list(required_product_names_str - existing_product_names)

    # required_product_category_name = "default"
    # query = select(ProductCategory).where(ProductCategory.name == required_product_category_name)
    # required_pc = await session.scalar(query)
    # if not required_pc:
    #     required_pc = ProductCategory(name=requiredf_product_category_name)
    #     session.add(required_pc)

    # for p in missing_product_names:
    #     session.add(Product(name=p, product_category=required_pc))


async def init_partner_organizations(session: AsyncSession):
    partner_orgs = list((await session.scalars(select(PartnerOrganization))).unique().all())
    existing_partner_organization_names = [po.name for po in partner_orgs]
    required_partner_organization_names = [po["organisatie_naam"] for po in partner_organizations]
    missing_partner_organization_names = set(required_partner_organization_names) - set(
        existing_partner_organization_names
    )

    for po in missing_partner_organization_names:
        partner_organization_config = next((p for p in partner_organizations if p["organisatie_naam"] == po), None)
        assert partner_organization_config, f"Configuration for {po} not found in partner_organizations"
        products = await get_products_by_names(partner_organization_config["products"], session=session)

        session.add(
            PartnerOrganization(
                name=po,
                description=partner_organization_config["description"],
                description_short=partner_organization_config["description_short"],
                products=products,
            )
        )


async def main():
    async with async_session.begin() as session:
        await init_slots(session)
        await session.flush()
        await init_types(session)
        await session.flush()
        await init_users(session)
        await session.flush()
        await init_products(session)
        await session.flush()
        await init_partner_organizations(session)
        await session.flush()


if __name__ == "__main__":
    asyncio.run(main())
