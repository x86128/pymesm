# Integer-only MESM6-like machine

Split data and program memory, each consist of 65536 words.

32 bit instruction words packed as pairs to 64bit words. So, maximum program size is 131072 instructions. 

Data memory is 65536 64-bit words, but ACC is 32-bit only.

16 bit program counter and index registers (address modifiers).

Same instruction op_codes numbers as MESM6 (total of 64+16).

For simplicity, CPU instruction encoded as:

| 8 bit | 8 bit | 16 bit |
|---|---|---|
| index | op_code | address |

Instructions implemented by translating original MESM6 microcode.

Most of the tests adopted from original MESM6 https://github.com/besm6/mesm6

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
