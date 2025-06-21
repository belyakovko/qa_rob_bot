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
                KeyboardButton(text="Генератор pairwise тестов"),
                KeyboardButton(text="/help")
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
WELCOME_MSG = "Добро пожаловать в QA Helper Bot! 🤖\n\nВыберите нужный инструмент:"
MENU_MSG = "Выберите нужный инструмент:"
HELP_MSG = (
    "Доступные команды:\n"
    "/genimage - генератор изображений\n"
    "/genpayment - генератор платежных данных\n"
    "/pairwise - генератор pairwise тестов\n"
    "/cancel - отмена текущей операции\n\n"
    "Или используйте кнопки меню ниже"
)