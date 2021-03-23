from dataclasses import dataclass


@dataclass
class Token:
    typ: str
    val: str


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

    def peek(self, typ):
        return self._curr.typ == typ

    def get(self, typ):
        if self.peek(typ):
            t = self._curr
            self.advance()
            return t
        else:
            print(f"Expected {typ}, got: {self._curr.typ}.")
            raise Exception("ParseError")

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
                elif s.isdigit():
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
                elif s in '+-':
                    state = 'BINOP'
                    tok_txt += s
                    self._pos += 1
                    break
                elif s == ',':
                    state = 'COMMA'
                    tok_txt += s
                    self._pos += 1
                    break
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
                    tok_txt = tok_txt.encode().decode('unicode-escape')
                    break
                tok_txt += s
                self._pos += 1
            else:
                print(f"Unknown state at {self._pos} {self.source[tok_pos:self._pos + 5]}")
                raise Exception("ParseError")
        self._next = Token(state, tok_txt)
