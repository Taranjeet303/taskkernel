from flowscript.lexer import Lexer
from flowscript.parser import Parser


def parse_expr(source: str):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).expression()


print(parse_expr("5 + 3 * 2"))
print(parse_expr('"hello"'))
print(parse_expr("true and false"))
print(parse_expr("[1, 2, 3]"))
print(parse_expr('{"name": "Alice"}'))
print(parse_expr("response.status"))
print(parse_expr('http_get("/users")'))
print(parse_expr("response.status == 200"))
print(parse_expr('http_get("/users").status'))
print(parse_expr("foo(1,2).bar.baz"))