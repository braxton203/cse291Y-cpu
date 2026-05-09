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
    "XNOR":  "1110",
    "XNORI": "1110",
    "MVHI":  "1011",
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
    oprtr = parts[0].upper()
    print(oprtr)
    operands = parts[1].strip().replace(' ', '') if len(parts) > 1 else ""
    return oprtr, operands

def expand(oprtr: str, operands: str) -> list[str]:

    if oprtr == "BR":
        return [f"BEQ R6,R6,{operands}"]

    if oprtr == "NOT":
        rd, rs = operands.split(",")
        return [f"NAND {rd},{rs},{rs}"]

    if oprtr == "BLE":
        rs1, rs2, imm = operands.split(",")
        return [f"LTE R6,{rs1},{rs2}", f"BNEZ R6,{imm}"]

    if oprtr == "BGE":
        rs1, rs2, imm = operands.split(",")
        return [f"GTE R6,{rs1},{rs2}", f"BNEZ R6,{imm}"]

    if oprtr == "CALL":
        m = re.match(r'(.+)\((.+)\)', operands)
        imm, rs1 = m.group(1), m.group(2)
        return [f"JAL RA,{imm}({rs1})"]

    if oprtr == "RET":
        return ["JAL R9,0(RA)"]

    if oprtr == "JMP":
        m = re.match(r'(.+)\((.+)\)', operands)
        imm, rs1 = m.group(1), m.group(2)
        return [f"JAL R9,{imm}({rs1})"]

def pseudo_map(lines):
    i = 0
    while i < len(lines):
        lines[i]   = lines[i].strip()
        if classify(lines[i]) == InstrType.PSEUDO:
            oprtr, operands = parse(lines[i])
            lines[i:i+1] = expand(oprtr, operands)
            print(lines[i:i+1])
            i += len(expand(oprtr, operands))
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
    if not op_match:
        return InstrType.UNKNOWN
    op = op_match.group(1).lower()
    if op in {"add", "sub", "and", "or", "xor", "nand", "nor", "xnor"}:
        return InstrType.ALU_R
    if op in {"addi", "subi", "andi", "ori", "xori", "nandi", "nori", "xnori", "mvhi"}:
        return InstrType.ALU_I
    if op in {"f", "eq", "lt", "lte", "t", "ne", "gte", "gt"}:
        return InstrType.CMP_R
    if op in {"fi", "eqi", "lti", "ltei", "ti", "nei", "gtei", "gti"}:
        return InstrType.CMP_I
    if op in {"lw"}:
        return InstrType.LOAD
    if op in {"sw"}:
        return InstrType.STORE
    if op in {"bf", "beq", "blt", "blte", "beqz", "bltz", "bltez",
              "bt", "bne", "bgte", "bgt", "bnez", "bgtez", "bgtz"}:
        return InstrType.BRANCH
    if op in {"jal"}:
        return InstrType.JAL
    if op in {"br", "not", "ble", "bge", "call", "ret", "jmp"}:
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
            return opcode_map["LW"], '0000'
        case InstrType.STORE:
            return opcode_map["SW"], '0000'
        case InstrType.BRANCH:
            return opcode_map["BRANCH"], branch_function_map[op]
        case InstrType.JAL:
            return opcode_map["JAL"], '0000'
        case _:
            raise ValueError(f"No opcode mapping for {instr_type} / {op}")
        


def parseName(line):
    if(classify(line) == InstrType.NAME):
        parts = line.strip().split(None, 1)
        name, value = parts[1].split("=")
        name = name.strip()
        value = parseint(value.strip())
        label_table[name] = value
def parseNames(lines):
    for x in lines:
        parseName(x)


def stripAndReplaceLabels(line_to_pc: OrderedDict) -> OrderedDict:
    result = OrderedDict()
    for pc, line in line_to_pc.items():
        if classify(line) not in (InstrType.LABEL, InstrType.NAME, InstrType.ORIG):
            result[pc] = replaceLabel(line)
    return result

def parse_reg(reg: str) -> str:
    named = {
        "RA": 15,
        "SP": 14,
        "FP": 13,
        "GP": 12,
        "RV": 3,
    }
    reg = reg.upper()
    if reg in named:
        return f"{named[reg]:04b}"
    return f"{int(''.join(c for c in reg if c.isdigit())):04b}"
def parse_imm(imm: str) -> str:
    return f"{int(imm) & 0xFFFF:016b}"
def parse_imm_reg(operand: str) -> tuple[str, str]:
    imm, reg = operand[:-1].split("(")
    return parse_imm(imm), parse_reg(reg)
def getmem(line):
    instr_type = classify(line)
    op = line.split(' ')[0]
    print(op)
    opc, function = get_opcode_and_func(instr_type, op)
    operands = parse(line)[1].split(",")
    print(operands)
    match instr_type:
        case InstrType.ALU_R:
            opn1 = parse_reg(operands[0])
            opn2 = parse_reg(operands[1])
            opn3 = parse_reg(operands[2])
            return opn1, opn2, opn3, '0000' * 3,  function, opc
        case InstrType.ALU_I:
            if(op.upper() == 'MVHI'):
               opn1 = parse_reg(operands[0])
               opn2 = '0000'
            else:
                opn1 = parse_reg(operands[0])
                opn2 = parse_reg(operands[1])
            imm = parse_imm(operands[2])
            return opn1, opn2, imm, function, opc
        case InstrType.CMP_R:
            opn1 = parse_reg(operands[0])
            opn2 = parse_reg(operands[1])
            opn3 = parse_reg(operands[2])
            return opn1, opn2, opn3, '0000' * 3,  function, opc
        case InstrType.CMP_I:

            opn1 = parse_reg(operands[0])
            opn2 = parse_reg(operands[1])
            imm = parse_imm(operands[2])
            return opn1, opn2, imm,  function , opc
        case InstrType.LOAD:
            opn1 = parse_reg(operands[0])
            opn3, opn2 = parse_imm_reg(operands[1])
            return opn1, opn2, opn3, function,  opc
        case InstrType.STORE:
            opn1 = parse_reg(operands[0])
            opn3, opn2 = parse_imm_reg(operands[1])
            return opn1, opn2, opn3, function,  opc
        case InstrType.BRANCH:
            if(op.upper() in ["BF", "BEQ", "BLT", "BLTE", "BT", "BNE", "BGTE", "BGT"]):
                opn1 = parse_reg(operands[0])
                opn2 = parse_reg(operands[1])
                imm = parse_imm(operands[2])
            else:
                opn1 = parse_reg(operands[0])
                opn2 = '0000'
                imm = parse_imm(operands[1])
            return opn1, opn2, imm, function, opc
        case InstrType.JAL:
            print(operands)
            opn1 = parse_reg(operands[0])
            opn3, opn2 = parse_imm_reg(operands[1])
            return opn1, opn2, opn3, function, opc
        case _:
            raise ValueError("no map")

def linetomems(lines_dict):
    for x in lines_dict.keys():
        if(classify(lines_dict[x]) != InstrType.WORD):
            lines_dict[x] = [lines_dict[x]] + [getmem(lines_dict[x])]
        else:
            lines_dict[x] = [lines_dict[x]] + [lines_dict[x].split(' ')[1]]
    return lines_dict
def replaceLabel(line: str) -> str: ## should work, temp
    oprtr, operands = parse(line)  
    operands = operands 
    line = f"{oprtr} {operands}" 
    instr_type = classify(line)
    ops = [o.strip() for o in operands.split(",")]

    if instr_type == InstrType.BRANCH:
        label = ops[-1]
        print(line)
        if label in label_table:
            ops[-1] = str(label_table[label])
        else:
            print("bad label")
        return f"{oprtr} {','.join(ops)}"

    if instr_type == InstrType.JAL:
        imm_rs = ops[-1]
        m = re.match(r'^([A-Za-z_]\w*)\((\w+)\)$', imm_rs)
        if m and m.group(1) in label_table:
            ops[-1] = f"{label_table[m.group(1)]}({m.group(2)})"
        return f"{oprtr} {','.join(ops)}"

    if instr_type in (InstrType.ALU_I, InstrType.CMP_I):
        label = ops[-1]
        if label in label_table:
            ops[-1] = str(label_table[label])
        return f"{oprtr} {','.join(ops)}"

    if instr_type in (InstrType.LOAD, InstrType.STORE):
        imm_rs = ops[-1]
        m = re.match(r'^([A-Za-z_]\w*)\((\w+)\)$', imm_rs)
        if m and m.group(1) in label_table:
            ops[-1] = f"{label_table[m.group(1)]}({m.group(2)})"
        return f"{oprtr} {','.join(ops)}"

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
    print(lines)
    linesDict = build_line_pc_map(lines)
    print(label_table)
    linesDict = stripAndReplaceLabels(linesDict)

    linesDict = linetomems(linesDict)
    print(linesDict)
    lines = [x[0]+"\n" for x in linesDict.values() ]
    write_file_lines(output_file, lines)