"""
main.py
-------
Punto de entrada del Decodificador de Instrucciones MIPS.
Ejecuta el modo interactivo en consola con visualización a color.

Uso:
    python main.py
    python main.py --hex 0x012A4020
    python main.py --bin 00000001001010100100000000100000
"""

import sys
import os

# Añadir carpeta src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from decoder import decode
from display import (
    print_banner,
    print_binary_segmented,
    print_fields_table,
    print_summary,
    print_legend,
    print_error,
    COLORS,
)

# ─── Ejemplos de instrucciones MIPS para demostración ─────────────────────────
EXAMPLES = [
    ("ADD  $t0, $t1, $t2",  "00000001001010100100000000100000"),
    ("SUB  $s0, $s1, $s2",  "00000010001100101000000000100010"),
    ("AND  $a0, $a1, $a2",  "00000000101001100010000000100100"),
    ("OR   $v0, $v1, $t0",  "00000000011010000001000000100101"),
    ("SLL  $t0, $t1, 4",    "00000000000010010100000100000000"),
    ("ADDI $t0, $zero, 10", "00100000000010000000000000001010"),
    ("LW   $t0, 4($sp)",    "10001111101010000000000000000100"),
    ("SW   $t1, 0($sp)",    "10101111101010010000000000000000"),
    ("BEQ  $t0, $t1, label","00010001000010010000000000000100"),
    ("J    dirección",       "00001000000000000000000000000001"),
]


def hex_to_binary(hex_str: str) -> str:
    """Convierte una cadena hexadecimal a binario de 32 bits."""
    hex_clean = hex_str.strip().lower().replace("0x", "")
    try:
        value = int(hex_clean, 16)
        return format(value, "032b")
    except ValueError:
        return ""


def print_examples_menu():
    """Muestra el menú de instrucciones de ejemplo."""
    print(f"  {COLORS['bold']}Instrucciones de ejemplo:{COLORS['reset']}")
    for i, (name, bits) in enumerate(EXAMPLES, 1):
        print(f"  {COLORS['dim']}{i:>2}.{COLORS['reset']}  "
              f"{COLORS['bold']}{name:<22}{COLORS['reset']}  "
              f"{COLORS['dim']}{bits}{COLORS['reset']}")
    print()


def run_decode(binary: str):
    """Ejecuta la decodificación y muestra todos los resultados visuales."""
    result = decode(binary)

    if not result.success:
        print_error(result.error)
        return

    f = result.fields
    print_binary_segmented(f)
    print_fields_table(f)
    print_summary(f)
    print_legend()


def interactive_mode():
    """Modo interactivo principal."""
    print_banner()

    while True:
        print(f"  {COLORS['bold']}Opciones:{COLORS['reset']}")
        print("   [1] Ingresar instrucción binaria (32 bits)")
        print("   [2] Ingresar instrucción hexadecimal")
        print("   [3] Ver ejemplos de instrucciones MIPS")
        print("   [4] Ejecutar todos los ejemplos")
        print("   [0] Salir")
        print()

        choice = input("  → Selecciona una opción: ").strip()

        if choice == "0":
            print(f"\n  {COLORS['dim']}¡Hasta luego!{COLORS['reset']}\n")
            break

        elif choice == "1":
            binary = input("  → Ingresa la instrucción (32 bits, espacios opcionales): ").strip()
            print()
            run_decode(binary)

        elif choice == "2":
            hex_input = input("  → Ingresa en hexadecimal (ej: 0x012A4020): ").strip()
            binary = hex_to_binary(hex_input)
            if not binary:
                print_error("Valor hexadecimal inválido.")
            else:
                print(f"  {COLORS['dim']}Binario equivalente: {binary}{COLORS['reset']}\n")
                run_decode(binary)

        elif choice == "3":
            print()
            print_examples_menu()
            choice2 = input("  → Elige un ejemplo (1-10) o Enter para volver: ").strip()
            if choice2.isdigit() and 1 <= int(choice2) <= len(EXAMPLES):
                name, bits = EXAMPLES[int(choice2) - 1]
                print(f"\n  {COLORS['bold']}Decodificando: {name}{COLORS['reset']}\n")
                run_decode(bits)
            print()

        elif choice == "4":
            for name, bits in EXAMPLES:
                sep = "═" * 60
                print(f"\n  {COLORS['bold']}{sep}{COLORS['reset']}")
                print(f"  {COLORS['bold']}  Instrucción: {name}{COLORS['reset']}\n")
                run_decode(bits)
            print()

        else:
            print_error("Opción no válida. Elige entre 0 y 4.")

        input(f"  {COLORS['dim']}Presiona Enter para continuar...{COLORS['reset']}")
        print("\033[2J\033[H", end="")  # Limpiar pantalla
        print_banner()


def cli_mode():
    """Modo de línea de comandos (flags --bin o --hex)."""
    print_banner()
    args = sys.argv[1:]

    if "--bin" in args:
        idx = args.index("--bin")
        binary = args[idx + 1] if idx + 1 < len(args) else ""
        run_decode(binary)

    elif "--hex" in args:
        idx = args.index("--hex")
        hex_val = args[idx + 1] if idx + 1 < len(args) else ""
        binary = hex_to_binary(hex_val)
        if not binary:
            print_error("Valor hexadecimal inválido.")
        else:
            print(f"  {COLORS['dim']}Binario equivalente: {binary}{COLORS['reset']}\n")
            run_decode(binary)

    else:
        print_error("Uso: python main.py --bin <32bits>  o  --hex <0xVALOR>")


# ─── Punto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_mode()
    else:
        interactive_mode()