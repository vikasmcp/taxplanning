import sys
import os
import traceback
from typing import Any, List, Dict
import pandas as pd
import streamlit as st
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

class TaxCalculator:
    def __init__(self):
        self.tax_slabs = {
            'old': [
                (250000, 0, 0),
                (500000, 250000, 0.05),
                (750000, 500000, 0.10),
                (1000000, 750000, 0.15),
                (1250000, 1000000, 0.20),
                (1500000, 1250000, 0.25),
                (float('inf'), 1500000, 0.30)
            ],
            'new': [
                (300000, 0, 0),
                (600000, 300000, 0.05),
                (900000, 600000, 0.10),
                (1200000, 900000, 0.15),
                (1500000, 1200000, 0.20),
                (float('inf'), 1500000, 0.30)
            ]
        }
        self.deductions = {
            '80C': {'limit': 150000, 'items': ['PPF', 'ELSS', 'Life Insurance', 'EPF']},
            '80D': {'limit': 25000, 'items': ['Health Insurance']},
            '80TTA': {'limit': 10000, 'items': ['Savings Account Interest']},
            'HRA': {'limit': 'Based on Rules', 'items': ['House Rent']}
        }

    def calculate_tax(self, income: float, deductions: Dict[str, float], regime: str = 'old') -> Dict[str, Any]:
        """
        Calculate tax liability based on income and deductions
        Args:
            income (float): Gross annual income
            deductions (Dict[str, float]): Dictionary of deductions under various sections
            regime (str): 'old' or 'new' tax regime
        Returns:
            Dict containing tax calculation details
        """
        total_deductions = sum(deductions.values())
        taxable_income = income - (total_deductions if regime == 'old' else 0)
        
        tax = 0
        tax_breakup = []
        
        for slab_limit, base, rate in self.tax_slabs[regime]:
            if taxable_income > base:
                taxable_amount = min(taxable_income - base, slab_limit - base)
                slab_tax = taxable_amount * rate
                tax += slab_tax
                tax_breakup.append({
                    'slab': f"{base+1}-{slab_limit}",
                    'rate': f"{rate*100}%",
                    'tax': slab_tax
                })
                
                if taxable_income <= slab_limit:
                    break
        
        # Calculate cess
        cess = tax * 0.04
        
        return {
            'gross_income': income,
            'total_deductions': total_deductions,
            'taxable_income': taxable_income,
            'tax_breakup': tax_breakup,
            'base_tax': tax,
            'cess': cess,
            'total_tax': tax + cess
        }

    def get_recommendations(self, income: float, current_deductions: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate tax-saving recommendations
        Args:
            income (float): Gross annual income
            current_deductions (Dict[str, float]): Current deductions being claimed
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for section, details in self.deductions.items():
            current = current_deductions.get(section, 0)
            if current < details['limit'] or details['limit'] == 'Based on Rules':
                remaining = details['limit'] - current if details['limit'] != 'Based on Rules' else 0
                recommendations.append({
                    'section': section,
                    'current_utilization': current,
                    'remaining_limit': remaining,
                    'suggested_instruments': details['items']
                })
        
        return recommendations

    def generate_tax_report(self, tax_details: Dict[str, Any], recommendations: List[Dict[str, Any]], 
                          output_format: str = 'excel') -> str:
        """
        Generate and export tax computation report
        Args:
            tax_details (Dict[str, Any]): Tax calculation details
            recommendations (List[Dict[str, Any]]): List of tax saving recommendations
            output_format (str): Output format (currently supports 'excel' only)
        Returns:
            str: Path to the generated report file
        """
        filename = f"tax_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if output_format.lower() == 'excel':
            with pd.ExcelWriter(f"{filename}.xlsx", engine='openpyxl') as writer:
                # Tax Calculation Sheet
                tax_df = pd.DataFrame([{
                    'Component': k,
                    'Amount': v if isinstance(v, (int, float)) else ''
                } for k, v in tax_details.items() if k != 'tax_breakup'])
                tax_df.to_excel(writer, sheet_name='Tax Calculation', index=False)
                
                # Tax Breakup Sheet
                if tax_details.get('tax_breakup'):
                    breakup_df = pd.DataFrame(tax_details['tax_breakup'])
                    breakup_df.to_excel(writer, sheet_name='Tax Breakup', index=False)
                
                # Recommendations Sheet
                recommendations_df = pd.DataFrame(recommendations)
                recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
            
            return f"{filename}.xlsx"
        
        return "Unsupported format"

class TaxPlannerMCP:
    def __init__(self):
        load_dotenv()
        self.mcp = FastMCP("taxation_tool")
        self.calculator = TaxCalculator()
        self.register_tools()
        
    def register_tools(self):
        @self.mcp.tool()
        async def calculate_tax_liability(income: float, deductions: Dict[str, float], regime: str = 'old') -> Dict[str, Any]:
            """Calculate tax liability based on provided income and deductions"""
            try:
                return self.calculator.calculate_tax(income, deductions, regime)
            except Exception as e:
                print(f"Error calculating tax: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {}

        @self.mcp.tool()
        async def get_tax_recommendations(income: float, deductions: Dict[str, float]) -> List[Dict[str, Any]]:
            """Get tax saving recommendations based on current financial status"""
            try:
                return self.calculator.get_recommendations(income, deductions)
            except Exception as e:
                print(f"Error generating recommendations: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return []

        @self.mcp.tool()
        async def generate_tax_report(tax_details: Dict[str, Any], recommendations: List[Dict[str, Any]], 
                                   output_format: str = 'excel') -> str:
            """Generate and export tax computation report"""
            try:
                filename = f"tax_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                if output_format.lower() == 'excel':
                    # Create Excel report
                    with pd.ExcelWriter(f"{filename}.xlsx", engine='openpyxl') as writer:
                        # Tax Calculation Sheet
                        tax_df = pd.DataFrame([{
                            'Component': k,
                            'Amount': v if isinstance(v, (int, float)) else ''
                        } for k, v in tax_details.items() if k != 'tax_breakup'])
                        tax_df.to_excel(writer, sheet_name='Tax Calculation', index=False)
                        
                        # Tax Breakup Sheet
                        if tax_details.get('tax_breakup'):
                            breakup_df = pd.DataFrame(tax_details['tax_breakup'])
                            breakup_df.to_excel(writer, sheet_name='Tax Breakup', index=False)
                        
                        # Recommendations Sheet
                        recommendations_df = pd.DataFrame(recommendations)
                        recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
                    
                    return f"{filename}.xlsx"
                
                return "Unsupported format"
                
            except Exception as e:
                print(f"Error generating report: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return str(e)

    def run(self):
        """Start the MCP server"""
        try:
            print("Running Tax Planning MCP Server...", file=sys.stderr)
            self.mcp.run(transport="stdio")
        except Exception as e:
            print(f"Fatal Error in MCP Server: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    tax_planner = TaxPlannerMCP()
    tax_planner.run()