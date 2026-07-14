import sqlite3

def connection():
    connect = sqlite3.connect('./database.db')
    cursor=connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY ,title TEXT,author TEXT,year INTEGER,category TEXT)""")
    connect.commit()
    connect.close()


def insert(title, author, year, category):
    connect = sqlite3.connect('./database.db')
    cursor = connect.cursor()
    cursor.execute("INSERT INTO books VALUES (NULL,?,?,?,?)", (title, author, year, category))
    connect.commit()
    connect.close()


def view_all():
    connect = sqlite3.connect('./database.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    connect.close()
    return rows



def delete(id):
    connect = sqlite3.connect('./database.db')
    cursor = connect.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (id,))
    connect.commit()
    connect.close()



def update(id, title, author, year, category):
    connect = sqlite3.connect('./database.db')
    cursor = connect.cursor()
    cursor.execute("UPDATE books SET title=? , author=?,year=? , category=? WHERE id = ?",
                   (title, author, year, category, id))
    connect.commit()
    connect.close()



def search(title):
    connect = sqlite3.connect('./database.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM books WHERE title LIKE ?",(f"%{title}%",))
    rows = cursor.fetchall()
    connect.close()
    return rows

connection()









