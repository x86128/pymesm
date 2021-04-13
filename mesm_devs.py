import array

MASK48 = 0xFFFFFFFFFFFF


class Device:
    def __init__(self, name):
        self.name = name
        self.size = 1

    def __str__(self):
        return self.name


class RamDevice(Device):
    def __init__(self, name, size):
        super().__init__(name)
        self.size = size
        # make array of 64bit words
        self.memory = array.array('Q', [0] * size)

    def read(self, address):
        if 0 <= address < self.size:
            return self.memory[address] & MASK48
        print(f"READ out of bounds in {self.name} at address {address}.")
        return 0

    def write(self, address, value):
        if 0 <= address < self.size:
            self.memory[address] = value & MASK48
            return
        print(f"WRITE out of bounds in {self.name} at address {address}.")


class Printer(Device):
    def __init__(self, name):
        super().__init__(name)

    def write(self, address, val):
        print(chr(val & 0xff), end='')


class Bus:
    def __init__(self, name, trace=False):
        self.name = name
        self.trace = trace
        self.mmaps = []
        self.devices = []

    def attach(self, device, offset):
        size = device.size
        if size <= 0:
            raise ValueError("Device memory size must be > 0")
        for i, mmap in enumerate(self.mmaps):
            if mmap[0] <= offset <= mmap[1]:
                raise IndexError(f"Attached device address space clamps with {self.devices[i]}.")
        self.mmaps.append((offset, offset + size - 1))
        self.devices.append(device)

    def read(self, address):
        result = 0
        if address == 0:
            return 0
        for i, mmap in enumerate(self.mmaps):
            if mmap[0] <= address <= mmap[1]:
                result = self.devices[i].read(address)
                break
        else:
            print(f"READ out of bounds at BUS {self.name} at {address}.")
        if self.trace:
            print(f"{self.name}: RD from {address:>05o} val: {result:>016o}")
        return result

    def write(self, address, value):
        if address == 0:
            return
        for i, mmap in enumerate(self.mmaps):
            if mmap[0] <= address <= mmap[1]:
                self.devices[i].write(address, value)
                if self.trace:
                    print(f"{self.name}: WR to {address:>05o} val: {value:>016o}")
                return
        print(f"WRITE out of bounds at BUS {self.name} at {address}.")
