from modules.handlers.handlers import Handlers
from modules.libraries.utils import const

# Main handler
handlers = Handlers(const.DATABASE_NAME)

# Start handler
start_handler = handlers.StartHandler(parent=handlers)

# Currency handlers
set_currency_handler = handlers.SetCurrencyHandler(parent=handlers)
set_interval_handler = handlers.SetIntervalHandler(parent=handlers)
set_threshold_handler = handlers.SetThreshold(parent=handlers)
get_rate_handler = handlers.GetRate(parent=handlers)
get_forecast_handler = handlers.GetForeCast(parent=handlers)