#
# Test for instructions ATI, ITA.
#
org     1
        xta     0
        vtm     -1,2
        ati     2
        vim     fail,2
        xta     data
        ati     2
        vzm     fail,2
        xta     0
        ita     2
        ati     3
        vzm     fail,3
        utm     1,3
        vim     fail,3
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
#-------------------------
dorg    0o2000            # данные с адреса 2000
arr     data    0o7777777777777777