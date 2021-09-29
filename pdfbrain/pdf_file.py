import pypdfium as pdfium
from .tools import lazyproperty, get_error_message
from .pdf_page import PDFPage

# this line is very important, otherwise it won't work
pdfium.FPDF_InitLibraryWithConfig(pdfium.FPDF_LIBRARY_CONFIG(2, None, None, 0))


class PDFFile:
    def __init__(self, ptr):
        self._ptr = ptr

    @classmethod
    def load(cls, filename, password=None):
        ptr = pdfium.FPDF_LoadDocument(filename, password)
        if not ptr:
            err_message = get_error_message()
            raise RuntimeError(f'PDFFile.load: failed to load {filename}: {err_message}')
        return cls(ptr)

    def __del__(self):
        pdfium.FPDF_CloseDocument(self._ptr)

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

