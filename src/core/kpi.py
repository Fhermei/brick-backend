"""
KPI Calculation Utilities for Brick SPMES

Formulas:
- KAR (KPI Achievement Ratio) = (Actual Value / Target Value) × 100
- BUR (Budget Utilisation Rate) = (Total Spent / Total Budget) × 100  
- BBR (Budget Burn Rate) = Total Spent / Days Elapsed
- Days to Exhaust = Remaining Budget / BBR
"""

from typing import Dict, Any
from datetime import datetime, date
import numpy as np


def compute_kar(actual_value: float, target_value: float) -> float:
    """
    Calculate KPI Achievement Ratio (KAR)
    
    Args:
        actual_value: Actual achieved value
        target_value: Target value to achieve
    
    Returns:
        KAR percentage (0-100+)
    """
    if not target_value or target_value == 0:
        return 0.0
    return round((actual_value / target_value) * 100, 2)


def get_kar_status(kar: float) -> Dict[str, Any]:
    """
    Get KAR status, color, and label based on threshold
    
    Thresholds:
        Critical: < 50%
        Warning: 50-74%
        Satisfactory: 75-99%
        Good: >= 100%
    """
    if kar < 50:
        return {
            "status": "critical",
            "color": "red",
            "label": "Critical",
            "bg_color": "bg-red-500/10",
            "border_color": "border-red-500/30",
            "text_color": "text-red-400"
        }
    elif kar < 75:
        return {
            "status": "warning",
            "color": "yellow",
            "label": "Warning",
            "bg_color": "bg-yellow-500/10",
            "border_color": "border-yellow-500/30",
            "text_color": "text-yellow-400"
        }
    elif kar < 100:
        return {
            "status": "satisfactory",
            "color": "green",
            "label": "Satisfactory",
            "bg_color": "bg-green-500/10",
            "border_color": "border-green-500/30",
            "text_color": "text-green-400"
        }
    else:
        return {
            "status": "good",
            "color": "emerald",
            "label": "Good",
            "bg_color": "bg-emerald-500/10",
            "border_color": "border-emerald-500/30",
            "text_color": "text-emerald-400"
        }


def compute_bur(total_spent: float, total_budget: float) -> float:
    """
    Calculate Budget Utilisation Rate (BUR)
    
    Args:
        total_spent: Amount spent so far
        total_budget: Total allocated budget
    
    Returns:
        BUR percentage (0-100+)
    """
    if not total_budget or total_budget == 0:
        return 0.0
    return round((total_spent / total_budget) * 100, 2)


def get_bur_status(bur: float) -> Dict[str, Any]:
    """
    Get BUR status, color, and alert level
    
    Thresholds:
        OK: < 80%
        Alert: 80-99%
        Critical: >= 100%
    """
    if bur >= 100:
        return {
            "status": "critical",
            "color": "red",
            "label": "Critical",
            "alert": "Budget exceeded! Immediate action required.",
            "bg_color": "bg-red-500/10",
            "border_color": "border-red-500/30",
            "text_color": "text-red-400"
        }
    elif bur >= 80:
        return {
            "status": "alert",
            "color": "yellow",
            "label": "Alert",
            "alert": f"Budget at {bur}% - approaching limit. Review spending.",
            "bg_color": "bg-yellow-500/10",
            "border_color": "border-yellow-500/30",
            "text_color": "text-yellow-400"
        }
    else:
        return {
            "status": "ok",
            "color": "green",
            "label": "OK",
            "alert": None,
            "bg_color": "bg-green-500/10",
            "border_color": "border-green-500/30",
            "text_color": "text-green-400"
        }


def compute_bbr(total_spent: float, days_elapsed: int) -> float:
    """
    Calculate Budget Burn Rate (BBR)
    
    Args:
        total_spent: Amount spent so far
        days_elapsed: Number of days elapsed since project start
    
    Returns:
        BBR as amount spent per day
    """
    if not days_elapsed or days_elapsed == 0:
        return 0.0
    return round(total_spent / days_elapsed, 2)


def compute_days_to_exhaust(remaining_budget: float, bbr: float) -> int:
    """
    Calculate days until budget is exhausted
    
    Args:
        remaining_budget: Budget remaining
        bbr: Budget burn rate per day
    
    Returns:
        Number of days until budget runs out
    """
    if not bbr or bbr == 0:
        return 999
    days = int(remaining_budget / bbr)
    return max(0, days)


def calculate_days_elapsed(start_date: date, end_date: date = None) -> int:
    """
    Calculate days elapsed from start date to now or end date
    
    Args:
        start_date: Project start date
        end_date: Optional end date (defaults to today)
    
    Returns:
        Number of days elapsed
    """
    today = date.today()
    target_date = end_date if end_date and end_date < today else today
    
    if start_date > target_date:
        return 0
    
    delta = target_date - start_date
    return delta.days


def calculate_remaining_days(end_date: date) -> int:
    """
    Calculate remaining days until end date
    
    Args:
        end_date: Project end date
    
    Returns:
        Number of days remaining
    """
    today = date.today()
    if end_date < today:
        return 0
    
    delta = end_date - today
    return delta.days


def aggregate_org_kpis(projects_data: list) -> Dict[str, Any]:
    """
    Aggregate KPI data across all projects in an organization
    
    Args:
        projects_data: List of project objects with their KPI data
    
    Returns:
        Aggregated organization KPIs
    """
    if not projects_data:
        return {
            "total_budget": 0,
            "total_spent": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "overdue_tasks": 0,
            "average_kar": 0,
            "average_bur": 0,
            "average_bbr": 0,
            "days_to_exhaust": 0
        }
    
    total_budget = sum(p.get('total_budget', 0) for p in projects_data)
    total_spent = sum(p.get('total_spent', 0) for p in projects_data)
    total_tasks = sum(p.get('total_tasks', 0) for p in projects_data)
    completed_tasks = sum(p.get('completed_tasks', 0) for p in projects_data)
    overdue_tasks = sum(p.get('overdue_tasks', 0) for p in projects_data)
    
    # Calculate weighted averages
    valid_kar = [p.get('kar', 0) for p in projects_data if p.get('kar', 0) > 0]
    average_kar = round(np.mean(valid_kar), 2) if valid_kar else 0
    
    valid_bur = [p.get('bur', 0) for p in projects_data if p.get('bur', 0) > 0]
    average_bur = round(np.mean(valid_bur), 2) if valid_bur else 0
    
    # Calculate overall BBR and days to exhaust
    days_elapsed = max([p.get('days_elapsed', 0) for p in projects_data] or [1])
    overall_bbr = total_spent / days_elapsed if days_elapsed > 0 else 0
    remaining_budget = total_budget - total_spent
    days_to_exhaust = compute_days_to_exhaust(remaining_budget, overall_bbr) if overall_bbr > 0 else 999
    
    return {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "average_kar": average_kar,
        "average_bur": average_bur,
        "average_bbr": round(overall_bbr, 2),
        "days_to_exhaust": days_to_exhaust,
        "completion_rate": round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
    }