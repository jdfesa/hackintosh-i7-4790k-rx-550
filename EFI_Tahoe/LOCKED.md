# 🔒 EFI BLOQUEADA — NO MODIFICAR

> [!CAUTION]
> Esta EFI está **congelada** desde el 19 de abril de 2026.
> Es la configuración funcional y probada para **macOS Tahoe 26.4.1** con Metal activo via SSDT ACPI spoof.

## ¿Por qué está bloqueada?

Esta carpeta tiene permisos de **solo lectura** a nivel filesystem para prevenir modificaciones accidentales.
Representa la EFI estable y verificada que arranca macOS Tahoe correctamente en este hardware.

## ¿Dónde se trabaja ahora?

Todo desarrollo futuro se hace en **`EFI_Sonoma/`**, que es una copia de esta EFI adaptada para macOS Sonoma 14.8.5 con OCLP.

## Si necesitás modificar esta EFI (emergencia)

```bash
# Desbloquear temporalmente
chmod -R u+w EFI_Tahoe/

# ... hacer cambios ...

# Volver a bloquear
chmod -R a-w EFI_Tahoe/
chmod u+w EFI_Tahoe/  # mantener el directorio navegable
```
