from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random
import logging
from messages import get_main_menu, MENU_MSG

logger = logging.getLogger(__name__)

class PaymentGeneratorStates(StatesGroup):
    waiting_for_payment_system = State()
    waiting_for_regenerate_choice = State()

PAYMENT_SYSTEMS = ['Visa', 'Mastercard', 'UnionPay', 'JCB', 'Mir']

async def generate_payment_command(message: Message, state: FSMContext):
    await show_payment_systems_menu(message, state)

async def show_payment_systems_menu(message: Message, state: FSMContext):
    builder = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=system)] for system in PAYMENT_SYSTEMS
        ] + [
            [KeyboardButton(text="Назад в меню")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("💳 Выберите платежную систему:", reply_markup=builder)
    await state.set_state(PaymentGeneratorStates.waiting_for_payment_system)

async def process_payment_system(message: Message, state: FSMContext):
    if message.text == "Назад в меню":
        await state.clear()
        await message.answer(MENU_MSG, reply_markup=get_main_menu())
        return
    
    if message.text not in PAYMENT_SYSTEMS:
        await message.answer("⚠ Пожалуйста, выберите систему из списка")
        return
    
    try:
        await generate_and_show_card(message, state, message.text)
    except Exception as e:
        logger.error(f"Payment data error: {e}", exc_info=True)
        await message.answer("❌ Ошибка при генерации данных", reply_markup=get_main_menu())
        await state.clear()

async def generate_and_show_card(message: Message, state: FSMContext, system: str):
    card_number = generate_card_number(system)
    expiry_date = f"{random.randint(1, 12):02d}/{random.randint(23, 30)}"
    cvv = f"{random.randint(0, 999):03d}"
    
    await message.answer(
        "🔹 <b>Тестовые платежные данные</b>\n\n"
        f"▪ <b>Система:</b> {system}\n"
        f"▪ <b>Номер карты:</b> <code>{card_number}</code>\n"
        f"▪ <b>Срок действия:</b> {expiry_date}\n"
        f"▪ <b>CVV/CVC:</b> <code>{cvv}</code>\n\n"
        "<i>Это тестовые данные для QA-тестирования</i>",
        parse_mode="HTML"
    )
    
    await ask_for_regenerate(message, state)

async def ask_for_regenerate(message: Message, state: FSMContext):
    builder = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать еще")],
            [KeyboardButton(text="Назад в меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("Хотите создать еще одну тестовую карту?", reply_markup=builder)
    await state.set_state(PaymentGeneratorStates.waiting_for_regenerate_choice)

async def process_regenerate_choice(message: Message, state: FSMContext):
    if message.text == "Создать еще":
        # Возвращаем пользователя к выбору платежной системы
        await show_payment_systems_menu(message, state)
    elif message.text == "Назад в меню":
        await state.clear()
        await message.answer(MENU_MSG, reply_markup=get_main_menu())
    else:
        await message.answer("Пожалуйста, используйте кнопки")

def generate_card_number(system: str) -> str:
    prefixes = {
        'Visa': ['4'],
        'Mastercard': ['51', '52', '53', '54', '55'],
        'UnionPay': ['62'],
        'JCB': ['35'],
        'Mir': ['2']
    }
    prefix = random.choice(prefixes.get(system, ['4']))
    number = prefix
    while len(number) < 15:
        number += str(random.randint(0, 9))
    total = 0
    for i, digit in enumerate(number):
        digit = int(digit)
        if i % 2 == 0:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    check_digit = (10 - (total % 10)) % 10
    return number + str(check_digit)