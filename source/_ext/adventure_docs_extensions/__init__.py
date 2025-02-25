#!/usr/bin/env python3
# This file is part of adventure-docs, licensed under the MIT License.
#
# Copyright (c) 2017-2022 KyoriPowered
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path
import re
from sphinx.application import Sphinx
from docutils.parsers.rst import nodes


def setup(app: Sphinx):
    app.add_role("mojira", mojira_role)
    app.connect('html-collect-pages', _fix_cloudflare_name_mangling)


_issue_regex = re.compile(r'[A-Z]+-[1-9][0-9]*')
_mojira_url = "https://bugs.mojang.com/browse/"


def mojira_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    if not _issue_regex.fullmatch(text):
        msg = inliner.reporter.error(f'Issue number must be in the format PROJECT-1234, but {text} was given instead', line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    ref = _mojira_url + text

    node = nodes.reference(rawtext, text, refuri=ref, **options)

    return [node], []


def _fix_cloudflare_name_mangling(app: Sphinx):
    """
    Cloudflare Pages does mangling of page names to strip the `.html` from the end.
    We need to preserve those links when moving to GitHub pages though, so we build out
    redirects using directory names.

    References https://gitlab.com/documatt/sphinx-reredirects/-/blob/master/sphinx_reredirects/__init__.py liberally
    """

    docs = app.env.found_docs
    outdir = Path(app.outdir)

    for doc in docs:
        if doc.endswith("/index") or (doc + "/index" in docs):
            continue

        doc_basename = doc.split('/')[-1]

        # Write out a temporary file
        from_path = outdir / doc / "index.html"
        to_uri = f"../{doc_basename}.html"
        from_contents = f'<html><head><meta http-equiv="refresh" content="0; url={to_uri}"></head></html>'

        from_path.parent.mkdir(parents=True, exist_ok=True)
        from_path.write_text(from_contents, encoding='UTF-8')

    return []
