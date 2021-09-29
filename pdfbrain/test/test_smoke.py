from pdfbrain import PDFFile
from . import res
from pytest import approx


def test_smoke():
    pdf = PDFFile.load(res('simple.pdf'))
    assert len(pdf) == 2

    page0 = pdf[0]
    assert page0.label == ''
    assert page0.media_box == (0.0, 0.0, 612.0, 792.0)
    assert page0.crop_box == (0.0, 0.0, 612.0, 792.0)


    img = pdf[1].render()
    assert img.size == (612, 792)

def test_text():
    pagen0 = PDFFile.load(res('simple.pdf'))[0]

    text_page0 = pagen0.text_page()
    assert len(text_page0) == 587
    assert text_page0.text[:20] == ' A Simple PDF File \r'
    assert text_page0.unicode(5) == 109
    assert text_page0.bbox(5) == (approx(116.15, 0.01), approx(722.28, 0.01), approx(135.16, 0.01), approx(736.81, 0.01))

def test_search():
    pagen0 = PDFFile.load(res('simple.pdf'))[0]

    text_page0 = pagen0.text_page()
    finder = text_page0.find('zzzzz')
    results = list(finder)
    assert len(results) == 1
    assert len(results[0]) == 1  # just one box is expected
    assert results[0][0] == (approx(196.29, 0.01), approx(616.896, 0.01), approx(220.67, 0.01), approx(622.126, 0.01))


def test_search_flags():
    pagen0 = PDFFile.load(res('simple.pdf'))[0]

    text_page0 = pagen0.text_page()
    finder = text_page0.find('Even', match_case=True)
    results = list(finder)
    assert len(results) == 1

    finder = text_page0.find('even', match_case=True)
    results = list(finder)
    assert len(results) == 0

    finder = text_page0.find('even', match_case=False)
    results = list(finder)
    assert len(results) == 1

    finder = text_page0.find('borin')
    results = list(finder)
    assert len(results) == 1

    finder = text_page0.find('borin', match_whole_word=True)
    results = list(finder)
    assert len(results) == 0
