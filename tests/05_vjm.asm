#
# Test for instruction VJM.
#
org 1
        utc     0
        vjm     a,2            # справа
lbl     a
        utm     -2,2           #  a = 2
        vim     fail,2
lbl     c
        vjm     b,2       #  слева
lbl     b
        utm     -4,2           # b = 4
        vim     fail,2
lbl     d
        vjm     f,2       # слева
lbl     e
        utc     -1
lbl     f
        vtm     1,3
        vzm     fail,3
lbl     g
        vtm     -1,3
        vjm     i,2
lbl     h
        vtm     -2,3
lbl     i
        utm     1,3
        vim     fail,3
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
