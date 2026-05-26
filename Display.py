"""
display.py
----------
Módulo de visualización: imprime la decodificación en la consola
con colores y formato legible usando la librería estándar (sin dependencias externas).
"""

from decoder import InstructionFields, get_register_name

# Códigos ANSI para colores en terminal
COLORS = {
    "opcode": "\033[38;5;196m",   # Rojo
    "rs":     "\033[38;5;214m",   # Naranja
    "rt":     "\033[38;5;226m",   # Amarillo
    "rd":     "\033[38;5;118m",   # Verde
    "shamt":  "\033[38;5;51m",    # Cyan
    "funct":  "\033[38;5;171m",   # Violeta
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "white":  "\033[97m",
    "bg_dark":"\033[48;5;235m",
}

FIELD_ORDER = ["opcode", "rs", "rt", "rd", "shamt", "funct"]

FIELD_LABELS = {
    "opcode": "OPCODE",
    "rs":     "RS    ",
    "rt":     "RT    ",
    "rd":     "RD    ",
    "shamt":  "SHAMT ",
    "funct":  "FUNCT ",
}

FIELD_BITS = {
    "opcode": "[31:26]",
    "rs":     "[25:21]",
    "rt":     "[20:16]",
    "rd":     "[15:11]",
    "shamt":  "[10:6] ",
    "funct":  "[5:0]  ",
}

FIELD_DESC = {
    "opcode": "Código de operación",
    "rs":     "Registro fuente 1",
    "rt":     "Registro fuente 2 / destino (Tipo I)",
    "rd":     "Registro destino (Tipo R)",
    "shamt":  "Cantidad de desplazamiento (shift amount)",
    "funct":  "Código de función (Tipo R)",
}


def _color(field: str, text: str) -> str:
    """Aplica color ANSI a un texto según el campo."""
    return f"{COLORS[field]}{text}{COLORS['reset']}"


def _bold(text: str) -> str:
    return f"{COLORS['bold']}{text}{COLORS['reset']}"


def print_banner():
    """Imprime el encabezado de la aplicación."""
    print()
    print(_bold("  ╔══════════════════════════════════════════════════════╗"))
    print(_bold("  ║     DECODIFICADOR DE INSTRUCCIONES MIPS 32-bit      ║"))
    print(_bold("  ║          Arquitectura de Computadores                ║"))
    print(_bold("  ╚══════════════════════════════════════════════════════╝"))
    print()


def print_binary_segmented(fields: InstructionFields):
    """
    Muestra la instrucción binaria completa con cada campo coloreado y
    separado visualmente.
    """
    raw = fields.raw_binary
    segments = {
        "opcode": raw[0:6],
        "rs":     raw[6:11],
        "rt":     raw[11:16],
        "rd":     raw[16:21],
        "shamt":  raw[21:26],
        "funct":  raw[26:32],
    }

    print("  ┌─ Instrucción binaria segmentada ─────────────────────────┐")
    print("  │                                                          │")

    # Línea de bits coloreados
    bit_line = "  │  "
    for field in FIELD_ORDER:
        bit_line += _color(field, segments[field]) + " "
    print(bit_line)

    # Línea de etiquetas centradas
    label_line = "  │  "
    widths = [6, 5, 5, 5, 5, 6]
    for field, width in zip(FIELD_ORDER, widths):
        label = field.upper().center(width)
        label_line += _color(field, label) + " "
    print(label_line)

    # Línea de posición de bits
    pos_line = "  │  "
    positions = ["31:26", "25:21", "20:16", "15:11", "10:6 ", "5:0  "]
    for field, pos in zip(FIELD_ORDER, positions):
        pos_str = pos.center(len(widths[FIELD_ORDER.index(field)] * " "))
        pos_line += f"{COLORS['dim']}{pos}{COLORS['reset']} "
    print(pos_line)

    print("  │                                                          │")
    print("  └──────────────────────────────────────────────────────────┘")
    print()


def print_fields_table(fields: InstructionFields):
    """Imprime la tabla detallada de cada campo."""
    raw = fields.raw_binary
    values_bin = {
        "opcode": fields.opcode,
        "rs":     fields.rs,
        "rt":     fields.rt,
        "rd":     fields.rd,
        "shamt":  fields.shamt,
        "funct":  fields.funct,
    }
    values_dec = {
        "opcode": fields.opcode_dec,
        "rs":     fields.rs_dec,
        "rt":     fields.rt_dec,
        "rd":     fields.rd_dec,
        "shamt":  fields.shamt_dec,
        "funct":  fields.funct_dec,
    }

    print("  ┌──────────────────────────────────────────────────────────────────────┐")
    print("  │  Campo   │  Bits   │  Binario  │  Dec  │  Hex   │  Valor / Nombre   │")
    print("  ├──────────────────────────────────────────────────────────────────────┤")

    for field in FIELD_ORDER:
        bits_bin = values_bin[field]
        bits_dec = values_dec[field]
        bits_hex = hex(bits_dec).upper().replace("X", "x")

        # Resolver nombre del campo
        if field in ("rs", "rt", "rd"):
            name = get_register_name(bits_bin)
        elif field == "opcode":
            name = fields.mnemonic if fields.instruction_type != "R" else "→ ver funct"
        elif field == "funct" and fields.instruction_type == "R":
            name = fields.mnemonic
        else:
            name = "-"

        label   = _color(field, FIELD_LABELS[field])
        bin_col = _color(field, bits_bin)
        dec_col = str(bits_dec).rjust(5)
        hex_col = bits_hex.rjust(6)
        name_col = _color(field, name)
        bits_pos = FIELD_BITS[field]

        print(f"  │  {label} │ {bits_pos} │  {bin_col}  │ {dec_col} │ {hex_col} │  {name_col:<30}{COLORS['reset']}│")

    print("  └──────────────────────────────────────────────────────────────────────┘")
    print()


def print_summary(fields: InstructionFields):
    """Imprime el resumen de la instrucción decodificada."""
    type_colors = {"R": "\033[38;5;118m", "I": "\033[38;5;226m", "J": "\033[38;5;214m"}
    t_color = type_colors.get(fields.instruction_type, "")

    print("  ┌─ Resumen ────────────────────────────────────┐")
    print(f"  │  Instrucción : {_bold(fields.mnemonic):<36}│")
    print(f"  │  Tipo        : {t_color}{_bold('Tipo ' + fields.instruction_type)}{COLORS['reset']:<36}│")

    if fields.instruction_type == "R":
        rd_name = get_register_name(fields.rd)
        rs_name = get_register_name(fields.rs)
        rt_name = get_register_name(fields.rt)
        asm = f"{fields.mnemonic} {rd_name}, {rs_name}, {rt_name}"
        print(f"  │  Ensamblador : {_bold(asm):<36}│")
    elif fields.instruction_type == "I":
        rt_name = get_register_name(fields.rt)
        rs_name = get_register_name(fields.rs)
        asm = f"{fields.mnemonic} {rt_name}, {rs_name}, {fields.funct_dec}"
        print(f"  │  Ensamblador : {_bold(asm):<36}│")

    print("  └──────────────────────────────────────────────┘")
    print()


def print_legend():
    """Imprime la leyenda de colores."""
    print("  " + _bold("Leyenda de colores:"))
    for field in FIELD_ORDER:
        desc = FIELD_DESC[field]
        print(f"  {_color(field, '■')} {_color(field, field.upper())} → {desc}")
    print()


def print_error(message: str):
    """Imprime un mensaje de error formateado."""
    print()
    print(f"  \033[38;5;196m✗ Error:\033[0m {message}")
    print()