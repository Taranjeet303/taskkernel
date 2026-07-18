from flowscript.lexer import Lexer

with open("examples/hello.flow", "r", encoding="utf-8") as f:
    source = f.read()

lexer = Lexer(source)
tokens = lexer.tokenize()

for token in tokens:
    print(token)