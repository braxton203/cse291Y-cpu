import sys
import re
from enum import Enum, auto
from collections import OrderedDict
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
    EMPTY = auto()
    UNKNOWN = auto()
label_table = {}
def read_file_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.readlines()

def write_file_lines(filepath, lines):
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)


def parseOrig(line):
    parts = line.strip().split()

    value = parts[1]

    if value.lower().startswith("0x"):
        return int(value, 16)
    else:
        return int(value)

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

        line_to_pc[pc] = line

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
            pc += 4

    return line_to_pc


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

    if op in {"beq", "blt", "bne", "bgt", "bge", "bf", "bt"}:
        return InstrType.BRANCH

    if op in {"jal"}:
        return InstrType.JAL

    return InstrType.UNKNOWN


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    lines = read_file_lines(input_file)

    print(build_line_pc_map(lines).keys())
    print(label_table)
    
    write_file_lines(output_file, lines)