PDF Brain
=========

Yet another PDF parser. This one is based on PDFium_ engine.

.. _PDFium: https://pdfium.googlesource.com/pdfium/

.. _FOXIT: https://developers.foxit.com/resources/pdf-sdk/c_api_reference_pdfium/index.html


Quick Start
-----------

Sample::

    from pdfbrain import PDFFile

    doc = PDFFile.load('sample.pdf')
    print('Number of pages:', len(doc))


.. toctree::
    :maxdepth: 2
    :caption: Manual:

    tutorial.rst
    reference.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`
