from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charityproject_crud
from app.models import CharityProject


CANNOT_DELETE_AN_INVESTED_PROJECT = (
    'В проект были внесены средства, не подлежит удалению!'
)
ERROR_UPDATING_CLOSED_PROJECT = (
    'Закрытый проект нельзя редактировать!'
)
ERROR_PROJECT_WITH_THIS_NAME_EXISTS = (
    'Проект с таким именем уже существует!'
)
ERROR_LOW_FULL_AMOUNT = (
    'Значение требуемой не может быть меньше внесённой'
)
ERROR_PROJECT_NOT_FOUND = 'Проект не найден!'


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession,
) -> None:
    project_id = await charityproject_crud.get_project_id_by_name(
        project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_PROJECT_WITH_THIS_NAME_EXISTS,
        )


async def check_charityproject_exists(
    charityproject_id: int,
    session: AsyncSession,
) -> CharityProject:
    project = await charityproject_crud.get(
        charityproject_id, session
    )
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_PROJECT_NOT_FOUND
        )
    return project


async def check_project_invested(
    project_id: int,
    session: AsyncSession
) -> None:
    invested_project = await charityproject_crud.get_project_invested_amount(
        project_id, session
    )

    if invested_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=CANNOT_DELETE_AN_INVESTED_PROJECT,
        )


async def charity_project_closed(
    project_id: int,
    session: AsyncSession,
) -> None:
    project_closed = await charityproject_crud.get_project_fully_invested(
        project_id, session
    )
    if project_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_UPDATING_CLOSED_PROJECT,
        )


async def check_updating_full_amount(
    project_id: int,
    updating_full_amount: int,
    session: AsyncSession,
) -> None:
    invested_amount = await charityproject_crud.get_project_invested_amount(
        project_id, session
    )
    if updating_full_amount < invested_amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ERROR_LOW_FULL_AMOUNT,
        )
