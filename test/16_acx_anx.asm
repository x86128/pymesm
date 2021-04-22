#
# Test for instructions ACX, ANX.
#
org     1
lbl     start
        ita     0
        acx     0
        uia     fail
        xta     cful
        acx     0
        aex     i48
        uia     fail
        xta     chess+1
        acx     im24
        aex     i1
        uia     fail

        vtm     -48,12
        vtm     48,11
        vtm     ws+1,15
        xta     i1
lbl     loop
        vim     nz,11
        xta     0
lbl     nz
        atx     ws
        anx     0
        its     11
        aex     0,15
        uia     fail
        xta     ws
        asn     63    # 64-1
        its     11
        aax     i7
        aox     0,15
        utm     -1,11
        vlm     loop,12

        xta     0
        anx     cful
        aex     cful
        uia     fail
        vtm     0o1001,14
        ita     14              # проверка
        anx     cful            # засылки
        yta     0
        aex     c008u           # остатка
        uia     fail            # в РМР
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
#-------------------------
dorg    0o2000            # данные с адреса 2000
arr     cful    0o7777777777777777
arr     i1          1
arr     i7          7
arr     i48         0o60
arr     im24        0o7777777777777750
arr     c008u       0o0010000000000000
arr     chess       [0o5252525252525252,
                     0o2525252525252525]
mem     ws      2
