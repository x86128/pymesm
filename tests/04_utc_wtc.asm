#
# Test for instructions UTC, WTC.
#
org 1
        utc     -1
        vtm     0,3
        vzm     fail,3
        utm     1,3
        vim     fail,3
lbl     a
        utc     -1
lbl     b
        vtm     0,3
        vzm     fail,3
        utm     1,3
        vim     fail,3
lbl     c
        wtc     mmask
        vtm     0,3
        vzm     fail,3
        utm     1,3
lbl     d
        vim     fail,3
        wtc     mmask
lbl     e
        vtm     0,3
        vzm     fail,3
        utm     1,3
        vim     fail,3
        utc     -7
        utc     8
        vtm     -2,3
        vzm     fail,3
        utm     1,3
        vim     fail,3
        wtc     mmask
        utc     8
        vtm     -6,3
        utm     -1,3
        vim     fail,3
        vtm     -1,3
#
        wtc     chess+1,3
        vtm     0,4
        mtj     5,4
        utm     -0o125252,5
        vim     fail,5
        utm     1,3
#
        wtc     chess+1,3
        vtm     0,4
        mtj     5,4
        utm     -0o52525,5
        vim     fail,5
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
# *-------------------------
dorg 0o2000            # данные с адреса 2000
arr mmask   0xFFFF
arr chess   [0o5252525252525252, 0o2525252525252525]
