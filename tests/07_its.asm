#
# Test for instruction ITS.
#
org 1
        vtm     ws,15
        ita     15
        aex     ones
        ati     14
#
        vtm     0o11,1
        vtm     0o22,2
        vtm     0o33,3
        ita     1
        its     2
        its     3
        its     0
        jaddm   15,14
        utm     -2,15
#
        vim     fail,15
        xta     ws
        aex     b11
        uia     fail
#
        xta     ws+1
        aex     b22
        uia     fail
#
        xta     ws+2
        aex     b33
        uia     fail
#
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
#-------------------------
dorg 0o2000
arr     ones    0xFFFF
arr     b11     0o11
arr     b22     0o22
arr     b33     0o33
mem     ws      3
