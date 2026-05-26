"""
test_decoder.py
---------------
Pruebas unitarias para el módulo decoder.py
Ejecutar con: python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from decoder import decode, clean_binary, validate_binary, get_register_name


# ─── Tests de validación ───────────────────────────────────────────────────────

class TestValidation:
    def test_cadena_vacia(self):
        result = decode("")
        assert result.success is False
        assert "vacía" in result.error

    def test_menos_de_32_bits(self):
        result = decode("0001")
        assert result.success is False
        assert "32" in result.error

    def test_mas_de_32_bits(self):
        result = decode("1" * 33)
        assert result.success is False

    def test_caracteres_invalidos(self):
        result = decode("0001002" + "0" * 25)
        assert result.success is False

    def test_instruccion_valida(self):
        result = decode("00000001001010100100000000100000")
        assert result.success is True


# ─── Tests de instrucciones Tipo R ────────────────────────────────────────────

class TestTipoR:
    def test_add(self):
        # ADD $t0, $t1, $t2 → 00000001001010100100000000100000
        result = decode("00000001001010100100000000100000")
        assert result.success is True
        f = result.fields
        assert f.instruction_type == "R"
        assert f.opcode == "000000"
        assert f.mnemonic == "ADD"
        assert f.rs == "01001"        # $t1
        assert f.rt == "01010"        # $t2
        assert f.rd == "01000"        # $t0

    def test_sub(self):
        # SUB $s0, $s1, $s2
        result = decode("00000010001100101000000000100010")
        assert result.success is True
        assert result.fields.mnemonic == "SUB"
        assert result.fields.instruction_type == "R"

    def test_sll(self):
        # SLL $t0, $t1, 4
        result = decode("00000000000010010100000100000000")
        assert result.success is True
        assert result.fields.mnemonic == "SLL"
        assert result.fields.shamt_dec == 4

    def test_campos_decimales_correctos(self):
        result = decode("00000001001010100100000000100000")
        f = result.fields
        assert f.opcode_dec == 0
        assert f.rs_dec == 9     # $t1
        assert f.rt_dec == 10    # $t2
        assert f.rd_dec == 8     # $t0


# ─── Tests de instrucciones Tipo I ────────────────────────────────────────────

class TestTipoI:
    def test_addi(self):
        # ADDI $t0, $zero, 10
        result = decode("00100000000010000000000000001010")
        assert result.success is True
        assert result.fields.mnemonic == "ADDI"
        assert result.fields.instruction_type == "I"

    def test_lw(self):
        result = decode("10001111101010000000000000000100")
        assert result.success is True
        assert result.fields.mnemonic == "LW"

    def test_sw(self):
        result = decode("10101111101010010000000000000000")
        assert result.success is True
        assert result.fields.mnemonic == "SW"

    def test_beq(self):
        result = decode("00010001000010010000000000000100")
        assert result.success is True
        assert result.fields.mnemonic == "BEQ"


# ─── Tests de instrucciones Tipo J ────────────────────────────────────────────

class TestTipoJ:
    def test_jump(self):
        result = decode("00001000000000000000000000000001")
        assert result.success is True
        assert result.fields.instruction_type == "J"
        assert result.fields.mnemonic == "J"

    def test_jal(self):
        result = decode("00001100000000000000000000000001")
        assert result.success is True
        assert result.fields.mnemonic == "JAL"


# ─── Tests de registros ───────────────────────────────────────────────────────

class TestRegistros:
    def test_zero(self):
        assert get_register_name("00000") == "$zero"

    def test_t0(self):
        assert get_register_name("01000") == "$t0"

    def test_sp(self):
        assert get_register_name("11101") == "$sp"

    def test_ra(self):
        assert get_register_name("11111") == "$ra"


# ─── Tests de clean_binary ────────────────────────────────────────────────────

class TestCleanBinary:
    def test_elimina_espacios(self):
        assert clean_binary("0000 0001 0010") == "000000010010"

    def test_elimina_prefijo_0b(self):
        assert clean_binary("0b101010") == "101010"

    def test_cadena_normal(self):
        assert clean_binary("001100") == "001100"