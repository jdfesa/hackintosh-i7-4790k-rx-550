# EFI Sonoma — Hackintosh i7-4790K + RX 550 Lexa

> **Estado**: ✅ Funcional — Instalador de macOS Sonoma 14.8.5 booteando correctamente.

EFI adaptada desde `EFI_Tahoe` según la [guía Dortania para Desktop Haswell](https://dortania.github.io/OpenCore-Install-Guide/config.plist/haswell.html), configurada para macOS Sonoma 14.8.5 + OCLP 2.4.1 root patches.

---

## Hardware

| Componente | Especificación |
|-----------|----------------|
| CPU | Intel Core i7-4790K (Haswell, 4C/8T) |
| Placa Base | Gigabyte B85 |
| dGPU | AMD RX 550 Lexa → Spoof ACPI a Baffin (`67FF`) |
| iGPU | Intel HD 4600 → headless compute + QuickSync |
| Audio | Realtek HD (`alcid=1`) |
| Red | Realtek PCIe GbE |

## ¿Por qué Sonoma?

Tahoe funciona con Metal, pero **no tiene decodificación de video por hardware** (Apple eliminó drivers HD 4600 desde Ventura). Sonoma 14.8.5 + OCLP permite restaurar los drivers de iGPU Haswell para QuickSync.

| Factor | Tahoe (actual) | Sonoma (esta EFI) |
|--------|---------------|-------------------|
| Metal / GPU | ✅ Nativo | ✅ Nativo |
| QuickSync (HW decode) | ❌ Software (~2.8 cores 4K) | ✅ Via OCLP root patches |
| SIP | ✅ Habilitado | ⚠️ Parcial (requerido por OCLP) |
| Updates | ✅ Directos | ⚠️ Manuales, verificar OCLP |

---

## Cambios respecto a EFI Tahoe

| Parámetro | Tahoe | Sonoma | Razón |
|-----------|-------|--------|-------|
| SMBIOS | `MacPro7,1` | `iMac14,2` | Perfil Haswell para OCLP |
| BoardProduct | `Mac-27AD2F918AE68F61` | `Mac-27ADBB7B4CEE8E61` | Match iMac14,2 |
| boot-args | `-radcodec amfi=0x80 watchdog=0 dk.e1000=0 e1000=0` | `amfi_get_out_of_my_way=0x1 ipc_control_port_options=0 revpatch=sbvmm -no_compat_check` | OCLP + compat bypass |
| CustomSMBIOSGuid | `true` | `false` | Estándar Dortania |
| UpdateSMBIOSMode | `Custom` | `Create` | Estándar Dortania |
| XhciPortLimit | `true` | `false` | Roto en macOS 11.3+ |
| Seriales | MacPro7,1 | Generados para iMac14,2 | GenSMBIOS/macserial |

**Sin cambio**: `AAPL,ig-platform-id = 04001204` (headless) · `csr-active-config = 03080000` · `SecureBootModel = Disabled` · `SSDT-GPU-SPOOF.aml` · Todos los kexts

---

## Boot-args

```
-v keepsyms=1 debug=0x100 alcid=1 agdpmod=pikera amfi_get_out_of_my_way=0x1 ipc_control_port_options=0 revpatch=sbvmm -no_compat_check
```

| Flag | Propósito |
|------|-----------|
| `-v` | Verbose boot |
| `keepsyms=1` | Preservar símbolos kernel para debug |
| `debug=0x100` | No rebootear en kernel panic |
| `alcid=1` | AppleALC layout Realtek |
| `agdpmod=pikera` | Display output en dGPU AMD |
| `amfi_get_out_of_my_way=0x1` | **OCLP** — deshabilita AMFI para root patches |
| `ipc_control_port_options=0` | Fix crashes Skype/WhatsApp/Spotify |
| `revpatch=sbvmm` | **Bypass board-id** — fuerza modo VMM para SMBIOS no soportado |
| `-no_compat_check` | **Bypass boot.efi** — desactiva check de compatibilidad hardware |

---

## Problema resuelto: Símbolo 🚫 (Prohibited Sign)

Al intentar bootear el instalador de Sonoma con SMBIOS `iMac14,2`, macOS mostraba el símbolo prohibido con `support.apple.com/mac/startup`.

**Causa**: `iMac14,2` fue eliminado del soporte nativo en macOS Ventura. El check de compatibilidad de `boot.efi` ocurre **antes** de que carguen los kexts, por lo que `RestrictEvents.kext` (que tiene `revpatch=sbvmm` en NVRAM) no alcanzaba a parchear el board-id a tiempo.

**Fix**: Agregar `revpatch=sbvmm` y `-no_compat_check` directamente en los boot-args (línea 591 del config.plist). Así el bypass se aplica desde el nivel de firmware, antes del check de boot.efi.

---

## MaLd0n.aml — No tocar

SSDT monolítico de Olarila que combina: EC + USBX + PLUG (plugin-type=1) + SBUS/MCHC + XHC RHUB.

**No se splitea ni renombra**. Las rutas ACPI internas están compiladas para este hardware, coexiste con SSDT-GPU-SPOOF sin conflictos, y cualquier cambio puede causar boot failures. Si funciona y el riesgo de romper supera el beneficio, no se toca.

---

## BIOS (Gigabyte B85)

Opciones verificadas en `Chipset → Graphics Configuration`:

| Setting | Valor |
|---------|-------|
| Primary Display | PEG |
| Internal Graphics | Enabled |

> DVMT Pre-Allocated e iGPU Multi-Monitor no encontrados en esta BIOS. WhateverGreen.kext maneja el framebuffer automáticamente.

---

## Post-instalación

1. Copiar EFI del USB al SSD interno
2. Abrir **OCLP 2.4.1** → Post-Install Root Patch → Start Root Patching
3. Reiniciar
4. Verificar:

```bash
# Metal
system_profiler SPDisplaysDataType | grep -i metal

# iGPU reconocida
system_profiler SPDisplaysDataType

# AppleGVA (post OCLP)
ioreg -l | grep -i "AppleGVA"
```

## Estrategia Bunker

- **Deshabilitar updates automáticos** en System Settings
- **Nunca actualizar macOS** sin verificar compatibilidad OCLP
- **Re-aplicar OCLP patches** tras cada update
- **Backup de EFI funcional** siempre en el repo

---

## Scripts de soporte

| Script | Uso |
|--------|-----|
| `scripts/generate_smbios.py` | Descarga macserial y genera seriales para cualquier SMBIOS |
| `scripts/apply_sonoma_config.py` | Aplica todos los cambios al config.plist con backup automático |

## Origen

Adaptada desde `EFI_Tahoe` · Referencia consultada: `Ventura-Hackintosh-Haswell-EFI/` (i5-4670, OC 0.9.4) · Seriales validados en checkcoverage.apple.com ✅

*Última actualización: 20 abril 2026*
