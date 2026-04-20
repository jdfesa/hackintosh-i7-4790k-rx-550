# EFI Sonoma — Hackintosh i7-4790K + RX 550 Lexa

> **Estado**: ⚠️ Parcialmente funcional — macOS Sonoma 14.8.5 bootea, display OK, pero **hardware video decode no activo** (AppleGVA no carga con SMBIOS `iMac14,2`). Migración a `MacPro7,1` pendiente.

EFI adaptada desde `EFI_Tahoe` según la [guía Dortania para Desktop Haswell](https://dortania.github.io/OpenCore-Install-Guide/config.plist/haswell.html).

**Ver [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para registro completo de problemas encontrados y soluciones probadas.**

---

## Hardware

| Componente | Especificación |
|-----------|----------------|
| CPU | Intel Core i7-4790K (Haswell, 4C/8T) |
| Placa Base | Gigabyte B85 |
| dGPU | AMD RX 550 Lexa → Spoof ACPI a Baffin (`67FF`) |
| iGPU | Intel HD 4600 → headless (`04001204`) |
| Audio | Realtek HD (`alcid=1`) |
| Red | Realtek PCIe GbE |

---

## Qué funciona ✅

- macOS Sonoma 14.8.5 instalación completa
- RX 550 Lexa con spoof Baffin: Metal, display 2560x1440 QHD a 60Hz HDMI
- Audio, red, USB
- VDADecoderChecker: "Hardware acceleration is fully supported" (nota: el decoder real no se activa, ver abajo)

## Qué NO funciona ❌

- **Hardware video decode**: AppleGVA framework no carga → video 4K se decodifica por CPU (~160-220% CPU)
- **OCLP root patches**: Causan login loop por conflicto dual GPU headless (documentado en [TROUBLESHOOTING.md](TROUBLESHOOTING.md))

---

## Boot-args actuales

```
-v keepsyms=1 debug=0x100 alcid=1 agdpmod=pikera amfi_get_out_of_my_way=0x1 ipc_control_port_options=0 revpatch=sbvmm -no_compat_check shikigva=80 unfairgva=1 -radcodec -wegnoigpu
```

| Flag | Propósito |
|------|-----------|
| `-v` | Verbose boot |
| `keepsyms=1` | Preservar símbolos kernel para debug |
| `debug=0x100` | No rebootear en kernel panic |
| `alcid=1` | AppleALC layout Realtek |
| `agdpmod=pikera` | Display output en dGPU AMD |
| `amfi_get_out_of_my_way=0x1` | Deshabilita AMFI (era para OCLP) |
| `ipc_control_port_options=0` | Fix crashes apps (era para OCLP) |
| `revpatch=sbvmm` | Bypass board-id en SMBIOS no soportado |
| `-no_compat_check` | Desactiva check compatibilidad hardware |
| `shikigva=80` | Forzar DRM decode vía AMD (inactivo sin AppleGVA) |
| `unfairgva=1` | DRM hardware AMD (inactivo sin AppleGVA) |
| `-radcodec` | Codec Radeon (inactivo sin AppleGVA) |
| `-wegnoigpu` | Ocultar iGPU a macOS |

---

## Config actual

| Parámetro | Valor | Nota |
|-----------|-------|------|
| SMBIOS | `iMac14,2` | **Causa probable del fallo de AppleGVA** |
| ig-platform-id | `04001204` | Headless, 0 conectores |
| csr-active-config | `FF0F0000` | SIP full disable |
| SecureBootModel | `Disabled` | |

---

## Próximo paso: Migrar a MacPro7,1

La [EFI de referencia](../references/EFI-Haswell-RX550-Lexa/) con hardware casi idéntico (i5-4590 + RX 550 Lexa) funciona con **DRM y encoders** usando `MacPro7,1`. La hipótesis es que `MacPro7,1` (sin iGPU) fuerza a macOS a cargar AppleGVA con el path de decodificación AMD.

Ver [TROUBLESHOOTING.md § Próximo paso](TROUBLESHOOTING.md#5-próximo-paso-migrar-a-macpro71) para el plan detallado.

---

## BIOS (Gigabyte B85)

| Setting | Valor |
|---------|-------|
| Primary Display | PEG |
| Internal Graphics | Enabled |

---

## MaLd0n.aml — No tocar

SSDT monolítico de Olarila: EC + USBX + PLUG + SBUS/MCHC + XHC RHUB. No se splitea ni renombra. Ver [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para justificación.

---

## Scripts de soporte

| Script | Uso |
|--------|-----|
| `scripts/generate_smbios.py` | Descarga macserial y genera seriales para cualquier SMBIOS |
| `scripts/apply_sonoma_config.py` | Aplica cambios al config.plist con backup automático |

## Origen

Adaptada desde `EFI_Tahoe` · Referencia consultada: `EFI-Haswell-RX550-Lexa/` (i5-4590, MacPro7,1) · Seriales generados con macserial

*Última actualización: 20 abril 2026*
