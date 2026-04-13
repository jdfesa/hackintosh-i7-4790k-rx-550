# Troubleshooting y Solución de Arranque - macOS Tahoe (15)

Este documento registra los problemas encontrados y las soluciones aplicadas durante el proceso de instalación de **macOS Tahoe** en un sistema basado en la arquitectura **Intel Haswell**. Es importante documentar esto de forma detallada, ya que macOS Tahoe probablemente sea una de las últimas versiones compatibles con procesadores x86.

## Hardware Objetivo
- **Procesador:** Intel Core i7-4790K (Haswell)
- **Placa Base:** Chipset B85
- **Tarjeta Gráfica:** AMD Radeon RX 550

## Problemas Encontrados

Durante las pruebas iniciales para intentar arrancar el instalador de macOS Tahoe, el sistema no lograba completar el inicio. Los principales obstáculos se centraban en las validaciones de compatibilidad de macOS para hardware descontinuado (como nuestra plataforma Haswell) y configuraciones previas al entorno de instalación.

## Soluciones y Cambios Implementados

Para lograr acceder al entorno del instalador y proceder con la instalación en el SSD, realizamos las siguientes configuraciones clave en OpenCore:

### 1. Evasión de Comprobaciones de Compatibilidad (Spoofing & Kexts)
Dado que el SMBIOS necesario o el hardware base (Haswell) ya no son oficialmente soportados para instalar las últimas versiones de macOS directamente, aplicamos medidas para saltarnos las validaciones de la plataforma:
- **Argumento de Arranque (Boot-arg):** Se añadió el argumento `-no_compat_check` en nuestra sección `NVRAM -> Add -> 7C436110-AB2A-4BBB-A880-FE41995C9F82 -> boot-args` del `config.plist`.
- **RestrictEvents.kext:** Integrado este kext y configurado usando el argumento adicional `revpatch=sbvmm`. Esta combinación engaña al sistema y a las actualizaciones de macOS para que admitan la ejecución de las funciones del instalador, logrando esquivar el bloqueo de compatibilidad.

### 2. Ajustes de la Configuración del Kernel (Quirks para B85)
Las placas base con chipset como B85 (y otras series 8 o 9 de Intel) a veces requieren correcciones a nivel de kernel para gestionar correctamente la hibernación, asignaciones de memoria y parches específicos.
- Nos aseguramos de revisar y habilitar los *Kernel Quirks* correspondientes en el archivo `config.plist`, estabilizando el inicio y la compatibilidad general.

### 3. Configuración del SMBIOS
- Se verificó y regeneró un registro de SMBIOS válido que brindará un buen perfil de energía ajustado para la configuración Haswell asegurando que OpenCore inyectara datos correctos, fundamentales para los servicios del SO y arranque seguro.

### 4. Preparación del Almacenamiento
*A modo de recordatorio para la fase del instalador:* 
- Para que la unidad SSD interna aparezca correctamente en el instalador y se pueda proceder a su uso, se estableció que debe estar obligatoriamente formateada como **Mac OS Extended (Journaled)** o preferiblemente **APFS**, utilizando un mapa de particiones **GUID (GPT)**.

---
*Documentación generada para facilitar futuras instalaciones y mantenimientos del equipo en macOS Tahoe.*
