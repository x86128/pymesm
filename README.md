# Python implementation of MESM6

Split data and program memory, each consist of 32768 48-bit wide words.

15 bit program counter and index registers (address modifiers).

Total of 64+16 instructions with MESM6 encoding.

Short address instruction format:

| 4 bit | 1 bit | 1 bit | 6 bit | 12 bit |
|---|---|---|---|---|
| index | 0 | ext | op_code | address |

Long address format:

| 4 bit | 1 bit | 4 bit | 15 bit |
|---|---|---|---|
| index | 1 | op_code | address |

Instructions implemented by translating original MESM6 microcode.

Most of the tests adopted from original MESM6 https://github.com/besm6/mesm6

## Implemented CPU instructions

* Load/store, register/register
  * ATX, XTA, ATI, ITA, XTS, STX, STI, ITS
* Arithmetic operations
  * A+X, A-X, X-A, AVX, A/X, A*X, ARX, AMX
  * E+N, E-N, E+X, E-X
* Shift
  * ASX, ASN
* Logic
  * AAX, AOX, AEX
* Address modifiers
  * UTC, WTC
* Set address modifier register
  * UTM, VTM, MTJ, J+M
* Branch
  * VZM, V1M, VLM, VJM, UJ, U1A, UZA
* Stop
  * STOP
    
Unimplemented instructions:
* MOD, APX, AUX, ACX, ANX, XTR, RTE, EXT
* extracodes

## Running

Let's build simple program: `exmaples/hello.asm`

```
# hello world using loop
org     1
ptr     prn0    65535

# loop setup
        vtm     -15,2
lbl     loop
        xta     hello+15,2
        atx     prn0
        vlm     loop,2
        stop    0o12345,6
dorg    1
arr     hello "Hello, world!!!\n"

```

Compile with listing print out

`python3 asm/asm.py -i examples/hello.asm -l`

```
Listing of examples/hello.asm
i 0001: vtm      FFF1,2
        utc      0000,0
i 0002: xta      0010,2
        atx      FFFF,0
i 0003: vlm      0002,2
        stop     14E5,6
Symbol table:
Name:     prn0 address: FFFF
Name:     loop address: 0002
Name:    hello address: 0001
```

Run with `./pymesm -i examples/hello.oct`

```
Hello, world!!!
CPU halted at 0003 with 14E5
Success
Simulation finished.
```

To run program with trace enabled add `-t` option:

`./pymesm -i examples/hello.oct -t`

```
...skipped...

0003: VLM 0002,M2
  M[2] = 0000
IBUS: RD from 0002 val: 020800100000FFFF
0002: XTA 0010,M2
DBUS: RD from 0010 val: 000000000000000A
  ACC = 0000000A
0002: ATX FFFF

DBUS: WR to FFFF val: 000000000000000A
IBUS: RD from 0003 val: 024F0002064B14E5
0003: VLM 0002,M2
0003: STOP 14E5,M6
CPU halted at 0003 with 14E5
Success
Simulation finished.
```
