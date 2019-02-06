#!/usr/bin/env python3
"""pandoc filters used in converting markdown cells to the target type.
usage in jinja template:
    convert_pandoc('markdown', 'json') | resolve_references | convert_pandoc('json','latex')  # noqa: E501

adapted from nbconvert/filters/filter_links.py
"""
import re
import sys
import json

from distutils.util import strtobool
from pandocfilters import (applyJSONFilters,  # noqa: F401
                           RawInline, Math, Image, Table)
# TODO at present we defer import, so we can monkey patch stdin during tests
# from pandocxnos import (elt, PandocAttributes,
#                         attach_attrs_factory, detach_attrs_factory,
#                         extract_attrs)
# from pandocxnos import init as get_pandoc_version
# from nbconvert.utils.pandoc import get_pandoc_version
# from nbconvert.filters.latex import escape_latex
from nbconvert.utils.pandoc import pandoc

if sys.version_info > (3,):
    from urllib.request import unquote  # pylint: disable=no-name-in-module
else:
    from urllib import unquote  # pylint: disable=no-name-in-module


LATEX_FIG_LABELLED = """\\begin{{figure}}[{options}]
\\hypertarget{{{label}}}{{%
\\begin{{center}}
\\adjustimage{{max size={{0.9\\linewidth}}{{0.9\\paperheight}},{size}}}{{{path}}}
\\end{{center}}
\\caption{{{caption}}}\\label{{{label}}}
}}
\\end{{figure}}"""  # noqa: E501

LATEX_FIG_UNLABELLED = """\\begin{{figure}}[{options}]
\\begin{{center}}
\\adjustimage{{max size={{0.9\\linewidth}}{{0.9\\paperheight}},{size}}}{{{path}}}
\\end{{center}}
\\caption{{{caption}}}
\\end{{figure}}"""  # noqa: E501


# TODO add doc/cell level meta tag for at_notation
def resolve_references(source, reftag="cref", at_notation=False):
    """
    Apply filters to the pandoc json object

    Parameters
    ----------
    source: str
        content in the form of a string encoded JSON object,
        as represented internally in ``pandoc``
    reftag: str
        latex tag for references, when converting [](#label) -> \\ref{label}
    at_notation: bool
        interpret @label as a citation or, if has known prefix modifier,
        a reference; '+' = cref, '^' = Cref, '!' = ref
        see: https://pandoc.org/MANUAL.html#citations

    """
    from pandocxnos import (elt,
                            attach_attrs_factory, detach_attrs_factory)
    from pandocxnos import init as get_pandoc_version
    # TODO is there a better way to get the pandoc-api-version
    api_version = None
    if get_pandoc_version() >= '1.18':
        source_json = json.loads(source)
        api_version = source_json.get("pandoc-api-version", None)

    global Image
    if get_pandoc_version() < '1.16':
        Image = elt('Image', 2)

    # resolve references
    filters = [_resolve_one_ref_func(reftag, use_at_notation=at_notation)]
    # resolve math
    filters.extend([
        attach_attrs_factory(Math, allow_space=True),
        _resolve_math,
        detach_attrs_factory(Math),
    ])
    # resolve images
    if get_pandoc_version() >= '1.16':
        filters.append(_resolve_figures_func(api_version))
    else:
        filters.extend([
            attach_attrs_factory(Image,
                                 extract_attrs=_extract_image_attrs),
            _resolve_figures_func(api_version),
            detach_attrs_factory(Image)
        ])
    # resolve tables
    filters.extend([
        _attach_attrs_table,
        _resolve_tables_func(api_version),
        detach_attrs_factory(Table),
    ])

    return applyJSONFilters(filters, source)


def _sanitize_label(label):
    """from pandoc documentation
    The citation key must begin with a letter, digit, or _,
    and may contain alphanumerics, _,
    and internal punctuation characters (:.#$%&-+?<>~/)
    """
    label = str(label).lower()
    label = re.sub("[^a-zA-Z0-9-:\.]+", "", label)
    # TODO raise warning if changed?
    return label


def _extract_image_attrs(x, n):
    """Extracts attributes for an image.  n is the index where the
    attributes begin.  Extracted elements are deleted from the element
    list x.  Attrs are returned in pandoc format.
    """
    from pandocxnos import extract_attrs, PandocAttributes
    from pandocxnos import init as get_pandoc_version
    try:
        return extract_attrs(x, n)

    except (ValueError, IndexError):

        if get_pandoc_version() < '1.16':
            # Look for attributes attached to the image path, as occurs with
            # image references for pandoc < 1.16 (pandoc-fignos Issue #14).
            # See http://pandoc.org/MANUAL.html#images for the syntax.
            # Note: This code does not handle the "optional title" for
            # image references (search for link_attributes in pandoc's docs).
            assert x[n-1]['t'] == 'Image'
            image = x[n-1]
            s = image['c'][-1][0]
            if '%20%7B' in s:
                path = s[:s.index('%20%7B')]
                attrs = unquote(s[s.index('%7B'):])
                image['c'][-1][0] = path  # Remove attr string from the path
                return PandocAttributes(attrs.strip(), 'markdown').to_pandoc()
        raise


def _attach_attrs_table(key, value, fmt, meta):
    """Extracts attributes and attaches them to element.

    We can't use attach_attrs_factory() because Table is a block-level element
    """
    from pandocxnos import extract_attrs
    if key in ['Table']:
        assert len(value) == 5
        caption = value[0]  # caption, align, x, head, body

        # Set n to the index where the attributes start
        n = 0
        while n < len(caption) and not \
                (caption[n]['t'] == 'Str' and caption[n]['c'].startswith('{')):
            n += 1

        try:
            attrs = extract_attrs(caption, n)
            value.insert(0, attrs)
        except (ValueError, IndexError):
            pass


def _resolve_one_ref_func(cmnd="cref", prefix="", use_at_notation=False):

    def resolve_one_reference(key, value, format, meta):
        """ takes a tuple of arguments that are compatible with
        ``pandocfilters.walk()`` that allows identifying hyperlinks in the
        document and transforms them into valid LaTeX
        calls so that linking to headers between cells is possible.

        Parameters
        ----------
        key: str
            the type of the pandoc object (e.g. 'Str', 'Para')
        value:
            the contents of the object (e.g. a string for 'Str', a list of
            inline elements for 'Para')
        format: str
            is the target output format (as supplied by the
            `format` argument of `walk`)
        meta:
            is the document's metadata

        Returns
        -------
        pandoc_object:

        """
        if key == 'Link':
            target = value[-1][0]  # in older pandoc, no attributes at front
            m = re.match(r'#(.+)$', target)
            if m:
                print(value)
                # pandoc automatically makes labels for headings.
                label = _sanitize_label(m.group(1))
                return RawInline(
                    'tex', '{0}\\{1}{{{2}}}'.format(prefix, cmnd, label))

        if use_at_notation:
            # References may occur in a variety of places; we must process them
            # all.
            if key in ['Para', 'Plain']:
                _process_at_refs(value)
            elif key == 'Image':
                _process_at_refs(value[-2])
            elif key == 'Table':
                _process_at_refs(value[-5])
            elif key == 'Span':
                _process_at_refs(value[-1])
            elif key == 'Emph':
                _process_at_refs(value)
            elif key == 'Strong':
                _process_at_refs(value)

        return None

    return resolve_one_reference


def _process_at_refs(el):
    # NOTE in pandoc-xnos they repair_refs for
    # "-f markdown+autolink_bare_uris" with pandoc < 1.18
    deletions = []
    for i, sub_el in enumerate(el):
        if sub_el['t'] == 'Cite' and len(sub_el['c']) == 2:
            citations = sub_el['c'][0]
            # extracts the */+/! modifier in front of the Cite
            modifier = None
            if el[i-1]['t'] == 'Str':
                modifier = el[i - 1]['c'][-1]
                if modifier in ['^', '+', '!']:
                    if len(el[i - 1]['c']) > 1:
                        # Cut the modifier off of the string
                        el[i-1]['c'] = el[i-1]['c'][:-1]
                    else:
                        # The element contains only the modifier; delete it
                        deletions.append(i-1)

            tag = {'+': 'cref', '^': "Cref", "!": "ref"}.get(modifier, 'cite')

            if tag == "ref" and len(citations) > 1:
                raise ValueError(
                    "element contains multiple references, which cannot be "
                    "handled by \\ref: {}".format(sub_el['c'][1]))

            labels = [citation["citationId"] for citation in citations]

            el[i] = RawInline(
                'tex', '\\{0}{{{1}}}'.format(tag, ",".join(labels)))

    # delete in place
    deleted = 0
    for delete in deletions:
        del el[delete - deleted]
        deleted += 1


def _resolve_math(key, value, format, meta):
    """ see https://github.com/tomduck/pandoc-eqnos/blob/master/pandoc_eqnos.py

    Parameters
    ----------
    key: str
        the type of the pandoc object (e.g. 'Str', 'Para')
    value:
        the contents of the object (e.g. a string for 'Str', a list of
        inline elements for 'Para')
    format: str
        is the target output format (as supplied by the
        `format` argument of `walk`)
    meta:
        is the document's metadata

    Returns
    -------
    pandoc_object:

    """
    if key == 'Math' and len(value) == 3:
        body = value[-1]
        # mtype = value[1] # e.g. {'t': 'InlineMath'} or {'t': 'DisplayMath'}
        attributes = value[0]
        label = attributes[0]
        keywords = dict(attributes[-1])
        if label:
            label = "\\label{{{0}}}".format(label)
        env = keywords.get('env', 'equation')
        numbered = '' if strtobool(keywords.get('numbered', 'true')) else '*'
        return RawInline('tex',
                         '\\begin{{{0}{1}}}{2}{3}'
                         '\\end{{{0}{1}}}'.format(env, numbered, body, label))


def _resolve_figures_func(api_version):
    def resolve_figures(key, value, fmt, meta):
        """ see https://github.com/tomduck/pandoc-eqnos/

        Parameters
        ----------
        key: str
            the type of the pandoc object (e.g. 'Str', 'Para')
        value:
            the contents of the object (e.g. a string for 'Str', a list of
            inline elements for 'Para')
        fmt: str
            is the target output format (as supplied by the
            `format` argument of `walk`)
        meta:
            is the document's metadata

        Returns
        -------
        pandoc_object:

        """
        from pandocxnos import init as get_pandoc_version
        if key == 'Para' and len(value) == 1 and value[0]['t'] == 'Image':
            if len(value[0]['c']) == 2:  # Unattributed, bail out
                return None
            attributes, caption_block = value[0]['c'][:2]
            path, typef = value[0]['c'][2]  # TODO is typef always 'fig:'

            # convert the caption to latex
            if get_pandoc_version() >= '1.18':
                caption_json = json.dumps(
                    {
                        "blocks": [{"t": "Para", "c": caption_block}],
                        "meta": meta,
                        "pandoc-api-version": api_version
                    })
            else:
                caption_json = json.dumps(
                    [{'unMeta': {}},
                     [{"t": "Para", "c": caption_block}]])

            caption = pandoc(caption_json, 'json', 'latex')

            label = _sanitize_label(attributes[0])

            keywords = dict(attributes[-1])
            options = keywords.get("placement", "")
            size = ''
            if "width" in keywords:
                size = 'width={0}\\linewidth'.format(keywords['width'])
            if "height" in keywords:
                size = 'height={0}\\paperheight'.format(keywords['height'])

            if label:
                latex = LATEX_FIG_LABELLED.format(
                    label=label,
                    options=options,
                    path=path,
                    caption=caption,
                    size=size)
            else:
                latex = LATEX_FIG_UNLABELLED.format(
                    options=options,
                    path=path,
                    caption=caption,
                    size=size)

            return {"t": "Para", "c": [RawInline('tex', latex)]}

    return resolve_figures


def _resolve_tables_func(api_version):
    def resolve_tables(key, value, fmt, meta):
        """ see https://github.com/tomduck/pandoc-tablenos

        Parameters
        ----------
        key: str
            the type of the pandoc object (e.g. 'Str', 'Para')
        value:
            the contents of the object (e.g. a string for 'Str', a list of
            inline elements for 'Para')
        fmt: str
            is the target output format (as supplied by the
            `format` argument of `walk`)
        meta:
            is the document's metadata

        Returns
        -------
        pandoc_object:

        """
        from pandocxnos import elt
        AttrTable = elt('Table', 6)

        if key == 'Table':
            if len(value) == 5:  # Unattributed, bail out
                return None
            attributes, caption = value[:2]
            label = _sanitize_label(attributes[0])
            value[1] += [RawInline('tex', '\\label{{{0}}}'.format(label))]
            return [AttrTable(*value)]

    return resolve_tables

# TODO sphinx directives (like todo, warning etc...)