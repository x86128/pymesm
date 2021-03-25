#
# Test for instructions AAX, AOX, AEX.
#
        org     1
        xta     cful
        aax     0
        uia     fail
        xta     cful
        aax     cful
        aex     cful
        uia     fail
        xta     chess
        aax     chess
        aex     chess
        uia     fail
        xta     chess
        aax     chess+1
        uia     fail
        xta     chess
        aox     chess+1
        aex     cful
        uia     fail
lbl pass
        stop    0o12345,6
lbl fail
        stop    0o76543,2
#-------------------------
        dorg    0o2000
arr     cful    0o7777777777777777
arr     chess   [0o5252525252525252, 0o2525252525252525]
