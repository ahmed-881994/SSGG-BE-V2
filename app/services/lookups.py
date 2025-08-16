"""
Lookups services for retrieving lookup data
"""
from typing import List, Dict, Any
from app.core.config import logger
from app.core.database_connection_pool import db_pool


def get_lookups() -> List[Dict[str, Any]]:
    """
    Get all lookup tables and their values
    
    Returns:
        List of lookup tables with their values
    """
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.callproc("GetLookups", [])
            records = cursor.fetchall()
            
            # Group lookups by table
            lookups = {}
            for record in records:
                table_name = record.get('table_name', record[0])
                table_desc = record.get('table_description', record[1]) 
                lookup_id = record.get('lookup_id', record[2])
                lookup_value = record.get('lookup_value', record[3])
                
                if table_name not in lookups:
                    lookups[table_name] = {
                        'table_name': table_name,
                        'table_description': table_desc,
                        'values': []
                    }
                
                lookups[table_name]['values'].append({
                    'id': lookup_id,
                    'value': lookup_value
                })
            
            return list(lookups.values())
            
    finally:
        db_pool.return_connection(conn)
