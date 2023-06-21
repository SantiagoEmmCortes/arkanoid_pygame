import sqlite3

#Conexion y creacion de la base de datos, para ejecutar por unica vez
with sqlite3.connect("Pygame/arkanoid_db.db") as conexion:
    try:
        conexion.execute('''
          create table score (
          id integer primary key autoincrement,
          nombre text,
          puntaje integer)
          ''')
    except sqlite3.OperationalError:
        print("Hubo un error al crear la tabla de score.")
    