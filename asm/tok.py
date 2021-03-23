class Tokenizer:

    def __init__(self, input):
        self.source = input
        self._curr = None
        self._next = None
        self._pos = 0
        self._len = len(self.source)
        self._line = 0
        self._lpos = 0
        self.advance()
        self.advance()

    @property
    def curr(self):
        return self._curr

    @property
    def next(self):
        return self._next

    def advance(self):
        self._curr = self._next
        tok_txt = ""
        tok_pos = self._pos
        state = 'NONE'
        while self._pos < self._len:
            s = self.source[self._pos]
            if state == 'NONE':
                if s.isspace():
                    if s == "\n":
                        self._line += 1
                    self._pos += 1
                    continue
                elif s.isalpha():
                    state = 'IDENT'
                elif s.isdigit() or s == '-':
                    state = 'NUMBER'
                elif s in "#;":
                    state = 'COMMENT'
                elif s in '[]':
                    tok_txt = s
                    state = 'BRACE'
                    self._pos += 1
                    break
                elif s == '"':
                    state = 'STRING'
                    self._pos += 1
                    continue
                else:
                    print(f"Unknown token at {self._pos}: {s}")
                    raise Exception("ParseError")
                tok_txt += s
                self._pos += 1
            elif state == 'IDENT':
                if s.isalpha() or s.isdigit():
                    tok_txt += s
                    self._pos += 1
                else:
                    break
            elif state == 'NUMBER':
                if s.isdigit() or s in 'obxOBX':
                    tok_txt += s
                    self._pos += 1
                elif s.isalpha():
                    print(f"Number format err at {self._pos} {self.source[tok_pos:self._pos + 5]}")
                    raise Exception("ParseError")
                else:
                    break
            elif state == 'COMMENT':
                if s == '\n':
                    tok_txt = ""
                    state = 'NONE'
                self._pos += 1
            elif state == 'STRING':
                if s == '"':
                    self._pos += 1
                    break
                tok_txt += s
                self._pos += 1
            else:
                print(f"Unknown state at {self._pos} {self.source[tok_pos:self._pos + 5]}")
                raise Exception("ParseError")
        self._next = (state, self._line, tok_pos, tok_txt)
