#!/usr/bin/python3

import argparse
from mesm_devs import Bus, RamDevice, Printer
from mesm_cpu import CPU
from mesm_utils import load_oct

argp = argparse.ArgumentParser()
argp.add_argument("-i", required=True, dest="input", help="Input *.oct file")
argp.add_argument("-c", default=100, type=int, help="Number of commands to execute")
argp.add_argument("-t", required=False, dest="trace", action="store_true", help="Print trace")
args = argp.parse_args()

if __name__ == '__main__':
    irom = RamDevice("IROM0", 65536)
    dram = RamDevice("DRAM0", 49152)
    printer = Printer("PRN0")

    ibus = Bus("IBUS")
    dbus = Bus("DBUS")

    ibus.attach(irom, 0)
    dbus.attach(dram, 0)
    dbus.attach(printer, 65535)

    load_oct(args.input, ibus, dbus)

    cpu = CPU(ibus, dbus)
    if args.trace:
        cpu.set_trace()
    cpu.run(args.c)

    while cpu.running:
        cpu.step()

    print("Simulation finished.")
