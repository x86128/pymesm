from mesm_devs import *
from mesm_cpu import CPU
from mesm_utils import load_oct

if __name__ == '__main__':
    irom = RamDevice("IROM0", 2048)
    dram = RamDevice("DRAM0", 2048)
    printer = Printer("PRN0")

    ibus = Bus("IBUS")
    dbus = Bus("DBUS")

    ibus.attach(irom, 0)
    dbus.attach(dram, 0)
    dbus.attach(printer, 2048)

    load_oct("examples/hello.oct", ibus, dbus)

    cpu = CPU(ibus, dbus)
    cpu.run()

    while cpu.running:
        cpu.step()

    print("Simulation finished.")
