from app.models import FinancialReport

class FinancialAnalyzer:
    def __init__(self, report: FinancialReport):
        self.report = report
        self.a = report.assets          # Сокращение для удобства
        self.l = report.liabilities
        self.p = report.profit_loss
        
        # Вспомогательные переменные (защита от деления на ноль)
        self.total_assets = self.a.total_balance_assets or 1  # Если 0, ставим 1 чтобы не упало
        self.revenue = self.p.revenue or 1

    def _safe_div(self, numerator, denominator):
        """Безопасное деление"""
        return round(numerator / denominator, 4) if denominator else 0

    # ==========================================
    # 1. Вертикальный анализ (Структура)
    # ==========================================
    def get_vertical_analysis(self):
        """Считаем долю каждой статьи в валюте баланса"""
        return {
            "non_current_assets_share": self._safe_div(self.a.total_non_current_assets, self.total_assets),
            "current_assets_share": self._safe_div(self.a.total_current_assets, self.total_assets),
            "equity_share": self._safe_div(self.l.total_capital, self.total_assets), # Автономия
            "liabilities_share": self._safe_div(self.l.total_long_term_liabilities + self.l.total_short_term_liabilities, self.total_assets)
        }

    # ==========================================
    # 2. Коэффициентный анализ (Ratios)
    # ==========================================
    def get_ratios(self):
        return {
            # --- Ликвидность ---
            # Текущая ликвидность = Оборотные активы / Краткосрочные обязательства
            "current_liquidity": self._safe_div(
                self.a.total_current_assets, 
                self.l.total_short_term_liabilities
            ),
            # Быстрая ликвидность = (Оборотные - Запасы) / Краткосрочные обяз.
            "quick_liquidity": self._safe_div(
                (self.a.total_current_assets - self.a.inventory),
                self.l.total_short_term_liabilities
            ),
            # Абсолютная ликвидность = Деньги / Краткосрочные обяз.
            "absolute_liquidity": self._safe_div(
                self.a.cash_and_equivalents,
                self.l.total_short_term_liabilities
            ),

            # --- Рентабельность ---
            # ROA = Чистая прибыль / Активы
            "roa": self._safe_div(self.p.net_profit, self.total_assets),
            # ROS = Чистая прибыль / Выручка
            "ros": self._safe_div(self.p.net_profit, self.revenue),
            
            # --- Финансовая устойчивость ---
            # Коэф. автономии = Капитал / Активы
            "autonomy": self._safe_div(self.l.total_capital, self.total_assets),
        }

    # ==========================================
    # 3. MDA (Multiple Discriminant Analysis) - Модель Альтмана
    # ==========================================
    def get_altman_z_score(self):
        """
        5-факторная модель Альтмана для частных компаний:
        Z = 0.717*X1 + 0.847*X2 + 3.107*X3 + 0.420*X4 + 0.998*X5
        """
        # X1 = (Оборотные активы - Краткосрочные обяз) / Активы
        working_capital = self.a.total_current_assets - self.l.total_short_term_liabilities
        x1 = self._safe_div(working_capital, self.total_assets)

        # X2 = Нераспределенная прибыль / Активы
        x2 = self._safe_div(self.l.retained_earnings, self.total_assets)

        # X3 = Прибыль до налогов / Активы
        x3 = self._safe_div(self.p.profit_before_tax, self.total_assets)

        # X4 = Капитал / Обязательства (все)
        all_liabilities = self.l.total_long_term_liabilities + self.l.total_short_term_liabilities
        x4 = self._safe_div(self.l.total_capital, all_liabilities)

        # X5 = Выручка / Активы
        x5 = self._safe_div(self.revenue, self.total_assets)

        z_score = 0.717*x1 + 0.847*x2 + 3.107*x3 + 0.420*x4 + 0.998*x5
        
        # Интерпретация
        if z_score < 1.23: conclusion = "Высокая вероятность банкротства"
        elif z_score > 2.9: conclusion = "Финансовая устойчивость высокая"
        else: conclusion = "Зона неопределенности"

        return {"score": round(z_score, 3), "conclusion": conclusion}

    # ==========================================
    # 4. Logit-модель (Например, модель Таффлера или упрощенная)
    # ==========================================
    # Logit сложен тем, что выдает вероятность 0..1 через экспоненту.
    # Возьмем популярную модель Лиса (она похожа на Z-score, но коэффициенты другие)
    # Или настоящую Logit (Ольсона), но там нужны логарифмы и сложные данные.
    # Для курсача часто под "Logit/Rating" имеют в виду Бивера или Бибаульта.
    # Давай сделаем R-модель (четырехфакторная прогнозная модель ИГЭА) - популярна в РФ.
    
    def get_r_model_igea(self):
        """Модель Иркутской ГЭА (адаптирована для РФ)"""
        k1 = self._safe_div(self.a.total_current_assets, self.total_assets)
        k2 = self._safe_div(self.p.net_profit, self.l.total_capital) # ROE
        k3 = self._safe_div(self.revenue, self.total_assets)
        k4 = self._safe_div(self.p.net_profit, self.p.cost_of_sales or 1)

        r_score = 8.38*k1 + 1*k2 + 0.054*k3 + 0.63*k4
        
        conclusion = "Вероятность банкротства низкая (до 10%)"
        if r_score < 0.42: conclusion = "Вероятность банкротства очень высокая"
        
        return {"score": round(r_score, 3), "conclusion": conclusion}

    # ==========================================
    # 5. Скоринговая модель (Рейтинг)
    # ==========================================
    def get_scoring_class(self):
        """
        Пример простой балльной оценки (Донцова-Никифорова или Сбербанк).
        Начисляем баллы за показатели.
        """
        score = 0
        
        # 1. Оценка ликвидности
        k_liq = self._safe_div(self.a.total_current_assets, self.l.total_short_term_liabilities)
        if k_liq >= 2.0: score += 30
        elif k_liq >= 1.0: score += 15
        
        # 2. Оценка автономии
        k_aut = self._safe_div(self.l.total_capital, self.total_assets)
        if k_aut >= 0.5: score += 20
        
        # 3. Рентабельность
        if self.p.net_profit > 0: score += 20
        
        # Класс заемщика
        if score >= 50: borrower_class = "Класс 1 (Отличное состояние)"
        elif score >= 30: borrower_class = "Класс 2 (Среднее состояние)"
        else: borrower_class = "Класс 3 (Плохое состояние)"

        return {"score": score, "class": borrower_class}

    # ==========================================
    # ОБЩИЙ ЗАПУСК
    # ==========================================
    def perform_full_analysis(self):
        return {
            "vertical": self.get_vertical_analysis(),
            "ratios": self.get_ratios(),
            "mda_altman": self.get_altman_z_score(),
            "logit_igea": self.get_r_model_igea(),
            "scoring": self.get_scoring_class()
        }
