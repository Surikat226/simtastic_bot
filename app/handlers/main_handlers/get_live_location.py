from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiohttp import ClientSession
from app.states.main_states import MainStates
from app.utils.logging import log_handler
from app.config import GEO_SERVICE_URL


get_live_location_router = Router()


@get_live_location_router.message(F.location)
@log_handler
async def live_location_updates(message: types.Message, state: FSMContext):
    """
    Обрабатывает начало стриминга геопозиции и принимает начальные координаты
    """

    loc = message.location
    if loc.live_period:  # Если есть live_period, значит был включён режим стриминга гео
        await message.answer("✅ Отлично! Ты начал транслировать live-локацию 🚴")
        await state.set_state(MainStates.get_live_location_menu)
    else:
        await message.answer(
            "ℹ️ Ты отправил разовую точку - это не совсем то, что нужно :(\n"
            "Попробуй ещё раз отправить свою геопозицию в реальном времени (воспользуйся инструкцией выше)"
        )


@get_live_location_router.edited_message(F.location)
@log_handler
async def live_location_updates(message: types.Message):
    """
    Принимает обновления геопозиции от пользователя
    """

    loc = message.location
    async with ClientSession() as session:
        await session.post(
            url=f"{GEO_SERVICE_URL}/coordinates",
            json={
                "user_id": message.from_user.id,
                "user_name": message.from_user.username,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "timestamp": message.date.isoformat()
            }
        )
