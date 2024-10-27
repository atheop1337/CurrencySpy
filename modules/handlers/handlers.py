from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ChatAction
from modules.libraries.dbms import Database
from modules.libraries.utils import const, _States, _Kbs, _Messages, _Methods, CryptoTracker
from datetime import datetime
from typing import Union
from asyncio import sleep
import logging

class Handlers:

    def __init__(self, db: str):
        self._db = Database(db)
        self._user_id = None
        self._user_name = None

    async def get_info(self, type: Union[types.Message, types.CallbackQuery]):
        if isinstance(type, (types.Message, types.CallbackQuery)):
            self._user_id = type.from_user.id
            self._user_name = type.from_user.username
        else:
            raise ValueError("Unsupported type provided")

    class BaseHandler:
        def __init__(self, parent):
            self._parent = parent

        async def handle(self, type: Union[types.Message, types.CallbackQuery], state: FSMContext):
            await self._parent.get_info(type)
            state_name = await state.get_state()

            if isinstance(type, types.Message):
                await self._handle_message(type, state, state_name)
            elif isinstance(type, types.CallbackQuery):
                await self._handle_callback_query(type, state, state_name)
            else:
                logging.warning("Unsupported type provided")

        async def _handle_message(self, message: types.Message, state: FSMContext, state_name):
            raise NotImplementedError

        async def _handle_callback_query(self, callback_query: types.CallbackQuery, state: FSMContext, state_name):
            raise NotImplementedError

    class StartHandler(BaseHandler):

        async def _handle_message(self, message: types.Message, state: FSMContext, state_name):
            logging.info(f"{self._parent._user_id} started bot")
            successfully = await self._parent._db.add_user(self._parent._user_id, self._parent._user_name)
            if successfully == 409:
                await self._parent._db.update_currency_price(self._parent._user_id)
            _message = _Messages.get_welcome_message(self._parent._user_name, successfully)
            await message.answer(_message)

        async def _handle_callback_query(self, callback_query: types.CallbackQuery, state: FSMContext, state_name):
            logging.info(f"{self._parent._user_id} started bot from callback")
            successfully = await self._parent._db.add_user(self._parent._user_id)
            if successfully == 409:
                await self._parent._db.update_currency_price(self._parent._user_id)
            _message = _Messages.get_welcome_message(self._parent._user_name, successfully) 
            await callback_query.message.answer(_message)

    class SetCurrencyHandler(BaseHandler):

        async def _handle_message(self, message: types.Message, state: FSMContext, state_name):
            if state_name is None:
                logging.info(f"{self._parent._user_name} with {self._parent._user_id} started changing currency from message")
                await message.answer(_Messages.get_set_currency_message())
                await state.set_state(_States.SetCurrency.currency)
            elif state_name == _States.SetCurrency.currency:
                await self._handle_currency(message, state)

        async def _handle_callback_query(self, callback_query: types.CallbackQuery, state: FSMContext, state_name):
            if state_name is None:
                logging.info(f"{self._parent._user_name} with {self._parent._user_id} started changing currency from callback")
                await callback_query.message.answer(_Messages.get_set_currency_message())
                await state.set_state(_States.SetCurrency.currency)
            elif state_name == _States.SetCurrency.currency:
                await self._handle_currency(callback_query.message, state)

        async def _handle_currency(self, message: types.Message, state: FSMContext):
            currency = message.text
            try:
                successfully = await self._parent._db.info_updater(self._parent._user_id, "currency", currency)
                logging.info(f"{self._parent._user_name} with {self._parent._user_id} changed currency to {currency}")
                await message.answer(f"Ваша отслеживаемая валюта успешно изменена на {currency}")
                await state.clear()
            except Exception as e:
                logging.error(f"Failed to update currency: {e}")
                await message.answer(f"Что-то пошло не так во время изменения валюты, попробуйте позже")
                await state.clear()
                return


    class SetIntervalHandler(BaseHandler):

        async def _handle_message(self, message: types.Message, state: FSMContext, state_name):
            if state_name is None:
                logging.info(f"{self._parent._user_name} with {self._parent._user_id} started changing interval from message")
                await message.answer(_Messages.get_set_interval_message())
                await state.set_state(_States.SetInterval.interval)
            elif state_name == _States.SetInterval.interval:
                await self._handle_interval(message, state)

        async def _handle_callback_query(self, callback_query: types.CallbackQuery, state: FSMContext, state_name):
            if state_name is None:
                logging.info(f"{self._parent._user_name} with {self._parent._user_id} started changing interval from callback")
                await callback_query.message.answer(_Messages.get_set_interval_message())
                await state.set_state(_States.SetInterval.interval)
            elif state_name == _States.SetInterval.interval:
                await self._handle_interval(callback_query.message, state)

        async def _handle_interval(self, message: types.Message, state: FSMContext):
            interval = message.text
            try:
                interval = int(interval)
                successfully = await self._parent._db.info_updater(self._parent._user_id, "interval", interval)
                logging.info(f"{self._parent._user_name} with {self._parent._user_id} changed interval to {interval} seconds")
                await message.answer(f"Ваш текущий интервал уведомлений успешно изменен на {interval} секунд")
                await state.clear()
            except ValueError:
                await message.answer("Интервал должен быть числом")
                await state.clear()
                return
            except Exception as e:
                await state.clear()
                logging.error(f"Failed to update interval: {e}")

    
    class SetThreshold(BaseHandler):
        
        async def _handle_message(self, message: types.Message, state: FSMContext, state_name):
            if state_name is None:
                logging.info(f"{self._parent._user_name} with {self._parent._user_id} started changing threshold from message")
                await message.answer(_Messages.get_set_threshold_message())
                await state.set_state(_States.SetThreshold.threshold)
            elif state_name == _States.SetThreshold.threshold:
                await self._handle_threshold(message, state)

        async def _handle_callback_query(self, callback_query: types.CallbackQuery, state: FSMContext, state_name):
            if state_name is None:
                logging.info(f"{self._parent._user_name} with {self._parent._user_id} started changing threshold from callback")
                await callback_query.message.answer(_Messages.get_set_threshold_message())
                await state.set_state(_States.SetThreshold.threshold)
            elif state_name == _States.SetThreshold.threshold:
                await self._handle_threshold(callback_query.message, state)

        async def _handle_threshold(self, message: types.Message, state: FSMContext):
            threshold = message.text
            try:
                threshold = int(threshold)
                successfully = await self._parent._db.info_updater(self._parent._user_id, "threshold", threshold)
                logging.info(f"{self._parent._user_name} with {self._parent._user_id} changed threshold to {threshold}")
                await message.answer(f"Ваш текущий порог уведомлений успешно изменен на {threshold}")
                await state.clear()
            except ValueError:
                await message.answer("Порог должен быть числом")
                await state.clear()
                return
            except Exception as e:
                logging.error(f"Failed to update threshold: {e}")
                await state.clear()

    
    class GetRate(BaseHandler):

        async def _handle_message(self, message: types.Message, state: FSMContext, state_name):
            logging.info(f"{self._parent._user_name} with {self._parent._user_id} started getting rate from message")
            successfully = await self._parent._db.update_currency_price(self._parent._user_id)
            if not successfully: 
                await message.answer("Что-то пошло не так во время обновления получения цены, попробуйте позже")
            udata = await self._parent._db.fetch_info(self._parent._user_id)
            if udata is not None:
                await message.answer(_Messages.get_rate_message(udata))

        async def _handle_callback_query(self, callback_query: types.CallbackQuery, state: FSMContext, state_name):
            logging.info(f"{self._parent._user_name} with {self._parent._user_id} started getting rate from callback")
            successfully = await self._parent._db.update_currency_price(self._parent._user_id)
            if not successfully:
                await callback_query.message.answer("Что-то пошло не так во время обновления получения цены, попробуйте позже")
            udata = await self._parent._db.fetch_info(self._parent._user_id)
            if udata is not None:
                await callback_query.message.answer(_Messages.get_rate_message(udata))

    
    class GetForeCast(BaseHandler):

        async def _handle_message(self, message: types.Message, state: FSMContext, state_name):
            logging.info(f"{self._parent._user_name} with {self._parent._user_id} started getting forecast from message")
            udata = await self._parent._db.fetch_info(self._parent._user_id)
            currency = udata["currency"]
            tracker = CryptoTracker(symbol=f"{currency}-USD")
            forecasted_price = tracker.run_analysis()
            await sleep(2)
            try:
                await message.answer_photo(types.FSInputFile(f'{currency}-USD-FORECAST-PRICE.png'), caption=f"Прогназируемая цена для {currency}: {forecasted_price} USD")
                logging.info(f"Sent forecasted graph and price for {currency} to user {self._parent._user_id}")
            except Exception as e:
                logging.error(f"Failed to send forecasted graph: {e}")
                await message.answer("Что-то пошло не так во время отправки прогноза, попробуйте позже")

        async def _handle_callback_query(self, callback_query: types.CallbackQuery, state: FSMContext, state_name):
            logging.info(f"{self._parent._user_name} with {self._parent._user_id} started getting forecast from callback")
            udata = await self._parent._db.fetch_info(self._parent._user_id)
            currency = udata["currency"]
            tracker = CryptoTracker(symbol=f"{currency}-USD")
            forecasted_price = tracker.run_analysis()
            await sleep(2)
            try:
                await callback_query.message.answer_photo(photo, caption=f"Прогнозируемая цена для {currency}: {forecasted_price} USD")
                logging.info(f"Sent forecasted graph and price for {currency} to user {self._parent._user_id}")
            except Exception as e:
                logging.error(f"Failed to send forecasted graph: {e}")
                await message.answer("Что-то пошло не так во время отправки прогноза закрытия, попробуйте позже")
            





