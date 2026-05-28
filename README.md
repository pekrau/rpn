# rpn v0.6

Interpreter using Reverse Polish Notation.

## Operators


### General

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **def** | Create a variable; a keyed item (value, array, procedure). | key:K item:VAP &rarr; - |
| **run** | Open a new input file, read items from it and execute. | filename(S) &rarr; - |
| **count** | Count the number of elements in the stack, and put that number on the stack. | ... &rarr; ... number:I |
| **dump** |  |  |


### Stack

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **print** | Pop the top value and print it. | item &rarr; - |
| **pop** | Pop the top item from the stack, and print if interactive. | ... item &rarr; ... |
| **dup** | Duplicate the top item. Just the reference, not a full copy. | item &rarr; item item |
| **copy** | Make a full copy of the item and put on the stack. | item &rarr; item itemcopy |
| **exch** | Exchange the two top items on the stack. | item1 item2 &rarr; item2 item1 |
| **clear** | Clear all items from the stack. | ... &rarr; <empty> |


### Control

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **if** | Conditional execution of a procedure. | bool:B procedure:PK &rarr; - |
| **ifelse** | Conditional execution of one of two procedures. If bool is true, the first procedure is executed, else the second. | bool:B procedure1:PK procedure2:PK &rarr; - |
| **repeat** | Repeat the procedure a number of times. | n:I procedure:PK &rarr; - |
| **for** | Loop the procedure from the initial value using the increment up to and including the limit. The loop value is pushed each time onto the stack before the procedure is executed. | initial:N increment:N limit:N procedure:PK &rarr; value:N |


### Logic

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **bool** | Convert the value to Bool; 0, 0.0, "" and [] are false, other values true. | value:NSA &rarr; bool:B |
| **not** | Bool 'not'. | bool:B &rarr; bool:B |
| **and** | Bool 'and'. | bool1:B bool2:B &rarr; bool:B |
| **or** | Bool 'or'. | bool1:B bool2:B &rarr; bool:B |
| **xor** | Bool 'xor' (exclusive or). | bool1:B bool2:B &rarr; bool:B |
| **gt** | Greater than. The values must of comparable types. | value1:NSKA value2:NSKA &rarr; bool:B |
| **ge** | Greater than or equal to. The values must of comparable types. | value1:NSKA value2:NSKA &rarr; bool:B |
| **lt** | Less than. The values must of comparable types. | value1:NSKA value2:NSKA &rarr; bool:B |
| **le** | Less than or equal to. The values must of comparable types. | value1:NSKA value2:NSKA &rarr; bool:B |
| **eq** | Equal to. The values must of comparable types. | value1:NSKA value2:NSKA &rarr; bool:B |
| **ne** | Not equal to. | value1:NSKA value2:NSKA &rarr; bool:B |


### Numbers

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **integer** | Convert the value to an integer. | value:NSB &rarr; integer:I |
| **round** | Convert the value to the nearest integer. | value:NSB &rarr; integer:I |
| **float** | Convert the value to a float. | value:NSB &rarr; float:F |
| **neg** | Negate the number. | value:N &rarr; value:N |


### Math

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **add** | Add the two numbers on the stack. | value1:N value2:N &rarr; value:N |
| **sub** | Subtract the top number on the stack from the next-to-top number. | value1:N value2:N &rarr; value:N |
| **mul** | Multiply the two numbers on the stack. | value1:N value2:N &rarr; value:N |
| **div** | Divide the next-to-top number on the stack by the top number. | value1:N value2:N &rarr; value:N |
| **log** | Natural logarithm of the number. | value:N &rarr; value:F |
| **log10** | Base-10 logarithm of the number. | value:N &rarr; value:F |
| **exp** | 'e' raised to the power of the number. | value:N &rarr; value:F |
| **power** | The next-to-top number to the power of the top number. | value1:N value2:N &rarr; value:F |
| **sqrt** | Square root of the number. | value:N &rarr; value:F |


### Others

| Operator | Description | Stack |
| :--- | :--- | :--- |
| **length** | Return length of the item (String, Array). | item:SA &rarr; length:I |
| **error** |  |  |
| **quit** |  |  |


## Predefined variables

- **e**: 2.718281828459045
- **pi**: 3.141592653589793
