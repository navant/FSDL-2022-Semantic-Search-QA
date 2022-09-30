import re
from io import StringIO
from typing import BinaryIO, List, cast

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.utils import FileOrName, open_filename


def pdf2text(pdf_file: FileOrName):
    # pdfminer Boilerplate
    rsrcmgr = PDFResourceManager()
    sio = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, sio, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Extract text
    with open_filename(pdf_file, "rb") as fp:
        fp = cast(BinaryIO, fp)
        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)

    # Get text from StringIO and remove nonprintable characters and trailing stuff
    text = sio.getvalue()
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]", "", text).rstrip()

    device.close()
    sio.close()

    return text


def chunk_text(text: str, chunk_len: int = 256, do_overlap: bool = False, overlap_size=15) -> List[str]:
    # Split text into smaller chunks
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + chunk_len])
        if do_overlap:
            i = i + chunk_len - overlap_size
        else:
            i = i + chunk_len
    return chunks


def remove_special_chars(text):
    """
    Remove newlines and tabs.

    Don't want to remove punctuation or case because it can convey sentiment or other contextual information.
    """
    text = text.split()
    text = " ".join(text)

    return text
