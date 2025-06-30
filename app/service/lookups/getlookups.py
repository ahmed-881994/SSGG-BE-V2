from app.exceptions.exceptions import EntityDoesNotExistError
from app.util.database import connect


def get_lookups():
    conn = connect()
    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            # cursor.execute(f"SELECT * FROM {os.environ.get('database')}.lookups")
            cursor.execute(f"SELECT * FROM lookups")
            tables = cursor.fetchall()
            if not tables:
                raise EntityDoesNotExistError(
                    message="No lookup tables found", name=None)

            data = []
            for table in tables:
                record = {}
                table_name = table.get("table_name")

                if not table_name:
                    continue  # Skip if table_name is None or empty

                record['TableName'] = table_name
                record['Description'] = table.get("description")
                # cursor.execute(f"SELECT {table_name[:-1] + '_id'}, {table_name[:-1]+'_name_ar'}, {table_name[:-1]+'_name_en'} FROM {os.environ.get('database')}.{table_name}")
                cursor.execute(
                    f"SELECT {table_name[:-1] + '_id'}, {table_name[:-1]+'_name_ar'}, {table_name[:-1]+'_name_en'} FROM {table_name}")
                records = cursor.fetchall()
                # print(records)
                if records:
                    record['LookupValues'] = []
                    for record_ in records:
                        record_entry = {
                            "LookupID": record_.get(table_name[:-1]+"_id"),
                            "AR": record_.get(table_name[:-1] + "_name_ar"),
                            "EN": record_.get(table_name[:-1] + "_name_en"),
                        }
                        record['LookupValues'].append(record_entry)
                data.append(record)

            return data
