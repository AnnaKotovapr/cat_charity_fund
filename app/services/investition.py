from datetime import datetime
from typing import List, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def investing(
    obj_in: Union[CharityProject, Donation],
    session: AsyncSession
) -> Union[CharityProject, Donation]:

    invested_model = determine_invested_model(obj_in)

    not_invested_objects = await non_invested_objects(
        invested_model, session
    )

    if not_invested_objects:
        await process_investments(obj_in, not_invested_objects, session)

    return obj_in


def determine_invested_model(
        obj: Union[CharityProject, Donation]
) -> type:
    if isinstance(obj, Donation):
        invested_model = CharityProject
        return invested_model
    invested_model = Donation
    return invested_model


async def non_invested_objects(
    model: Union[CharityProject, Donation],
    session: AsyncSession
) -> List[Union[CharityProject, Donation]]:

    objects = await session.execute(
        select(model).where(
            model.fully_invested is not True).order_by(
                model.create_date)
    )
    return objects.scalars().all()


async def process_investments(
        obj_in: Union[CharityProject, Donation],
        not_invested_objects: List[Union[CharityProject, Donation]],
        session: AsyncSession
) -> None:

    available_amount = obj_in.full_amount

    for obj in not_invested_objects:
        need_amount = obj.full_amount - obj.invested_amount
        investment = min(need_amount, available_amount)

        available_amount -= investment
        obj.invested_amount += investment
        obj_in.invested_amount += investment

        if obj.full_amount == obj.invested_amount:
            close_invested_object(obj)

        if not available_amount:
            close_invested_object(obj_in)
            break

    await session.commit()


def close_invested_object(
        obj: Union[CharityProject, Donation],
) -> None:

    obj.fully_invested = True
    obj.close_date = datetime.now()
