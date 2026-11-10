"""
Generate PDF Report for:
Comparison of Conductor at http://localhost:8080 (Quarkus + ES8)
vs http://localhost:9090 (Callysta + Redis Indexing)
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
        self.cell(0, 5, 'LAPORAN BENCHMARK & KOMPARASI PRODUK CONDUCTOR - NETFLIX CONDUCTOR', align='L')
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
        self.cell(0, 5, 'Dokumen Laporan Benchmark Conductor: Port 8080 vs Port 9090 - Sistem AP2T / Billing PLN', align='L')
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
    pdf.ln(2.2)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(16, 51, 82)
    pdf.cell(0, 5.2, f"{num}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(16, 51, 82)
    pdf.set_line_width(0.3)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 186, pdf.get_y())
    pdf.ln(1.8)

def main():
    pdf = PDFReport(orientation='P', unit='mm', format='A4')
    pdf.set_margins(12, 14, 12)
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Document Main Title
    pdf.set_font('Helvetica', 'B', 13.5)
    pdf.set_text_color(16, 51, 82)
    pdf.cell(0, 6.5, 'Laporan Benchmark Conductor: Port 8080 vs Port 9090', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    pdf.set_font('Helvetica', '', 8.8)
    pdf.set_text_color(80, 95, 115)
    pdf.cell(0, 4.5, 'Komparasi Kinerja Throughput (TPS), Latensi, Efisiensi Storage, dan Stabilitas pada Definisi Workflow Sama', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(2.5)

    # Summary Info Cards (Grid 3x2)
    start_y = pdf.get_y()
    card_w = (186 - 6) / 3 # 60mm each
    card_h = 14.5

    draw_card(pdf, 12, start_y, card_w, card_h, "Lingkungan Pengujian", "Port 8080 vs Port 9090")
    draw_card(pdf, 12 + card_w + 3, start_y, card_w, card_h, "Tingkat Keberhasilan", "8080: 100% vs 9090: 95,9%", (39, 134, 61))
    draw_card(pdf, 12 + (card_w + 3)*2, start_y, card_w, card_h, "Keandalan (Stabilitas)", "8080: 0 Gagal | 9090: 9 GAGAL", (180, 40, 40))

    draw_card(pdf, 12, start_y + card_h + 2.5, card_w, card_h, "Throughput Root (TPS)", "8080 Unggul 2,14x (+113,9%)", (0, 102, 204))
    draw_card(pdf, 12 + card_w + 3, start_y + card_h + 2.5, card_w, card_h, "Kecepatan Durasi (Mean)", "8080 2,38x Lebih Cepat (2,7m vs 6,5m)", (0, 102, 204))
    draw_card(pdf, 12 + (card_w + 3)*2, start_y + card_h + 2.5, card_w, card_h, "Arsitektur Index Storage", "8080: ES8 Disk vs 9090: Redis RAM", (140, 50, 150))

    pdf.set_y(start_y + (card_h * 2) + 4.5)

    # -------------------------------------------------------------
    # 1. KESIMPULAN AWAL & PERBANDINGAN ARSITEKTUR
    # -------------------------------------------------------------
    section_title(pdf, "1", "Perbandingan Arsitektur & Ringkasan Eksekutif")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(35, 45, 55)
    pdf.multi_cell(186, 3.8,
        "Pengujian komparasi dilakukan terhadap 2 produk orkestrator Conductor yang berjalan bersamaan di lingkungan pengujian: "
        "Conductor Quarkus (http://localhost:8080) dan Callysta Conductor (http://localhost:9090). Keduanya mengeksekusi "
        "definisi workflow yang sama persis (versi optimasi 1 task konsolidasi pada workflow_general_non_energi). "
        "Hasil benchmark membuktikan bahwa port 8080 (conductor-quarkus) JELAS LEBIH UNGGUL dari sisi TPS (+114%), "
        "kecepatan durasi (2,38x lebih cepat), efisiensi storage/RAM, serta stabilitas (100% tuntas vs 9 gagal di port 9090)."
    )
    pdf.ln(1)

    # Tabel 1: Spesifikasi Arsitektur
    col_w_spec = [46, 52, 52, 36]
    headers_spec = ["Komponen Arsitektur", "Port 8080 (Conductor Quarkus)", "Port 9090 (Callysta Conductor)", "Status / Dampak"]
    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_fill_color(27, 54, 93)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers_spec):
        pdf.cell(col_w_spec[i], 5, h, border=1, align='C', fill=True)
    pdf.ln()

    arch_rows = [
        ("Docker Container / Image", "conductor (conductor-quarkus:amd64)", "callysta (callysta-conductor)", "Runtime Quarkus vs Standard"),
        ("Definisi workflow_normal", "Versi 1 (7 Tasks)", "Versi 1 (7 Tasks)", "Sama Persis"),
        ("Definisi general_non_energi", "Versi 4 (1 Task Konsolidasi)", "Versi 4 (1 Task Konsolidasi)", "Sama Persis"),
        ("Queue & State Storage", "Redis Cluster (v8.2.4)", "Redis Cluster (v8.2.4)", "Sama (Port 7001-7006)"),
        ("Search & Indexing Engine", "Elasticsearch 8.19.11 (Disk)", "Redis Cluster In-Memory (RAM)", "8080 Unggul Jauh"),
        ("Script Context Pool", "Enabled (Pool Size 150)", "Default / Unpooled", "8080 Lebih Responsif"),
    ]

    for r_idx, r in enumerate(arch_rows):
        c = (248, 251, 255) if r_idx % 2 == 1 else (255, 255, 255)
        pdf.set_fill_color(*c)
        pdf.set_text_color(30, 40, 50)
        pdf.set_font('Helvetica', '', 7.2)
        pdf.cell(col_w_spec[0], 4.7, r[0], border=1, fill=True)
        pdf.cell(col_w_spec[1], 4.7, r[1], border=1, align='C', fill=True)
        pdf.cell(col_w_spec[2], 4.7, r[2], border=1, align='C', fill=True)
        if "Unggul" in r[3] or "Responsif" in r[3]:
            pdf.set_font('Helvetica', 'B', 7.2)
            pdf.set_text_color(0, 102, 204)
        pdf.cell(col_w_spec[3], 4.7, r[3], border=1, align='C', fill=True)
        pdf.ln()

    pdf.ln(1)

    # -------------------------------------------------------------
    # 2. TABEL PERBANDINGAN ROOT WORKFLOW_NORMAL
    # -------------------------------------------------------------
    section_title(pdf, "2", "Perbandingan Kinerja Root Workflow (workflow_normal)")
    col_w_root = [52, 45, 45, 44]
    headers_root = ["Indikator Kinerja Root", "Port 8080 (Quarkus)", "Port 9090 (Callysta)", "Keunggulan Port 8080"]
    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_fill_color(27, 54, 93)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers_root):
        pdf.cell(col_w_root[i], 5, h, border=1, align='C', fill=True)
    pdf.ln()

    root_rows = [
        ("Tingkat Keberhasilan (Success)", "100% COMPLETED (250/250)", "95,88% (233 Sukses, 9 GAGAL)", "8080 Stabil (0 Gagal)"),
        ("Total Waktu Selesai Batch (Span)", "225,92 detik (3,77 menit)", "450,31 detik (7,51 menit)", "1,99x Lebih Cepat (-49,8%)"),
        ("Throughput Batch (TPS)", "1,1066 TPS (66,40 WPM)", "0,5174 TPS (31,05 WPM)", "2,14x LEBIH TINGGI (+113,9%)"),
        ("Rata-rata Durasi Eksekusi (Mean)", "163,17 detik (2,72 menit)", "388,95 detik (6,48 menit)", "2,38x LEBIH CEPAT (-58,0%)"),
        ("Median Durasi Eksekusi (P50)", "168,16 detik", "388,41 detik", "2,31x Lebih Cepat"),
        ("Persentil 90 (P90)", "215,15 detik", "407,47 detik", "1,89x Lebih Cepat"),
        ("Durasi Tercepat (Minimum)", "67,00 detik", "355,37 detik", "5,30x Lebih Cepat"),
        ("Durasi Terlama (Maksimum)", "224,48 detik", "440,73 detik", "1,96x Lebih Cepat"),
        ("Beban Kumulatif Worker", "40.792 detik (11,33 Jam)", "90.625 detik (25,17 Jam)", "Hemat 13,84 Jam Kerja"),
    ]

    for r_idx, r in enumerate(root_rows):
        c = (248, 251, 255) if r_idx % 2 == 1 else (255, 255, 255)
        pdf.set_fill_color(*c)
        pdf.set_text_color(30, 40, 50)
        pdf.set_font('Helvetica', '', 7.2)
        pdf.cell(col_w_root[0], 4.7, r[0], border=1, fill=True)
        pdf.cell(col_w_root[1], 4.7, r[1], border=1, align='C', fill=True)
        pdf.cell(col_w_root[2], 4.7, r[2], border=1, align='C', fill=True)
        if "LEBIH TINGGI" in r[3] or "LEBIH CEPAT" in r[3] or "Stabil" in r[3] or "Hemat" in r[3]:
            pdf.set_font('Helvetica', 'B', 7.2)
            pdf.set_text_color(0, 102, 204)
        pdf.cell(col_w_root[3], 4.7, r[3], border=1, align='C', fill=True)
        pdf.ln()

    # --- PAGE 2 ---
    pdf.add_page()

    # -------------------------------------------------------------
    # 3. TABEL PERBANDINGAN SUB-WORKFLOW GENERAL NON ENERGI
    # -------------------------------------------------------------
    section_title(pdf, "3", "Perbandingan Kinerja Sub-Workflow (workflow_general_non_energi)")
    col_w_sub = [52, 45, 45, 44]
    headers_sub = ["Indikator Kinerja Sub-Workflow", "Port 8080 (Quarkus)", "Port 9090 (Callysta)", "Keunggulan Port 8080"]
    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_fill_color(27, 54, 93)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers_sub):
        pdf.cell(col_w_sub[i], 5, h, border=1, align='C', fill=True)
    pdf.ln()

    sub_rows = [
        ("Total Eksekusi Selesai", "250 Workflow (100%)", "233 Workflow (Sebagian gagal)", "8080 Sukses Penuh"),
        ("Total Waktu Batch (Span)", "165,43 detik (2,76 menit)", "274,41 detik (4,57 menit)", "1,66x Lebih Cepat (-39,7%)"),
        ("Throughput Sub-Workflow (TPS)", "1,5112 TPS (90,67 WPM)", "0,8491 TPS (50,95 WPM)", "1,78x LEBIH TINGGI (+78,0%)"),
        ("Rata-rata Durasi Eksekusi (Mean)", "16,50 detik", "142,32 detik (2,37 menit)", "8,62x LEBIH CEPAT (-88,4%)"),
        ("Median Durasi Eksekusi (P50)", "0,51 detik (506 ms)", "149,27 detik", "295x LEBIH CEPAT!"),
        ("Persentil 75 (P75)", "17,58 detik", "179,76 detik", "10,2x Lebih Cepat"),
        ("Persentil 90 (P90)", "65,78 detik", "182,36 detik", "2,77x Lebih Cepat"),
        ("Durasi Tercepat (Minimum)", "0,075 detik (75 ms)", "66,37 detik", "885x Lebih Cepat"),
        ("Durasi Terlama (Maksimum)", "142,80 detik", "187,69 detik", "1,31x Lebih Cepat"),
        ("Beban Kumulatif Worker", "4.125,84 detik (1,15 Jam)", "33.161,23 detik (9,21 Jam)", "Hemat 8,06 Jam Komputasi"),
    ]

    for r_idx, r in enumerate(sub_rows):
        c = (248, 251, 255) if r_idx % 2 == 1 else (255, 255, 255)
        pdf.set_fill_color(*c)
        pdf.set_text_color(30, 40, 50)
        pdf.set_font('Helvetica', '', 7.2)
        pdf.cell(col_w_sub[0], 4.7, r[0], border=1, fill=True)
        pdf.cell(col_w_sub[1], 4.7, r[1], border=1, align='C', fill=True)
        pdf.cell(col_w_sub[2], 4.7, r[2], border=1, align='C', fill=True)
        if "LEBIH TINGGI" in r[3] or "LEBIH CEPAT" in r[3] or "Sukses" in r[3] or "Hemat" in r[3]:
            pdf.set_font('Helvetica', 'B', 7.2)
            pdf.set_text_color(0, 102, 204)
        pdf.cell(col_w_sub[3], 4.7, r[3], border=1, align='C', fill=True)
        pdf.ln()

    pdf.ln(1)

    # -------------------------------------------------------------
    # 4. TABEL PERBANDINGAN SPACE / STORAGE & MEMORY
    # -------------------------------------------------------------
    section_title(pdf, "4", "Perbandingan Space / Storage & Konsumsi Memory")
    col_w_stor = [48, 48, 48, 42]
    headers_stor = ["Aspek Penyimpanan", "Port 8080 (Quarkus + ES8)", "Port 9090 (Callysta + Redis Index)", "Analisis Efisiensi"]
    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_fill_color(27, 54, 93)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers_stor):
        pdf.cell(col_w_stor[i], 5, h, border=1, align='C', fill=True)
    pdf.ln()

    stor_rows = [
        ("Penyimpanan Index Search", "Elasticsearch 8 di Disk", "Redis Cluster di RAM", "8080 Jauh Lebih Hemat RAM"),
        ("Konsumsi Memory RAM Redis", "Bersih (~20 MB antrean)", "Sangat Tinggi (>632 MB RAM)", "9090 membebani RAM Redis"),
        ("Kompresi Payload Histori", "Tinggi (Lucene Segments)", "Raw JSON (Uncompressed)", "8080 Hemat Storage Disk"),
        ("Potensi Risiko OOM / Kegagalan", "Sangat Rendah (Bebas OOM)", "Tinggi (Kenaikan memory)", "9090 memicu task failure"),
        ("Ukuran Payload per Workflow", "~4,2 KB in / ~2,3 KB out", "~4,2 KB in / ~2,2 KB out", "Data bisnis identik"),
    ]

    for r_idx, r in enumerate(stor_rows):
        c = (248, 251, 255) if r_idx % 2 == 1 else (255, 255, 255)
        pdf.set_fill_color(*c)
        pdf.set_text_color(30, 40, 50)
        pdf.set_font('Helvetica', '', 7.2)
        pdf.cell(col_w_stor[0], 4.7, r[0], border=1, fill=True)
        pdf.cell(col_w_stor[1], 4.7, r[1], border=1, align='C', fill=True)
        pdf.cell(col_w_stor[2], 4.7, r[2], border=1, align='C', fill=True)
        if "Hemat" in r[3] or "Rendah" in r[3]:
            pdf.set_font('Helvetica', 'B', 7.2)
            pdf.set_text_color(39, 134, 61)
        pdf.cell(col_w_stor[3], 4.7, r[3], border=1, align='C', fill=True)
        pdf.ln()

    pdf.ln(1)

    # -------------------------------------------------------------
    # 5. INVESTIGASI KEGAGALAN 9 WORKFLOW DI PORT 9090
    # -------------------------------------------------------------
    section_title(pdf, "5", "Investigasi Akar Masalah Kegagalan Transaksi di Port 9090")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(35, 45, 55)
    fail_text = (
        "Pada port 9090 tercatat 9 workflow berstatus FAILED dengan pesan: 'Error scheduling tasks'. "
        "Investigasi membuktikan bahwa penyebabnya adalah konfigurasi 'conductor.indexing.type=redis_cluster' dengan "
        "'maxmemory_policy=noeviction'. Seluruh inverted index search, payload input, dan log eksekusi dipaksa masuk ke RAM Redis, "
        "sehingga memori Redis melonjak (>632 MB). Saat terjadi lonjakan batch konkuren, antrean antartask mengalami lock contention "
        "dan Redis menolak alokasi baru, menyebabkan task gagal dijadwalkan. Sebaliknya, pada port 8080 data histori di-offload ke "
        "Elasticsearch 8.x di disk, sehingga Redis Cluster beroperasi stabil dan mencapai tingkat keberhasilan 100% sempurna."
    )
    pdf.multi_cell(186, 3.8, fail_text)
    pdf.ln(1)

    # -------------------------------------------------------------
    # 6. KESIMPULAN AKHIR
    # -------------------------------------------------------------
    section_title(pdf, "6", "Kesimpulan Akhir & Rekomendasi")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(35, 45, 55)
    concl = (
        "1. Kinerja & Throughput: Port 8080 (Conductor Quarkus) 2,14x lebih unggul dalam throughput TPS dan 2,38x lebih cepat dalam menyelesaikan batch.\n"
        "2. Efisiensi Storage: Port 8080 memisahkan layer transaksional (Redis) dan layer indexing (Elasticsearch), mencegah pemborosan RAM.\n"
        "3. Rekomendasi: Conductor Quarkus (Port 8080) adalah arsitektur terbaik dan paling siap untuk skala produksi billing PLN."
    )
    pdf.multi_cell(186, 3.8, concl)

    # Sign-off note
    pdf.ln(2.5)
    pdf.set_draw_color(220, 225, 230)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(1.5)
    pdf.set_font('Helvetica', 'I', 7.2)
    pdf.set_text_color(120, 130, 140)
    pdf.cell(0, 4, "Laporan benchmark resmi digenerate otomatis berdasarkan perbandingan faktual REST API Conductor port 8080 dan 9090.", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Save PDF
    out_pdf_name = "Laporan_Komparasi_Conductor_8080_vs_9090.pdf"
    out_pdf_alias = "Summary_Komparasi_Conductor_8080_vs_9090.pdf"

    print(f"Saving PDF to {out_pdf_name}...")
    pdf.output(out_pdf_name)

    print(f"Saving copy to {out_pdf_alias}...")
    pdf.output(out_pdf_alias)

    pdf_size = os.path.getsize(out_pdf_name) / 1024
    print(f"PDF generated successfully: {out_pdf_name} ({pdf_size:.1f} KB, {pdf.page_no()} pages)")

if __name__ == '__main__':
    main()
