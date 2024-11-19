from src.shared.entities.basemodel import BaseModel

# Master
from src.domains.master.entities.va_categories import Category
from src.domains.master.entities.va_dealer import Dealer
from src.domains.master.entities.va_dealer_branch import DealerBranch
from src.domains.master.entities.va_model import Model
from src.domains.master.entities.va_segment import Segment
from src.domains.master.entities.va_stock_pilot import StockPilot
from src.domains.forecasts.entities.va_dealer_forecast import DealerForecast
from src.domains.forecasts.entities.va_dealer_forecast_model import DealerForecastModel
from src.domains.forecasts.entities.va_dealer_forecast_month import DealerForecastMonth

from src.domains.calculation.entities.va_slot_calculation import SlotCalculation
from src.domains.calculation.entities.va_slot_calculation_stock_pilot import (
    SlotCalculationStockPilot,
)
from src.domains.calculation.entities.va_slot_calculation_model import (
    SlotCalculationModel,
)
from src.domains.calculation.entities.va_slot_calculation_month import (
    SlotCalculationMonth,
)
