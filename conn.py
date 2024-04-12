import logging
import sqlite3
from sqlite3 import Error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    try:
        connection = sqlite3.connect('results.db')
        logger.info("Connected to SQLite database")
        return connection
    except Error as e:
        logger.error("Error while connecting to SQLite: %s", e)
        return None

def create_table_if_not_exists(connection, table_name, columns):
    if connection:
        cursor = connection.cursor()
        create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})"
        try:
            cursor.execute(create_table_query)
            connection.commit()
            logger.info("Table %s created successfully", table_name)
        except Error as e:
            logger.error("Error creating table %s: %s", table_name, e)

def save_result_to_sql(result, School, Grade, term, exam_type):
    connection = get_connection()
    if connection is not None:
        try:
            table_name = f"{School}_{Grade}_{term}_{exam_type}".replace(" ", "_").lower()
            result.columns = ["".join(e for e in col if e.isalnum() or e=='_') for col in result.columns]
            column_types = []
            for column in result.columns:
                if result[column].dtype == 'int64':
                    column_types.append(f'`{column}` INTEGER')
                elif result[column].dtype == 'float64':
                    column_types.append(f'`{column}` REAL')
                else:
                    column_types.append(f'`{column}` TEXT')
            columns = ', '.join(column_types)
            create_table_if_not_exists(connection, table_name, columns)
            cursor = connection.cursor()
            placeholders = ', '.join(['?' for _ in result.columns])
            insert_query = f"INSERT INTO `{table_name}` ({', '.join(result.columns)}) VALUES ({placeholders})"
            data = [tuple(row) for row in result.values]
            cursor.executemany(insert_query, data)
            connection.commit()
            logger.info("Data saved to table %s", table_name)
        except Exception as e:
            logger.error("Error while saving data to SQLite: %s", e)
        finally:
            connection.close()
            logger.info("Connection closed")
    else:
        logger.error("Failed to save data to SQLite. No connection to SQLite database.")
