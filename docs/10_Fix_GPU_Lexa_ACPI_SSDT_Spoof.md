# 10 — Solución Definitiva: Aceleración Metal en RX 550 Lexa via SSDT ACPI

> **Estado:** ✅ RESUELTO — Metal confirmado activo en macOS Monterey 12.x  
> **Fecha:** 2026-04-14  
> **Horas invertidas:** ~72 horas distribuidas en varios días de iteración

---

## Contexto: El Problema que Nadie Había Resuelto

La **AMD ASRock Phantom Gaming RX 550 2GB GDDR5** usa el chip **Lexa (Device ID: `1002:699F`)**, que nunca recibió soporte nativo de Apple. Todo el mundo en la comunidad hackintosh reportaba que el spoofing a Baffin (`67FF`) funcionaba para identificar la tarjeta, pero el acelerador de hardware (`AMDRadeonX4000_AMDBaffinGraphicsAccelerator`) nunca llegaba a activarse, quedando con `=0` en el IORegistry.

El sistema arrancaba, la tarjeta aparecía en "Acerca de esta Mac" con 2GB y nombre correcto, pero:
- Dock completamente negro y opaco
- Animaciones de ventanas a tirones insoportables
- Sin línea `Metal: Supported` en `system_profiler`
- `ioreg` mostraba `AMDBaffinGraphicsAccelerator=0`

### El Diagnóstico Final

Tras semanas de investigación cruzando múltiples repos de GitHub, Reddit e InsanelyMac, se identificaron dos enfoques de spoofing:

| Método | Nivel | Resultado en Lexa |
|--------|-------|-------------------|
| `DeviceProperties` en `config.plist` | OpenCore (bootloader) | ❌ La tarjeta se identifica pero el driver aborta |
| `SSDT-GPU-SPOOF.aml` (tabla ACPI) | Firmware UEFI/ACPI | ✅ El driver Baffin carga completamente |

**La diferencia crítica:** El método ACPI inyecta el `device-id` **antes** de que el kernel despierte los drivers de hardware. El firmware le "presenta" al SO un dispositivo que ya dice ser Baffin desde el arranque, sin que el driver tenga oportunidad de detectar el verdadero chip subyacente.

El método `DeviceProperties` actúa **después**, cuando el driver ya está a punto de inicializarse y puede detectar la inconsistencia entre el device-id falso y el silicio real.

---

## Referencia: El Repo Que Abrió el Camino

Encontrado mediante búsqueda exhaustiva en GitHub:

- **[dipaksarkar/EFI-GIGABYTE-H510M-H](https://github.com/dipaksarkar/EFI-GIGABYTE-H510M-H)**
  - Hardware: Gigabyte H510M-H + i3 10100 (Comet Lake) + **AMD RX 550 Lexa**
  - macOS: Big Sur, Catalina y posteriores
  - Claim: "Everything works" incluyendo DRM (Netflix, ATV+)
  - Clave: Usa `SSDT-GPU-SPOOF.aml` en lugar de `DeviceProperties`

> ⚠️ **No se puede usar directamente**: el hardware es Comet Lake con una ruta ACPI diferente (`\_SB.PC00.PEG1.PEGP`). Nuestro sistema Haswell B85 usa `\_SB.PCI0.PEG0.PEGP`.

---

## La Solución Paso a Paso

### 1. Desensamblar el SSDT de referencia

```bash
# iasl está incluido dentro de Hackintool.app
IASL=/Applications/Hackintool.app/Contents/Resources/Utilities/iasl

"$IASL" -d EFI-GIGABYTE-H510M-H-main/EFI/OC/ACPI/SSDT-GPU-SPOOF.aml
# Genera: SSDT-GPU-SPOOF.dsl (código fuente legible)
```

El `.dsl` descompilado reveló la estructura y las referencias ACPI del sistema H510M:
```
External (_SB_.PC00, DeviceObj)
External (_SB_.PC00.PEG1.PEGP, DeviceObj)
Scope (\_SB.PC00.PEG1.PEGP) { ... }
Scope (\_SB.PC00) { Method (DTGP ...) }
```

### 2. Identificar la ruta ACPI correcta para Haswell B85

El archivo `System.info` del repo de referencia confirmaba la diferencia:

```
ACPI Path: \_SB.PC00.PEG1.PEGP   ← Comet Lake (H510M-H)
```

Para **Haswell B85**, la ruta estándar es:
```
ACPI Path: \_SB.PCI0.PEG0.PEGP   ← Haswell (B85)
```

Esto también coincide con la ruta PCI confirmada por `system_profiler`:
```
PCI Path: PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)
ACPI:     IOService:/AppleACPIPlatformExpert/PCI0@0/AppleACPIPCI/PEG0@1/IOPP/GFX0@0
```

### 3. Crear el SSDT adaptado (`SSDT-GPU-SPOOF-Haswell.dsl`)

```asl
DefinitionBlock ("", "SSDT", 2, "DRTNIA", "AMDGPU", 0x00001000)
{
    // Rutas ACPI de Haswell B85 — ¡NO las de Comet Lake!
    External (_SB_.PCI0,           DeviceObj)
    External (_SB_.PCI0.PEG0.PEGP, DeviceObj)

    Scope (\_SB.PCI0.PEG0.PEGP)
    {
        If (_OSI ("Darwin"))   // Solo en macOS
        {
            Method (_DSM, 4, NotSerialized)
            {
                Local0 = Package (0x0E)
                {
                    "built-in",          Buffer (One) { 0x00 },
                    "AAPL,slot-name",    Buffer (0x13) { "Internal@0,1,0/0,0" },
                    "@0,AAPL,boot-display", Buffer (0x04) { 0x01, 0x00, 0x00, 0x00 },

                    // ── INYECCIÓN CLAVE ─────────────────────────────────
                    // 0xFF 0x67 0x00 0x00 = little-endian de 0x67FF (Baffin)
                    "device-id",         Buffer (0x04) { 0xFF, 0x67, 0x00, 0x00 },

                    // Desactiva el spoof de WhateverGreen para no duplicar
                    "no-gfx-spoof",      Buffer (0x04) { 0x00, 0x01, 0x00, 0x00 },

                    // ID interno AMD (formato 2 bytes)
                    "ATY,DeviceID",      Buffer (0x02) { 0xFF, 0x67 },

                    "model",             Buffer (0x12) { "AMD Radeon RX 550" }
                }
                DTGP (Arg0, Arg1, Arg2, Arg3, RefOf (Local0))
                Return (Local0)
            }
        }
    }

    // Helper DTGP bajo el nodo raíz PCI0 (Haswell)
    Scope (\_SB.PCI0)
    {
        Method (DTGP, 5, NotSerialized)
        {
            If ((Arg0 == ToUUID ("a0b5b7c6-1318-441c-b0c9-fe695eaf949b")))
            {
                If ((Arg1 == One))
                {
                    If ((Arg2 == Zero)) { Arg4 = Buffer (One) { 0x03 }; Return (One) }
                    If ((Arg2 == One))  { Return (One) }
                }
            }
            Arg4 = Buffer (One) { 0x00 }
            Return (Zero)
        }
    }
}
```

### 4. Compilar el DSL a AML

```bash
"$IASL" SSDT-GPU-SPOOF-Haswell.dsl
# Output: SSDT-GPU-SPOOF-Haswell.aml — 387 bytes, 0 Errors, 0 Warnings
```

### 5. Desplegar en la EFI

```bash
cp SSDT-GPU-SPOOF-Haswell.aml EFI_Monterey/EFI/OC/ACPI/SSDT-GPU-SPOOF.aml
```

### 6. Actualizar `config.plist`

**ACPI → Add**: Registrar el nuevo SSDT
```xml
<dict>
    <key>Comment</key>
    <string>GPU Lexa to Baffin ACPI-level spoof (\_SB.PCI0.PEG0.PEGP Haswell B85)</string>
    <key>Enabled</key>
    <true/>
    <key>Path</key>
    <string>SSDT-GPU-SPOOF.aml</string>
</dict>
```

**DeviceProperties**: Eliminar `device-id` del bloque GPU (el SSDT lo maneja ahora y `no-gfx-spoof` evita que WEG lo duplique)
```xml
<!-- device-id eliminado — ahora lo inyecta el SSDT a nivel ACPI -->
<key>PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)</key>
<dict>
    <key>model</key>
    <string>AMD Radeon RX 550 (Lexa 699F - ACPI SSDT Spoof Active)</string>
</dict>
```

### 7. Reset NVRAM + Reinicio

Obligatorio después de cada cambio en el config.plist: seleccionar **Reset NVRAM** en el picker de OpenCore antes de arrancar.

---

## Verificación: El Veredicto Final

### Antes del SSDT
```
system_profiler SPDisplaysDataType | grep -i metal
→ (sin output — Metal no disponible)

ioreg | grep AMDBaffinGraphicsAccelerator
→ "AMDRadeonX4000_AMDBaffinGraphicsAccelerator"=0
```

### Después del SSDT ✅
```
system_profiler SPDisplaysDataType | grep -i metal
→ Metal: Supported

ioreg | grep AMDRadeonX4000_AMD | grep -v "=0"
→ +-o AMDRadeonX4000_AMDBaffinGraphicsAccelerator
     <registered, matched, active>
  +-o AMDRadeonX4000_AMDAccel2DContext    (múltiples)
  +-o AMDRadeonX4000_AMDAccelDevice       (múltiples)
  +-o AMDRadeonX4000_AMDAccelCommandQueue (múltiples)
  +-o AMDRadeonX4000_AMDAccelSurface      (múltiples)
  +-o AMDRadeonX4000_AMDSIGLContext
  +-o AMDRadeonX4000_AMDCICLContext
```

**Resultado visible en el sistema:**
- ✅ Dock con transparencia y blur nativo
- ✅ Animaciones de ventanas completamente fluidas
- ✅ Minimizar/maximizar sin tirones
- ✅ Mission Control operativo
- ✅ Sistema usable localmente (no solo por Remote Desktop)

---

## Lección Técnica Para la Comunidad

> Si tu RX 550 Lexa (699F) es detectada correctamente (nombre, VRAM) pero `AMDBaffinGraphicsAccelerator=0`, el problema **no es el device-id en sí** — es el **momento y nivel en que se inyecta**.
>
> La inyección vía `DeviceProperties` en OpenCore ocurre demasiado tarde para el driver AMD.  
> La inyección vía `_DSM` en una tabla ACPI ocurre durante la enumeración de hardware del firmware, antes de que el driver inicialice el dispositivo.
>
> **La solución: siempre preferir SSDT sobre DeviceProperties para spoofing de GPU en chips Lexa.**

---

## Archivos Relacionados

| Archivo | Ubicación | Propósito |
|---------|-----------|-----------|
| `SSDT-GPU-SPOOF-Haswell.dsl` | `/` (raíz del repo) | Código fuente del SSDT adaptado |
| `SSDT-GPU-SPOOF-Haswell.aml` | `/` (raíz del repo) | Binario compilado (fuente de verdad) |
| `SSDT-GPU-SPOOF.aml` | `EFI_Monterey/EFI/OC/ACPI/` | El SSDT activo en la EFI |
| `config.plist` | `EFI_Monterey/EFI/OC/` | ACPI/Add apunta a este SSDT |
