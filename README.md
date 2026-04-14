# Hackintosh i7-4790K + RX 550 (Lexa)

> [!CAUTION]
> ## 🚫 VEREDICTO FINAL — GPU Incompatible con macOS (2026-04-14)
>
> Tras **semanas de investigación intensiva, múltiples instalaciones limpias y decenas de combinaciones de configuración**, hemos llegado a una conclusión técnica irrefutable:
>
> ### ❌ La AMD RX 550 ASRock Phantom Gaming (Lexa 699F) es incompatible con macOS
>
> La GPU en cuestión es la **AMD ASRock Phantom Gaming Radeon RX 550 PHANTOM G R RX550 2GB GDDR5**, cuyo chip interno es el **módulo Lexa (Device ID: 1002:699F)**. Este módulo **nunca recibió soporte de Apple** en ninguna versión de macOS, a diferencia de su hermano Baffin (67FF) que sí es compatible de forma nativa.
>
> **Si tienes una tarjeta RX 550 y estás buscando usarla en macOS: verifica primero si tu modelo usa el chip Lexa o Baffin.** El módulo Lexa es un callejón sin salida. El módulo Baffin funciona.

---

> [!NOTE]
> ## 📣 ¿Encontraste una solución? ¡Contribuye!
>
> Este repositorio está **abierto al público**. Si has llegado aquí porque tienes hardware similar y lograste hacer funcionar una RX 550 Lexa (699F) en macOS con aceleración Metal real, **nos encantaría saberlo**.
>
> Por favor abre un **[Issue en GitHub](../../issues)** describiendo:
> - La versión exacta de macOS que usaste
> - Tu configuración de OpenCore (especialmente `DeviceProperties`)
> - El resultado de `ioreg -l | grep -i accelerator` (buscando `AMDRadeonX4000_AMDBaffinGraphicsAccelerator=1`)
> - Cualquier kext especial o parche de kernel que hayas aplicado
>
> Este proyecto representó muchas horas de trabajo voluntario. Cualquier aporte de la comunidad sería invaluable.

---

## El Problema Central: ¿Qué es el módulo Lexa y por qué no funciona?

La serie RX 550 de AMD viene en **dos variantes de chip internas completamente distintas**:

| Chip | Device ID | Soporte macOS | Rendimiento |
|------|-----------|-------------|-------------|
| **Baffin** | `0x67FF` | ✅ Soportado nativamente en Polaris | Pleno Metal, plug-and-play |
| **Lexa** | `0x699F` | ❌ Nunca soportado por Apple | Sin Metal, modo VESA solamente |

El problema es que **visualmente las dos tarjetas son idénticas** desde fuera. Muchos vendedores y listings online no especifican cuál es cuál, y el usuario no lo descubre hasta que intenta instalar macOS.

## Evidencia Técnica Irrefutable

### Prueba 1: `system_profiler SPDisplaysDataType`
La tarjeta es **detectada y mostrada correctamente** en "Acerca de esta Mac". El spoof de Device ID funciona a nivel de identificación:
```
AMD Radeon RX 550 (Lexa 699F Spoofed to Baffin 67FF)
  VRAM (Total): 2 GB
  Vendor: AMD (0x1002)
  Device ID: 0x67ff      ← El spoof funciona para el reconocimiento
```
Sin embargo, **no aparece ninguna línea de `Metal:`**. En una GPU funcionando correctamente aparecería `Metal: Supported, Metal Family: Metal GPUFamily Mac 2`. Su ausencia confirma el modo VESA.

### Prueba 2: `ioreg -l | grep -i accelerator`
Este es el veredicto definitivo. La línea clave del output fue:
```
"AMDRadeonX4000_AMDBaffinGraphicsAccelerator"=0
```
**`=0` significa cero instancias activas.** El driver Baffin intentó iniciarse, habló con el chip en "lenguaje Baffin", el chip Lexa respondió de forma incompatible y el driver abortó silenciosamente. El acelerador nunca arrancó.

En un sistema con Metal funcional, esa línea diría `=1`.

### Síntomas en pantalla
- Dock completamente negro y opaco (sin transparencias)
- Animaciones de ventanas a tirones severos
- Imposibilidad de reproducir protectores de pantalla
- Interfaz de OCLP en blanco (catch-22: OCLP necesita Metal mínimo para renderizar su propio UI)
- Sistema utilizable vía Remote Desktop pero con rendimiento inaceptable para uso local

## Itinerario de Intentos Realizados

Todo fue intentado de forma metódica, documentado en la carpeta `/docs`:

1. **Tahoe (macOS 26):** Instalado. Sin aceleración. Lag crítico. Descartado.
2. **Sequoia (macOS 15):** Instalado. Sin Metal. OCLP en blanco por falta de aceleración básica (catch-22). Descartado.
3. **Monterey (macOS 12):** Instalado. Drivers Polaris nativos presentes pero **el acelerador Baffin no carga** porque el chip Lexa no es compatible a nivel de silicio. Estado final: modo VESA.
4. **Spoofing Device-ID a 67FF (Baffin):** Aplicado correctamente en todas las pruebas vía `DeviceProperties` en `config.plist`. Funciona a nivel de identificación, falla a nivel de driver.
5. **Boot-args especializados:** `-radcodec`, `agdpmod=pikera`, `unfairgva=1`. Probados. Sin efecto sobre la carga del acelerador.
6. **OCLP Root Patches en Sequoia:** La interfaz del parcheador se mostraba en blanco por la falta de Metal, impidiendo aplicar los parches (catch-22 irresolvible).
7. **EFI Híbrida (base Olarila + spoofing personalizado):** Creada y refinada. Resolvió el problema de red y audio. No resolvió la GPU.
8. **Múltiples SMBIOS:** `iMac18,3`, `iMac14,2`, `MacPro7,1`. Ninguno cambió el comportamiento del acelerador.
9. **iGPU en modo Headless (`04001204`):** Configurada para asistir la decodificación. Mejora mínima, no resuelve Metal.

## GPUs Recomendadas como Reemplazo

Si tienes este hardware y quieres macOS funcionando al 100%, reemplaza la GPU:

| GPU | Chip | Precio aprox. (2ª mano) | Soporte macOS |
|-----|------|------------------------|---------------|
| **RX 560 4GB** | Baffin | ~20-35 USD | ✅ Nativo, hasta Sonoma |
| **RX 570 4/8GB** | Ellesmere | ~30-50 USD | ✅ Nativo, hasta Sonoma |
| **RX 580 8GB** | Ellesmere | ~40-70 USD | ✅ Nativo, la más recomendada |
| **RX 6600 / 6600 XT** | Navi 23 | ~80-130 USD | ✅ Nativo, hasta macOS reciente |

> [!IMPORTANT]
> Al comprar una RX 550 de segunda mano, verifica explícitamente que sea **Baffin (Device ID 67FF)** y no **Lexa (Device ID 699F)**. Usa GPU-Z en Windows para confirmarlo antes de pagar.

---

## Especificaciones del Hardware

- **Procesador:** Intel Core i7-4790K (Haswell, 4 núcleos / 8 hilos, 4.0GHz base)
- **Placa Base:** Intel B85 Chipset
- **Memoria RAM:** 16 GB
- **Tarjeta Gráfica:** AMD ASRock Phantom Gaming Radeon RX 550 PHANTOM G R RX550 2GB GDDR5
  - Chip interno: **Lexa (Device ID: 1002:699F)** ← **INCOMPATIBLE con macOS**
- **Almacenamiento macOS:** SSD SATA 256 GB en caja USB 3.0 externa
- **Red:** Realtek PCIe GbE Family Controller
- **Audio:** High Definition Audio (Realtek)

## Estructura de Documentación (`/docs`)

| Nº | Documento | Contenido |
|----|-----------|-----------|
| 01-05 | Configuración base | Extracción de hardware, preparación EFI inicial |
| 06 | Preparación USB y Flasheo | Proceso de creación del instalador USB |
| 07 | Análisis EFIs | Comparativa EFI personalizada vs. Olarila |
| 08 | Troubleshooting Tahoe | Por qué Tahoe fue descartado |
| 09 | Veredicto GPU y Downgrade | **El documento clave que explica toda la incompatibilidad** |

La EFI funcional disponible en `/EFI_Monterey` arranca correctamente Monterey con red y audio operativos. La GPU opera en modo VESA sin aceleración Metal.
