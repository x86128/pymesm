#!/usr/bin/env python3

import sys
import os.path
import argparse
import array
from dataclasses import dataclass
from tok import Tokenizer


@dataclass
class Fix:
    pc: int
    sym: str
    offset: int


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

MASK15 = 0o77777
MASK48 = 0o7777777777777777


def pack_insn(indx, op, addr):
    halfword = indx << 20
    if op > 0o77:  # long instruction
        op -= 48
        halfword |= op << 15
        halfword |= addr
    else:  # short instruction
        halfword |= op << 12
        if addr <= 0o07777:  # low address
            halfword |= addr
        elif addr >= 0o70000:  # extended hi address
            halfword |= 1 << 18
            halfword |= addr & 0o07777
        else:  # unrepresentable address
            print(f"WARN: unrepresentable address {addr:>05o}")
            return -1
    return halfword


if __name__ == '__main__':
    source = open(input_file).read()
    t = Tokenizer(source)

    PC = 0
    DP = 0
    irom = array.array('Q', [0xFFFFFFFFFFFFFFFF] * 65536)
    dram = array.array('Q', [0xFFFFFFFFFFFFFFFF] * 32768)

    fix_list = []  # tuples(pc, 'name', offset)
    names = {}
    bss_size = 0

    error_count = 0
    while not t.eof:
        if keyword := t.get('IDENT'):
            kwrd = keyword.val.lower()
            line = keyword.line
            if kwrd in keywords:
                if kwrd == 'org':
                    if op_addr := t.get_number():
                        PC = 2 * (op_addr.as_num & MASK15)
                    else:
                        print(f"at line {line}: ORG: correct address required")
                        error_count += 1
                        break
                elif kwrd == 'dorg':
                    if op_addr := t.get_number():
                        DP = op_addr.as_num & MASK15
                    else:
                        print(f"at line {line}: DataORG: correct address required")
                        error_count += 1
                        break
                elif kwrd == 'ptr':
                    if name := t.get('IDENT'):
                        if op_addr := t.get_number():
                            names[name.val] = op_addr.as_num & MASK15
                    else:
                        print(f"at line {line}: PTR: identifier required")
                        error_count += 1
                        break
                elif kwrd == 'lbl':
                    if name := t.get('IDENT'):
                        if PC & 1 == 1:
                            irom[PC] = pack_insn(0, op_codes['utc'], 0)  # UTC 0
                            PC += 1
                        names[name.val] = PC >> 1
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
                        names[name.val] = DP
                        # array of chars in "STRING"
                        if chars := t.get('STRING'):
                            for c in chars.val:
                                dram[DP] = ord(c)
                                DP += 1
                        # array of "NUMBER"
                        elif array := t.get_number_array():
                            for val in array:
                                dram[DP] = val & MASK48
                                DP += 1
                        # single constant
                        elif val := t.get_number():
                            dram[DP] = val.as_num & MASK48
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
                        names[name.val] = DP
                        if size := t.get_number():
                            DP += size.as_num
                            bss_size += size.as_num
                        else:
                            print(f"at line {line}: {name.val} number required")
                            error_count += 1
                            break
                else:
                    print(f"Unimplemented keyword: {kwrd}")
                    error_count += 1
                    break
            elif kwrd in op_names:
                # parse opcode
                # opName [number | ident][{+|-}number|ident][(number)]
                op = kwrd
                op_offset = 0
                op_addr = 0
                op_indx = 0
                sym = ""
                # try "OP NUMBER"
                if addr := t.get_number():
                    op_addr = addr.as_num & MASK15
                # then "OP NAME[+-NUMBER]"
                elif name := t.get('IDENT'):
                    sym = name.val
                    if t.get('BRACE'):
                        if addr := t.get_number():
                            op_offset = addr.as_num & MASK15
                            if not t.get('BRACE'):
                                print(f"at line {line}: ] brace required")
                                error_count += 1
                                break
                        else:
                            print(f"at line {line}: number required")
                            error_count += 1
                            break
                    # then "OP NAME+-OFFSET"
                    elif offset := t.get_number():
                        op_offset = offset.as_num & MASK15
                    # then just "OP NAME"
                    else:
                        op_offset = 0
                    if name.val in names:
                        op_addr = (names[name.val] + op_offset) & MASK15
                    else:
                        op_addr = (name.val, op_offset)
                # index register suffix "xta 123,15"
                if t.get('COMMA'):
                    if indx := t.get_number():
                        op_indx = indx.as_num & 0xF
                    else:
                        print(f"at line {line}: index register number required")
                        error_count += 1
                        break
                # check if we need add symbol to fixup table
                if isinstance(op_addr, tuple):
                    irom[PC] = pack_insn(op_indx, op_codes[op], 0)
                    fix_list.append(Fix(PC, op_addr[0], op_addr[1]))
                else:
                    irom[PC] = pack_insn(op_indx, op_codes[op], op_addr & MASK15)
                PC += 1
            else:
                print(f"line: {line}: Unknown assembler command: {kwrd}")
                error_count += 1
                break
        else:
            print(f"near line {t.curr.line}: keyword or command required")
            error_count += 1
            break
    # if after assembly PC points to right instruction, set it to UTC 0 to fill word
    if PC & 1 == 1:
        irom[PC] = pack_insn(0, op_codes['utc'], 0)  # UTC 0
        PC += 1
    # check for errors
    if error_count > 0:
        print(f"Assembly errors count: {error_count}")
        sys.exit(1)

    # do fixups: fix = tuple(pc, sym_name, offset)
    for fix in fix_list:
        if fix.sym in names:
            addr = (names[fix.sym] + fix.offset) & MASK15
            # short address instructions require address range check
            if irom[fix.pc] & (1 << 19) == 0:
                if addr >= 0o70000:
                    irom[fix.pc] |= 1 << 18
                    irom[fix.pc] |= addr & 0o7777
                elif addr <= 0o7777:
                    irom[fix.pc] |= addr & 0o7777
                else:
                    print(f"Execution address {addr:>0o5} out of range at {fix.pc:>05o} for symbol {fix.sym}")
                    raise IndexError
            else:
                irom[fix.pc] |= addr
        else:
            print(f"Undefined symbol: {fix.sym}")
            raise ValueError

    if args.listing:
        print(f"Listing of {input_file}")

    with open(output_file, 'wt') as out:
        # do irom print out
        for pc in range(0, 65536, 2):
            if irom[pc] != 0xFFFFFFFFFFFFFFFF:
                opc = pc >> 1
                out.write(f"i {opc:>05o} {irom[pc]:>08o} {irom[pc + 1]:>08o}\n")
                if args.listing:
                    print(f"i {opc:>05o} {irom[pc]:>08o} {irom[pc + 1]:>08o}")
        # do dram print out
        for dp in range(32768):
            if dram[dp] != 0xFFFFFFFFFFFFFFFF:
                out.write(f"d {dp:>05o} {dram[dp] >> 24:>08o} {dram[dp] & 0xFFFFFF:>08o}\n")

        if args.listing:
            print("\nSymbol table:")
            for i in names:
                print(f"Name: {i: >8} address: {names[i]:>05o}")
            if bss_size != 0:
                print(f"\nBSS size: {bss_size}")
