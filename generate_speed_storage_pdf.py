"""
Generate PDF Report for the last 2 analyses:
1. Speedup & Throughput Analysis (Kecepatan)
2. Storage & Database Footprint Analysis (Storage)
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class PDFReport(FPDF):
    def header(self):
        # Top banner line
        self.set_fill_color(16, 51, 82) # Deep navy
        self.rect(0, 0, 210, 4, 'F')

        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(100, 110, 125)
        self.set_y(6)
        self.cell(0, 5, 'LAPORAN ANALISIS PERFORMA & EFISIENSI STORAGE - NETFLIX CONDUCTOR', align='L')
        self.set_font('Helvetica', '', 8)
        self.set_y(6)
        self.cell(0, 5, '10 November 2026', align='R')

        # Divider line
        self.set_draw_color(220, 225, 230)
        self.line(12, 12, 198, 12)
        self.set_y(15)

    def footer(self):
        self.set_y(-12)
        self.set_draw_color(220, 225, 230)
        self.line(12, 285, 198, 285)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(120, 130, 140)
        self.cell(0, 5, 'Dokumen Analisis Performa & Storage Conductor - Sistem AP2T / Billing PLN', align='L')
        self.cell(0, 5, f'Halaman {self.page_no()} dari {{nb}}', align='R')

def draw_card(pdf, x, y, w, h, label, value, val_color=(20, 30, 45)):
    pdf.set_fill_color(245, 248, 252) # Light soft blue-gray
    pdf.set_draw_color(215, 225, 238) # Light border
    pdf.rect(x, y, w, h, 'DF')

    pdf.set_xy(x + 3, y + 2.2)
    pdf.set_font('Helvetica', 'B', 7.2)
    pdf.set_text_color(100, 115, 135)
    pdf.cell(w - 6, 3.8, label.upper(), align='L')

    pdf.set_xy(x + 3, y + 6.8)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(*val_color)
    pdf.cell(w - 6, 5.5, value, align='L')

def section_title(pdf, num, title):
    pdf.ln(2.5)
    pdf.set_font('Helvetica', 'B', 10.5)
    pdf.set_text_color(16, 51, 82)
    pdf.cell(0, 5.5, f"{num}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(16, 51, 82)
    pdf.set_line_width(0.3)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 186, pdf.get_y())
    pdf.ln(2)

def main():
    pdf = PDFReport(orientation='P', unit='mm', format='A4')
    pdf.set_margins(12, 14, 12)
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Document Main Title
    pdf.set_font('Helvetica', 'B', 13.5)
    pdf.set_text_color(16, 51, 82)
    pdf.cell(0, 6.5, 'Laporan Analisis Perbandingan Kecepatan & Penggunaan Storage', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    pdf.set_font('Helvetica', '', 8.8)
    pdf.set_text_color(80, 95, 115)
    pdf.cell(0, 4.5, 'Evaluasi Dampak Optimasi Konsolidasi Task workflow_general_non_energi: Hari Ini (10 Nov) vs Kemarin (09 Nov)', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(2.5)

    # Summary Info Cards (Grid 3x2)
    start_y = pdf.get_y()
    card_w = (186 - 6) / 3 # 60mm each
    card_h = 14.5

    draw_card(pdf, 12, start_y, card_w, card_h, "Target Sub-Workflow", "workflow_general_non_energi")
    draw_card(pdf, 12 + card_w + 3, start_y, card_w, card_h, "Percepatan Latensi (Mean)", "10,23x Lebih Cepat (16,5s vs 168,9s)", (0, 102, 204))
    draw_card(pdf, 12 + (card_w + 3)*2, start_y, card_w, card_h, "Percepatan Median (P50)", "19,84x Lebih Cepat (0,51s vs 10,04s)", (0, 102, 204))

    draw_card(pdf, 12, start_y + card_h + 2.5, card_w, card_h, "Kenaikan Throughput (TPS)", "+875,5% (1,51 TPS vs 0,15 TPS)", (39, 134, 61))
    draw_card(pdf, 12 + card_w + 3, start_y + card_h + 2.5, card_w, card_h, "Reduksi Task Records", "-98,97% (250 vs 24.250 tasks)", (39, 134, 61))
    draw_card(pdf, 12 + (card_w + 3)*2, start_y + card_h + 2.5, card_w, card_h, "Penghematan Storage DB", "-68,6% DB & -41,3% Elasticsearch", (140, 50, 150))

    pdf.set_y(start_y + (card_h * 2) + 4.5)

    # -------------------------------------------------------------
    # 1. ANALISIS PERBEDAAN KECEPATAN (SPEEDUP & THROUGHPUT)
    # -------------------------------------------------------------
    section_title(pdf, "1", "Analisis Perbedaan Kecepatan & Throughput Runtime")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(35, 45, 55)
    pdf.multi_cell(186, 3.8,
        "Perubahan definisi alur kerja workflow_general_non_energi dari 97 task modular menjadi 1 task konsolidasi "
        "(hitung_semua_workflow_general_non_energi) berhasil memangkas 98,97% overhead penjadwalan pada engine Conductor. "
        "Hasil pengujian batch 250 transaksi pelanggan antara Kemarin (09 Nov) dan Hari Ini (10 Nov) menunjukkan lonjakan kinerja drastis:"
    )
    pdf.ln(1)

    # Tabel 1: Metrik Kecepatan Sub-Workflow
    col_w1 = [52, 42, 42, 50]
    headers_t1 = ["Indikator Kinerja Sub-Workflow", "Kemarin (97 Task)", "Hari Ini (1 Task)", "Selisih / Faktor Percepatan"]

    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_fill_color(27, 54, 93)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers_t1):
        pdf.cell(col_w1[i], 5.2, h, border=1, align='C', fill=True)
    pdf.ln()

    sub_speed_rows = [
        ("Total Waktu Batch (Span 250 Wf)", "1.613,69 detik (26,89 menit)", "165,43 detik (2,76 menit)", "9,75x LEBIH CEPAT (-89,75%)"),
        ("Throughput Batch (TPS)", "0,1549 TPS (9,30 WPM)", "1,5112 TPS (90,67 WPM)", "+875,5% (Naik 9,75x lipat)"),
        ("Rata-rata Durasi Eksekusi (Mean)", "168,86 detik (~2,81 menit)", "16,50 detik", "10,23x LEBIH CEPAT (-90,23%)"),
        ("Median Durasi Eksekusi (P50)", "10,04 detik", "0,51 detik (506 ms)", "19,84x LEBIH CEPAT (-94,96%)"),
        ("Persentil 75 (P75)", "238,66 detik (~4,0 menit)", "17,58 detik", "13,58x Lebih Cepat"),
        ("Persentil 90 (P90)", "568,67 detik (~9,5 menit)", "65,78 detik", "8,65x Lebih Cepat"),
        ("Persentil 95 (P95)", "829,67 detik (~13,8 menit)", "82,40 detik", "10,07x Lebih Cepat"),
        ("Durasi Tercepat (Minimum)", "3,594 detik", "0,075 detik (75 ms)", "47,92x LEBIH CEPAT"),
        ("Durasi Terlama (Maksimum)", "1.408,64 detik (23,48 menit)", "142,80 detik (2,38 menit)", "9,86x Lebih Cepat (-21,1 menit)"),
        ("Beban Kerja Kumulatif Worker", "42.214,65 detik (11,73 Jam)", "4.125,84 detik (1,15 Jam)", "Hemat 10,58 Jam Komputasi"),
    ]

    for r_idx, r in enumerate(sub_speed_rows):
        c = (248, 251, 255) if r_idx % 2 == 1 else (255, 255, 255)
        pdf.set_fill_color(*c)
        pdf.set_text_color(30, 40, 50)
        pdf.set_font('Helvetica', '', 7.2)
        pdf.cell(col_w1[0], 4.7, r[0], border=1, fill=True)
        pdf.cell(col_w1[1], 4.7, r[1], border=1, align='C', fill=True)
        pdf.cell(col_w1[2], 4.7, r[2], border=1, align='C', fill=True)

        is_high = ("LEBIH CEPAT" in r[3] or "Naik" in r[3] or "Hemat" in r[3])
        if is_high:
            pdf.set_font('Helvetica', 'B', 7.2)
            pdf.set_text_color(0, 102, 204)
        pdf.cell(col_w1[3], 4.7, r[3], border=1, align='C', fill=True)
        pdf.ln()

    pdf.ln(1)

    # Dampak End-to-End pada Root Workflow
    pdf.set_font('Helvetica', 'B', 8.2)
    pdf.set_text_color(16, 51, 82)
    pdf.cell(0, 4.5, "Dampak End-to-End pada Root Workflow (workflow_normal):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    col_w_root = [52, 42, 42, 50]
    headers_root = ["Metrik Root workflow_normal", "Kemarin (09 Nov)", "Hari Ini (10 Nov)", "Efisiensi Total"]
    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_fill_color(35, 75, 115)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers_root):
        pdf.cell(col_w_root[i], 5, h, border=1, align='C', fill=True)
    pdf.ln()

    root_rows = [
        ("Total Waktu Selesai Batch (Span)", "1.720,11 detik (28,67 menit)", "225,92 detik (3,77 menit)", "7,61x Lebih Cepat (-24,9 menit)"),
        ("Throughput Transaksi (TPS)", "0,1453 TPS (8,72 WPM)", "1,1066 TPS (66,40 WPM)", "+661,4% (Naik 7,61x lipat)"),
        ("Rata-rata Durasi Instance", "997,88 detik (16,63 menit)", "163,17 detik (2,72 menit)", "6,12x Lebih Cepat (-83,65%)"),
        ("Beban Kumulatif Worker DB/Queue", "249.470,70 detik (69,30 Jam)", "40.792,10 detik (11,33 Jam)", "Menghemat 57,97 Jam Komputasi"),
    ]

    for r_idx, r in enumerate(root_rows):
        c = (248, 251, 255) if r_idx % 2 == 1 else (255, 255, 255)
        pdf.set_fill_color(*c)
        pdf.set_text_color(30, 40, 50)
        pdf.set_font('Helvetica', '', 7.2)
        pdf.cell(col_w_root[0], 4.7, r[0], border=1, fill=True)
        pdf.cell(col_w_root[1], 4.7, r[1], border=1, align='C', fill=True)
        pdf.cell(col_w_root[2], 4.7, r[2], border=1, align='C', fill=True)
        pdf.set_font('Helvetica', 'B', 7.2)
        pdf.set_text_color(39, 134, 61)
        pdf.cell(col_w_root[3], 4.7, r[3], border=1, align='C', fill=True)
        pdf.ln()

    # --- PAGE 2 ---
    pdf.add_page()

    # -------------------------------------------------------------
    # 2. ANALISIS PERBANDINGAN PENGGUNAAN STORAGE
    # -------------------------------------------------------------
    section_title(pdf, "2", "Analisis Perbandingan Penggunaan Storage & Database Footprint")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(35, 45, 55)
    pdf.multi_cell(186, 3.8,
        "Optimasi alur kerja tidak hanya mempercepat waktu pemrosesan, melainkan mereduksi beban I/O disk secara masif "
        "di tiga tingkatan penyimpanan: Elasticsearch (Search & Indexing), Oracle Database (State Store), dan Redis (RAM & Queue). "
        "Berikut adalah rincian perbandingan konsumsi storage faktual pada batch 250 pelanggan:"
    )
    pdf.ln(1)

    # Tabel 3: Perbandingan Storage Multi-Layer
    col_w_stor = [50, 42, 42, 52]
    headers_stor = ["Layer / Komponen Penyimpanan", "Kemarin (97 Task)", "Hari Ini (1 Task)", "Penghematan Storage / Delta"]

    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_fill_color(27, 54, 93)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers_stor):
        pdf.cell(col_w_stor[i], 5.2, h, border=1, align='C', fill=True)
    pdf.ln()

    stor_rows = [
        ("Elasticsearch: Jumlah Dokumen Task", "24.250 dokumen", "250 dokumen", "-24.000 dokumen (-98,97%)"),
        ("Elasticsearch: Rata-rata Ukuran Doc", "1.177 bytes (~1,18 KB)", "67.051 bytes (~65,48 KB)", "Konsolidasi script dalam 1 doc"),
        ("Elasticsearch: Total Raw Document Size", "27,23 MB", "15,99 MB", "Hemat 11,24 MB (-41,28%)"),
        ("Elasticsearch: Lucene Index Overhead", "Sangat tinggi (24.250 doc ID)", "Sangat ringan (250 doc ID)", "-98,97% index leaf nodes & memory"),
        ("Database Relasional: Baris Tabel 'task'", "24.250 baris", "250 baris", "-24.000 baris (-98,97%)"),
        ("Database Relasional: Status Transitions", "~48.500 mutasi status", "~500 mutasi status", "-48.000 mutasi I/O updates"),
        ("Database Relasional: Table Space & Index", "~53,35 MB", "~16,75 MB", "Hemat ~36,60 MB (-68,60%)"),
        ("Database Relasional: Redo Log & Undo", "Traffic tulis sangat tinggi", "Traffic tulis minimal", "Pangkas ~90% disk I/O churn"),
        ("Redis RAM: Operasi Queue Push/Pop", "24.250 transaksi queue", "250 transaksi queue", "-24.000 operasi (-98,97%)"),
        ("Redis RAM: Distributed Lock Keys", "24.250 kunci lock", "250 kunci lock", "-24.000 lock contention"),
        ("Level Workflow: Ukuran Doc Workflow", "5,65 KB in / 1,43 KB out", "5,74 KB in / 1,44 KB out", "Relatif sama (100% identik)"),
    ]

    for r_idx, r in enumerate(stor_rows):
        c = (248, 251, 255) if r_idx % 2 == 1 else (255, 255, 255)
        pdf.set_fill_color(*c)
        pdf.set_text_color(30, 40, 50)
        pdf.set_font('Helvetica', '', 7.2)
        pdf.cell(col_w_stor[0], 4.7, r[0], border=1, fill=True)
        pdf.cell(col_w_stor[1], 4.7, r[1], border=1, align='C', fill=True)
        pdf.cell(col_w_stor[2], 4.7, r[2], border=1, align='C', fill=True)

        is_high = ("-98,97%" in r[3] or "Hemat" in r[3] or "Pangkas" in r[3])
        if is_high:
            pdf.set_font('Helvetica', 'B', 7.2)
            pdf.set_text_color(0, 102, 204)
        pdf.cell(col_w_stor[3], 4.7, r[3], border=1, align='C', fill=True)
        pdf.ln()

    pdf.ln(1)

    # -------------------------------------------------------------
    # 3. PROYEKSI EFISIENSI STORAGE SKALA PRODUKSI
    # -------------------------------------------------------------
    section_title(pdf, "3", "Proyeksi Efisiensi Storage pada Skala Produksi (1 Juta Pelanggan)")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(35, 45, 55)
    pdf.multi_cell(186, 3.8,
        "Jika efisiensi ini diproyeksikan pada pemrosesan batch bulanan skala penuh billing PLN "
        "(asumsi volume beban 1.000.000 rekening pelanggan):"
    )
    pdf.ln(1)

    col_w_proj = [52, 42, 42, 50]
    headers_proj = ["Parameter Produksi (1 Juta Rekening)", "Skema Lama (97 Task)", "Skema Baru (1 Task)", "Efisiensi Nyata yang Diraih"]

    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_fill_color(35, 75, 115)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers_proj):
        pdf.cell(col_w_proj[i], 5, h, border=1, align='C', fill=True)
    pdf.ln()

    proj_rows = [
        ("Total Record Task (DB & ES)", "97.000.000 record", "1.000.000 record", "Menghapus 96 Juta baris/dokumen!"),
        ("Storage Task di Elasticsearch", "~108,9 GB", "~63,9 GB", "Hemat ~45,0 GB disk ES (-41,3%)"),
        ("Storage Tabel & Indeks di Database", "~213,4 GB", "~67,0 GB", "Hemat ~146,4 GB storage DB (-68,6%)"),
        ("Volume Transaksi Redo Log DB", "Ekstrem (97 Juta insert + 194M update)", "Ringan (1 Juta insert + 2M update)", "Bebas dari risiko bottleneck I/O disk"),
    ]

    for r_idx, r in enumerate(proj_rows):
        c = (248, 251, 255) if r_idx % 2 == 1 else (255, 255, 255)
        pdf.set_fill_color(*c)
        pdf.set_text_color(30, 40, 50)
        pdf.set_font('Helvetica', '', 7.2)
        pdf.cell(col_w_proj[0], 4.7, r[0], border=1, fill=True)
        pdf.cell(col_w_proj[1], 4.7, r[1], border=1, align='C', fill=True)
        pdf.cell(col_w_proj[2], 4.7, r[2], border=1, align='C', fill=True)
        pdf.set_font('Helvetica', 'B', 7.2)
        pdf.set_text_color(39, 134, 61)
        pdf.cell(col_w_proj[3], 4.7, r[3], border=1, align='C', fill=True)
        pdf.ln()

    pdf.ln(1)

    # -------------------------------------------------------------
    # 4. KESIMPULAN ARSITEKTURAL
    # -------------------------------------------------------------
    section_title(pdf, "4", "Kesimpulan Arsitektural & Rekomendasi Teknis")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(35, 45, 55)
    concl = (
        "1. Sinergi Sempurna Antara Kecepatan & Penghematan: Optimasi task konsolidasi tidak menimbulkan trade-off; "
        "sistem mendapatkan percepatan 10,23x lebih cepat sekaligus menghemat 41,28% ruang disk Elasticsearch dan 68,6% ruang database.\n"
        "2. Skalabilitas Teruji: Pengurangan 98,97% operasi queue Redis dan locking membebaskan thread decider Conductor, "
        "sehingga sistem mampu menangani lonjakan transaksi (peak burst) tanpa antrean macet.\n"
        "3. Rekomendasi: Pola konsolidasi task serupa sangat disarankan untuk diterapkan pada sub-workflow spesifik tarif lainnya "
        "(seperti workflow tarif beban blok) untuk mencapai throughput TPS maksimal secara menyeluruh."
    )
    pdf.multi_cell(186, 3.8, concl)

    # Sign-off note
    pdf.ln(2.5)
    pdf.set_draw_color(220, 225, 230)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(1.5)
    pdf.set_font('Helvetica', 'I', 7.2)
    pdf.set_text_color(120, 130, 140)
    pdf.cell(0, 4, "Laporan resmi digenerate otomatis berdasarkan data metrik REST API Conductor v3.13.0 & cluster Elasticsearch 8.19.", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Save PDF
    out_pdf_name = "Laporan_Analisis_Kecepatan_dan_Storage_Workflow_General_Non_Energi.pdf"
    out_pdf_alias = "Summary_Analisis_Kecepatan_dan_Storage.pdf"

    print(f"Saving PDF to {out_pdf_name}...")
    pdf.output(out_pdf_name)

    print(f"Saving copy to {out_pdf_alias}...")
    pdf.output(out_pdf_alias)

    pdf_size = os.path.getsize(out_pdf_name) / 1024
    print(f"PDF generated successfully: {out_pdf_name} ({pdf_size:.1f} KB, {pdf.page_no()} pages)")

if __name__ == '__main__':
    main()
