"""Data analysis service"""
import logging
from typing import Dict, List, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class Analyzer:
    """Service for analyzing data"""
    
    def __init__(self):
        self.supported_types = [
            "statistical_summary",
            "trend_detection",
            "outlier_detection",
            "correlation_analysis"
        ]
    
    async def analyze(
        self,
        data: List[Dict],
        analysis_type: str,
        columns: List[str] = None
    ) -> Dict[str, Any]:
        """Perform data analysis"""
        
        logger.info(f"📊 Starting analysis: {analysis_type}")
        
        # Validate analysis type
        if analysis_type not in self.supported_types:
            raise ValueError(
                f"Unknown analysis type: {analysis_type}. "
                f"Supported types: {', '.join(self.supported_types)}"
            )
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Select columns if specified
        if columns:
            numeric_columns = [col for col in columns if col in df.columns]
        else:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        logger.info(f"Analyzing columns: {numeric_columns}")
        
        # Route to appropriate analysis
        if analysis_type == "statistical_summary":
            return await self._statistical_summary(df, numeric_columns)
        elif analysis_type == "trend_detection":
            return await self._trend_detection(df, numeric_columns)
        elif analysis_type == "outlier_detection":
            return await self._outlier_detection(df, numeric_columns)
        elif analysis_type == "correlation_analysis":
            return await self._correlation_analysis(df, numeric_columns)
    
    async def _statistical_summary(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Generate statistical summary"""
        try:
            results = {}
            
            for col in columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    results[col] = {
                        "mean": float(df[col].mean()),
                        "median": float(df[col].median()),
                        "std": float(df[col].std()),
                        "min": float(df[col].min()),
                        "max": float(df[col].max()),
                        "count": int(df[col].count())
                    }
            
            logger.info(f"✅ Statistical summary complete for {len(results)} columns")
            return {
                "type": "statistical_summary",
                "results": results,
                "rows_analyzed": len(df)
            }
        except Exception as e:
            logger.error(f"❌ Statistical summary failed: {e}")
            raise
    
    async def _trend_detection(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Detect trends in data"""
        try:
            trends = {}
            
            for col in columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    values = df[col].dropna().values
                    if len(values) > 1:
                        # Simple trend: compare first half vs second half
                        mid = len(values) // 2
                        first_half_mean = np.mean(values[:mid])
                        second_half_mean = np.mean(values[mid:])
                        
                        if second_half_mean > first_half_mean:
                            trend = "increasing"
                            trend_strength = ((second_half_mean - first_half_mean) / first_half_mean * 100) if first_half_mean != 0 else 0
                        elif second_half_mean < first_half_mean:
                            trend = "decreasing"
                            trend_strength = ((first_half_mean - second_half_mean) / first_half_mean * 100) if first_half_mean != 0 else 0
                        else:
                            trend = "stable"
                            trend_strength = 0
                        
                        trends[col] = {
                            "trend": trend,
                            "strength": float(trend_strength),
                            "first_half_avg": float(first_half_mean),
                            "second_half_avg": float(second_half_mean)
                        }
            
            logger.info(f"✅ Trend detection complete for {len(trends)} columns")
            return {
                "type": "trend_detection",
                "results": trends,
                "rows_analyzed": len(df)
            }
        except Exception as e:
            logger.error(f"❌ Trend detection failed: {e}")
            raise
    
    async def _outlier_detection(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Detect outliers in data"""
        try:
            outliers = {}
            
            for col in columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                    outlier_count = outlier_mask.sum()
                    outlier_indices = df[outlier_mask].index.tolist()
                    
                    outliers[col] = {
                        "count": int(outlier_count),
                        "percentage": float(outlier_count / len(df) * 100),
                        "lower_bound": float(lower_bound),
                        "upper_bound": float(upper_bound),
                        "outlier_indices": outlier_indices[:10]  # First 10
                    }
            
            logger.info(f"✅ Outlier detection complete for {len(outliers)} columns")
            return {
                "type": "outlier_detection",
                "results": outliers,
                "rows_analyzed": len(df)
            }
        except Exception as e:
            logger.error(f"❌ Outlier detection failed: {e}")
            raise
    
    async def _correlation_analysis(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Analyze correlations between columns"""
        try:
            # Get numeric data
            numeric_df = df[columns].select_dtypes(include=[np.number])
            
            if len(numeric_df.columns) < 2:
                return {
                    "type": "correlation_analysis",
                    "results": {},
                    "message": "Need at least 2 numeric columns for correlation analysis",
                    "rows_analyzed": len(df)
                }
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()
            
            # Find strong correlations
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    col_i = corr_matrix.columns[i]
                    col_j = corr_matrix.columns[j]
                    corr_value = corr_matrix.iloc[i, j]
                    
                    if abs(corr_value) > 0.5:  # Strong correlation threshold
                        strong_correlations.append({
                            "column_1": col_i,
                            "column_2": col_j,
                            "correlation": float(corr_value)
                        })
            
            logger.info(f"✅ Correlation analysis complete with {len(strong_correlations)} strong correlations")
            return {
                "type": "correlation_analysis",
                "results": {
                    "strong_correlations": strong_correlations,
                    "correlation_matrix": corr_matrix.to_dict()
                },
                "rows_analyzed": len(df)
            }
        except Exception as e:
            logger.error(f"❌ Correlation analysis failed: {e}")
            raise


# Global analyzer instance
analyzer = Analyzer()
