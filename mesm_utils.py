def load_oct(filename, ibus, dbus):
    with open(filename) as f:
        for line in f:
            s = line.split()
            address = int(s[1], 16)
            word = (int(s[2], 16) << 32) | int(s[3], 16)
            if s[0] == "i":
                # instruction
                ibus.write(address, word)
            else:
                # data
                dbus.write(address, word)
