import streamlit as st
import pandas as pd
from taxation_tool import TaxCalculator
import json

def main():
    st.title("Indian Tax Planning Assistant")
    
    calculator = TaxCalculator()
    
    # Sidebar for inputs
    st.sidebar.header("Financial Information")
    
    # Income Details
    income = st.sidebar.number_input("Annual Income (₹)", min_value=0.0, value=500000.0, step=10000.0)
    
    # Tax Regime Selection
    regime = st.sidebar.radio("Select Tax Regime", ['old', 'new'])
    
    # Deductions Input
    st.sidebar.header("Deductions")
    deductions = {}
    
    # 80C Deductions
    st.sidebar.subheader("Section 80C (Max: ₹1,50,000)")
    deductions['80C'] = st.sidebar.number_input("80C Investments (PPF, ELSS, etc.)", 
                                              min_value=0.0, max_value=150000.0, value=0.0)
    
    # 80D Deductions
    st.sidebar.subheader("Section 80D (Max: ₹25,000)")
    deductions['80D'] = st.sidebar.number_input("Health Insurance Premium", 
                                              min_value=0.0, max_value=25000.0, value=0.0)
    
    # 80TTA Deductions
    st.sidebar.subheader("Section 80TTA (Max: ₹10,000)")
    deductions['80TTA'] = st.sidebar.number_input("Savings Account Interest", 
                                                min_value=0.0, max_value=10000.0, value=0.0)
    
    # HRA Deductions
    st.sidebar.subheader("HRA")
    deductions['HRA'] = st.sidebar.number_input("House Rent Allowance", 
                                              min_value=0.0, value=0.0)

    # Calculate Tax
    if st.button("Calculate Tax"):
        # Get tax calculation
        tax_details = calculator.calculate_tax(income, deductions, regime)
        
        # Get recommendations
        recommendations = calculator.get_recommendations(income, deductions)
        
        # Display Results
        st.header("Tax Calculation Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Income & Deductions")
            st.write(f"Gross Income: ₹{tax_details['gross_income']:,.2f}")
            st.write(f"Total Deductions: ₹{tax_details['total_deductions']:,.2f}")
            st.write(f"Taxable Income: ₹{tax_details['taxable_income']:,.2f}")
        
        with col2:
            st.subheader("Tax Liability")
            st.write(f"Base Tax: ₹{tax_details['base_tax']:,.2f}")
            st.write(f"Health & Education Cess: ₹{tax_details['cess']:,.2f}")
            st.write(f"Total Tax: ₹{tax_details['total_tax']:,.2f}")
        
        # Tax Breakup
        st.header("Tax Breakup")
        breakup_df = pd.DataFrame(tax_details['tax_breakup'])
        st.table(breakup_df)
        
        # Recommendations
        st.header("Tax Saving Recommendations")
        for rec in recommendations:
            with st.expander(f"Section {rec['section']} Recommendations"):
                st.write(f"Current Utilization: ₹{rec['current_utilization']:,.2f}")
                if isinstance(rec['remaining_limit'], (int, float)):
                    st.write(f"Remaining Limit: ₹{rec['remaining_limit']:,.2f}")
                st.write("Suggested Investment Options:")
                for item in rec['suggested_instruments']:
                    st.write(f"- {item}")
        
        # Export Options
        st.header("Export Report")
        if st.button("Export to Excel"):
            filename = calculator.generate_tax_report(tax_details, recommendations)
            st.success(f"Report exported successfully as {filename}")

if __name__ == "__main__":
    main()