from pymodbus.client import ModbusTcpClient
import os
import time

PLC_IP = '192.168.1.111'
client = ModbusTcpClient(PLC_IP, port=502)
BASE_SALIDAS = 1536 # La dirección que descubriste con tu barrido

def descubrir_y0():
    if client.connect():
        #addres: 1536,
        for i in range(0,2400):
            res = client.read_coils(address=i, count=1, device_id=1)
            
            if not res.isError():
                if True in res.bits:
                    print(f"direccion {i}: {res.bits}")
        client.close()

def monitorear_salidas():
    if not client.connect():
        print("No se pudo conectar al PLC.")
        return

    try:
        while True:
            # Leer las 4 salidas (Y0, Y1, Y2, Y3) de un solo golpe
            res = client.read_coils(address=BASE_SALIDAS, count=4, device_id=1)
            
            # Limpiar la terminal según el sistema operativo
            # 'cls' para Windows, 'clear' para Linux/Mac
            os.system('cls' if os.name == 'nt' else 'clear')
            
            if not res.isError():
                # Formatear la salida para verla en una sola línea
                estados = res.bits[:4]
                linea = " | ".join([f"Y{i}: {'ON' if estado else 'OFF'}" for i, estado in enumerate(estados)])
                print(f"Monitoreando PLC {PLC_IP} (Presione Ctrl+C para salir)")
                print("-" * 50)
                print(f"ESTADO ACTUAL: {linea}")
            else:
                print(f"Error de lectura: {res}")
            
            # Tiempo de espera entre lecturas (ajustable)
            time.sleep(0.5) 

    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario.")
    finally:
        client.close()
        print("Conexión cerrada.")



def localizar_m0():
    if client.connect():
        print("--- Escaneando rango de memorias M (Buscando M0 en ON) ---")
        
        rangos = [(0, 8000)]
        
        #3072, 1536
        for inicio, fin in rangos:
            for i in range(inicio, fin):
                res = client.read_coils(address=i, count=1, device_id=1)
                if not res.isError():
                    if res.bits[0] is True:
                        print(f"¡BIT ENCONTRADO! Dirección Modbus {i} está en ON.")
        client.close()
    else:
        print("Error de conexión.")


#Componente PLC,Dirección Modbus (Decimal),Función Modbus
#Y0,1536,Coil (0x01 / 0x05)
#Y1,1537,Coil (0x01 / 0x05)
#M0,3072,Coil (0x01 / 0x05)
#M1,3073,Coil (0x01 / 0x05)
#X0,1024,Discrete Input (0x02)


M0_ADDRESS = 3073  # Tu descubrimiento
Y0_ADDRESS = 1536  # Tu descubrimiento
def control_y0_via_m0():
    if client.connect():
        # 1. Encendemos M0
        print("Activando M0...")
        client.write_coil(address=M0_ADDRESS, value=False, device_id=1)
        time.sleep(0.5)
        
        # 2. Verificamos si Y0 se encendió (por la lógica del PLC)
        res = client.read_coils(address=Y0_ADDRESS, count=1, device_id=1)
        if not res.isError():
            print(f"Estado de Y0: {'ENCENDIDO' if res.bits[0] else 'APAGADO'}")
            
        client.close()
        
def escanear_registros():
    """
    V0=512
    """
    if client.connect():
        print("--- Escaneando Holding Registers (V/D y CV) ---")
        # Probamos los bloques lógicos basados en tus hallazgos
        
        for base in range(0,16000):
            # Leemos de 50 en 50 para no saturar
            res = client.read_holding_registers(address=base, count=50, device_id=1)
            if not res.isError():
                # Si ves un número diferente de 0, ¡ahí hay algo!
                for i, valor in enumerate(res.registers):
                    if valor != 0:
                        print(f"¡DATO ENCONTRADO! Dirección {base + i}: Valor = {valor}")
            else:
                print(f"Bloque {base} no disponible.")
        client.close()
        
        

def escanear_input_registers():
    if client.connect():
        print("--- Escaneando Input Registers (Función 04) ---")
        # Probamos los bloques donde tu PLC organiza la memoria
        
        for base in range(16383,16385):
            # Leemos bloques de 100 registros
            res = client.read_input_registers(address=base, count=100, device_id=1)
            
            if not res.isError():
                for i, valor in enumerate(res.registers):
                    if valor != 0: # Si hay un valor, encontramos una variable activa
                        print(f"¡REGISTRO ENCONTRADO! Dirección {base + i}: Valor = {valor}")
            else:
                print(f"Bloque {base}: No soportado o error.")
        client.close()
    else:
        print("No se pudo conectar.")

if __name__ == "__main__":
    escanear_input_registers()
