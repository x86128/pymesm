from logging import info, warning
from mesm_opcodes import *


class CPU:
    def __init__(self, ibus, dbus):
        self.pc = 1
        self.running = False
        self.ibus = ibus
        self.dbus = dbus

        self.interrupt = False
        self.c = 0
        self.c_active = False

        self.acc = 0

        # index registers
        self._m = [0] * 16
        self._k = [0] * 16
        self.m = self._m

        # instruction cache
        self.cmd_cache = 0
        self.is_left = True

        # decoded command
        self.op_indx = 0
        self.op_code = 0
        self.op_addr = 0

        self.vaddr = 0
        self.pc_next = 0
        self.stack = False
        self.rr_reg = 0

    def uaddr(self):
        return (self.m[self.op_indx] + self.vaddr) & 0xFFFF

    def fetch(self):
        self.cmd_cache = self.ibus.read(self.pc)

    def decode(self):
        if self.is_left:
            w = (self.cmd_cache >> 32) & 0xFFFFFFFF
        else:
            w = self.cmd_cache & 0xFFFFFFFF
        self.op_indx = (w >> 24) & 0xF
        self.op_code = (w >> 16) & 0xFF
        self.op_addr = w & 0xFFFF

        if self.c_active:
            self.vaddr = (self.op_addr + self.c) & 0xFFFF
        else:
            self.vaddr = self.op_addr
        self.c_active = False

        if self.op_indx == 15:
            if self.vaddr == 0:
                self.stack = True
            elif self.op_code == 0o41 and self.uaddr() == 15:
                self.stack = True
            else:
                self.stack = False
        else:
            self.stack = False

    def mod_inc(self, index):
        self.m[index] = (self.m[index] + 1) & 0xFFFF

    def mod_dec(self, index):
        self.m[index] = (self.m[index] + 0xFFFF) & 0xFFFF

    def op_atx(self):
        self.dbus.write(self.uaddr(), self.acc)
        if self.stack:
            self.mod_inc(15)

    def op_xta(self):
        if self.stack:
            self.mod_dec(15)
        self.acc = self.dbus.read(self.uaddr())
        # info(f"ACC: {self.acc:>08X}")

    def op_aax(self):
        if self.stack:
            self.mod_dec(15)
        x = self.dbus.read(self.uaddr())
        self.acc = self.acc & x
        # info(f"ACC: {self.acc:>08X}")

    def op_aex(self):
        if self.stack:
            self.mod_dec(15)
        x = self.dbus.read(self.uaddr())
        self.acc = self.acc ^ x
        # info(f"ACC: {self.acc:>08X}")

    def op_aox(self):
        if self.stack:
            self.mod_dec(15)
        x = self.dbus.read(self.uaddr())
        self.acc = self.acc | x
        # info(f"ACC: {self.acc:>08X}")

    def op_utc(self):
        self.c = self.uaddr()
        self.c_active = True

    def op_vtm(self):
        self.m[self.op_indx] = self.vaddr

    def op_stop(self):
        self.running = False
        # info(f"CPU halted at {self.pc:>04X} with {self.op_addr:>04X}")

    def acc_is_zero(self):
        return self.acc == 0

    def print_insn(self):
        if self.op_indx == 0:
            print(f"{self.pc:>04X}: {OP_CODE[self.op_code]} {self.op_addr:>04X}")
        else:
            print(
                f"{self.pc:>04X}: {OP_CODE[self.op_code]} {self.op_addr:>04X}(M{self.op_indx}={self.m[self.op_indx]:>04X})")

    def step(self):
        # FETCH
        if self.is_left:
            self.fetch()
        # DECODE
        self.decode()
        # EXECUTE
        if self.is_left:
            self.pc_next = self.pc
        else:
            self.pc_next = self.pc + 1

        self.is_left = not self.is_left

        # self.print_insn()

        if self.op_code == OP_ATX:
            self.op_atx()
        elif self.op_code == OP_XTA:
            self.op_xta()
        elif self.op_code == OP_AAX:
            self.op_aax()
        elif self.op_code == OP_AEX:
            self.op_aex()
        elif self.op_code == OP_AOX:
            self.op_aox()
        elif self.op_code == OP_UTC:
            self.op_utc()
        elif self.op_code == OP_VTM:
            self.op_vtm()
        elif self.op_code == OP_STOP:
            self.op_stop()
        else:
            self.running = False
            self.print_insn()

        self.pc = self.pc_next

    def run(self):
        self.running = True
