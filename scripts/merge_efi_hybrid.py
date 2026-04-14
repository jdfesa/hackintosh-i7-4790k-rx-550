import plistlib
import os

print("--- Iniciando Fusión de EFI Sequoia (Haswell + Lexa) ---")

config_path = "EFI_Sequoia/EFI/OC/config.plist"
if not os.path.exists(config_path):
    print(f"Error: {config_path} no existe.")
    exit(1)

with open(config_path, 'rb') as f:
    config = plistlib.load(f)

# 1. Inyectar Propiedades de Video (Lexa Spoof)
pci_gpu_path = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"
gpu_spoof = {
    "device-id": bytes.fromhex("FF670000"),
    "model": "AMD Radeon RX 550 (Lexa 699F Spoofed to Baffin 67FF)"
}

if 'DeviceProperties' not in config: config['DeviceProperties'] = {'Add': {}, 'Delete': {}}
config['DeviceProperties']['Add'][pci_gpu_path] = gpu_spoof

# 2. Inyectar iGPU Headless (para decodificación)
pci_igpu_path = "PciRoot(0x0)/Pci(0x2,0x0)"
igpu_props = {
    "AAPL,ig-platform-id": bytes.fromhex("04001204"),  # Haswell Headless
    "model": "Intel HD Graphics 4600 (Headless Mode)"
}
config['DeviceProperties']['Add'][pci_igpu_path] = igpu_props

# 3. Registrar AMFIPass.kext
amfi_kext = {
    "Arch": "x86_64",
    "BundlePath": "AMFIPass.kext",
    "Comment": "Permite OCLP Root Patches",
    "Enabled": True,
    "ExecutablePath": "Contents/MacOS/AMFIPass",
    "MaxKernel": "",
    "MinKernel": "23.0.0",
    "PlistPath": "Contents/Info.plist"
}

# Insertar AMFIPass después de WhateverGreen o al final de la lista
kexts = config['Kernel']['Add']
if not any(k['BundlePath'] == 'AMFIPass.kext' for k in kexts):
    kexts.append(amfi_kext)

# 4. Configurar SIP y Boot-args para OCLP
nvram_7C = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
if nvram_7C not in config['NVRAM']['Add']: config['NVRAM']['Add'][nvram_7C] = {}

# SIP 0x803 (03080000)
config['NVRAM']['Add'][nvram_7C]['csr-active-config'] = bytes.fromhex("03080000")

# Boot-args
existing_args = config['NVRAM']['Add'][nvram_7C].get('boot-args', '')
new_args = "-v keepsyms=1 debug=0x100 alcid=1 amfi=0x80 watchdog=0 agdpmod=pikera"

# Mantener los parámetros de ethernet de Oralilla si existían (dk.e1000=0)
if "dk.e1000=0" in existing_args: new_args += " dk.e1000=0"
if "e1000=0" in existing_args: new_args += " e1000=0"

config['NVRAM']['Add'][nvram_7C]['boot-args'] = new_args

# 5. Asegurar SecureBootModel Disabled
config['Misc']['Security']['SecureBootModel'] = "Disabled"

# 6. Guardar cambios
with open(config_path, 'wb') as f:
    plistlib.dump(config, f)

print(f"--- Fusión Completada con éxito en {config_path} ---")
