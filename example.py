import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

cursor.execute("select * from events")
rows = cursor.fetchall()
print(rows)

new_rows = [('The kite', 'Tokyo', '1965-08-15'),
            ('Lock Rock', 'Sanghai', '1973-03-01'), ('Coldplay', 'Paris', '2025-09-10')]

cursor.executemany("insert into events values(?, ?, ?)", new_rows)
connection.commit()