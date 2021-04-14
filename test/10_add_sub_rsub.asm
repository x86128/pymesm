#
# Test for instructions А+Х, А-Х, Х-А.
#
org 1
lbl start
        vtm     stack,15
        ntr     3
        vtm     64,14
        ita     14
        sub     f65                  # целое 65 без порядка
        uza     fail

        add     b1
        uia     fail

        aox     0
        uia     fail

        xta     b2
        rsub     b1
        sub     b0037777777777777
        uia     fail

        aox     0
        uia     fail

        xta     b2
        xts     b1
        xts     b2
        xts     b3
        sub     0,15                    # 3-2=1
        uia     fail

        add     0,15                    # 1+1 = 2
        rsub     0,15                    # 2-2 = 0
        uia     fail

        aox     0
        uia     fail

        xta     b6400000000000100    # целое 64
        sub     b6400000000000102    # целое 66
        uza     fail

        add     e20
        uia     fail

        aox     0
        uza     fail

        aex     b6400000000000000    # целое 0
        uia     fail

        ntr     2
        xta     e20                 # 2.0
        xts     e30                 # 3.0
        xts     e20                 # 2.0
        xts     e30                 # 3.0
        add     0,15                    # 3+2
        sub     0,15                    # 5-3
        rsub     0,15                    # 2-2
        uia     fail

        ntr     2
        xta     e10                 # 1.0
        sub     em20               # -2.0
        uia     fail
        aex     e30
        uia     fail

        ntr     0o77                    # нормализация отключена
        xta     b0010000000000000    # минимальное положительное
        add     b0010000000000000
        ntr     0
        aex     b0050000000000000    # проверка нормализации вправо
        uia     fail

        ntr     0
        xta     b7700000000001000
        add     b4000000000000001
        aex     b6010000000000001    # проверка залипающего бита
        uia     fail                    # минимальное положительное

        xta     b0010000000000000
        rsub    b4010000000000000
        yta     64
        aex     b3757777777600000
        uia     fail

lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2

dorg    0o2000            # данные с адреса 2000
arr     f65     65
arr     b1      1
arr     b2      2
arr     b3      3
arr     b0037777777777777    0o0037777777777777
arr     b6400000000000100    0o6400000000000100
arr     b6400000000000102    0o6400000000000102
arr     b6400000000000000    0o6400000000000000
arr     e10                 0o4050000000000000
arr     e20                 0o4110000000000000
arr     e30                 0o4114000000000000
arr     em20                0o4060000000000000
arr     b0010000000000000   0o0010000000000000
arr     b0050000000000000   0o0050000000000000
arr     b7700000000001000   0o7700000000001000
arr     b4000000000000001   0o4000000000000001
arr     b6010000000000001   0o6010000000000001
arr     b4010000000000000   0o4010000000000000
arr     b3757777777600000   0o3757777777600000
mem     stack   10                      # стек
