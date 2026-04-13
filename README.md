# Hackintosh i7-4790K + RX 550 (Lexa)

> [!WARNING]
> ## ⚠️ TRABAJO EN PROGRESO — Sesión pausada el 2026-04-13
>
> **Estado actual:** macOS Tahoe 26.4.1 arranca y es usable, pero **sin aceleración Metal/GPU** (rendering por software).
>
> ### Problema pendiente: AMD RX 550 (Lexa 699F) sin aceleración gráfica
> - El spoof a Baffin (67FF) está aplicado correctamente en `DeviceProperties`.
> - La ruta PCI detectada es correcta: `PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)`.
> - WhateverGreen.kext está activo (no puede quitarse — sin imagen al arranque).
> - OCLP 2.4.1 dice "No patches required" porque con SMBIOS `iMac18,3` (iMac con GPU Polaris real), no detecta necesidad de parchear.
> - La aceleración gráfica Metal no está activa (verificar con `system_profiler SPDisplaysDataType | grep Metal`).
>
> ### Próximos pasos a investigar
> 1. Ejecutar `system_profiler SPDisplaysDataType | grep -E "Vendor|Device|Metal|Chipset|Model"` para confirmar si Metal está activo.
> 2. Revisar si `AMDRadeonX4000.kext` (driver Polaris) existe en el sistema o fue eliminado en Tahoe/Sequoia.
> 3. Si el driver no existe en el sistema, OCLP es la única solución — investigar por qué no lo ofrece con `iMac18,3`.
> 4. Alternativa: probar SMBIOS `MacPro7,1` o `iMac19,1` para ver si OCLP detecta diferente.
>
> ### Estado de la EFI actual
> - SMBIOS: `iMac18,3`
> - boot-args: `-v keepsyms=1 debug=0x100 alcid=1 -radcodec -no_compat_check revpatch=sbvmm -amfipassbeta agdpmod=pikera`
> - AMFIPass.kext v1.4.1 incluido y activo
> - WhateverGreen.kext activo
> - `amfi=0x80` eliminado (era la causa de inestabilidad previa)
> - **Internet (Ethernet RealTek) funciona** ✅
> - **Audio funciona** ✅
> - **GPU: detectada pero SIN Metal** ⚠️

Bienvenido a este repositorio. Este proyecto documenta y contiene la configuración (carpeta EFI) para instalar macOS (Vanilla OpenCore) en una PC de escritorio basada en arquitectura Intel Haswell y gráficos AMD Polaris/Lexa.

## Objetivo
El objetivo es aislar la instalación de macOS en un disco SSD externo conectado por USB 3.0 para evitar comprometer sistemas Windows previamente instalados, garantizando hardware nativo estable y una configuración limpia sin el uso de herramientas genéricas (como Olarila o scripts automatizados).

## Especificaciones del Hardware
- **Procesador:** Intel Core i7-4790K (Haswell)
- **Placa Base:** Intel B85 Chipset
- **Memoria RAM:** 16 GB
- **Tarjeta Gráfica:** AMD Radeon RX 550 (Device ID: 1002, 699F - **Lexa Core**)
- **Almacenamiento (Para macOS):** SSD SATA de 256 GB conectado externamente por caja USB 3.0 *(Nota: Los discos internos se aislarán/ignorarán durante este proceso para evitar cualquier impacto al sistema existente).*
- **Red:** Realtek PCIe GbE Family Controller
- **Audio:** High Definition Audio Device (Realtek)

## Estructura de Documentación
Toda la documentación técnica del proceso se construirá paso a paso en la carpeta `/docs`. Empezando por la extracción de datos en Windows y culminando con los parches específicos para la tarjeta de video (Spoofing).
