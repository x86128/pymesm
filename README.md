# Integer-only MESM6-like machine

Split data and program memory, each consist of 65536 words.

32 bit instruction words packed as pairs to 64bit words. So, maximum program size is 131072 instructions. 

Data memory is 65536 32-bit words.

16 bit program counter.

Same instruction op_codes numbers as MESM6 (total of 64+16).

For simplicity, CPU instruction encoded as:

| 8 bit | 8 bit | 16 bit |
|---|---|---|
| index | op_code | address |

