from aiogram import Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import logging
from messages import WELCOME_MSG, MENU_MSG, HELP_MSG, get_main_menu, get_back_menu

logger = logging.getLogger(__name__)

# Импорты команд

from plugins.json_validator import (
    json_validator_command,
    process_json_validation,
    process_repeat_choice,
    JsonValidatorStates
)

from plugins.image_generator import (
    generate_image_command,
    process_format_choice,
    process_image_params,
    handle_choice,
    ImageGeneratorStates
)

from plugins.payment_generator import (
    generate_payment_command as payment_gen_command,
    process_payment_system,
    process_regenerate_choice,
    PaymentGeneratorStates
)

from plugins.pairwise_tester import (
    pairwise_command as pairwise_test_command,
    process_pairwise_parameters,
    PairwiseStates
)

class CommandRouter:
    def __init__(self, dp: Dispatcher):
        self.dp = dp
        self.text_commands = {
            "генератор изображений": self.handle_image_command,
            "генератор платежных данных": self.handle_payment_command,
            "генератор pairwise тестов": self.handle_pairwise_command,
            "валидатор json": self.handle_json_validator_command,
            "назад в меню": self.handle_back_to_menu,
            "информация": self.handle_help_command
        }

    async def handle_json_validator_command(self, message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(JsonValidatorStates.waiting_for_json)
        await json_validator_command(message, state)

    async def handle_image_command(self, message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(ImageGeneratorStates.waiting_for_params)
        await generate_image_command(message, state)

    async def handle_payment_command(self, message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(PaymentGeneratorStates.waiting_for_payment_system)
        await payment_gen_command(message, state)

    async def handle_pairwise_command(self, message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(PairwiseStates.waiting_for_parameters)
        await pairwise_test_command(message, state)

    async def handle_back_to_menu(self, message: Message, state: FSMContext):
        await state.clear()
        await message.answer(MENU_MSG, reply_markup=get_main_menu())

    async def handle_help_command(self, message: Message, state: FSMContext):
        await state.clear()
        await message.answer(HELP_MSG, reply_markup=get_main_menu())

    def register_handlers(self):
        try:
            logger.info("Регистрация обработчиков команд...")
            
            # Универсальный обработчик /cancel
            @self.dp.message(Command("cancel"))
            async def cmd_cancel(message: Message, state: FSMContext):
                await state.clear()
                await message.answer("✅ Операция отменена", reply_markup=get_main_menu())

            # Обработчики базовых команд
            @self.dp.message(Command("start"))
            async def cmd_start(message: Message, state: FSMContext):
                await state.clear()
                await message.answer(WELCOME_MSG, reply_markup=get_main_menu())

            @self.dp.message(Command("help"))
            async def cmd_help(message: Message, state: FSMContext):
                await self.handle_help_command(message, state)

            # Обработчики специализированных команд
            @self.dp.message(Command("genimage"))
            async def cmd_genimage(message: Message, state: FSMContext):
                await self.handle_image_command(message, state)

            @self.dp.message(Command("genpayment"))
            async def cmd_genpayment(message: Message, state: FSMContext):
                await self.handle_payment_command(message, state)

            @self.dp.message(Command("pairwise"))
            async def cmd_pairwise(message: Message, state: FSMContext):
                await self.handle_pairwise_command(message, state)
            
            @self.dp.message(Command("validatejson"))
            async def cmd_validatejson(message: Message, state: FSMContext):
                await self.handle_json_validator_command(message, state)

            # Обработчики состояний
            @self.dp.message(StateFilter(ImageGeneratorStates.waiting_for_params))
            async def handle_image_state(message: Message, state: FSMContext):
                if message.text == "Назад в меню" or message.text == "/help":
                    handler = self.handle_help_command if message.text == "/help" else self.handle_back_to_menu
                    await handler(message, state)
                    return
                await process_image_params(message, state)

            @self.dp.message(StateFilter(ImageGeneratorStates.waiting_for_format))
            async def handle_format_choice(message: Message, state: FSMContext):
                    await process_format_choice(message, state)
                    
            @self.dp.message(StateFilter(ImageGeneratorStates.waiting_for_choice))
            async def handle_image_choice(message: Message, state: FSMContext):
                await handle_choice(message, state)
          
            @self.dp.message(StateFilter(PaymentGeneratorStates.waiting_for_payment_system))
            async def handle_payment_state(message: Message, state: FSMContext):
                if message.text == "Назад в меню":
                    await self.handle_back_to_menu(message, state)
                    return
                await process_payment_system(message, state)

            @self.dp.message(StateFilter(PaymentGeneratorStates.waiting_for_regenerate_choice))
            async def handle_regenerate_choice(message: Message, state: FSMContext):
                if message.text == "Назад в меню":
                    await self.handle_back_to_menu(message, state)
                    return
                await process_regenerate_choice(message, state)

            @self.dp.message(StateFilter(PairwiseStates.waiting_for_parameters))
            async def handle_pairwise_state(message: Message, state: FSMContext):
                if message.text == "Назад в меню" or message.text == "/help":
                    handler = self.handle_help_command if message.text == "/help" else self.handle_back_to_menu
                    await handler(message, state)
                    return
                await process_pairwise_parameters(message, state)

            @self.dp.message(StateFilter(PairwiseStates.waiting_for_action))
            async def handle_pairwise_action(message: Message, state: FSMContext):
                from plugins.pairwise_tester import process_pairwise_action
                await process_pairwise_action(message, state)

            @self.dp.message(StateFilter(JsonValidatorStates.waiting_for_json))
            async def handle_json_validation(message: Message, state: FSMContext):
                if message.text == "Назад в меню":
                    await self.handle_back_to_menu(message, state)
                    return
                await process_json_validation(message, state)
          
            @self.dp.message(StateFilter(JsonValidatorStates.waiting_for_repeat))
            async def handle_json_repeat_choice(message: Message, state: FSMContext):
                if message.text == "Назад в меню":
                    await self.handle_back_to_menu(message, state)
                    return
                await process_repeat_choice(message, state)


            # Главный обработчик текстовых сообщений
            @self.dp.message()
            async def handle_text(message: Message, state: FSMContext):
                text = message.text.lower()
                if text in self.text_commands:
                    await self.text_commands[text](message, state)
                else:
                    current_state = await state.get_state()
                    if not current_state:
                        await message.answer(MENU_MSG, reply_markup=get_main_menu())

            logger.info("Все обработчики успешно зарегистрированы")
            
        except Exception as e:
            logger.error(f"Ошибка регистрации обработчиков: {e}", exc_info=True)
            raise