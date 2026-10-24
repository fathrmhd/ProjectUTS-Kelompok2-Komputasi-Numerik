"""Backend Metode Iterasi Titik Tetap (fixed-point iteration).

Rumus iterasi:
    x_{r+1} = g(x_r),  r = 0, 1, 2, ...

Kriteria berhenti:
    |x_{r+1} - x_r| < ε   (ε = toleransi)
atau jumlah iterasi mencapai batas maksimum N.

Catatan teori (tidak dihitung di modul ini):
    Iterasi dijamin konvergen bila |g'(x)| < 1 di sekitar akar.
    Jika |g'(x)| > 1, iterasi cenderung divergen.

Modul ini murni logika: tanpa GUI, tanpa print/input di dalam fungsi solver,
dan tanpa pembulatan angka (format desimal adalah urusan GUI).
"""

from __future__ import annotations

import math
from dataclasses import asdict, astuple, dataclass
from typing import Callable, Union

# Nilai |x| di atas batas ini dianggap sudah "meledak" (divergen).
# Tanpa batas ini, g(x) = x**2 + 1 akan berakhir OverflowError, bukan "divergen".
BATAS_DIVERGEN = 1e100

_NAMA_DIIZINKAN = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "pi": math.pi,
    "e": math.e,
    "abs": abs,
    "pow": math.pow,
}


@dataclass
class LangkahIterasi:
    """Satu baris tabel iterasi."""

    r: int
    x_r: float
    g_x_r: float
    galat: float


@dataclass
class HasilIterasi:
    """Hasil lengkap proses iterasi titik tetap."""

    akar: float | None
    jumlah_iterasi: int
    status: str  # "konvergen" | "divergen" | "maks_iterasi" | "error_perhitungan"
    pesan: str
    riwayat: list[LangkahIterasi]

    def ke_list_tuple(self) -> list[tuple]:
        """Ubah riwayat menjadi list tuple (r, x_r, g_x_r, galat) untuk ttk.Treeview."""
        return [astuple(langkah) for langkah in self.riwayat]

    def ke_list_dict(self) -> list[dict]:
        """Ubah riwayat menjadi list dict dengan kunci r, x_r, g_x_r, galat."""
        return [asdict(langkah) for langkah in self.riwayat]


def buat_fungsi(ekspresi: str) -> Callable[[float], float]:
    """Ubah string ekspresi (mis. "(x + 2) ** 0.5", "exp(-x)") menjadi fungsi g(x).

    Simbol "^" diperlakukan sebagai pangkat. Hanya fungsi math tertentu dan
    variabel x yang boleh dipakai. Raise ValueError jika ekspresi tidak valid.
    """
    if not isinstance(ekspresi, str) or not ekspresi.strip():
        raise ValueError("Ekspresi g(x) tidak boleh kosong.")
    # Tutup celah eval lewat atribut dunder seperti __class__.
    if "__" in ekspresi:
        raise ValueError("Ekspresi mengandung karakter '__' yang tidak diizinkan.")

    teks = ekspresi.strip().replace("^", "**")
    try:
        kode = compile(teks, "<g(x)>", "eval")
    except SyntaxError:
        raise ValueError(f"Sintaks ekspresi tidak valid: '{ekspresi}'.") from None

    namespace = {"__builtins__": {}, **_NAMA_DIIZINKAN}

    def g(x: float) -> float:
        """Evaluasi ekspresi pada nilai x."""
        return eval(kode, namespace, {"x": x})

    try:
        hasil_uji = g(1.0)
    except NameError as err:
        raise ValueError(
            f"Nama tidak dikenal dalam ekspresi: {err.name!r}. "
            "Gunakan variabel x dan fungsi: " + ", ".join(_NAMA_DIIZINKAN) + "."
        ) from None
    except (TypeError, AttributeError) as err:
        raise ValueError(f"Ekspresi tidak valid: {err}.") from None
    except ArithmeticError:
        pass  # Galat hitung di x = 1 (mis. log(x - 1)) belum tentu terjadi saat iterasi.
    except ValueError:
        pass  # Domain math di x = 1, sama seperti di atas.
    else:
        # complex tetap diterima: hasil complex di x = 1 belum tentu muncul saat iterasi.
        if isinstance(hasil_uji, bool) or not isinstance(hasil_uji, (int, float, complex)):
            raise ValueError("Ekspresi harus menghasilkan bilangan.")
    return g


def iterasi_titik_tetap(
    g: Union[Callable[[float], float], str],
    x0: float,
    toleransi: float,
    maks_iterasi: int,
) -> HasilIterasi:
    """Jalankan iterasi titik tetap x_{r+1} = g(x_r) mulai dari x0.

    Berhenti saat |x_{r+1} - x_r| < toleransi (status "konvergen"), saat nilai
    divergen (complex/inf/nan/terlalu besar), saat terjadi galat perhitungan,
    atau saat mencapai maks_iterasi. Riwayat langkah selalu dikembalikan.
    Raise ValueError jika input tidak valid.
    """
    if isinstance(g, str):
        g = buat_fungsi(g)
    elif not callable(g):
        raise ValueError("g harus berupa fungsi atau string ekspresi.")

    if isinstance(toleransi, bool) or not isinstance(toleransi, (int, float)) or not toleransi > 0:
        raise ValueError("Toleransi harus bilangan lebih besar dari 0.")
    if isinstance(maks_iterasi, bool) or not isinstance(maks_iterasi, int) or maks_iterasi < 1:
        raise ValueError("Maksimum iterasi harus bilangan bulat >= 1.")
    if isinstance(x0, bool) or not isinstance(x0, (int, float)) or not math.isfinite(x0):
        raise ValueError("Tebakan awal x0 harus bilangan hingga.")

    riwayat: list[LangkahIterasi] = []

    def selesai(status: str, pesan: str) -> HasilIterasi:
        # Akar hanya bermakna jika iterasi tidak divergen/error.
        ada_akar = riwayat and status in ("konvergen", "maks_iterasi")
        akar = riwayat[-1].g_x_r if ada_akar else None
        return HasilIterasi(akar, len(riwayat), status, pesan, riwayat)

    x = float(x0)
    for r in range(1, maks_iterasi + 1):
        try:
            gx = g(x)
        except (OverflowError, ZeroDivisionError, ValueError) as err:
            return selesai(
                "error_perhitungan",
                f"Galat perhitungan pada iterasi ke-{r} (x = {x}): {err}.",
            )

        if isinstance(gx, bool) or not isinstance(gx, (int, float, complex)):
            return selesai(
                "error_perhitungan",
                f"Iterasi ke-{r}: g(x) menghasilkan {type(gx).__name__}, bukan bilangan.",
            )
        if isinstance(gx, complex):
            return selesai("divergen", f"Iterasi ke-{r} menghasilkan bilangan kompleks; iterasi divergen.")
        try:
            gx = float(gx)
        except OverflowError:  # int terlalu besar untuk float
            gx = math.inf
        if not math.isfinite(gx):
            return selesai("divergen", f"Iterasi ke-{r} menghasilkan nilai tak hingga/NaN; iterasi divergen.")

        galat = abs(gx - x)
        riwayat.append(LangkahIterasi(r, x, gx, galat))

        if abs(gx) > BATAS_DIVERGEN:
            return selesai("divergen", f"Nilai membesar tanpa batas pada iterasi ke-{r}; iterasi divergen.")
        if galat < toleransi:
            return selesai("konvergen", f"Konvergen setelah {r} iterasi, akar ≈ {gx}.")
        x = gx

    return selesai(
        "maks_iterasi",
        f"Maksimum {maks_iterasi} iterasi tercapai; hampiran terakhir = "
        f"{riwayat[-1].g_x_r} (belum memenuhi toleransi).",
    )


if __name__ == "__main__":

    def cetak_tabel(hasil: HasilIterasi) -> None:
        print(f"{'r':>4} | {'x_r':>22} | {'g(x_r)':>22} | {'galat':>12}")
        print("-" * 70)
        for r, x_r, gx, galat in hasil.ke_list_tuple():
            print(f"{r:>4} | {x_r:>22.12g} | {gx:>22.12g} | {galat:>12.4e}")
        print(f"Status: {hasil.status} | Iterasi: {hasil.jumlah_iterasi} | Akar: {hasil.akar}")
        print(f"Pesan : {hasil.pesan}\n")

    kasus = [
        ("a", "(x + 2) ** 0.5", 0.5, 1e-6, 50, "konvergen"),
        ("b", "exp(-x)", 0.5, 1e-6, 100, "konvergen"),
        ("c", "x**2 + 1", 2, 1e-6, 50, "divergen"),
        ("d", "cos(x)", 1, 1e-6, 3, "maks_iterasi"),
    ]
    for nama, ekspresi, x0, eps, n, harapan in kasus:
        print(f"=== Kasus {nama}: g(x) = {ekspresi}, x0 = {x0}, eps = {eps}, N = {n} ===")
        hasil = iterasi_titik_tetap(ekspresi, x0, eps, n)
        cetak_tabel(hasil)
        assert hasil.status == harapan, (nama, hasil.status)

    assert abs(iterasi_titik_tetap("(x + 2) ** 0.5", 0.5, 1e-6, 50).akar - 2) < 1e-5
    assert abs(iterasi_titik_tetap("exp(-x)", 0.5, 1e-6, 100).akar - 0.567143) < 1e-5

    print("=== Uji tambahan: field akar ===")
    hasil = iterasi_titik_tetap("x**2 + 1", 2, 1e-6, 50)
    assert hasil.status == "divergen" and hasil.akar is None
    print(f"x**2 + 1, x0=2      : {hasil.status}, akar = {hasil.akar}")
    hasil = iterasi_titik_tetap("log(x)", 0.5, 1e-6, 50)
    assert hasil.status == "error_perhitungan" and hasil.akar is None
    print(f"log(x), x0=0.5      : {hasil.status}, akar = {hasil.akar} | {hasil.pesan}")
    hasil = iterasi_titik_tetap("-x", 1, 1e-6, 20)
    assert hasil.status == "maks_iterasi" and hasil.akar is not None
    print(f"-x, x0=1, N=20      : {hasil.status}, akar = {hasil.akar} | {hasil.pesan}")
    hasil = iterasi_titik_tetap(lambda x: "abc", 1, 1e-6, 5)
    assert hasil.status == "error_perhitungan" and hasil.akar is None
    print(f"callable -> str     : {hasil.status} | {hasil.pesan}\n")

    print("=== Uji tambahan: hasil ekspresi bukan bilangan ===")
    for ekspresi in ['"abc"', "(1,2)"]:
        try:
            buat_fungsi(ekspresi)
            raise AssertionError(f"Seharusnya ValueError: {ekspresi}")
        except ValueError as err:
            print(f"buat_fungsi({ekspresi!r}) -> ValueError: {err}")
    print()

    print('=== Kasus e: ekspresi tidak valid "x +* 2" ===')
    try:
        iterasi_titik_tetap("x +* 2", 0.5, 1e-6, 10)
        raise AssertionError("Seharusnya ValueError")
    except ValueError as err:
        print(f"ValueError tertangkap: {err}\n")

    print("Semua kasus sesuai harapan.")
