from io import BytesIO
import openpyxl

def parse_balance_sheet(file_content: bytes):

    wb = openpyxl.load_workbook(BytesIO(file_content), data_only=True)
    sheet = wb.active 
    data = {}
    code_map = {
    # --- АКТИВЫ ---
    "1110": "intangible_assets",
    "1120": "research_and_dev_results",
    "1130": "intangible_search_assets",
    "1140": "tangible_search_assets",
    "1150": "fixed_assets",
    "1160": "income_bearing_investments",
    "1170": "long_term_financial_investments",
    "1180": "deferred_tax_assets",
    "1190": "other_non_current_assets",
    "1100": "total_non_current_assets", # ИТОГО I

    "1210": "inventory",
    "1220": "vat_receivable",
    "1230": "accounts_receivable",
    "1240": "financial_investments_sec_section",
    "1250": "cash_and_equivalents",
    "1260": "other_current_assets",
    "1200": "total_current_assets", # ИТОГО II

    # --- ПАССИВЫ ---
    "1310": "authorized_capital",
    "1320": "own_shares_bought",
    "1340": "non_current_assets_revaluation",
    "1350": "additional_capital",
    "1360": "reserve_capital",
    "1370": "retained_earnings",
    "1300": "total_capital", # ИТОГО III

    "1410": "long_term_borrowings",
    "1420": "deferred_tax_liabilities",
    "1430": "estimated_liabilities",
    "1450": "other_long_term_liabilities",
    "1400": "total_long_term_liabilities", # ИТОГО IV

    "1510": "short_term_borrowings",
    "1520": "accounts_payable",
    "1530": "future_income",
    "1540": "estimated_short_term_liabilities",
    "1550": "other_short_term_liabilities",
    "1500": "total_short_term_liabilities", # ИТОГО V
    
    "1700": "total_balance_liabilities", # БАЛАНС

    # --- ПРИБЫЛИ И УБЫТКИ ---
    "2110": "revenue",
    "2120": "cost_of_sales",
    "2100": "gross_profit",
    "2210": "commercial_expenses",
    "2220": "administrative_expenses",
    "2200": "sales_profit",
    "2310": "participation_income",
    "2320": "interest_receivable",
    "2330": "interest_payable",
    "2340": "other_income",
    "2350": "other_expenses",
    "2300": "profit_before_tax",
    "2410": "income_tax",
    "2460": "other_operations",
    "2400": "net_profit"
    }


    for row in sheet.iter_rows(min_row=1, max_row=100, values_only=True):
        for cell in row:
            if str(cell) in code_map:
                key = code_map[str(cell)]
                idx = row.index(cell)
                for val in row[idx+1:]:
                    if isinstance(val, (int, float)):
                        data[key] = float(val)
                        break
    
    return data
