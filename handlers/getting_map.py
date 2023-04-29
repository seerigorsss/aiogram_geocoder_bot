from aiogram import Router, F
from aiogram.filters import Command
from aiogram.utils.markdown import hide_link
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, URLInputFile
from geocode.main import static_maps, geocode_object

from keyboards.simple_row import make_row_keyboard

router = Router()

map_types = ["Схема", "Спутник", "Гибрид"]
map_dict = dict(zip(map_types, ['map', 'sat', 'sat,skl']))


class ChooseMap(StatesGroup):
    selecting_place = State()
    choosing_map_type = State()


@router.message(Command("geocode"))
async def cmd_geocode(message: Message, state: FSMContext):
    await message.answer(
        text="Введите название местности:\n"
             "Если хотите отменить действие, отправьте /cancel",
    )
    # Устанавливаем пользователю состояние "вводит название местности"
    await state.set_state(ChooseMap.selecting_place)


@router.message(
    ChooseMap.selecting_place,
)
async def choosing_map_type(message: Message, state: FSMContext):
    await state.update_data(selected_place=message.text)
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите тип карты:",
        reply_markup=make_row_keyboard(map_types)
    )
    await state.set_state(ChooseMap.choosing_map_type)


@router.message(ChooseMap.choosing_map_type, F.text.in_(map_types))
async def map_type_chosen(message: Message, state: FSMContext):
    await state.update_data(selected_map_type=message.text)
    user_data = await state.get_data()
    geocode_name = user_data['selected_place']
    map_type = map_dict[user_data['selected_map_type']]
    geocode_status = geocode_object(geocode_name)
    if "OK" in geocode_status.keys():
        result_url = static_maps(geocode_status["OK"], map_type)
        image_from_url = URLInputFile(result_url)
        await message.answer_photo(
            image_from_url,
            caption=f"<b>{geocode_name}</b>"
        )
        await message.answer(
            text=f"Отлично, ниже карта введеной местности.\n"
                 f"Вы можете снова получить карту местности, отправив /geocode",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
    else:
        await message.answer(
            text=f"Возникла ошибка при обработке запроса.\n"
                 f"{geocode_status['error']}\n"
                 f"Попробуйте снова: /geocode",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()


@router.message(ChooseMap.choosing_map_type)
async def map_type_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого типа карты.\n\n"
             "Пожалуйста, выберите одно из названий из списка ниже:",
        reply_markup=make_row_keyboard(map_types)
    )
