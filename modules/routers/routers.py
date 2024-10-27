from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command
from modules.handlers import start_handler, set_currency_handler, set_interval_handler, get_rate_handler, set_threshold_handler, get_forecast_handler
from modules.libraries.utils import _States
from typing import Union

router = Router()

@router.message(CommandStart())
async def start_handler_command(message: types.Message, state: FSMContext):
    await start_handler.handle(message, state)

@router.callback_query(F.data == "get_rate")
@router.message(Command("get_rate"))
async def get_rate_handler_command(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await get_rate_handler.handle(message, state)

@router.callback_query(F.data == "forecast")
@router.message(Command("forecast"))
async def get_forecast_handler_command(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await get_forecast_handler.handle(message, state)

@router.callback_query(F.data == "set_currency")
@router.message(Command("set_currency"))
@router.message(_States.SetCurrency.currency)
async def set_currency_handler_command(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await set_currency_handler.handle(message, state)

@router.callback_query(F.data == "set_interval")
@router.message(Command("set_interval"))
@router.message(_States.SetInterval.interval)
async def set_interval_handler_command(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await set_interval_handler.handle(message, state)

@router.callback_query(F.data == "set_threshold")
@router.message(Command("set_threshold"))
@router.message(_States.SetThreshold.threshold)
async def set_threshold_handler_command(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await set_threshold_handler.handle(message, state)