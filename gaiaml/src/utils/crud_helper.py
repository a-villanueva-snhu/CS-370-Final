## A helper utility to handle CRUD operations for SQLite database.


#  Creates a new table in the database
#  Parameters:
#  - cursor: SQLite cursor object
#  - table_name: Name of the table to create
#  - columns: List of column definitions (e.g., ['id INTEGER PRIMARY KEY',
#             'name TEXT', 'age INTEGER'])
def create_table(cursor, table_name, columns):
    """
    Create a table in the database.

    :param cursor: SQLite cursor object
    :param table_name: Name of the table to create
    :param columns: List of column definitions (e.g., ['id INTEGER PRIMARY KEY', 'name TEXT'])
    """
    columns_str = ', '.join(columns)
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
    cursor.execute(query)

# Prints all tables in the database, TEST only, not used in production code
# Parameters:
# - cursor: SQLite cursor object
def print_tables(cursor):
    """
    Print all tables in the database.

    :param cursor: SQLite cursor object
    """
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(tables)