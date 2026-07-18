from flowscript.lexer import Lexer

source = """
flow user_import {

    step "Fetch Users" {

        let retries = 3

        if retries < 5 {
            retries = retries + 1
        }

    }

}
"""

lexer = Lexer(source)
tokens = lexer.tokenize()

for token in tokens:
    print(token)