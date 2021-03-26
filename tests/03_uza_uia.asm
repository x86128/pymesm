# 
#  Test for instructions XTA, UZA, UIA.
# 
org     1
        xta     zero
        uza     ok
        uj      fail
# 
lbl     ok
        uia     fail
        uia     fail
# 
        xta     one
        uza     fail
        uza     fail
        uia     pass
# 
lbl     fail
        stop    0o76543,2
lbl     pass
        stop    0o12345,6
# -------------------------
dorg    0o2000
arr     zero    0
arr     one     1
