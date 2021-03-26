#!/usr/bin/python3

import sys
from mesm_devs import *
from mesm_cpu import CPU
from mesm_utils import load_oct

if __name__ == '__main__':
    irom = RamDevice("IROM0", 65536)
    dram = RamDevice("DRAM0", 49152)
    printer = Printer("PRN0")

    ibus = Bus("IBUS")
    dbus = Bus("DBUS")

    ibus.attach(irom, 0)
    dbus.attach(dram, 0)
    dbus.attach(printer, 65535)

    if len(sys.argv) < 2:
        print("Usage:\npymesm.py program.oct")
        sys.exit(1)

    load_oct(sys.argv[1], ibus, dbus)

    cpu = CPU(ibus, dbus)
    cpu.run(40)

    while cpu.running:
        cpu.step()

    print("Simulation finished.")
