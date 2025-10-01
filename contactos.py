from db import conectar

def mostrar_paises():
    """Muestra la lista de países disponibles"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, codigo FROM paises')
    paises = cursor.fetchall()
    conn.close()
    
    print("\n=== PAÍSES DISPONIBLES ===")
    for pais in paises:
        print(f"{pais[0]}. {pais[1]} ({pais[2]})")
    print()
    return paises

def verificar_usuario_en_agenda(ci_nit):
    """Verifica si el CI o NIT está registrado en la agenda"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Buscar por CI
    cursor.execute('SELECT * FROM contactos WHERE ci = ?', (ci_nit,))
    resultado = cursor.fetchone()
    
    # Si no encuentra por CI, buscar por NIT
    if not resultado:
        cursor.execute('SELECT * FROM contactos WHERE nit = ?', (ci_nit,))
        resultado = cursor.fetchone()
    
    conn.close()
    return resultado is not None

def agregar_contacto():
    """Agrega un nuevo contacto (establecimiento o persona)"""
    print("\n=== AGREGAR CONTACTO ===")
    print("1. Establecimiento")
    print("2. Persona")
    
    tipo = input("Seleccione tipo de contacto (1-2): ")
    
    if tipo not in ['1', '2']:
        print("Opción inválida.")
        return
    
    tipo = int(tipo)
    conn = conectar()
    cursor = conn.cursor()
    
    if tipo == 1:  # Establecimiento
        nit = input("Ingrese NIT: ")
        nombre = input("Ingrese nombre del establecimiento: ")
        telefono = input("Ingrese teléfono: ")
        
        # Dirección con mínimo 2 calles, máximo 3
        calles = []
        print("Ingrese dirección (mínimo 2 calles, máximo 3):")
        for i in range(3):
            calle = input(f"Calle {i+1}: ").strip()
            if calle:
                calles.append(calle)
            elif i < 2:
                print("Debe ingresar al menos 2 calles.")
                conn.close()
                return
            else:
                break
        
        direccion = ", ".join(calles)
        
        mostrar_paises()
        pais_id = input("Seleccione ID del país: ")
        
        cursor.execute('''
            INSERT INTO contactos (tipo, nit, nombre, telefono, direccion, pais_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tipo, nit, nombre, telefono, direccion, pais_id))
        
    else:  # Persona
        ci = input("Ingrese CI: ")
        nombre = input("Ingrese nombre: ")
        fecha_nac = input("Ingrese fecha de nacimiento (DD/MM/AAAA): ")
        direccion = input("Ingrese dirección: ")
        
        mostrar_paises()
        pais_id = input("Seleccione ID del país: ")
        
        cursor.execute('''
            INSERT INTO contactos (tipo, ci, nombre, fecha_nac, direccion, pais_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tipo, ci, nombre, fecha_nac, direccion, pais_id))
    
    conn.commit()
    conn.close()
    print("\n✓ Contacto agregado exitosamente.")

def buscar_contacto():
    """Busca contactos con sistema de filtros múltiples"""
    print("\n=== BUSCAR CONTACTO ===")
    ci_nit = input("Ingrese su CI o NIT para acceder: ")
    
    # Verificar si el usuario está en la agenda
    if not verificar_usuario_en_agenda(ci_nit):
        print("\n✗ No está registrado en la agenda.")
        print("Será redirigido a agregar su contacto primero...\n")
        agregar_contacto()
        return
    
    print("\n✓ Acceso concedido.")
    print("\n=== BÚSQUEDA CON FILTROS ===")
    print("Ingrese los datos que desea filtrar (deje en blanco para omitir)")
    
    # Recoger filtros del usuario
    filtro_ci = input("CI (dejar en blanco para omitir): ").strip()
    filtro_nit = input("NIT (dejar en blanco para omitir): ").strip()
    filtro_nombre = input("Nombre (dejar en blanco para omitir): ").strip()
    filtro_direccion = input("Dirección (dejar en blanco para omitir): ").strip()
    filtro_fecha_nac = input("Fecha de nacimiento DD/MM/AAAA (dejar en blanco para omitir): ").strip()
    
    print("\nPaíses disponibles:")
    mostrar_paises()
    filtro_pais = input("ID del país (dejar en blanco para omitir): ").strip()
    
    # Construir la consulta SQL dinámicamente
    conn = conectar()
    cursor = conn.cursor()
    
    query = '''
        SELECT c.*, p.nombre, p.codigo 
        FROM contactos c 
        LEFT JOIN paises p ON c.pais_id = p.id 
        WHERE 1=1
    '''
    params = []
    
    if filtro_ci:
        query += ' AND c.ci LIKE ?'
        params.append(f'%{filtro_ci}%')
    
    if filtro_nit:
        query += ' AND c.nit LIKE ?'
        params.append(f'%{filtro_nit}%')
    
    if filtro_nombre:
        query += ' AND c.nombre LIKE ?'
        params.append(f'%{filtro_nombre}%')
    
    if filtro_direccion:
        query += ' AND c.direccion LIKE ?'
        params.append(f'%{filtro_direccion}%')
    
    if filtro_fecha_nac:
        query += ' AND c.fecha_nac = ?'
        params.append(filtro_fecha_nac)
    
    if filtro_pais:
        query += ' AND c.pais_id = ?'
        params.append(filtro_pais)
    
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()
    
    if resultados:
        print(f"\n=== RESULTADOS ENCONTRADOS: {len(resultados)} ===")
        for contacto in resultados:
            print(f"\n{'='*50}")
            print(f"ID: {contacto[0]}")
            print(f"Tipo: {'Establecimiento' if contacto[1] == 1 else 'Persona'}")
            if contacto[1] == 1:
                print(f"NIT: {contacto[3]}")
            else:
                print(f"CI: {contacto[2]}")
            print(f"Nombre: {contacto[4]}")
            if contacto[5]:
                print(f"Fecha de nacimiento: {contacto[5]}")
            if contacto[6]:
                print(f"Teléfono: {contacto[6]}")
            print(f"Dirección: {contacto[7]}")
            print(f"País: {contacto[9]} ({contacto[10]})")
    else:
        print("\n✗ No se encontraron contactos con los filtros especificados.")

def actualizar_contacto():
    """Actualiza un contacto existente"""
    print("\n=== ACTUALIZAR CONTACTO ===")
    id_contacto = input("Ingrese ID del contacto a actualizar: ")
    
    conn = conectar()
    cursor = conn.cursor()
    
    # Verificar que existe el contacto
    cursor.execute('SELECT * FROM contactos WHERE id = ?', (id_contacto,))
    contacto = cursor.fetchone()
    
    if not contacto:
        print("\n✗ Contacto no encontrado.")
        conn.close()
        return
    
    print("\n¿Qué desea actualizar?")
    print("1. Nombre")
    print("2. Teléfono")
    print("3. Dirección")
    
    opcion = input("Seleccione opción (1-3): ")
    
    if opcion == '1':
        nuevo_valor = input("Ingrese nuevo nombre: ")
        cursor.execute('UPDATE contactos SET nombre = ? WHERE id = ?', (nuevo_valor, id_contacto))
    elif opcion == '2':
        nuevo_valor = input("Ingrese nuevo teléfono: ")
        cursor.execute('UPDATE contactos SET telefono = ? WHERE id = ?', (nuevo_valor, id_contacto))
    elif opcion == '3':
        nuevo_valor = input("Ingrese nueva dirección: ")
        cursor.execute('UPDATE contactos SET direccion = ? WHERE id = ?', (nuevo_valor, id_contacto))
    else:
        print("Opción inválida.")
        conn.close()
        return
    
    conn.commit()
    conn.close()
    print("\n✓ Contacto actualizado exitosamente.")

def eliminar_contacto():
    """Elimina un contacto por ID"""
    print("\n=== ELIMINAR CONTACTO ===")
    id_contacto = input("Ingrese ID del contacto a eliminar: ")
    
    conn = conectar()
    cursor = conn.cursor()
    
    # Verificar que existe el contacto
    cursor.execute('SELECT * FROM contactos WHERE id = ?', (id_contacto,))
    contacto = cursor.fetchone()
    
    if not contacto:
        print("\n✗ Contacto no encontrado.")
        conn.close()
        return
    
    confirmacion = input(f"¿Está seguro de eliminar el contacto '{contacto[4]}'? (s/n): ")
    
    if confirmacion.lower() == 's':
        cursor.execute('DELETE FROM contactos WHERE id = ?', (id_contacto,))
        conn.commit()
        print("\n✓ Contacto eliminado exitosamente.")
    else:
        print("\nOperación cancelada.")
    
    conn.close()