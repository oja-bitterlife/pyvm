let ADDR_ERROR = 0xFF

let OP_HALT = 0x00
let OP_LDC = 0x01  // Load (R0) Constant(word)
let OP_LD = 0x02  // Load (R0) from memory
let OP_ST = 0x03  // Store (R0) to memory
let OP_STA = 0x04  // Store (R0) to VM[R1]
let OP_JMP = 0x10  // Jump
let OP_JZ = 0x11  // Jump if Zero (R0 == 0)
let OP_JNZ = 0x12  // Jump if Not Zero (R0 != 0)
let OP_CMP = 0x20  // R0とR1を比較してR0に 0 or 1 で結果を格納。比較演算はSubコードで指定する。
let OP_NOT = 0x30  // R0 = R0 != 0 ? 1 : 0
let OP_ADD = 0x31  // R0 = R0 + R1
let OP_SUB = 0x32  // R0 = R0 - R1
let OP_MUL = 0x33  // R0 = R0 * R1
let OP_DIV = 0x34  // R0 = R0 / R1
let OP_MOD = 0x35  // R0 = R0 % R1

// 比較演算のサブコード
let CMP_EQ = 0x00  // R0 == R1
let CMP_NE = 0x01  // R0 != R1
let CMP_LT = 0x02  // R0 < R1
let CMP_LE = 0x03  // R0 <= R1
let CMP_GT = 0x04  // R0 > R1
let CMP_GE = 0x05  // R0 >= R1
