"""
Data file processing - CSV and Excel support
"""
import csv
import io
from typing import List, Dict, Any
from fastapi import UploadFile
import logging

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


class DataProcessor:
    """Process uploaded data files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_file_size = 10 * 1024 * 1024  # 10 MB
    
    async def process_file(self, file: UploadFile) -> tuple[List[Dict[str, Any]], str]:
        """Process uploaded file - returns (data, file_type)"""
        content = await file.read()
        
        if len(content) > self.max_file_size:
            raise ValueError(f"File too large. Max: {self.max_file_size / 1024 / 1024:.1f} MB")
        
        if file.filename.endswith('.csv'):
            return self._process_csv(content), 'csv'
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            return self._process_excel(content), 'excel'
        else:
            raise ValueError(f"Unsupported file format: {file.filename}")
    
    def _process_csv(self, content: bytes) -> List[Dict[str, Any]]:
        """Process CSV file"""
        try:
            text_content = content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(text_content))
            data = []
            for row in reader:
                # Convert numeric strings to numbers
                processed_row = {}
                for key, value in row.items():
                    processed_row[key] = self._try_convert_to_number(value)
                data.append(processed_row)
            
            if not data:
                raise ValueError("CSV file is empty")
            
            self.logger.info(f"✅ Processed CSV: {len(data)} rows")
            return data
        except Exception as e:
            self.logger.error(f"❌ CSV processing failed: {e}")
            raise
    
    def _process_excel(self, content: bytes) -> List[Dict[str, Any]]:
        """Process Excel file"""
        try:
            if not HAS_OPENPYXL:
                raise RuntimeError("openpyxl not installed. Install with: uv add openpyxl")
            
            workbook = openpyxl.load_workbook(io.BytesIO(content))
            sheet = workbook.active
            
            # Get headers
            headers = [cell.value for cell in sheet]
            
            # Get data
            data = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if any(cell is not None for cell in row):
                    row_dict = {}
                    for header, value in zip(headers, row):
                        row_dict[header] = value
                    data.append(row_dict)
            
            if not data:
                raise ValueError("Excel file is empty")
            
            self.logger.info(f"✅ Processed Excel: {len(data)} rows")
            return data
        except Exception as e:
            self.logger.error(f"❌ Excel processing failed: {e}")
            raise
    
    @staticmethod
    def _try_convert_to_number(value: str) -> Any:
        """Try converting string to int or float"""
        if value is None or value == "":
            return None
        
        try:
            if "." in str(value):
                return float(value)
            else:
                return int(value)
        except (ValueError, TypeError):
            return value
    
    @staticmethod
    def get_numeric_columns(data: List[Dict[str, Any]]) -> List[str]:
        """Get columns that contain numeric data"""
        if not data:
            return []
        
        numeric_cols = []
        for key in data.keys():
            try:
                for row in data:
                    if row[key] is not None:
                        float(row[key])
                numeric_cols.append(key)
            except (ValueError, TypeError):
                pass
        
        return numeric_cols
