from flowscript.lexer import Lexer
from flowscript.parser import Parser

with open("examples/hello.flow", "r") as f:
    source = f.read()

tokens = Lexer(source).tokenize()

parser = Parser(tokens)
program = parser.parse()

print(program)