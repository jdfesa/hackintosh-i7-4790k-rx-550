# Fase 1 y 2: OpenCore y Kexts Base

Este documento detalla estructura fundamental instalada en la carpeta `EFI/` y los controladores o "Kexts" (Kernel Extensions) base de macOS que inyectaremos mediante OpenCore.

## Archivos Base de OpenCore (Fase 1)
Descargamos la versión oficial estable ("Release") de OpenCorePkg. Limpiamos la estructura, dejando el esqueleto limpio conformado por:

- `EFI/BOOT/BOOTx64.efi`: El cargador de arranque primario.
- `EFI/OC/OpenCore.efi`: El motor base de OpenCore.
- `EFI/OC/Drivers/OpenRuntime.efi`: Extensión necesaria para el soporte de memoria e inyección en macOS.
- `EFI/OC/Drivers/HfsPlus.efi`: Descargado de forma separada del repositorio OcBinaryData. Necesario para que la BIOS pueda "ver" la partición HFS/APFS donde instalaremos macOS.
- `EFI/OC/config.plist`: El archivo maestro (partiendo de `Sample.plist`) donde configuraremos todos los parámetros a medida más adelante.

## Kexts Base Inyectados (Fase 2)
Descargamos las herramientas más vitales generadas por el equipo Acidanthera y la comunidad:

| Kext | Función en la máquina (i7-4790K / Haswell) |
| :--- | :--- |
| **Lilu.kext** | Motor central. Permite aplicar parches "al vuelo" a otros kexts. Necesario para todos los que siguen. |
| **VirtualSMC.kext** | Emula el chip SMC de las computadoras Apple. Sin esto, macOS no arrancará. |
| `SMCProcessor.kext` | Sensor hijo de SMC. Monitorea la temperatura del i7-4790K. |
| `SMCSuperIO.kext` | Sensor hijo de SMC. Monitorea las velocidades de los ventiladores de la placa madre. |
| **WhateverGreen.kext** | Controlador de parches de video central. Fundamental para inyectar nuestro "Spoof" a la placa de video RX 550 más adelante. |
| **AppleALC.kext** | Permite habilitar el chip de audio High Definition Realtek que detectamos. |
| **RealtekRTL8111.kext** | Kext de conexión de red Ethernet de Mieze para tu placa madre. |

*(Nota: los sensores de batería en VirtualSMC fueron eliminados del ensamblado ya que esta unidad es de escritorio).*
