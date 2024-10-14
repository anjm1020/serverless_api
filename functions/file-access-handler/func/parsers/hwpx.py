import zipfile

import lxml.etree as ET

from func.parsers.document_processor import DocumentProcessor


class HWPXProcessor(DocumentProcessor):
    def process(self, file_path):
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            if "Contents/section0.xml" in zip_ref.namelist():
                with zip_ref.open("Contents/section0.xml") as section_file:
                    tree = ET.parse(section_file)
                    root = tree.getroot()

                    text = ""
                    for elem in root.iter():
                        if elem.text:
                            text += elem.text.strip() + "\n"
                return text
            else:
                raise KeyError("section0.xml Not found in HWPX file.")
