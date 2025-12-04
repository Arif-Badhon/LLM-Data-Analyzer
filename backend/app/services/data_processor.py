"""
Data Processing Service
Handles CSV and Excel file uploads and processing
"""
import logging
import pandas as pd
from pathlib import Path
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process uploaded data files (CSV, Excel)"""
    
    SUPPORTED_FORMATS = ["csv", "xlsx", "xls"]
    
    def __init__(self):
        self.temp_dir = Path("./uploads")
        self.temp_dir.mkdir(exist_ok=True)
    
    async def process_file(self, file: UploadFile) -> tuple:
        """
        Process uploaded file (CSV or Excel)
        
        Returns:
            tuple: (data_list, file_type)
        """
        try:
            # Validate file type
            file_ext = self._get_file_extension(file.filename)
            if file_ext not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            logger.info(f"🔄 Processing file: {file.filename}")
            
            # Save file temporarily
            file_path = self.temp_dir / file.filename
            contents = await file.read()
            
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Process based on file type
            if file_ext == "csv":
                data = self._process_csv(str(file_path))
            else:  # xlsx or xls
                data = self._process_excel(str(file_path))
            
            logger.info(f"✅ File processed: {len(data)} rows")
            return data, file_ext
            
        except ValueError as e:
            logger.error(f"❌ Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ File processing failed: {e}")
            raise ValueError(f"File processing failed: {e}")
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension"""
        return filename.split(".")[-1].lower()
    
    def _process_csv(self, file_path: str) -> list:
        """Process CSV file using pandas"""
        try:
            df = pd.read_csv(file_path)
            
            # Replace NaN values with None (becomes null in JSON)
            df = df.where(pd.notna(df), None)
        
            data = df.to_dict("records")
            logger.info(f"📄 CSV processed: {len(data)} rows, {len(df.columns)} columns")
            return data
        except Exception as e:
            logger.error(f"❌ CSV processing failed: {e}")
            raise ValueError(f"CSV processing error: {e}")

    def _process_excel(self, file_path: str) -> list:
        """Process Excel file using pandas"""
        try:
            df = pd.read_excel(file_path)
            
            # Replace NaN values with None (becomes null in JSON)
            df = df.where(pd.notna(df), None)
            
            data = df.to_dict("records")
            logger.info(f"📊 Excel processed: {len(data)} rows, {len(df.columns)} columns")
            return data
        except Exception as e:
            logger.error(f"❌ Excel processing failed: {e}")
            raise ValueError(f"Excel processing error: {e}")


