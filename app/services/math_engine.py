from app.models import FinancialReport
from pydantic import BaseModel

# --- СХЕМЫ ОТВЕТА (Pydantic) ---
class AnalysisResultSchema(BaseModel):
    liquidity: dict[str, float]
    profitability: dict[str, float]
    activity: dict[str, float]
    bankruptcy_altman: dict[str, str | float]
    bankruptcy_taffler: dict[str, str | float]

# --- АНАЛИЗАТОР ---
class FinancialAnalyzer:
    def __init__(self, report: FinancialReport):
        self.report = report
        self.a = report.assets
        self.l = report.liabilities
        self.p = report.profit_loss
        
        self._prepare_data()

    def _val(self, value) -> float:
        """
        Защита от None. Если в базе NULL, считаем как 0.0
        """
        if value is None:
            return 0.0
        return float(value)

    def _prepare_data(self):
        # Вспомогательная функция, чтобы собрать все нужные цифры в кучу
        # и гарантировать, что они float, а не None.
        
        # 1. Активы
        self.current_assets = self._val(self.a.total_current_assets)
        self.non_current_assets = self._val(self.a.total_non_current_assets)
        self.total_assets = self.current_assets + self.non_current_assets
        # Если итог не сошелся или равен 0 (пустой отчет), ставим 1, чтобы не делить на ноль
        if self.total_assets == 0: self.total_assets = 1.0

        self.inventory = self._val(self.a.inventory)
        self.cash = self._val(self.a.cash_and_equivalents)
        self.receivables = self._val(self.a.accounts_receivable)
        
        # 2. Пассивы
        self.short_liabilities = self._val(self.l.total_short_term_liabilities)
        self.long_liabilities = self._val(self.l.total_long_term_liabilities)
        self.total_liabilities = self.short_liabilities + self.long_liabilities
        
        self.equity = self._val(self.l.total_capital)
        self.retained_earnings = self._val(self.l.retained_earnings)
        
        # 3. Прибыли
        self.revenue = self._val(self.p.revenue)
        self.net_profit = self._val(self.p.net_profit)
        self.profit_before_tax = self._val(self.p.profit_before_tax)
        self.sales_profit = self._val(self.p.sales_profit)
        self.cost_of_sales = self._val(self.p.cost_of_sales)

    def _safe_div(self, num: float, denom: float) -> float:
        """Безопасное деление с округлением"""
        if denom == 0:
            return 0.0
        return round(num / denom, 4)

    # ============================
    # МЕТОДЫ РАСЧЕТА
    # ============================

    def calc_liquidity(self):
        return {
            "current_ratio": self._safe_div(self.current_assets, self.short_liabilities),
            "quick_ratio": self._safe_div(self.current_assets - self.inventory, self.short_liabilities),
            "absolute_ratio": self._safe_div(self.cash, self.short_liabilities),
        }

    def calc_profitability(self):
        return {
            "ros": self._safe_div(self.net_profit, self.revenue) * 100,
            "roa": self._safe_div(self.net_profit, self.total_assets) * 100,
            "roe": self._safe_div(self.net_profit, self.equity) * 100,
        }

    def calc_activity(self):
        # Оборачиваемость активов
        asset_turnover = self._safe_div(self.revenue, self.total_assets)
        
        # Оборачиваемость запасов в днях
        inventory_days = 0.0
        if self.cost_of_sales != 0:
            # cost_of_sales часто отрицательный в отчете, берем модуль
            inventory_days = (365 * self.inventory) / abs(self.cost_of_sales)
            
        return {
            "asset_turnover": asset_turnover,
            "inventory_days": round(inventory_days, 1)
        }

    def calc_altman(self):
        # Модель Альтмана для частных компаний (5-факторная)
        working_capital = self.current_assets - self.short_liabilities
        
        x1 = self._safe_div(working_capital, self.total_assets)
        x2 = self._safe_div(self.retained_earnings, self.total_assets)
        x3 = self._safe_div(self.profit_before_tax, self.total_assets)
        x4 = self._safe_div(self.equity, self.total_liabilities)
        x5 = self._safe_div(self.revenue, self.total_assets)

        z = 0.717*x1 + 0.847*x2 + 3.107*x3 + 0.420*x4 + 0.998*x5
        
        if z < 1.23: conclusion = "Высокая вероятность банкротства"
        elif z > 2.9: conclusion = "Финансовое состояние устойчивое"
        else: conclusion = "Зона неопределенности"

        return {"score": round(z, 3), "conclusion": conclusion}

    def calc_taffler(self):
        # Модель Таффлера (4-факторная)
        x1 = self._safe_div(self.sales_profit, self.short_liabilities)
        x2 = self._safe_div(self.current_assets, self.total_liabilities)
        x3 = self._safe_div(self.short_liabilities, self.total_assets)
        x4 = self._safe_div(self.revenue, self.total_assets)
        
        z = 0.53*x1 + 0.13*x2 + 0.18*x3 + 0.16*x4
        
        if z > 0.3: conclusion = "Риск банкротства низкий"
        elif z < 0.2: conclusion = "Риск банкротства высокий"
        else: conclusion = "Ситуация неопределенная"

        return {"score": round(z, 3), "conclusion": conclusion}

    # ============================
    # ГЛАВНЫЙ МЕТОД
    # ============================
    def get_full_analysis(self) -> AnalysisResultSchema:
        return AnalysisResultSchema(
            liquidity=self.calc_liquidity(),
            profitability=self.calc_profitability(),
            activity=self.calc_activity(),
            bankruptcy_altman=self.calc_altman(),
            bankruptcy_taffler=self.calc_taffler()
        )
