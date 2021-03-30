#
# Test for instruction STI.
#
org 1
        vtm     ws+3,15
        ita     15
        aex     ones
        ati     14

        sti     0
        sti     3
        sti     2
        ati     1

        jaddm   15,14
        utm     4,15
        vim     fail,15

        utm     -0o33,3
        vim     fail,3
        utm     -0o22,2
        vim     fail,2
        utm     -0o11,1
        vim     fail,1
#
# STI (15) when M15=15: special case
#
        xta     cful
        atx     49000
        atx     49001
        xta     0
        vtm     49000,15
        xts     0,15
        aex     cful
        uia     fail

        xta     49000
        uia     fail
        vtm     15,15
        xta     b49001
        sti     0,15
        aex     cful
        uia     fail

lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2

dorg    0o2000
arr     ones    0xFFFF
arr     b49001  49001
arr     cful    0o7777777777777777
arr     ws      [0o11, 0o22, 0o33]

