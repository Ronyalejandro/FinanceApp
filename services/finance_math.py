"""Servicio para cálculos financieros y proyecciones."""
from typing import List, Tuple
from db.database import DatabaseManager

class FinanceMath:
    @staticmethod
    def calculate_average_savings(db: DatabaseManager, days: int = 90) -> float:
        """
        Calcula el ahorro mensual promedio basado en los últimos 'days' días (por defecto 90).
        Fórmula: (Suma(Ingresos) - Suma(Gastos)) / (días / 30)
        """
        transactions = db.get_recent_transactions(days)
        
        ingresos = sum(t[3] for t in transactions if t[1] == "Ingreso")
        gastos = sum(t[3] for t in transactions if t[1] == "Gasto")
        
        net_savings = ingresos - gastos
        
        # Si no hay ahorros o es negativo, devuelve 0 (¿o permitir negativo? Las proyecciones suelen asumir inversión positiva)
        # Pero para el 'ahorro promedio' podría ser negativo.
        
        months = max(days / 30, 1) # Evitar división por cero, asumir al menos un marco de tiempo de 1 mes
        monthly_average = net_savings / months
        
        return monthly_average

    @staticmethod
    def calculate_compound_growth(principal: float, monthly_contribution: float, 
                                  rate_annual: float = 0.08, months: int = 120) -> Tuple[List[int], List[float]]:
        """
        Calcula el crecimiento del interés compuesto mensualmente.
        Devuelve (lista_de_meses, lista_de_montos).
        """
        rate_monthly = rate_annual / 12
        amounts = []
        time_points = []
        
        current_amount = principal
        
        # Iniciar en el mes 0
        amounts.append(current_amount)
        time_points.append(0)
        
        for m in range(1, months + 1):
            # Interés ganado
            interest = current_amount * rate_monthly
            # Añadir contribución
            current_amount += interest + monthly_contribution
            
            amounts.append(current_amount)
            time_points.append(m)
            
        return time_points, amounts
