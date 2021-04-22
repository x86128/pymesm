#
# Test for instructions Е+N, Е-N, Е+Х, Е-Х.
#
org     1
lbl     start
        vtm     -0o176,12
        xta     cfe8u
        atx     ws
lbl     loop1
        xta     ws
        eaddn   63  # 64-1
        atx     ws
        asn     105 # 64+41
        ati     14
        jaddm   14,12
        vim     fail,14
        vlm     loop1,12
        xta     ws
        esubn   65     # 64+1
        uza     fail
        vtm     -0o176,12
        xta     c008u
        atx     ws
        vtm     -1,11
lbl     loop2
        xta     ws
        esubx   c7e8u
        atx     ws
        asn     105   # 64+41
        ati     14
        jaddm   14,11
        vim     fail,14
        utm     -1,11
        vlm     loop2,12
        xta     ws
        eaddx   c008u
        aex     c7e8u
        uia     fail

        xta     b7030000000000000    #=b'7030000000000000'
        eaddx   b4010000000000000
        aex     b6760000000000000    #=b'6760000000000000'
        uia     fail

lbl     pass
        stop    0o12345,6
lbl     fail
        stop    0o76543,2
#-------------------------
dorg    0o2000
arr     cfe8u   0o7750000000000000
arr     c008u   0o0010000000000000
arr     c7e8u   0o3750000000000000
arr     b7030000000000000   0o7030000000000000
arr     b4010000000000000   0o4010000000000000
arr     b6760000000000000   0o6760000000000000
mem     ws      1
