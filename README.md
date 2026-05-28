# rpn v0.6

Interpreting calculator using Reverse Polish Notation.

## Invocation

```
usage: rpn.py [-h] [-i] [-s SESSION] [-S]

Interpreting calculator using Reverse Polish Notation.

options:
  -h, --help            show this help message and exit
  -i, --interactive     After executing files, leave in interactive mode.
  -s SESSION, --session SESSION
                        Session file to run at startup and dump to at exit.
  -S, --autosession     Use the session file defined by environment variable
                        RPN_SESSION_FILE.
```

## Operators


### General

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **def** | Create a variable; a keyed item (value, array, procedure). | key item &rarr; - |
| **run** | Open a new input file, read items from it and execute. | filename &rarr; - |
| **count** | Count the number of elements in the stack, and put that number on the stack. | ... &rarr; ... number |
| **dump** | Write out the current stack and keyspaces to the named file. | filename &rarr; - |
| **quit** | Quit from execution without saving to any session file. | - |

### Stack

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **print** | Pop the top value and print it. | item &rarr; - |
| **pop** | Pop the top item from the stack, and print if interactive. | item &rarr; - |
| **dup** | Duplicate the top item. Just the reference, not a full copy. | item &rarr; item item |
| **copy** | Make a full copy of the item and put on the stack. | item &rarr; item copy |
| **exch** | Exchange the two top items on the stack. | item1 item2 &rarr; item2 item1 |
| **clear** | Clear all items from the stack. | ... &rarr; <empty> |

### Control

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **if** | Conditional execution of a procedure. | bool procedureK &rarr; - |
| **ifelse** | Conditional execution of one of two procedures. If bool is true, the first procedure is executed, else the second. | bool procedure1 procedure2 &rarr; - |
| **repeat** | Repeat the procedure a number of times. | n procedure &rarr; - |
| **for** | Loop the procedure from the initial value using the increment up to and including the limit. The loop value is pushed each time onto the stack before the procedure is executed. | initial increment limit procedure &rarr; value |

### Logic

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **bool** | Convert the value to Bool; 0, 0.0, "" and [] are false, other values true. | value &rarr; bool |
| **not** | Bool 'not'. | bool &rarr; bool |
| **and** | Bool 'and'. | bool1 bool2 &rarr; bool |
| **or** | Bool 'or'. | bool1 bool2 &rarr; bool |
| **xor** | Bool 'xor' (exclusive or). | bool1 bool2 &rarr; bool |
| **gt** | Greater than. The values must of comparable types. | value1 value2 &rarr; bool |
| **ge** | Greater than or equal to. The values must of comparable types. | value1 value2 &rarr; bool |
| **lt** | Less than. The values must of comparable types. | value1 value2 &rarr; bool |
| **le** | Less than or equal to. The values must of comparable types. | value1 value2 &rarr; bool |
| **eq** | Equal to. | value1 value2 &rarr; bool:B |
| **ne** | Not equal to. | value1 value2 &rarr; bool |

### Numbers

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **integer** | Convert the value to an integer. | value &rarr; integer |
| **round** | Convert the value to the nearest integer. | value &rarr; integer |
| **float** | Convert the value to a float. | value &rarr; float |
| **neg** | Negate the number. | value &rarr; value |

### Math

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **add** | Add the two numbers on the stack. | value1 value2:N &rarr; value |
| **sub** | Subtract the top number on the stack from the next-to-top number. | value1 value2 &rarr; value |
| **mul** | Multiply the two numbers on the stack. | value1 value2 &rarr; value |
| **div** | Divide the next-to-top number on the stack by the top number. | value1 value2 &rarr; value |
| **log** | Natural logarithm of the number. | value &rarr; value |
| **log10** | Base-10 logarithm of the number. | value &rarr; value |
| **exp** | 'e' raised to the power of the number. | value &rarr; value |
| **power** | The next-to-top number to the power of the top number. | value1 value2 &rarr; value |
| **sqrt** | Square root of the number. | value &rarr; value |

### Others

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **abs** | Absolute value of the number. | value &rarr; value |
| **error** | Raise an error. | - |
| **length** | Return length of the item (String, Array). | item &rarr; length |

### Interactive

The following one-character operators are available only in interactive mode.

| Operator | Description | Stack |
| :--- | :--- | :--- |
| = | Print the stack | - |
| § | Print the keyspaces | - |
| ? | Print the operators | - |

## Predefined variables

- **e**: 2.718281828459045
- **pi**: 3.141592653589793

# Demo

```
*# Script testing rpn.*

/equality_check {eq {"OK" print} {"Error!" print} ifelse} def

/double {2 mul} def

3 double 6 equality_check
*# > OK*

-2 double -4 equality_check
*# > OK*

-2 double 4 equality_check
*# > Error!*
```
