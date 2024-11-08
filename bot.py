import asyncio
import calendar
# import logging
from config import TOKEN, ADMIN_ID
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
import calculate as calc
from bank_holidays import get_bank_holidays_for_year as get_bh
from collections import defaultdict
from datetime import time

# Setup logging for debugging
# logging.basicConfig(level=logging.INFO)

API_TOKEN = TOKEN


async def start_bot(bot: Bot):
    await bot.send_message(ADMIN_ID, text="Бот запущен!")


async def stop_bot(bot: Bot):
    await bot.send_message(ADMIN_ID, text="Бот выключен!")


# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.startup.register(start_bot)
dp.shutdown.register(stop_bot)
router = Router()
dp.include_router(router)


# Setup States for FSM
class Form(StatesGroup):
    date = State()
    profession = State()
    start_hour = State()
    start_minute = State()
    duration = State()


shift_data = []  # List for storing shift data


# Function for creating calendar
def create_calendar(year: int = datetime.now().year, month: int = datetime.now().month):
    keyboard = InlineKeyboardBuilder()
    keyboard_days = InlineKeyboardBuilder()

    # Heading
    keyboard.row(InlineKeyboardButton(text=f"{calendar.month_name[month]} {year}", callback_data="ignore"))

    # Week days
    for day in ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']:
        keyboard_days.add(InlineKeyboardButton(text=day, callback_data="ignore"))

    # Month days
    for week in calendar.monthcalendar(year, month):
        for day in week:
            if day == 0:
                keyboard_days.add(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                keyboard_days.add(InlineKeyboardButton(text=str(day), callback_data=f"day_{day}_{month}_{year}"))

    # Switching months back and forth
    keyboard.attach(keyboard_days.adjust(7))
    keyboard.row(
        InlineKeyboardButton(text="<", callback_data=f"prev month_{year}_{month}"),
        InlineKeyboardButton(text=">", callback_data=f"next month_{year}_{month}")
    )

    # Button "Calculate"
    keyboard_calculate = InlineKeyboardBuilder().row(InlineKeyboardButton(text="Calculate", callback_data="calculate"))
    keyboard.attach(keyboard_calculate)

    return keyboard.as_markup()


# Function for choosing role
def create_role_keyboard():
    role_keyboard = InlineKeyboardBuilder()
    role_keyboard.row(InlineKeyboardButton(text="CHARGEHAND", callback_data="OCC_CH"))
    role_keyboard.add(InlineKeyboardButton(text="FLT DRIVER", callback_data="OCC_FLT"))
    role_keyboard.add(InlineKeyboardButton(text="HANDBALLER", callback_data="OCC_HB"))
    return role_keyboard.as_markup()


# Function for choosing hour
def create_hour_keyboard():
    hour_keyboard = InlineKeyboardBuilder()
    for hour in range(24):
        hour_keyboard.add(InlineKeyboardButton(text=f"{hour:02d}", callback_data=f"hour_{hour}"))
    return hour_keyboard.adjust(6).as_markup()


# Function for choosing minute
def create_minute_keyboard():
    minute_keyboard = InlineKeyboardBuilder()
    for minute in range(0, 60, 15):  # Шаг в 15 минут
        minute_keyboard.add(InlineKeyboardButton(text=f"{minute:02d}", callback_data=f"minute_{minute}"))
    return minute_keyboard.adjust(2).as_markup()


# Function for choosing duration
def create_duration_keyboard():
    duration_keyboard = InlineKeyboardBuilder()
    for duration in range(1, 13):  # Продолжительность в часах
        duration_keyboard.add(InlineKeyboardButton(text=f"{duration} hrs", callback_data=f"duration_{duration}"))
    return duration_keyboard.adjust(4).as_markup()


# Handling 'start' command
@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("Hi! This bot helps calculate wages for BCP in Harwich (TLP staff). \n"
                         "Choose shift date, role, starting time, and shift duration. \n"
                         "To finish, press 'Calculate' below the calendar.")
    await state.set_state(Form.date)
    await message.answer("Please select a date:", reply_markup=create_calendar())


# Handling callback queries for days from the calendar
@router.callback_query(lambda c: c.data and c.data.startswith('day_'))
async def process_day_selection(callback_query: CallbackQuery, state: FSMContext):
    _, day, month, year = callback_query.data.split('_')
    selected_date = f"{year}-{month}-{day}"
    await state.update_data(date=selected_date)
    await state.set_state(Form.profession)
    await callback_query.message.edit_text("Please select a role:", reply_markup=create_role_keyboard())


# Handling callback queries for roles
@router.callback_query(lambda c: c.data and c.data.startswith('OCC_'))
async def process_profession_selection(callback_query: CallbackQuery, state: FSMContext):
    _, occupation = callback_query.data.split('_')
    await state.update_data(profession=occupation)
    await state.set_state(Form.start_hour)
    await callback_query.message.edit_text("Please select the start hour:", reply_markup=create_hour_keyboard())


# Handling callback queries for hours
@router.callback_query(lambda c: c.data and c.data.startswith('hour_'))
async def process_hour_selection(callback_query: CallbackQuery, state: FSMContext):
    _, hour = callback_query.data.split('_')
    await state.update_data(start_hour=hour)
    await state.set_state(Form.start_minute)
    await callback_query.message.edit_text("Please select the start minute:", reply_markup=create_minute_keyboard())


# Handling callback queries for minutes
@router.callback_query(lambda c: c.data and c.data.startswith('minute_'))
async def process_minute_selection(callback_query: CallbackQuery, state: FSMContext):
    _, minute = callback_query.data.split('_')
    await state.update_data(start_minute=minute)
    await state.set_state(Form.duration)
    await callback_query.message.edit_text("Please select the duration:", reply_markup=create_duration_keyboard())


# Handling callback queries for durations
@router.callback_query(lambda c: c.data and c.data.startswith('duration_'))
async def process_duration_selection(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    _, duration = callback_query.data.split('_')

    # Saving shifts to shift_data
    shift_data.append({
        'date': data['date'],
        'profession': data['profession'],
        'start_time': f"{data['start_hour']}:{data['start_minute']}",
        'duration': duration
    })

    # Deleting previous message
    await callback_query.message.delete()

    # Starting input data for a new shift
    await state.set_state(Form.date)
    await callback_query.message.answer("Please select a date for the next shift or press 'Calculate' to finish:",
                                        reply_markup=create_calendar())


# Handling 'help' command
@router.message(Command("help"))
async def help(message: types.Message):
    # Отправляем справку по работе бота
    await message.answer("Hi! This BOT is helping with counting salary for BCP in Harwich (TLP staff). \n"
                         "For this you need to choose a shift date, role, starting time and shift duration. \n"
                         "You can select several shifts and after press 'Calculate' button below the calendar. \n")


# Handling 'calculate' command
@router.callback_query(lambda c: c.data == "calculate")
async def process_calculate(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    shift_dict = defaultdict(dict)
    i = 0
    for shift in shift_data:
        date = datetime.strptime(shift['date'], '%Y-%m-%d')
        week_number = calc.week_count(date)
        start_time = list(map(int, (shift['start_time'].split(':'))))
        start_time = time(start_time[0], start_time[1])
        duration = time(int(shift['duration']))
        shift_dict[week_number][i] = {'date': date, 'time': start_time, 'duration': duration,
                                      'profession': shift['profession']}
        i += 1
    bank_holidays_list = [datetime.strptime(x, '%Y-%m-%d') for x in get_bh('england-and-wales')]
    salary_calc = calc.salary_calc(shift_dict, bank_holidays_list)
    n = '\n'
    result_message = (f"Total salary: \n{n.join(salary_calc)}\n\nThe first number is the week number, "
                      f"the second is the weekly salary."
                      f"\nThis is the gross salary. And don't forget that all hours after midnight on Sunday will be "
                      f"paid a week later.")

    await callback_query.message.edit_text(result_message if shift_data else "No shifts recorded.")
    shift_data.clear()  # Clear shift_data after calculation


# Handling callback queries for previous month
@router.callback_query(lambda c: c.data and c.data.startswith('prev month_'))
async def process_prev_month(callback_query: CallbackQuery):
    _, year, month = callback_query.data.split('_')
    year = int(year)
    month = int(month) - 1
    if month == 0:
        month = 12
        year -= 1
    await callback_query.message.edit_reply_markup(reply_markup=create_calendar(year, month))


# Handling callback queries for next month
@router.callback_query(lambda c: c.data and c.data.startswith('next month_'))
async def process_next_month(callback_query: CallbackQuery):
    _, year, month = callback_query.data.split('_')
    year = int(year)
    month = int(month) + 1
    if month == 13:
        month = 1
        year += 1
    await callback_query.message.edit_reply_markup(reply_markup=create_calendar(year, month))


# Function for starting the bot
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
