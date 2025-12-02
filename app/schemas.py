from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserSchema(BaseModel):

    """
    SCHEMA FOR USER
    """
    id: int
    username: str
    email: str
    hashed_password: str
    role: str

    class Config:
        from_attributes = True 
"""
END 
"""


"""

SCHEMAS FOR FINANCIAL REPORT

"""
# ==========================================
# Вложенные компоненты (Активы, Пассивы, ОПУ)
# ==========================================

class AssetsSchema(BaseModel):
    """Разделы I и II баланса"""
    # Используем Optional[float] = 0.0, чтобы если фронт не прислал поле, оно стало нулем
    intangible_assets: Optional[float] = 0.0
    research_and_dev_results: Optional[float] = 0.0
    intangible_search_assets: Optional[float] = 0.0
    tangible_search_assets: Optional[float] = 0.0
    fixed_assets: Optional[float] = 0.0
    income_bearing_investments: Optional[float] = 0.0
    long_term_financial_investments: Optional[float] = 0.0
    deferred_tax_assets: Optional[float] = 0.0
    other_non_current_assets: Optional[float] = 0.0
    total_non_current_assets: float = Field(..., description="Итого по разделу I")

    inventory: Optional[float] = 0.0
    vat_receivable: Optional[float] = 0.0
    accounts_receivable: Optional[float] = 0.0
    financial_investments_sec_section: Optional[float] = 0.0
    cash_and_equivalents: Optional[float] = 0.0
    other_current_assets: Optional[float] = 0.0
    total_current_assets: float = Field(..., description="Итого по разделу II")

    model_config = ConfigDict(from_attributes=True)


class LiabilitiesSchema(BaseModel):
    """Разделы III, IV и V баланса"""
    authorized_capital: Optional[float] = 0.0
    own_shares_bought: Optional[float] = 0.0
    non_current_assets_revaluation: Optional[float] = 0.0
    additional_capital: Optional[float] = 0.0
    reserve_capital: Optional[float] = 0.0
    retained_earnings: Optional[float] = 0.0
    total_capital: float = Field(..., description="Итого по разделу III")

    long_term_borrowings: Optional[float] = 0.0
    deferred_tax_liabilities: Optional[float] = 0.0
    estimated_liabilities: Optional[float] = 0.0
    other_long_term_liabilities: Optional[float] = 0.0
    total_long_term_liabilities: float = Field(..., description="Итого по разделу IV")

    short_term_borrowings: Optional[float] = 0.0
    accounts_payable: Optional[float] = 0.0
    future_income: Optional[float] = 0.0
    estimated_short_term_liabilities: Optional[float] = 0.0
    other_short_term_liabilities: Optional[float] = 0.0
    total_short_term_liabilities: float = Field(..., description="Итого по разделу V")
    
    total_balance_liabilities: Optional[float] = 0.0 # Итого баланс

    model_config = ConfigDict(from_attributes=True)


class ProfitLossSchema(BaseModel):
    """Отчет о финансовых результатах"""
    revenue: Optional[float] = 0.0
    cost_of_sales: Optional[float] = 0.0
    gross_profit: Optional[float] = 0.0
    commercial_expenses: Optional[float] = 0.0
    administrative_expenses: Optional[float] = 0.0
    sales_profit: Optional[float] = 0.0

    participation_income: Optional[float] = 0.0
    interest_receivable: Optional[float] = 0.0
    interest_payable: Optional[float] = 0.0
    other_income: Optional[float] = 0.0
    other_expenses: Optional[float] = 0.0
    
    profit_before_tax: Optional[float] = 0.0
    
    income_tax: Optional[float] = 0.0
    current_income_tax: Optional[float] = 0.0
    deferred_income_tax: Optional[float] = 0.0
    other_operations: Optional[float] = 0.0
    
    net_profit: float = Field(..., description="Чистая прибыль (обязательно)")

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Основные схемы для API
# ==========================================

# 1. Схема для СОЗДАНИЯ отчета (входные данные)
class FinancialReportCreate(BaseModel):
    organization_name: str
    period: str
    
    assets: AssetsSchema
    liabilities: LiabilitiesSchema
    profit_loss: ProfitLossSchema


# 2. Схема для ЧТЕНИЯ отчета (выходные данные с ID и датой)
class FinancialReportResponse(FinancialReportCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

"""

END

"""