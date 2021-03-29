import sys
from dataclasses import dataclass


@dataclass
class Token:
    typ: str
    val: str
    line: int


class Tokenizer:

    def __init__(self, input):
        self.source = input
        self._curr = None
        self._next = None
        self._pos = 0
        self._len = len(self.source)
        self._line = 1
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
            print(f"line {self._curr.line}: expected {typ}, got: {self._curr.typ}.")
            sys.exit(1)

    def advance(self):
        self._curr = self._next
        tok_txt = ""
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
                    print(f"line: {self._line}: Unknown token: {s}")
                    sys.exit(1)
                tok_txt += s
                self._pos += 1
            elif state == 'IDENT':
                if s.isalpha() or s.isdigit():
                    tok_txt += s
                    self._pos += 1
                else:
                    break
            elif state == 'NUMBER':
                if s.isdigit() or s in 'obxOBXABCDEFabcdef':
                    tok_txt += s
                    self._pos += 1
                elif s.isalpha():
                    print(f"line: {self._line}: Number format error")
                    sys.exit(1)
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
                print(f"line: {self._line}: Unknown state at {state}")
                sys.exit(1)
        self._next = Token(state, tok_txt, self._line)
