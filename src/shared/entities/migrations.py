from src.shared.entities.basemodel import BaseModel

# Master
from src.domains.masters.entities.va_categories import Category
from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.entities.va_segments import Segment
from src.domains.masters.entities.va_stock_pilots import StockPilot
from src.domains.masters.entities.va_models import Model
from src.domains.masters.entities.va_order_configurations import OrderConfiguration

# Forecast
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecast_detail_months import ForecastDetailMonth
from src.domains.forecasts.entities.va_monthly_targets import MonthlyTarget
from src.domains.forecasts.entities.va_monthly_target_details import MonthlyTargetDetail
from src.domains.forecasts.entities.va_monthly_targets import MonthlyTarget
from src.domains.forecasts.entities.va_monthly_target_details import MonthlyTargetDetail


# Calculations
from src.domains.calculations.entities.va_slot_calculations import SlotCalculation
from src.domains.calculations.entities.va_slot_calculation_details import SlotCalculationDetail
from src.domains.calculations.entities.va_slot_calculation_stock_pilots import SlotCalculationStockPilot
from src.domains.calculations.entities.va_slot_calculation_order_configuration import SlotCalculationOrderConfiguration
