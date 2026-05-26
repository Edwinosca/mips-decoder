"""
decoder.py
----------
Módulo principal para decodificar instrucciones MIPS de 32 bits.
Soporta instrucciones tipo R, tipo I y tipo J.
"""

from dataclasses import dataclass
from typing import Optional


# ─── Tablas de referencia MIPS ────────────────────────────────────────────────

OPCODES: dict[str, str] = {
    "000000": "Tipo-R (ver funct)",
    "001000": "ADDI",
    "001001": "ADDIU",
    "001100": "ANDI",
    "000100": "BEQ",
    "000101": "BNE",
    "001111": "LUI",
    "100011": "LW",
    "001101": "ORI",
    "001010": "SLTI",
    "101011": "SW",
    "000010": "J",
    "000011": "JAL",
}

FUNCT_CODES: dict[str, str] = {
    "100000": "ADD",
    "100001": "ADDU",
    "100100": "AND",
    "001000": "JR",
    "100111": "NOR",
    "100101": "OR",
    "101010": "SLT",
    "000000": "SLL",
    "000010": "SRL",
    "100010": "SUB",
    "100011": "SUBU",
}

REGISTERS: dict[str, str] = {
    "00000": "$zero", "00001": "$at",  "00010": "$v0",  "00011": "$v1",
    "00100": "$a0",   "00101": "$a1",  "00110": "$a2",  "00111": "$a3",
    "01000": "$t0",   "01001": "$t1",  "01010": "$t2",  "01011": "$t3",
    "01100": "$t4",   "01101": "$t5",  "01110": "$t6",  "01111": "$t7",
    "10000": "$s0",   "10001": "$s1",  "10010": "$s2",  "10011": "$s3",
    "10100": "$s4",   "10101": "$s5",  "10110": "$s6",  "10111": "$s7",
    "11000": "$t8",   "11001": "$t9",  "11010": "$k0",  "11011": "$k1",
    "11100": "$gp",   "11101": "$sp",  "11110": "$fp",  "11111": "$ra",
}


# ─── Estructuras de datos ──────────────────────────────────────────────────────

@dataclass
class InstructionFields:
    """Campos extraídos de una instrucción MIPS de 32 bits."""
    raw_binary: str
    opcode:     str          # bits [31:26]
    rs:         str          # bits [25:21]
    rt:         str          # bits [20:16]
    rd:         str          # bits [15:11]
    shamt:      str          # bits [10:6]
    funct:      str          # bits [5:0]
    instruction_type: str    # "R", "I" o "J"
    mnemonic:   str          # nombre de la instrucción
    opcode_dec: int
    rs_dec:     int
    rt_dec:     int
    rd_dec:     int
    shamt_dec:  int
    funct_dec:  int


@dataclass
class DecoderResult:
    """Resultado completo de la decodificación."""
    success:    bool
    fields:     Optional[InstructionFields]
    error:      Optional[str]


# ─── Lógica de decodificación ──────────────────────────────────────────────────

def clean_binary(raw: str) -> str:
    """Elimina espacios y prefijos '0b' de la cadena binaria."""
    return raw.strip().replace(" ", "").replace("0b", "").replace("0B", "")


def validate_binary(binary: str) -> Optional[str]:
    """
    Valida que la cadena sea una instrucción binaria MIPS válida de 32 bits.
    Retorna un mensaje de error o None si es válida.
    """
    if not binary:
        return "La instrucción no puede estar vacía."
    if not all(c in "01" for c in binary):
        return f"La instrucción contiene caracteres inválidos. Solo se permiten '0' y '1'."
    if len(binary) != 32:
        return f"La instrucción debe tener exactamente 32 bits. Se recibieron {len(binary)}."
    return None


def determine_instruction_type(opcode: str) -> str:
    """Determina el tipo de instrucción (R, I o J) según el opcode."""
    if opcode == "000000":
        return "R"
    if opcode in ("000010", "000011"):
        return "J"
    return "I"


def decode(binary_str: str) -> DecoderResult:
    """
    Decodifica una instrucción MIPS de 32 bits.

    Args:
        binary_str: Cadena de 32 bits (se aceptan espacios).

    Returns:
        DecoderResult con los campos decodificados o un mensaje de error.
    """
    cleaned = clean_binary(binary_str)

    error = validate_binary(cleaned)
    if error:
        return DecoderResult(success=False, fields=None, error=error)

    # Extraer campos bit a bit según el formato MIPS
    opcode = cleaned[0:6]
    rs     = cleaned[6:11]
    rt     = cleaned[11:16]
    rd     = cleaned[16:21]
    shamt  = cleaned[21:26]
    funct  = cleaned[26:32]

    instruction_type = determine_instruction_type(opcode)

    # Resolver el mnemónico
    if instruction_type == "R":
        mnemonic = FUNCT_CODES.get(funct, f"FUNCT desconocido ({funct})")
    else:
        mnemonic = OPCODES.get(opcode, f"OPCODE desconocido ({opcode})")

    fields = InstructionFields(
        raw_binary       = cleaned,
        opcode           = opcode,
        rs               = rs,
        rt               = rt,
        rd               = rd,
        shamt            = shamt,
        funct            = funct,
        instruction_type = instruction_type,
        mnemonic         = mnemonic,
        opcode_dec       = int(opcode, 2),
        rs_dec           = int(rs, 2),
        rt_dec           = int(rt, 2),
        rd_dec           = int(rd, 2),
        shamt_dec        = int(shamt, 2),
        funct_dec        = int(funct, 2),
    )

    return DecoderResult(success=True, fields=fields, error=None)


def get_register_name(binary_5bits: str) -> str:
    """Retorna el nombre del registro MIPS dado su representación en 5 bits."""
    return REGISTERS.get(binary_5bits, "?")