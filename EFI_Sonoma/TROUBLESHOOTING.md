# Troubleshooting — EFI Sonoma (Haswell + RX 550 Lexa)

> Registro de problemas encontrados, soluciones probadas, y lecciones aprendidas durante la configuración de macOS Sonoma 14.8.5 en un i7-4790K con RX 550 Lexa (spoof Baffin).

---

## Índice

- [1. OCLP Login Loop (WindowServer crash)](#1-oclp-login-loop-windowserver-crash)
- [2. Safe Mode no funciona con Shift](#2-safe-mode-no-funciona-con-shift)
- [3. SIP — De parcial a completo disable](#3-sip--de-parcial-a-completo-disable)
- [4. AppleGVA no carga — Decode por CPU](#4-applegva-no-carga--decode-por-cpu)
- [5. Próximo paso: Migrar a MacPro7,1](#5-próximo-paso-migrar-a-macpro71)

---

## 1. OCLP Login Loop (WindowServer crash)

### Síntoma

Después de aplicar OCLP 2.4.1 root patches ("Graphics: Intel Haswell"), el sistema bootea hasta la pantalla de login, se ingresa la contraseña, la pantalla hace un glitch y vuelve al login. Loop infinito.

### Causa raíz

OCLP instala el **stack completo de display Intel Haswell**: `AppleIntelFramebufferAzul.kext` + `AppleIntelHD5000Graphics.kext` + bundles GL/MTL/VA + parches de Metal/compilers. No existe opción "compute-only".

Con nuestra configuración **dual GPU (iGPU headless + dGPU AMD)**:
- La iGPU tiene `ig-platform-id = 04001204` (0 conectores, headless)
- Los kexts de OCLP intentan inicializar conectores de display en la iGPU
- WindowServer no puede resolver el pipeline entre AMD (con monitor) e Intel (con drivers que dicen que debería tener monitor pero no tiene)
- WindowServer crashea → loop

### Intentos fallidos

| Intento | Qué hicimos | Resultado |
|---------|-------------|-----------|
| **1. OCLP directo** | Aplicar root patches con config mínima (solo `ig-platform-id`) | ❌ Login loop |
| **2. Framebuffer patches** | Agregar `framebuffer-patch-enable`, `framebuffer-stolenmem`, `framebuffer-fbmem` | ❌ Login loop idéntico |

### Por qué funciona en otros equipos

- **Macs reales (iMac14,2)**: La iGPU ES el display principal → OCLP instala drivers de display → funcionan porque hay monitor conectado
- **Hackintosh con SOLO iGPU**: Misma situación, iGPU maneja display
- **Hackintosh dual GPU (headless iGPU + dGPU)**: OCLP instala drivers de display para una GPU que tiene 0 conectores → crash

### Recuperación

Para recuperar el sistema tras un login loop por OCLP:

1. Agregar `-x` a `boot-args` en `config.plist` (fuerza Safe Mode vía OpenCore)
2. Copiar config.plist al USB
3. Bootear → Safe Mode (fondo blanco, dock negro = normal)
4. OCLP → Post-Install Root Patch → **Revert Root Patches**
5. Apagar, quitar `-x` del config.plist, copiar de nuevo
6. Bootear normal

> **⚠️ IMPORTANTE**: Safe Mode vía tecla Shift NO funciona en este setup. Muestra el símbolo prohibido porque el check de SMBIOS se re-ejecuta en Safe Mode. Usar `-x` en boot-args es la única forma.

### Alternativa mencionada (no probada)

Un usuario en foros recomienda **macOS Sequoia** (no Sonoma) con el mismo setup iMac14,2 + OCLP. Afirma que los patches de Sequoia manejan mejor el dual GPU. No verificado.

### Conclusión

**OCLP + iGPU Haswell headless + dGPU AMD = incompatible en Sonoma.** No hay modo "compute-only" en OCLP para la iGPU.

---

## 2. Safe Mode no funciona con Shift

### Síntoma

Mantener Shift durante el boot muestra el símbolo prohibido (🚫) en lugar de entrar a Safe Mode.

### Causa

Safe Mode vía teclado re-ejecuta la verificación de compatibilidad de SMBIOS. `iMac14,2` fue eliminado del soporte nativo desde macOS Ventura. Los boot-args (`revpatch=sbvmm`, `-no_compat_check`) que normalmente bypasean este check son ignorados en Safe Mode por teclado.

### Solución

Usar `-x` en boot-args del `config.plist`:

```
boot-args: -v -x keepsyms=1 debug=0x100 ...
```

`-x` fuerza Safe Mode a nivel de OpenCore, antes del check de compatibilidad.

---

## 3. SIP — De parcial a completo disable

### Historial de cambios

| Valor | Hex | Estado |
|-------|-----|--------|
| `AwgAAA==` | `0x803` | Parcial — original para OCLP |
| `/w8AAA==` | `0xFFF` | **Completo disable — actual** |

### Por qué full disable

- OCLP necesita SIP parcial (`0x803`) mínimo
- Para Yabai scripting addition se necesita `task_for_pid` que solo está en full disable
- En un hackintosh bunker sin updates automáticos, el riesgo real de seguridad es mínimo
- SIP es 100% reversible: cambiar el valor y reiniciar

### Consecuencias de SIP deshabilitado

- `/System` es escribible (OCLP lo necesita)
- No protección contra kexts no firmados
- Kernel debugger habilitado
- NVRAM firmware desprotegida
- **NO brickea hardware** — SIP es software, reversible siempre

---

## 4. AppleGVA no carga — Decode por CPU

### Síntoma

Tras agregar flags AMD (`shikigva=80 unfairgva=1 -radcodec`) inspirados en la [EFI de referencia](../EFI-Haswell-RX550-Lexa/), el sistema bootea correctamente pero:

- `ioreg -l | grep -i "AppleGVA"` → **vacío** (framework no cargado)
- `VDADecoderChecker` → "Hardware acceleration is fully supported" (falso positivo)
- Activity Monitor → **Safari Graphics and Media: ~160-220% CPU** durante video 4K
- La decodificación sigue siendo por CPU, no por GPU

### Flags probados

```
shikigva=80 unfairgva=1 -radcodec -wegnoigpu
```

| Flag | Propósito | Resultado |
|------|-----------|-----------|
| `shikigva=80` | Forzar DRM decode por AMD (documentado Dortania) | ❌ AppleGVA no carga |
| `unfairgva=1` | Habilitar DRM hardware AMD | ❌ Sin efecto |
| `-radcodec` | Activar codec Radeon | ❌ Sin efecto |
| `-wegnoigpu` | Ocultar iGPU de macOS | ❌ Sin efecto |

### Causa raíz identificada

La diferencia con la EFI de referencia que **sí funciona**:

| | EFI Referencia ✅ | Nuestra EFI ❌ |
|---|---|---|
| **SMBIOS** | `MacPro7,1` | `iMac14,2` |
| **iGPU en DeviceProperties** | No tiene | Sí (headless) |
| **CustomSMBIOSGuid** | `true` | `false` |
| **UpdateSMBIOSMode** | `Custom` | `Create` |

Con `MacPro7,1`, macOS asume que **no hay iGPU** (es un Xeon) y carga AppleGVA con el path de decodificación AMD. Con `iMac14,2`, macOS busca la iGPU para decode → no encuentra drivers (removidos en Sonoma) → fallback a CPU.

### Forzar AMD decoder (post-boot)

Estos comandos no resolvieron el problema de fondo, pero están documentados para referencia:

```bash
defaults write com.apple.AppleGVA gvaForceAMDAVCDecode -boolean yes
defaults write com.apple.AppleGVA gvaForceAMDKE -boolean yes
```

---

## 5. Próximo paso: Migrar a MacPro7,1

### Plan pendiente

Para lograr hardware video decode vía AMD en Sonoma, se necesita replicar la EFI de referencia más fielmente:

1. **SMBIOS**: Cambiar de `iMac14,2` a `MacPro7,1`
2. **Generar nuevos seriales**: `macserial -m MacPro7,1`
3. **Quitar iGPU de DeviceProperties**: Eliminar la entrada `PciRoot(0x0)/Pci(0x2,0x0)` o dejarla vacía
4. **CustomSMBIOSGuid**: Cambiar a `true`
5. **UpdateSMBIOSMode**: Cambiar a `Custom`
6. **Mantener boot-args**: `shikigva=80 unfairgva=1 -radcodec` (ya confirmado en EFI referencia)
7. **Quitar flags innecesarios**: `amfi_get_out_of_my_way=0x1`, `ipc_control_port_options=0` (eran para OCLP)
8. **Verificar**: `ioreg -l | grep -i "AppleGVA"` debe devolver resultados

### Alternativo: Instalar Sequoia + OCLP

Si `MacPro7,1` no da resultados con AppleGVA:
- Instalar macOS Sequoia
- SMBIOS `iMac14,2`
- Aplicar OCLP root patches para iGPU Haswell
- Este camino fue recomendado por un usuario con hardware similar

### Alternativo: macOS Monterey (nativo)

Monterey 12.x es la **última versión con drivers nativos Intel HD 4600**:
- QuickSync nativo sin OCLP
- Ambas GPUs funcionan nativamente
- Sin SIP disable, sin hacks
- Trade-off: fin de security updates (12.7.6, sept 2024)

---

## Resumen de config.plist actual

```
SMBIOS: iMac14,2
ig-platform-id: 04001204 (headless)
csr-active-config: FF0F0000 (SIP full disable)
SecureBootModel: Disabled
boot-args: -v keepsyms=1 debug=0x100 alcid=1 agdpmod=pikera
           amfi_get_out_of_my_way=0x1 ipc_control_port_options=0
           revpatch=sbvmm -no_compat_check
           shikigva=80 unfairgva=1 -radcodec -wegnoigpu
```

### Estado actual del sistema

- ✅ macOS Sonoma 14.8.5 corriendo estable
- ✅ RX 550 Lexa → Baffin spoof con Metal
- ✅ Display 2560x1440 QHD a 60Hz HDMI
- ❌ Hardware video decode no activo (AppleGVA no carga)
- ❌ OCLP root patches incompatibles con dual GPU headless
- 🔜 Migración a MacPro7,1 pendiente para activar decode AMD

---

## Referencias

- [Dortania: Fixing DRM](https://dortania.github.io/OpenCore-Post-Install/universal/drm.html)
- [Dortania: Haswell config](https://dortania.github.io/OpenCore-Install-Guide/config.plist/haswell.html)
- [WhateverGreen DRM Chart](https://github.com/acidanthera/WhateverGreen/blob/master/Manual/FAQ.Chart.md)
- [OCLP Supported Models](https://dortania.github.io/OpenCore-Legacy-Patcher/MODELS.html)
- [OCLP Patch Explanation](https://dortania.github.io/OpenCore-Legacy-Patcher/PATCHEXPLAIN.html)
- [MacRumors: Sonoma OCLP thread](https://forums.macrumors.com/threads/macos-14-sonoma-on-unsupported-macs-thread.2391630/)
- EFI referencia: `EFI-Haswell-RX550-Lexa/` (i5-4590, RX 550 Lexa 4GB, MacPro7,1)

*Última actualización: 20 abril 2026*
