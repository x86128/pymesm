#
# Test for instructions XTR, NTR, RТЕ, UZA, U1A, УТА.
#
org     1
lbl     start
        vtm     ws+1,15
        ita     0
        vtm     0o77,2
        vtm     -63,3      # 1-64
lbl     loop
        ntr     0,2
        rte     0o77
        atx     ws
        its     2
        asn     23       # 64-41
        aex     0,15
        uia     fail
        uia     fail
        xtr     0
        rte     0o77
# С некоторых пор команда RTE уставливает логическую группу.
#       uza     fail
#       aox
        uia     fail
        xtr     ws
        rte     0o77
        its     2
        asn     23       # 64-41
        aex     0,15
        uia     fail
        uia     fail
#
        vtm     ws+1,15
        xtr     0,15
        vtm     mst,15
        rte     0o77
        its     2
        asn     23          # 64-41
        aex     0,15
        uia     fail
        utm     -1,2
        vlm     loop,3
#
        ntr     0o77
        rte     0o41
        aex     b2040000000000000
        uia     fail
        ntr     0
        uza     fail
lbl     a
        uia     ok
        uj      fail
lbl     ok
        ntr     7               # логическая группа
        uia     fail
        ntr     11              # группа умножения
        uza     fail
        aox     0
        uia     fail
        ntr     19              # группа сложения
        uia     fail
        xta     cful
        uza     fail
        ntr     11
        uia     fail
        ntr     19
        uza     fail
#
        ntr     24              # гс+гу = гс
        uza     fail
        ntr     12              # гу+гл = гу
        uia     fail
        xta     b1              # =b'1'
        ntr     20              # гс+гл = гс
        uia     fail
        xta     cful
        aex     0
        xta     0
        yta     0
        aex     cful
        uia     fail
        arx     0               # должна
        uza     fail            # получиться
        arx     cful            # группа умножения
        uia     fail
        aax     cful            # логическая группа
        uza     fail
#
lbl     align
        xta     0
        ntr     0o77               # ставим R = 077
        atx     ws                 # не меняет R
        rte     0o77               # читаем R
        aex     b3740000000000000  # =b'3740000000000000'
        uia     fail               # ждём единицы в порядке
#
lbl     align2
        xta     cful
        ntr     0               # нет группы
        xta     0               # левая команда
        uza     align3          # проверяем логическую группу
        uj      fail
#
lbl     align3
        ntr     0               # нет группы
        xta     0               # правая команда
        uza     pass            # проверяем логическую группу
#
lbl     fail
        stop    0o76543,2
lbl     pass
        stop    0o12345,6
#-------------------------
dorg    0o2000              # данные с адреса 2000
arr     b3740000000000000   0o3740000000000000
arr     b1                  0o1
arr     b2040000000000000   0o2040000000000000
arr     cful                0o7777777777777777
mem     mst     40
mem     ws      1030
