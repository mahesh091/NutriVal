from flask import g
import sqlite3

def connect_db(): #folder path
    sql = sqlite3.connect('C:/Users/mahesh/Desktop/foodtracker/food_log.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db