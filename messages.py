from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Основное меню
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Генератор изображений"),
                KeyboardButton(text="Генератор платежных данных"),
            ],
            [
                KeyboardButton(text="Генератор Pairwise тестов"),
                KeyboardButton(text="Валидатор JSON")
            ],
            [
                KeyboardButton(text="Информация")
            ]
        ],
        resize_keyboard=True
    )

# Меню с кнопкой Назад
def get_back_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Назад в меню")]
        ],
        resize_keyboard=True
    )

# Текстовые сообщения
WELCOME_MSG = "Добро пожаловать в QA_Rob_Bot! 🤖\n\nВыберите нужный инструмент:"
MENU_MSG = "Выберите нужный инструмент:"
HELP_MSG = (
    "Доступные команды:\n"
    "/genimage - генератор изображений\n"
    "/genpayment - генератор платежных данных\n"
    "/pairwise - генератор pairwise тестов\n"
    "/validatejson - валидатор JSON\n"
    "/cancel - отмена текущей операции\n"
    "/help - вызов справки\n\n"
    "Или используйте кнопки меню ниже"
)