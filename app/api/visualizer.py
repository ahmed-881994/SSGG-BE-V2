import re
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_user_in_token
from app.schemas.visualizer_schema import VisualizerQuery, VisualizerQueryResponse


router = APIRouter(prefix="/visualizer", tags=["Visualizer"], dependencies=[Depends(get_user_in_token)])

from app.schemas.visualizer_schema import VisualizerQuery


router = APIRouter(prefix="/visualizer", tags=["Visualizer"], dependencies=[Depends(get_user_in_token)])

# Tables to exclude from visualization queries
EXCLUDED_TABLES = ["users", "roles", "permissions", "role_permissions", "route_patterns", "route_permissions", "public_routes","audit"]

def validate_select_query(query: str) -> None:
    """
    Validates that the query is a SELECT statement and doesn't access excluded tables.
    """
    # Remove comments and extra whitespace
    cleaned_query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    cleaned_query = re.sub(r'/\*.*?\*/', '', cleaned_query, flags=re.DOTALL)
    cleaned_query = ' '.join(cleaned_query.split()).strip().upper()
    
    # Check if query starts with SELECT
    if not cleaned_query.startswith('SELECT'):
        raise ValueError("Only SELECT queries are allowed")
    
    # Check for forbidden keywords that could modify data
    forbidden_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'REPLACE']
    for keyword in forbidden_keywords:
        if keyword in cleaned_query:
            raise ValueError(f"Query contains forbidden keyword: {keyword}")
    
    # Check for excluded tables
    query_lower = query.lower()
    for table in EXCLUDED_TABLES:
        # Match table name with word boundaries
        if re.search(rf'\b{table.lower()}\b', query_lower):
            raise ValueError(f"Access to table '{table}' is not allowed")

@router.post("", response_model= VisualizerQueryResponse)
def execute_visualization_query(body: VisualizerQuery, db: Session = Depends(get_db_session)):
    """
    Executes a visualization query and returns the results.
    """
    try:
        # Validate query
        validate_select_query(body.query)
        
        result = db.execute(text(body.query))
        columns = list(result.keys())
        rows = [dict(row._mapping) for row in result.fetchall()]
        
        data = {
            "columns": columns,
            "rows": rows
        }
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")
    
@router.get("/ddl")
def get_database_ddl(db: Session = Depends(get_db_session)):
    """
    Generates the entire DDL of the database.
    """
    try:
        # Increase GROUP_CONCAT max length to handle large tables
        db.execute(text("SET SESSION group_concat_max_len = 1000000"))
        # Create placeholders for excluded tables
        excluded_tables_str = ', '.join([f"'{table}'" for table in EXCLUDED_TABLES])
        
        ddl_query = f"""
        SELECT 
            CONCAT(
                'CREATE TABLE ', TABLE_SCHEMA, '.', TABLE_NAME, ' (\n',
                GROUP_CONCAT(
                    CONCAT('  ', COLUMN_NAME, ' ', COLUMN_TYPE,
                        CASE WHEN IS_NULLABLE = 'NO' THEN ' NOT NULL' ELSE '' END,
                        CASE WHEN COLUMN_DEFAULT IS NOT NULL THEN CONCAT(' DEFAULT ', COLUMN_DEFAULT) ELSE '' END
                    )
                    ORDER BY ORDINAL_POSITION
                    SEPARATOR ',\n'
                ),
                '\n);'
            ) as ddl
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'SSGG'
        AND TABLE_NAME NOT IN ({excluded_tables_str})
        GROUP BY TABLE_SCHEMA, TABLE_NAME
        ORDER BY TABLE_NAME
        """
        
        result = db.execute(text(ddl_query))
        ddl_statements = [row[0] for row in result.fetchall()]
        return {"ddl": "".join(ddl_statements).replace('\n', '')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating DDL: {str(e)}")