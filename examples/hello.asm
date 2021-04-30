# hello world using loop
org     1
ptr     prn0    32767

# loop setup
        vtm     -15,2
lbl     loop
        xta     hello+15,2
        atx     prn0
        vlm     loop,2
        stop    0o12345,6
dorg    0o2000
arr     hello "Hello, world!!!\n"
