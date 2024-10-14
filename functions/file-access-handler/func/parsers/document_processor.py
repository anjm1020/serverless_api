from abc import ABC, abstractmethod


class DocumentProcessor(ABC):
    @abstractmethod
    def process(self, file_path: str) -> str:
        pass


class DocumentProcessorProxy(DocumentProcessor):
    def __init__(self):
        from func.parsers.docx import DOCXProcessor
        from func.parsers.hwp import HWPProcessor
        from func.parsers.hwpx import HWPXProcessor
        from func.parsers.pdf import PDFProcessor
        from func.parsers.pptx import PPTXProcessor

        self.__factory = {
            "docx": DOCXProcessor(),
            "hwp": HWPProcessor(),
            "hwpx": HWPXProcessor(),
            "pdf": PDFProcessor(),
            "pptx": PPTXProcessor(),
        }

    def process(self, file_path: str) -> str:
        ext = file_path.split(".")[-1]
        processor = self.__factory.get(ext)
        if processor:
            return processor.process(file_path)
        else:
            print(f"Unsupported file type: {ext}")
            return ""
