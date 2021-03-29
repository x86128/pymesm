#!/usr/bin/python3

import sys
import os.path
import argparse
from tok import Tokenizer
from opcodes import OPCODES

argp = argparse.ArgumentParser()
argp.add_argument("-i", required=True, dest="input", type=str, help="Input asm file")
argp.add_argument("-o", required=False, dest="output", type=str, help="Output *.oct filename")
argp.add_argument("-l", default=False, dest="listing", action="store_true", help="Print listing")
args = argp.parse_args()

input_file = args.input
if not input_file.endswith('.asm'):
    print("Input file must ends with .asm")
    sys.exit(2)

output_file = args.output
if output_file is None:
    output_file = os.path.splitext(input_file)[0] + '.oct'

keywords = ['ptr', 'org', 'dorg', 'arr', 'mem', 'lbl']

if __name__ == '__main__':
    source = open(input_file).read()
    t = Tokenizer(source)

    PC = 0
    DP = 0
    irom = [('NONE', 0, 0o102, 0)] * 131072  # fill with MODA
    dram = [0] * 65536

    names = {}


    def get_number(tok):
        # try unary first "- NUMBER"
        if binop := tok.get('BINOP'):
            if num := tok.get('NUMBER'):
                return eval(binop.val + num.val)
            else:
                return None
        # then just "NUMBER"
        elif num := tok.get('NUMBER'):
            return eval(num.val)
        else:
            return None


    def get_number_array(tok):
        result = []
        if not t.get('BRACE'):
            return None
        while True:
            if num := get_number(tok):
                result.append(num)
            else:
                return None
            if t.get('COMMA'):
                continue
            elif t.get('BRACE'):
                break
            else:
                return None
        return result


    error_count = 0
    while not t.eof:
        if keyword := t.get('IDENT'):
            kwrd = keyword.val.lower()
            line = keyword.line
            if kwrd in keywords:
                if kwrd == 'org':
                    if op_addr := get_number(t):
                        PC = 2 * (op_addr & 0xFFFF)
                    else:
                        print(f"at line {line}: ORG: correct address required")
                        error_count += 1
                        break
                elif kwrd == 'dorg':
                    if op_addr := get_number(t):
                        DP = op_addr & 0xFFFF
                    else:
                        print(f"at line {line}: DataORG: correct address required")
                        error_count += 1
                        break
                elif kwrd == 'ptr':
                    if name := t.get('IDENT'):
                        if op_addr := get_number(t):
                            names[name] = (name.val, op_addr & 0xFFFF)
                    else:
                        print(f"at line {line}: PTR: identifier required")
                        error_count += 1
                        break
                elif kwrd == 'lbl':
                    if name := t.get('IDENT'):
                        if PC & 1 == 1:
                            irom[PC] = ('CMD', 0, 0o102, 0)  # MODA or UTC 0
                            PC += 1
                        names[name.val] = (name.val, PC >> 1)
                    else:
                        print(f"at line {line}: LBL: identifier required")
                        error_count += 1
                        break
                elif kwrd == 'arr':
                    if name := t.get('IDENT'):
                        if name.val in names:
                            print(f"at line {line}: {name.val} already defined")
                            error_count += 1
                            break
                        names[name.val] = (name.val, DP)
                        # array of chars in "STRING"
                        if chars := t.get('STRING'):
                            for c in chars.val:
                                dram[DP] = ord(c)
                                DP += 1
                        # array of "NUMBER"
                        elif array := get_number_array(t):
                            for val in array:
                                dram[DP] = val & 0xFFFFFFFF
                                DP += 1
                        # single constant
                        elif val := get_number(t):
                            dram[DP] = val & 0xFFFFFFFF
                            DP += 1
                        else:
                            print(f"at line: {line}: array declaration syntax error")
                            error_count += 1
                            break
                    else:
                        print(f"line: {line} Array declaration syntax error")
                        error_count += 1
                        break
                elif kwrd == 'mem':
                    if name := t.get('IDENT'):
                        if name.val in names:
                            print(f"at line {line}: {name.val} already defined")
                            error_count += 1
                            break
                        names[name.val] = (name.val, DP)
                        DP += get_number(t)
                else:
                    print(f"Unimplemented keyword: {kwrd}")
                    error_count += 1
                    break
            elif kwrd in OPCODES:
                op = kwrd
                op_offset = 0
                op_addr = 0
                op_indx = 0
                sym = ""
                # try "OP NUMBER"
                if (addr := get_number(t)) is not None:
                    op_addr = addr & 0xFFFF
                # then "OP NAME[+-NUMBER]"
                elif name := t.get('IDENT'):
                    sym = name.val
                    if t.get('BRACE'):
                        if addr := get_number(t):
                            op_offset = addr & 0xFFFF
                            if not t.get('BRACE'):
                                print(f"at line {line}: ] brace required")
                                error_count += 1
                                break
                        else:
                            print(f"at line {line}: number required")
                            error_count += 1
                            break
                    # then "OP NAME+-OFFSET"
                    elif offset := get_number(t):
                        op_offset = offset & 0xFFFF
                    # then just "OP NAME"
                    else:
                        op_offset = 0
                    if name.val in names:
                        op_addr = (names[name.val][1] + op_offset) & 0xFFFF
                    else:
                        op_addr = (name.val, op_offset)
                # index register suffix "xta 123,15"
                if t.get('COMMA'):
                    if indx := get_number(t):
                        op_indx = indx & 0xF
                    else:
                        print(f"at line {line}: index register number required")
                        error_count += 1
                        break
                # check if we need add symbol to fixup table
                if isinstance(op_addr, tuple):
                    irom[PC] = ('FIX', op_indx, OPCODES[op], op_addr[0], op_addr[1])
                else:
                    irom[PC] = ('CMD', op_indx, OPCODES[op], op_addr)
                # print(f"_PC: {PC >> 1:0>4X}.{PC & 1} {op} {sym}{op_addr}+{op_offset}, M{op_indx}")
                PC += 1
            else:
                print(f"line: {line}: Unknown assembler command: {kwrd}")
                error_count += 1
                break
        else:
            print(f"near line {t.curr.line}: keyword or command required")
            error_count += 1
            break

    # check for errors
    if error_count > 0:
        print(f"Assembly errors count: {error_count}")
        sys.exit(1)

    # do fixups
    for i in range(131072):
        if irom[i][0] == 'FIX':
            if irom[i][3] in names:
                irom[i] = ('CMD', irom[i][1], irom[i][2], names[irom[i][3]][1] + irom[i][4])
            else:
                print(f"Undefined symbol: {irom[i][3]}")
                raise Exception("UndefinedSymbol")

    if args.listing:
        print(f"Listing of {input_file}")

    op_names = {v: k for v, k in enumerate(OPCODES)}
    with open(output_file, 'wt') as out:
        # do irom print out
        for pc in range(0, 131072, 2):
            if irom[pc][0] != 'NONE':
                opc = pc >> 1
                left_idx = irom[pc][1] << 24
                left_op = irom[pc][2] << 16
                left_op_name = op_names[irom[pc][2]]
                left_addr = irom[pc][3]
                left = left_idx | left_op | left_addr
                right_idx = irom[pc + 1][1] << 24
                right_op = irom[pc + 1][2] << 16
                right_op_name = op_names[irom[pc][2]]
                right_addr = irom[pc + 1][3]
                right = right_idx | right_op | right_addr
                out.write(f"i {opc:>04X} {left:>08X} {right:>08X}\n")
                if args.listing:
                    print(f"i {opc:>04X}: {left_op_name: <8} {left_addr:>04X},{irom[pc][1]}")
                    print(f"        {right_op_name: <8} {right_addr:>04X},{irom[pc + 1][1]}")

        if args.listing:
            print("Symbol table:")
            for i in names:
                print(f"Name: {names[i][0]: >8} address: {names[i][1]:>04X}")
        # do dram print out
        for dp in range(65536):
            if dram[dp] != 0:
                out.write(f"d {dp:>04X} 00 {dram[dp]:>08X}\n")
