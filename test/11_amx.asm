#
# Test for instruction AMX.
#
org     1
ptr     start
        vtm     stack,15
        ntr     3                       # без нормализации и округления
        vtm     64,14
        ita     14
        amx     f65                  # целое 65 без порядка
        uza     fail                    # |64| - |65| = -1
        aex     minus1                  # целое -1 без порядка
        uia     fail
#-------------------------
        xta     minus1
        amx     minus1
        uia     fail
#
        aox     0                       # |-1| - |-1| = 0
        uia     fail
#-------------------------
        xta     b2
        xts     b3
        amx     0,15                    # |3| - |2| = 1
        uia     fail
#
        aex     b1
        uia     fail
#-------------------------
        xta     b0067777777777777
        amx     b1
        aex     b0050000000000000
        uia     fail
#-------------------------
        xta     b4050000000000000        # =e'1' b4050000000000000
        xts     b6427777777777777        # =e'-549755813889' b6427777777777777
        amx     0,15
        aex     b6410000000000000        # =e'549755813888' b6410000000000000
        uia     fail
#-------------------------
        ntr     0                        # с нормализацией и округлением
        xta     b6410000000000002        # =e'549755813890' b6410000000000002
        xts     b6410000000000003        # =e'549755813891' 6410000000000003
        amx     0,15
        aex     b4050000000000000        # =e'1' b4050000000000000
        uia     fail
#
        xta     b4060000000000000    # -2
        amx     b4057777777777765    # 1.99999999998
        aex     b1653000000000000    # 2.0008883439004e-11
        uia     fail
#-------------------------
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
#-------------------------
dorg    0o2000            # данные с адреса 2000
arr     minus1  0o0037777777777777     # целое -1 без порядка
arr     b1      1
arr     b2      2
arr     b3      3
arr     b0067777777777777   0o0067777777777777
arr     b0050000000000000   0o0050000000000000
arr     b4050000000000000   0o4050000000000000
arr     b6427777777777777   0o6427777777777777
arr     b6410000000000000   0o6410000000000000
arr     b6410000000000002   0o6410000000000002
arr     b6410000000000003   0o6410000000000003
arr     b4060000000000000   0o4060000000000000
arr     b4057777777777765   0o4057777777777765
arr     b1653000000000000   0o1653000000000000
mem     stack   10                      # стек
arr     f65     65
        fin
