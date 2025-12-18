# Mapeo de Direcciones Modbus - PLC HNC Serie HCS
Modelo probado: HCS-6X4Y-T  
Configuración necesaria: PLC en modo "Soft Address" (Mapeo por bloques de 1024/512)

Este repositorio contiene las direcciones Modbus TCP confirmadas mediante barridos técnicos (scanning). Es ideal para quienes necesitan integrar estos PLCs con Python, Django o sistemas SCADA sin tener la documentación clara del fabricante.

---

## 1. Tabla de Direccionamiento (Modbus Decimal)

Estas direcciones son las que responden tras el barrido. Si usas el modo estándar de HNC, estos son tus puntos de conexión:

| Componente PLC     | Dirección (DEC) | Tipo de Objeto Modbus | Función (FC) |
|       :---         |       :---      |          :---         |     :---     |
|   X   (Entradas)   |       1024      |    Discrete Input     |      02      |
|   Y (Salidas)      |       1536      |          Coil         |    01, 05    |
|   M (Memorias)     |       3072      |          Coil         |    01, 05    |
|   CV (Contadores)  |       16384     |      Input Register   |      04      |
|   V / D (Datos)    |       512       |     Holding Register  |    03, 06    |

---

## 2. Detalles de Implementación

### Entradas y Salidas (X / Y)
* X0...X5: Se leen desde la 1024. Úsalas para monitorear sensores o botones físicos.
* Y0...Y3: Se controlan desde la 1536. Son las salidas a relevador o transistor del PLC.

### Memorias Internas (M)
* M0: Arranca en la 3072. Es la forma más fácil de mandar comandos desde Python al programa Ladder.

### Contadores (CV - Totales de Pozo)
* CV0: Se encuentra en la dirección 16384.
* Nota para 32 bits: Si el contador es de alta velocidad o un totalizador grande, usa dos registros. Para leerlo correctamente en Python:  
  `valor_total = (registro_alto << 16) + registro_bajo`

---

## 3. Código de ejemplo (Python + PyModbus)

Ojo: En esta versión de PLC y librería, es obligatorio usar `device_id=1`.
