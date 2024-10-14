from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P

from func.parsers.document_processor import DocumentProcessor


class DOCXProcessor(DocumentProcessor):
    def process(self, file_path: str) -> str:
        doc = Document(file_path)

        full_text = []

        for element in doc.element.body:
            if isinstance(element, CT_P):
                para_text = element.text if element.text else ""
                full_text.append(para_text)
            elif isinstance(element, CT_Tbl):
                for row in element.xpath(".//w:tr"):
                    row_text = "\t".join(
                        cell.text for cell in row.xpath(".//w:tc//w:p//w:t")
                    )
                    full_text.append(row_text)

        return "\n".join(full_text)
