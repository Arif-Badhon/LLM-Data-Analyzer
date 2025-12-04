"""
ML suggestions - anomaly detection and insights
"""
from typing import List, Dict, Any
import logging
import statistics


class MLSuggester:
    """Generate ML-based suggestions from data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, data: List[Dict[str, Any]], context: str = None) -> List[Dict[str, Any]]:
        """Generate ML suggestions"""
        suggestions = []
        
        if not data:
            return suggestions
        
        # Detect missing values
        suggestions.extend(self._check_missing_values(data))
        
        # Detect outliers
        suggestions.extend(self._detect_outliers(data))
        
        # Detect imbalances
        suggestions.extend(self._detect_imbalances(data))
        
        # Detect data quality issues
        suggestions.extend(self._detect_quality_issues(data))
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return suggestions[:10]  # Top 10 suggestions
    
    def _check_missing_values(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for missing values"""
        suggestions = []
        
        for col in data.keys():
            missing_count = sum(1 for row in data if row[col] is None or row[col] == "")
            if missing_count > 0:
                percentage = (missing_count / len(data)) * 100
                
                if percentage > 50:
                    suggestions.append({
                        "title": f"High Missing Values in {col}",
                        "description": f"{percentage:.1f}% of {col} is missing. Consider data imputation or removal.",
                        "confidence": min(0.95, percentage / 100),
                        "action": "impute_or_remove",
                        "category": "data_quality"
                    })
                elif percentage > 10:
                    suggestions.append({
                        "title": f"Missing Values in {col}",
                        "description": f"{percentage:.1f}% of {col} is missing. Consider handling these values.",
                        "confidence": min(0.8, percentage / 100),
                        "action": "handle_missing",
                        "category": "data_quality"
                    })
        
        return suggestions
    
    def _detect_outliers(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect outliers"""
        suggestions = []
        numeric_cols = self._get_numeric_columns(data)
        
        for col in numeric_cols:
            values = [row[col] for row in data if row[col] is not None]
            if len(values) > 4:
                try:
                    q1 = sorted(values)[len(values) // 4]
                    q3 = sorted(values)[3 * len(values) // 4]
                    iqr = q3 - q1
                    outliers = [v for v in values if v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr]
                    
                    if outliers:
                        outlier_percentage = (len(outliers) / len(values)) * 100
                        if outlier_percentage > 5:
                            suggestions.append({
                                "title": f"Outliers Detected in {col}",
                                "description": f"{len(outliers)} outlier(s) ({outlier_percentage:.1f}%) found. Review and handle appropriately.",
                                "confidence": min(0.85, outlier_percentage / 100),
                                "action": "review_outliers",
                                "category": "anomaly"
                            })
                except:
                    pass
        
        return suggestions
    
    def _detect_imbalances(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect data imbalances"""
        suggestions = []
        
        for col in data.keys():
            values = [row[col] for row in data if row[col] is not None]
            if len(set(values)) < len(values) * 0.1:  # Few unique values
                from collections import Counter
                counts = Counter(values)
                most_common_count = counts.most_common(1)
                imbalance_ratio = most_common_count / len(values)
                
                if imbalance_ratio > 0.8:
                    suggestions.append({
                        "title": f"Class Imbalance in {col}",
                        "description": f"One value appears {imbalance_ratio*100:.1f}% of the time. Data is highly imbalanced.",
                        "confidence": min(0.9, imbalance_ratio),
                        "action": "rebalance_data",
                        "category": "pattern"
                    })
        
        return suggestions
    
    def _detect_quality_issues(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect data quality issues"""
        suggestions = []
        
        # Check for duplicates
        if len(data) != len(set(str(row) for row in data)):
            duplicate_count = len(data) - len(set(str(row) for row in data))
            suggestions.append({
                "title": "Duplicate Records Found",
                "description": f"{duplicate_count} duplicate row(s) detected. Consider deduplication.",
                "confidence": 0.9,
                "action": "deduplicate",
                "category": "data_quality"
            })
        
        return suggestions
    
    @staticmethod
    def _get_numeric_columns(data: List[Dict[str, Any]]) -> List[str]:
        """Get numeric columns"""
        if not data:
            return []
        
        numeric = []
        for key in data.keys():
            try:
                for row in data:
                    if row[key] is not None:
                        float(row[key])
                numeric.append(key)
            except (ValueError, TypeError):
                pass
        return numeric
