import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional, final
from datetime import datetime
from calculations import *


def main():
    # Page Configs
    st.set_page_config(layout="wide",
                       page_title="UK Financial Planning Calculator",
                       page_icon="🏦")

    # Sidebar inputs
    st.sidebar.header("📊 Financial Inputs")
    
    # 1. Annual Income
    st.sidebar.subheader("💼 Income")
    annual_salary = st.sidebar.number_input("Annual Base Salary (£)", value=50000, step=1000)
    annual_bonus = st.sidebar.number_input("Annual Bonus (£)", value=5000, step=1000)
    total_annual_income = annual_salary + annual_bonus
    
    # 2. RSU Details
    st.sidebar.subheader("📈 RSU (Restricted Stock Units)")
    num_rsu_entries = st.sidebar.number_input("Number of RSU entries", min_value=0, max_value=5, value=1)
    currency_conversion = st.sidebar.number_input("USD to GBP conversion rate", min_value=0.0, max_value=1.0, value = 0.79, step=0.01)

    rsu_data = []
    total_rsu_value = 0
    
    for i in range(num_rsu_entries):
        st.sidebar.markdown(f"**RSU Entry {i+1}**")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            num_stocks = st.number_input(f"Number of stocks", value=100, key=f"stocks_{i}")
        with col2:
            stock_price = st.number_input(f"Stock price ($)", value=50.0, key=f"price_{i}")
        
        vest_date = st.sidebar.date_input(f"Vesting date {i+1}", key=f"date_{i}")
        
        entry_value = num_stocks * stock_price * currency_conversion
        total_rsu_value += entry_value
        
        rsu_data.append({
            'entry': i+1,
            'num_stocks': num_stocks,
            'stock_price': stock_price,
            'total_value': entry_value,
            'vest_date': vest_date
        })


    # 3. Debt/Mortgage
    st.sidebar.subheader("🏠 Debt & Mortgage")
    monthly_expense_excl_mortgage  = st.sidebar.number_input("Monthly Expenses excl Mortgage (£)", value=800, step=100)

    mortgage_amount = st.sidebar.number_input("Mortgage/Debt Amount (£)", value=345000, step=5000)
    mortgage_rate = st.sidebar.number_input("Interest Rate (%)", value=4.1, step=0.1) / 100
    mortgage_years = st.sidebar.number_input("Mortgage Term (years)", value=27, step=1)

    
    # 4. Current Savings
    st.sidebar.subheader("💰 Current Savings")
    current_savings = st.sidebar.number_input("Current Savings (£)", value=20000, step=1000)
    current_isa = st.sidebar.number_input("Current ISA (£)", value=20000, step=1000)
    current_pension = st.sidebar.number_input("Current Pension (£)", value=15000, step=1000)

     # 5. Charity Donations
    st.sidebar.subheader("💝 Charity Donations")
    annual_charity_donation = st.sidebar.number_input("Annual Charity Donation (£)", value=0, step=1000)
    
    # 6. Allocation Strategy
    st.sidebar.subheader("📋 Allocation Strategy")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        annual_isa_allocation = st.sidebar.number_input("Annual ISA Allocation (£)", value=1000, min_value=0, max_value=20000, step=1000)
        annual_pension_allocation = st.sidebar.number_input("Annual Pension Allocation (£)", value=1000, min_value=0, max_value=60000, step=1000)
    with col2:
        annual_normal_savings_allocation = st.sidebar.number_input("Annual Normal Savings (£)", value=1000, min_value=0, step=1000)
    
    # 7. Growth rates
    st.sidebar.subheader("💰 Investment Growth Rates")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        isa_growth_rate = st.number_input("ISA Growth Rate (%)", value=6.0, step=0.1) / 100
        pension_growth_rate = st.number_input("Pension Growth Rate (%)", value=7.0, step=0.1) / 100
    with col2:
        normal_savings_rate = st.number_input("Normal Savings Rate (%)", value=3.0, step=0.1) / 100
        rsu_growth_rate = st.number_input("RSU Growth Rate (%)", value=8.0, step=0.1) / 100
    
    # 8. Projection Period
    st.sidebar.subheader("Projection Period")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        years_to_retirement = st.number_input("Years to Retirement", value=10, step = 1)
    with col2:
        projection_years = st.number_input("Projection Years", value=20, min_value=1, max_value=50)
    
    # Main content
    st.header("UK Financial Planning Calculator")
    st.subheader("📊 Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        tax_summary = calculate_uk_tax(total_annual_income, 0)
        st.metric("Gross Annual Income", f"£{total_annual_income:,.0f}")
        #st.caption(f"💼 Income:£{total_annual_income:,.0f} • 📈 RSU: £{total_rsu_value:,.0f}")
    with col2:
        st.metric("Net Annual Income", f"£{tax_summary['net_income']:,.0f}")
    with col3:
        st.metric("Total Tax & NI", f"£{tax_summary['total_tax']:,.0f}")
    with col4:
        st.metric("Effective Tax Rate", f"{tax_summary['effective_tax_rate']:.1%}")
    
    # Calculate annual contributions
    pension_tax_relief = calculate_pension_tax_relief(
        annual_pension_allocation,
        total_annual_income
    )
    charity_tax_relief_amount =charity_tax_relief(
        annual_charity_donation,
        total_annual_income
    )

    mortgage_annual = calculate_mortgage_scenarios(mortgage_amount, mortgage_rate, mortgage_years, {})['monthly_payment'].mean() * 12
    annual_expenses = monthly_expense_excl_mortgage * 12
    
    net_savings = (tax_summary['net_income'] 
                    - annual_expenses
                    - mortgage_annual
                    - annual_charity_donation)

    net_savings_with_tax_relief = net_savings + pension_tax_relief['extra_tax_relief'] + charity_tax_relief_amount['charity_tax_relief']+ pension_tax_relief['government_relief']

    st.divider()

    expenses = (monthly_expense_excl_mortgage * 12) +(calculate_mortgage_scenarios(mortgage_amount, mortgage_rate, mortgage_years, {})['monthly_payment'].mean() * 12) + annual_charity_donation
    total_allocation = annual_isa_allocation + annual_pension_allocation + annual_normal_savings_allocation 


    col1, col2 = st.columns([2.5,1])
    with col1:
        st.subheader("Allocation Check")
        if (round(tax_summary['net_income'] - expenses - total_allocation)) < 0:
            st.error(f"Net Income: £{tax_summary['net_income']:,.0f}. \n\nExpenses: £{expenses:,.0f} & Total Savings: £{total_allocation:,.0f}\n\nPlease reduce savings or expenses by {abs(tax_summary['net_income'] - expenses - total_allocation):,.0f}")
            
        if (round(tax_summary['net_income'] - expenses - total_allocation)) > 0:
            st.error(f"Net Income: £{tax_summary['net_income']:,.0f} \n\nExpenses: £{expenses:,.0f} & Total Savings: £{total_allocation:,.0f}\n\nPlease increase Savings or Expenses by {abs(tax_summary['net_income'] - expenses - total_allocation):,.0f}")
            #additional_savings = tax_summary['net_income'] - expenses - total_allocation
        if (round(tax_summary['net_income'] - expenses - total_allocation)) == 0:
            st.success("✅ Allocation totals to Net Income")
        
        st.markdown("")
        colA, colB, colC = st.columns(3)
        with colA:
            st.metric(f"Total Savings", f"£{net_savings:,.0f}")
        with colB:
            st.metric(f"Total Expenses", f"£{expenses:,.0f}")
        with colC:
            st.metric(f"Total allocated savings", f"£{total_allocation:,.0f}")

    with col2:
        st.subheader("💰 Tax Relief Summary")
        total_tax_relief = net_savings_with_tax_relief - net_savings
        
        # Main total in a container
        with st.container():
            st.metric("Total Tax Relief", f"£{total_tax_relief:,.0f}")
        
        # Breakdown in organized sections
        st.markdown("**Breakdown:**")
        
        relief_data = [
            ("🏛️ Government Relief", pension_tax_relief['government_relief']),
            ("💝 Charity Tax Relief", charity_tax_relief_amount['charity_tax_relief']),
            ("🏦 Pension Tax Relief", pension_tax_relief['extra_tax_relief'])
        ]
        
        for label, amount in relief_data:
            if amount > 0:
                percentage = (amount / total_tax_relief * 100) if total_tax_relief > 0 else 0
                st.markdown(f"**{label}**: £{amount:,.0f} ({percentage:.1f}%)")


    st.divider()
    # RSU allocation
    #annual_rsu_isa = min(total_rsu_value * isa_allocation, ANNUAL_ISA_LIMIT - annual_isa_contribution)
    #annual_rsu_pension = min(total_rsu_value * pension_allocation, ANNUAL_PENSION_LIMIT - annual_pension_contribution)
    #annual_rsu_normal = total_rsu_value * normal_savings_allocation
    
    
    # Detailed tables
    st.subheader("📋 Detailed Projections")
    
    tab1, tab2, tab3 = st.tabs(["Savings Projection", "RSU Details", "Mortgage Scenarios"])
    
    with tab1:
        st.subheader("📈 Savings Projection")
        # Project investments
        total_annual_pension = annual_pension_allocation + pension_tax_relief['government_relief']

        total_balances_pd = project_investments(
            (current_savings + current_isa + current_pension),
            (annual_isa_allocation + pension_tax_relief['extra_tax_relief'] + charity_tax_relief_amount['charity_tax_relief'])/12,
            (total_annual_pension)/12,
            (annual_normal_savings_allocation)/12,
            years_to_retirement,
            projection_years,
            isa_growth_rate,
            pension_growth_rate,
            normal_savings_rate
        )

        total_balances_pd['month_year'] = pd.to_datetime(total_balances_pd['projection_year'].astype(str) + '-' + total_balances_pd['month'].astype(str))
        total_balances_pd = total_balances_pd.sort_values('month_year')

        first_isa_balance = total_balances_pd['isa_balance'].iloc[0]
        first_pension_balance = total_balances_pd['pension_balance'].iloc[0]
        first_normal_savings_balance = total_balances_pd['savings_balance'].iloc[0]
        first_total_balance = total_balances_pd['total_balance'].iloc[0]
        first_principal = total_balances_pd['principal'].iloc[0]


        final_isa_balance = total_balances_pd['isa_balance'].iloc[-1]
        final_pension_balance = total_balances_pd['pension_balance'].iloc[-1]
        final_normal_savings_balance = total_balances_pd['savings_balance'].iloc[-1]
        final_total_balance = total_balances_pd['total_balance'].iloc[-1]
        final_principal = total_balances_pd['principal'].iloc[-1]

        total_balances_pd = total_balances_pd[['month_year', 'principal', 'isa_balance', 'pension_balance', 'savings_balance', 'total_balance']]    

        col1, col2 = st.columns([1,3])
        with col1:
            st.metric("Total Savings", f"£{final_total_balance:,.0f}")
            st.metric(
                "Principal", 
                f"£{final_principal:,.0f}",
                delta=f"{((final_principal-first_principal)/first_principal)*100:.1f}%"
            )

            st.metric(
                "ISA Balance", 
                f"£{final_isa_balance:,.0f}",
                delta=f"{(final_isa_balance - (annual_isa_allocation*projection_years))/(annual_isa_allocation*years_to_retirement)*100:.1f}%"
            )

            st.metric(
                "Pension Balance", 
                f"£{final_pension_balance:,.0f}",
                delta=f"{(final_pension_balance- (annual_pension_allocation*projection_years))/(annual_pension_allocation*years_to_retirement)*100:.1f}%"
            )
            st.metric(
                "Normal Savings", 
                f"£{final_normal_savings_balance:,.0f}",
                delta=f"{(final_normal_savings_balance- (annual_normal_savings_allocation*years_to_retirement))/(annual_normal_savings_allocation*projection_years)*100:.1f}%"
            )
                
                                
        with col2:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=total_balances_pd['month_year'], y=total_balances_pd['principal'], 
                            name='Principal', line=dict(color='purple'), fill='tonexty', stackgroup='savings',
                            hovertemplate = '<br>Date: %{x}<br>%{fullData.name}: £%{y:,.0f}'
                            ),

                secondary_y=False,
            )

            fig.add_trace(
                go.Scatter(x=total_balances_pd['month_year'], y=total_balances_pd['isa_balance'], 
                            name='ISA', line=dict(color='blue'), fill='tonexty', stackgroup='savings',
                            hovertemplate = '<br>Date: %{x}<br>%{fullData.name}: £%{y:,.0f}'
                            ),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=total_balances_pd['month_year'], y=total_balances_pd['pension_balance'], 
                            name='Pension', line=dict(color='green'), fill='tonexty', stackgroup='savings',
                            hovertemplate = '<br>Date: %{x}<br>%{fullData.name}: £%{y:,.0f}'
                            ),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=total_balances_pd['month_year'], y=total_balances_pd['savings_balance'], 
                            name='Normal Savings', line=dict(color='orange'), fill='tonexty', stackgroup='savings',
                            hovertemplate = '<br>Date: %{x}<br>%{fullData.name}: £%{y:,.0f}'
                            ),

                secondary_y=False,
            )


            fig.update_xaxes(title_text="Years")
            fig.update_yaxes(title_text="Savings (£)", secondary_y=False, tickformat=",")
            fig.update_layout(
                title="Projected Savings Growth",
                showlegend=True,
                height = 600,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5
                )
            )
            
            st.plotly_chart(
                fig, 
                use_container_width=True, 
                use_container_height = True, 
                hovermode="y unified"
            )

        total_balances_st = total_balances_pd.rename(columns={'month_year': 'Date','principal': 'Principal', 'isa_balance': 'ISA', 'pension_balance': 'Pension', 'savings_balance': 'Normal Savings', 'total_balance': 'Total'})
        total_balances_st = total_balances_st.style.format(
            {
                'Date': '{:%d-%m-%Y}',
                'Principal': '£{:,.0f}',
                'ISA': '£{:,.0f}',
                'Pension': '£{:,.0f}',
                'Normal Savings': '£{:,.0f}',
                'Total': '£{:,.0f}'
            }
        )
        st.dataframe(
            total_balances_st, 
            use_container_width=True,
            hide_index=True,
            height=350
        )
    
    with tab2:
        rsu_df = pd.DataFrame(rsu_data)
        if not rsu_df.empty:
            st.dataframe(rsu_df, use_container_width=True)
    
    with tab3:
        st.subheader("🏠 Mortgage vs Extra Savings Analysis")
    
        extra_payment_amounts = {2026: 100000, 2027: 5000, 2028: 2000}
        original_mortgage = calculate_mortgage_scenarios(
            mortgage_amount, mortgage_rate, mortgage_years, {}
        )

        mortgage_with_overpayment = calculate_mortgage_scenarios(
            mortgage_amount, mortgage_rate, mortgage_years, extra_payment_amounts
        )
        
        interest_saved = original_mortgage.groupby('year')['interest_repayment'].sum() - mortgage_with_overpayment.groupby('year')['interest_repayment'].sum()
        interest_saved_pd = pd.DataFrame(interest_saved)
        interest_saved_pd['year'] = interest_saved_pd.index

        mortgage_fig = go.Figure()

        col_a, col_b = st.columns(2)
        with col_a:
            mortgage_fig.add_trace(
                go.Scatter(
                    x = original_mortgage['month_year'],
                    y = original_mortgage['remaining_balance'],
                    name = 'Original Mortgage',
                    line = dict(color='red'),
                    hovertemplate = '<br>Date: %{x}<br>Remaining Balance: £%{y:,.0f}<extra></extra>'
                )
            )

            mortgage_fig.add_trace(
                go.Scatter(
                    x = mortgage_with_overpayment['month_year'],
                    y = mortgage_with_overpayment['remaining_balance'],
                    name = 'Mortgage with Overpayments',
                    line = dict(color='green'),
                    hovertemplate = '<br>Date: %{x}<br>Remaining Balance: £%{y:,.0f}<extra></extra>'
                )
            )

            mortgage_fig.update_layout(
                title = 'Mortgage Repayment Comparison',
                xaxis_title = 'Date',
                yaxis_title = 'Remaining Balance (£)',
                hovermode = 'x unified',
                yaxis_tickformat = ',',
                height = 600,
                showlegend = True,
                legend = dict(
                    orientation = 'h',
                    yanchor = 'bottom',
                    y = 1.02,
                    xanchor = 'center',
                    x = 0.5
                )
            )

            st.plotly_chart(mortgage_fig, use_container_width=True)

        with col_b:
            interest_repayment_fig = go.Figure()
            interest_repayment_fig.add_trace(
                go.Bar(
                    x = interest_saved_pd['year'],
                    y = interest_saved_pd['interest_repayment'],
                    name = 'Interest Saved',
                    marker = dict(color='blue'),
                    hovertemplate = '<br>Year: %{x}<br>Interest Repayment Saved: £%{y:,.0f}<extra></extra>'
                )
            )
            # interest_repayment_fig.add_trace(
            #     go.Bar(
            #         x = mortgage_with_overpayment['month_year'],
            #         y = mortgage_with_overpayment['interest_repayment'],
            #         name = 'Mortgage with Overpayments',
            #         marker = dict(color='green'),
            #         hovertemplate = '<br>Date: %{x}<br>Interest Repayment: £%{y:,.0f}<extra></extra>'
            #     )
            # )

            interest_repayment_fig.update_layout(
                title = 'Interest Repayment Comparison',
                xaxis_title = 'Date',
                yaxis_title = 'Interest Repayment (£)',
                hovermode = 'x unified',
                yaxis_tickformat = ',',
                height = 600,
                showlegend = True,
                legend = dict(
                    orientation = 'h',
                    yanchor = 'bottom',
                    y = 1.02,
                    xanchor = 'center',
                    x = 0.5
                )
            )

            st.plotly_chart(interest_repayment_fig, use_container_width=True)

        st.dataframe(mortgage_with_overpayment.round(0), use_container_width=True)
        
    # Key insights
    st.subheader("💡 Key Insights")
    
    final_total = total_balances_pd.iloc[-1]['total_balance']
    final_isa = total_balances_pd.iloc[-1]['isa_balance']
    final_pension = total_balances_pd.iloc[-1]['pension_balance']
    
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        st.metric(
            f"Total after {projection_years} years",
            f"£{final_total:,.0f}",
            delta=f"£{final_total - (current_savings + current_pension):,.0f}"
        )
    
    with col_i2:
        annual_growth = ((final_total / (current_savings + current_pension + 1)) ** (1/projection_years) - 1) * 100
        st.metric("Annual Growth Rate", f"{annual_growth:.1f}%")
    
    with col_i3:
        monthly_savings_rate = (annual_isa_allocation + annual_isa_allocation + annual_normal_savings_allocation) / 12
        st.metric("Monthly Savings", f"£{monthly_savings_rate:,.0f}")

if __name__ == "__main__":
    main()