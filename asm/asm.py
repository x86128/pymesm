import sys
from tok import Tokenizer
from opcodes import OPCODES


def print_usage():
    print("Usage:")
    print("asm.py input.asm [output.asm]")


keywords = ['ptr', 'org', 'arr', 'mem', 'lbl']

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()

    if not sys.argv[1].endswith(".asm"):
        print(".asm extension required")
        print_usage()
    source = open(sys.argv[1]).read()
    t = Tokenizer(source)

    PC = 0
    ptrs = {}
    lbls = {}

    while t.curr[0] != 'NONE':
        if t.curr[0] == 'IDENT':
            if t.curr[3].lower() in keywords:
                kwrd = t.curr[3].lower()
                if kwrd == 'org':
                    PC = 2 * eval(t.next[3])
                    t.advance()
                    print(f"PC set to {PC:0>4X}")
                elif kwrd == 'ptr':
                    t.advance()
                    name = t.curr[3]
                    t.advance()
                    addr = eval(t.curr[3])
                    ptrs[name] = (name, addr)
                    print(f"PTRS set {(name, addr)}")
                elif kwrd == 'lbl':
                    if PC % 1 == 1:
                        # TODO: gen MODA (NOP)
                        PC += 1
                    lbls[t.next[3]] = (t.curr[3], PC)
                    print(f"Label set to {(t.curr[3], PC)}")
                    t.advance()
                else:
                    print("Unimplemented keyword")
                    raise Exception("UnimplementedKeyword")
            elif t.curr[3].upper() in OPCODES:
                print(f"PC: {PC:0>4X} {t.curr[3]} {t.next[3]}")
                t.advance()
                PC += 1
            else:
                print(f"Unknown assembler command: {t.curr[3]}")
                raise Exception()
        else:
            print(f"Error at line {t.curr[1]}: keyword or command required")
            raise Exception("AssemblyError")
        t.advance()
