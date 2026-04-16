#!/bin/bash

# Este script extrae y formatea información detallada del hardware 
# para demostrar el éxito de la configuración del Hackintosh.
# Totalmente seguro de usar, solo efectúa consultas de lectura.

clear
echo -e "\033[1;36m=========================================================\033[0m"
echo -e "\033[1;32m         🍏 HACKINTOSH TAHOE - ABSOLUTE VICTORY 🍏       \033[0m"
echo -e "\033[1;36m=========================================================\033[0m"

# OS Info
os_name=$(sw_vers -productName)
os_vers=$(sw_vers -productVersion)
os_build=$(sw_vers -buildVersion)
kernel=$(uname -rs)

# CPU Info (Low-level extact string from kernel)
cpu_brand=$(sysctl -n machdep.cpu.brand_string)
cpu_cores=$(sysctl -n hw.physicalcpu)
cpu_threads=$(sysctl -n hw.logicalcpu)

# RAM Info (Parsing the exact type and speed from the first stick)
ram_total=$(system_profiler SPHardwareDataType | awk -F": " '/Memory/{print $2; exit}' | xargs)
ram_type=$(system_profiler SPMemoryDataType | awk -F": " '/Type/{print $2; exit}' | xargs)
ram_speed=$(system_profiler SPMemoryDataType | awk -F": " '/Speed/{print $2; exit}' | xargs)

# SMBIOS and Bootloader
smbios=$(sysctl -n hw.model)
oc_ver=$(nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:opencore-version 2>/dev/null | awk '{print $2}' | xargs)
if [ -z "$oc_ver" ]; then oc_ver="Active (EFI SSDT Spoof)"; fi

# Deep GPU Info 
gpu_name=$(system_profiler SPDisplaysDataType | awk -F": " '/Chipset Model/{print $2; exit}' | xargs)
gpu_mem=$(system_profiler SPDisplaysDataType | awk -F": " '/VRAM/{print $2; exit}' | xargs)
gpu_id=$(system_profiler SPDisplaysDataType | awk -F": " '/Device ID/{print $2; exit}' | xargs)
gpu_bus=$(system_profiler SPDisplaysDataType | awk -F": " '/PCIe Lane Width/{print $2; exit}' | xargs)
gpu_metal=$(system_profiler SPDisplaysDataType | awk -F": " '/Metal/{print $2; exit}' | xargs)
monitor=$(system_profiler SPDisplaysDataType | awk -F": " '/Resolution/{print $2; exit}' | xargs)

echo -e "\033[1;33m[+] OS SYSTEM\033[0m"
echo -e "    OS:      \033[1;37m$os_name $os_vers ($os_build)\033[0m"
echo -e "    Kernel:  \033[1;37m$kernel\033[0m"
echo -e "    SMBIOS:  \033[1;37m$smbios\033[0m"
echo -e "    Boot:    \033[1;35mOpenCore $oc_ver\033[0m"
echo ""
echo -e "\033[1;33m[+] EXTREME HARDWARE\033[0m"
echo -e "    CPU:     \033[1;37m$cpu_brand\033[0m"
echo -e "    Cores:   \033[1;37m$cpu_cores Cores / $cpu_threads Threads\033[0m"
echo -e "    RAM:     \033[1;37m$ram_total $ram_type @ $ram_speed\033[0m"
echo ""
echo -e "\033[1;33m[+] GRAPHICS & NATIVE ACCELERATION\033[0m"
echo -e "    GPU:     \033[1;36m$gpu_name\033[0m"
echo -e "    VRAM:    \033[1;37m$gpu_mem \033[1;30m(PCIe $gpu_bus Ancho de bus)\033[0m"
echo -e "    Spoof:   \033[1;31m$gpu_id  (Lexa -> Baffin ACPI Inject)\033[0m"
echo -e "    Metal:   \033[1;32m$gpu_metal \033[1;37m⚡\033[0m"
echo -e "    Display: \033[1;37m$monitor\033[0m"
echo -e "\033[1;36m=========================================================\033[0m"
