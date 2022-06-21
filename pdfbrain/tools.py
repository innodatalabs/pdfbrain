import functools
import pypdfium2 as pdfium


def lazyproperty(fn):
    attr_name = '_lazy_' + fn.__name__

    @property
    @functools.wraps(fn)
    def f(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return f

def get_error_message():
    err_code = pdfium.FPDF_GetLastError()
    return {
        0: 'Success',
        1: 'Unknown error',
        2: 'File access error (file cannot be found or be opened)',
        3: 'Data format error',
        4: 'Incorrect password error',
        5: 'Unsupported security scheme error',
        6: 'License authorization error',
    }.get(err_code, f'Error code {err_code}')
