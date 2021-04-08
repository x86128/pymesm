import array

MASK12 = 0xFFF
MASK15 = 0x7FFF
MASK24 = 0xFFFFFF
MASK48 = 0xFFFFFFFFFFFF
BIT19 = 1 << 19
BIT18 = 1 << 18

op_names = ['atx', 'stx', 'mod', 'xts', 'add', 'sub', 'rsub', 'amx',
            'xta', 'aax', 'aex', 'arx', 'avx', 'aox', 'div', 'mul',
            'apx', 'aux', 'acx', 'anx', 'eaddx', 'esubx', 'asx', 'xtr',
            'rte', 'yta', 'e32', 'e33', 'eaddn', 'esub', 'asn', 'ntr',
            'ati', 'sti', 'ita', 'its', 'mtj', 'jaddm', 'e46', 'e47',
            'e50', 'e51', 'e52', 'e53', 'e54', 'e55', 'e56', 'e57',
            'e60', 'e61', 'e62', 'e63', 'e64', 'e65', 'e66', 'e67',
            'e70', 'e71', 'e72', 'e73', 'e74', 'e75', 'e76', 'e77',
            'e20', 'e21', 'utc', 'wtc', 'vtm', 'utm', 'uza', 'uia',
            'uj', 'vjm', 'ij', 'stop', 'vzm', 'vim', 'e36', 'vlm']
op_codes = {op: i for i, op in enumerate(op_names)}

op_unimplemented = ['mod', 'amx', 'apx', 'aux', 'acx', 'anx', 'eaddx',
                    'esubx', 'eaddn', 'xtr', 'rte', 'yta', 'e32', 'e33',
                    'e46', 'e47', 'e36', 'e20', 'e21', 'esub', 'esubx', 'ntr',
                    'e50', 'e51', 'e52', 'e53', 'e54', 'e55', 'e56', 'e57',
                    'e60', 'e61', 'e62', 'e63', 'e64', 'e65', 'e66', 'e67',
                    'e70', 'e71', 'e72', 'e73', 'e74', 'e75', 'e76', 'e77']


class CPU:
    def __init__(self, ibus, dbus):
        self.pc = 1
        self.commands = 100
        self.ibus = ibus
        self.dbus = dbus

        self.running = False
        self.failure = False

        self.interrupt = False
        self.c = 0
        self.c_active = False

        self.acc = 0

        # index registers
        self._m = array.array('H', [0] * 16)
        self._k = array.array('H', [0] * 16)
        self.m_reg = self._m

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

        self.trace = False

        for op in op_unimplemented:
            setattr(self, f"op_{op}", self.op_unimpl)

        self._opcodes = [getattr(self, f"op_{op}") for op in op_names]

    @property
    def m(self):
        return self.m_reg[self.op_indx]

    @property
    def sp(self):
        return self.m_reg[15] & MASK15

    @sp.setter
    def sp(self, addr):
        self.m_reg[15] = addr & MASK15
        if self.trace:
            print(f"  M[15] = {self.m_reg[15]:>05o}")

    @property
    def uaddr(self):
        return (self.m + self.vaddr) & MASK15

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

    def set_trace(self):
        self.trace = True
        self.dbus.trace = True
        self.ibus.trace = True

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
            w = (self.cmd_cache >> 24) & MASK24
        else:
            w = self.cmd_cache & MASK24

        self.op_indx = (w >> 20) & 0xF
        if w & BIT19 == 0:  # short address command
            self.op_code = (w >> 12) & 0o77
            self.op_addr = w & MASK12
            if w & BIT18 != 0:  # address is extended
                self.op_addr |= 0o70000
        else:  # long address command
            self.op_code = ((w >> 15) & 0o37) + 48
            self.op_addr = w & MASK15

        if self.c_active:
            self.vaddr = (self.op_addr + self.c) & MASK15
        else:
            self.vaddr = self.op_addr
        self.c_active = False

        self.stack = False
        if self.op_indx == 15:
            if self.vaddr == 0:
                self.stack = True
            elif self.op_code == 0o41 and self.uaddr == 15:
                self.stack = True

    def m_wr(self, i, val):
        i = i & 0xF
        if i != 0:
            self.m_reg[i] = val & MASK15
            if self.trace:
                print(f"  M[{i}] = {self.m_reg[i]:>05o}")

    def m_rd(self, i):
        return self.m_reg[i & 0xF] & MASK15

    def acc_wr(self, val):
        self.acc = val & MASK48
        if self.trace:
            print(f"  ACC = {self.acc:>016o}")

    def op_atx(self):
        self.dbus.write(self.uaddr, self.acc)
        if self.stack:
            self.sp += 1

    def op_ati(self):
        self.m_wr(self.uaddr, self.acc)

    def op_ita(self):
        self.acc_wr(self.m_rd(self.uaddr))
        self.set_log()

    def op_stx(self):
        self.dbus.write(self.uaddr, self.acc)
        self.sp -= 1
        self.acc_wr(self.dbus.read(self.sp))
        self.set_log()

    def op_sti(self):  # uh oh instruction
        if not self.stack:
            self.sp -= 1
        self.m_wr(self.uaddr, self.acc)
        self.acc_wr(self.dbus.read(self.sp))
        self.set_log()

    def op_its(self):
        self.dbus.write(self.sp, self.acc)
        self.sp += 1
        self.acc_wr(self.m_rd(self.uaddr))
        self.set_log()

    def op_xts(self):
        self.dbus.write(self.sp, self.acc)
        self.sp += 1
        self.acc_wr(self.dbus.read(self.uaddr))
        self.set_log()

    def op_add(self):
        if self.stack:
            self.sp -= 1
        self.acc_wr(self.acc + self.dbus.read(self.uaddr))
        self.set_add()

    def op_sub(self):
        if self.stack:
            self.sp -= 1
        self.acc_wr(self.acc - self.dbus.read(self.uaddr))
        self.set_add()

    def op_rsub(self):
        if self.stack:
            self.sp -= 1
        self.acc_wr(self.dbus.read(self.uaddr) - self.acc)
        self.set_add()

    def op_avx(self):
        if self.stack:
            self.sp -= 1
        self.acc_wr(-self.acc)
        self.set_add()

    def op_div(self):
        if self.stack:
            self.sp -= 1
        self.acc_wr(self.acc / (self.dbus.read(self.uaddr)))
        self.set_mul()

    def op_mul(self):
        if self.stack:
            self.sp -= 1
        self.acc_wr(self.acc * self.dbus.read(self.uaddr))
        self.set_mul()

    def op_asx(self):
        if self.stack:
            self.sp -= 1
        n = self.dbus.read(self.uaddr)
        result = self.acc
        if n >= 64:
            result >>= (n - 64)
        else:
            result <<= (64 - n)
        self.acc_wr(result)
        self.set_log()

    def op_asn(self):
        n = self.uaddr
        result = self.acc
        if n >= 64:
            result >>= (n - 64)
        else:
            result <<= (64 - n)
        self.acc_wr(result)
        self.set_log()

    def op_xta(self):
        if self.stack:
            self.sp -= 1
        self.acc_wr(self.dbus.read(self.uaddr))
        self.set_log()

    def op_aax(self):
        if self.stack:
            self.sp -= 1
        x = self.dbus.read(self.uaddr)
        self.acc_wr(self.acc & x)
        self.set_log()

    def op_arx(self):
        if self.stack:
            self.sp -= 1
        ua = self.acc
        ux = self.dbus.read(self.uaddr)
        t = ua + ux
        if t > MASK48:
            t += 1
        self.acc_wr(t)
        self.set_mul()

    def op_aex(self):
        if self.stack:
            self.sp -= 1
        x = self.dbus.read(self.uaddr)
        self.acc_wr(self.acc ^ x)
        self.set_log()

    def op_aox(self):
        if self.stack:
            self.sp -= 1
        x = self.dbus.read(self.uaddr)
        self.acc_wr(self.acc | x)
        self.set_log()

    def op_utc(self):
        self.c = self.uaddr
        self.c_active = True

    def op_wtc(self):
        if self.stack:
            self.sp -= 1
        self.c = self.dbus.read(self.uaddr) & MASK15
        self.c_active = True

    def op_utm(self):
        self.m_wr(self.op_indx, self.uaddr)

    def op_vtm(self):
        self.m_wr(self.op_indx, self.vaddr)

    def op_mtj(self):
        self.m_wr(self.vaddr, self.m)

    def op_jaddm(self):
        self.m_wr(self.vaddr, self.m_rd(self.vaddr) + self.m)

    def op_vim(self):
        if self.m != 0:
            self.pc_next = self.vaddr
            self.is_left = True

    def op_vzm(self):
        if self.m == 0:
            self.pc_next = self.vaddr
            self.is_left = True

    def op_vjm(self):
        self.pc_next = self.vaddr
        self.is_left = True
        self.m_wr(self.op_indx, self.pc + 1)

    def op_vlm(self):
        if self.m != 0:
            self.pc_next = self.vaddr
            self.is_left = True
            self.m_wr(self.op_indx, self.m + 1)

    def op_stop(self):
        self.running = False
        print(f"CPU halted at {self.pc:>05o} with {self.op_addr:>05o}")
        if self.op_addr == 0o12345:
            print("Success")
        elif self.op_addr == 0o76543:
            self.failure = True
            print("Failure")

    def op_uj(self):
        self.is_left = True
        self.pc_next = self.uaddr

    def op_ij(self):
        pass

    def op_uia(self):
        if self.omega:
            self.pc_next = self.uaddr
            self.is_left = True
        # self.rmr = self.acc

    def op_uza(self):
        if not self.omega:
            self.pc_next = self.uaddr
            self.is_left = True

    def op_unimpl(self):
        self.running = False
        print(f"Unimplemented instruction at: {self.pc}")
        self.print_insn()

    def print_insn(self):
        if self.op_indx == 0:
            print(f"{self.pc:>05o}: {op_names[self.op_code]} {self.op_addr:>05o}")
        else:
            print(
                f"{self.pc:>05o}: {op_names[self.op_code]} {self.op_addr:>05o},M{self.op_indx}")

    def step(self):
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

        if self.trace:
            self.print_insn()

        self._opcodes[self.op_code]()

        self.pc = self.pc_next
        self.commands -= 1

    def run(self, num=100):
        self.commands = num
        self.running = True
