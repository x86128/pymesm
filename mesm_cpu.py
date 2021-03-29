from logging import info, warning
from mesm_opcodes import *


class CPU:
    def __init__(self, ibus, dbus):
        self.pc = 1
        self.running = False
        self.commands = 100
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

    @property
    def uaddr(self):
        return (self.m[self.op_indx] + self.vaddr) & 0xFFFF

    @property
    def f_log(self):
        return self.rr_reg & 0b11100 == 0b100

    @property
    def f_mul(self):
        return self.rr_reg & 0b11100 == 0b1000

    @property
    def f_add(self):
        return self.rr_reg & 0b11100 == 0b10000

    @property
    def omega(self):
        """
        case additive: ω = (A[41] != 0); /* A < 0 */ break;
	    case multiplicative: ω = (A[48] != 1); /* abs(A) < 0.5 */ break;
	    case logical: ω = (A[48:1] != 0); /* A != 0 */ break;
	    case 0: ω = 1;
        """
        if self.f_log and self.acc != 0:
            return True
        elif self.f_add and self.acc >= 0x80000000:
            return True
        elif self.f_mul and self.acc < 0x80000000:
            return True
        else:
            return False

    def set_log(self):
        self.rr_reg = self.rr_reg & 0b11100011 | 0b100

    def set_mul(self):
        self.rr_reg = self.rr_reg & 0b11100011 | 0b1000

    def set_add(self):
        self.rr_reg = self.rr_reg & 0b11100011 | 0b10000

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

        self.stack = False
        if self.op_indx == 15:
            if self.vaddr == 0:
                self.stack = True
            elif self.op_code == 0o41 and self.uaddr == 15:
                self.stack = True

    def mod_inc(self, index):
        self.m[index] = (self.m[index] + 1) & 0xFFFF

    def mod_dec(self, index):
        self.m[index] = (self.m[index] + 0xFFFF) & 0xFFFF

    def op_atx(self):
        self.dbus.write(self.uaddr, self.acc & 0xFFFFFFFF)
        if self.stack:
            self.mod_inc(15)

    def op_ati(self):
        t = self.uaddr & 0xF
        if t != 0:
            self.m[t] = self.acc & 0xFFFF

    def op_ita(self):
        t = self.uaddr & 0xF
        self.acc = self.m[t]
        self.set_log()

    def op_stx(self):
        self.dbus.write(self.uaddr, self.acc & 0xFFFFFFFF)
        self.mod_dec(15)
        self.acc = self.dbus.read(self.m[15]) & 0xFFFFFFFF
        self.set_log()

    def op_xta(self):
        if self.stack:
            self.mod_dec(15)
        self.acc = self.dbus.read(self.uaddr) & 0xFFFFFFFF
        self.set_log()
        # info(f"ACC: {self.acc:>08X}")

    def op_aax(self):
        if self.stack:
            self.mod_dec(15)
        x = self.dbus.read(self.uaddr) & 0xFFFFFFFF
        self.acc = self.acc & x
        self.set_log()
        # info(f"ACC: {self.acc:>08X}")

    def op_aex(self):
        if self.stack:
            self.mod_dec(15)
        x = self.dbus.read(self.uaddr) & 0xFFFFFFFF
        self.acc = self.acc ^ x
        self.set_log()
        # info(f"ACC: {self.acc:>08X}")

    def op_aox(self):
        if self.stack:
            self.mod_dec(15)
        x = self.dbus.read(self.uaddr) & 0xFFFFFFFF
        self.acc = self.acc | x
        self.set_log()
        # info(f"ACC: {self.acc:>08X}")

    def op_utc(self):
        self.c = self.uaddr
        self.c_active = True

    def op_wtc(self):
        if self.stack:
            self.mod_dec(15)
        self.c = self.dbus.read(self.uaddr)
        self.c_active = True

    def op_utm(self):
        t = self.op_indx & 0xF
        if t != 0:
            self.m[t] = self.uaddr

    def op_vtm(self):
        self.m[self.op_indx] = self.vaddr

    def op_mtj(self):
        t = self.vaddr & 0xF
        if t != 0:
            self.m[t] = self.m[self.op_indx]

    def op_jaddm(self):
        t = self.vaddr & 0xF
        if t != 0:
            self.m[t] = (self.m[t] + self.m[self.op_indx]) & 0xFFFF

    def op_vim(self):
        if self.m[self.op_indx] != 0:
            self.pc_next = self.vaddr
            self.is_left = True
    
    def op_vzm(self):
        if self.m[self.op_indx] == 0:
            self.pc_next = self.vaddr
            self.is_left = True

    def op_stop(self):
        self.running = False
        print(f"CPU halted at {self.pc:>04X} with {self.op_addr:>04X}")
        if self.op_addr == 0o12345:
            print("Success")
        elif self.op_addr == 0o76543:
            print("Failure")

    def op_uj(self):
        self.is_left = True
        self.pc_next = self.uaddr

    def op_uia(self):
        if self.omega:
            self.pc_next = self.uaddr
            self.is_left = True
        # self.rmr = self.acc

    def op_uza(self):
        if not self.omega:
            self.pc_next = self.uaddr
            self.is_left = True

    def print_insn(self):
        if self.op_indx == 0:
            print(f"{self.pc:>04X}: {OP_CODE[self.op_code]} {self.op_addr:>04X}")
        else:
            print(
                f"{self.pc:>04X}: {OP_CODE[self.op_code]} {self.op_addr:>04X}(M{self.op_indx}={self.m[self.op_indx]:>04X})")

    def step(self):
        self.commands -= 1
        if self.commands <= 0:
            self.running = False
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

        self.print_insn()

        if self.op_code == OP_ATX:
            self.op_atx()
        elif self.op_code == OP_ATI:
            self.op_ati()
        elif self.op_code == OP_ITA:
            self.op_ita()
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
        elif self.op_code == OP_WTC:
            self.op_wtc()
        elif self.op_code == OP_UTM:
            self.op_utm()
        elif self.op_code == OP_VTM:
            self.op_vtm()
        elif self.op_code == OP_MTJ:
            self.op_mtj()
        elif self.op_code == OP_JADDM:
            self.op_jaddm()
        elif self.op_code == OP_VIM:
            self.op_vim()
        elif self.op_code == OP_VZM:
            self.op_vzm()
        elif self.op_code == OP_STOP:
            self.op_stop()
        elif self.op_code == OP_UJ:
            self.op_uj()
        elif self.op_code == OP_UIA:
            self.op_uia()
        elif self.op_code == OP_UZA:
            self.op_uza()
        else:
            self.running = False
            print("Unknown instruction at:")
            self.print_insn()

        self.pc = self.pc_next

    def run(self, num=100):
        self.commands = num
        self.running = True
