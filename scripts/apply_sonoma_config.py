#!/usr/bin/env python3
"""
Apply all Sonoma EFI config.plist modifications:
- SMBIOS: MacPro7,1 → iMac14,2
- Board identifiers for iMac14,2
- boot-args for Sonoma + OCLP
- Kernel quirks adjustments
- Generated SMBIOS serials from smbios_generated.json
"""
import plistlib
import json
import os
import sys
import binascii
import shutil
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_DIR, "EFI_Sonoma", "EFI", "OC", "config.plist")
SMBIOS_JSON = os.path.join(SCRIPT_DIR, "smbios_generated.json")

# iMac14,2 board identifier
BOARD_ID = "Mac-27ADBB7B4CEE8E61"

def load_smbios():
    with open(SMBIOS_JSON) as f:
        return json.load(f)

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"ERROR: Config not found: {CONFIG_PATH}")
        sys.exit(1)
    
    if not os.path.exists(SMBIOS_JSON):
        print(f"ERROR: SMBIOS data not found: {SMBIOS_JSON}")
        print("Run generate_smbios.py first!")
        sys.exit(1)
    
    smbios = load_smbios()
    serial = smbios["serial"]
    board_serial = smbios["board_serial"]
    sm_uuid = smbios["uuid"]
    rom_hex = smbios["rom"]
    rom_bytes = binascii.unhexlify(rom_hex)
    
    # Backup original
    backup_path = CONFIG_PATH + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(CONFIG_PATH, backup_path)
    print(f"Backup saved: {backup_path}")
    
    # Load plist
    with open(CONFIG_PATH, "rb") as f:
        config = plistlib.load(f)
    
    print("\n=== Applying Sonoma EFI modifications ===\n")
    
    # =========================================
    # 1. BOOT-ARGS
    # =========================================
    old_bootargs = config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]
    new_bootargs = "-v keepsyms=1 debug=0x100 alcid=1 agdpmod=pikera amfi_get_out_of_my_way=0x1 ipc_control_port_options=0"
    config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] = new_bootargs
    print(f"[1] boot-args:")
    print(f"    OLD: {old_bootargs}")
    print(f"    NEW: {new_bootargs}")
    
    # =========================================
    # 2. KERNEL QUIRKS
    # =========================================
    # CustomSMBIOSGuid: true → false
    config["Kernel"]["Quirks"]["CustomSMBIOSGuid"] = False
    print(f"\n[2] Kernel > Quirks > CustomSMBIOSGuid: true → false")
    
    # XhciPortLimit: true → false
    config["Kernel"]["Quirks"]["XhciPortLimit"] = False
    print(f"    Kernel > Quirks > XhciPortLimit: true → false")
    
    # =========================================
    # 3. PLATFORMINFO > GENERIC (main SMBIOS section for OpenCore)
    # =========================================
    generic = config["PlatformInfo"]["Generic"]
    
    generic["SystemProductName"] = "iMac14,2"
    generic["SystemSerialNumber"] = serial
    generic["MLB"] = board_serial
    generic["SystemUUID"] = sm_uuid
    generic["ROM"] = rom_bytes
    generic["SpoofVendor"] = True  # Dortania recommends YES
    generic["AdviseFeatures"] = False  # Dortania: NO for standard setups
    
    print(f"\n[3] PlatformInfo > Generic:")
    print(f"    SystemProductName: iMac14,2")
    print(f"    SystemSerialNumber: {serial}")
    print(f"    MLB: {board_serial}")
    print(f"    SystemUUID: {sm_uuid}")
    print(f"    ROM: {rom_hex}")
    print(f"    SpoofVendor: true")
    
    # =========================================
    # 4. PLATFORMINFO > DATAHUB
    # =========================================
    datahub = config["PlatformInfo"]["DataHub"]
    datahub["BoardProduct"] = BOARD_ID
    datahub["SystemProductName"] = "iMac14,2"
    datahub["SystemSerialNumber"] = serial
    datahub["SystemUUID"] = sm_uuid
    
    print(f"\n[4] PlatformInfo > DataHub:")
    print(f"    BoardProduct: {BOARD_ID}")
    print(f"    SystemProductName: iMac14,2")
    
    # =========================================
    # 5. PLATFORMINFO > PLATFORMNVRAM
    # =========================================
    pnvram = config["PlatformInfo"]["PlatformNVRAM"]
    pnvram["BID"] = BOARD_ID
    pnvram["MLB"] = board_serial
    pnvram["ROM"] = rom_bytes
    pnvram["SystemSerialNumber"] = serial
    pnvram["SystemUUID"] = sm_uuid
    
    print(f"\n[5] PlatformInfo > PlatformNVRAM:")
    print(f"    BID: {BOARD_ID}")
    print(f"    MLB: {board_serial}")
    
    # =========================================
    # 6. PLATFORMINFO > SMBIOS
    # =========================================
    smbios_section = config["PlatformInfo"]["SMBIOS"]
    smbios_section["BoardProduct"] = BOARD_ID
    smbios_section["BoardSerialNumber"] = board_serial
    smbios_section["BoardVersion"] = "iMac14,2"
    smbios_section["ChassisSerialNumber"] = serial
    smbios_section["ChassisVersion"] = BOARD_ID
    smbios_section["SystemFamily"] = "iMac"
    smbios_section["SystemProductName"] = "iMac14,2"
    smbios_section["SystemSerialNumber"] = serial
    smbios_section["SystemUUID"] = sm_uuid
    # BoardType: 10 is correct for iMac14,2 (Motherboard)
    smbios_section["BoardType"] = 10
    
    print(f"\n[6] PlatformInfo > SMBIOS:")
    print(f"    BoardProduct: {BOARD_ID}")
    print(f"    SystemFamily: iMac")
    print(f"    SystemProductName: iMac14,2")
    print(f"    BoardType: 10")
    
    # =========================================
    # 7. UpdateSMBIOSMode: Custom → Create
    # =========================================
    config["PlatformInfo"]["UpdateSMBIOSMode"] = "Create"
    print(f"\n[7] PlatformInfo > UpdateSMBIOSMode: Custom → Create")
    
    # =========================================
    # 8. Verify iGPU config (just report, don't change)
    # =========================================
    igpu = config["DeviceProperties"]["Add"].get("PciRoot(0x0)/Pci(0x2,0x0)", {})
    ig_platform_id = igpu.get("AAPL,ig-platform-id", b"")
    ig_hex = ig_platform_id.hex() if isinstance(ig_platform_id, bytes) else "unknown"
    print(f"\n[8] DeviceProperties > iGPU (verification only):")
    print(f"    AAPL,ig-platform-id: {ig_hex} ({'04001204 ✅ headless correct' if ig_hex == '04001204' else '⚠️ unexpected!'})")
    
    # =========================================
    # 9. Verify csr-active-config (just report, don't change)
    # =========================================
    csr = config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"].get("csr-active-config", b"")
    csr_hex = csr.hex() if isinstance(csr, bytes) else "unknown"
    print(f"\n[9] NVRAM > csr-active-config: {csr_hex} ({'✅ SIP partially disabled for OCLP' if csr_hex == '03080000' else '⚠️ review needed'})")
    
    # =========================================
    # SAVE
    # =========================================
    with open(CONFIG_PATH, "wb") as f:
        plistlib.dump(config, f, sort_keys=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Config saved: {CONFIG_PATH}")
    print(f"📋 Backup at: {backup_path}")
    print(f"{'='*60}")
    
    print(f"\n⚠️  IMPORTANT: Verify serial at https://checkcoverage.apple.com")
    print(f"    Serial to check: {serial}")
    print(f"    Expected result: 'Unable to check coverage for this serial number.'")
    print(f"\n⚠️  BIOS settings to verify before booting:")
    print(f"    - IGPU Multi-Monitor: Enabled")
    print(f"    - Primary Display: PEG / Auto")
    print(f"    - DVMT Pre-Allocated: 64MB or more")


if __name__ == "__main__":
    main()
