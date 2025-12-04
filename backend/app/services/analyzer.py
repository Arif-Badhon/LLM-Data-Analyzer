"""
Data analysis service - statistical, trend, correlation analysis
"""
from typing import List, Dict, Any
import logging
import statistics

try:
    import numpy as np
    import pandas as pd
    from scipy.stats import skew, kurtosis
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


class Analyzer:
    """Perform statistical and trend analysis on data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, data: List[Dict[str, Any]], analysis_type: str, columns: List[str] = None) -> Dict[str, Any]:
        """Dispatch to appropriate analysis method"""
        analysis_type = analysis_type.lower()
        
        if analysis_type == "statistical":
            return self.statistical_analysis(data, columns)
        elif analysis_type == "correlation":
            return self.correlation_analysis(data, columns)
        elif analysis_type == "trend":
            return self.trend_analysis(data, columns)
        elif analysis_type == "outliers":
            return self.outlier_analysis(data, columns)
        elif analysis_type == "distribution":
            return self.distribution_analysis(data, columns)
        elif analysis_type == "summary":
            return self.summary_analysis(data)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    def statistical_analysis(self, data: List[Dict[str, Any]], columns: List[str] = None) -> Dict[str, Any]:
        """Statistical analysis - mean, median, std, min, max"""
        try:
            numeric_cols = columns or self._get_numeric_columns(data)
            results = {
                "mean": {},
                "median": {},
                "std_dev": {},
                "min": {},
                "max": {},
                "count": len(data)
            }
            
            for col in numeric_cols:
                values = [row[col] for row in data if row[col] is not None]
                if values:
                    results["mean"][col] = round(statistics.mean(values), 2)
                    results["median"][col] = round(statistics.median(values), 2)
                    if len(values) > 1:
                        results["std_dev"][col] = round(statistics.stdev(values), 2)
                    results["min"][col] = round(min(values), 2)
                    results["max"][col] = round(max(values), 2)
            
            return results
        except Exception as e:
            self.logger.error(f"Statistical analysis failed: {e}")
            raise
    
    def correlation_analysis(self, data: List[Dict[str, Any]], columns: List[str] = None) -> Dict[str, Any]:
        """Correlation analysis between numeric columns"""
        try:
            if not HAS_SCIPY:
                raise RuntimeError("pandas and scipy required for correlation analysis")
            
            df = pd.DataFrame(data)
            numeric_cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
            
            corr_matrix = df[numeric_cols].corr().round(2)
            
            # Find significant correlations
            significant_pairs = []
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.5:  # Threshold
                        significant_pairs.append({
                            "col1": col1,
                            "col2": col2,
                            "correlation": float(corr_value)
                        })
            
            return {
                "matrix": corr_matrix.to_dict(),
                "significant_pairs": significant_pairs
            }
        except Exception as e:
            self.logger.error(f"Correlation analysis failed: {e}")
            raise
    
    def trend_analysis(self, data: List[Dict[str, Any]], columns: List[str] = None) -> Dict[str, Any]:
        """Trend analysis - increasing, decreasing, stable"""
        try:
            numeric_cols = columns or self._get_numeric_columns(data)
            trends = {}
            trend_strength = {}
            
            for col in numeric_cols:
                values = [row[col] for row in data if row[col] is not None]
                if len(values) > 2:
                    # Simple trend: compare first half vs second half
                    mid = len(values) // 2
                    first_half_avg = statistics.mean(values[:mid])
                    second_half_avg = statistics.mean(values[mid:])
                    
                    if second_half_avg > first_half_avg * 1.05:
                        trends[col] = "increasing"
                        strength = (second_half_avg - first_half_avg) / first_half_avg
                    elif second_half_avg < first_half_avg * 0.95:
                        trends[col] = "decreasing"
                        strength = (first_half_avg - second_half_avg) / first_half_avg
                    else:
                        trends[col] = "stable"
                        strength = 0.0
                    
                    trend_strength[col] = round(strength, 2)
            
            return {
                "trends": trends,
                "trend_strength": trend_strength
            }
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            raise
    
    def outlier_analysis(self, data: List[Dict[str, Any]], columns: List[str] = None) -> Dict[str, Any]:
        """Outlier detection using IQR method"""
        try:
            numeric_cols = columns or self._get_numeric_columns(data)
            outliers = {}
            total_outliers = 0
            
            for col in numeric_cols:
                values = sorted([row[col] for row in data if row[col] is not None])
                if len(values) > 4:
                    q1 = values[len(values) // 4]
                    q3 = values[3 * len(values) // 4]
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    col_outliers = [v for v in values if v < lower_bound or v > upper_bound]
                    outliers[col] = col_outliers
                    total_outliers += len(col_outliers)
            
            return {
                "outliers": outliers,
                "outlier_count": total_outliers,
                "outlier_percentage": round((total_outliers / len(data)) * 100, 2) if data else 0
            }
        except Exception as e:
            self.logger.error(f"Outlier analysis failed: {e}")
            raise
    
    def distribution_analysis(self, data: List[Dict[str, Any]], columns: List[str] = None) -> Dict[str, Any]:
        """Distribution analysis - skewness, kurtosis"""
        try:
            if not HAS_SCIPY:
                return {"error": "scipy required for distribution analysis"}
            
            numeric_cols = columns or self._get_numeric_columns(data)
            distributions = {}
            skewness = {}
            kurt = {}
            
            for col in numeric_cols:
                values = [row[col] for row in data if row[col] is not None]
                if len(values) > 2:
                    distributions[col] = {
                        "min": round(min(values), 2),
                        "max": round(max(values), 2),
                        "range": round(max(values) - min(values), 2)
                    }
                    skewness[col] = round(float(skew(values)), 2)
                    kurt[col] = round(float(kurtosis(values)), 2)
            
            return {
                "distributions": distributions,
                "skewness": skewness,
                "kurtosis": kurt
            }
        except Exception as e:
            self.logger.error(f"Distribution analysis failed: {e}")
            raise
    
    def summary_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summary of data"""
        try:
            if not data:
                return {"error": "No data"}
            
            cols = list(data.keys())
            return {
                "total_rows": len(data),
                "total_columns": len(cols),
                "columns": cols,
                "data_types": self._infer_types(data)
            }
        except Exception as e:
            self.logger.error(f"Summary analysis failed: {e}")
            raise
    
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
    
    @staticmethod
    def _infer_types(data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Infer column data types"""
        types = {}
        if not data:
            return types
        
        for key in data.keys():
            try:
                for row in data:
                    if row[key] is not None:
                        float(row[key])
                types[key] = "numeric"
            except (ValueError, TypeError):
                types[key] = "string"
        
        return types
    
    def generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary"""
        return f"Analysis completed with {len(results)} metrics."
