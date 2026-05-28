"Interpreting calculator using Reverse Polish Notation."

import argparse
import copy
import io
import math
import os
import pathlib
import re
import readline
import sys

from icecream import ic


__version__ = "0.6.1"


class Error(Exception):
    pass


class Item:
    "Lexical token and/or execution instruction."

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.__class__.__name__

    @property
    def type(self):
        return self.__class__.__name__.lower()

    def __call__(self, executor):
        executor.push(self)


class Whitespace(Item):
    RX = re.compile(r"\s+")

    def __call__(self, executor):
        pass


class Identifier(Item):
    RX = re.compile(r"[a-z]\w*", re.IGNORECASE)

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{self.__class__.__name__} {self.value}"

    def __call__(self, executor):
        executor.dereference(self)

            
class Key(Item):
    RX = re.compile(r"/[a-z]\w*", re.IGNORECASE)

    def __init__(self, value):
        self.value = value[1:]

    def __str__(self):
        return f"/{self.value}"

    def __repr__(self):
        return f"{self.__class__.__name__} {self.value}"


class Value(Item):
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__} {self.value}"

    def __call__(self, executor):
        "Push variable value onto data stack; called by executor.dispatch."
        executor.push(self)


class Bool(Value):
    RX = re.compile(r"true|false")

    def __init__(self, value):
        if not isinstance(value, bool):
            value = value == "true"
        self.value = value

    def __str__(self):
        return "true" if self.value else "false"

    def __repr__(self):
        return f"{self.__class__.__name__} {self}"


class Number(Value):
    pass


class Float(Number):
    RX = re.compile(r"[-+]?\d+\.\d+")

    def __init__(self, value):
        if not isinstance(value, int):
            value = float(value)
        self.value = value


class Integer(Number):
    RX = re.compile(r"[-+]?\d+")

    def __init__(self, value):
        if not isinstance(value, int):
            value = int(value)
        self.value = value


class String(Value):
    RX = re.compile(r'".*?"')

    def __init__(self, value):
        self.value = value.strip('"')

    def __str__(self):
        return f'"{self.value}"'

    def __repr__(self):
        return f'{self.__class__.__name__} "{self.value}"'


class BeginArray(Item):
    RX = re.compile(r"\[")

    def __init__(self, dummy):
        pass

    def __call__(self, executor):
        executor.data_stack.append(self)


class Array(Value):
    RX = re.compile(r"\]")

    def __init__(self, dummy):
        pass

    def __str__(self):
        return f"[{' '.join([str(v) for v in self.value])}]"

    def __call__(self, executor):
        self.value = []
        while executor.data_stack:
            item = executor.data_stack.pop()
            if isinstance(item, BeginArray):
                self.value = list(reversed(self.value))
                break
            self.value.append(item)
        else:
            raise Error("array has no beginning")
        executor.data_stack.append(self)


class ProcedureBegin(Item):
    RX = re.compile(r"\{")

    def __init__(self, dummy):
        self.procedure = Procedure()

    def __call__(self, executor, within_definition=False):
        for item in executor:
            # When procedure defined within procedure.
            if isinstance(item, ProcedureBegin):
                item(executor, within_definition=True)
                self.procedure.append(item.procedure)
            elif isinstance(item, ProcedureEnd):
                break
            elif isinstance(item, Whitespace):
                pass
            else:
                self.procedure.append(item)
        if not within_definition:
            executor.push(self.procedure)


class ProcedureEnd(Item):
    RX = re.compile(r"\}")

    def __init__(self, dummy):
        pass

    def __call__(self, executor):
        pass


class Procedure(Item):
    "Instances placed in the data or exec stacks; not encountered by the lexer."

    def __init__(self):
        self.name = None
        self.code = []

    def __str__(self):
        if self.name:
            return f"Procedure {self.name}"
        else:
            return f"{{{' '.join([str(c) for c in self.code])}}}"

    def __iter__(self):
        self.iterator = iter(self.code)
        return self

    def __next__(self):
        return next(self.iterator)

    def append(self, item):
        self.code.append(item)


class Repeat(Item):
    "Repeat the procedure a number of times."

    def __init__(self, executor, n, proc):
        self.executor = executor
        self.start = n.value
        self.n = n.value
        self.proc = proc

    def __str__(self):
        return f"Repeat {self.n} ({self.start}) {self.proc}"

    def __iter__(self):
        return self

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        self.executor.execute(iter(self.proc))
        return next(self.executor)


class Neg(Item):
    RX = re.compile(r"-")

    def __str__(self):
        return "neg"

    def __repr__(self):
        return "neg"

    def __call__(self, executor):
        executor.execute(iter([Identifier("neg")]))


class Add(Item):
    RX = re.compile(r"\+")

    def __str__(self):
        return "add"

    def __repr__(self):
        return "add"

    def __call__(self, executor):
        executor.execute(iter([Identifier("add")]))


class Sub(Item):
    RX = re.compile(r"\-")

    def __str__(self):
        return "sub"

    def __repr__(self):
        return "sub"

    def __call__(self, executor):
        executor.execute(iter([Identifier("sub")]))


class Mul(Item):
    RX = re.compile(r"\*")

    def __str__(self):
        return "mul"

    def __repr__(self):
        return "mul"

    def __call__(self, executor):
        executor.execute(iter([Identifier("mul")]))


class Div(Item):
    RX = re.compile(r"/")

    def __str__(self):
        return "div"

    def __repr__(self):
        return "div"

    def __call__(self, executor):
        executor.execute(iter([Identifier("div")]))


class Interactive(Item):
    pass


class Stack(Interactive):
    "Print the stack items."

    RX = re.compile(r"=")

    def __init__(self, dummy):
        pass

    def __call__(self, executor):
        if executor.interactive:
            for item in reversed(executor.data_stack):
                print(f" {item}")


class Keyspaces(Interactive):
    "Print the keyspaces."

    RX = re.compile(r"§")

    def __init__(self, dummy):
        pass

    def __call__(self, executor):
        if executor.interactive:
            for pos, keyspace in enumerate(executor.keyspaces):
                indent = "  " * pos
                for key, item in keyspace.items():
                    print(f"{indent}/{key} {item} def")


class Operators(Interactive):
    "Print information about the operators."

    RX = re.compile(r"\?")

    def __init__(self, dummy):
        pass

    def __call__(self, executor):
        if executor.interactive:
            for name in sorted([n for n in dir(executor) if n.startswith("op_")]):
                lines = [s.strip() for s in getattr(executor, name).__doc__.split("\n")]
                lines = [l for l in lines if l]
                print(f"{name[3:]:8}:", lines[0])
                for line in lines[1:]:
                    print(f"          {line}")


class Unknown(Item):
    RX = re.compile(r"\S+")

    def __init__(self, value):
        self.value = value

    def __call__(self, executor):
        raise Error(f"invalid token '{self.value}' in {executor.exec_stack[-1]}")


class Lexer:
    "Iterator delivering items from an input file."

    ITEM_CLASSES = [
        Whitespace,
        Bool,  # Must be checked before identifier!
        Identifier,
        Key,
        Float,
        Integer,
        String,
        BeginArray,
        Array,
        ProcedureBegin,
        ProcedureEnd,
        Add,
        Sub,
        Mul,
        Div,
        Stack,
        Keyspaces,
        Operators,
        Unknown,
    ]

    def __init__(self, infile):
        "If non-interactive, infile is closed when its end has been reached."
        self.infile = infile
        self.name = infile.name
        self.line = ""
        self.line_count = 0
        self.span = (0, 0)

    def __str__(self):
        if self.span[0] + 1 == self.span[1]:
            pos = str(self.span)
        else:
            pos = f"{self.span[0]}-{self.span[1]-1}"
        return f"{self.name} line {self.line_count} pos {pos}: '{self.line[self.span[0]:self.span[1]]}'"

    def __iter__(self):
        return self

    def __next__(self):
        while self.span[1] >= len(self.line):
            if self.interactive:
                try:
                    line = input("rpn > ")
                except (EOFError, KeyboardInterrupt):
                    print()
                    raise StopIteration
            else:
                line = self.infile.readline()
                if not line:
                    self.infile.close()
                    raise StopIteration
            try:
                line = line[: line.index("#")]
            except ValueError:
                pass
            self.line = line.rstrip()
            self.line_count += 1
            self.span = (0, 0)
        for item_class in self.ITEM_CLASSES:
            if m := item_class.RX.match(self.line, self.span[1]):
                self.span = m.span()
                return item_class(m.group())

    @property
    def interactive(self):
        "Is the input coming from an interactive session?"
        return self.infile.isatty()


class Executor:
    "Execute the items provided by the iterator at the top of the execution stack."

    def __init__(self):
        self.exec_stack = []
        self.data_stack = []
        self.keyspaces = [{"e": Float(math.e), "pi": Float(math.pi)}]

    def __call__(self, infile):
        "Parse and execute the items from the input file."
        self.exec_stack.append(Lexer(infile))
        for item in self:
            try:
                item(self)
            except Error as error:
                sys.stderr.write(f"Error: {error}\n")
                sys.stderr.write("--- traceback\n")
                for source in reversed(self.exec_stack):
                    sys.stderr.write(f"  {source}\n")
                sys.stderr.write("--- stack\n")
                for item in reversed(self.data_stack[:3]):
                    sys.stderr.write(f"  {item}\n")
                if len(self.data_stack) == 0:
                    sys.stderr.write("  <empty>\n")
                if len(self.data_stack) > 3:
                    sys.stderr.write(" ...\n")
                if self.interactive:
                    while len(self.exec_stack) != 1:
                        source = self.exec_stack.pop()
                        try:
                            source.infile.close()
                        except AttributeError:
                            pass
                else:
                    sys.exit(1)

    def __iter__(self):
        return self

    def __next__(self):
        while self.exec_stack:
            try:
                return next(self.exec_stack[-1])
            except StopIteration:
                self.exec_stack.pop()
        raise StopIteration

    def __enter__(self):
        "Keep track of items that were popped off the data stack."
        self.popped = []
        return self

    def __exit__(self, type, value, tb):
        "If failure, then put popped items back on stack."
        if type is not None:
            while self.popped:
                self.data_stack.append(self.popped.pop())

    def __getitem__(self, identifier):
        "Lookup up the item by its identifier in the nearest keyspace."
        assert isinstance(identifier, str)
        for keyspace in reversed(self.keyspaces):
            try:
                return keyspace[identifier]
            except KeyError:
                pass
        raise KeyError(identifier)

    def dereference(self, identifier):
        "Dereference the identifer."
        assert isinstance(identifier, Identifier)
        # Reference to a value or procedure.
        try:  
            item = self[identifier.value]
        # Neither variable nor procedure: must be operator.
        except KeyError:
            try:
                method = getattr(self, f"op_{identifier.value}")
            except AttributeError:
                raise Error("undefined identifier")
            else:
                with self:
                    method()
        else:
            if isinstance(item, Procedure):
                item.name = identifier.value
                self.exec_stack.append(iter(item))
            elif isinstance(item, Value):
                item(self)
            else:
                raise NotImplementedError

    @property
    def interactive(self):
        "Is this an interactive session?"
        return self.exec_stack[0].interactive

    @property
    def lexer(self):
        "Return the current lexer."
        for source in reversed(self.exec_stack):
            if isinstance(source, Lexer):
                return source

    def push(self, item):
        "Push the item onto the data stack."
        assert isinstance(item, Item)
        self.data_stack.append(item)

    def pop(self, *item_classes, error=None):
        try:
            self.popped.append(item := self.data_stack.pop())
        except IndexError:
            raise Error("not enough items on the stack")
        if item_classes and not isinstance(item, item_classes):
            raise Error(error or f"Item must be {' or '.join([c.__name__.lower() for c in item_classes])}")
        return item

    def execute(self, iterator):
        "Push the iterator on top of the stack."
        self.exec_stack.append(iterator)

    def dump(self, outfile):
        """Output current state of the executor.
        Do not include any unfinished array from the stack.
        """
        in_array = 0
        for pos in range(len(self.data_stack)):
            if isinstance(self.data_stack[pos], BeginArray):
                in_array += 1
            elif isinstance(self.data_stack[pos], Array):
                in_array -= 1
        # XXX clean up for in_array, in_procedure!
        assert in_array == 0
        for item in self.data_stack:
            outfile.write(f"{item}\n")
        for keyspace in self.keyspaces:
            for key, item in keyspace.items():
                outfile.write(f"/{key} {item} def\n")

    def get_procedure(self, item):
        "If the item is a key, return the procedure associated with its identifier."
        assert isinstance(item, (Procedure, Key))
        if isinstance(item, Key):
            try:
                value = item.value
                item = self[value]
            except KeyError:
                raise Error(f"no such procedure '{value}' defined")
            if not isinstance(item, Procedure):
                raise Error(f"'{value}' does not refer to a procedure")
        return item

    def op_run(self):
        """Open a new input file, read items from it and execute.
        filename => -
        """
        try:
            self.execute(Lexer(open(self.pop(String).value)))
        except IOError as error:
            raise Error(str(error))

    def op_quit(self):
        """Quit from execution without saving to any session file.
        N/A
        """
        sys.exit(0)

    def op_dump(self):
        """Write out the current stack and keyspaces to the named file.
        filename => -
        """
        with open(self.pop(String).value, "w") as outfile:
            self.dump(outfile)

    def op_def(self):
        """Create a variable; a keyed item (value, array, procedure).
        key item => -
        """
        item = self.pop()
        key = self.pop(Key, error="Item must be a key.")
        item.location = str(self.lexer)
        self.keyspaces[-1][key.value] = item

    def op_pop(self):
        """Pop the top item from the stack, and print if interactive.
        item => -
        """
        item = self.pop()
        if self.interactive:
            print(item)

    def op_dup(self):
        """Duplicate the top item. Just the reference, not a full copy.
        item => item item
        """
        item = self.pop()
        self.push(item)
        self.push(item)

    def op_copy(self):
        """Make a full copy of the item and put on the stack.
        item => item copy
        """
        item = self.pop()
        self.push(item)
        self.push(copy.deepcopy(item))

    def op_exch(self):
        """Exchange the two top items on the stack.
        item1 item2 => item2 item1
        """
        item2 = self.pop()
        item1 = self.pop()
        self.push(item2)
        self.push(item1)

    def op_clear(self):
        """Clear all items from the stack.
        ... => &lt;empty&gt;
        """
        while self.data_stack:  # Keep list the same object.
            self.data_stack.pop()

    def op_if(self):
        """Conditional execution of a procedure.
        bool procedureK => -
        """
        proc = self.get_procedure(self.pop(Key, Procedure))
        if not self.pop(Bool).value:
            return
        self.execute(iter(proc))

    def op_ifelse(self):
        """Conditional execution of one of two procedures. If bool is true,
        the first procedure is executed, else the second.
        bool procedure1 procedure2 => -
        """
        proc_false = self.get_procedure(self.pop(Key, Procedure))
        proc_true = self.get_procedure(self.pop(Key, Procedure))
        if self.pop(Bool).value:
            self.execute(iter(proc_true))
        else:
            self.execute(iter(proc_false))

    def op_repeat(self):
        """Repeat the procedure a number of times.
        n procedure => -
        """
        proc = self.get_procedure(self.pop(Key, Procedure))
        n = self.pop(Integer)
        self.execute(Repeat(self, n, proc))

    def op_for(self):
        """Loop the procedure from the initial value using the increment
        up to and including the limit. The loop value is pushed each time
        onto the stack before the procedure is executed.
        initial increment limit procedure => value
        """
        proc = self.get_procedure(self.pop(Key, Procedure))
        limit = self.pop(Number)
        increment = self.pop(Number)
        initial = self.pop(Number)
        self.execute(For(initial, increment, limit, proc))

    def op_count(self):
        """Count the number of elements in the stack, and put
        that number on the stack.
        => number
        """
        self.push(Integer(len(self.data_stack)))

    def op_bool(self):
        """Convert the value to Bool; 0, 0.0, "" and [] are false,
        other values true.
        value => bool
        """
        self.push(Bool(bool(self.pop().value)))

    def op_not(self):
        """Bool 'not'.
        bool => bool
        """
        self.push(Bool(not self.pop(Bool).value))

    def op_and(self):
        """Bool 'and'.
        bool1 bool2 => bool
        """
        self.push(Bool(self.pop(Bool).value and self.pop(Bool).value))

    def op_or(self):
        """Bool 'or'.
        bool1 bool2 => bool
        """
        self.push(Bool(self.pop(Bool).value or self.pop(Bool).value))

    def op_xor(self):
        """Bool 'xor' (exclusive or).
        bool1 bool2 => bool
        """
        self.push(Bool(self.pop(Bool).value != self.pop(Bool).value))

    def op_gt(self):
        """Greater than. The values must of comparable types.
        value1 value2 => bool
        """
        item2 = self.pop()
        item1 = self.pop()
        self._comparable(item1, item2)
        self.push(Bool(item1.value > item2.value))

    def op_ge(self):
        """Greater than or equal to. The values must of comparable types.
        value1 value2 => bool
        """
        item2 = self.pop()
        item1 = self.pop()
        self._comparable(item1, item2)
        self.push(Bool(item1.value >= item2.value))

    def op_lt(self):
        """Less than. The values must of comparable types.
        value1 value2 => bool
        """
        item2 = self.pop()
        item1 = self.pop()
        self._comparable(item1, item2)
        self.push(Bool(item1.value < item2.value))

    def op_le(self):
        """Less than or equal to. The values must of comparable types.
        value1 value2 => bool
        """
        item2 = self.pop()
        item1 = self.pop()
        self._comparable(item1, item2)
        self.push(Bool(item1.value <= item2.value))

    def op_eq(self):
        """Equal to.
        value1 value2 => bool
        """
        item2 = self.pop()
        item1 = self.pop()
        self.push(Bool(item1.value == item2.value))

    def op_ne(self):
        """Not equal to.
        value1 value2 => bool
        """
        item2 = self.pop()
        item1 = self.pop()
        self.push(Bool(item1.value != item2.value))

    def _comparable(self, item1, item2):
        if not (
            (isinstance(item1, (Bool, Number)) and isinstance(item2, (Bool, Number)))
            or (isinstance(item1, (String, Key)) and isinstance(item2, (String, Key)))
            or (isinstance(item1, Array) and isinstance(item2, Array))
        ):
            raise Error(f"item type {item2.type} and {item1.type} are not comparable")

    def op_length(self):
        """Return length of the item (String, Array).
        item => length
        """
        item = self.pop(String, Array)
        self.push(Integer(len(item)))

    def op_integer(self):
        """Convert the value to an integer.
        value => integer
        """
        item = self.pop(Number, String, Bool)
        try:
            self.push(int(item.value))
        except ValueError:
            raise Error(f"cannot convert value '{item.value}' to Integer")

    def op_round(self):
        """Convert the value to the nearest integer.
        value => integer
        """
        item = self.pop(Number, String, Bool)
        try:
            self.push(round(float(item.value)))
        except ValueError:
            raise Error(f"cannot convert value '{item.value}' to Integer")

    def op_float(self):
        """Convert the value to a float.
        value => float
        """
        item = self.pop(Number, String, Bool)
        try:
            self.push(float(item.value))
        except ValueError:
            raise Error(f"cannot convert value '{item.value}' to Float")

    def op_abs(self):
        """Absolute value of the number.
        value => value
        """
        item = self.pop(Number)
        if isinstance(item, Integer):
            self.push(Integer(abs(item.value)))
        else:
            self.push(Float(abs(item.value)))

    def op_neg(self):
        """Negate the number. Also available as '-'.
        value => value
        """
        item = self.pop(Number)
        if isinstance(item, Integer):
            self.push(Integer(-item.value))
        else:
            self.push(Float(-item.value))

    def op_add(self):
        """Add the two numbers on the stack. Also available as '+'.
        value1 value2 => value
        """
        item2 = self.pop(Number)
        item1 = self.pop(Number)
        if isinstance(item1, Integer) and isinstance(item2, Integer):
            self.push(Integer(item1.value + item2.value))
        else:
            self.push(Float(item1.value + item2.value))

    def op_sub(self):
        """Subtract the top number on the stack from the next-to-top number.
        Also available as '-'.
        value1 value2 => value
        """
        item2 = self.pop(Number)
        item1 = self.pop(Number)
        if isinstance(item1, Integer) and isinstance(item2, Integer):
            self.push(Integer(item1.value - item2.value))
        else:
            self.push(Float(item1.value - item2.value))

    def op_mul(self):
        """Multiply the two numbers on the stack. Also available as '*'.
        value1 value2 => value
        """
        item2 = self.pop(Number)
        item1 = self.pop(Number)
        if isinstance(item1, Integer) and isinstance(item2, Integer):
            self.push(Integer(item1.value * item2.value))
        else:
            self.push(Float(item1.value * item2.value))

    def op_div(self):
        """Divide the next-to-top number on the stack by the top number.
        Also available as '/'.
        value1 value2 => value
        """
        item2 = self.pop(Number)
        if item2.value == 0:
            raise Error("cannot divide by zero")
        item1 = self.pop(Number)
        self.push(Float(item1.value / item2.value))

    def op_log(self):
        """Natural logarithm of the number.
        value => value
        """
        item = self.pop(Number)
        if item.value <= 0:
            raise Error("cannot take log of value less or equal to zero")
        self.push(Float(math.log(item.value)))

    def op_log10(self):
        """Base-10 logarithm of the number.
        value => value
        """
        item = self.pop(Number)
        if item.value <= 0:
            raise Error("cannot take log10 of value less or equal to zero")
        self.push(Float(math.log10(item.value)))

    def op_exp(self):
        """'e' raised to the power of the number.
        value => value
        """
        item = self.pop(Number)
        self.push(Float(math.exp(item.value)))

    def op_power(self):
        """The next-to-top number to the power of the top number.
        value1 value2 => value
        """
        item2 = self.pop(Number)
        item1 = self.pop(Number)
        self.push(Float(math.pow(item2, item1)))

    def op_sqrt(self):
        """Square root of the number.
        value => value
        """
        item = self.pop(Number)
        if item.value < 0:
            raise Error("cannot take square root of value less than zero")
        self.push(Float(math.sqrt(item.value)))

    def op_print(self):
        """Pop the top value and print it.
        item => -
        """
        item = self.pop()
        if isinstance(item, String):
            print(item.value)
        else:
            print(item)

    def op_error(self):
        """Raise an error.
        No change.
        """
        raise Error("an error was raised")


def get_command_line_parser():
    "Return the command line parser."
    parser = argparse.ArgumentParser(prog="rpn.py", description=__doc__.splitlines()[0])
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_const",
        const=True,
        default=False,
        help="After executing files, leave in interactive mode.",
    )

    parser.add_argument(
        "-s",
        "--session",
        help="Session file to run first at startup and dump to at exit.",
    )
    parser.add_argument(
        "-S",
        "--autosession",
        action="store_const",
        const=True,
        default=False,
        help="Use the session file defined by environment variable RPN_SESSION_FILE.",
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Names of RPN script files to execute. If none, then interactive mode.",
    )
    return parser


if __name__ == "__main__":
    args = get_command_line_parser().parse_args()

    executor = Executor()

    for filename in args.filenames:
        filename = pathlib.Path(filename)
        if not filename.exists():
            sys.stderr.write(f"Error: file '{filename}' does not exist\n")
            sys.exit(1)

    session = args.session or (args.autosession and os.environ.get("RPN_SESSION_FILE"))
    if session:
        session = pathlib.Path(session)
        if session.exists():
            with open(session) as infile:
                executor(infile)

    for filename in args.filenames:
        with open(filename) as infile:
            executor(infile)

    if not args.filenames or args.interactive:
        executor(sys.stdin)

    if session:
        with open(session, "w") as outfile:
            executor.dump(outfile)
