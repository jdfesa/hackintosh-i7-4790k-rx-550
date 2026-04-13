# Hackintosh i7-4790K + RX 550 (Lexa)

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
