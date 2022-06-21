from PIL import Image
from ctypes import c_float, byref, create_string_buffer, cast, POINTER, c_ubyte
import pypdfium2 as pdfium
from .tools import lazyproperty, get_error_message
from .pdf_text_page import PDFTextPage
import weakref


def _close_page(pageref):
    page = pageref()
    if page:
        page.close()

class PDFPage:
    def __init__(self, parent, ptr, pageno):
        self._parent = parent
        self._ptr = ptr
        self._pageno = pageno
        weakref.finalize(self, _close_page, weakref.ref(self))

    def close(self):
        if self._ptr:
            pdfium.FPDF_ClosePage(self._ptr)
            self._ptr = None

    @classmethod
    def load(cls, doc, pageno):
        if not (0 <= pageno < doc.numpages):
            raise RuntimeError(f'Page number {pageno} is out of bounds')

        ptr = pdfium.FPDF_LoadPage(doc._ptr, pageno)
        if not ptr:
            err_message = get_error_message()
            raise RuntimeError(f'PDFPage.load: failed to load page {pageno}: {err_message}')

        return cls(doc, ptr, pageno)

    @lazyproperty
    def width(self):
        return pdfium.FPDF_GetPageWidthF(self._ptr)

    @lazyproperty
    def height(self):
        return pdfium.FPDF_GetPageHeightF(self._ptr)

    # @property
    # def bbox(self):
    #     rect = FPDF_RECT(0., 0., 0., 0.)
    #     if not so.FPDF_GetPageBoundingBox(self._page, pointer(rect)):
    #         err = so.RED_LastError()
    #         raise RuntimeError('internal error: %s' % err)
    #     return rect.left, rect.top, rect.right, rect.bottom

    @lazyproperty
    def crop_box(self):
        '''Page crop box.'''
        left, bottom, right, top = c_float(), c_float(), c_float(), c_float()

        mediabox = self.media_box
        rc = pdfium.FPDFPage_GetCropBox(self._ptr,
            byref(left), byref(bottom), byref(right), byref(top))
        if rc:
            cropbox = left.value, bottom.value, right.value, top.value
        else:
            cropbox = mediabox

        x0 = max(cropbox[0], mediabox[0])
        x1 = min(cropbox[2], mediabox[2])
        y0 = max(cropbox[1], mediabox[1])
        y1 = min(cropbox[3], mediabox[3])

        assert x0 < x1 and y0 < y1

        return x0, y0, x1, y1

    @lazyproperty
    def media_box(self):
        '''Page media box.'''
        left, bottom, right, top = c_float(), c_float(), c_float(), c_float()

        rc = pdfium.FPDFPage_GetMediaBox(self._ptr,
            byref(left), byref(bottom), byref(right), byref(top))
        if not rc:
            return (0, 0, 612, 792)

        return left.value, bottom.value, right.value, top.value

    @lazyproperty
    def rotation(self):
        '''Page rotation.

        * 0 - no rotation
        * 1 - rotated 90 degrees clock-wise
        * 2 - rotated 180 degrees clock-wise
        * 3 - rotated 270 degrees clock-wise
        '''
        return pdfium.FPDFPage_GetRotation(self._ptr)

    @lazyproperty
    def label(self):
        '''Page label.'''
        out = create_string_buffer(4096)
        l = pdfium.FPDF_GetPageLabel(self._parent._ptr, self._pageno + 1, out, 4096)
        if l < 4:
            return ''
        return out.raw[:l-2].decode('utf-16le')

    @staticmethod
    def _get_matrix(rotation, crop_box, rect, scale):
        '''PDFium renderer "conveniently" auto-rotates according to page.rotation value.
        We want to render page in native coordinate system (so that we can, for example,
        use word box coordinates to render the word). Hence we have to undo the "clever"
        transform that PDFium engine applies.
        '''
        cx0, cy0, cx1, cy1 = crop_box
        x0, y0, x1, y1 = rect
        #
        if rotation == 0:
            matrix = (scale, 0., 0., scale, (cx0-x0) * scale, (y1-cy1) * scale)
        elif rotation == 1:
            matrix = (0., -scale, scale, 0., (cx0-x0) * scale, (y1-cy0) * scale)
        elif rotation == 2:
            matrix = (-scale, 0., 0., -scale, (cx1-x0) * scale, (y1-cy0) * scale)
        elif rotation == 3:
            matrix = (0., scale, -scale, 0., (cx1-x0) * scale, (y1-cy1) * scale)
        else:
            raise RuntimeError('Unexpected rotation value: %s' % rotation)
        return matrix

    def render(self, scale=1.0, rect=None, optimize_for_lcd=False, grayscale=False, annot=False):
        '''Render page (or rectangle on the page) to memory (the pixel format is BGRx)

        Args:
            scale (float):      scale to use (default is 1.0, which will assume that 1pt takes 1px)
            rect (tuple):       optional rectangle to render. Value is a 4-tuple of (x0, y0, x1, y1) in PDF coordinates.
                                if None, then page's :attr:`crop_box` will be used for rendering.
        '''
        x0, y0, x1, y1 = self.crop_box if rect is None else rect
        matrix = pdfium.FS_MATRIX(*self._get_matrix(self.rotation, self.crop_box, (x0, y0, x1, y1), scale))

        width = int((x1 - x0) * scale + 0.5)
        height = int((y1 - y0) * scale + 0.5)
        cropper = pdfium.FS_RECTF(0, 0, width, height)

        bitmap = pdfium.FPDFBitmap_Create(width, height, 0)
        pdfium.FPDFBitmap_FillRect(bitmap, 0, 0, width, height, 0xFFFFFFFF)
        # pdfium.FPDF_RenderPageBitmapWithMatrix(bitmap, self._ptr, matrix, cropper, pdfium.FPDF_LCD_TEXT | pdfium.FPDF_ANNOT)
        options = 0
        if optimize_for_lcd:
            options |= pdfium.FPDF_LCD_TEXT
        if grayscale:
            options |= pdfium.FPDF_GRAYSCALE
        if annot:
            options |= pdfium.FPDF_ANNOT
        pdfium.FPDF_RenderPageBitmapWithMatrix(bitmap, self._ptr, matrix, cropper, options)

        # retrieve data from bitmap
        buffer = pdfium.FPDFBitmap_GetBuffer(bitmap)
        buffer_ = cast(buffer, POINTER(c_ubyte * (width * height * 4)))
        img = Image.frombuffer("RGBA", (width, height), buffer_.contents, "raw", "BGRA", 0, 1)
        pdfium.FPDFBitmap_Destroy(bitmap)
        return img

    def text_page(self):
        return PDFTextPage.load(self)
