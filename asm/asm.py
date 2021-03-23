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
    irom = [('NONE',0o102,0)] * 131072 # fill with MODA
    dram = [0] * 65536

    lbls = {}
    names = {}

    while t.curr[0] != 'NONE':
        if t.curr[0] == 'IDENT':
            if t.curr[3].lower() in keywords:
                kwrd = t.curr[3].lower()
                if kwrd == 'org':
                    PC = 2 * eval(t.next[3])
                    t.advance()
                    print(f"PC set to {PC>>1:0>4X}")
                elif kwrd == 'dorg':
                    DP = eval(t.next[3])
                    t.advance()
                    print(f"DP set to {DP:0>4X}")
                elif kwrd == 'ptr':
                    t.advance()
                    name = t.curr[3]
                    t.advance()
                    addr = eval(t.curr[3])
                    names[name] = (name, addr)
                    print(f"PTRS set {(name, addr)}")
                elif kwrd == 'lbl':
                    if PC % 1 == 1:
                        irom[PC] = ('CMD',0o102, 0)  # MODA
                        PC += 1
                    names[t.next[3]] = (t.curr[3], PC>>1)
                    print(f"Label set to {(t.curr[3], PC>>1)}")
                    t.advance()
                elif kwrd == 'arr':
                    t.advance()
                    name = t.curr[3]
                    t.advance()
                    text = t.curr[3]
                    names[name] = (name, DP)
                    for c in text:
                        dram[DP] = ord(c)
                        DP += 1
                else:
                    print(f"Unimplemented keyword: {kwrd}")
                    raise Exception("UnimplementedKeyword")
            elif t.curr[3].upper() in OPCODES:
                op = t.curr[3].upper()
                t.advance()
                name = t.curr[3]
                offset = 0
                if t.curr[0] == 'NUMBER':
                    addr = eval(t.curr[3])
                    irom[PC] = ('CMD', OPCODES[op], addr)
                    print(f"PC: {PC>>1:0>4X}.{PC&1} {op} {addr}")
                else:
                    if t.next[0] == 'BRACE': # arr access
                        t.advance()
                        t.advance()
                        offset = eval(t.curr[3])
                        t.advance()
                    else:
                        offset = 0
                    if name in names:
                        addr = names[name][1]+offset
                        irom[PC] = ('CMD', OPCODES[op], addr)
                        print(f"PC: {PC>>1:0>4X}.{PC&1} {op} {name}+{offset}:{addr}")
                    else:
                        print(f"PC: {PC>>1:0>4X}.{PC&1} {op} {name}+{offset}:FIX")
                        irom[PC] = ('FIX', OPCODES[op], name, offset)
                PC += 1
            else:
                print(f"Unknown assembler command: {t.curr[3]}")
                raise Exception()
        else:
            print(f"Error at line {t.curr[1]}: keyword or command required")
            raise Exception("AssemblyError")
        t.advance()

    # do fixups
    for i in range(131072):
        if irom[i][0] == 'FIX':
            if irom[i][2] in names:
                irom[i] = ('CMD', irom[i][1], names[irom[i][2]][1]+irom[i][3])
            else:
                print(f"Undefined symbol: {irom[i][2]}")
                raise Exception("UndefinedSymbol")

    if len(sys.argv) == 3:
        output = sys.argv[2]
    else:
        output = sys.argv[1][:-4]+".oct"
    
    with open(output,'wt') as out:
        # do irom print out
        for pc in range(0,131072,2):
            if irom[pc][0] != 'NONE':
                opc = pc >> 1
                left_idx = 0 << 24
                left_op = irom[pc][1] << 16
                left_addr = irom[pc][2]
                left = left_idx | left_op | left_addr
                right_idx = 0 << 32
                right_op = irom[pc+1][1] << 16
                right_addr = irom[pc+1][2]
                right = right_idx | right_op | right_addr
                out.write(f"i {opc:>04X} {left:>08X} {right:>08X}\n")
        # do dram print out
        for dp in range(65536):
            if dram[dp] != 0:
                out.write(f"d {dp:>04X} 00 {dram[dp]:>08X}\n")