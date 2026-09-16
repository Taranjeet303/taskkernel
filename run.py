import sys

from flowscript.lexer import Lexer
from flowscript.parser import Parser
from flowscript.interpreter import Interpreter
from flowscript.environment import Environment


def main():
    if len(sys.argv) != 2:
        print("Usage: python run.py <file.flow>")
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename, "r", encoding="utf-8") as file:
        source = file.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    program = parser.parse()

    interpreter = Interpreter()
    env = Environment()
    result = interpreter.execute(program, env)
    
   

    if result is not None:
        print(result)


if __name__ == "__main__":
    main()