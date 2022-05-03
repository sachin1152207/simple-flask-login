import sqlite3

conn = sqlite3.connect('account.db')
cursor = conn.cursor()

cursor.execute("CREATE TABLE 'Account'("fullName" TEXT)") 