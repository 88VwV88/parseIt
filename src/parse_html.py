import re


PARSE_TAG = re.compile(r'''
                    <(\w+)([\s\w\-=\.:#\\/'"]*)>
                        ([^\1]*)
                    </\1>
                       ''', re.VERBOSE)

def parse_html(html: str) -> dict | str:
    if parts := PARSE_TAG.findall(html):
        print(parts)
        DOM = {}
        for name, attribs, content in parts:
            if attribs:
                attribs = attribs.split(' ')
                attrs = {}
                for attrib in attribs:
                    if '=' in attrib:
                        attr, value = attrib.split('=')
                        attrs[attr] = value.replace('"', '')
                DOM[name] = {'attrs': attrs, 'contents': parse_html(content)}
            else:
                DOM[name] = {'attrs': attribs.strip(), 'contents': parse_html(content)}
        return DOM
    else:
        return html

def read_html(filename: str) -> str | None:
    contents = b""
    with open(filename, "rb") as file:
        for line in file:
            contents += line.strip()
    return contents.decode(encoding='utf-8')

if __name__ == '__main__':
    _html = '<html><head><title>Hi!</title></head><body class="main">Hello, World!</body></html>'
    print(parse_html(_html))