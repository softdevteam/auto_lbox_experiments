#! /usr/bin/env python2.7

import sys
import re, os, json
from time import time
from grammars.grammars import EcoFile
from grammar_parser.gparser import Terminal
from treelexer.lexer import Lexer
from incparser.syntaxtable import FinishSymbol, Reduce, Accept, Shift

class Parser(object):

    def __init__(self, stable):
        self.stable = stable
        self.state = 0
        self.stack = [("$", 0)]
        self.log = []

    def parse(self, tokens):
        self.log = []
        tokens = iter(tokens)
        token = tokens.next()
        la = Terminal(token[1])
        while True:
            self.log.append(token)
            elem = self.stable.lookup(self.state, la)
            if type(elem) is Shift:
                self.state = elem.action
                self.stack.append((la, self.state))
                try:
                    token = tokens.next()
                    la = Terminal(token[1])
                except StopIteration:
                    la = FinishSymbol()
            elif type(elem) is Reduce:
                for i in range(elem.amount()):
                    self.stack.pop()
                self.state = self.stack[-1][1]
                goto = self.stable.lookup(self.state, elem.action.left)
                assert goto != None
                self.state = goto.action
                self.stack.append((elem.action.left, self.state))
            elif type(elem) is Accept:
                return True
            else:
                return False

if __name__ == "__main__":
    jsonfile = sys.argv[1]
    with open(jsonfile) as f:
        s = json.load(f)
    
    sqlitecmd = EcoFile("Sqlitecmd", "grammars/sqlite.eco", "")
    sqlitecmd.change_start("cmdx")
    incparser, inclexer = sqlitecmd.load()
    lexer = inclexer.lexer
    stable = incparser.syntaxtable

    working = []
    failed = []

    for stmt in s:
        stmt2 = stmt.replace("\n", "\r") # Eco grammar compatiblity fix
        # append semicolon to tests where it's missing
        for stmt3 in stmt2.split(";"):
            stmt3 = stmt3.strip()
            if stmt3 == "":
                continue
            if stmt3.startswith("--") or stmt3 == "" or stmt3.startswith("/*"):
                continue
            tokens = lexer.lex(stmt3)
            parser = Parser(stable)
            success = False
            e = None
            try:
                success = parser.parse(tokens)
            except TypeError, e:
                pass
            if not success:
                failed.append(stmt3)
                sys.stdout.write("x")
                sys.stdout.flush()
            else:
                working.append(stmt3)
                sys.stdout.write(".")
                sys.stdout.flush()

    with open("../../../sqlstmts.json", "w") as f:
        json.dump(working, f, indent=0)

    with open("../../../sqlstmts_fail.json", "w") as f:
        json.dump(failed, f, indent=0)
