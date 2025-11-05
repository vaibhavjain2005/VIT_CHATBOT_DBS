from typing import List, Dict, Optional
import numpy as np
from datetime import datetime


def calculate_trend_metrics(historical_data: List[Dict]) -> Dict:
    """Calculate various trend metrics from historical data."""
    if not historical_data or len(historical_data) < 2:
        return {
            "trend_direction": "stable",
            "confidence": 0.5,
            "avg_yearly_change": 0.0,
            "volatility": 0.0
        }
    
    # Extract year and rank data
    years = []
    ranks = []
    for data in historical_data:
        years.append(data.get("year"))
        ranks.append(data.get("avg_rank", 0))
    
    # Calculate year-over-year changes
    yoy_changes = []
    for i in range(1, len(ranks)):
        if ranks[i-1] != 0:
            change = ((ranks[i] - ranks[i-1]) / ranks[i-1]) * 100
            yoy_changes.append(change)
    
    if not yoy_changes:
        return {
            "trend_direction": "stable",
            "confidence": 0.5,
            "avg_yearly_change": 0.0,
            "volatility": 0.0
        }
    
    # Calculate metrics
    avg_change = np.mean(yoy_changes)
    std_dev = np.std(yoy_changes) if len(yoy_changes) > 1 else 0
    
    # Determine trend direction
    if abs(avg_change) < 2:
        trend = "stable"
    else:
        trend = "increasing" if avg_change > 0 else "decreasing"
    
    # Calculate confidence based on consistency and data points
    consistency = 1 / (1 + (std_dev / 10))  # Normalize volatility
    data_points_factor = min(len(historical_data) / 5, 1)  # Max boost from 5 years
    confidence = (consistency * 0.7 + data_points_factor * 0.3)
    confidence = round(min(max(confidence, 0.3), 0.9), 2)  # Clamp between 0.3 and 0.9
    
    return {
        "trend_direction": trend,
        "confidence": confidence,
        "avg_yearly_change": round(avg_change, 2),
        "volatility": round(std_dev, 2)
    }


def predict_next_year(historical_data: List[Dict], confidence_threshold: float = 0.6) -> Optional[Dict]:
    """Predict next year's rank range based on historical trends."""
    if not historical_data or len(historical_data) < 2:
        return None
    
    metrics = calculate_trend_metrics(historical_data)
    if metrics["confidence"] < confidence_threshold:
        return None
    
    latest_data = historical_data[-1]
    next_year = latest_data["year"] + 1
    avg_change = metrics["avg_yearly_change"] / 100  # Convert percentage to decimal
    
    # Calculate predicted ranks
    latest_avg = latest_data.get("avg_rank", 0)
    if latest_avg == 0:
        return None
    
    predicted_avg = latest_avg * (1 + avg_change)
    rank_range = latest_data.get("max_rank", 0) - latest_data.get("min_rank", 0)
    
    if rank_range == 0:
        rank_range = latest_avg * 0.2  # Default to 20% of average if no range
    
    return {
        "year": next_year,
        "predicted_min_rank": max(1, round(predicted_avg - (rank_range/2))),
        "predicted_max_rank": round(predicted_avg + (rank_range/2)),
        "predicted_avg_rank": round(predicted_avg),
        "confidence": metrics["confidence"],
        "trend_direction": metrics["trend_direction"],
        "avg_yearly_change": metrics["avg_yearly_change"]
    }


def generate_trend_summary(historical_data: List[Dict], prediction: Optional[Dict] = None) -> str:
    """Generate a human-readable summary of the trends and prediction."""
    if not historical_data:
        return "No historical data available for trend analysis."
    
    metrics = calculate_trend_metrics(historical_data)
    years_of_data = len(historical_data)
    
    # Start with historical trend
    if years_of_data == 1:
        summary = "Only one year of historical data available. "
    else:
        summary = f"Based on {years_of_data} years of historical data, "
        if metrics["trend_direction"] == "stable":
            summary += "cutoff ranks have remained relatively stable "
        else:
            summary += f"cutoff ranks have shown a {metrics['trend_direction']} trend "
        summary += f"with an average yearly change of {abs(metrics['avg_yearly_change'])}%. "
    
    # Add prediction if available
    if prediction and prediction["confidence"] >= 0.6:
        next_year = prediction["year"]
        summary += f"\nFor {next_year}, "
        if prediction["trend_direction"] == "stable":
            summary += "ranks are expected to remain stable "
        else:
            summary += f"ranks are expected to continue {prediction['trend_direction']} "
        summary += f"with predicted ranks between {prediction['predicted_min_rank']} "
        summary += f"and {prediction['predicted_max_rank']}. "
        summary += f"(Confidence: {int(prediction['confidence']*100)}%)"
    
    return summary