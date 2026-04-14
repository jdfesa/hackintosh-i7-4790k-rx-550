/*
 * SSDT-GPU-SPOOF.dsl — Adapted for Haswell B85 + AMD RX 550 Lexa (699F)
 *
 * Hardware: Intel i7-4790K (Haswell), Intel B85 Chipset
 * GPU: AMD ASRock Phantom Gaming RX 550 2GB GDDR5 (Lexa core, Device ID: 1002:699F)
 * PCI Path: PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)
 * ACPI Path: \_SB.PCI0.PEG0.PEGP   ← Haswell/B85 standard path
 *
 * Purpose: Inject Baffin (67FF) device-id at ACPI/DSM level — a lower-level
 * injection than DeviceProperties in config.plist — to force the AMD Baffin
 * driver to load against the Lexa chip. Based on dipaksarkar's working EFI
 * for H510M-H (Comet Lake, ACPI path: \_SB.PC00.PEG1.PEGP).
 *
 * Adapted by: Antigravity / jdfesa hackintosh project
 * Reference:  https://github.com/dipaksarkar/EFI-GIGABYTE-H510M-H
 */

DefinitionBlock ("", "SSDT", 2, "DRTNIA", "AMDGPU", 0x00001000)
{
    // ── External references — Haswell/B85 ACPI node names ──────────────────
    External (_SB_.PCI0,      DeviceObj)
    External (_SB_.PCI0.PEG0.PEGP, DeviceObj)

    // ── GPU Device-Specific Method (DSM) ───────────────────────────────────
    Scope (\_SB.PCI0.PEG0.PEGP)
    {
        If (_OSI ("Darwin"))   // Only inject on macOS
        {
            Method (_DSM, 4, NotSerialized)
            {
                Local0 = Package (0x0E)
                {
                    // Mark as built-in to avoid default VESA framebuffer
                    "built-in",
                    Buffer (One) { 0x00 },

                    // Slot name for System Information display
                    "AAPL,slot-name",
                    Buffer (0x13) { "Internal@0,1,0/0,0" },

                    // Force display output on connector 0
                    "@0,AAPL,boot-display",
                    Buffer (0x04) { 0x01, 0x00, 0x00, 0x00 },

                    // ── THE KEY INJECTION ──────────────────────────────────
                    // Spoof Lexa (699F) → Baffin (67FF) at DSM level
                    // 0xFF 0x67 0x00 0x00 = little-endian 0x67FF
                    "device-id",
                    Buffer (0x04) { 0xFF, 0x67, 0x00, 0x00 },

                    // Suppress WhateverGreen's own spoof to avoid double-patching
                    "no-gfx-spoof",
                    Buffer (0x04) { 0x00, 0x01, 0x00, 0x00 },

                    // ATI/AMD internal device ID (same value, 2-byte format)
                    "ATY,DeviceID",
                    Buffer (0x02) { 0xFF, 0x67 },

                    // Human-readable model name shown in System Information
                    "model",
                    Buffer (0x12) { "AMD Radeon RX 550" }
                }

                DTGP (Arg0, Arg1, Arg2, Arg3, RefOf (Local0))
                Return (Local0)
            }
        }
    }

    // ── DTGP helper method — placed under PCI0 (Haswell root) ──────────────
    Scope (\_SB.PCI0)
    {
        Method (DTGP, 5, NotSerialized)
        {
            If ((Arg0 == ToUUID ("a0b5b7c6-1318-441c-b0c9-fe695eaf949b")))
            {
                If ((Arg1 == One))
                {
                    If ((Arg2 == Zero))
                    {
                        Arg4 = Buffer (One) { 0x03 }
                        Return (One)
                    }
                    If ((Arg2 == One))
                    {
                        Return (One)
                    }
                }
            }
            Arg4 = Buffer (One) { 0x00 }
            Return (Zero)
        }
    }
}
