import struct
import zlib

import olefile

from func.parsers.document_processor import DocumentProcessor


class HWPProcessor(DocumentProcessor):
    def process(self, file_path):
        f = olefile.OleFileIO(file_path)
        dirs = f.listdir()

        if ["FileHeader"] not in dirs or ["\x05HwpSummaryInformation"] not in dirs:
            raise Exception("Not Valid HWP.")

        header = f.openstream("FileHeader")
        header_data = header.read()
        is_compressed = (header_data[36] & 1) == 1

        nums = [int(d[1][len("Section") :]) for d in dirs if d[0] == "BodyText"]
        sections = ["BodyText/Section" + str(x) for x in sorted(nums)]

        text = ""
        for section in sections:
            bodytext = f.openstream(section)
            data = bodytext.read()
            if is_compressed:
                unpacked_data = zlib.decompress(data, -15)
            else:
                unpacked_data = data

            section_text = ""
            i = 0
            size = len(unpacked_data)
            while i < size:
                header = struct.unpack_from("<I", unpacked_data, i)[0]
                rec_type = header & 0x3FF
                rec_len = (header >> 20) & 0xFFF

                if rec_type in [67]:
                    rec_data = unpacked_data[i + 4 : i + 4 + rec_len]
                    section_text += rec_data.decode("utf-16")
                    section_text += "\n"

                i += 4 + rec_len

            text += section_text + "\n"
        return text
