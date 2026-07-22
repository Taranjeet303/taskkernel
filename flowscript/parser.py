from .tokens import Token, TokenType
from .ast_nodes import (
    # Base expression nodes
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    Identifier,
    BinaryOp,
    UnaryOp,
    Call,
    MemberAccess,
    ListLiteral,
    RecordLiteral,

    # Statement nodes
    LetStmt,
    AssignStmt,
    IfStmt,
    WhileStmt,
    ForStmt,
    ReturnStmt,
    ExprStmt,

    # Helper nodes
    Parameter,

    # Top-level nodes
    TaskDef,
    OnFailClause,
    StepDef,
    FlowDef,
    Program,
)


class ParseError(Exception):
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"Parse error at line {line}, col {col}: {message}")


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # ---------- token stream helpers ----------

    def peek(self) -> Token:
        return self.tokens[self.pos]
    
    def peek_next(self) -> Token:
        if self.pos + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos + 1]

    def previous(self) -> Token:
        return self.tokens[self.pos - 1]

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def check(self, type_: TokenType) -> bool:
        return self.peek().type == type_

    def advance(self) -> Token:
        if not self.is_at_end():
            self.pos += 1
        return self.previous()

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, type_: TokenType, message: str) -> Token:
        if self.check(type_):
            return self.advance()
        tok = self.peek()
        raise ParseError(message, tok.line, tok.col)

    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            pass

    # ---------- expression grammar (precedence climbing) ----------
    

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        expr = self.logical_and()
        while self.match(TokenType.OR):
            op_tok = self.previous()
            right = self.logical_and()
            expr = BinaryOp(expr, "or", right, op_tok.line, op_tok.col)
        return expr

    def logical_and(self):
        expr = self.equality()
        while self.match(TokenType.AND):
            op_tok = self.previous()
            right = self.equality()
            expr = BinaryOp(expr, "and", right, op_tok.line, op_tok.col)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.EQ_EQ, TokenType.NOT_EQ):
            op_tok = self.previous()
            right = self.comparison()
            expr = BinaryOp(expr, op_tok.lexeme, right, op_tok.line, op_tok.col)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.LT, TokenType.GT, TokenType.LT_EQ, TokenType.GT_EQ):
            op_tok = self.previous()
            right = self.term()
            expr = BinaryOp(expr, op_tok.lexeme, right, op_tok.line, op_tok.col)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self.previous()
            right = self.factor()
            expr = BinaryOp(expr, op_tok.lexeme, right, op_tok.line, op_tok.col)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            op_tok = self.previous()
            right = self.unary()
            expr = BinaryOp(expr, op_tok.lexeme, right, op_tok.line, op_tok.col)
        return expr

    def unary(self):
        if self.match(TokenType.NOT, TokenType.MINUS):
            op_tok = self.previous()
            operand = self.unary()
            return UnaryOp(op_tok.lexeme, operand, op_tok.line, op_tok.col)
        return self.call()

    def call(self):
        expr = self.primary()

        while True:

           
            if self.match(TokenType.DOT):
                dot = self.previous()

                identifier = self.consume(
                    TokenType.IDENTIFIER,
                    "Expected identifier after '.'."
                )

                expr = MemberAccess(
                    base=expr,
                    member=identifier.lexeme,
                    line=dot.line,
                    col=dot.col
                )

            
            elif self.match(TokenType.LPAREN):
                lparen = self.previous()

                arguments = []

                if not self.check(TokenType.RPAREN):
                    arguments.append(self.expression())

                    while self.match(TokenType.COMMA):
                        arguments.append(self.expression())

                self.consume(
                    TokenType.RPAREN,
                    "Expected ')' after arguments."
                )

                expr = Call(
                    callee=expr,
                    arguments=arguments,
                    line=lparen.line,
                    col=lparen.col
                )

            else:
                break

        return expr


    def primary(self):

        if self.match(TokenType.NUMBER):
            token = self.previous()
            return NumberLiteral(
                value=token.literal,
                line=token.line,
                col=token.col
            )

        if self.match(TokenType.STRING):
            token = self.previous()
            return StringLiteral(
                value=token.literal,
                line=token.line,
                col=token.col
            )

        if self.match(TokenType.TRUE, TokenType.FALSE):
            token = self.previous()
            return BooleanLiteral(
                value=token.literal,
                line=token.line,
                col=token.col
            )

        if self.match(TokenType.IDENTIFIER):
            token = self.previous()
            return Identifier(
                name=token.lexeme,
                line=token.line,
                col=token.col
            )

        if self.match(TokenType.LPAREN):
            expr = self.expression()

            self.consume(
                TokenType.RPAREN,
                "Expected ')' after expression."
            )

            return expr

        if self.match(TokenType.LBRACKET):
            start = self.previous()
            self.skip_newlines()

            elements = []

            if not self.check(TokenType.RBRACKET):
                elements.append(self.expression())

                while self.match(TokenType.COMMA):
                     self.skip_newlines()
                     elements.append(self.expression())

            self.skip_newlines()          

            self.consume(
                TokenType.RBRACKET,
                "Expected ']' after list."
            )

            return ListLiteral(
                elements=elements,
                line=start.line,
                col=start.col
            )

        if self.match(TokenType.LBRACE):
            start = self.previous()
            self.skip_newlines()

            fields = {}

            if not self.check(TokenType.RBRACE):

                key = self.consume(
                    TokenType.STRING,
                    "Expected string key."
                )

                self.consume(
                    TokenType.COLON,
                    "Expected ':' after key."
                )

                value = self.expression()

                fields[key.literal] = value

                while self.match(TokenType.COMMA):
                    self.skip_newlines()

                    key = self.consume(
                        TokenType.STRING,
                        "Expected string key."
                    )

                    self.consume(
                        TokenType.COLON,
                        "Expected ':' after key."
                    )

                    value = self.expression()

                    fields[key.literal] = value

            self.skip_newlines()        

            self.consume(
                TokenType.RBRACE,
                "Expected '}' after record."
            )

            return RecordLiteral(
                fields=fields,
                line=start.line,
                col=start.col
    )

        token = self.peek()

        if token.type == TokenType.EOF:
            raise ParseError(
                "Unexpected end of input",
                token.line,
                token.col
            )

        raise ParseError(
            f"Unexpected token '{token.lexeme}'",
            token.line,
            token.col
        )
    
#--------------statement parsing--------------------------
    def let_statement(self):
        let_tok = self.consume(TokenType.LET, "Expected 'let'.")
        
        name_tok = self.consume(TokenType.IDENTIFIER, "Expected variable name.")
        
        type_annotation = None
        if self.match(TokenType.COLON):
            type_tok = self.consume(TokenType.IDENTIFIER, "Expected type name after ':'.")
            type_annotation = type_tok.lexeme
        
        self.consume(TokenType.EQ, "Expected '=' after variable name.")
        
        value = self.expression()
        
        self.consume(TokenType.NEWLINE, "Expected newline after variable declaration.")
        
        return LetStmt(
            name=name_tok.lexeme,
            type_annotation=type_annotation,
            value=value,
            line=let_tok.line,
            col=let_tok.col
        )    
    
    def assign_statement(self):
        identifier_tok = self.consume(
            TokenType.IDENTIFIER,
            "Expected variable name."
        )

        self.consume(
            TokenType.EQ,
            "Expected '=' after variable name."
        )

        value = self.expression()

        self.consume(
            TokenType.NEWLINE,
            "Expected newline after assignment."
        )

        return AssignStmt(
            target=Identifier(
                name=identifier_tok.lexeme,
                line=identifier_tok.line,
                col=identifier_tok.col,
            ),
            value=value,
            line=identifier_tok.line,
            col=identifier_tok.col,
        )
    
    def if_statement(self):
        if_tok = self.consume(
            TokenType.IF,
            "Expected 'if'."
        )

        condition = self.expression()

        then_branch = self.block()

        else_branch = None

        if self.match(TokenType.ELSE):
            else_branch = self.block()

        return IfStmt(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            line=if_tok.line,
            col=if_tok.col,
        )
    
    def while_statement(self):
        while_tok = self.consume(
            TokenType.WHILE,
            "Expected 'while'."
        )

        condition = self.expression()

        body = self.block()

        return WhileStmt(
            condition=condition,
            body=body,
            line=while_tok.line,
            col=while_tok.col,
        )
    def for_statement(self):
        for_tok = self.consume(
            TokenType.FOR,
            "Expected 'for'."
        )

        variable_tok = self.consume(
            TokenType.IDENTIFIER,
            "Expected loop variable after 'for'."
        )

        self.consume(
            TokenType.IN,
            "Expected 'in' after loop variable."
        )

        iterable = self.expression()

        body = self.block()

        return ForStmt(
            variable=variable_tok.lexeme,
            iterable=iterable,
            body=body,
            line=for_tok.line,
            col=for_tok.col,
        )
    
    def return_statement(self):
        return_tok = self.consume(
            TokenType.RETURN,
            "Expected 'return'."
        )

        value = None

        if not self.check(TokenType.NEWLINE):
            value = self.expression()

        self.consume(
            TokenType.NEWLINE,
            "Expected newline after return statement."
        )

        return ReturnStmt(
            value=value,
            line=return_tok.line,
            col=return_tok.col,
        )
    
    def expression_statement(self):
        expr = self.expression()

        self.consume(
            TokenType.NEWLINE,
            "Expected newline after expression."
        )

        return ExprStmt(
            expression=expr,
            line=expr.line,
            col=expr.col,
        )
    
    def statement(self):

        self.skip_newlines()

        if self.check(TokenType.LET):
            return self.let_statement()

        if (
            self.check(TokenType.IDENTIFIER)
            and self.peek_next().type == TokenType.EQ
        ):
            return self.assign_statement()

        if self.check(TokenType.IF):
            return self.if_statement()

        if self.check(TokenType.WHILE):
            return self.while_statement()

        if self.check(TokenType.FOR):
            return self.for_statement()

        if self.check(TokenType.RETURN):
            return self.return_statement()

        return self.expression_statement()
    
    def block(self):
        self.consume(
            TokenType.LBRACE,
            "Expected '{' to start block."
        )

        self.skip_newlines()

        statements = []

        while True:

            self.skip_newlines()

            if self.check(TokenType.RBRACE):
                break

            if self.is_at_end():
                tok = self.peek()
                raise ParseError(
                    "Expected '}' before end of input.",
                    tok.line,
                    tok.col,
                )

            statements.append(self.statement())

        self.consume(
            TokenType.RBRACE,
            "Expected '}' after block."
        )

        self.skip_newlines()

        return statements
    
#----------- Top-Level Parsing  ----------------------

    def task_definition(self):
        task_tok = self.consume(
            TokenType.TASK,
            "Expected 'task'."
        )

        name_tok = self.consume(
            TokenType.IDENTIFIER,
            "Expected task name."
        )

        self.consume(
            TokenType.LPAREN,
            "Expected '(' after task name."
        )

        params = []

        if not self.check(TokenType.RPAREN):
            while True:
                param_tok = self.consume(
                    TokenType.IDENTIFIER,
                    "Expected parameter name."
                )

                type_annotation = None

                if self.match(TokenType.COLON):
                    type_tok = self.consume(
                        TokenType.IDENTIFIER,
                        "Expected type name after ':'."
                    )
                    type_annotation = type_tok.lexeme

                params.append(
                    Parameter(
                        name=param_tok.lexeme,
                        type_annotation=type_annotation,
                    )
                )

                if not self.match(TokenType.COMMA):
                    break

        self.consume(
            TokenType.RPAREN,
            "Expected ')' after parameters."
        )

        body = self.block()

        return TaskDef(
            name=name_tok.lexeme,
            params=params,
            body=body,
            line=task_tok.line,
            col=task_tok.col,
        )
    
    def on_fail_clause(self):
        on_fail_tok = self.consume(
            TokenType.ON_FAIL,
            "Expected 'on_fail'."
        )

        body = self.block()

        return OnFailClause(
            body=body,
            line=on_fail_tok.line,
            col=on_fail_tok.col,
        )
    
    def step_definition(self):
        step_tok = self.consume(
            TokenType.STEP,
            "Expected 'step'."
        )

        label_tok = self.consume(
            TokenType.STRING,
            "Expected step label."
        )

        body = self.block()

        self.skip_newlines()

        on_fail = None

        if self.check(TokenType.ON_FAIL):
            on_fail = self.on_fail_clause()

        return StepDef(
            label=label_tok.literal,
            body=body,
            on_fail=on_fail,
            line=step_tok.line,
            col=step_tok.col,
        )
    
    def flow_definition(self):
        flow_tok = self.consume(
            TokenType.FLOW,
            "Expected 'flow'."
        )

        name_tok = self.consume(
            TokenType.IDENTIFIER,
            "Expected flow name."
        )

        self.consume(
            TokenType.LBRACE,
            "Expected '{' after flow name."
        )

        self.skip_newlines()

        body = []

        while True:

            self.skip_newlines()

            if self.is_at_end():
                tok = self.peek()
                raise ParseError(
                    "Expected '}' after flow body.",
                    tok.line,
                    tok.col,
                )

            if self.check(TokenType.RBRACE):
                break

            if self.check(TokenType.STEP):
                body.append(self.step_definition())

            elif self.check(TokenType.TASK):
                body.append(self.task_definition())

            else:
                body.append(self.statement())

        self.consume(
            TokenType.RBRACE,
            "Expected '}' after flow body."
        )

        self.skip_newlines()

        return FlowDef(
            name=name_tok.lexeme,
            body=body,
            line=flow_tok.line,
            col=flow_tok.col,
        )
    def parse(self):
        flows = []

        if self.is_at_end():
            tok = self.peek()
            raise ParseError(
                "Expected at least one flow definition.",
                tok.line,
                tok.col,
            )

        while not self.is_at_end():
            flows.append(self.flow_definition())

        return Program(flows=flows)