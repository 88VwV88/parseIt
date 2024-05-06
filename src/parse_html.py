import re

PARSE_TAG = re.compile(r'''
                    <(?P<tag>\w+)\s*(?P<attribs>[\w\-=\.#\\/'"]*)>
                        (?P<content>[^\1]*)
                    </\1>
                       ''', re.VERBOSE)

def parse_html(html):

    if (matches := PARSE_TAG.split(html)):
        DOM = []
        for match in matches:
            print(f'{match = }')
            # tag, attribs, contents = match.groups()
            # DOM += {tag: [attribs, parse_html(contents) or contents]}
        return DOM
    else:
        return ''

print(parse_html('<!DOCTYPE html><html lang="en"><head><link rel="stylesheet" href="#"></head><body class="main"><p>Hello, World!</p></body></html>'))