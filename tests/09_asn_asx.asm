#
# Test for instructions ASN, ASX.
#
org     1
        vtm     -32,12
        vtm     32,11
lbl     a
        xta     bit32
        asn     63,11         # влево на 1 разряд
        aex     masks,11
        uia     fail
        utm     -1,11
        vlm     a,12
#
        vtm     -32,12
        vtm     32,11
lbl     b
        xta     i1
        asn     32,11     # влево на 15
        aex     masks,11
        uia     fail
        utm     -1,11
        vlm     b,12
#
        xta     cful
        asx     cful
        uia     fail
#
        xta     chess
        asx     right1
        aex     chess+1
        uia     fail
#
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
#-------------------------
dorg    0o2000                          # данные с адреса 2000
arr     cful    0xFFFFFFFF
arr     chess   [0xAAAAAAAA, 0x55555555]
arr     bit32   0x80000000
arr     masks   [0,
                0x80000000,
                0x40000000,
                0x20000000,
                0x10000000,
                0x08000000,
                0x04000000,
                0x02000000,
                0x01000000,
                0x00800000,
                0x00400000,
                0x00200000,
                0x00100000,
                0x00080000,
                0x00040000,
                0x00020000,
                0x00010000,
                0x00008000,
                0x00004000,
                0x00002000,
                0x00001000,
                0x00000800,
                0x00000400,
                0x00000200,
                0x00000100,
                0x00000080,
                0x00000040,
                0x00000020,
                0x00000010,
                0x00000008,
                0x00000004,
                0x00000002]
arr     i1      1
arr     right1  0x41
