from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from allpairspy import AllPairs
import openpyxl
from io import BytesIO
import logging
from messages import get_main_menu, get_back_menu

logger = logging.getLogger(__name__)

class PairwiseStates(StatesGroup):
    waiting_for_parameters = State()

async def pairwise_command(message: Message, state: FSMContext):
    await state.set_state(PairwiseStates.waiting_for_parameters)
    await message.answer(
        "Введите параметры для pairwise тестирования в формате:\n"
        "'параметр1: значение1, значение2; параметр2: значение1, значение2'\n"
        "Пример: 'os: mac, win; size: 1000, 1200'\n\n"
        "Для возврата в меню нажмите 'Назад в меню'",
        reply_markup=get_back_menu()
    )

async def process_pairwise_parameters(message: Message, state: FSMContext):
    # Обработка кнопки "Назад в меню"
    if message.text == "Назад в меню":
        await state.clear()
        await message.answer(
            "Добро пожаловать в QA Helper Bot! 🤖\n\nВыберите нужный инструмент:",
            reply_markup=get_main_menu()
        )
        return
    
    try:
        # Парсим ввод пользователя
        parameters = {}
        input_text = message.text.strip()
        
        # Разбиваем на пары параметр: значения
        param_blocks = [block.strip() for block in input_text.split(';') if block.strip()]
        
        for block in param_blocks:
            if ':' not in block:
                await message.answer(
                    "❌ Ошибка формата. Используйте 'параметр: значение1, значение2'",
                    reply_markup=get_back_menu()
                )
                return
                
            param_name, values_str = block.split(':', 1)
            param_name = param_name.strip()
            values = [v.strip() for v in values_str.split(',') if v.strip()]
            
            if not param_name or not values:
                await message.answer(
                    "❌ Ошибка: параметр и значения не могут быть пустыми",
                    reply_markup=get_back_menu()
                )
                return
                
            parameters[param_name] = values
        
        if not parameters:
            await message.answer(
                "❌ Не удалось распознать параметры. Проверьте формат ввода.",
                reply_markup=get_back_menu()
            )
            return
        
        # Генерируем комбинации
        pairwise_combinations = list(AllPairs(parameters.values()))
        
        # Формируем текстовый отчет
        report = (
            f"🔹 <b>Pairwise тестирование</b>\n\n"
            f"<b>Параметры:</b>\n" +
            "\n".join(f"• {param}: {', '.join(values)}" for param, values in parameters.items()) +
            f"\n\n<b>Оптимальное количество тестов:</b> {len(pairwise_combinations)}"
        )
        
        # Создаем Excel файл
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Pairwise Tests"
        
        # Записываем параметры
        ws.append(["Параметр", "Значения"])
        for param, values in parameters.items():
            ws.append([param, ", ".join(values)])
        
        # Записываем тесты
        ws.append([])
        ws.append(["Тест #"] + list(parameters.keys()))
        for i, test in enumerate(pairwise_combinations, 1):
            ws.append([i] + list(test))
        
        # Сохраняем в буфер
        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        # Отправляем результат
        await message.answer(report, parse_mode="HTML")
        await message.answer_document(
            document=excel_buffer,
            filename="pairwise_tests.xlsx",
            caption="Excel файл с тестами",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        logger.error(f"Pairwise error: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при обработке параметров. Проверьте формат ввода.",
            reply_markup=get_back_menu()
        )
    
    await state.clear()