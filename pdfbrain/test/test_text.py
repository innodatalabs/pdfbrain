from pdfbrain import PDFFile
from . import res

def test_text():
    pagen1 = PDFFile.load(res('bug001.pdf'))[1]

    text_page1 = pagen1.text_page()
    assert len(text_page1) == 0
    assert text_page1.text == ''
