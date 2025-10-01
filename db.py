import sqlite3

def conectar():
    """Establece conexión con la base de datos"""
    return sqlite3.connect('agenda.db')

def crear_base_datos():
    """Crea las tablas necesarias e inserta datos iniciales"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Crear tabla paises
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            codigo TEXT NOT NULL
        )
    ''')
    
    # Crear tabla contactos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo INTEGER NOT NULL,
            ci TEXT,
            nit TEXT,
            nombre TEXT NOT NULL,
            fecha_nac TEXT,
            telefono TEXT,
            direccion TEXT,
            pais_id INTEGER,
            FOREIGN KEY (pais_id) REFERENCES paises(id)
        )
    ''')
    
    # Verificar si ya existen países
    cursor.execute('SELECT COUNT(*) FROM paises')
    if cursor.fetchone()[0] == 0:
        # Insertar países iniciales
        paises_iniciales = [
            ('Bolivia', '+591'),
            ('Argentina', '+54'),
            ('Chile', '+56'),
            ('Perú', '+51'),
            ('Brasil', '+55')
        ]
        cursor.executemany('INSERT INTO paises (nombre, codigo) VALUES (?, ?)', paises_iniciales)
    
    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

# Crear la base de datos al importar el módulo
crear_base_datos()