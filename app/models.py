from sqlalchemy import Column, Enum, ForeignKey, Integer, String, DateTime, Float, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base
import enum



Base = declarative_base()

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    ANALYST = "analyst"
    MANAGER = "manager"

class User(Base):
    """
    User model class
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

class FinancialReport(Base):
    """
    Financial report class
    """
    __tablename__ = 'financial_reports'

    id = Column(Integer, index= True, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    organization_name = Column(String, nullable=False)
    period = Column(String, nullable=False)
    created_at = Column(DateTime,  default= func.now())

    assets = relationship("ReportAssets", 
                          back_populates="report", 
                          uselist=False, 
                          cascade="all, delete-orphan"
    )
    
    
    liabilities = relationship ("ReportLiabilities", 
                                back_populates="report", 
                                uselist=False,
                                cascade="all, delete-orphan"
    )
    profit_loss = relationship("ReportProfitLoss", 
                               back_populates="report", 
                               uselist=False,
                               cascade="all, delete-orphan"
    )

class ReportAssets(Base):
    """
    This class include 1 and 2 sections of the balance sheet
    """
    __tablename__ = 'report_assets'

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("financial_reports.id"))

    # --- РАЗДЕЛ I. ВНЕОБОРОТНЫЕ АКТИВЫ ---
    intangible_assets = Column(Float)                   # Code: 1110 Нематериальные активы
    research_and_dev_results = Column(Float)            # Code: 1120 Результаты исследований и разработок
    intangible_search_assets = Column(Float)            # Code: 1130 Нематериальные поисковые активы
    tangible_search_assets = Column(Float)              # Code: 1140 Материальные поисковые активы
    fixed_assets = Column(Float)                        # Code: 1150 Основные средства
    income_bearing_investments = Column(Float)          # Code: 1160 Доходные вложения в материальные ценности
    long_term_financial_investments = Column(Float)     # Code: 1170 Финансовые вложения (долгосрочные)
    deferred_tax_assets = Column(Float)                 # Code: 1180 Отложенные налоговые активы
    other_non_current_assets = Column(Float)            # Code: 1190 Прочие внеоборотные активы
    
    total_non_current_assets = Column(Float)            # Code: 1100 Итого по разделу I

    # --- РАЗДЕЛ II. ОБОРОТНЫЕ АКТИВЫ ---
    inventory = Column(Float)                           # Code: 1210 Запасы
    vat_receivable = Column(Float)                      # Code: 1220 Налог на добавленную стоимость по приобретенным ценностям
    accounts_receivable = Column(Float)                 # Code: 1230 Дебиторская задолженность
    financial_investments_sec_section = Column(Float)   # Code: 1240 Финансовые вложения (за исключением денежных эквивалентов)
    cash_and_equivalents = Column(Float)                # Code: 1250 Денежные средства и денежные эквиваленты
    other_current_assets = Column(Float)                # Code: 1260 Прочие оборотные активы
    
    total_current_assets = Column(Float)                # Code: 1200 Итого по разделу II

    report = relationship("FinancialReport", back_populates="assets")


class ReportLiabilities(Base):
    """
    This class include 3, 4, 5 sections of the balance sheet
    """
    __tablename__ = "report_liabilities"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("financial_reports.id"))

    # --- III. КАПИТАЛ И РЕЗЕРВЫ ---
    authorized_capital = Column(Float)          # 1310 Уставный капитал
    own_shares_bought = Column(Float)           # 1320 Собственные акции, выкупленные у акционеров
    non_current_assets_revaluation = Column(Float) # 1340 Переоценка внеоборотных активов
    additional_capital = Column(Float)          # 1350 Добавочный капитал (без переоценки)
    reserve_capital = Column(Float)             # 1360 Резервный капитал
    retained_earnings = Column(Float)           # 1370 Нераспределенная прибыль (непокрытый убыток)
    
    total_capital = Column(Float)               # 1300 Итого по разделу III (Капитал и резервы)

    # --- IV. ДОЛГОСРОЧНЫЕ ОБЯЗАТЕЛЬСТВА ---
    long_term_borrowings = Column(Float)        # 1410 Заемные средства (долгосрочные)
    deferred_tax_liabilities = Column(Float)    # 1420 Отложенные налоговые обязательства
    estimated_liabilities = Column(Float)       # 1430 Оценочные обязательства
    other_long_term_liabilities = Column(Float) # 1450 Прочие обязательства
    
    total_long_term_liabilities = Column(Float) # 1400 Итого по разделу IV

    # --- V. КРАТКОСРОЧНЫЕ ОБЯЗАТЕЛЬСТВА ---
    short_term_borrowings = Column(Float)       # 1510 Заемные средства (краткосрочные)
    accounts_payable = Column(Float)            # 1520 Кредиторская задолженность
    future_income = Column(Float)               # 1530 Доходы будущих периодов
    estimated_short_term_liabilities = Column(Float) # 1540 Оценочные обязательства (краткосрочные)
    other_short_term_liabilities = Column(Float) # 1550 Прочие обязательства
    
    total_short_term_liabilities = Column(Float) # 1500 Итого по разделу V

    # Итоговый баланс (Пассив)
    total_balance_liabilities = Column(Float)   # 1700 БАЛАНС (Пассив)

    report = relationship("FinancialReport", back_populates="liabilities")
    

class ReportProfitLoss(Base):
    """
    This class include income statement
    """
    __tablename__ = "report_profit_loss"

    id = Column(Integer, primary_key=True, index= True)
    report_id = Column(Integer, ForeignKey("financial_reports.id"))

        # Основные показатели деятельности
    revenue = Column(Float)                     # Code: 2110 Выручка
    cost_of_sales = Column(Float)               # Code: 2120 Себестоимость продаж
    gross_profit = Column(Float)                # Code: 2100 Валовая прибыль (убыток)
    commercial_expenses = Column(Float)         # Code: 2210 Коммерческие расходы
    administrative_expenses = Column(Float)     # Code: 2220 Управленческие расходы
    
    sales_profit = Column(Float)                # Code: 2200 Прибыль (убыток) от продаж

    # Прочие доходы и расходы
    participation_income = Column(Float)        # Code: 2310 Доходы от участия в других организациях
    interest_receivable = Column(Float)         # Code: 2320 Проценты к получению
    interest_payable = Column(Float)            # Code: 2330 Проценты к уплате
    other_income = Column(Float)                # Code: 2340 Прочие доходы
    other_expenses = Column(Float)              # Code: 2350 Прочие расходы

    profit_before_tax = Column(Float)           # Code: 2300 Прибыль (убыток) до налогообложения

    # Налоги
    income_tax = Column(Float)                  # Code: 2410 Налог на прибыль
    current_income_tax = Column(Float)          # Code: 2411 Текущий налог на прибыль
    deferred_income_tax = Column(Float)         # Code: 2412 Отложенный налог на прибыль
    other_operations = Column(Float)            # Code: 2460 Прочее

    net_profit = Column(Float)                  # Code: 2400 Чистая прибыль (убыток)

    report = relationship("FinancialReport", back_populates="profit_loss")
