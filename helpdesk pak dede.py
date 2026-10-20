"""
Helpdesk Kampus (versi CLI, hanya pakai library bawaan Python)

Fitur:
1. Pusat Bantuan / FAQ per kategori
2. Chatbot sederhana (mencocokkan pertanyaan dengan FAQ)
3. Buat tiket layanan ke bagian terkait (Akademik, Keuangan, dll.)
4. Cek status tiket berdasarkan ID tiket / NIM
5. Mode Staf: lihat tiket, balas, dan ubah status
Data tiket disimpan di file tiket_kampus.json
"""

import json
import os
import random
import string
from datetime import datetime

DB_FILE = "tiket_kampus.json"

# ------------------------------------------------------------------
# Data FAQ
# ------------------------------------------------------------------
FAQ = {
    "Akademik": [
        ("Bagaimana cara mengisi KRS?",
         "Login ke portal akademik pada masa KRS, pilih mata kuliah sesuai "
         "kuota SKS, lalu klik Simpan dan ajukan persetujuan ke dosen wali.",
         ["krs", "kartu rencana studi", "isi krs", "ambil mata kuliah"]),
        ("Bagaimana cara mengajukan cuti akademik?",
         "Ajukan surat permohonan cuti ke bagian akademik sebelum masa KRS, "
         "dengan persetujuan dosen wali dan ketua prodi.",
         ["cuti", "cuti akademik", "berhenti sementara"]),
        ("Bagaimana cara melihat nilai dan KHS?",
         "Buka portal akademik > menu KHS > pilih semester. Jika nilai belum "
         "muncul, hubungi dosen pengampu atau bagian akademik.",
         ["nilai", "khs", "ipk", "ips", "transkrip"]),
    ],
    "Keuangan": [
        ("Bagaimana cara membayar UKT?",
         "Pembayaran UKT dilakukan melalui Virtual Account bank mitra kampus "
         "sesuai tagihan di portal. Simpan bukti pembayaran.",
         ["ukt", "spp", "bayar kuliah", "virtual account", "tagihan"]),
        ("Bagaimana cara mengajukan keringanan atau cicilan UKT?",
         "Ajukan permohonan ke bagian keuangan beserta dokumen pendukung "
         "(surat keterangan penghasilan orang tua) sebelum jatuh tempo.",
         ["keringanan", "cicil", "cicilan", "angsur", "dispensasi"]),
    ],
    "Beasiswa": [
        ("Beasiswa apa saja yang tersedia?",
         "Tersedia beasiswa prestasi, KIP Kuliah, dan beasiswa mitra. Info "
         "pendaftaran diumumkan di portal kemahasiswaan.",
         ["beasiswa", "kip", "bantuan biaya", "prestasi"]),
    ],
    "Perpustakaan & Fasilitas": [
        ("Bagaimana cara meminjam buku perpustakaan?",
         "Tunjukkan KTM di meja sirkulasi. Maksimal 3 buku untuk 7 hari dan "
         "bisa diperpanjang 1 kali lewat portal perpustakaan.",
         ["pinjam buku", "perpustakaan", "perpanjang buku", "denda"]),
        ("Bagaimana cara mengakses WiFi kampus?",
         "Sambungkan ke WiFi kampus lalu login memakai NIM dan kata sandi "
         "portal. Jika gagal, hubungi UPT TIK.",
         ["wifi", "internet", "hotspot", "jaringan"]),
    ],
    "Akun & Layanan Digital": [
        ("Saya lupa password portal mahasiswa",
         "Klik 'Lupa Kata Sandi' di halaman login portal, lalu ikuti tautan "
         "reset yang dikirim ke email kampus. Atau datang ke UPT TIK.",
         ["lupa password", "lupa sandi", "reset password", "login", "akun"]),
        ("Bagaimana cara mengurus KTM yang hilang?",
         "Buat surat kehilangan dari kepolisian, isi formulir di bagian "
         "kemahasiswaan, dan bayar biaya cetak ulang.",
         ["ktm", "kartu mahasiswa", "kartu hilang", "hilang"]),
    ],
}

KATEGORI_TIKET = ["Akademik", "Keuangan", "Beasiswa",
                  "Perpustakaan & Fasilitas", "Akun & Layanan Digital", "Lainnya"]
STATUS = ["Open", "Diproses", "Selesai"]


# ------------------------------------------------------------------
# Penyimpanan data
# ------------------------------------------------------------------
def muat_tiket():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def simpan_tiket(tiket):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tiket, f, indent=2, ensure_ascii=False)


def buat_id():
    acak = "".join(random.choices(string.digits, k=5))
    return f"HD-{datetime.now():%y%m%d}-{acak}"


def garis(judul=""):
    print("\n" + "=" * 60)
    if judul:
        print(judul.center(60))
        print("=" * 60)


# ------------------------------------------------------------------
# Fitur FAQ & Chatbot
# ------------------------------------------------------------------
def tampilkan_faq():
    garis("PUSAT BANTUAN KAMPUS")
    kategori = list(FAQ.keys())
    for i, k in enumerate(kategori, 1):
        print(f"{i}. {k}")
    pilih = input("\nPilih kategori (angka, Enter untuk kembali): ").strip()
    if not pilih.isdigit() or not 1 <= int(pilih) <= len(kategori):
        return
    daftar = FAQ[kategori[int(pilih) - 1]]
    garis(kategori[int(pilih) - 1])
    for i, (tanya, _, _) in enumerate(daftar, 1):
        print(f"{i}. {tanya}")
    p = input("\nPilih pertanyaan (angka): ").strip()
    if p.isdigit() and 1 <= int(p) <= len(daftar):
        tanya, jawab, _ = daftar[int(p) - 1]
        print(f"\nQ: {tanya}\nA: {jawab}")


def cari_jawaban(pertanyaan):
    """Cocokkan pertanyaan user dengan FAQ berdasarkan kata kunci."""
    teks = pertanyaan.lower()
    terbaik, skor_terbaik = None, 0
    for daftar in FAQ.values():
        for tanya, jawab, kunci in daftar:
            skor = sum(1 for k in kunci if k in teks)
            skor += sum(1 for kata in tanya.lower().split()
                        if len(kata) > 4 and kata in teks) * 0.5
            if skor > skor_terbaik:
                terbaik, skor_terbaik = (tanya, jawab), skor
    return terbaik if skor_terbaik >= 1 else None


def chatbot():
    garis("CHATBOT HELPDESK KAMPUS (ketik 'selesai' untuk keluar)")
    print("Bot: Halo, mahasiswa! Ada yang bisa saya bantu?")
    while True:
        tanya = input("Kamu: ").strip()
        if tanya.lower() in ("selesai", "exit", "keluar"):
            print("Bot: Terima kasih, semangat kuliahnya!")
            return
        hasil = cari_jawaban(tanya)
        if hasil:
            print(f"Bot: {hasil[1]}")
        else:
            print("Bot: Maaf, saya belum menemukan jawabannya. "
                  "Silakan buat tiket agar staf kampus bisa membantu.")
            if input("Buat tiket sekarang? (y/n): ").lower() == "y":
                buat_tiket(deskripsi_awal=tanya)
                return


# ------------------------------------------------------------------
# Fitur Tiket
# ------------------------------------------------------------------
def buat_tiket(deskripsi_awal=""):
    garis("BUAT TIKET LAYANAN")
    nama = input("Nama lengkap          : ").strip()
    nim = input("NIM                   : ").strip()
    prodi = input("Program studi         : ").strip()
    email = input("Email kampus/aktif    : ").strip()

    for i, k in enumerate(KATEGORI_TIKET, 1):
        print(f"{i}. {k}")
    pilih = input("Kategori (angka): ").strip()
    kategori = (KATEGORI_TIKET[int(pilih) - 1]
                if pilih.isdigit() and 1 <= int(pilih) <= len(KATEGORI_TIKET)
                else "Lainnya")

    if deskripsi_awal:
        print(f"Keluhan              : {deskripsi_awal}")
        deskripsi = deskripsi_awal
    else:
        deskripsi = input("Ceritakan kendala kamu: ").strip()

    if not nama or not nim or not email or not deskripsi:
        print("Nama, NIM, email, dan keluhan wajib diisi.")
        return

    tiket = muat_tiket()
    baru = {
        "id": buat_id(),
        "nama": nama,
        "nim": nim,
        "prodi": prodi,
        "email": email,
        "kategori": kategori,
        "deskripsi": deskripsi,
        "status": "Open",
        "dibuat": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "balasan": [],
    }
    tiket.append(baru)
    simpan_tiket(tiket)
    print(f"\nTiket berhasil dibuat! ID tiket kamu: {baru['id']}")
    print("Simpan ID ini untuk mengecek status tiket.")


def cetak_tiket(t):
    garis(f"TIKET {t['id']}")
    print(f"Nama     : {t['nama']} ({t['nim']})")
    print(f"Prodi    : {t['prodi'] or '-'}")
    print(f"Email    : {t['email']}")
    print(f"Kategori : {t['kategori']}")
    print(f"Status   : {t['status']}")
    print(f"Dibuat   : {t['dibuat']}")
    print(f"Keluhan  : {t['deskripsi']}")
    if t["balasan"]:
        print("\nBalasan Staf:")
        for b in t["balasan"]:
            print(f"  [{b['waktu']}] {b['staf']}: {b['pesan']}")
    else:
        print("\nBelum ada balasan dari staf.")


def cek_status():
    garis("CEK STATUS TIKET")
    kunci = input("Masukkan ID tiket / NIM: ").strip().upper()
    ditemukan = [t for t in muat_tiket()
                 if t["id"].upper() == kunci or t["nim"].upper() == kunci]
    if not ditemukan:
        print("Tiket tidak ditemukan.")
        return
    for t in ditemukan:
        cetak_tiket(t)


# ------------------------------------------------------------------
# Mode Staf
# ------------------------------------------------------------------
def mode_staf():
    garis("MODE STAF KAMPUS")
    sandi = input("Masukkan sandi staf: ")
    if sandi != "staf123":  # ganti sandi ini untuk produksi
        print("Sandi salah.")
        return
    nama_staf = input("Nama staf: ").strip() or "Staf Kampus"

    while True:
        tiket = muat_tiket()
        garis("DAFTAR TIKET")
        if not tiket:
            print("Belum ada tiket.")
        for i, t in enumerate(tiket, 1):
            print(f"{i}. {t['id']} | {t['kategori']:<24} | {t['status']:<9} | {t['nama']}")
        pilih = input("\nPilih tiket (angka) atau Enter untuk keluar: ").strip()
        if not pilih.isdigit() or not 1 <= int(pilih) <= len(tiket):
            return
        t = tiket[int(pilih) - 1]
        cetak_tiket(t)

        print("\n1. Balas tiket\n2. Ubah status\n3. Kembali")
        aksi = input("Pilih aksi: ").strip()
        if aksi == "1":
            pesan = input("Pesan balasan: ").strip()
            if pesan:
                t["balasan"].append({
                    "staf": nama_staf,
                    "pesan": pesan,
                    "waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                if t["status"] == "Open":
                    t["status"] = "Diproses"
        elif aksi == "2":
            for i, s in enumerate(STATUS, 1):
                print(f"{i}. {s}")
            s = input("Status baru (angka): ").strip()
            if s.isdigit() and 1 <= int(s) <= len(STATUS):
                t["status"] = STATUS[int(s) - 1]
        simpan_tiket(tiket)


# ------------------------------------------------------------------
# Menu utama
# ------------------------------------------------------------------
def main():
    menu = {
        "1": ("Pusat Bantuan (FAQ)", tampilkan_faq),
        "2": ("Chat dengan Bot", chatbot),
        "3": ("Buat Tiket Layanan", buat_tiket),
        "4": ("Cek Status Tiket", cek_status),
        "5": ("Mode Staf Kampus", mode_staf),
    }
    while True:
        garis("HELPDESK KAMPUS")
        for k, (nama, _) in menu.items():
            print(f"{k}. {nama}")
        print("0. Keluar")
        pilih = input("\nPilih menu: ").strip()
        if pilih == "0":
            print("Terima kasih sudah menghubungi Helpdesk Kampus!")
            break
        if pilih in menu:
            menu[pilih][1]()
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()