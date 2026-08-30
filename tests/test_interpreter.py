from flowscript.lexer import Lexer
from flowscript.parser import Parser
from flowscript.interpreter import Interpreter
from flowscript.environment import Environment

# def eval_expr(source: str):
#     tokens = Lexer(source).tokenize()
#     parser = Parser(tokens)
#     expr = parser.expression()  # test expression-level first
#     interp = Interpreter()
#     env = Environment()
#     return interp.evaluate(expr, env)

# print(eval_expr("5 + 3 * 2"))              # 11
# print(eval_expr('"hello" + " world"'))     # "hello world"
# print(eval_expr("10 / 3"))                 # 3.333...
# print(eval_expr("not true"))               # False
# print(eval_expr("[1, 2, 3]"))              # [1, 2, 3]
# print(eval_expr('{"a": 1, "b": 2}'))       # {"a": 1, "b": 2}
# print(eval_expr("false and (1/0 == 0)"))   # should NOT raise if short-circuit works — 1/0 never evaluated
# print(eval_expr("10 / 0"))                 # should raise FlowRuntimeError cleanly
# print(eval_expr("false and (1/0 == 0)"))   # False
# print(eval_expr("true or (1/0 == 0)"))     # True
# print(eval_expr("true and (5 > 3)"))       # True
# print(eval_expr("false or (5 > 3)"))       # True

# ---------- Day 5: full flow execution test ----------

def run_flow(source: str):
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    interp = Interpreter()
    interp.run(program)


source = """
flow test_flow {
    task add(a, b) {
        return a + b
    }

    step "basic math" {
        let x = add(2, 3)
        log(x)
    }

    step "loop test" {
        let total = 0
        for n in [1, 2, 3, 4] {
            total = total + n
        }
        log(total)
    }

    step "conditional" {
        let y = 10
        if y > 5 {
            log("big")
        } else {
            log("small")
        }
    }
}
""".strip()

#run_flow(source)

def test_on_fail():
    source = """flow test_fail {
        step "failing step" {
            let x = 10 / 0
        } on_fail {
            let recovered = 100
            let x = recovered
        }
    }"""

    run_flow(source)


test_on_fail()
print("✅ on_fail test completed successfully")