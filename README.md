# Hackintosh i7-4790K + RX 550 Lexa — macOS Tahoe (26.x)

![Aceleración 3D Conseguida: Metal Nativo en Tahoe](docs/images/tahoe_victory.jpg)

> [!CAUTION]
> ## ⛔ No copies esta EFI directamente
>
> Este repositorio es una **contribución técnica a la comunidad hackintosh**, no una EFI lista para usar. El autor lo comparte para documentar la solución porque otras personas en la misma situación (RX 550 Lexa sin Metal) no encontraban información clara — y una EFI pública de otro repo fue el punto de partida que permitió encontrar la respuesta.
>
> **Por qué NO deberías copiar y pegar la EFI tal cual:**
> - El `config.plist` contiene un **número de serie (Serial Number), MLB y SystemUUID** generados específicamente para este hardware. Usarlos en otro equipo puede causar conflictos con los servidores de Apple (iMessage, iCloud, activación).
> - La ruta ACPI del GPU (`\_SB.PCI0.PEG0.PEGP`) y el path PCI son **específicos de esta placa B85**. En otro hardware pueden ser completamente distintos.
> - Los kexts de red están configurados para el controlador Realtek de esta placa. El tuyo puede ser diferente.
>
> **Qué SÍ podés (y deberías) hacer:**
> 1. Estudiar la técnica del `SSDT-GPU-SPOOF.aml` documentada en [`docs/10`](docs/10_Fix_GPU_Lexa_ACPI_SSDT_Spoof.md).
> 2. Verificar la ruta ACPI de tu propia GPU con Hackintool (pestaña PCIe).
> 3. Compilar tu propio SSDT adaptado usando el fuente en `scripts/SSDT-GPU-SPOOF-Haswell.dsl` como base.
> 4. Generar tus propios seriales SMBIOS con [GenSMBIOS](https://github.com/corpnewt/GenSMBIOS).

> [!NOTE]
> ## ✅ FUNCIONANDO — Metal GPU Activo en macOS Tahoe (26.4.1)
>
> Tras varios días de investigación y pruebas, el sistema **funciona con aceleración Metal y QE/CI** en **macOS Tahoe 26.4.1 (25E253)**. La GPU renderiza gráficos 3D, transparencias y animaciones con fluidez nativa.
>
> **Hallazgo clave:** en este hardware y esta GPU, el spoofing de la Lexa vía `DeviceProperties` en `config.plist` no logró activar el acelerador. El método que funcionó consistentemente fue la inyección a nivel ACPI mediante `SSDT-GPU-SPOOF.aml` compilado con la ruta correcta del hardware. Al hacerlo así, macOS reconoce la placa como Baffin (`67FF`), habilitando Metal.
>
> **Nota:** Metal activo **no equivale** a soporte multimedia completo — la decodificación de video por hardware (VideoToolbox/AppleGVA) sigue sin funcionar. Ver [limitaciones](#%EF%B8%8F-limitación-conocida-decodificación-de-video-por-hardware).
>
> Ver documentación completa en [`docs/10_Fix_GPU_Lexa_ACPI_SSDT_Spoof.md`](docs/10_Fix_GPU_Lexa_ACPI_SSDT_Spoof.md)

---

> [!IMPORTANT]
> ## ⚠️ Advertencia: RX 550 Lexa requiere configuración especial
>
> La **AMD RX 550 con chip Lexa (Device ID `1002:699F`)** no tiene soporte nativo en macOS. Funciona mediante un spoof a Baffin (`67FF`). En este hardware (Haswell B85), la inyección vía `DeviceProperties` no activó el acelerador — **el método que funcionó fue ACPI/SSDT**. Otros usuarios con variantes distintas de RX 550 podrían tener resultados diferentes. Ver [`docs/10_Fix_GPU_Lexa_ACPI_SSDT_Spoof.md`](docs/10_Fix_GPU_Lexa_ACPI_SSDT_Spoof.md) para entender por qué y cómo reproducirlo.

---

## El Camino Recorrido

Este proyecto no fue una instalación rápida. Fue una investigación real de incompatibilidades de hardware y sus causas raíz:

| Intento | macOS | Resultado |
|---------|-------|-----------|
| **Tahoe (macOS 26) sin spoof ACPI** | Primera prueba | ❌ Sin aceleración, lag crítico |
| **Sequoia (macOS 15) sin spoof ACPI** | Segunda prueba | ❌ Interfaz sin respuesta (catch-22 sin Metal básico) |
| **Monterey + DeviceProperties spoof** | Tercera prueba | ❌ GPU identificada, acelerador `=0` |
| **Monterey + SSDT ACPI spoof** | Progreso sólido | ✅ Metal activo, demostró que el spoof funcionaba |
| **Tahoe (macOS 26.4.1) + SSDT ACPI spoof** | **Aceleración 3D Conseguida** | ✅ Metal activo, sistema fluido. Decode de video pendiente (ver limitaciones) |

La GPU spoofada pasó de fallar repetidamente a mostrar **Metal: Supported** (con drivers Baffin `AMDRadeonX4000` ejecutándose de forma estable). Metal y QE/CI operativos; la decodificación de video por hardware queda como [limitación conocida](#%EF%B8%8F-limitación-conocida-decodificación-de-video-por-hardware).

---

## Especificaciones del Hardware

- **Procesador:** Intel Core i7-4790K (Haswell, 4 núcleos / 8 hilos, 4.0GHz base)
- **Placa Base:** Intel B85 Chipset
- **Memoria RAM:** 16 GB
- **Tarjeta Gráfica:** AMD ASRock Phantom Gaming Radeon RX 550 PHANTOM G R RX550 2GB GDDR5
  - Chip interno: **Lexa (Device ID: `1002:699F`)**
  - Spoofado a: **Baffin (`67FF`)** vía SSDT ACPI — ✅ Metal funcionando
- **Almacenamiento macOS:** SSD SATA 256 GB en caja USB 3.0 externa
- **Red:** Realtek PCIe GbE Family Controller
- **Audio:** High Definition Audio (Realtek)
- **macOS instalado:** Tahoe 26.4.1 (Build 25E253)

---

## Configuración EFI Activa

La EFI funcional fue adaptada para Tahoe. Elementos clave:

| Componente | Valor | Propósito |
|-----------|-------|-----------| 
| **SMBIOS** | `MacPro7,1` | Identidad dGPU-only, compatible con Tahoe |
| **SSDT** | `SSDT-GPU-SPOOF.aml` | Spoof Lexa → Baffin a nivel ACPI |
| **boot-args** | `-radcodec agdpmod=pikera` | Intento de decode AMD (sin efecto confirmado en Lexa spoofada) + salida display |
| **iGPU** | HD 4600 headless (`04001204`) | Declarada pero **sin drivers en Tahoe** (ver limitaciones) |
| **Red** | RealtekRTL8111.kext | Ethernet funcionando |
| **Audio** | AppleALC alcid=1 | Audio funcionando |

---

## ⚖️ Limitación Conocida: Decodificación de Video por Hardware

> [!WARNING]
> ### La decodificación de video por hardware (VideoToolbox/AppleGVA) NO funciona en esta configuración
>
> Aunque Metal y la aceleración 3D de la GPU funcionan **perfectamente**, la decodificación de video por hardware **no está activa**. Esto fue verificado con `ioreg -l | grep -i "AppleGVA"` (sin resultados) y confirmado con mediciones de CPU reales durante la reproducción de video.

### ¿Por qué ocurre?

En un hackintosh Haswell, la decodificación de video por hardware normalmente depende de **Intel QuickSync** (iGPU HD 4600). Aunque la iGPU está configurada en modo headless (`AAPL,ig-platform-id = 04001204`), **Apple eliminó por completo los drivers de Intel HD 4600 (Haswell) a partir de macOS Ventura (13.x)**. En macOS Tahoe, la iGPU está declarada en el config.plist pero macOS no tiene drivers para utilizarla.

El flag `-radcodec` en boot-args intenta forzar la decodificación vía AMD. Sin embargo, la evidencia comunitaria alrededor de la Lexa spoofada a Baffin indica que **no garantiza activar H.264/H.265 por hardware en estas RX 550** — hay reportes concretos donde incluso con spoof correcto la tarjeta sigue sin decode por hardware ni DRM pleno. En esta configuración, `-radcodec` no logra activar el framework AppleGVA. Cuando macOS no encuentra hardware de decodificación disponible, hace **fallback silencioso a decodificación por CPU (software)**.

### Impacto medido (datos reales del sistema)

Mediciones realizadas reproduciéndose un video 4K HDR 60fps en YouTube (Safari) con Activity Monitor:

| Resolución | CPU en `Safari Graphics and Media` | CPU idle del sistema | Cores ocupados en decode |
|---|---|---|---|
| **1080p** | ~50-80% | ~80% | ~0.5-1 core |
| **1440p (2K)** | ~87% | ~72% | ~1 core |
| **2160p (4K)** | **~227%** | **~53%** | **~2.8 cores** |

*Con decodificación por hardware activa, `Safari Graphics and Media` consumiría ~5-10% CPU en cualquier resolución.*

### ¿Es crítico para el uso diario?

**No, para la mayoría de los casos el impacto es tolerable.** El i7-4790K tiene 8 hilos lógicos (800% CPU total) y compensá con potencia bruta:

| Escenario de uso | Impacto | Veredicto |
|---|---|---|
| Navegar, programar, uso general | Sin impacto | ✅ Perfecto |
| YouTube/video a 1080p de fondo | ~1 core ocupado | ✅ Imperceptible |
| YouTube 4K | ~2.8 cores ocupados | 🟡 Funcional, CPU trabaja más |
| Video 4K + máquinas virtuales simultáneas | ~5-6 cores comprometidos | 🔴 Ajustado |
| DRM (Netflix/Apple TV+ en Safari) | No funciona | ❌ Usar Chrome/Firefox |

### Estado actual y próximos pasos

**Actualmente en Tahoe (26.x)** — Metal y aceleración 3D funcionan de forma nativa sin OCLP. Esto **no equivale** a soporte completo del stack multimedia: la decodificación de video por hardware (VideoToolbox/AppleGVA) no está activa. El sistema es funcional para uso general y el i7-4790K compensa con potencia bruta en decodificación por software.

### Roadmap: Escenarios evaluados

El objetivo es que este hackintosh funcione como una **máquina secundaria sólida**. Para el decode de video por hardware se necesitaría reactivar la iGPU Intel HD 4600 (QuickSync), lo cual requiere drivers que Apple eliminó a partir de Ventura.

| Escenario | Soporte Metal | HW Decode | OCLP requerido | Madurez | Valoración |
|-----------|:---:|:---:|:---:|---|---|
| **Tahoe (actual)** | ✅ Nativo | ❌ | No | Configuración validada | Ideal si el decode por software es aceptable |
| **Sonoma** | ✅ con OCLP | 🟡 Posible con OCLP | Sí | Patching Legacy Metal maduro y estable | **Candidato principal** si se busca HW decode |
| **Sequoia** | ✅ con OCLP | 🟡 Posible con OCLP | Sí | Soporte OCLP confirmado, menor madurez que Sonoma | Alternativa viable |
| **Monterey** | ✅ Nativo | ✅ Nativo | No | Última versión con drivers Haswell nativos | Baseline de control para verificar HW decode |

#### Sobre OCLP y Tahoe

El soporte oficial y estable de OCLP para macOS Tahoe **sigue sin confirmarse**. Existen nightlies y forks como OCLP-Plus, pero con resultados mixtos y sin el grado de confianza que tuvo Sonoma o Sequoia. No es prudente contar con esto como solución a corto plazo.

#### Decisión actual

Tras evaluar el impacto real con benchmarks (ver tablas arriba), la configuración actual de Tahoe **se mantiene como daily driver**. El decode por software en 1080p/1440p consume menos de 1 core y es imperceptible en uso cotidiano. Solo en escenarios de 4K simultáneo con VMs o compilación pesada justificaría reconsiderar un downgrade — en cuyo caso, **Sonoma sería el candidato principal** por la madurez de su patching Legacy Metal.

> [!NOTE]
> ### TODO — Evaluación pendiente
>
> - [ ] Benchmark de CPU prolongado (video 4K + compilación + VM) para medir impacto en workloads exigentes
> - [ ] Monitorear si OCLP anuncia soporte oficial para Tahoe
> - [ ] Si se decide bajar: probar Sonoma en partición separada con SMBIOS `iMac14,2`, iGPU headless según [guía Dortania Haswell](https://dortania.github.io/OpenCore-Install-Guide/config.plist/haswell.html), y OCLP root patches
> - [ ] Verificar activación de AppleGVA y comparar CPU usage con/sin HW decode
> - [ ] Decisión final: ¿la ganancia justifica perder SIP, updates directos y la última versión de macOS?
>
> El criterio es pragmático: si la diferencia en multitarea real es considerable, se baja a Sonoma. Si es marginal para el uso diario, no vale la pena el mantenimiento extra de OCLP.

---

## Para Reproducir Este Hackintosh

1. Instalar macOS usando el USB con una EFI funcional. Gracias al Spoof ACPI, la aceleración es **totalmente nativa (no se requiere OCLP)**.
2. En OpenCore picker: **Reset NVRAM** antes del primer arranque tras cambios
3. Verificar que Metal está activo:
   ```bash
   system_profiler SPDisplaysDataType | grep -i metal
   # → Metal: Supported
   
   ioreg -l | grep "AMDBaffinGraphicsAccelerator" | grep -v "=0"
   # → registered, matched, active
   ```
4. Verificar estado de decodificación de video por hardware:
   ```bash
   ioreg -l | grep -i "AppleGVA"
   # → Sin output = decode por software (esperado en Tahoe con Haswell)
   ```
5. **Resumen Visual y Validación Final:** Incluimos un script que genera un reporte a color del estado del hardware. Ejecutá en tu terminal:
   ```bash
   bash scripts/show_hardware_status.sh
   ```
6. Si el acelerador no carga: asegurarse de que `SSDT-GPU-SPOOF.aml` está en `EFI/OC/ACPI/` **y** declarado en `config.plist → ACPI → Add`

---

## ¿Tenés una RX 550 Lexa y encontraste otra solución?

Este repositorio es **público**. Si lograste hacer funcionar Metal con otro método o en otra versión de macOS, abrí un **[Issue](../../issues)** describiendo:
- Versión de macOS
- Configuración de tu EFI (especialmente ACPI y DeviceProperties)
- Output de `ioreg -l | grep -i accelerator`
- Output de `ioreg -l | grep -i "AppleGVA"` (para verificar HW decode)

---

## Estructura de Documentación (`/docs`)

| Nº | Documento | Contenido |
|----|-----------|-----------| 
| 01-05 | Configuración base | Extracción de hardware, preparación EFI inicial |
| 06 | Preparación USB y Flasheo | Proceso de creación del instalador USB |
| 07 | Análisis EFIs | Comparativa EFI personalizada vs. Olarila |
| 08 | Troubleshooting Tahoe | Por qué Tahoe fue descartado |
| 09 | Veredicto GPU y Downgrade a Monterey | La investigación comunitaria y la decisión técnica |
| **10** | **Fix GPU Lexa — SSDT ACPI Spoof** | **La solución definitiva documentada paso a paso** |
| **11** | **Limitaciones: HW Decode y análisis iGPU** | **Análisis técnico del decode por hardware y evaluación de escenarios macOS** |
