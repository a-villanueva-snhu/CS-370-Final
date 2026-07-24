## This is main Database file for the project. 
# It contains all the functions to interact with the database. 
# It is used by the other files in the project to store and 
# retrieve data from the database.

import sqlite3
import gaiaml.src.utils.crud_helper as crud

## Setup the database connection and cursor
conn = sqlite3.connect('gaiaml.db')

cursor = conn.cursor()

## Create a test table 
crud.create_table(cursor, 'test_table', ['id INTEGER PRIMARY KEY', 'name TEXT', 'age INTEGER'])


## Commit the changes and close the connection
conn.commit()

## Test print the tables in the database
crud.print_tables(cursor)

## Close the connection
conn.close()
