# Fase 7: Arranque e Instalación en el SSD Externo

Una vez que el instalador USB está 100% completo, con el sistema operativo oficial flasheado, y la carpeta `EFI` inyectada en su partición de arranque, nos encontramos en la recta final: instalar macOS en nuestro target.

## ¿Por qué NO formatear el SSD previamente?

Es un impulso común intentar conectar el SSD destino (de 256GB en este caso) a una computadora Windows o a una versión antigua de macOS para formatearlo en APFS antes de siquiera intentar la instalación. 

**Esto es un error:**
El instalador de macOS moderno cuenta con una versión muy específica y actualizada del sistema de archivos APFS. Si formateamos el disco con una herramienta antigua o de terceros, al momento de que el instalador verifique el disco, puede detectar una discrepancia de versiones de contenedores APFS, arrojando errores crípticos (como "Se requiere una actualización de firmware") y abortando la instalación sin previo aviso.

Por lo tanto, la regla de oro es **entregarle al instalador el disco "crudo" o sin tocar**, y que el propio instalador de la versión de macOS destino decida cómo estructurar y formatear nativamente el disco.

---

## 1. Arranque Inicial (Booting)
1. Conecta el Pendrive USB de Instalación que preparamos y el SSD Externo en los puertos nativos traseros de la placa madre del equipo destino (Intel i7-4790K).
2. Enciende el equipo y presiona el atajo de la placa base para abrir el menú de booteo rápido (`F11`, `F12`, `F8` dependiendo del fabricante).
3. Selecciona arrancar la partición UEFI correspondiente a la memoria USB.
4. Te dará la bienvenida el menú gráfico de OpenCore. Selecciona **Install macOS Tahoe**.

## 2. Preparación y Formateo del SSD (Desde la Instalación)
Tras unos minutos donde macOS carga en memoria y procesa las configuraciones de hardware que preparamos:
1. Serás recibido por la pantalla visual del **Entorno de Recuperación de macOS** (macOS Recovery).
2. En la lista de opciones, selecciona **Utilidad de Discos** (Disk Utility) y dale a Continuar.
3. En la barra superior de Disk Utility, ve a **Visualización (View)** y marca **Mostrar todos los dispositivos (Show All Devices)**. 
4. En el panel izquierdo, busca la **raíz absoluta** física de tu SSD externo de 256GB.
5. Haz clic en el botón **Borrar (Erase)** y obligatoriamente rellena los datos así:
   - **Nombre:** (A elección, usualmente `Macintosh HD` o `Tahoe`).
   - **Formato:** `APFS`
   - **Esquema (Scheme):** `Mapa de particiones GUID` (GUID Partition Map).
   
*Este proceso generará la estructura correcta y moderna de APFS, además de particionar el disco dejándolo listo para arrancar.*

## 3. Instalación de macOS
1. Cierra la Utilidad de Discos para volver al menú principal.
2. Selecciona **Instalar macOS**.
3. Sigue los pasos de licencia y al preguntarte dónde instalar, elige tu flamante disco recién formateado.
4. El equipo **se reiniciará múltiples veces** (al menos 3 o 4) durante el proceso. Esto es absolutamente normal. 
5. Durante cada reinicio, al aparecer el menú de OpenCore, el sistema debería **auto-seleccionar** el disco interno `Macintosh HD` para proseguir (si no lo hace, selecciónalo tú).

Una vez concluido este proceso asíncrono, serás recibido con la clásica pantalla de bienvenida y configuración de usuario inicial de Apple.
