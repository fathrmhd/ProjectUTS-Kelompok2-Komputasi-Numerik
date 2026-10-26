from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Callable, List, Optional

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

# --------------------------------------------------------------------------
# Konstanta batas input
# --------------------------------------------------------------------------
MAX_ITERATIONS = 100   # iterasi maksimum yang boleh diinput
MAX_DECIMALS = 6       # jumlah angka desimal maksimum yang boleh diinput


class InputError(ValueError):
    """Dilempar bila input pengguna / evaluasi fungsi tidak valid."""


# ==========================================================================
# 1. PARSER FUNGSI
# ==========================================================================
_X = sp.Symbol("x")

# Karakter yang diizinkan dalam teks fungsi
_ALLOWED_CHARS = re.compile(r"^[0-9a-z+\-*/^().,\s]+$")

# Namespace terbatas untuk parse_expr
_GLOBALS = {
    "__builtins__": {},
    "Integer": sp.Integer, "Float": sp.Float, "Rational": sp.Rational,
    "Symbol": sp.Symbol, "Function": sp.Function,
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "ln": sp.log,
    "log10": lambda v: sp.log(v, 10),
    "sqrt": sp.sqrt, "abs": sp.Abs,
}
_LOCALS = {"x": _X, "e": sp.E, "pi": sp.pi}

_TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)

_SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_TO_SUP = str.maketrans("0123456789-", _SUP_DIGITS + "⁻")
_FROM_SUP = str.maketrans(_SUP_DIGITS + "⁻", "0123456789-")
_SUP_RUN = f"⁻?[{_SUP_DIGITS}]+"
_FRACTION_AHEAD = r"[.,](?:\d|$)"


def superscript_exponents(text: str) -> str:
    """
    Ubah pangkat bilangan bulat menjadi superscript:
        "x**2 - 5x + 4" -> "x² - 5x + 4"
    """
    text = re.sub(rf"({_SUP_RUN})(?={_FRACTION_AHEAD})",
                  lambda m: "**" + m.group(1).translate(_FROM_SUP), text)
    text = re.sub(rf"({_SUP_RUN})(\d+)(?!\d)(?!{_FRACTION_AHEAD})",
                  lambda m: (m.group(1) + m.group(2)).translate(_TO_SUP), text)
    text = re.sub(rf"\s*(?:\*\*|\^)\s*(-?\d+)(?!\d)(?!{_FRACTION_AHEAD})",
                  lambda m: m.group(1).translate(_TO_SUP), text)
    return text


def _superscripts_to_python(text: str) -> str:
    """Kebalikannya untuk parser: 'x²' -> 'x**2'."""
    def repl(m):
        digits = m.group(0).translate(_FROM_SUP)
        return f"**({digits})" if digits.startswith("-") else f"**{digits}"
    return re.sub(_SUP_RUN, repl, text)


def _normalize_function_text(text: str) -> str:
    """Rapikan teks fungsi: huruf kecil, simbol unicode, koma desimal."""
    s = text.strip().lower()
    s = _superscripts_to_python(s)
    for old, new in {"−": "-", "–": "-", "×": "*", "÷": "/"}.items():
        s = s.replace(old, new)
    s = re.sub(r"(?<=\d),(?=\d)", ".", s)
    return s


@dataclass
class ParsedFunction:
    """Hasil parsing fungsi: ekspresi SymPy + fungsi skalar + fungsi vektor."""
    expr: sp.Expr
    scalar: Callable[[float], float]
    vector: Callable[[np.ndarray], np.ndarray]
    display: str


def parse_function(text: str, label: str = "Fungsi") -> ParsedFunction:
    """Ubah teks matematika menjadi objek ParsedFunction."""
    if not text or not text.strip():
        raise InputError(f"{label} belum diisi.")

    s = _normalize_function_text(text)
    hint = f"Contoh penulisan {label}: x**2 - 6x - 2  atau  sqrt(6x + 2)"
    if not _ALLOWED_CHARS.match(s):
        raise InputError(f"{label} mengandung karakter yang tidak diizinkan.\n{hint}")

    try:
        expr = parse_expr(s, local_dict=dict(_LOCALS), global_dict=dict(_GLOBALS),
                          transformations=_TRANSFORMS)
    except Exception:
        raise InputError(f"Penulisan {label} tidak valid.\n{hint}")

    if not isinstance(expr, sp.Expr):
        raise InputError(f"{label} tidak valid.\n{hint}")
    if not expr.free_symbols <= {_X}:
        raise InputError(f"{label} hanya boleh memakai variabel x.\n{hint}")

    raw_scalar = sp.lambdify(_X, expr, modules="math")
    raw_vector = sp.lambdify(_X, expr, modules="numpy")

    def scalar(x: float) -> float:
        try:
            val = float(raw_scalar(x))
        except (ValueError, ZeroDivisionError, OverflowError, TypeError) as exc:
            raise InputError(f"{label} tidak terdefinisi di x = {x:g} ({exc}).")
        if not math.isfinite(val):
            raise InputError(f"{label} bernilai tak hingga / tidak terdefinisi di x = {x:g}.")
        return val

    def vector(xs: np.ndarray) -> np.ndarray:
        with np.errstate(all="ignore"):
            try:
                ys = np.asarray(raw_vector(xs), dtype=float)
                if ys.ndim == 0:
                    ys = np.full_like(xs, float(ys), dtype=float)
            except Exception:
                ys = np.full_like(xs, np.nan, dtype=float)
                for i, xv in enumerate(xs):
                    try:
                        ys[i] = scalar(float(xv))
                    except Exception:
                        pass
        ys[~np.isfinite(ys)] = np.nan
        return ys

    display = superscript_exponents(text.strip())
    return ParsedFunction(expr, scalar, vector, display)


# ==========================================================================
# 2. VALIDASI INPUT & PENURUNAN g(x)
# ==========================================================================
def derive_g_methods(f_text: str) -> Optional[dict[str, str]]:
    """
    Turunkan 3 cara mencari g(x) dari f(x) = 0 untuk persamaan kuadrat ax^2 + bx + c = 0
    sesuai dengan materi (Slide 5 & 7):
      - Cara 1 : Isolasi x^2      -> x = sqrt((-bx - c)/a)
      - Cara 2 : Isolasi x        -> x = (-ax^2 - c)/b
      - Cara 3 : Faktorisasi x    -> x = -c / (ax + b)
    Mengembalikan dict {"cara1": ..., "cara2": ..., "cara3": ...} bila polinomial berderajat 2.
    """
    try:
        pf = parse_function(f_text, "Fungsi F(X)")
    except Exception:
        return None

    try:
        poly = sp.Poly(pf.expr, _X)
    except Exception:
        return None

    if poly.degree() != 2:
        return None

    coeffs = poly.all_coeffs()
    if len(coeffs) != 3:
        return None

    a, b, c = coeffs
    if a == 0 or b == 0:
        return None

    # Cara 1: ax^2 + bx + c = 0 => x^2 = (-bx - c)/a => x = sqrt(...)
    inner1 = sp.simplify((-b * _X - c) / a)
    str1 = f"sqrt({inner1})"

    # Cara 2: bx = -ax^2 - c => x = (-ax^2 - c)/b
    num_parts = []
    if -a == 1:
        num_parts.append("x**2")
    elif -a == -1:
        num_parts.append("-x**2")
    else:
        num_parts.append(f"{-a}*x**2")

    if -c > 0:
        num_parts.append(f"+ {-c}")
    elif -c < 0:
        num_parts.append(f"- {c}")
    num_str = " ".join(num_parts) if len(num_parts) > 1 else num_parts[0]
    str2 = f"({num_str}) / ({b})" if b < 0 else f"({num_str}) / {b}"

    # Cara 3: x(ax + b) = -c => x = -c / (ax + b)
    num3 = -c
    den_parts = []
    if a == 1:
        den_parts.append("x")
    elif a == -1:
        den_parts.append("-x")
    else:
        den_parts.append(f"{a}*x")

    if b > 0:
        den_parts.append(f"+ {b}")
    elif b < 0:
        den_parts.append(f"- {-b}")
    den_str = " ".join(den_parts)
    str3 = f"{num3} / ({den_str})"

    return {
        "cara1": str1,
        "cara2": str2,
        "cara3": str3,
    }


def parse_number(text: str, label: str) -> float:
    t = (text or "").strip().replace(",", ".")
    if not t:
        raise InputError(f"{label} belum diisi.")
    try:
        val = float(t)
    except ValueError:
        raise InputError(f"{label} harus berupa angka.")
    if not math.isfinite(val):
        raise InputError(f"{label} harus berupa angka yang valid.")
    return val


def parse_integer(text: str, label: str) -> int:
    val = parse_number(text, label)
    if val != int(val):
        raise InputError(f"{label} harus berupa bilangan bulat.")
    return int(val)


@dataclass
class SolverInputs:
    """Semua input yang sudah tervalidasi untuk Metode Iterasi."""
    f_func: ParsedFunction
    g_func: ParsedFunction
    x0: float
    eps: float
    n_max: int
    decimals: int


def parse_inputs(
    f_text: str,
    g_text: str,
    x0_text: str,
    eps_text: str,
    n_text: str,
    decimals_text: str,
) -> SolverInputs:
    """Validasi seluruh isian form; lempar InputError bila ada yang tidak sesuai."""
    if not g_text or not g_text.strip():
        raise InputError("Fungsi g(x) belum diisi.")

    g_func = parse_function(g_text, "Fungsi g(x)")

    # Bila F(x) diisi gunakan F(x), bila kosong otomatis turunkan F(x) = x - g(x)
    if f_text and f_text.strip():
        f_func = parse_function(f_text, "Fungsi F(X)")
    else:
        norm_g = _normalize_function_text(g_text)
        f_func = parse_function(f"x - ({norm_g})", "Fungsi F(X)")

    x0_val = parse_number(x0_text, "Pendekatan Awal (x₀)")
    eps_val = parse_number(eps_text, "Toleransi Error (e)")
    n_val = parse_integer(n_text, "Iterasi Maksimum (N)")
    dec_val = parse_integer(decimals_text, "Jumlah Angka Desimal")

    if eps_val <= 0:
        raise InputError("Toleransi Error (e) harus lebih besar dari 0.")
    if not 1 <= n_val <= MAX_ITERATIONS:
        raise InputError(f"Iterasi Maksimum (N) harus antara 1 dan {MAX_ITERATIONS}.")
    if not 1 <= dec_val <= MAX_DECIMALS:
        raise InputError(f"Jumlah Angka Desimal harus antara 1 dan {MAX_DECIMALS}.")

    return SolverInputs(f_func, g_func, x0_val, eps_val, n_val, dec_val)


# ==========================================================================
# 3. ALGORITMA METODE ITERASI (TITIK TETAP)
# ==========================================================================
@dataclass
class IterationRow:
    r: int
    x: float
    gx: float
    fx: float
    e_tol: float
    valid: bool
    error_msg: Optional[str] = None


@dataclass
class IterationResult:
    inputs: SolverInputs
    rows: List[IterationRow]
    first_true: Optional[int]
    root: float
    f_root: float
    root_iteration: int
    converged: bool
    exact_root: bool
    diverged: bool = False
    stop_reason: Optional[str] = None

    @property
    def solution_index(self) -> int:
        return self.first_true if self.first_true is not None else len(self.rows) - 1


def solve(inputs: SolverInputs) -> IterationResult:
    """
    Jalankan Metode Iterasi (Iterasi Titik Tetap).

    Algoritma :
      1. x_i = g(x_{i-1})
      2. e_tol = |g(x_i) - x_i|
      3. Validasi = TRUE jika e_tol < e (atau f(x) = 0).
      4. Jika tidak konvergen sampai N, nilai pendekatan adalah x iterasi terakhir.
    """
    f = inputs.f_func.scalar
    g = inputs.g_func.scalar
    eps = inputs.eps
    n_max = inputs.n_max

    x = inputs.x0
    rows: List[IterationRow] = []
    first_true: Optional[int] = None
    exact = False
    diverged = False
    stop_reason: Optional[str] = None

    for r in range(1, n_max + 1):
        # Evaluasi f(x)
        try:
            fx = f(x)
        except Exception:
            fx = float("nan")

        # Evaluasi g(x)
        try:
            gx = g(x)
        except Exception as exc:
            diverged = True
            stop_reason = f"g(x) tidak terdefinisi di x = {x:g} ({exc})"
            rows.append(IterationRow(r, x, float("nan"), fx, float("nan"), False, error_msg=stop_reason))
            break

        if not math.isfinite(gx) or abs(gx) > 1e12:
            diverged = True
            stop_reason = f"Nilai g(x) membesar menuju tak hingga (divergen di x = {gx:g})"
            rows.append(IterationRow(r, x, gx, fx, float("nan"), False, error_msg=stop_reason))
            break

        e_tol = abs(gx - x)
        is_exact = (abs(fx) < 1e-14) or (gx == x)
        valid = (e_tol < eps) or is_exact

        rows.append(IterationRow(r, x, gx, fx, e_tol, valid))

        if valid and first_true is None:
            first_true = len(rows) - 1
            exact = is_exact

        # Langkah iterasi berikutnya
        x = gx

    if not rows:
        raise InputError("Gagal menjalankan iterasi pertama.")

    sol_idx = first_true if first_true is not None else len(rows) - 1
    sol_row = rows[sol_idx]

    root = sol_row.gx if math.isfinite(sol_row.gx) else sol_row.x
    try:
        f_root = f(root)
    except Exception:
        f_root = sol_row.fx

    return IterationResult(
        inputs=inputs,
        rows=rows,
        first_true=first_true,
        root=root,
        f_root=f_root,
        root_iteration=sol_row.r,
        converged=first_true is not None,
        exact_root=exact,
        diverged=diverged,
        stop_reason=stop_reason,
    )


# ==========================================================================
# 4. PEMFORMATAN ANGKA
# ==========================================================================
def format_number(value: Optional[float], decimals: int) -> str:
    """Format angka sesuai jumlah desimal, dengan koma sebagai pemisah desimal."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    if not math.isfinite(value):
        return str(value)
    if value == 0:
        value = 0.0
    if value != 0 and round(value, decimals) == 0:
        text = f"{value:.{decimals}E}"
    else:
        text = f"{value:.{decimals}f}"
    return text.replace(".", ",")


# ==========================================================================
# 5. RINGKASAN HASIL
# ==========================================================================
@dataclass
class ResultSummary:
    root_text: str
    f_root_text: str
    iteration_text: str
    conclusion: str


def summarize(result: IterationResult) -> ResultSummary:
    """Susun teks untuk blok 'Hasil Perhitungan'."""
    d = result.inputs.decimals
    root = format_number(result.root, d)
    f_root = format_number(result.f_root, d)
    eps = format_number(result.inputs.eps, d)
    sol_row = result.rows[result.solution_index]

    if result.converged and result.exact_root:
        conclusion = (f"Akar fungsi berhasil ditemukan pada iterasi ke-{result.root_iteration} "
                      f"dengan nilai x = {root} dan f(x) = 0 (akar eksak).")
    elif result.converged:
        conclusion = (f"Akar fungsi berhasil ditemukan pada iterasi ke-{result.root_iteration} "
                      f"dengan nilai x = {root} dan toleransi e_tol < {eps}.")
    elif result.diverged:
        conclusion = (f"Peringatan: iterasi terhenti pada iterasi ke-{sol_row.r} "
                      f"karena fungsi g(x) divergen atau tidak terdefinisi ({result.stop_reason}). "
                      f"Pendekatan terakhir adalah x = {root}.")
    else:
        last_e = format_number(sol_row.e_tol, d)
        conclusion = (f"Peringatan: iterasi maksimum (N = {result.inputs.n_max}) tercapai sebelum "
                      f"e_tol < {eps} terpenuhi. Akar pendekatan terakhir adalah x = {root} "
                      f"pada iterasi ke-{result.root_iteration} dengan e_tol = {last_e}.")

    return ResultSummary(root, f_root, str(result.root_iteration), conclusion)

