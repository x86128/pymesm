def load_oct(filename, ibus, dbus):
    with open(filename) as f:
        for line in f:
            s = line.split()
            address = int(s[1], 8)
            word = (int(s[2], 8) << 24) | int(s[3], 8)
            if s[0] == "i":
                # instruction
                ibus.write(address, word)
            else:
                # data
                dbus.write(address, word)
