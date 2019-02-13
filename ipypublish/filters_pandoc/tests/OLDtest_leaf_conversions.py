from ipypublish.filters_pandoc.utils import apply_filter
from ipypublish.filters_pandoc.OLDleaf_conversions import main


def test_latex_to_rst():
    """
    """
    in_string = [
        r"\cref{label1} \Cref{label2}  \cite{a-cite-key_2019}",
        "",
        r"\ref{label3}  \todo[inline]{something todo}",
        "",
        r"\todo{something else todo}"
    ]

    out_string = apply_filter(in_string, main, "rst")

    assert out_string == "\n".join([
        ":ref:`label1` :ref:`label2`  :cite:`a-cite-key_2019` ",
        "",
        ":ref:`label3`",
        "",
        ".. todo:: something todo"
        "",
        "",
        "",
        "",
        ".. todo:: something else todo",
        "",
        "",
        ""
    ])


def test_latex_to_rst_with_numref():
    """"""
    in_string = [
        "---",
        "ipub:",
        "    use_numref: true",
        "---",
        "",
        r"\cref{label1} \Cref{label2}  \cite{a-cite-key_2019}",
        "",
        r"\ref{label3}  \todo[inline]{something todo}",
        "",
        r"\todo{something else todo}"
    ]

    out_string = apply_filter(in_string, main, "rst")

    assert out_string == "\n".join([
        ":numref:`label1` :numref:`label2`  :cite:`a-cite-key_2019` ",
        "",
        ":ref:`label3`",
        "",
        ".. todo:: something todo"
        "",
        "",
        "",
        "",
        ".. todo:: something else todo",
        "",
        "",
        ""
    ])


def test_html_to_latex_label():

    in_string = [
        "[some text](#alabel)"
    ]

    out_string = apply_filter(in_string, main, "latex")

    assert out_string == "\n".join([
        r"\cref{alabel}",
        ""
    ])


def test_html_to_latex_label_with_custom_tag():

    in_string = [
        "---",
        "ipub:",
        "    reftag: other",
        "---",
        "",
        "[some text](#alabel)"
    ]

    out_string = apply_filter(in_string, main, "latex", strip_meta=True)

    assert out_string == "\n".join([
        r"\other{alabel}",
        ""
    ])


def test_html_to_latex_cite():

    in_string = [
        'surrounding <cite data-cite="cite_key">text</cite> text'
    ]

    out_string = apply_filter(in_string, main, "latex")

    assert out_string == "\n".join([
        r"surrounding \cite{cite_key} text",
        ""
    ])


def test_html_to_rst_cite():

    in_string = [
        'surrounding <cite data-cite="cite_key">text</cite> text'
    ]

    out_string = apply_filter(in_string, main, "rst")

    assert out_string == "\n".join([
        "surrounding  :cite:`cite_key`  text",
        ""
    ])


def test_citations_latex():

    in_string = [
        '@label1',
        '',
        '[an internal link](#label2)'
        '',
        '[an external link](http://something.org)',
        '',
        '![a citation @label](path/to/image.png)',
    ]

    out_string = apply_filter(in_string, main, "latex")

    assert out_string.strip() == "\n".join([
        "\\cref{label1}",
        "",
        "\\cref{label2} \\href{http://something.org}{an external link}",
        "",
        "\\begin{figure}",
        "\\centering",
        "\includegraphics{path/to/image.png}",
        "\\caption{a citation \cref{label}}",
        "\\end{figure}"
    ])


def test_citations_rst():

    in_string = [
        '@label1',
        '',
        '[an internal link](#label2)'
        '',
        '[an external link](http://something.org)',
        '',
        '![a citation @label](path/to/image.png)',
    ]

    out_string = apply_filter(in_string, main, "rst")

    assert out_string.strip() == "\n".join([
        ":ref:`label1`",
        "",
        ":ref:`label2` `an external link <http://something.org>`__",
        "",
        ".. figure:: path/to/image.png",
        "   :alt: a citation :ref:`label`",
        "",
        "   a citation :ref:`label`"
    ])
