import PyPDF2

from func.parsers.document_processor import DocumentProcessor


class PDFProcessor(DocumentProcessor):
    def process(self, file_path):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
