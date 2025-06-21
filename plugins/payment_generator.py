from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random
import logging
from messages import get_main_menu

logger = logging.getLogger(__name__)

class PaymentGeneratorStates(StatesGroup):
    waiting_for_payment_system = State()

PAYMENT_SYSTEMS = ['Visa', 'Mastercard', 'UnionPay', 'JCB', 'Mir']

async def generate_payment_command(message: Message, state: FSMContext):
    await state.clear()
    
    # Создаем клавиатуру с системами и кнопкой "Назад"
    builder = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=system)] for system in PAYMENT_SYSTEMS
        ] + [
            [KeyboardButton(text="Назад в меню")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "💳 Выберите платежную систему:",
        reply_markup=builder
    )
    await state.set_state(PaymentGeneratorStates.waiting_for_payment_system)

async def process_payment_system(message: Message, state: FSMContext):
    # Обработка кнопки "Назад в меню"
    if message.text == "Назад в меню":
        await state.clear()
        await message.answer(
            "Добро пожаловать в QA Helper Bot! 🤖\n\nВыберите нужный инструмент:",
            reply_markup=get_main_menu()
        )
        return
    
    # Проверка выбора системы
    if message.text not in PAYMENT_SYSTEMS:
        await message.answer(
            "⚠ Пожалуйста, выберите систему из списка",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=system)] for system in PAYMENT_SYSTEMS
                ] + [
                    [KeyboardButton(text="Назад в меню")]
                ],
                resize_keyboard=True
            )
        )
        return
    
    try:
        # Генерация тестовых данных
        card_number = generate_card_number(message.text)
        expiry_date = f"{random.randint(1, 12):02d}/{random.randint(23, 30)}"
        cvv = f"{random.randint(0, 999):03d}"
        
        await message.answer(
            "🔹 <b>Тестовые платежные данные</b>\n\n"
            f"▪ <b>Система:</b> {message.text}\n"
            f"▪ <b>Номер карты:</b> <code>{card_number}</code>\n"
            f"▪ <b>Срок действия:</b> {expiry_date}\n"
            f"▪ <b>CVV/CVC:</b> <code>{cvv}</code>\n\n"
            "<i>Это тестовые данные для QA-тестирования</i>",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        logger.error(f"Payment data error: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при генерации данных",
            reply_markup=get_main_menu()
        )
    
    await state.clear()

def generate_card_number(system: str) -> str:
    """Генерирует валидный номер карты по алгоритму Луна"""
    prefixes = {
        'Visa': ['4'],
        'Mastercard': ['51', '52', '53', '54', '55'],
        'UnionPay': ['62'],
        'JCB': ['35'],
        'Mir': ['2']
    }
    
    prefix = random.choice(prefixes.get(system, ['4']))
    number = prefix
    
    # Генерация основной части номера
    while len(number) < 15:
        number += str(random.randint(0, 9))
    
    # Расчет контрольной суммы
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