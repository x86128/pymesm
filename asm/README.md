# Mesm-mini simple assembler

Used to write CPU tests.

One line of *.asm file is one instruction to assembler.

## Assembler directives

| directive | description |
|---|---|
| org _address_ | set PC to address |
| dorg _address_ | set DP to address (data pointer, for initialised variables and arrays) |
| ptr _name_ _address_ | occurrences of _name_ will be replace to _address_ |
| arr _name_ "string" | _name_ will be replaced with addr of first word of string |
| arr _name_ [list of numbers] | _name_ will be replaced with addr of first element |
| arr _name_ number | _name_ will be replaced with addr of number in data memory |
| mem _name_ _size_ | allocates buffer of _size_ in data memory |
| lbl _name_ | bind to _name_ current val of PC |

## Instructions encoding

`xta addr`, where `addr` is _oct_, _dec_ or _hex_ (in Python style)

`xta name`, if name is _ptr_ replaced with address, if name is _arr_ replaced with address of first element.

`xta name[2]`, if name is arr/mem then will be replaced with addr of third element.

`xta name+5,12`, offset and index register also possible

## example

```
# example of switches to leds
org 1
ptr switches 0x800
ptr leds 0x800
lbl start
xta switches
atx leds
uj start
```
