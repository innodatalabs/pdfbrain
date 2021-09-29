Tutorial
========

.. module:: pdfbrain
    :noindex:
.. PDF Brain tutorial

The philosophy of **pdfbrain** is to map API to standard and well undersood Python objects, like
:class:`list` and :class:`dict`.

In this tutorial we will use the following :download:`sample document <../../pdfbrain/test/resources/sample.pdf>`.

Version
-------

Here is how to get the PDF Brain version string::

    import pdfbrain

    pdfbrain.__version__
    >> '0.0.1'

PDFFile
-------

:class:`PDFFile` is the top-level object, and the only object that can be instantiated directly::

    from pdfbrain import PDFFile

    doc = PDFFile.load('sample.pdf')

    len(doc)
    >> 15

As you can see, :class:`PDFFile` resembles standard Python :class:`list`, containing :class:`PDFPage` objects.

PDF file creators can attach arbitraty key-value strings to the document, that we call ``meta`` (official
PDf specs call it ``Document Information Dictionary``).
Most commonly these values describe ``Author``, ``Title``, and the name of software that created this
document. Lets see the meta in our sample::

    doc.meta['Title']
    >> 'Red Stork'

You can change `meta` content and save the updated document::

    doc.meta['Title'] = 'Awesome PDF parsing library'
    doc.save('awesome.pdf')

Document has a lazily populated collection of fonts. Initially this collection is empty. As pages are being accessed
and parsed, this collection is being populated::

    list(doc[0])  # read all objects from page 1
    len(doc.fonts)
    >> 2


PDFPage
-------

:class:`PDFPage` represents PDF page. Get page by indexing a :class:`PDFFile` object, just like a normal list::

    page = doc[0]
    page.crop_box
    >> (0.0, 0.0, 612.0, 792.0)

:class:`PDFPage` has :attr:`PDFPage.label`, representing the page label (like ``xxi``, or ``128``)::

    doc[2].label  # this is the label of the third page
    >> 'i'


.. To be continued ..