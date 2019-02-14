""" a panflute filter to find raw elements
and convert them to format agnostic Span elements
"""
import re
from panflute import Element, Doc, Cite, RawInline, Link  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.definitions import (
    PREFIX_MAP_LATEX_R, PREFIX_MAP_RST_R, ATTRIBUTE_CITE_CLASS,
    IPUB_META_ROUTE
)

RAWSPAN_CLASS = "raw-content"

CONVERTED_CITE_CLASS = "converted-Cite"
CONVERTED_OTHER_CLASS = "converted-Other"


def create_cite_span(identifier, rawformat, is_block,
                     prefix="", alt=None):
    citation = pf.Citation(
        identifier
    )
    attributes = {"raw-format": rawformat, "prefix": prefix}
    if alt is not None:
        attributes["alt"] = str(alt)
    cite = Cite(citations=[citation])
    span = pf.Span(
        cite,
        classes=[RAWSPAN_CLASS, CONVERTED_CITE_CLASS, ATTRIBUTE_CITE_CLASS],
        attributes=attributes
    )
    if is_block:
        return pf.Plain(span)
    else:
        return span


def process_internal_links(link, doc):
    # type: (Link, Doc) -> Element
    """extract links that point to internal items, e.g. [text](#label)"""
    if not isinstance(link, pf.Link):
        return None
    match = re.match(r'#(.+)$', link.url)
    if not match:
        return None

    return create_cite_span(
        match.group(1), "markdown", False,
        prefix=dict(PREFIX_MAP_LATEX_R).get(
            doc.get_metadata(IPUB_META_ROUTE + ".reftag", "cref"), "cref"),
        alt=pf.stringify(pf.Plain(*list(link.content))).strip())


def process_html(element, doc):
    # type: (RawInline, Doc) -> Element
    """extract raw html <cite data-cite="cite_key">text</cite>"""
    if not (isinstance(element, (pf.RawInline, pf.RawBlock)) and
            element.format in ("html", "html5")):
        return None

    match = re.match(
        r"<cite\s*data-cite\s*=\"?([^>\"]*)\"?>", element.text)
    if not match:
        return None

    # look for the closing tag
    content = []
    closing = element.next

    while closing:
        if (isinstance(closing, pf.RawInline) and
                closing.format in ("html", "html5")):
            endmatch = re.match(r"^\s*</cite>\s*$", closing.text)
            if endmatch:
                break
        content.append(closing)
        closing = closing.next

    if not closing:
        # TODO emit warning?
        return None

    doc.to_delete.setdefault(element.parent, set()).update(content+[closing])

    # TODO include original content
    return create_cite_span(match.group(1), "html",
                            isinstance(element, pf.RawBlock))


def process_latex(element, doc):
    # type: (RawInline, Doc) -> Element
    """extract all latex adhering to \\tag{content} or \\tag[options]{content}
    to a Span element with class RAWSPAN_CLASS attributes:

    ::

        attributes={"format": "latex",
                    "tag": tag, "content": content, "options": options}

    - Cref, cref, ref, and cite will aslo have class CONVERTED_CITE_CLASS
    - everything else will also have class CONVERTED_OTHER_CLASS

    """
    if not (isinstance(element, (pf.RawInline, pf.RawBlock)) and
            element.format in ("tex", "latex")):
        return None

    # find tags with no option, i.e \tag{label}
    match_latex_noopts = re.match(
        r"^\s*\\([^\{\[]+)\{([^\}]+)\}\s*$", element.text)

    if match_latex_noopts:

        tag = match_latex_noopts.group(1)
        content = match_latex_noopts.group(2)

        if tag in dict(PREFIX_MAP_LATEX_R):
            return create_cite_span(
                content, "latex", isinstance(element, pf.RawBlock),
                prefix=dict(PREFIX_MAP_LATEX_R).get(tag, ""))

        else:
            span = pf.Span(
                classes=[RAWSPAN_CLASS, CONVERTED_OTHER_CLASS],
                attributes={"format": "latex", "tag": tag,
                            "content": content, "original": element.text}
            )
            if isinstance(element, pf.RawBlock):
                return pf.Plain(span)
            else:
                return span

    # find tags with option, i.e \tag[options]{label}
    match_latex_wopts = re.match(
        r"^\s*\\([^\{\[]+)\[([^\]]*)\]\{([^\}]+)\}\s*$", element.text)

    if match_latex_wopts:

        tag = match_latex_wopts.group(1)
        options = match_latex_wopts.group(2)
        content = match_latex_wopts.group(3)

        span = pf.Span(
            classes=[RAWSPAN_CLASS, CONVERTED_OTHER_CLASS],
            attributes={"format": "latex",
                        "tag": tag, "content": content,
                        options: "options",
                        "original": element.text}
        )
        if isinstance(element, pf.RawBlock):
            return pf.Plain(span)
        else:
            return span

    return None


def process_rst(para, doc):
    # type: (pf.Para, Doc) -> Element
    """extract rst adhering to ``:role:`label```, where role is a known
    to a Cite element with class RAWSPAN_CLASS and CONVERTED_CITE_CLASS
    and attributes:

    ::

        attributes={"format": "rst",
                    "role": tag, "content": content}

    """
    # "a :ref:`label` b" is converted to:
    # ListContainer(Para(Str(a) Space Str(:ref:) Code(label) Space Str(b)))
    if not (isinstance(para, (pf.Para))):
        return None

    # match_rst_role = re.match(
    #     "^\\s*\\:([a-z]+)\\:\\`([^\\`]+)\\`$", element.text)

    new_para = []
    skip_next = False

    for element in para.content:

        if skip_next:
            skip_next = False
            continue

        if not (isinstance(element, pf.Str)
                and isinstance(element.next, pf.Code)):
            new_para.append(element)
            continue

        if not (len(element.text) > 2 and
                element.text.startswith(":") and
                element.text.endswith(":")):
            new_para.append(element)
            continue

        role = element.text[1:-1]
        content = element.next.text

        if role in dict(PREFIX_MAP_RST_R):
            new_element = create_cite_span(
                content, "rst", False,
                prefix=dict(PREFIX_MAP_RST_R).get(role, ""))
            new_para.append(new_element)
            skip_next = True
        else:
            new_para.append(element)
            # span = pf.Span(
            #     classes=[RAWSPAN_CLASS, CONVERTED_OTHER_CLASS],
            #     attributes={"format": "rst", "role": role,
            #                 "content": content, "original": element.text}
            # )
            # if isinstance(element, pf.RawBlock):
            #     return pf.Plain(span)
            # else:
            #     return span
    
    if len(new_para) != len(para.content):
        return pf.Para(*new_para)


def gather_processors(element, doc):
    """ we gather the processors,
    so that we don't have to do multiple passes
    """
    if isinstance(element, pf.Link):
        return process_internal_links(element, doc)
    if (isinstance(element, (pf.RawInline, pf.RawBlock)) and
            element.format in ("html", "html5")):
        return process_html(element, doc)
    if (isinstance(element, (pf.RawInline, pf.RawBlock)) and
            element.format in ("tex", "latex")):
        return process_latex(element, doc)
    if (isinstance(element, (pf.Para,))):
        return process_rst(element, doc)


def prepare(doc):
    # type: (Doc) -> None
    doc.to_delete = {}


def finalize(doc):
    # type: (Doc) -> None
    # TODO is this the best approach? see sergiocorreia/panflute#96
    for element, delete in doc.to_delete.items():
        if isinstance(element, pf.Table):
            element.caption = [e for e in element.caption if e not in delete]
        else:
            element.content = [e for e in element.content if e not in delete]
    del doc.to_delete


def main(doc=None, extract_formats=True):
    # type: (Doc, bool) -> None
    """if extract_formats then convert citations defined in
    latex, rst or html formats to special Span elements
    """
    return pf.run_filter(gather_processors,
                         prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
