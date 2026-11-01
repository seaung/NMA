"""Excel 导入导出辅助"""
import io

from django.http import HttpResponse
from openpyxl import Workbook, load_workbook


def build_excel_response(headers: list, rows: list, filename: str) -> HttpResponse:
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def read_excel_rows(file_obj) -> list[dict]:
    wb = load_workbook(file_obj, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    header = [str(h).strip() if h is not None else "" for h in rows[0]]
    result = []
    for raw in rows[1:]:
        if all(cell is None for cell in raw):
            continue
        result.append({header[i]: raw[i] for i in range(min(len(header), len(raw)))})
    return result
