from pymodbus.client import ModbusTcpClient
import os
import time

# --- CONFIGURACIÓN GLOBAL (Fácil de modificar) ---
PLC_IP = '192.168.1.111'
PORT = 502
ID_DISPOSITIVO = 1  # Tu device_id que funciona

client = ModbusTcpClient(PLC_IP, port=PORT)

# =========================================================
# 1. ESCANEO DE BITS (COILS / DISCRETE INPUTS)
# =========================================================

def escanear_coils(inicio=1536, fin=3600):
    """
    Busca Coils (Y/M) activos. 
    Retorna una lista en res.bits.
    """
    print(f"\n[SCAN] Buscando Coils activos entre {inicio} y {fin}...")
    if client.connect():
        for i in range(inicio, fin):
            res = client.read_coils(address=i, count=1, device_id=ID_DISPOSITIVO)
            if not res.isError():
                if True in res.bits:
                    print(f"-> Dirección {i}: {res.bits}")
        client.close()
    else:
        print("Error de conexión.")

def localizar_m0_on(inicio=0, fin=8000):
    """
    Escaneo amplio para encontrar memorias auxiliares (M) en estado ON.
    """
    print(f"\n[SCAN] Localizando memorias M en ON (Rango {inicio}-{fin})...")
    if client.connect():
        for i in range(inicio, fin):
            res = client.read_coils(address=i, count=1, device_id=ID_DISPOSITIVO)
            if not res.isError():
                if res.bits[0] is True:
                    print(f"¡BIT ENCONTRADO! Dirección Modbus {i} está en ON.")
        client.close()

# =========================================================
# 2. ESCANEO DE REGISTROS (V / D / CV)
# =========================================================

def escanear_holding_registers(inicio=0, fin=16000, saltos=1):
    """
    Busca registros de datos (V o D). 
    Recibe una lista en res.registers.
    """
    print(f"\n[SCAN] Buscando Holding Registers (V/D) entre {inicio} y {fin}...")
    if client.connect():
        for base in range(inicio, fin):
            res = client.read_holding_registers(address=base, count=saltos, device_id=ID_DISPOSITIVO)
            if not res.isError():
                for i, valor in enumerate(res.registers):
                    if valor != 0:
                        print(f"¡DATO! Dirección {base + i}: Valor = {valor}")
        client.close()

def escanear_input_registers(inicio=16383, fin=16400):
    """
    Busca registros de entrada (CV / Contadores).
    Función 04 de Modbus.
    """
    print(f"\n[SCAN] Buscando Input Registers (CV) entre {inicio} y {fin}...")
    if client.connect():
        for i in range(inicio, fin):
            res = client.read_input_registers(address=i, count=1, device_id=ID_DISPOSITIVO)
            if not res.isError():
                for idx, valor in enumerate(res.registers):
                    if valor != 0:
                        print(f"¡REGISTRO ENCONTRADO! Dirección {i}: Valor = {valor}")
        client.close()

# =========================================================
# 3. MONITOREO Y CONTROL
# =========================================================

def monitorear_salidas_y(base=1536, cant=4):
    """
    Monitoreo en tiempo real de las salidas Y.
    """
    if not client.connect(): return
    print("Monitoreando... Ctrl+C para salir.")
    try:
        while True:
            res = client.read_coils(address=base, count=cant, device_id=ID_DISPOSITIVO)
            os.system('cls' if os.name == 'nt' else 'clear')
            if not res.isError():
                estados = res.bits[:cant]
                linea = " | ".join([f"Y{i}: {'ON' if e else 'OFF'}" for i, e in enumerate(estados)])
                print(f"MONITOREO PLC {PLC_IP} | Base: {base}")
                print("-" * 50)
                print(f"ESTADO ACTUAL: {linea}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nDetenido.")
    finally:
        client.close()

def forzar_m_y_verificar(m_addr=3073, y_addr=1536):
    """
    Activa una memoria M y verifica el estado de una salida Y.
    """
    if client.connect():
        print(f"Escribiendo False en M{m_addr}...")
        client.write_coil(address=m_addr, value=False, device_id=ID_DISPOSITIVO)
        time.sleep(0.5)
        res = client.read_coils(address=y_addr, count=1, device_id=ID_DISPOSITIVO)
        if not res.isError():
            print(f"Estado de Y{y_addr}: {'ENCENDIDO' if res.bits[0] else 'APAGADO'}")
        client.close()

# =========================================================
# 4. INTERFAZ DE SELECCIÓN
# =========================================================

def menu():
    while True:
        print("\n--- HERRAMIENTA DE MAPEO HNC ---")
        print("1. Escanear Coils (Salidas/Memorias)")
        print("2. Localizar M0 (Búsqueda ON)")
        print("3. Monitorear Salidas Y (Tiempo Real)")
        print("4. Escanear Holding Registers (V/D)")
        print("5. Escanear Input Registers (CV/Contadores)")
        print("6. Probar Trigger M -> Y")
        print("0. Salir")
        
        op = input("\nSeleccione opción: ")

        if op == "1": escanear_coils(inicio=1530, fin=1550)
        elif op == "2": localizar_m0_on(inicio=3070, fin=3080)
        elif op == "3": monitorear_salidas_y(base=1536)
        elif op == "4": escanear_holding_registers(inicio=510, fin=520)
        elif op == "5": escanear_input_registers(inicio=16380, fin=16400)
        elif op == "6": forzar_m_y_verificar()
        elif op == "0": break
        else: print("Opción inválida.")

if __name__ == "__main__":
    menu()