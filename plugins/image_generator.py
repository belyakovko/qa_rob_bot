from aiogram.types import Message, BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from PIL import Image, ImageDraw, ImageFont
import io
import logging
import re
from messages import get_back_menu, get_main_menu, WELCOME_MSG

logger = logging.getLogger(__name__)

# Константы
MAX_SIZE = 5000
SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
DEFAULT_COLOR = (255, 255, 255)  # Белый
TEXT_COLOR = (0, 0, 0)  # Черный

class ImageGeneratorStates(StatesGroup):
    waiting_for_format = State()
    waiting_for_params = State()
    waiting_for_choice = State()  # Новое состояние для выбора действия

async def generate_image_command(message: Message, state: FSMContext):
    await state.set_state(ImageGeneratorStates.waiting_for_format)
    
    format_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="JPG"), KeyboardButton(text="PNG")],
            [KeyboardButton(text="GIF"), KeyboardButton(text="BMP")],
            [KeyboardButton(text="Назад в меню")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "📝 Выберите формат изображения:",
        reply_markup=format_keyboard
    )

async def process_format_choice(message: Message, state: FSMContext):
    if message.text == "Назад в меню":
        await state.clear()
        from messages import MENU_MSG, get_main_menu  # Изменено: импортируем MENU_MSG вместо WELCOME_MSG
        await message.answer(MENU_MSG, reply_markup=get_main_menu())  # Используем MENU_MSG
        return
      
    format_map = {
        "JPG": "jpg",
        "PNG": "png",
        "GIF": "gif",
        "BMP": "bmp"
    }
    
    if message.text not in format_map:
        await message.answer("Пожалуйста, выберите формат из предложенных вариантов")
        return
    
    await state.update_data(format=format_map[message.text])
    await send_size_prompt(message, state)

async def send_size_prompt(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_format = data['format']
    
    examples = {
        "jpg": "300 #FF5733 (красный квадрат)\n800 600 (белый прямоугольник)",
        "png": "500 (квадрат 500x500)\n1024 768 #00FF00 (зеленый прямоугольник)",
        "gif": "200 #FFFF00 (желтый квадрат)\n400 400 (белый квадрат)",
        "bmp": "300 300 #0000FF (синий квадрат)\n600 400 (белый прямоугольник)"
    }[selected_format]
    
    await message.answer(
        f"🖼 Вы выбрали <b>{selected_format.upper()}</b> формат\n\n"
        "📏 Теперь введите параметры изображения:\n"
        "• <code>размер</code> - для квадратного изображения\n"
        "• <code>ширина высота</code> - для прямоугольного\n"
        "• Можно добавить цвет в формате #RRGGBB\n\n"
        "📋 Примеры:\n"
        f"<code>{examples}</code>\n\n"
        "Например:\n"
        f"<code>500</code> - квадрат 500x500\n"
        f"<code>800 600 #FF0000</code> - красный прямоугольник\n\n"
        "❓ Просто введите нужные параметры в чат",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Назад")],  # Возврат к выбору формата
                [KeyboardButton(text="Назад в меню")]  # Новая кнопка для возврата в главное меню
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(ImageGeneratorStates.waiting_for_params)

async def process_image_params(message: Message, state: FSMContext):
    if message.text == "Назад":
        await generate_image_command(message, state)
        return
    elif message.text == "Назад в меню":
        await state.clear()
        await message.answer(WELCOME_MSG, reply_markup=get_main_menu())
        return
    
    try:
        data = await state.get_data()
        ext = data['format']
        parts = message.text.split()
        
        # Определяем параметры
        if len(parts) == 1:
            if parts[0].startswith('#'):
                raise ValueError("Сначала укажите размер, затем цвет")
            size = int(parts[0])
            width = height = size
            color = DEFAULT_COLOR
        elif len(parts) == 2:
            if parts[1].startswith('#'):
                size = int(parts[0])
                width = height = size
                hex_color = parts[1]
            else:
                width = int(parts[0])
                height = int(parts[1])
                color = DEFAULT_COLOR
        elif len(parts) == 3:
            width = int(parts[0])
            height = int(parts[1])
            hex_color = parts[2]
        else:
            raise ValueError("Неверное количество параметров")

        if 'hex_color' in locals():
            if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hex_color):
                raise ValueError("Неверный формат цвета. Используйте HEX (например: #FF5733)")
            hex_color = hex_color.lstrip('#')
            color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        if width <= 0 or height <= 0:
            raise ValueError("Размеры должны быть положительными числами")
        if width > MAX_SIZE or height > MAX_SIZE:
            raise ValueError(f"Максимальный размер: {MAX_SIZE}px")
        
        img = Image.new('RGB', (width, height), color=color)
        d = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", size=min(width, height)//10)
        except:
            font = ImageFont.load_default()
        
        text = f"{width}x{height}\n.{ext}"
        text_bbox = d.textbbox((0, 0), text, font=font)
        x = (width - (text_bbox[2] - text_bbox[0])) / 2
        y = (height - (text_bbox[3] - text_bbox[1])) / 2
        d.text((x, y), text, font=font, fill=TEXT_COLOR)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=ext if ext != 'jpg' else 'JPEG')
        
        await message.answer_photo(
            photo=BufferedInputFile(
                file=img_byte_arr.getvalue(),
                filename=f"image_{width}x{height}.{ext}"
            ),
            caption=f"✅ Готово! {width}x{height}.{ext}"
        )
        
        # Предлагаем создать еще или вернуться в меню
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Создать ещё")],
                [KeyboardButton(text="Назад в меню")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            "Хотите создать ещё одно изображение?",
            reply_markup=keyboard
        )
        await state.set_state(ImageGeneratorStates.waiting_for_choice)
        
    except ValueError as e:
        await message.answer(f"❌ Ошибка: {e}\nПопробуйте еще раз")
    except Exception as e:
        logger.error(f"Image generation error: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка при создании изображения")
        await state.clear()

async def handle_choice(message: Message, state: FSMContext):
    if message.text == "Создать ещё":
        await generate_image_command(message, state)
    elif message.text == "Назад в меню":
        await state.clear()
        from messages import MENU_MSG, get_main_menu
        await message.answer(MENU_MSG, reply_markup=get_main_menu())  # Используем MENU_MSG
    else:
        await message.answer("Пожалуйста, используйте кнопки")