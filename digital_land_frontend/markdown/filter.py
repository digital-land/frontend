#!/usr/bin/env python3

import markdown
from markdown.extensions.toc import TocExtension

from digital_land_frontend.markdown.govukify import govukify

# init markdown - basic setup with table of contents
md = markdown.Markdown(extensions=[TocExtension(toc_depth="2-3"), "tables"])


def compile_markdown(s, md=md):
    html = md.convert(s)
    return govukify(html)


# making markdown compiler available to jinja templates
def markdown_filter(s):
    return compile_markdown(s)
