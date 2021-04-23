#
# Test for instructions ASN, ASX.
#
org     1
        vtm     -48,12
        vtm     48,11
lbl     a
        xta     bit48
        asn     63,11         # влево на 1 разряд
        aex     masks,11
        uia     fail
        utm     -1,11
        vlm     a,12
#
        vtm     -48,12
        vtm     48,11
lbl     b
        xta     i1
        asn     16,11     # влево на 48
        aex     masks,11
        uia     fail
        utm     -1,11
        vlm     b,12
#
        xta     cful
        asx     cful
        uia     fail
#
        xta     chess+1
        asx     c0ful
        aex     chess
        uia     fail

        xta     cful            # а что
        asn     52              # попадет (64-12)
        yta     0               # в рмр
        aex     cfff            # при
        uia     fail            # сдвигах ?

        xta     cful
        asn     68              # 64+4
        yta     0
        aex     cfu
        uia     fail

        xta     cful
        asx     b0020000000000000    # сдвиг на -64
        uia     fail

lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
#-------------------------
dorg    0o2000                          # данные с адреса 2000
arr     b0020000000000000   0o0020000000000000
arr     cful     0xFFFFFFFFFFFF
arr     chess   [0xAAAAAAAAAAAA,
                 0x555555555555]
arr     bit48   0o4000000000000000
arr     masks   [0,
                0x800000000000,
                0x400000000000,
                0x200000000000,
                0x100000000000,
                0x80000000000,
                0x40000000000,
                0x20000000000,
                0x10000000000,
                0x8000000000,
                0x4000000000,
                0x2000000000,
                0x1000000000,
                0x800000000,
                0x400000000,
                0x200000000,
                0x100000000,
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
arr     c0ful   0o3777777777777777
arr     cfu     0o7400000000000000
arr     cfff    0o7777
arr     right1  0x41
