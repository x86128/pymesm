#
# Test for instructions ATX 0(0), XTA 0(0), ATI 0(0), ITA 0(0).
# Address 0 and register m0 should always return 0.
#
ptr     start   1
        vtm     -1,2
        ita     2
        atx     0
lbl     a0left
        xta     0               # слева
        ati     2
        vim     fail,2
        vtm     -1,2
        ita     2
lbl     a0rght
        atx     0
        xta     0               # справа
        ati     2
        vim     fail,2
#
        vtm     -1,2
        ita     2
        ati     0
lbl     m0left
        ita     0               # слева
        ati     2
        vim     fail,2
        vtm     -1,2
        ita     2
lbl     m0rght
        ati     0
        ita     0               # справа
        ati     2
        vim     fail,2
#
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
