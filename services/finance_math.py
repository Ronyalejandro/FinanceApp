"""Service for financial calculations and projections."""
from typing import List, Tuple
from db.database import DatabaseManager

class FinanceMath:
    @staticmethod
    def calculate_average_savings(db: DatabaseManager, days: int = 90) -> float:
        """
        Calculates the average monthly savings based on the last 'days' (default 90).
        Formula: (Sum(Income) - Sum(Expenses)) / (days / 30)
        """
        transactions = db.get_recent_transactions(days)
        
        ingresos = sum(t[3] for t in transactions if t[1] == "Ingreso")
        gastos = sum(t[3] for t in transactions if t[1] == "Gasto")
        
        net_savings = ingresos - gastos
        
        # If no savings or negative, return 0 (or allow negative? Projections usually assume positive investment)
        # But for 'average savings' it could be negative.
        
        months = max(days / 30, 1) # Avoid division by zero, assume at least 1 month timeframe
        monthly_average = net_savings / months
        
        return monthly_average

    @staticmethod
    def calculate_compound_growth(principal: float, monthly_contribution: float, 
                                  rate_annual: float = 0.08, months: int = 120) -> Tuple[List[int], List[float]]:
        """
        Calculates compound interest growth monthly.
        Returns (list_of_months, list_of_amounts).
        """
        rate_monthly = rate_annual / 12
        amounts = []
        time_points = []
        
        current_amount = principal
        
        # Start at month 0
        amounts.append(current_amount)
        time_points.append(0)
        
        for m in range(1, months + 1):
            # Interest earned
            interest = current_amount * rate_monthly
            # Add contribution
            current_amount += interest + monthly_contribution
            
            amounts.append(current_amount)
            time_points.append(m)
            
        return time_points, amounts
