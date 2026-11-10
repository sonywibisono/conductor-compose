"""
Script to export Conductor execution results of workflow_normal to Excel (.xlsx / .xls).
Reference: http://localhost:8080/executions?workflowType=workflow_normal
"""

import sys
import os
import json
import urllib.request
from datetime import datetime, timezone, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

WIB = timezone(timedelta(hours=7))

def to_wib_str(iso_str):
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.astimezone(WIB).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(iso_str)

def parse_java_map(s):
    """
    Parses Java Map.toString() format:
    {key1=val1, key2={sub=val}, list=[a, b]}
    into native Python dicts, lists, and typed primitives.
    """
    if not s or not isinstance(s, str):
        return {} if not s else s
    s = s.strip()
    idx = 0
    n = len(s)

    def parse_value():
        nonlocal idx
        skip_ws()
        if idx >= n:
            return None
        if s[idx] == '{':
            return parse_dict()
        elif s[idx] == '[':
            return parse_list()
        else:
            return parse_primitive()

    def skip_ws():
        nonlocal idx
        while idx < n and s[idx] in ' \t\r\n':
            idx += 1

    def parse_dict():
        nonlocal idx
        if idx >= n or s[idx] != '{':
            return {}
        idx += 1
        d = {}
        skip_ws()
        if idx < n and s[idx] == '}':
            idx += 1
            return d
        while idx < n:
            skip_ws()
            start = idx
            while idx < n and s[idx] not in '=,}':
                idx += 1
            key = s[start:idx].strip()
            if idx < n and s[idx] == '=':
                idx += 1
                val = parse_value()
                if key:
                    d[key] = val
            else:
                if key:
                    d[key] = None
            skip_ws()
            if idx < n and s[idx] == ',':
                idx += 1
            elif idx < n and s[idx] == '}':
                idx += 1
                break
        return d

    def parse_list():
        nonlocal idx
        if idx >= n or s[idx] != '[':
            return []
        idx += 1
        l = []
        skip_ws()
        if idx < n and s[idx] == ']':
            idx += 1
            return l
        while idx < n:
            val = parse_value()
            l.append(val)
            skip_ws()
            if idx < n and s[idx] == ',':
                idx += 1
            elif idx < n and s[idx] == ']':
                idx += 1
                break
        return l

    def parse_primitive():
        nonlocal idx
        start = idx
        while idx < n and s[idx] not in ',}]':
            idx += 1
        raw_val = s[start:idx].strip()
        if raw_val == 'null':
            return None
        elif raw_val == 'true':
            return True
        elif raw_val == 'false':
            return False
        try:
            return int(raw_val)
        except ValueError:
            pass
        try:
            return float(raw_val)
        except ValueError:
            pass
        return raw_val

    return parse_value()

def format_cell(cell, value, is_header=False):
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    if is_header:
        cell.font = Font(name='Segoe UI', size=10, bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = Border(
            left=Side(style='thin', color='103352'),
            right=Side(style='thin', color='103352'),
            top=Side(style='thin', color='103352'),
            bottom=Side(style='medium', color='0F2439')
        )
    else:
        cell.font = Font(name='Segoe UI', size=9.5)
        cell.border = thin_border
        if isinstance(value, int):
            cell.number_format = '#,##0'
            cell.alignment = Alignment(horizontal='right', vertical='center')
        elif isinstance(value, float):
            cell.number_format = '#,##0.00'
            cell.alignment = Alignment(horizontal='right', vertical='center')
        else:
            cell.alignment = Alignment(horizontal='left', vertical='center')

def auto_fit_columns(ws, max_col_width=45, min_col_width=12):
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val = str(cell.value or '')
            if '\n' in val:
                lines = val.split('\n')
                line_len = max(len(l) for l in lines)
                max_len = max(max_len, line_len)
            else:
                max_len = max(max_len, len(val))
        width = min(max_col_width, max(min_col_width, max_len + 3))
        ws.column_dimensions[col_letter].width = width

def main():
    print("Fetching workflow_normal executions from Conductor API...")
    url = 'http://localhost:8080/api/workflow/search?query=workflowType%20IN%20(workflow_normal)&size=5000'
    req = urllib.request.urlopen(url)
    data = json.loads(req.read().decode('utf-8'))
    items = data.get('results', [])
    total_hits = data.get('totalHits', len(items))
    print(f"Total executions found: {total_hits} (received {len(items)})")

    records = []
    print("Parsing workflow inputs and outputs...")
    for idx, item in enumerate(items, 1):
        wfid = item.get('workflowId', '')
        status = item.get('status', '')
        start_wib = to_wib_str(item.get('startTime'))
        end_wib = to_wib_str(item.get('endTime'))
        exec_time = item.get('executionTime', 0)

        # Parse input
        raw_inp = item.get('input', '')
        parsed_inp = parse_java_map(raw_inp) if isinstance(raw_inp, str) else (raw_inp or {})
        inp_data = parsed_inp.get('data', {}) if isinstance(parsed_inp, dict) else {}

        # Parse output
        raw_out = item.get('output', '')
        parsed_out = parse_java_map(raw_out) if isinstance(raw_out, str) else (raw_out or {})

        out_main = parsed_out.get('output', {}) if isinstance(parsed_out, dict) else {}
        out_energi = parsed_out.get('output_energi', {}) if isinstance(parsed_out, dict) else {}

        # Flatten out_main
        flattened_out_main = {}
        if isinstance(out_main, dict):
            for k, v in out_main.items():
                if k == 'pascabayar' and isinstance(v, dict):
                    for subk, subv in v.items():
                        flattened_out_main[f"pasca_{subk}"] = subv
                elif k == 'stimulus' and isinstance(v, dict):
                    for subk, subv in v.items():
                        flattened_out_main[f"stimulus_{subk}"] = subv
                else:
                    flattened_out_main[k] = v

        records.append({
            'no': idx,
            'workflowId': wfid,
            'status': status,
            'startTimeWIB': start_wib,
            'endTimeWIB': end_wib,
            'executionTime': exec_time,
            'idpel': inp_data.get('idpel'),
            'thblrek': inp_data.get('thblrek'),
            'nama': inp_data.get('nama'),
            'tarif': inp_data.get('tarif'),
            'daya': inp_data.get('daya'),
            'unitup': inp_data.get('unitup'),
            'kdprosesklp': inp_data.get('kdprosesklp'),
            'out_main': flattened_out_main,
            'out_energi': out_energi if isinstance(out_energi, dict) else {}
        })

    print(f"Processed {len(records)} records. Building Excel workbook...")

    wb = openpyxl.Workbook()

    # Determine unique keys across all records
    all_out_keys = set()
    for r in records:
        all_out_keys.update(r['out_main'].keys())

    all_energi_keys = set()
    for r in records:
        all_energi_keys.update(r['out_energi'].keys())

    # Preferred human-friendly ordering for Billing Output
    ordered_out_keys = [
        # Pemakaian energi & jam nyala
        'pemkwh', 'pemkvarh', 'kwhlwbp', 'kwhwbp', 'jamnyala',
        # Rupiah pokok
        'rpptl', 'rpptl_bruto', 'rpptl_netto', 'rppln', 'rprek_bruto', 'rprek_netto',
        'rplwbp', 'rpwbp', 'rpblok3', 'rpkvarh', 'rpbeban',
        # Pajak & retribusi
        'prosenppj', 'rpppjptl', 'rpbpju', 'prosentase', 'rpppn', 'rpppn_r3', 'rpmat',
        # Angsuran & komponen lain
        'rpangsa', 'rpangsb', 'rpangsc', 'rpppjangsa', 'rpppjangsb', 'rpppjangsc',
        'rpinvoice', 'rpkompensasi', 'rpreduksi', 'rpdiskon',
        # Biaya keterlambatan
        'rpbk1', 'rpbk2', 'rpbk3',
        # DPP
        'dpp_ptl', 'dpp_opsel', 'dpp_rec', 'dpp_sewakap', 'dpp_sewatrafo', 'dpp_bptrafo', 'dpp_uap',
        # Biaya khusus & sewa
        'rpuap', 'rpopsel', 'rpsewakap', 'rpsewatrafo', 'rpsewatrafo_trafo', 'rpbptrafo', 'rpcapacity_plts',
        'rprec', 'jmlunitrec', 'hargarec',
        # Total Tagihan
        'rptag', 'rptag_bruto', 'rptag_netto', 'rptag_mat',
        # Pascabayar
        'pasca_rptag_billxx_awal', 'pasca_rptag_billxx_fnl', 'pasca_rpmaks_offset', 'pasca_rpoffset', 'pasca_rpsaldo_akhir',
        # Stimulus
        'stimulus_offset_rpptl', 'stimulus_offset_rpbpju', 'stimulus_offset_rpppn', 'stimulus_offset_rpmat',
        'stimulus_offset_rptagmat', 'stimulus_rpmaks_offset', 'stimulus_rpoffset', 'stimulus_rpsaldo_akhir',
        'stimulus_rptag_billxx_awal', 'stimulus_rptag_billxx_fnl', 'stimulus_offset_rpangsa', 'stimulus_offset_rpangsb',
        'stimulus_offset_rpangsc', 'stimulus_offset_rpsewakap', 'stimulus_offset_rpsewatrafo', 'stimulus_offset_rpbptrafo',
        # Parameter
        'subWorkflowId', 'blok3', 'kelbkvarh', 'rpmaks_offset', 'rpoffset', 'rpsaldo_akhir',
        'value_a', 'value_b',
        'rpppn_bptrafo', 'rpppn_capacity_plts', 'rpppn_opspararel', 'rpppn_rec', 'rpppn_sewakap', 'rpppn_sewatrafo', 'rpppn_uap'
    ]
    # Add any remaining keys
    for k in sorted(all_out_keys):
        if k not in ordered_out_keys:
            ordered_out_keys.append(k)

    # Preferred human-friendly ordering for Energi Output
    ordered_energi_keys = [
        # Hari & Beban
        'haripakai', 'haripakai_bulan', 'haribeban', 'haribeban_bulan',
        # Jam Nyala & Fraksi
        'jamnyala', 'jamnyala_real', 'fraksikwh', 'fraksibeban', 'fraksiemin', 'batas_emin', 'emin_rm_plts',
        # Pemakaian KWh
        'pemkwh', 'pemkwh_reg', 'pemkwh_real', 'kwhlwbp', 'kwhlwbp_reg', 'kwhlwbp_real',
        'kwhwbp', 'kwhwbp_reg', 'kwhwbp_real', 'kwhmin_emin_reg', 'kwhblok3_reg', 'kwhblok3_real',
        'pemkvarh', 'kvarhpakai_real', 'kvarhlebih', 'kelbkvarh', 'blok3',
        # Tarif Satuan
        'trflwbp_reg', 'trflwbp_tdl', 'trfwbp_reg', 'trfwbp_tdl', 'trfkvarh', 'trfbeban', 'trfblok3',
        # Hasil Rupiah Energi
        'rpptl', 'rplwbp', 'rplwbp_reg', 'rplwbp_param', 'rpwbp', 'rpwbp_reg', 'rpwbp_param',
        'rpkwh_reg', 'rpkvarh', 'rpkvarh_param', 'rpblok3', 'rpblok3_reg', 'rpbeban', 'rprekmin',
        # PLTS / Ekspor Impor
        'kapasitas_plts_atap', 'kwhlwbp_import', 'kwhlwbp_export', 'kwhlwbp_net', 'kwhlwbp_offset', 'kwhlwbp_pot_offset',
        'kwhwbp_import', 'kwhwbp_export', 'pemkwh_import', 'pemkwh_export', 'pemkvarh_import', 'pemkvarh_export',
        'kwh_saldoawal_plts', 'kwh_tambah_plts', 'kwh_kurang_plts', 'kwh_saldoakhir_plts', 'blok3_import', 'blok3_export',
        # Premium
        'trflwbp_premium', 'trfwbp_premium', 'pemkwh_premium', 'kwhlwbp_premium', 'kwhwbp_premium', 'kwhmin_emin_premium',
        'rplwbp_premium', 'rpwbp_premium', 'rpkwh_premium',
        # Sub Workflow
        'subWorkflowId'
    ]
    for k in sorted(all_energi_keys):
        if k not in ordered_energi_keys:
            ordered_energi_keys.append(k)

    # -------------------------------------------------------------
    # SHEET 1: Output Billing (Utama)
    # -------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Output Billing (Utama)"
    ws1.views.sheetView[0].showGridLines = True

    headers1 = [
        "No", "Workflow ID", "IDPEL", "THBLREK", "Nama Pelanggan", "Tarif", "Daya", "Status",
        "Waktu Mulai (WIB)", "Waktu Selesai (WIB)", "Durasi (ms)"
    ] + ordered_out_keys

    ws1.append(headers1)
    ws1.row_dimensions[1].height = 28
    for col_idx in range(1, len(headers1) + 1):
        cell = ws1.cell(row=1, column=col_idx)
        format_cell(cell, cell.value, is_header=True)

    zebra_fill = PatternFill(start_color='F9FAFB', end_color='F9FAFB', fill_type='solid')

    for r in records:
        row_vals = [
            r['no'], r['workflowId'], str(r['idpel'] or ''), str(r['thblrek'] or ''),
            str(r['nama'] or ''), str(r['tarif'] or ''), r['daya'], r['status'],
            r['startTimeWIB'], r['endTimeWIB'], r['executionTime']
        ]
        for k in ordered_out_keys:
            row_vals.append(r['out_main'].get(k))
        ws1.append(row_vals)

        row_idx = ws1.max_row
        ws1.row_dimensions[row_idx].height = 20
        use_zebra = (r['no'] % 2 == 0)
        for c_idx in range(1, len(row_vals) + 1):
            cell = ws1.cell(row=row_idx, column=c_idx)
            format_cell(cell, cell.value, is_header=False)
            if use_zebra:
                cell.fill = zebra_fill

    ws1.freeze_panes = "D2"
    ws1.auto_filter.ref = ws1.dimensions
    auto_fit_columns(ws1)

    # -------------------------------------------------------------
    # SHEET 2: Output Energi (Detail)
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="Output Energi (Detail)")
    ws2.views.sheetView[0].showGridLines = True

    headers2 = [
        "No", "Workflow ID", "IDPEL", "THBLREK", "Tarif", "Daya", "Status"
    ] + ordered_energi_keys

    ws2.append(headers2)
    ws2.row_dimensions[1].height = 28
    for col_idx in range(1, len(headers2) + 1):
        cell = ws2.cell(row=1, column=col_idx)
        format_cell(cell, cell.value, is_header=True)

    for r in records:
        row_vals = [
            r['no'], r['workflowId'], str(r['idpel'] or ''), str(r['thblrek'] or ''),
            str(r['tarif'] or ''), r['daya'], r['status']
        ]
        for k in ordered_energi_keys:
            row_vals.append(r['out_energi'].get(k))
        ws2.append(row_vals)

        row_idx = ws2.max_row
        ws2.row_dimensions[row_idx].height = 20
        use_zebra = (r['no'] % 2 == 0)
        for c_idx in range(1, len(row_vals) + 1):
            cell = ws2.cell(row=row_idx, column=c_idx)
            format_cell(cell, cell.value, is_header=False)
            if use_zebra:
                cell.fill = zebra_fill

    ws2.freeze_panes = "D2"
    ws2.auto_filter.ref = ws2.dimensions
    auto_fit_columns(ws2)

    # -------------------------------------------------------------
    # SHEET 3: Output Gabungan (All Fields)
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title="Output Gabungan (All Fields)")
    ws3.views.sheetView[0].showGridLines = True

    combined_out_headers = [f"billing_{k}" for k in ordered_out_keys]
    combined_energi_headers = [f"energi_{k}" for k in ordered_energi_keys]

    headers3 = [
        "No", "Workflow ID", "IDPEL", "THBLREK", "Nama", "Tarif", "Daya", "Status"
    ] + combined_out_headers + combined_energi_headers

    ws3.append(headers3)
    ws3.row_dimensions[1].height = 28
    for col_idx in range(1, len(headers3) + 1):
        cell = ws3.cell(row=1, column=col_idx)
        format_cell(cell, cell.value, is_header=True)

    for r in records:
        row_vals = [
            r['no'], r['workflowId'], str(r['idpel'] or ''), str(r['thblrek'] or ''),
            str(r['nama'] or ''), str(r['tarif'] or ''), r['daya'], r['status']
        ]
        for k in ordered_out_keys:
            row_vals.append(r['out_main'].get(k))
        for k in ordered_energi_keys:
            row_vals.append(r['out_energi'].get(k))
        ws3.append(row_vals)

        row_idx = ws3.max_row
        ws3.row_dimensions[row_idx].height = 20
        use_zebra = (r['no'] % 2 == 0)
        for c_idx in range(1, len(row_vals) + 1):
            cell = ws3.cell(row=row_idx, column=c_idx)
            format_cell(cell, cell.value, is_header=False)
            if use_zebra:
                cell.fill = zebra_fill

    ws3.freeze_panes = "C2"
    ws3.auto_filter.ref = ws3.dimensions
    auto_fit_columns(ws3)

    # -------------------------------------------------------------
    # SHEET 4: Output Murni (Pure Output Saja)
    # -------------------------------------------------------------
    ws4 = wb.create_sheet(title="Output Murni (Hanya Output)")
    ws4.views.sheetView[0].showGridLines = True

    headers4 = ["No", "Workflow ID"] + ordered_out_keys

    ws4.append(headers4)
    ws4.row_dimensions[1].height = 28
    for col_idx in range(1, len(headers4) + 1):
        cell = ws4.cell(row=1, column=col_idx)
        format_cell(cell, cell.value, is_header=True)

    for r in records:
        row_vals = [r['no'], r['workflowId']]
        for k in ordered_out_keys:
            row_vals.append(r['out_main'].get(k))
        ws4.append(row_vals)

        row_idx = ws4.max_row
        ws4.row_dimensions[row_idx].height = 20
        use_zebra = (r['no'] % 2 == 0)
        for c_idx in range(1, len(row_vals) + 1):
            cell = ws4.cell(row=row_idx, column=c_idx)
            format_cell(cell, cell.value, is_header=False)
            if use_zebra:
                cell.fill = zebra_fill

    ws4.freeze_panes = "C2"
    ws4.auto_filter.ref = ws4.dimensions
    auto_fit_columns(ws4)

    # Save to file
    out_xlsx_path = "hasil_eksekusi_workflow_normal_output.xlsx"
    out_xls_path = "hasil_eksekusi_workflow_normal_output.xls"

    print(f"Saving workbook to {out_xlsx_path}...")
    wb.save(out_xlsx_path)
    print(f"Saving copy to {out_xls_path}...")
    wb.save(out_xls_path)

    xlsx_size = os.path.getsize(out_xlsx_path) / (1024 * 1024)
    print(f"Export completed successfully!")
    print(f"File 1: {out_xlsx_path} ({xlsx_size:.2f} MB)")
    print(f"File 2: {out_xls_path} ({xlsx_size:.2f} MB)")
    print(f"Total Rows exported: {len(records)}")
    print(f"Sheets created: {[s.title for s in wb.worksheets]}")

if __name__ == '__main__':
    main()
