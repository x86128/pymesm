#
# Test for instruction VLM.
#
org 1
        vtm     -9,2
        vtm     -10,3
lbl     a
        utm     1,3
        vlm     a,2
        vim     fail,2
        vim     fail,3
        vlm     fail,2         ; а что при "0"
        vim     fail,2
#
# слабое место: короткий цикл
#
        xta     cful
        vtm     -255,14
lbl     b
        atx     ws+255,14
        vlm     b,14
        xta     0
        vtm     -255,15
lbl     c
        arx     ws+255,15
        vlm     c,15
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
        vtm     -255,14
        vtm     -255,13
lbl     d
        arx     ws+255,14
        vlm     d,14
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
lbl     e
        arx     ws+255,13
        vlm     e,13
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
        vtm     -255,12
        vtm     -255,11
lbl     f
        arx     ws+255,12
        vlm     f,12
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
lbl     g
        arx     ws+255,11
        vlm     g,11
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
        vtm     -255,10
        vtm     -255,9
lbl     h
        arx     ws+255,10
        vlm     h,10
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
lbl     i
        arx     ws+255,9
        vlm     i,9
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
        vtm     -255,8
        vtm     -255,7
lbl     j
        arx     ws+255,8
        vlm     j,8
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
lbl     k
        arx     ws+255,7
        vlm     k,7
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
        vtm     -255,6
        vtm     -255,5
lbl     l
        arx     ws+255,6
        vlm     l,6
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
lbl     m
        arx     ws+255,5
        vlm     m,5
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
        vtm     -255,4
        vtm     -255,3
lbl     n
        arx     ws+255,4
        vlm     n,4
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
lbl     o
        arx     ws+255,3
        vlm     o,3
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
        vtm     -255,2
lbl     p
        arx     ws+255,2
        vlm     p,2
        aex     0
        uza     fail
        aex     cful
        uia     fail
#
        vtm     -255,1
lbl     q
        arx     ws+255,1
        vlm     q,1
        aex     0
        uza     fail
        aex     cful
        uia     fail
lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
#-------------------------
dorg    0o2000            # данные с адреса 2000
arr     cful    0o7777777777777777
mem     ws  1030
