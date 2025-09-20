import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

# UK Tax System Constants (2024/25)
PERSONAL_ALLOWANCE = 12570
BASIC_RATE_THRESHOLD = 50270
HIGHER_RATE_THRESHOLD = 125140
LOSS_OF_PERSONAL_ALLOWANCE_THRESHOLD = 100000
BASIC_RATE = 0.20
HIGHER_RATE = 0.40
ADDITIONAL_RATE = 0.45

# National Insurance (2024/25)
NI_THRESHOLD = 12570
NI_UPPER_THRESHOLD = 50270
NI_BASIC_RATE = 0.08
NI_HIGHER_RATE = 0.02

# Pension and ISA limits
ANNUAL_ISA_LIMIT = 20000
ANNUAL_PENSION_LIMIT = 60000
LIFETIME_ISA_LIMIT = 4000  # for under 40s


def calculate_uk_tax(annual_income: float, rsu_value: float) -> Dict[str, float]:
    """Calculate UK income tax and national insurance"""
    annual_income += rsu_value
    # Income Tax
    if annual_income <= PERSONAL_ALLOWANCE:
        income_tax = 0
    elif annual_income <= BASIC_RATE_THRESHOLD:
        income_tax = (annual_income - PERSONAL_ALLOWANCE) * BASIC_RATE
    elif annual_income <= LOSS_OF_PERSONAL_ALLOWANCE_THRESHOLD and annual_income > BASIC_RATE_THRESHOLD:
        income_tax = (BASIC_RATE_THRESHOLD - PERSONAL_ALLOWANCE) * BASIC_RATE + \
                     (annual_income - BASIC_RATE_THRESHOLD) * HIGHER_RATE
    elif annual_income <= HIGHER_RATE_THRESHOLD and annual_income > LOSS_OF_PERSONAL_ALLOWANCE_THRESHOLD:
        rate_above = annual_income - LOSS_OF_PERSONAL_ALLOWANCE_THRESHOLD
        NEW_PERSONAL_ALLOWANCE = PERSONAL_ALLOWANCE - (rate_above/2)
        NEW_BASIC_RATE_THRESHOLD = BASIC_RATE_THRESHOLD - PERSONAL_ALLOWANCE
        income_tax = (BASIC_RATE_THRESHOLD - PERSONAL_ALLOWANCE) * BASIC_RATE + \
                    (annual_income - NEW_PERSONAL_ALLOWANCE - NEW_BASIC_RATE_THRESHOLD) * HIGHER_RATE
    elif annual_income > HIGHER_RATE_THRESHOLD:
        NEW_BASIC_RATE_THRESHOLD = BASIC_RATE_THRESHOLD - PERSONAL_ALLOWANCE
        income_tax = NEW_BASIC_RATE_THRESHOLD * BASIC_RATE + \
                    (HIGHER_RATE_THRESHOLD - NEW_BASIC_RATE_THRESHOLD) * HIGHER_RATE + \
                    (annual_income - HIGHER_RATE_THRESHOLD) * ADDITIONAL_RATE
    
    # National Insurance
    if annual_income <= NI_THRESHOLD:
        ni_contribution = 0
    elif annual_income <= NI_UPPER_THRESHOLD:
        ni_contribution = (annual_income - NI_THRESHOLD) * NI_BASIC_RATE
    else:
        ni_contribution = (NI_UPPER_THRESHOLD - NI_THRESHOLD) * NI_BASIC_RATE + \
                         (annual_income - NI_UPPER_THRESHOLD) * NI_HIGHER_RATE
    
    net_income = annual_income - income_tax - ni_contribution
    
    return {
        'gross_income': annual_income,
        'income_tax': income_tax,
        'ni_contribution': ni_contribution,
        'total_tax': income_tax + ni_contribution,
        'net_income': net_income,
        'effective_tax_rate': (income_tax + ni_contribution) / annual_income if annual_income > 0 else 0
    }

def calculate_pension_tax_relief(pension_contribution: float, annual_income: float) -> float:
    """Calculate tax relief on pension contributions"""
    government_relief = pension_contribution * 0.25
    if annual_income <= BASIC_RATE_THRESHOLD:
        extra_tax_relief = 0
    elif annual_income < HIGHER_RATE_THRESHOLD:
        extra_tax_relief = (pension_contribution + government_relief) * (HIGHER_RATE-BASIC_RATE)
    elif annual_income >= HIGHER_RATE_THRESHOLD:
        extra_tax_relief = (pension_contribution + government_relief) * (ADDITIONAL_RATE-BASIC_RATE)
    
    return {"government_relief": government_relief,
            "extra_tax_relief": extra_tax_relief,
            "total_tax_relief": government_relief + extra_tax_relief,
            "total_pension_amount": pension_contribution + government_relief
            }

extra_payments_by_year = {
    2025: 50000
    }    # £5,000 extra in 2025

def calculate_mortgage_scenarios(
    principal: float, 
    rate: float, 
    years: int, 
    extra_annual_repayments: dict()) -> float:
    #
    """Calculate mortgage payoff scenarios with different extra payment amounts"""
    monthly_balance = []
    start_year = datetime.now().year
    start_month = datetime.now().month
    monthly_rate = rate / 12
    total_payment_months = (years * 12) + start_month

    if monthly_rate == 0:  # Handle 0% interest rate
        monthly_payment = principal / total_payment_months
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**total_payment_months) / \
                        ((1 + monthly_rate)**total_payment_months - 1)
    
    remaining_balance = principal

    for month in range((1+ start_month), (total_payment_months+1)):
        years_lapsed = (month-1) // 12 
        current_year = start_year + years_lapsed 
        

        if (remaining_balance- monthly_payment) > 0:
            print(remaining_balance)
            if current_year in extra_annual_repayments.keys():
                extra_monthly_payment = extra_annual_repayments[current_year] / 12
                interest_repayment = remaining_balance * monthly_rate
                capital_repayment = monthly_payment + extra_monthly_payment - interest_repayment

                remaining_balance -= capital_repayment
                
                monthly_balance.append({
                    'month': ((month-1)%12)+1,
                    'year': current_year,
                    'monthly_payment': monthly_payment + extra_monthly_payment,
                    'extra_monthly_payment': extra_monthly_payment,
                    'capital_repayment': capital_repayment,
                    'interest_repayment': interest_repayment,
                    'remaining_balance': remaining_balance,
                })
                month += 1
            
            else:
                extra_monthly_payment = 0
                interest_repayment = remaining_balance * monthly_rate
                capital_repayment = monthly_payment - interest_repayment               

                remaining_balance -= capital_repayment
                monthly_balance.append({
                    'month': ((month-1)%12)+1,
                    'year': current_year,
                    'monthly_payment': monthly_payment,
                    'extra_monthly_payment': extra_monthly_payment,
                    'capital_repayment': capital_repayment,
                    'interest_repayment': interest_repayment,
                    'remaining_balance': remaining_balance,
                })

                month += 1

        else:            
            interest_repayment = (remaining_balance*monthly_rate)
            monthly_payment = remaining_balance + interest_repayment
            remaining_balance = 0
            extra_monthly_payment = 0
            capital_repayment = monthly_payment - interest_repayment
           

            print(interest_repayment)
            print(monthly_payment)
            print(capital_repayment)

            monthly_balance.append({
                    'month': ((month-1)%12)+1,
                    'year': current_year,
                    'monthly_payment': monthly_payment,
                    'extra_monthly_payment': extra_monthly_payment,
                    'capital_repayment': capital_repayment,
                    'interest_repayment': interest_repayment,
                    'remaining_balance': remaining_balance,
                })
            
            break

    
    monthly_balance = pd.DataFrame(monthly_balance)
    monthly_balance['month_year'] = pd.to_datetime(monthly_balance['year'].astype(str) + '-' + monthly_balance['month'].astype(str), format = '%Y-%m')
    monthly_balance = monthly_balance.sort_values('month_year')
    return monthly_balance

def mortgage_overpayment_summary(principal: float, rate: float, years: int, extra_annual_repayments: dict()) -> list:
    original_repayments = calculate_mortgage_scenarios(principal, rate, years, extra_annual_repayments = {})
    overpayments = calculate_mortgage_scenarios(principal, rate, years, extra_annual_repayments)
    total_interest_saved = original_repayments['interest_repayment'].sum() - overpayments['interest_repayment'].sum()

    original_months = years * 12
    months_with_repayment = overpayments['month'].max()
    
    return {
        'total_interest_saved': total_interest_saved,
        'total_interest_saved_percentage': total_interest_saved / original_repayments['interest_repayment'].sum() * 100,
        'total_overpayments': overpayments['extra_monthly_payment'].sum(),
        'overpayment_rate_of_return_yoy': (total_interest_saved / overpayments['extra_monthly_payment'].sum()) / (overpayments['month'].max()) * 12*100,
        'total_years_months_saved_months': f'{(original_months - months_with_repayment) // 12} years and {(original_months - months_with_repayment) % 12} months'
    }

def charity_tax_relief(charity_donation: float, annual_income: float) -> float:
    """Calculate tax relief on charity contributions"""
    gift_aid_amount = charity_donation / 0.8
    if annual_income <= BASIC_RATE_THRESHOLD:
        charity_tax_relief = 0
    elif annual_income < HIGHER_RATE_THRESHOLD:
        charity_tax_relief = gift_aid_amount * (HIGHER_RATE-BASIC_RATE)
    elif annual_income >= HIGHER_RATE_THRESHOLD:
        charity_tax_relief = gift_aid_amount * (ADDITIONAL_RATE-BASIC_RATE)

    return {"gift_aid_amount": gift_aid_amount,
            "charity_tax_relief": charity_tax_relief,
            "total_tax_relief": charity_tax_relief + gift_aid_amount - charity_donation
            }

def monthly_savings(
    annual_income: float,
    annual_base_salary: float,
    monthly_expenses: Optional[float] = 0, 
    annual_charity_donation: Optional[float] = 0, 
    annual_mortgage_overpayment: Optional[float] = 0, 
    principal: Optional[float] = 0, 
    rate: Optional[float] = 0, 
    years: Optional[int] = 0, 
    pension_allocation: Optional[float] = 0, #9% based on base salary
    stocks_ISA_annual_amount: Optional[float] = 0, 
    sipp_pension_annual_amount: Optional[float] = 0
    ) -> dict:

    monthly_net_income = calculate_uk_tax(annual_income)['net_income'] / 12
    mortgage_repayments = calculate_mortgage_scenarios(principal, rate, years, extra_annual_repayments = {})['monthly_payment'].mean()
    monthly_mortgage_overpayment = annual_mortgage_overpayment / 12

    monthly_charity_donation = annual_charity_donation / 12
    monthly_charity_tax_relief = charity_tax_relief(annual_charity_donation, annual_income)['charity_tax_relief'] /12
    monthly_paye_pension_contribution = pension_allocation * annual_base_salary/12

    monthly_stocks_isa_contribution = stocks_ISA_annual_amount/12
    monthly_sipp_pension_contribution = sipp_pension_annual_amount/12 + calculate_pension_tax_relief(sipp_pension_annual_amount, annual_income)['government_relief'] / 12

    monthly_pension_tax_relief = calculate_pension_tax_relief(monthly_sipp_pension_contribution*12, annual_income)['extra_tax_relief'] / 12

    monthly_net_savings = monthly_net_income - monthly_expenses  - mortgage_repayments - monthly_mortgage_overpayment- monthly_pension_contribution - monthly_charity_donation \
                        + monthly_charity_tax_relief + monthly_pension_tax_relief

    return {"monthly_income": monthly_net_income,
            "monthly_expenses": monthly_expenses,
            "monthly_mortgage_repayments": mortgage_repayments,
            "monthly_paye_pension_contribution": monthly_paye_pension_contribution,
            "monthly_charity_donation": monthly_charity_donation,
            "monthly_charity_tax_relief": monthly_charity_tax_relief,
            "monthlt_savings": monthly_net_savings,
            "monthly_stocks_isa_contribution": monthly_stocks_isa_contribution,
            "monthly_sipp_pension_contribution": monthly_sipp_pension_contribution,
            "monthly_pension_tax_relief": monthly_pension_tax_relief
            }


def project_investments(
    principal: float, 
    isa_monthly_contribution: float, 
    pension_monthly_contribution: float, 
    savings_monthly_contribution: float,
    years_with_contribution: int, 
    projection_years: int,
    isa_yoy_growth_rate: float,
    pension_yoy_growth_rate: float,
    savings_yoy_growth_rate: float) -> List[float]:

    """Project investment growth over time with compound interest"""
    start_year = datetime.now().year
    start_month = datetime.now().month
    total_months = (projection_years * 12) + start_month
    monthly_isa_growth_rate = (1 + isa_yoy_growth_rate) ** (1/12) - 1
    monthly_pension_growth_rate = (1 + pension_yoy_growth_rate) ** (1/12) - 1
    monthly_savings_growth_rate = (1 + savings_yoy_growth_rate) ** (1/12) - 1

    avg_monthly_growth_rate = (
        monthly_isa_growth_rate * (isa_monthly_contribution / (pension_monthly_contribution + isa_monthly_contribution + savings_monthly_contribution)) +
        monthly_pension_growth_rate * (pension_monthly_contribution / (pension_monthly_contribution + isa_monthly_contribution + savings_monthly_contribution)) +
        monthly_savings_growth_rate * (savings_monthly_contribution / (pension_monthly_contribution + isa_monthly_contribution + savings_monthly_contribution))
    )

    isa_balance = 0
    pension_balance = 0
    savings_balance = 0
    balances = []
    
    for month in range((1+ start_month), total_months+1):
        if month == (1+ start_month):
            principal = principal
            isa_balance = isa_monthly_contribution
            pension_balance = pension_monthly_contribution
            savings_balance = savings_monthly_contribution
            total_balance = principal + isa_monthly_contribution + pension_monthly_contribution + savings_monthly_contribution
        elif month <= ((years_with_contribution * 12)+start_month):
            principal = principal * (1 + avg_monthly_growth_rate)
            isa_balance = isa_balance * (1 + monthly_isa_growth_rate) + isa_monthly_contribution
            pension_balance = pension_balance * (1 + monthly_pension_growth_rate) + pension_monthly_contribution
            savings_balance = savings_balance * (1 + monthly_savings_growth_rate) + savings_monthly_contribution
            total_balance = principal + isa_balance + pension_balance + savings_balance
        elif month > ((years_with_contribution * 12)+start_month):
            principal = principal * (1 + avg_monthly_growth_rate)
            isa_balance = isa_balance * (1 + monthly_isa_growth_rate)
            pension_balance = pension_balance * (1 + monthly_pension_growth_rate)
            savings_balance = savings_balance * (1 + monthly_savings_growth_rate)
            total_balance = principal + isa_balance + pension_balance + savings_balance


        balance_dict = {
            'month': ((month-1)%12)+1,
            'projection_year': start_year + (month - 1) // 12,
            'total_balance': total_balance,
            'principal': principal,
            'isa_balance': isa_balance,
            'pension_balance': pension_balance,
            'savings_balance': savings_balance
        }
        balances.append(balance_dict)

    total_balance = pd.DataFrame(balances)
    return total_balance




if __name__ == "__main__":
    print(project_investments(
    principal=55000,
    isa_monthly_contribution=7200/12,
    pension_monthly_contribution=6000/12,
    savings_monthly_contribution=720/12,
    years_with_contribution=5,
    projection_years=20,
    isa_yoy_growth_rate=0.07,
    pension_yoy_growth_rate=0.06,
    savings_yoy_growth_rate=0.03
    ))
    # print(calculate_mortgage_scenarios(
    #     principal=345000, 
    #     rate=0.041, 
    #     years=27, 
    #     extra_annual_repayments={2026: 10000, 2027: 5000, 2028: 2000}))

    # original_mortgage = calculate_mortgage_scenarios(
    #     345000, 0.041, 27, {}
    # )

    # mortgage_with_overpayment = calculate_mortgage_scenarios(
    #     345000, 0.041, 27, {2026: 100000, 2027: 5000, 2028: 2000}
    # )
        
    # interest_saved = original_mortgage.groupby('year')['interest_repayment'].sum() - mortgage_with_overpayment.groupby('year')['interest_repayment'].sum()
    # interest_saved_pd = pd.DataFrame(interest_saved)
    # interest_saved_pd['year'] = interest_saved_pd.index
    # print(original_mortgage)
    # print(mortgage_with_overpayment)
    # print(interest_saved_pd)