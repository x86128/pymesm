import array
from math import ldexp, frexp

MASK7 = 0x7F
MASK12 = 0xFFF
MASK15 = 0x7FFF
MASK24 = 0xFFFFFF
MASK40 = 0x0FFFFFFFFFF
MASK41 = 0x1FFFFFFFFFF
MASK42 = 0x3FFFFFFFFFF
MASK48 = 0xFFFFFFFFFFFF

BIT20 = 1 << 19
BIT19 = 1 << 18
BIT40 = 1 << 39
BIT41 = 1 << 40
BIT42 = 1 << 41

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
                    'esubx', 'eaddn', 'xtr', 'rte', 'e32', 'e33',
                    'e46', 'e47', 'e36', 'e20', 'e21', 'esub', 'esubx',
                    'e50', 'e51', 'e52', 'e53', 'e54', 'e55', 'e56', 'e57',
                    'e60', 'e61', 'e62', 'e63', 'e64', 'e65', 'e66', 'e67',
                    'e70', 'e71', 'e72', 'e73', 'e74', 'e75', 'e76', 'e77']


def tobesm(x):
    m, e = frexp(x)

    if m < 0:
        m = int(-m * BIT41)
        m = ((m ^ MASK41) + 1) & MASK41
    else:
        m = int(m * BIT41)

    e += 64
    # нормализуем влево, если 41-й и 40-й биты отличаются
    while (m & BIT41 == 0) == (m & BIT40 == 0):
        m = (m << 1) & MASK41
        e -= 1
        if e < 0:
            break
    if e < 0:  # underflow
        return 0

    # упаковываем число
    e &= 0o177
    m &= MASK41
    return (e << 41) | m


def frombesm(x):
    e, m = (x & 0xFE0000000000) >> 41, x & MASK41
    if m & BIT41:
        m = -float(- m & MASK41)
    return ldexp(m, e - 64 - 40)


def norm(self, exp, mnt, rmr, rnd_rq):
    rounded = False
    if self.norm_ena:
        while (mnt & BIT41 == 0) == (mnt & BIT40 == 0):
            mnt = (mnt << 1) & MASK42
            if rmr & 0x8000000000:
                mnt |= 1
                rounded = True
            rmr = (rmr << 1) & MASK40
            exp -= 1
            if exp < 0:
                break
    if exp < 0:
        return 0, 0
    if self.round_ena and not rounded:
        mnt |= 1
    return exp, mnt


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
        self.rmr = 0

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
        if self.f_log:
            return self.acc != 0
        elif self.f_add:
            return self.acc & BIT41 != 0
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

    @property
    def norm_ena(self):
        return self.rr_reg & 1 == 0

    @property
    def round_ena(self):
        return self.rr_reg & 2 == 0

    def fetch(self):
        self.cmd_cache = self.ibus.read(self.pc)

    def decode(self):
        if self.is_left:
            w = (self.cmd_cache >> 24) & MASK24
        else:
            w = self.cmd_cache & MASK24

        self.op_indx = (w >> 20) & 0xF
        if w & BIT20 == 0:  # short address command
            self.op_code = (w >> 12) & 0o77
            self.op_addr = w & MASK12
            if w & BIT19 != 0:  # address is extended
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
            print(f"  ACC = {self.acc:>016o} ({frombesm(self.acc)})")

    def rmr_wr(self, rmr):
        self.rmr = rmr
        if self.trace:
            print(f"  RMR = {self.rmr:>016o}")

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

    def op_ntr(self):
        self.rr_reg = self.uaddr & 0x3F
        if self.trace:
            print(f"  RR = {self.rr_reg:>06b}")

    def negate(self, x):
        e, m = (x >> 41) & MASK7, x & MASK41
        if m & BIT41:
            m |= BIT42
        m = ((MASK42 ^ m) + 1) & MASK42

        if (m & BIT42 == 0) != (m & BIT41 == 0):
            e += 1
            if m & 1:
                self.rmr = (self.rmr >> 1) | (1 << 39)
            m >>= 1
        # нормализуем влево, если 41-й и 40-й биты отличаются
        while self.norm_ena and (m & BIT41 == 0) == (m & BIT40 == 0):
            m = (m << 1) & MASK41
            e -= 1
            if e < -1:
                break
        return e, m

    def op_add(self):
        if self.stack:
            self.sp -= 1
        x = self.dbus.read(self.uaddr)
        e, m = (x >> 41) & MASK7, x & MASK41
        self.add(self.acc, e, m)
        self.set_add()

    def op_sub(self):
        if self.stack:
            self.sp -= 1
        x = self.dbus.read(self.uaddr)
        e, m = self.negate(x)
        self.add(self.acc, e, m)
        self.set_add()

    def op_rsub(self):
        if self.stack:
            self.sp -= 1
        e, m = self.negate(self.acc)
        self.add(self.dbus.read(self.uaddr), e, m)
        self.set_add()

    def add(self, a, b_exp, b_mnt):
        a_exp, a_mnt = (a >> 41) & MASK7, a & MASK41
        # b_exp, b_mnt = (b >> 41) & MASK7, b & MASK41
        if a_exp < b_exp:
            a_exp, b_exp = b_exp, a_exp
            a_mnt, b_mnt = b_mnt, a_mnt

        a_sgn = (a_mnt & BIT41) != 0
        b_sgn = (b_mnt & BIT41) != 0

        rmr = self.rmr & MASK40
        rnd_rq = 0
        while a_exp > b_exp:
            b_exp += 1
            if b_mnt & 1:
                rnd_rq |= 1
            rmr = rmr >> 1 | ((b_mnt & 1) << 39)
            b_mnt >>= 1
            if b_sgn:
                b_mnt |= BIT41

        if b_sgn:
            b_mnt |= BIT42
        if a_sgn:
            a_mnt |= BIT42

        a_mnt = (a_mnt + b_mnt) & MASK42

        # шаг нормализации вправо после сложения
        if (a_mnt & BIT42 == 0) != (a_mnt & BIT41 == 0):
            a_exp += 1
            rmr = rmr >> 1 | ((a_mnt & 1) << 39)
            if a_mnt & 1:
                rnd_rq |= 1
            a_mnt >>= 1
            if a_exp > 0o177:
                print("WARN: Exponent overflow")
                self.failure = True
                a_exp = 0o177

        if self.norm_ena:
            while (a_mnt & BIT40 == 0) == (a_mnt & BIT41 == 0):
                a_mnt = (a_mnt << 1) & MASK41
                if rmr & BIT40:
                    rnd_rq = 0
                    a_mnt |= 1
                rmr = (rmr << 1) & MASK40
                a_exp -= 1
                if a_exp < 0:
                    a_exp, a_mnt = 0, 0
                    rmr = 0
                    break

        if self.round_ena and rnd_rq:
            a_mnt |= 1

        self.rmr_wr(rmr)
        self.acc_wr((a_exp << 41) | (a_mnt & MASK41))

    def op_yta(self):
        if self.f_log:
            self.acc_wr(self.rmr)
        else:
            e = ((self.acc >> 41) & 0x7F + self.uaddr & 0x7F - 64) & 0x7F
            m = self.rmr & MASK40
            while self.norm_ena and (m & BIT41 == 0) == (m & BIT40 == 0):
                m = (m << 1) & MASK41
                e -= 1
                if e < 0:
                    break
            if e < 0:  # underflow
                e, m = 0, 0
            # упаковываем число
            e &= 0o177
            m &= MASK41
            self.acc_wr((e << 41) | m)

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
