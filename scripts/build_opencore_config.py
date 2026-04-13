import plistlib
import os

print("Iniciando compilación de config.plist a medida para Haswell y RX 550 (Lexa)")

plist_path = r".\EFI\OC\config.plist"
if not os.path.exists(plist_path):
    print(f"Error: No se encontró el archivo en {plist_path}")
    exit(1)

with open(plist_path, 'rb') as f:
    config = plistlib.load(f)

# 1. Limpieza de advertencias de Sample.plist
if "WARNING - 1" in config: del config["WARNING - 1"]
if "WARNING - 2" in config: del config["WARNING - 2"]

# 2. Inyección de Tablas ACPI
config['ACPI']['Add'] = [
    {'Arch': 'Any', 'Comment': 'Control de Energía i7 Haswell', 'Enabled': True, 'Path': 'SSDT-PLUG.aml'},
    {'Arch': 'Any', 'Comment': 'Fake EC Control', 'Enabled': True, 'Path': 'SSDT-EC.aml'}
]

# 3. Inyección de Kexts en orden estricto
config['Kernel']['Add'] = [
    {'Arch': 'x86_64', 'BundlePath': 'Lilu.kext', 'Comment': 'Motor de parches', 'Enabled': True, 'ExecutablePath': 'Contents/MacOS/Lilu', 'MaxKernel': '', 'MinKernel': '', 'PlistPath': 'Contents/Info.plist'},
    {'Arch': 'x86_64', 'BundlePath': 'VirtualSMC.kext', 'Comment': 'Emulador SMC', 'Enabled': True, 'ExecutablePath': 'Contents/MacOS/VirtualSMC', 'MaxKernel': '', 'MinKernel': '', 'PlistPath': 'Contents/Info.plist'},
    {'Arch': 'x86_64', 'BundlePath': 'WhateverGreen.kext', 'Comment': 'Parches de Video', 'Enabled': True, 'ExecutablePath': 'Contents/MacOS/WhateverGreen', 'MaxKernel': '', 'MinKernel': '', 'PlistPath': 'Contents/Info.plist'},
    {'Arch': 'x86_64', 'BundlePath': 'AppleALC.kext', 'Comment': 'Audio HD', 'Enabled': True, 'ExecutablePath': 'Contents/MacOS/AppleALC', 'MaxKernel': '', 'MinKernel': '', 'PlistPath': 'Contents/Info.plist'},
    {'Arch': 'x86_64', 'BundlePath': 'SMCProcessor.kext', 'Comment': 'Sensor Temp CPU', 'Enabled': True, 'ExecutablePath': 'Contents/MacOS/SMCProcessor', 'MaxKernel': '', 'MinKernel': '', 'PlistPath': 'Contents/Info.plist'},
    {'Arch': 'x86_64', 'BundlePath': 'SMCSuperIO.kext', 'Comment': 'Sensor Fans', 'Enabled': True, 'ExecutablePath': 'Contents/MacOS/SMCSuperIO', 'MaxKernel': '', 'MinKernel': '', 'PlistPath': 'Contents/Info.plist'},
    {'Arch': 'x86_64', 'BundlePath': 'RealtekRTL8111.kext', 'Comment': 'Red Ethernet', 'Enabled': True, 'ExecutablePath': 'Contents/MacOS/RealtekRTL8111', 'MaxKernel': '', 'MinKernel': '', 'PlistPath': 'Contents/Info.plist'},
]

# 4. Quirks del Kernel (Haswell)
config['Kernel']['Quirks']['AppleCpuPmCfgLock'] = True
config['Kernel']['Quirks']['AppleXcpmCfgLock'] = True
config['Kernel']['Quirks']['DisableIoMapper'] = True
config['Kernel']['Quirks']['PanicNoKextDump'] = True
config['Kernel']['Quirks']['PowerTimeoutKernelPanic'] = True
config['Kernel']['Quirks']['XhciPortLimit'] = True

# 5. Quirks del Booter (Haswell)
config['Booter']['Quirks']['AvoidRuntimeDefrag'] = True
config['Booter']['Quirks']['EnableSafeModeSlide'] = True
config['Booter']['Quirks']['ProvideCustomSlide'] = True
config['Booter']['Quirks']['SetupVirtualMap'] = True

# 6. Miscelánea
config['Misc']['Debug']['AppleDebug'] = True
config['Misc']['Debug']['ApplePanic'] = True
config['Misc']['Debug']['DisableWatchDog'] = True
config['Misc']['Debug']['Target'] = 67
config['Misc']['Security']['AllowSetDefault'] = True
config['Misc']['Security']['ScanPolicy'] = 0
config['Misc']['Security']['SecureBootModel'] = 'Disabled'
config['Misc']['Security']['Vault'] = 'Optional'

# 7. NVRAM (Argumentos de arranque)
nvram_guid = '7C436110-AB2A-4BBB-A880-FE41995C9F82'
if nvram_guid in config['NVRAM']['Add']:
    config['NVRAM']['Add'][nvram_guid]['boot-args'] = '-v keepsyms=1 debug=0x100 alcid=1'
    # alcid=1 es para inyectar AppleALC estandar y revpatch es por si usa algo más
    config['NVRAM']['Add'][nvram_guid]['prev-lang:kbd'] = 'es:87'

# 8. PlatformInfo (SMBIOS)
# Usaremos iMacPro1,1 en lugar de iMac15,1 para permitir instalaciones nativas 
# de macOS Ventura, Sonoma y Sequoia, desactivando el soporte nativo a la iGPU de Haswell
# y dándole el control absoluto del video a la RX 550 para aceleración nativa.
config['PlatformInfo']['Generic']['SystemProductName'] = 'iMacPro1,1'

# 9. UEFI Drivers
config['UEFI']['Drivers'] = [
    {'Arguments': '', 'Comment': 'HFS+ File System Driver', 'Enabled': True, 'Path': 'HfsPlus.efi'},
    {'Arguments': '', 'Comment': 'OpenRuntime', 'Enabled': True, 'Path': 'OpenRuntime.efi'},
    {'Arguments': '', 'Comment': 'Reset NVRAM Utility', 'Enabled': True, 'Path': 'ResetNvramEntry.efi'},
    {'Arguments': '', 'Comment': 'GUI', 'Enabled': True, 'Path': 'OpenCanopy.efi'},
]

# 10. EL PARCHE CRÍTICO: LEXA SPOOF
pci_gpu_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"
# Convertimos el string 67FF0000 a bytes para la inyección Data en XML
spoof_bytes = bytes.fromhex('FF670000')

if pci_gpu_path not in config['DeviceProperties']['Add']:
    config['DeviceProperties']['Add'][pci_gpu_path] = {}

config['DeviceProperties']['Add'][pci_gpu_path]['device-id'] = spoof_bytes
config['DeviceProperties']['Add'][pci_gpu_path]['model'] = 'AMD Radeon RX 550 (Lexa 699F Spoofed to Baffin 67FF)'

with open(plist_path, 'wb') as f:
    plistlib.dump(config, f)

print(f"Modificación completa. Archivo guardado con éxito y Spoof aplicado en {pci_gpu_path}.")
