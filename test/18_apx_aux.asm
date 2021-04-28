#
# Test for instructions APX, AUX.
#
org     1
lbl     start
        xta     chess
        apx     cful
        aux     c0ful
        aex     chess+1
        uia     fail
        xta     chess
        apx     chess+1
        uia     fail
        xta     chess
        apx     chess
        aux     chess+1
        aex     chess+1
        uia     fail
        xta     cful
        aux     chess+1
        aex     chess+1
        uia     fail
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
#
dorg    0o2000
arr     cful    0o7777777777777777
arr     c0ful   0o3777777777777777
arr     chess   [0o5252525252525252, 0o2525252525252525]
