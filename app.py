import streamlit as st
import pandas as pd
from taxation_tool import TaxCalculator

def main():
    st.title("Indian Tax Planning Assistant")
    
    calculator = TaxCalculator()
    
    # Sidebar for inputs
    st.sidebar.header("Financial Information")
    
    # Income Details
    income = st.sidebar.number_input("Annual Income (₹)", min_value=0.0, value=500000.0, step=10000.0)
    
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
        # Get tax comparison
        comparison = calculator.compare_tax_regimes(income, deductions)
        old_regime = comparison['old_regime']
        new_regime = comparison['new_regime']
        
        # Get recommendations
        recommendations = calculator.get_recommendations(income, deductions)
        
        # Display Results
        st.header("Tax Regime Comparison")
        
        # Create three columns for comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Old Regime")
            st.write(f"Gross Income: ₹{old_regime['gross_income']:,.2f}")
            st.write(f"Total Deductions: ₹{old_regime['total_deductions']:,.2f}")
            st.write(f"Taxable Income: ₹{old_regime['taxable_income']:,.2f}")
            st.write(f"Base Tax: ₹{old_regime['base_tax']:,.2f}")
            st.write(f"Cess: ₹{old_regime['cess']:,.2f}")
            st.write(f"Total Tax: ₹{old_regime['total_tax']:,.2f}")
        
        with col2:
            st.subheader("New Regime")
            st.write(f"Gross Income: ₹{new_regime['gross_income']:,.2f}")
            st.write(f"Total Deductions: ₹{new_regime['total_deductions']:,.2f}")
            st.write(f"Taxable Income: ₹{new_regime['taxable_income']:,.2f}")
            st.write(f"Base Tax: ₹{new_regime['base_tax']:,.2f}")
            st.write(f"Cess: ₹{new_regime['cess']:,.2f}")
            st.write(f"Total Tax: ₹{new_regime['total_tax']:,.2f}")
        
        with col3:
            st.subheader("Summary")
            st.write("Recommended Regime:", comparison['recommended_regime'].upper())
            st.write(f"You save: ₹{comparison['savings']:,.2f}")
            
            # Add a visual indicator for recommended regime
            if comparison['recommended_regime'] == 'old':
                st.success("Old Regime is better for you!")
            else:
                st.success("New Regime is better for you!")
        
        # Tax Breakup Comparison
        st.header("Tax Breakup Comparison")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Old Regime Breakup")
            old_breakup_df = pd.DataFrame(old_regime['tax_breakup'])
            st.table(old_breakup_df)
        
        with col2:
            st.subheader("New Regime Breakup")
            new_breakup_df = pd.DataFrame(new_regime['tax_breakup'])
            st.table(new_breakup_df)
        
        # Recommendations
        if comparison['recommended_regime'] == 'old':
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
            filename = calculator.generate_tax_report(comparison, recommendations)
            st.success(f"Report exported successfully as {filename}")

if __name__ == "__main__":
    main()