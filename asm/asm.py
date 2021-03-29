import sys
from tok import Tokenizer
from opcodes import OPCODES


def print_usage():
    print("Usage:")
    print("asm.py input.asm [output.oct]")


keywords = ['ptr', 'org', 'dorg', 'arr', 'mem', 'lbl']

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()

    if not sys.argv[1].endswith(".asm"):
        print(".asm extension required")
        print_usage()
    source = open(sys.argv[1]).read()
    t = Tokenizer(source)

    PC = 0
    DP = 0
    irom = [('NONE', 0, 0o102, 0)] * 131072  # fill with MODA
    dram = [0] * 65536

    lbls = {}
    names = {}


    def get_number(tok):
        # try unary first "- NUMBER"
        if tok.peek('BINOP') and tok.curr.val == '-':
            if tok.next.typ == 'NUMBER':
                bop = t.get('BINOP').val
                return eval(bop + t.get('NUMBER').val)
        # than just "NUMBER"
        elif tok.peek('NUMBER'):
            return eval(t.get('NUMBER').val)
        else:
            print(f"line: {tok.curr.line}: Expected number, got ", tok.curr.typ)
            sys.exit(1)

    def get_number_array(tok):
        result = []
        while True:
            # try unary first "- NUMBER"
            if tok.peek('BINOP') and tok.curr.val == '-':
                if tok.next.typ == 'NUMBER':
                    bop = t.get('BINOP').val
                    result.append(eval(bop + t.get('NUMBER').val))
            # than just "NUMBER"
            elif tok.peek('NUMBER'):
                result.append(eval(t.get('NUMBER').val))
            else:
                print("Expected number, got ", tok.curr)
                sys.exit(1)
            if t.peek('COMMA'):
                t.get('COMMA')
                continue
            else:
                break
        return result


    while not t.peek('NONE'):
        if t.peek('IDENT'):
            cmd = t.get('IDENT')
            kwrd = cmd.val.lower()
            if kwrd in keywords:
                if kwrd == 'org':
                    PC = 2 * (get_number(t) & 0xFFFF)
                    print(f"PC set to {PC >> 1:0>4X}")
                elif kwrd == 'dorg':
                    DP = get_number(t) & 0xFFFF
                    print(f"DP set to {DP:0>4X}")
                elif kwrd == 'ptr':
                    name = t.get('IDENT').val
                    addr = get_number(t) & 0xFFFF
                    names[name] = (name, addr)
                    print(f"PTR set {(name, addr)}")
                elif kwrd == 'lbl':
                    if PC & 1 == 1:
                        irom[PC] = ('CMD', 0, 0o102, 0)  # MODA
                        PC += 1
                    name = t.get('IDENT').val
                    names[name] = (name, PC >> 1)
                    print(f"Label set to {(name, PC >> 1)}")
                elif kwrd == 'arr':
                    name = t.get('IDENT').val
                    names[name] = (name, DP)
                    # array of chars in "STRING"
                    if t.peek('STRING'):
                        for c in t.get('STRING').val:
                            dram[DP] = ord(c)
                            DP += 1
                    # array of "NUMBER"
                    elif t.peek('BRACE'):
                        t.get('BRACE')
                        for val in get_number_array(t):
                            dram[DP] = val & 0xFFFFFFFF
                            DP += 1
                        t.get('BRACE')
                    # single constant
                    elif t.peek('BINOP') or t.peek('NUMBER'):
                        val = get_number(t) & 0xFFFFFFFF
                        dram[DP] = val
                        DP += 1
                    else:
                        print(f"line: {t.curr.line} Array declaration syntax error")
                        sys.exit(1)
                elif kwrd == 'mem':
                    name = t.get('IDENT').val
                    names[name] = (name, DP)
                    DP += get_number(t)
                else:
                    print(f"Unimplemented keyword: {kwrd}")
                    sys.exit(1)
            elif kwrd in OPCODES:
                op = kwrd
                offset = 0
                addr = 0
                indx = 0
                # try "OP NUMBER"
                if t.peek('NUMBER'):
                    addr = get_number(t) & 0xFFFF
                    # irom[PC] = ('CMD', OPCODES[op], addr)
                    print(f"PC: {PC >> 1:0>4X}.{PC & 1} {op} {addr}")
                # than "OP -NUMBER"
                elif t.peek('BINOP'):
                    addr = get_number(t) & 0xFFFF
                    # irom[PC] = ('CMD', OPCODES[op], addr)
                    print(f"PC: {PC >> 1:0>4X}.{PC & 1} {op} {addr}")
                else:
                    # than "OP NAME[+-NUMBER]"
                    name = t.get('IDENT').val
                    if t.peek('BRACE'):  # arr access
                        t.get('BRACE')
                        offset = get_number(t) & 0xFFFF
                        t.get('BRACE')
                    # than "OP NAME+-OFFSET"
                    elif t.peek('BINOP'):
                        bop = t.get('BINOP').val
                        if bop == '+':
                            offset = eval(t.get('NUMBER').val)
                        elif bop == '-':
                            offset = 0 - eval(t.get('NUMBER').val)
                        else:
                            print(f"line: {t.curr.line}: Unexpected bin_op {bop}.")
                            sys.exit(1)
                    # than just "OP NAME"
                    else:
                        offset = 0
                    if name in names:
                        addr = (names[name][1] + offset) & 0xFFFF
                        print(f"PC: {PC >> 1:0>4X}.{PC & 1} {op} {name}+{offset}:{addr}")
                    else:
                        addr = (name, offset)
                        print(f"PC: {PC >> 1:0>4X}.{PC & 1} {op} {name}+{offset}:FIX")
                # index register suffix "xta 123,15"
                if t.peek('COMMA'):
                    t.get('COMMA')
                    indx = get_number(t)

                if isinstance(addr, tuple):
                    irom[PC] = ('FIX', indx, OPCODES[op], addr[0], addr[1])
                else:
                    irom[PC] = ('CMD', indx, OPCODES[op], addr)
                PC += 1
            else:
                print(f"line: {cmd.line}: Unknown assembler command: {kwrd}")
                sys.exit(1)
        else:
            print(f"line {t.curr.line}: keyword or command required")
            sys.exit(1)

    # do fixups
    for i in range(131072):
        if irom[i][0] == 'FIX':
            if irom[i][3] in names:
                irom[i] = ('CMD', irom[i][1], irom[i][2], names[irom[i][3]][1] + irom[i][4])
            else:
                print(f"Undefined symbol: {irom[i][3]}")
                raise Exception("UndefinedSymbol")

    if len(sys.argv) == 3:
        output = sys.argv[2]
    else:
        output = sys.argv[1][:-4] + ".oct"

    with open(output, 'wt') as out:
        # do irom print out
        for pc in range(0, 131072, 2):
            if irom[pc][0] != 'NONE':
                opc = pc >> 1
                left_idx = irom[pc][1] << 24
                left_op = irom[pc][2] << 16
                left_addr = irom[pc][3]
                left = left_idx | left_op | left_addr
                right_idx = irom[pc + 1][1] << 24
                right_op = irom[pc + 1][2] << 16
                right_addr = irom[pc + 1][3]
                right = right_idx | right_op | right_addr
                out.write(f"i {opc:>04X} {left:>08X} {right:>08X}\n")
        # do dram print out
        for dp in range(65536):
            if dram[dp] != 0:
                out.write(f"d {dp:>04X} 00 {dram[dp]:>08X}\n")
