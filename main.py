from contactos import agregar_contacto, buscar_contacto, actualizar_contacto, eliminar_contacto

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*40)
    print("    AGENDA TELEFÓNICA")
    print("="*40)
    print("1. Agregar contacto")
    print("2. Buscar contacto")
    print("3. Actualizar contacto")
    print("4. Eliminar contacto")
    print("5. Salir")
    print("="*40)

def main():
    """Función principal del programa"""
    print("\n¡Bienvenido a la Agenda Telefónica!")
    print("Sistema de gestión de contactos")
    
    while True:
        mostrar_menu()
        opcion = input("\nSeleccione una opción (1-5): ")
        
        if opcion == '1':
            agregar_contacto()
        
        elif opcion == '2':
            buscar_contacto()
        
        elif opcion == '3':
            actualizar_contacto()
        
        elif opcion == '4':
            eliminar_contacto()
        
        elif opcion == '5':
            print("\n¡Gracias por usar la Agenda Telefónica!")
            print("Hasta pronto.")
            break
        
        else:
            print("\n✗ Opción inválida. Por favor, seleccione una opción del 1 al 5.")
        
        # Pausa antes de mostrar el menú nuevamente
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()