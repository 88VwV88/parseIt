import re

SPLIT_TAGS = re.compile(r'''
                    <(\w+)(\s*([\w\-=\.#\\/'"]*))>
                        ([^\1]*)
                    </\1>
                        ''', re.VERBOSE)
PARSE_TAG = re.compile(r'''
                    <(?P<name>\w+)(?P<attribs>[\s\w\-=\.:#\\/'"]*)>
                        (?P<content>[^\1]*)
                    </\1>
                       ''', re.VERBOSE)

def parse_html(html):
    if parts := PARSE_TAG.findall(html):
        DOM = {}
        for name, attribs, content in parts:
            DOM[name] = (attribs.strip(), parse_html(content))
        return DOM
    else:
        return ''

def read_html(filename: str) -> str | None:
    contents = b""
    with open(filename, "rb") as file:
        for line in file:
            contents += line.strip()
    return contents.decode(encoding='utf-8')

if __name__ == '__main__':
    _html = read_html('career-synopsis.html')
    print(parse_html(_html))