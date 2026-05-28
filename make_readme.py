"Prepare a Markdown README file for the rpn program."

import sys
import rpn

def print_markdown():
    print(f"# rpn v{rpn.__version__}")
    print()
    print(rpn.__doc__)
    print()
    executor = rpn.Executor()
    print("## Operators")
    print()
    all_ops = set(n[3:] for n in dir(executor) if n.startswith("op_"))
    for title, ops in [("General", ["def", "run", "count", "dump"]),
                       ("Stack", ["print", "pop", "dup", "copy", "exch", "clear"]),
                       ("Control", ["if", "ifelse", "repeat", "for"]),
                       ("Logic", ["bool", "not", "and", "or", "xor", "gt",
                                  "ge", "lt", "le", "eq", "ne"]),
                       ("Numbers", ["integer", "round", "float", "neg"]),
                       ("Math", ["add", "sub", "mul", "div", "log", "log10",
                                 "exp", "power", "sqrt"]),
                       ]:
        print_operators(executor, title, ops)
        all_ops.difference_update(ops)
    print_operators(executor, "Others", all_ops)
    print()
    print("## Predefined variables")
    print()
    for key, value in executor.keyspaces[0].items():
        print(f"- **{key}**: {value}")

def print_operators(executor, title, ops):
    print()
    print(f"### {title}")
    print()
    print("| Operator | Description | Stack |")
    print("| :--- | :--- | :--- |")
    for op in ops:
        lines = getattr(executor, f"op_{op}").__doc__.split("\n")
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        print(f"| **{op}** | {' '.join(lines[:-1])} | {lines[-1].replace('=>', '&rarrow;') if len(lines) > 1 else ""} |")
    print()
    

if __name__ == "__main__":
    with open("README.md", "w") as outfile:
        sys.stdout = outfile
        print_markdown()
