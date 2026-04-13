# Fase 3: Tablas ACPI y Hardware en Serie

Para engañar eficientemente al instalador de macOS y lograr que interactúe correctamente con el hardware de nuestra PC, necesitamos inyectar archivos compilados conocidos como SSDT (System Server Descriptor Table) en las tablas ACPI de la placa base Intel B85. 

Para un procesador de arquitectura Haswell (Core i7-4790K) de escritorio, la configuración recomendada por Dortania es estricta e incluye únicamente dos archivos vitales. Si saturamos esta carpeta con SSDTs innecesarios (como lo hacen los instaladores genéricos), rompemos el sistema.

## 1. SSDT-PLUG.aml
*   **Función:** Habilita el control de energía nativo (Power Management/XCPM) del procesador.
*   **Por qué es crucial:** Sin él, el i7-4790K se negará a reducir su frecuencia cuando está inactivo, operando al máximo todo el tiempo. Esto causaría desgaste prematuro, altas temperaturas y un alto consumo energético.

## 2. SSDT-EC.aml
*   **Función:** Inyecta un dispositivo Controlador Embebido (Embedded Controller - EC) "falso" en el sistema.
*   **Por qué es crucial:** Las Mac reales delegan la administración de su propia energía a un chip EC muy específico. macOS (especialmente desde Catalina en adelante) realiza comprobaciones al inicio para buscar este chip. Si no lo encuentra por su nombre estricto en la tabla, el proceso de arranque se trabará ("Kernel Panic" o cuelgue infinito). Nuestra tabla le dice al sistema: *"Aquí está el controlador que buscas"*, permitiendo que el arranque continúe suavemente.
