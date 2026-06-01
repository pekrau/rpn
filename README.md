# rpn v0.7.1

Interpreting calculator using Reverse Polish Notation.

## Invocation

```
usage: rpn.py [-h] [-i] [-s SESSION] [-S] [filenames ...]

Interpreting calculator using Reverse Polish Notation.

positional arguments:
  filenames             Names of RPN script files to execute. If none, then
                        interactive mode.

options:
  -h, --help            show this help message and exit
  -i, --interactive     After executing files, leave in interactive mode.
  -s SESSION, --session SESSION
                        Session file to run first at startup and dump to at
                        exit.
  -S, --autosession     Use the session file defined by environment variable
                        RPN_SESSION_FILE.
```

## Operators


### General

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **def** | Create a variable in the current keyspace. A variable is a keyed item (value, array, procedure). | key item &rarr; - |
| **del** | Delete a variable from the current keyspace. If no such variable, then no effect. | key &rarr; - |
| **run** | Open a new input file, read items from it and execute. | filename &rarr; - |
| **count** | Count the number of elements in the stack, and put that number on the stack. | &rarr; number |
| **dump** | Write out the current stack and keyspaces to the named file. | filename &rarr; - |
| **quit** | Quit from execution without saving to any session file. | N/A |

### Stack

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **pop** | Pop the top item from the stack, and print if interactive. | item &rarr; - |
| **dup** | Duplicate the top item. A full copy is created. | item &rarr; item item |
| **exch** | Exchange the two top items on the stack. | item1 item2 &rarr; item2 item1 |
| **clear** | Clear all items from the stack. | ... &rarr; &lt;empty&gt; |
| **print** | Pop the top value and print it. | item &rarr; - |

### Control

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **if** | Conditional execution of a procedure. | bool procedureK &rarr; - |
| **ifelse** | Conditional execution of one of two procedures. If bool is true, the first procedure is executed, else the second. | bool procedure1 procedure2 &rarr; - |
| **loop** | Infinite loop over the procedure. Use operator 'exit' to quit it. | procedure &rarr; - |
| **repeat** | Repeat the procedure a number of times. | n procedure &rarr; - |
| **for** | Loop the procedure from the initial value using the increment up to and including the limit. The loop value is pushed each time onto the stack before the procedure is executed. | initial increment limit procedure &rarr; value |
| **exit** | Exit the innermost loop. In none, then no action. | - |

### Logic

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **bool** | Convert the value to Bool; 0, 0.0, "" and [] are false, other values true. | value &rarr; bool |
| **not** | Bool 'not'. | bool &rarr; bool |
| **and** | Bool 'and'. | bool1 bool2 &rarr; bool |
| **or** | Bool 'or'. | bool1 bool2 &rarr; bool |
| **xor** | Bool 'xor' (exclusive or). | bool1 bool2 &rarr; bool |
| **gt** | Greater than; value1 > value2. The values must of comparable types. | value2 value1 &rarr; bool |
| **ge** | Greater than or equal to; value1 >= value2. The values must of comparable types. | value2 value1 &rarr; bool |
| **lt** | Less than; value1 < value2. The values must of comparable types. | value2 value1 &rarr; bool |
| **le** | Less than or equal to; value1 <= value2. The values must of comparable types. | value2 value1 &rarr; bool |
| **eq** | Equal to; value1 == value2. | value1 value2 &rarr; bool |
| **ne** | Not equal to; value1 != value2. | value1 value2 &rarr; bool |

### Numbers

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **integer** | Convert the value to an integer. | value &rarr; integer |
| **round** | Convert the value to the nearest integer. | value &rarr; integer |
| **float** | Convert the value to a float. | value &rarr; float |
| **abs** | Absolute value of the number. | value &rarr; value |
| **neg** | Negate the number. | value &rarr; value |

### Math

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **add** | Add the two numbers on the stack. Also available as '+'. | value1 value2 &rarr; value |
| **sub** | Subtract the top number on the stack from the next-to-top number; value1 - value2. Also available as '-'. | value1 value2 &rarr; value |
| **mul** | Multiply the two numbers on the stack. Also available as '*'. | value1 value2 &rarr; value |
| **div** | Divide the next-to-top number on the stack by the top number; value1 / value2. Also available as '/'. | value1 value2 &rarr; value |
| **log** | Natural logarithm of the number. | value &rarr; value |
| **log10** | Base-10 logarithm of the number. | value &rarr; value |
| **exp** | 'e' raised to the power of the number. | value &rarr; value |
| **power** | The next-to-top number to the power of the top number; value1 ^ value2. | value1 value2 &rarr; value |
| **sqrt** | Square root of the number. | value &rarr; value |

### Trigonometry

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **cos** | Cosine of the number (radians). | value &rarr; value |
| **sin** | Sine of the number (radians). | value &rarr; value |
| **tan** | Tangent of the number (radians). | value &rarr; value |
| **acos** | Arc cosine of the number (radians). | value &rarr; value |
| **asin** | Arc sine of the number (radians). | value &rarr; value |
| **atan** | Arc tangent of the number (radians). | value &rarr; value |
| **atan2** | Arc tangent of the next-to-top number divided by the top number (radians). | value1 value2 &rarr; value |
| **degrees** | Convert the value in radians to degrees. | value &rarr; value |
| **radians** | Convert the value in degrees to radians. | value &rarr; value |

### Others

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **length** | Return length of the item (String, Array). | item &rarr; length |
| **error** | Raise an error. | No change. |
| **noop** | No operation. | No change. |

### Interactive

The following one-character operators are available only in interactive mode.

| Operator | Description | Stack |
| :--- | :--- | :--- |
| = | Print the stack. | No change. |
| § | Print the keyspaces. | No change. |
| ? | Print the operators. | No change. |

## Predefined variables

- **e**: 2.718281828459045
- **pi**: 3.141592653589793

# Demo

```
# Script testing rpn.

/equality_check {eq {"OK" print} {"Error!" print} ifelse} def

/double {2 mul} def

3 double 6 equality_check
# > OK

-2 double -4 equality_check
# > OK

-2 double 4 equality_check
# > Error!

```
