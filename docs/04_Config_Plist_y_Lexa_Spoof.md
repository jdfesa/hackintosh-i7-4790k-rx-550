# Fase 4: Configuración final y Spoof de Lexa RX 550

El archivo `config.plist` es el "cerebro" temporal de la placa base donde indicamos qué configuraciones específicas activar para que el hardware sea compatible.
Para asegurar su correcto funcionamiento, hemos creado y ejecutado un script en Python (disponible en `scripts/build_opencore_config.py`) para evitar errores humanos al escribir código XML a mano.

## Datos Clave Configurados:

1.  **PlatformInfo / SMBIOS:** Hemos firmado la máquina virtualmente como una `iMac15,1`. Este es el modelo oficial de Apple que utilizó el mismo procesador Intel Core i7-4790K que tienes, lo cual asegura el mejor perfil de energía.
2.  **NVRAM y Boot Arguments:** Se inyectaron `-v keepsyms=1 debug=0x100 alcid=1`
    *   `-v`: Verbose. Mostrará las letras en pantalla como en Linux al iniciar, esencial para investigar si hay errores.
    *   `alcid=1`: Identificador nativo inyectado para que `AppleALC.kext` logre encender el audio High Definition de la placa B85.
3.  **Spoof de Tarjeta Gráfica (El parche Crítico):**
    *   **Ruta Asumida:** Hemos inyectado las propiedades en la ruta PCI Express matriz: `PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)`
    *   **Engaño:** Se forzó la llave `device-id` con el valor hexadecimal `<FF670000>` (que invertido en lectura de *little endian* de PC es `67FF`).
    *   Con esto, tu chip **Lexa** pasará la comprobación del *WhateverGreen* haciéndose pasar por un chip Baffin.

## 🛠️ ¿Cómo reconstruir este config.plist?
Si en el futuro reinstalas OpenCore desde otro repositorio y pierdes este archivo, basta con tener un `Sample.plist` nuevo en `EFI/OC/` y volver a ejecutar el comando:
```powershell
python scripts\build_opencore_config.py
```
El script leerá y parchará todo en milésimas de segundo, reconstruyendo la magia.
