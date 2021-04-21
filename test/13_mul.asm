#
# Test for instructions А*Х, А/Х.
#
org     1
lbl     start
        vtm     stack,15
        ntr     3
        xta     cdu5l
        mul     c5udl           # 13/2**64
        atx     0,15
        yta     64
        stx     ws
        aex     cau
        uia     fail

        xta     ws
        aex     cau41l          # 65/2**24
        uia     fail

        xta     c5u5l           # 5/2**64
        mul     cim13           # = -65
        atx     0,15
        yta     64
        stx     ws
        aex     ca1ufs
        uia     fail

        xta     ws
        eaddn     88           # 64+24
        aex     cd0fbf          # -65!-
        uia     fail

        ntr     2
        xta     c848u           # 2.
        mul     c84cu           # 3.
        atx     ws
        aex     c84cu           # 3.
        aex     c02u
        uia     fail            # !=6

lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2

dorg    0o2000            # данные с адреса 2000
arr     cdu5l   0o6400000000000005
arr     c5udl   0o2400000000000015
arr     cau     0o5000000000000000
arr     cau41l  0o5000000000000101
arr     c5u5l   0o2400000000000005
arr     cim13   0o6437777777777763
arr     ca1ufs  0o5037777777777777
arr     cd0fbf  0o6417777777777677
arr     c848u   0o4110000000000000
arr     c84cu   0o4114000000000000     # 3.
arr     c02u    0o0040000000000000
mem     ws      1
mem     stack   10                      # стек
