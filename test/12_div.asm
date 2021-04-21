#
# Test for instruction А/Х.
#
org     1
ptr     start
        vtm     stack,15
        ntr     3
        xta     e60     # 6.0
        div     e30     # 3.0
        aex     e20     # 2.0
        uia     fail
#
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2

#-------------------------
dorg    0o2000
arr     e60     0o4154000000000000 # 6.0
arr     e30     0o4114000000000000 # 3.0
arr     e20     0o4110000000000000 # 2.0
mem     stack   10                      # стек
