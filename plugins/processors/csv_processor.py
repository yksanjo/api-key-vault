"""
CSV processor plugin.
"""

import csv
import io
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class CSVProcessorConfig(BasePluginConfig):
    """Configuration for CSV processor."""
    delimiter: str = Field(default=",", description="CSV delimiter")
    quotechar: str = Field(default='"', description="Quote character")
    encoding: str = Field(default="utf-8", description="File encoding")


class CSVProcessor(BasePlugin):
    """
    Process CSV files: read, write, transform, filter, and analyze.
    """
    
    name = "csv_processor"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Process CSV files with various operations"
    tags = ["data-processing", "csv", "data"]
    config_class = CSVProcessorConfig
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Process CSV data.
        
        Args:
            operation: Operation to perform (read, write, filter, transform, aggregate)
            data: CSV data (string or list of dicts)
            file_path: Path to CSV file
            **kwargs: Additional operation-specific arguments
            
        Returns:
            Dictionary with processing result
        """
        operation = kwargs.get("operation", "read")
        
        if operation == "read":
            return self._read_csv(kwargs)
        elif operation == "write":
            return self._write_csv(kwargs)
        elif operation == "filter":
            return self._filter_csv(kwargs)
        elif operation == "transform":
            return self._transform_csv(kwargs)
        elif operation == "aggregate":
            return self._aggregate_csv(kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _read_csv(self, kwargs: Dict) -> Dict[str, Any]:
        """Read CSV data."""
        data = kwargs.get("data")
        file_path = kwargs.get("file_path")
        limit = kwargs.get("limit")
        
        if file_path:
            with open(file_path, 'r', encoding=self.config.encoding) as f:
                reader = csv.DictReader(f, delimiter=self.config.delimiter)
                rows = list(reader)
        elif data:
            if isinstance(data, str):
                reader = csv.DictReader(
                    io.StringIO(data), 
                    delimiter=self.config.delimiter
                )
                rows = list(reader)
            else:
                rows = data
        else:
            return {"error": "No data or file_path provided"}
        
        if limit:
            rows = rows[:limit]
        
        return {
            "data": rows,
            "count": len(rows),
            "columns": list(rows[0].keys()) if rows else []
        }
    
    def _write_csv(self, kwargs: Dict) -> Dict[str, Any]:
        """Write CSV data."""
        data = kwargs.get("data", [])
        file_path = kwargs.get("file_path")
        columns = kwargs.get("columns")
        
        if not data:
            return {"error": "No data provided"}
        
        output = io.StringIO()
        if columns:
            writer = csv.DictWriter(
                output, 
                fieldnames=columns,
                delimiter=self.config.delimiter
            )
            writer.writeheader()
        else:
            writer = csv.DictWriter(
                output, 
                fieldnames=data[0].keys(),
                delimiter=self.config.delimiter
            )
            writer.writeheader()
        
        writer.writerows(data)
        csv_string = output.getvalue()
        
        if file_path:
            with open(file_path, 'w', encoding=self.config.encoding) as f:
                f.write(csv_string)
            return {"success": True, "file": file_path}
        
        return {"data": csv_string, "success": True}
    
    def _filter_csv(self, kwargs: Dict) -> Dict[str, Any]:
        """Filter CSV data based on conditions."""
        data = kwargs.get("data", [])
        column = kwargs.get("column")
        value = kwargs.get("value")
        operator = kwargs.get("operator", "equals")
        
        if not data:
            return {"error": "No data provided"}
        
        filtered = []
        for row in data:
            row_value = row.get(column)
            
            if operator == "equals" and row_value == value:
                filtered.append(row)
            elif operator == "contains" and value in str(row_value):
                filtered.append(row)
            elif operator == "startswith" and str(row_value).startswith(value):
                filtered.append(row)
            elif operator == "endswith" and str(row_value).endswith(value):
                filtered.append(row)
            elif operator == "greater" and float(row_value or 0) > float(value):
                filtered.append(row)
            elif operator == "less" and float(row_value or 0) < float(value):
                filtered.append(row)
        
        return {
            "data": filtered,
            "count": len(filtered),
            "original_count": len(data)
        }
    
    def _transform_csv(self, kwargs: Dict) -> Dict[str, Any]:
        """Transform CSV data."""
        data = kwargs.get("data", [])
        transformations = kwargs.get("transformations", {})
        
        if not data:
            return {"error": "No data provided"}
        
        transformed = []
        for row in data:
            new_row = row.copy()
            for column, transformation in transformations.items():
                if transformation == "uppercase":
                    new_row[column] = row.get(column, "").upper()
                elif transformation == "lowercase":
                    new_row[column] = row.get(column, "").lower()
                elif transformation == "titlecase":
                    new_row[column] = row.get(column, "").title()
                elif transformation == "strip":
                    new_row[column] = row.get(column, "").strip()
                elif transformation == "int":
                    try:
                        new_row[column] = int(row.get(column, 0))
                    except (ValueError, TypeError):
                        new_row[column] = 0
                elif transformation == "float":
                    try:
                        new_row[column] = float(row.get(column, 0))
                    except (ValueError, TypeError):
                        new_row[column] = 0.0
            transformed.append(new_row)
        
        return {
            "data": transformed,
            "count": len(transformed)
        }
    
    def _aggregate_csv(self, kwargs: Dict) -> Dict[str, Any]:
        """Aggregate CSV data."""
        data = kwargs.get("data", [])
        group_by = kwargs.get("group_by")
        aggregates = kwargs.get("aggregates", {})
        
        if not data:
            return {"error": "No data provided"}
        
        if not group_by:
            # Calculate overall aggregates
            result = {}
            for column, operation in aggregates.items():
                values = [float(row.get(column, 0)) for row in data]
                if operation == "sum":
                    result[column] = sum(values)
                elif operation == "avg":
                    result[column] = sum(values) / len(values) if values else 0
                elif operation == "min":
                    result[column] = min(values) if values else None
                elif operation == "max":
                    result[column] = max(values) if values else None
                elif operation == "count":
                    result[column] = len(values)
            return {"aggregates": result}
        
        # Group by column
        groups: Dict[str, List[Dict]] = {}
        for row in data:
            key = row.get(group_by, "unknown")
            if key not in groups:
                groups[key] = []
            groups[key].append(row)
        
        result = {}
        for group_key, group_data in groups.items():
            group_result = {"count": len(group_data)}
            for column, operation in aggregates.items():
                values = [float(row.get(column, 0)) for row in group_data]
                if operation == "sum":
                    group_result[f"{column}_sum"] = sum(values)
                elif operation == "avg":
                    group_result[f"{column}_avg"] = sum(values) / len(values) if values else 0
                elif operation == "min":
                    group_result[f"{column}_min"] = min(values) if values else None
                elif operation == "max":
                    group_result[f"{column}_max"] = max(values) if values else None
            result[group_key] = group_result
        
        return {"groups": result}
