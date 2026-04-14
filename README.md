# Hackintosh i7-4790K + RX 550 (Lexa)

> [!WARNING]
> ## ⚠️ TRABAJO EN PROGRESO — Sesión pausada el 2026-04-14
>
> **Estado actual:** macOS Tahoe y Sequoia probados. Ambos resultan **inviables** para un uso fluido debido a la falta de aceleración Metal/GPU con la tarjeta Lexa.
>
> ### Problema Crítico Confirmado: AMD RX 550 (Lexa 699F)
> - Las tarjetas Lexa necesitan un "Spoofing" para hacerse pasar por Baffin (67FF) porque Apple nunca les dio soporte oficial.
> - A partir de macOS Ventura/Sonoma/Sequoia, Apple eliminó los drivers Polaris nativos.
> - Al depender de OCLP (OpenCore Legacy Patcher) para reinyectarlos en Sequoia, el sistema cae en un "Catch-22": OCLP requiere aceleración Metal básica para renderizar su interfaz UI, pero como la Lexa no la tiene, la aplicación se muestra en blanco impidiendo parchar (Pantalla Blanca).
>
> ### Decisión Técnica: Downgrade a macOS Monterey (12.x)
> - Tras una investigación cruzada comunitaria, la solución dictaminada es instalar **macOS Monterey**.
> - En Monterey, los drivers Polaris siguen estando de forma nativa en el sistema base de Apple.
> - Se aplicará el spoofing en la EFI hacia Baffin (67FF), y Monterey activará la aceleración Metal al 100% de manera automática y nativa, sin requerir parches de OCLP rompiendo el sistema.
>
> ### Estado de la EFI actual (Híbrida para Monterey)
> - SMBIOS: `MacPro7,1`
> - boot-args: `-v keepsyms=1 debug=0x100 alcid=1 amfi=0x80 watchdog=0 agdpmod=pikera dk.e1000=0 e1000=0`
> - AMFIPass.kext v1.4.1 incluido y activo
> - Prev-lang:kbd forzado a `en-US:0` para evitar bloqueos regionales en el instalador
> - **Internet (Intel/Realtek/Atheros) inyectado vía Oralilla base** ✅
> - **Audio funciona** ✅
> - **GPU: Spoof Baffin activado, listo para Metal Nativo en Monterey** ⏳

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
