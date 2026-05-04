import sys
import re
from enum import Enum, auto
from collections import OrderedDict
# General opcode mapping
# Bits [3:2] = MSB, Bits [1:0] = LSB

opcode_map = {
    "ALU-R":  "0000",
    "CMP-R":  "0010",
    "SW":     "0101",
    "BRANCH": "0110",
    "ALU-I":  "1000",
    "LW":     "1001",
    "CMP-I":  "1010",
    "JAL":    "1011",
}

alu_function_map = {
    "ADD":   "0000",
    "ADDI":  "0000",
    "SUB":   "0001",
    "SUBI":  "0001",
    "AND":   "0100",
    "ANDI":  "0100",
    "OR":    "0101",
    "ORI":   "0101",
    "XOR":   "0110",
    "XORI":  "0110",
    "NAND":  "1100",
    "NANDI": "1100",
    "NOR":   "1101",
    "NORI":  "1101",
    "NXOR":  "1110",
    "NXORI": "1110",
}

cmp_function_map = {
    "F":     "0000",
    "FI":    "0000",
    "EQ":    "0001",
    "EQI":   "0001",
    "LT":    "0010",
    "LTI":   "0010",
    "LTE":   "0011",
    "LTEI":  "0011",
    "T":     "1000",
    "TI":    "1000",
    "NE":    "1001",
    "NEI":   "1001",
    "GTE":   "1010",
    "GTEI":  "1010",
    "GT":    "1011",
    "GTI":   "1011",
}

branch_function_map = {
    "BF":    "0000",
    "BEQ":   "0001",
    "BLT":   "0010",
    "BLTE":  "0011",
    "BEQZ":  "0101",
    "BLTZ":  "0110",
    "BLTEZ": "0111",
    "BT":    "1000",
    "BNE":   "1001",
    "BGTE":  "1010",
    "BGT":   "1011",
    "BNEZ":  "1101",
    "BGTEZ": "1110",
    "BGTZ":  "1111",
}

class InstrType(Enum):
    ALU_R = auto()
    ALU_I = auto()
    CMP_R = auto()
    CMP_I = auto()
    LOAD = auto()
    STORE = auto()
    BRANCH = auto()
    JAL = auto()
    LABEL = auto()
    ORIG = auto()
    WORD = auto()
    NAME = auto()
    PSEUDO = auto()
    EMPTY = auto()
    UNKNOWN = auto()

pseudo_instructions = {
    "BR":   {"fmt": "imm",         "itext": ["BEQ R6,R6,imm"]},
    "NOT":  {"fmt": "RD,RS",       "itext": ["NAND RD,RS,RS"]},
    "BLE":  {"fmt": "RS1,RS2,imm", "itext": ["LTE R6,RS1,RS2","BNEZ R6,imm"]},
    "BGE":  {"fmt": "RS1,RS2,imm", "itext": ["GTE R6,RS1,RS2","BNEZ R6,imm"]},
    "CALL": {"fmt": "imm(RS1)",    "itext": ["JAL RA,imm(RS1)"]},
    "RET":  {"fmt": "",            "itext": ["JAL R9,0(RA)"]},
    "JMP":  {"fmt": "imm(RS1)",    "itext": ["JAL R9,imm(RS1)"]},
}
label_table = {}
def read_file_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.readlines()

def write_file_lines(filepath, lines):
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

def parseint(intstr):
    if intstr.lower().startswith("0x"):
        return int(intstr, 16)
    else:
        return int(intstr)
def parseOrig(line):
    parts = line.strip().split()

    value = parts[1]

    return parseint(value)

def parseLabel(line):
    return line.strip().split(':')[0]

def build_line_pc_map(lines):
    pc = 0
    line_to_pc = OrderedDict()

    for line in lines:
        line = line.strip()
        instr_type = classify(line)
        if(instr_type == InstrType.UNKNOWN):
            continue


        if instr_type == InstrType.LABEL:
            lname = parseLabel(line)
            label_table[lname] = pc
            continue

        if instr_type == InstrType.ORIG:
            pc = parseOrig(line);
            continue

        if instr_type == InstrType.NAME:
            continue


        if instr_type in {
            InstrType.ALU_R,
            InstrType.ALU_I,
            InstrType.CMP_R,
            InstrType.CMP_I,
            InstrType.LOAD,
            InstrType.STORE,
            InstrType.BRANCH,
            InstrType.JAL,
            InstrType.WORD,
        }:
            line_to_pc[pc] = line
            pc += 4

    return line_to_pc

def parse(line: str) -> tuple[str, str]:
    parts    = line.split(None, 1)
    mnemonic = parts[0].upper()
    operands = parts[1].strip() if len(parts) > 1 else ""
    return mnemonic, operands

def expand(mnemonic: str, operands: str) -> list[str]:
    entry      = pseudo_instructions[mnemonic]
    fmt_tokens = [t.strip() for t in entry["fmt"].split(",")] if entry["fmt"] else []
    op_tokens  = [t.strip() for t in operands.split(",")] if operands else []
    bindings   = dict(zip(fmt_tokens, op_tokens))

    def apply(template: str) -> str:
        for k, v in bindings.items():
            template = template.replace(k, v)
        return template

    return [apply(t) for t in entry["itext"]]

def pseudo_map(lines):
    i = 0
    while i < len(lines):
        lines[i]   = lines[i].strip()

        if classify(lines[i]) == InstrType.PSEUDO:
            mnemonic, operands = parse(lines[i])
            print(mnemonic)
            lines[i:i+1] = expand(mnemonic, operands)
            i += len(expand(mnemonic, operands))
        else:
            i += 1

    return lines


def classify(line: str) -> InstrType:
    line = line.strip()

    if not line:
        return InstrType.EMPTY

    if re.match(r'^[A-Za-z_]\w*:$', line):
        return InstrType.LABEL

    if re.match(r'^\.(orig)\b', line, re.I):
        return InstrType.ORIG

    if re.match(r'^\.(word)\b', line, re.I):
        return InstrType.WORD

    if re.match(r'^\.(name)\b', line, re.I):
        return InstrType.NAME

    op_match = re.match(r'^\s*([A-Za-z]+)', line)
    print(op_match)
    if not op_match:
        return InstrType.UNKNOWN

    op = op_match.group(1).lower()
    print(op)
    if op in {"add", "sub", "and", "or", "xor", "nand", "nor", "nxor"}:
        return InstrType.ALU_R

    if op in {"addi", "subi", "andi", "ori", "xori"}:
        return InstrType.ALU_I

    if op in {"eq", "lt", "lte", "gt", "gte", "ne"}:
        return InstrType.CMP_R

    if op in {"lw"}:
        return InstrType.LOAD

    if op in {"sw"}:
        return InstrType.STORE

    if op in {"beq", "blt", "bne", "bgt", "bf", "bt"}:
        return InstrType.BRANCH

    if op in {"jal"}:
        return InstrType.JAL
    if op in {"br", "not", "ble", "bge", "call", "ret", "jump"}:
        return InstrType.PSEUDO

    return InstrType.UNKNOWN
def get_opcode_and_func(instr_type: InstrType, op: str) -> tuple[str, str | None]:
    op = op.upper()

    match instr_type:
        case InstrType.ALU_R:
            return opcode_map["ALU-R"], alu_function_map[op]
        case InstrType.ALU_I:
            return opcode_map["ALU-I"], alu_function_map[op]
        case InstrType.CMP_R:
            return opcode_map["CMP-R"], cmp_function_map[op]
        case InstrType.CMP_I:
            return opcode_map["CMP-I"], cmp_function_map[op]
        case InstrType.LOAD:
            return opcode_map["LW"], None
        case InstrType.STORE:
            return opcode_map["SW"], None
        case InstrType.BRANCH:
            return opcode_map["BRANCH"], branch_function_map[op]
        case InstrType.JAL:
            return opcode_map["JAL"], None
        case _:
            raise ValueError(f"No opcode mapping for {instr_type} / {op}")
        


def parseName(line):
    if(classify(line) == InstrType.NAME):
        parts = line.strip().split(None, 1)
        name, value = parts[1].split("=")
        name = name.strip()
        value = parseint(value.strip())
        label_table[value] = name
def parseNames(lines):
    for x in lines:
        parseName(x)


def stripAndReplaceLabels(line_to_pc: OrderedDict) -> OrderedDict:
    result = OrderedDict()
    for pc, line in line_to_pc.items():
        if classify(line) not in (InstrType.LABEL, InstrType.NAME, InstrType.ORIG):
            result[pc] = replaceLabel(line)
    return result

def replaceLabel(line: str) -> str: ## should work, temp
    instr_type = classify(line)
    mnemonic, operands = parse(line)
    ops = [o.strip() for o in operands.split(",")]

    if instr_type == InstrType.BRANCH:
        label = ops[-1]
        if label in label_table:
            ops[-1] = str(label_table[label])
        return f"{mnemonic} {','.join(ops)}"

    if instr_type == InstrType.JAL:
        imm_rs = ops[-1]
        m = re.match(r'^([A-Za-z_]\w*)\((\w+)\)$', imm_rs)
        if m and m.group(1) in label_table:
            ops[-1] = f"{label_table[m.group(1)]}({m.group(2)})"
        return f"{mnemonic} {','.join(ops)}"

    if instr_type in (InstrType.ALU_I, InstrType.CMP_I):
        label = ops[-1]
        if label in label_table:
            ops[-1] = str(label_table[label] & 0xFFFF)
        return f"{mnemonic} {','.join(ops)}"

    if instr_type in (InstrType.LOAD, InstrType.STORE):
        imm_rs = ops[-1]
        m = re.match(r'^([A-Za-z_]\w*)\((\w+)\)$', imm_rs)
        if m and m.group(1) in label_table:
            ops[-1] = f"{label_table[m.group(1)] & 0xFFFF}({m.group(2)})"
        return f"{mnemonic} {','.join(ops)}"

    if instr_type == InstrType.WORD:
        val = operands.strip()
        if val in label_table:
            return f".WORD {label_table[val]}"
        return line

    return line
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    lines = read_file_lines(input_file)
    lines = pseudo_map(lines)

    parseNames(lines)

    linesDict = build_line_pc_map(lines)
    lines = stripAndReplaceLabels(linesDict)
    print(label_table)
    

    lines = [x+"\n" for x in lines.values() ]
    write_file_lines(output_file, lines)