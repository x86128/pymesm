#
# Test for ARX instruction.
#
org     1
lbl     start
        xta     i11
        arx     i1
        aex     i12
        uia     fail
        xta     cful
        arx     i1
        aex     i1
        uia     fail
        xta     cful
        arx     cful
        aex     cful
        uia     fail
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
#-------------------------
dorg    0o2000            # данные с адреса 2000
arr     cful    0o7777777777777777
arr     i1      0o1
arr     i11     0o11
arr     i12     0o12
