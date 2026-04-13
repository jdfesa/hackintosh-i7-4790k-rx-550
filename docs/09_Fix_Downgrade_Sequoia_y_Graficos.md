# 09. Solución a la lentitud: Downgrade a Sequoia y Configuración de iGPU

## El Problema con macOS Tahoe
Inicialmente, intentamos instalar y configurar **macOS Tahoe** (versión 26). Aunque logramos arrancar y engañar (mediante *spoofing*) la dGPU RX 550 (Lexa) para que el sistema la reconociera como Baffin, el rendimiento general del equipo resultó ser inaceptablemente lento (lag crítico en la interfaz gráfica y lentitud extrema en todas las acciones).

Tras consulta y confirmación de expertos (Alejandro Barreiro), la conclusión fue contundente: **Es inviable correr Tahoe suavemente en este hardware**. 
Las razones técnicas principales son:

1. **Políticas agresivas en Tahoe:** OpenCore Legacy Patcher (OCLP) logra *bootear*, pero las nuevas versiones de macOS (Tahoe) manejan exigencias gráficas donde el sistema no perdona componentes no nativos sin chips dedicados recientes.
2. **RX 550 (Lexa) y su Talón de Aquiles:** La variante Lexa de la RX 550 **no tiene soporte de hardware nativo propio para decodificación de video en macOS**. 
3. Al no tener capacidades de decodificación propias, y frente a un sistema avanzado y estricto como Tahoe, el procesador se encarga de todo por subprocesos lentos, asfixiando por completo a la máquina.

El veredicto fue claro: *"Olvídate de Tahoe... hasta Sequoia funcionará bien"*.

## La Solución de Oro: Downgrade a Sequoia y Modo Headless
Para obtener un Hackintosh usable, veloz y estable, la estrategia consiste en dos pilares fundamentales:

1. **Bajar la versión del SO (Downgrade):** Olvidar Tahoe e Instalar **macOS Sequoia (15.x)**, el cual es el límite real y comprobado donde este combo de hardware brilla y soporta la aceleración vía OCLP.
   
   ![Descargando macOS Sequoia con Mist](images/mist_download_sequoia.png)
2. **Activar la Gráfica Integrada en Modo "Headless":** El procesador i7-4790K tiene Gráficos Integrados (iGPU) *Intel HD Graphics 4600*. La magia consistió en ordenarle a macOS que use **la HD 4600 exclusivamentepara procesar la decodificación pesada en segundo plano**, dejando a la RX 550 con la labor simple de "dar imagen". 

A esto se le conoce como modo Headless (sin cabeza / sin monitor enchufado).

### Parches y Ajustes en config.plist

Para lograr esto (y usando las guías oficiales de Dortania), actualizamos el script de generación del EFI con tres modificaciones clave:

#### 1. Identidad de iMac correcta (SMBIOS)
Se abandonó el perfil de iMac18,3 y se pasó al **`iMac14,2`**. Este perfil corresponde a la generación Haswell y le indica a macOS que "espere y use" la ayuda de una gráfica integrada.

#### 2. Inyección de la HD 4600 (iGPU)
Se parcheó explícitamente el bus de la gráfica integrada `PciRoot(0x0)/Pci(0x2,0x0)` indicando su propósito específico para cálculos:
* **`AAPL,ig-platform-id`**: `04001204` *(Este es el identificador mágico en hexadecimal que fuerza el modo Headless en Haswell)*.

#### 3. Mantener el Engaño de la dGPU
La RX 550 original se conservó con el spoofing de *Baffin* para mantener su compatibilidad base con AMD en Sequoia:
* Modificado en `PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)`
* `device-id = FF670000` (67FF en reversa, que emula la RX 560 Baffin).

## Resumen y Advertencia Final
**No se debe intentar usar Tahoe (macOS 26) en una Build con RX 550 (Lexa) y Haswell.** 

El camino a seguir, como hemos documentado, es usar **macOS Sequoia**. Con Sequoia instalado nativamente, y el `config.plist` activando la iGPU en modo asistente (Headless), macOS tendrá suficientes herramientas de hardware para fluir perfectamente bien mediante los parches de OCLP.

## Anexo: Preparación del USB para Sequoia

A modo de registro, este fue el proceso exacto que seguimos para preparar el instalador USB una vez que la descarga de Mist finalizó y decidimos proceder con el downgrade a Sequoia.

### 1. Creación del Instalador y Montaje de EFI

A diferencia de la preparación anterior (ver doc 06), al conectar el pendrive el sistema puede asignarle un identificador de disco distinto (en este caso fue `disk4`). Es vital comprobar esto con `diskutil list` antes de proceder para evitar borrar el disco equivocado.

Una vez creado el instalador de Sequoia con `createinstallmedia`, el proceso para inyectar nuestra configuración ganadora fue el siguiente:

1. Listar los discos (`diskutil list`) e identificar la partición EFI del USB (ej. `disk4s1`).
2. Montar esa partición usando `sudo diskutil mount /dev/disk4s1`.
3. Copiar la carpeta `EFI` (con la configuración generada por nuestro script `build_opencore_config.py`) directamente a la raíz de la partición montada.

A continuación se muestra el registro visual del proceso en la terminal:

![Montaje y copia de EFI en el USB](images/preparacion_usb_sequoia.jpg)
