

from pathlib import Path
from openpyxl import Workbook, load_workbook, worksheet


def open_excel_workbook(file_path: Path) -> Workbook:
    return load_workbook(file_path)

def get_worksheet(workbook: Workbook, sheet_name: str = None) -> worksheet:
    if sheet_name is None:
        return workbook.active
    else:
        return workbook[sheet_name]
    
def save_workbook(workbook: Workbook, file_path: Path):
    workbook.save(file_path)
    
def get_header_column_index(
    worksheet: worksheet, header_name: str, header_row_index: int = 1
) -> int | None:
    index = None
    
    for cell in worksheet[header_row_index]:
        if str(cell.value).strip().lower() == header_name.lower():
            index = cell.column
            
    return index
    
