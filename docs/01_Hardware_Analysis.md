# Fase 1: Análisis de Hardware en Windows

Antes de comenzar a descargar archivos para el Hackintosh, es de vital importancia conocer el hardware exacto interno de la máquina. Esto evita dolores de cabeza y previene usar configuraciones o parches inapropiados de distribuciones genéricas.

## Comandos de PowerShell Utilizados

Para escanear los componentes críticos directamente en Windows 11 utilizando PowerShell sin necesidad de instalar programas de terceros (como AIDA64), hemos utilizado la clase `Get-CimInstance`:

### 1. Modelo del Procesador
```powershell
Get-CimInstance Win32_Processor | Select-Object Name
```
*   **Resultado:** Intel(R) Core(TM) i7-4790K CPU @ 4.00GHz (Arquitectura Haswell)

### 2. Tarjeta Gráfica y Device ID
Este comando es crítico, especialmente para la familia AMD RX 500, ya que revela la ID de dispositivo real y nos indica si el chip gráfico es soportado o no nativamente.
```powershell
Get-CimInstance Win32_VideoController | Format-Table Name, PNPDeviceID -AutoSize
```
*   **Resultado:** Radeon RX550 / Device ID: `PCI\VEN_1002&DEV_699F`. 
*   **Nota crítica:** El Device ID `699F` pertenece al core **Lexa**, no al Baffin. Requiere de *Device ID Spoofing* (a `67FF`) en OpenCore para activar la aceleración de video en macOS.

### 3. Modelo de la Placa Base
```powershell
Get-CimInstance Win32_BaseBoard | Format-Table Manufacturer, Product -AutoSize
```
*   **Resultado:** Chipset B85 (Totalmente compatible).

### 4. Controlador de Red (Ethernet)
```powershell
Get-CimInstance Win32_NetworkAdapter | Where-Object { $_.PhysicalAdapter -eq $true } | Select-Object Name, PNPDeviceID
```
*   **Resultado:** Realtek PCIe GbE Family Controller. Requiere el kext `RealtekRTL8111.kext`.

### 5. Controladores de Audio
```powershell
Get-CimInstance Win32_SoundDevice | Select-Object Name, PNPDeviceID
```
*   **Resultado:** High Definition Audio Device. Funcionará con `AppleALC.kext` y explorando los `layout-id` válidos correspondientes al ALC interno.

### 6. Almacenamiento Objetivo
Para garantizar la máxima seguridad y evitar corromper la instalación actual de Windows, no tocaremos los discos duros internos de este sistema.
*   **Disco Asignado a Hackintosh:** SSD SATA de 256 GB montado en Caddy/Caja externa por conexión USB 3.0.

---

Siguiente paso: Estructuración base de OpenCore y compilación de tablas ACPI específicas para la arquitectura Haswell.
