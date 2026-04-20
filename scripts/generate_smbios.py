#!/usr/bin/env python3
"""
Generate SMBIOS data for iMac14,2 using GenSMBIOS's macserial.
This script:
1. Downloads macserial from OpenCorePkg
2. Generates iMac14,2 serials
3. Outputs them for manual or automated use
"""
import subprocess, os, sys, tempfile, zipfile, shutil, uuid, json, binascii
try:
    from secrets import randbits, choice
except ImportError:
    from random import SystemRandom
    _sysrand = SystemRandom()
    randbits = _sysrand.getrandbits
    choice = _sysrand.choice

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GENSMBIOS_DIR = os.path.join(SCRIPT_DIR, "GenSMBIOS")
MACSERIAL_PATH = os.path.join(GENSMBIOS_DIR, "Scripts", "macserial")

# Apple ROM prefixes from GenSMBIOS
try:
    with open(os.path.join(GENSMBIOS_DIR, "Scripts", "prefix.json")) as f:
        ROM_PREFIXES = json.load(f)
except:
    ROM_PREFIXES = []

def download_macserial():
    """Download macserial from latest OpenCorePkg release"""
    import urllib.request
    
    print("Downloading OpenCorePkg RELEASE to get macserial...")
    
    # Get latest release page
    req = urllib.request.Request(
        "https://github.com/acidanthera/OpenCorePkg/releases/latest",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode()
    
    # Find the RELEASE zip URL
    release_url = None
    for line in html.split("\n"):
        if 'href="/acidanthera/OpenCorePkg/releases/download/' in line and "-RELEASE.zip" in line:
            release_url = "https://github.com" + line.split('href="')[1].split('"')[0]
            break
    
    if not release_url:
        # Try expanded_assets approach
        for line in html.split("\n"):
            if "expanded_assets" in line:
                try:
                    assets_url = line.split('src="')[1].split('"')[0]
                    req2 = urllib.request.Request(assets_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req2) as resp2:
                        assets_html = resp2.read().decode()
                    for l in assets_html.split("\n"):
                        if 'href="/acidanthera/OpenCorePkg/releases/download/' in l and "-RELEASE.zip" in l:
                            release_url = "https://github.com" + l.split('href="')[1].split('"')[0]
                            break
                except:
                    pass
                break

    if not release_url:
        print("ERROR: Could not find OpenCorePkg release URL")
        sys.exit(1)
    
    print(f"  Downloading from: {release_url}")
    
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "OpenCorePkg.zip")
    
    req = urllib.request.Request(release_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        with open(zip_path, "wb") as f:
            f.write(resp.read())
    
    print("  Extracting macserial...")
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if name.endswith("macserial") and "Utilities" in name:
                # Extract macserial
                target_dir = os.path.join(GENSMBIOS_DIR, "Scripts")
                os.makedirs(target_dir, exist_ok=True)
                with z.open(name) as src, open(MACSERIAL_PATH, "wb") as dst:
                    dst.write(src.read())
                os.chmod(MACSERIAL_PATH, 0o755)
                print(f"  macserial extracted to: {MACSERIAL_PATH}")
                break
    
    shutil.rmtree(temp_dir)


def generate_rom():
    """Generate Apple-like ROM (6 bytes)"""
    rom_str = "{:x}".format(randbits(8*6)).upper().rjust(12, "0")
    if ROM_PREFIXES:
        prefix = choice(ROM_PREFIXES)
        if isinstance(prefix, str):
            rom_str = prefix + rom_str[len(prefix):]
    return rom_str


def generate_smbios(smbios_type="iMac14,2"):
    """Generate SMBIOS data using macserial"""
    if not os.path.exists(MACSERIAL_PATH):
        download_macserial()
    
    if not os.path.exists(MACSERIAL_PATH):
        print("ERROR: macserial not found!")
        sys.exit(1)
    
    # Run macserial to generate all SMBIOS types
    result = subprocess.run(
        [MACSERIAL_PATH, "-a"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"ERROR: macserial failed: {result.stderr}")
        sys.exit(1)
    
    # Find matching SMBIOS type
    for line in result.stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = [x.strip() for x in line.split("|")]
        if len(parts) >= 2 and parts[0].lower() == smbios_type.lower():
            serial = parts[1]
            board_serial = parts[2] if len(parts) > 2 else "GENERATE_MANUALLY"
            sm_uuid = str(uuid.uuid4()).upper()
            rom = generate_rom()
            
            return {
                "type": parts[0],
                "serial": serial,
                "board_serial": board_serial,
                "uuid": sm_uuid,
                "rom": rom,
                "rom_bytes": binascii.unhexlify(rom.encode("utf-8"))
            }
    
    print(f"ERROR: SMBIOS type '{smbios_type}' not found in macserial output")
    sys.exit(1)


if __name__ == "__main__":
    smbios_type = sys.argv[1] if len(sys.argv) > 1 else "iMac14,2"
    print(f"\n{'='*60}")
    print(f"  Generating SMBIOS for: {smbios_type}")
    print(f"{'='*60}\n")
    
    data = generate_smbios(smbios_type)
    
    print(f"Type:         {data['type']}")
    print(f"Serial:       {data['serial']}")
    print(f"Board Serial: {data['board_serial']}")
    print(f"SmUUID:       {data['uuid']}")
    print(f"Apple ROM:    {data['rom']}")
    print()
    
    # Output as JSON for scripting
    json_data = {k: v for k, v in data.items() if k != "rom_bytes"}
    json_path = os.path.join(SCRIPT_DIR, "smbios_generated.json")
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"JSON saved to: {json_path}")
