"""
Export workflow_normal executions for TODAY (2026-11-10) to Excel (.xlsx / .xls),
and perform comparison with YESTERDAY (2026-11-09) on matching (idpel, thblrek).
"""

import os
import json
import urllib.request
from datetime import datetime, timezone, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from export_workflow_normal_xls import parse_java_map, to_wib_str, format_cell, auto_fit_columns, WIB

def main():
    print("Fetching workflow_normal executions from Conductor API...")
    url = 'http://localhost:8080/api/workflow/search?query=workflowType%20IN%20(workflow_normal)&size=5000'
    req = urllib.request.urlopen(url)
    data = json.loads(req.read().decode('utf-8'))
    items = data.get('results', [])
    print(f"Total search items: {len(items)}")

    today_records = []
    yesterday_map = {}

    for it in items:
        st = it.get('startTime')
        if not st:
            continue
        dt = datetime.fromisoformat(st.replace('Z', '+00:00')).astimezone(WIB)
        d_str = dt.strftime('%Y-%m-%d')
        if d_str not in ('2026-11-10', '2026-11-09'):
            continue

        wfid = it.get('workflowId', '')
        status = it.get('status', '')
        start_wib = to_wib_str(st)
        end_wib = to_wib_str(it.get('endTime'))
        exec_time = it.get('executionTime', 0)

        # Parse input
        raw_inp = it.get('input', '')
        parsed_inp = parse_java_map(raw_inp) if isinstance(raw_inp, str) else (raw_inp or {})
        inp_data = parsed_inp.get('data', {}) if isinstance(parsed_inp, dict) else {}

        # Parse output
        raw_out = it.get('output', '')
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

        idpel = str(inp_data.get('idpel') or '')
        thblrek = str(inp_data.get('thblrek') or '')
        key = (idpel, thblrek)

        rec = {
            'workflowId': wfid,
            'status': status,
            'startTimeWIB': start_wib,
            'endTimeWIB': end_wib,
            'executionTime': exec_time,
            'idpel': idpel,
            'thblrek': thblrek,
            'nama': inp_data.get('nama', ''),
            'tarif': inp_data.get('tarif', ''),
            'daya': inp_data.get('daya', 0),
            'unitup': inp_data.get('unitup', ''),
            'kdprosesklp': inp_data.get('kdprosesklp', ''),
            'out_main': flattened_out_main,
            'out_energi': out_energi if isinstance(out_energi, dict) else {}
        }

        if d_str == '2026-11-10':
            today_records.append(rec)
        elif d_str == '2026-11-09':
            yesterday_map[key] = rec

    print(f"Today (2026-11-10) records: {len(today_records)}")
    print(f"Yesterday (2026-11-09) records: {len(yesterday_map)}")

    # Sort today records by idpel
    today_records.sort(key=lambda x: (x['idpel'], x['thblrek']))
    for idx, r in enumerate(today_records, 1):
        r['no'] = idx

    # Determine unique keys across today records
    all_out_keys = set()
    for r in today_records:
        all_out_keys.update(r['out_main'].keys())

    all_energi_keys = set()
    for r in today_records:
        all_energi_keys.update(r['out_energi'].keys())

    ordered_out_keys = [
        'pemkwh', 'pemkvarh', 'kwhlwbp', 'kwhwbp', 'jamnyala',
        'rpptl', 'rpptl_bruto', 'rpptl_netto', 'rppln', 'rprek_bruto', 'rprek_netto',
        'rplwbp', 'rpwbp', 'rpblok3', 'rpkvarh', 'rpbeban',
        'prosenppj', 'rpppjptl', 'rpbpju', 'prosentase', 'rpppn', 'rpppn_r3', 'rpmat',
        'rpangsa', 'rpangsb', 'rpangsc', 'rpppjangsa', 'rpppjangsb', 'rpppjangsc',
        'rpinvoice', 'rpkompensasi', 'rpreduksi', 'rpdiskon',
        'rpbk1', 'rpbk2', 'rpbk3',
        'dpp_ptl', 'dpp_opsel', 'dpp_rec', 'dpp_sewakap', 'dpp_sewatrafo', 'dpp_bptrafo', 'dpp_uap',
        'rpuap', 'rpopsel', 'rpsewakap', 'rpsewatrafo', 'rpsewatrafo_trafo', 'rpbptrafo', 'rpcapacity_plts',
        'rprec', 'jmlunitrec', 'hargarec',
        'rptag', 'rptag_bruto', 'rptag_netto', 'rptag_mat',
        'pasca_rptag_billxx_awal', 'pasca_rptag_billxx_fnl', 'pasca_rpmaks_offset', 'pasca_rpoffset', 'pasca_rpsaldo_akhir',
        'stimulus_offset_rpptl', 'stimulus_offset_rpbpju', 'stimulus_offset_rpppn', 'stimulus_offset_rpmat',
        'stimulus_offset_rptagmat', 'stimulus_rpmaks_offset', 'stimulus_rpoffset', 'stimulus_rpsaldo_akhir',
        'stimulus_rptag_billxx_awal', 'stimulus_rptag_billxx_fnl', 'stimulus_offset_rpangsa', 'stimulus_offset_rpangsb',
        'stimulus_offset_rpangsc', 'stimulus_offset_rpsewakap', 'stimulus_offset_rpsewatrafo', 'stimulus_offset_rpbptrafo',
        'subWorkflowId', 'blok3', 'kelbkvarh', 'rpmaks_offset', 'rpoffset', 'rpsaldo_akhir',
        'value_a', 'value_b',
        'rpppn_bptrafo', 'rpppn_capacity_plts', 'rpppn_opspararel', 'rpppn_rec', 'rpppn_sewakap', 'rpppn_sewatrafo', 'rpppn_uap'
    ]
    for k in sorted(all_out_keys):
        if k not in ordered_out_keys:
            ordered_out_keys.append(k)

    ordered_energi_keys = [
        'haripakai', 'haripakai_bulan', 'haribeban', 'haribeban_bulan',
        'jamnyala', 'jamnyala_real', 'fraksikwh', 'fraksibeban', 'fraksiemin', 'batas_emin', 'emin_rm_plts',
        'pemkwh', 'pemkwh_reg', 'pemkwh_real', 'kwhlwbp', 'kwhlwbp_reg', 'kwhlwbp_real',
        'kwhwbp', 'kwhwbp_reg', 'kwhwbp_real', 'kwhmin_emin_reg', 'kwhblok3_reg', 'kwhblok3_real',
        'pemkvarh', 'kvarhpakai_real', 'kvarhlebih', 'kelbkvarh', 'blok3',
        'trflwbp_reg', 'trflwbp_tdl', 'trfwbp_reg', 'trfwbp_tdl', 'trfkvarh', 'trfbeban', 'trfblok3',
        'rpptl', 'rplwbp', 'rplwbp_reg', 'rplwbp_param', 'rpwbp', 'rpwbp_reg', 'rpwbp_param',
        'rpkwh_reg', 'rpkvarh', 'rpkvarh_param', 'rpblok3', 'rpblok3_reg', 'rpbeban', 'rprekmin',
        'kapasitas_plts_atap', 'kwhlwbp_import', 'kwhlwbp_export', 'kwhlwbp_net', 'kwhlwbp_offset', 'kwhlwbp_pot_offset',
        'kwhwbp_import', 'kwhwbp_export', 'pemkwh_import', 'pemkwh_export', 'pemkvarh_import', 'pemkvarh_export',
        'kwh_saldoawal_plts', 'kwh_tambah_plts', 'kwh_kurang_plts', 'kwh_saldoakhir_plts', 'blok3_import', 'blok3_export',
        'trflwbp_premium', 'trfwbp_premium', 'pemkwh_premium', 'kwhlwbp_premium', 'kwhwbp_premium', 'kwhmin_emin_premium',
        'rplwbp_premium', 'rpwbp_premium', 'rpkwh_premium',
        'subWorkflowId'
    ]
    for k in sorted(all_energi_keys):
        if k not in ordered_energi_keys:
            ordered_energi_keys.append(k)

    wb = openpyxl.Workbook()
    zebra_fill = PatternFill(start_color='F9FAFB', end_color='F9FAFB', fill_type='solid')

    # -------------------------------------------------------------
    # SHEET 1: Output Billing (Hari Ini)
    # -------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Output Billing (Hari Ini)"
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

    for r in today_records:
        row_vals = [
            r['no'], r['workflowId'], r['idpel'], r['thblrek'],
            r['nama'], r['tarif'], r['daya'], r['status'],
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
    # SHEET 2: Output Energi (Hari Ini)
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="Output Energi (Hari Ini)")
    ws2.views.sheetView[0].showGridLines = True

    headers2 = [
        "No", "Workflow ID", "IDPEL", "THBLREK", "Tarif", "Daya", "Status"
    ] + ordered_energi_keys

    ws2.append(headers2)
    ws2.row_dimensions[1].height = 28
    for col_idx in range(1, len(headers2) + 1):
        cell = ws2.cell(row=1, column=col_idx)
        format_cell(cell, cell.value, is_header=True)

    for r in today_records:
        row_vals = [
            r['no'], r['workflowId'], r['idpel'], r['thblrek'],
            r['tarif'], r['daya'], r['status']
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
    # SHEET 3: Output Gabungan (Hari Ini)
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title="Output Gabungan (Hari Ini)")
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

    for r in today_records:
        row_vals = [
            r['no'], r['workflowId'], r['idpel'], r['thblrek'],
            r['nama'], r['tarif'], r['daya'], r['status']
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
    # SHEET 4: Output Murni (Hari Ini)
    # -------------------------------------------------------------
    ws4 = wb.create_sheet(title="Output Murni (Hari Ini)")
    ws4.views.sheetView[0].showGridLines = True

    headers4 = ["No", "Workflow ID"] + ordered_out_keys
    ws4.append(headers4)
    ws4.row_dimensions[1].height = 28
    for col_idx in range(1, len(headers4) + 1):
        cell = ws4.cell(row=1, column=col_idx)
        format_cell(cell, cell.value, is_header=True)

    for r in today_records:
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

    # -------------------------------------------------------------
    # SHEET 5: Komparasi Hari Ini vs Kemarin
    # -------------------------------------------------------------
    ws5 = wb.create_sheet(title="Komparasi Hari Ini vs Kemarin")
    ws5.views.sheetView[0].showGridLines = True

    headers5 = [
        "No", "IDPEL", "THBLREK", "Nama Pelanggan", "Tarif", "Daya",
        "Workflow ID (Hari Ini)", "Workflow ID (Kemarin)",
        "Durasi Hari Ini (detik)", "Durasi Kemarin (detik)",
        "pemkwh (Hari Ini)", "pemkwh (Kemarin)", "Selisih pemkwh",
        "rpptl (Hari Ini)", "rpptl (Kemarin)", "Selisih rpptl",
        "rpbpju (Hari Ini)", "rpbpju (Kemarin)", "Selisih rpbpju",
        "rpppn (Hari Ini)", "rpppn (Kemarin)", "Selisih rpppn",
        "rpmat (Hari Ini)", "rpmat (Kemarin)", "Selisih rpmat",
        "rptag (Hari Ini)", "rptag (Kemarin)", "Selisih rptag",
        "Status Komparasi Output"
    ]
    ws5.append(headers5)
    ws5.row_dimensions[1].height = 28
    for col_idx in range(1, len(headers5) + 1):
        cell = ws5.cell(row=1, column=col_idx)
        format_cell(cell, cell.value, is_header=True)

    identical_fill = PatternFill(start_color='E2F0D9', end_color='E2F0D9', fill_type='solid') # soft green

    for r in today_records:
        key = (r['idpel'], r['thblrek'])
        y = yesterday_map.get(key)
        if not y:
            status_comp = "Data Kemarin Tidak Ada"
            y_wfid = "-"
            y_dur = 0
            y_pemkwh = y_rpptl = y_rpbpju = y_rpppn = y_rpmat = y_rptag = 0
        else:
            y_wfid = y['workflowId']
            y_dur = round(y['executionTime'] / 1000.0, 2)
            y_out = y['out_main']
            y_pemkwh = y_out.get('pemkwh', 0) or 0
            y_rpptl = y_out.get('rpptl', 0) or 0
            y_rpbpju = y_out.get('rpbpju', 0) or 0
            y_rpppn = y_out.get('rpppn', 0) or 0
            y_rpmat = y_out.get('rpmat', 0) or 0
            y_rptag = y_out.get('rptag', 0) or 0

        t_out = r['out_main']
        t_pemkwh = t_out.get('pemkwh', 0) or 0
        t_rpptl = t_out.get('rpptl', 0) or 0
        t_rpbpju = t_out.get('rpbpju', 0) or 0
        t_rpppn = t_out.get('rpppn', 0) or 0
        t_rpmat = t_out.get('rpmat', 0) or 0
        t_rptag = t_out.get('rptag', 0) or 0
        t_dur = round(r['executionTime'] / 1000.0, 2)

        diff_pemkwh = t_pemkwh - y_pemkwh
        diff_rpptl = t_rpptl - y_rpptl
        diff_rpbpju = t_rpbpju - y_rpbpju
        diff_rpppn = t_rpppn - y_rpppn
        diff_rpmat = t_rpmat - y_rpmat
        diff_rptag = t_rptag - y_rptag

        all_diff_zero = (diff_pemkwh == 0 and diff_rpptl == 0 and diff_rpbpju == 0 and
                         diff_rpppn == 0 and diff_rpmat == 0 and diff_rptag == 0)
        status_comp = "100% Identik (Sama)" if all_diff_zero else "Ada Perbedaan"

        row_vals = [
            r['no'], r['idpel'], r['thblrek'], r['nama'], r['tarif'], r['daya'],
            r['workflowId'], y_wfid,
            t_dur, y_dur,
            t_pemkwh, y_pemkwh, diff_pemkwh,
            t_rpptl, y_rpptl, diff_rpptl,
            t_rpbpju, y_rpbpju, diff_rpbpju,
            t_rpppn, y_rpppn, diff_rpppn,
            t_rpmat, y_rpmat, diff_rpmat,
            t_rptag, y_rptag, diff_rptag,
            status_comp
        ]
        ws5.append(row_vals)

        row_idx = ws5.max_row
        ws5.row_dimensions[row_idx].height = 20
        use_zebra = (r['no'] % 2 == 0)
        for c_idx in range(1, len(row_vals) + 1):
            cell = ws5.cell(row=row_idx, column=c_idx)
            format_cell(cell, cell.value, is_header=False)
            if c_idx == len(row_vals) and status_comp == "100% Identik (Sama)":
                cell.fill = identical_fill
                cell.font = Font(name='Segoe UI', size=9.5, bold=True, color='276A3C')
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif use_zebra:
                cell.fill = zebra_fill

    ws5.freeze_panes = "D2"
    ws5.auto_filter.ref = ws5.dimensions
    auto_fit_columns(ws5)

    # Save files
    out_xlsx_path = "hasil_eksekusi_workflow_normal_hari_ini_20261110.xlsx"
    out_xls_path = "hasil_eksekusi_workflow_normal_hari_ini_20261110.xls"

    print(f"Saving workbook to {out_xlsx_path}...")
    wb.save(out_xlsx_path)
    print(f"Saving copy to {out_xls_path}...")
    wb.save(out_xls_path)

    xlsx_size = os.path.getsize(out_xlsx_path) / (1024 * 1024)
    print("Done!")
    print(f"Generated: {out_xlsx_path} ({xlsx_size:.2f} MB)")
    print(f"Generated: {out_xls_path} ({xlsx_size:.2f} MB)")
    print(f"Sheets: {[s.title for s in wb.worksheets]}")

if __name__ == '__main__':
    main()
