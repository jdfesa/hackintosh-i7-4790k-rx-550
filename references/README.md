# References

> Carpeta de EFIs y configuraciones de terceros usadas como guía.  
> **Nada aquí es de nuestra autoría.** Son archivos descargados de la comunidad para consulta y comparación.

---

## EFI-Haswell-RX550-Lexa

**Fuente**: Comunidad Olarila  
**Hardware**: i5-4590, RX 550 Lexa 4GB, Kingster H81  
**SMBIOS**: MacPro7,1  
**macOS**: Catalina → Tahoe (según autor)

**Por qué es útil**: Es la única EFI de referencia con hardware casi idéntico al nuestro (Haswell + RX 550 Lexa spoof Baffin) que confirma **DRM y hardware video decode funcionando** usando `MacPro7,1` + `shikigva=80 unfairgva=1 -radcodec`, sin OCLP ni iGPU.

**Diferencias clave con nuestra EFI**: Usa `MacPro7,1` (no `iMac14,2`), no configura iGPU, y hace el spoof de la Lexa vía DeviceProperties (no SSDT).
