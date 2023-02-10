import pypdfium2 as pdfium
import sys
from .tools import lazyproperty, get_error_message
from .pdf_page import PDFPage
import weakref

# this line is very important, otherwise it won't work
pdfium.FPDF_InitLibraryWithConfig(pdfium.FPDF_LIBRARY_CONFIG(2, None, None, 0))


def _close_file(fileref):
    file = fileref()
    if file:
        file.close()

class PDFFile:
    def __init__(self, ptr, filename):
        self._ptr = ptr
        self.filename = filename
        weakref.finalize(self, _close_file, weakref.ref(self))

    @classmethod
    def load(cls, filename, password=None):
        ptr = pdfium.FPDF_LoadDocument(filename, password)
        if not ptr:
            err_message = get_error_message()
            raise RuntimeError(f'PDFFile.load: failed to load {filename}: {err_message}')
        return cls(ptr, filename)

    def close(self):
        if self._ptr:
            pdfium.FPDF_CloseDocument(self._ptr)
            self._ptr = None

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    @lazyproperty
    def numpages(self):
        return pdfium.FPDF_GetPageCount(self._ptr)

    def __len__(self):
        return self.numpages

    def __getitem__(self, pageno):
        return PDFPage.load(self, pageno)

    def __iter__(self):
        for pageno in range (len(self)):
            yield self[pageno]

