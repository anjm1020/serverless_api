from func.parsers.document_processor import DocumentProcessorProxy


def extract_text_from_file(file_path):
    processor = DocumentProcessorProxy()
    text = processor.process(file_path)
    # Version of if embedding server doesn't support chunking
    chunks = _split_text(text)
    return [_minimize_newlines(chunk) for chunk in chunks]

    # Version of if embedding server supports chunking
    # return _minimize_newlines(text)


def _minimize_newlines(text):
    lines = text.splitlines()
    minimized_text = [line.strip() for line in lines if line.strip()]
    return " ".join(minimized_text)


def _split_text(text, max_length=1024, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_length, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start += max_length - overlap

    return chunks
