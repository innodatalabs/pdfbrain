from ctypes import POINTER, cast, byref, c_double, c_uint16
import unicodedata
import pypdfium as pdfium
from .tools import lazyproperty


class PDFTextPage:
    def __init__(self, parent, ptr):
        self._parent = parent
        self._ptr = ptr

    @classmethod
    def load(cls, parent):
        ptr = pdfium.FPDFText_LoadPage(parent._ptr)
        if not ptr:
            raise RuntimeError('failed to load text')
        return cls(parent, ptr)

    def __del__(self):
        pdfium.FPDFText_ClosePage(self._ptr)

    def __len__(self):
        return pdfium.FPDFText_CountChars(self._ptr)

    def unicode(self, index):
        if not (0 <= index < len(self)):
            raise RuntimeError(f'Character index is out of bounds: {index}')

        return pdfium.FPDFText_GetUnicode(self._ptr, index)

    def bbox(self, index):
        if not (0 <= index < len(self)):
            raise RuntimeError(f'Character index is out of bounds: {index}')

        left, bottom, right, top = c_double(), c_double(), c_double(), c_double()
        rc = pdfium.FPDFText_GetCharBox(self._ptr, index,
            byref(left), byref(right), byref(bottom), byref(top))
        if not rc:
            raise RuntimeError(f'Failed to determine character bounds for {index}')

        return left.value, bottom.value, right.value, top.value

    def bboxes(self, index, count):
        if not (0 <= index < index + count <= len(self)):
            raise RuntimeError(f'Character span is out of bounds: {index}, {count}')

        howmany = pdfium.FPDFText_CountRects(self._ptr, index, count)
        for i in range(howmany):
            left, bottom, right, top = c_double(), c_double(), c_double(), c_double()
            pdfium.FPDFText_GetRect(self._ptr, i, byref(left), byref(top), byref(right), byref(bottom))
            yield left.value, bottom.value, right.value, top.value

    @lazyproperty
    def text(self):
        array_p = (c_uint16 * (len(self) + 1))()
        rc = pdfium.FPDFText_GetText(self._ptr, 0, len(self), cast(array_p, POINTER(c_uint16)))
        if not rc:
            raise RuntimeError('text extraction failed')

        txt = bytearray(array_p)[:2*rc-2].decode('utf-16le')
        return ''.join(c for c in txt if c in '\r\n' or unicodedata.category(c) not in ('Cc', 'Co', 'Cs', 'Cn'))

    def find(self, needle, start_index=0, match_case=False, match_whole_word=False):
        flags = 0
        if match_case:
            flags |= pdfium.FPDF_MATCHCASE
        if match_whole_word:
            flags |= pdfium.FPDF_MATCHWHOLEWORD

        needle = needle.encode('utf-16le') + b'\x00\x00'
        assert len(needle) % 2 == 0
        needle_ = cast(needle, POINTER(c_uint16))

        sch = pdfium.FPDFText_FindStart(self._ptr, needle_, flags, start_index)
        try:
            while pdfium.FPDFText_FindNext(sch):
                count = pdfium.FPDFText_GetSchCount(sch)
                index = pdfium.FPDFText_GetSchResultIndex(sch)
                yield tuple(self.bboxes(index, count))
        finally:
            pdfium.FPDFText_FindClose(sch)
