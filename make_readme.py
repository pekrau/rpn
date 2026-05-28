"Prepare a Markdown README file for the rpn program."

import sys
import rpn

def print_markdown():
    print(f"# rpn v{rpn.__version__}")

    print()
    print(rpn.__doc__)

    print()
    print("## Invocation")
    print()

    print("```")
    rpn.get_command_line_parser().print_help()
    print("```")

    executor = rpn.Executor()
    print()
    print("## Operators")
    print()
    all_ops = set(n[3:] for n in dir(executor) if n.startswith("op_"))
    for title, ops in [("General", ["def", "run", "count", "dump", "quit"]),
                       ("Stack", ["print", "pop", "dup", "copy", "exch", "clear"]),
                       ("Control", ["if", "ifelse", "repeat", "for"]),
                       ("Logic", ["bool", "not", "and", "or", "xor", "gt",
                                  "ge", "lt", "le", "eq", "ne"]),
                       ("Numbers", ["integer", "round", "float", "abs", "neg"]),
                       ("Math", ["add", "sub", "mul", "div", "log", "log10",
                                 "exp", "power", "sqrt"]),
                       ]:
        print_operators(executor, title, ops)
        all_ops.difference_update(ops)
    if all_ops:
        print_operators(executor, "Others", all_ops)

    print()
    print("### Interactive")
    print()
    print("The following one-character operators are available only in interactive mode.")

    print()
    print("| Operator | Description | Stack |")
    print("| :--- | :--- | :--- |")
    print("| = | Print the stack | No change. |")
    print("| § | Print the keyspaces | No change. |")
    print("| ? | Print the operators | No change. |")

    print()
    print("## Predefined variables")
    print()
    for key, value in executor.keyspaces[0].items():
        print(f"- **{key}**: {value}")

    print()
    print("# Demo")
    print()
    print("```")
    print(open("test.rpn").read())
    print("```")
    

def print_operators(executor, title, ops):
    print()
    print(f"### {title}")
    print()
    print("| Operator | Description | Stack |")
    print("| :--- | :--- | :--- |")
    for op in ops:
        lines = getattr(executor, f"op_{op}").__doc__.splitlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        if len(lines) > 1:
            stack = lines[-1].replace('=>', '&rarr;')
            lines = lines[:-1]
        else:
            stack = "-"
        print(f"| **{op}** | {' '.join(lines)} | {stack} |")
    

if __name__ == "__main__":
    with open("README.md", "w") as outfile:
        sys.stdout = outfile
        print_markdown()
