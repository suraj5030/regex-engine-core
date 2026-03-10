import sys


class InputBuffer:
    def __init__(self, data=None):
        if data is None:
            data = sys.stdin.read()
        self._source = data
        self._pos = 0
        self._input_buffer = []

    def GetChar(self):
        if self._input_buffer:
            return self._input_buffer.pop()
        if self._pos >= len(self._source):
            return ""
        ch = self._source[self._pos]
        self._pos += 1
        return ch

    def UngetChar(self, c):
        if c:
            self._input_buffer.append(c)
        return c

    def UngetString(self, s):
        for c in reversed(s):
            self._input_buffer.append(c)
        return s

    def EndOfInput(self):
        if self._input_buffer:
            return False
        return self._pos >= len(self._source)
