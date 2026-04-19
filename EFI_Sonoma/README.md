# EFI Sonoma — Hackintosh i7-4790K + RX 550 Lexa

> [!CAUTION]
> ## 🚧 PROYECTO EN PROGRESO — NO USAR ESTA EFI
>
> Esta EFI **no está lista para arrancar**. Es una copia de trabajo de `EFI_Tahoe` que será modificada para macOS Sonoma 14.8.5.
> Los cambios necesarios (SMBIOS, iGPU config, boot-args) **todavía no fueron aplicados**.
> Si necesitás una EFI funcional, usá `EFI_Tahoe` que es la configuración estable y probada en macOS Tahoe 26.4.1.

---

## Objetivo: Sistema Bullet-Proof en macOS Sonoma 14.8.5

> [!IMPORTANT]
> Esta EFI es una **copia de trabajo** de `EFI_Tahoe` que será adaptada para macOS Sonoma 14.8.5 con OCLP.
> La EFI de Tahoe no se toca — funciona perfecta para su propósito.

---

## ¿Por qué Sonoma y no Tahoe?

La EFI de Tahoe ya funciona: Metal activo, GPU acelerada, sistema fluido. Pero tiene una **limitación estructural** que no podemos resolver en esa versión: **no hay decodificación de video por hardware (QuickSync)**, porque Apple eliminó los drivers de Intel HD 4600 (Haswell) a partir de macOS Ventura.

El objetivo de esta nueva EFI es tener un **sistema completamente optimizado** — no solo funcional, sino aprovechando el 100% del hardware disponible.

### Tahoe vs Sonoma — Comparación técnica

| Factor | Tahoe (26.x) — EFI actual | Sonoma (14.x) — EFI objetivo |
|--------|---------------------------|------------------------------|
| **Metal / GPU Acceleration** | ✅ Nativo (SSDT ACPI spoof) | ✅ Nativo (SSDT ACPI spoof) |
| **iGPU Intel HD 4600** | ❌ Sin drivers en el sistema | ✅ Restaurable via OCLP root patches |
| **QuickSync (HW decode)** | ❌ Decode por software (~2.8 cores en 4K) | ✅ Esperable con iGPU activa (~5-10% CPU) |
| **AppleGVA framework** | ❌ No disponible | ✅ Restaurable via OCLP |
| **OCLP necesario** | No (Metal funciona nativo) | Sí (para restaurar drivers iGPU Haswell) |
| **SIP** | ✅ Habilitado | ⚠️ Parcialmente deshabilitado (requerido por OCLP) |
| **Updates de Apple** | ✅ Directos | ⚠️ Deben ser manuales y verificados vs OCLP |
| **Security patches** | ✅ Activos | ✅ Activos hasta ~fin 2026 |
| **Estabilidad OCLP** | N/A | ✅ Root patches Haswell maduros y probados |

---

## ¿Por qué Sonoma y no Sequoia?

Esta fue la decisión más analizada. Sequoia (15.x) es más nueva, pero **Sonoma es más segura a largo plazo** para este hardware. Las razones:

### 1. OCLP en modo mantenimiento vs. desarrollo activo
- **Sequoia**: OCLP dice explícitamente *"Sequoia support is still in active development"* en cada release. Cada update de Apple puede romper los patches.
- **Sonoma**: OCLP tiene soporte maduro. Apple ya solo envía security patches, no cambia frameworks internos.

### 2. El proyecto OCLP tiene futuro incierto
- Los developers principales se están yendo del proyecto (marzo 2026).
- Ya no aceptan donaciones.
- OCLP 2.4.1 solo menciona soporte hasta Sequoia 15.5, pero Apple ya va por 15.7.5.
- En Sonoma, aunque OCLP deje de actualizarse, **los patches ya aplicados siguen funcionando** mientras no actualicemos macOS.

### 3. Sonoma todavía recibe security patches
- La última versión es **Sonoma 14.8.5** (24 marzo 2026).
- Apple mantiene security updates para las 3 últimas versiones mayores.
- Estimado hasta fin de 2026 o principios de 2027.

### 4. Menor superficie de riesgo
- Sonoma no tiene cambios agresivos en el kernel como los que Apple introdujo en Sequoia.
- Los root patches de Haswell para Sonoma llevan 2+ años de pruebas comunitarias.
- La probabilidad de un security update de Apple rompiendo los patches es mínima en una versión en mantenimiento.

---

## Hardware target

| Componente | Especificación |
|-----------|----------------|
| **CPU** | Intel Core i7-4790K (Haswell, 4C/8T, 4.0GHz) |
| **Placa Base** | Intel B85 Chipset |
| **RAM** | 16 GB |
| **dGPU** | AMD RX 550 Lexa → Spoof ACPI a Baffin (`67FF`) |
| **iGPU** | Intel HD 4600 → Objetivo: headless compute + QuickSync |
| **Almacenamiento** | SSD (interno, reemplazando Linux/Windows) |
| **Red** | Realtek PCIe GbE |
| **Audio** | Realtek HD Audio |

---

## Configuración objetivo

| Componente | Valor | Propósito |
|-----------|-------|-----------|
| **SMBIOS** | `iMac14,2` | Perfil nativo Haswell con soporte iGPU + dGPU |
| **SSDT** | `SSDT-GPU-SPOOF.aml` | Spoof Lexa → Baffin a nivel ACPI (mantener de Tahoe) |
| **iGPU** | HD 4600 headless compute | `AAPL,ig-platform-id` según Dortania Haswell |
| **OCLP** | Root patches post-instalación | Restaurar drivers Haswell eliminados |
| **boot-args** | Por definir | Ajustar para Sonoma + OCLP |
| **macOS target** | **Sonoma 14.8.5** | Última versión estable disponible |
| **OCLP target** | **2.3.2 o 2.4.1** | Versión estable con soporte Sonoma completo |

---

## Cambios pendientes respecto a EFI_Tahoe

> [!NOTE]
> Estos cambios se irán aplicando en esta carpeta. La EFI de Tahoe permanece intacta.

- [ ] Cambiar SMBIOS de `MacPro7,1` → `iMac14,2`
- [ ] Configurar iGPU Intel HD 4600 según [guía Dortania Haswell dGPU+iGPU](https://dortania.github.io/OpenCore-Install-Guide/config.plist/haswell.html)
- [ ] Ajustar `AAPL,ig-platform-id` para headless compute
- [ ] Ajustar `device-id` de la iGPU si es necesario
- [ ] Revisar boot-args (posiblemente remover `-radcodec`, agregar flags para OCLP)
- [ ] Verificar compatibilidad de kexts con Sonoma 14.8.5
- [ ] Preparar instalador USB con Sonoma 14.8.5
- [ ] Instalar en SSD interno (reemplazando SO actual)
- [ ] Aplicar OCLP root patches post-instalación
- [ ] Verificar QuickSync activo: `ioreg -l | grep -i "AppleGVA"`
- [ ] Verificar Metal activo: `system_profiler SPDisplaysDataType | grep -i metal`
- [ ] Verificar HW decode: reproducir video 4K y medir CPU usage
- [ ] Deshabilitar actualizaciones automáticas de macOS
- [ ] Documentar resultado final

---

## Estrategia "Bunker" post-instalación

Una vez que el sistema esté funcionando al 100%:

1. **Deshabilitar actualizaciones automáticas** — System Settings → General → Software Update → desactivar todo
2. **Nunca actualizar macOS** sin verificar primero que OCLP tiene soporte para esa versión
3. **Hacer backup de la EFI funcional** — copia en el repo y copia offline
4. **Documentar todo** — cada cambio queda registrado en este repo

---

## Origen de esta EFI

Esta EFI es una copia exacta de `EFI_Tahoe` (que funciona con macOS Tahoe 26.4.1 con Metal activo vía SSDT ACPI spoof). Se usa como base porque:

1. La estructura OpenCore ya está probada y funcional para este hardware
2. El SSDT-GPU-SPOOF.aml para la RX 550 se mantiene igual
3. Los kexts base (Lilu, WhateverGreen, RealtekRTL8111, AppleALC) son los mismos
4. Solo necesitamos ajustar SMBIOS, iGPU config, y boot-args para Sonoma

---

*Última actualización: 19 abril 2026*
