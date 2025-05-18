from datetime import date
from xml.sax import saxutils
from dataclasses import dataclass

COPYRIGHT_TEMPLATE = "Copyright (c) {0} {1}. All rights reserved."

STYLESHEET_TEMPLATE = (
    '\t<link rel="stylesheet" type="text/css" media="all" href="{}">\n'
)


HTML_TEMPLATE = """<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">

<head>
    <title>{title}</title>
    <meta name="Description" content="{description}" />
    <meta name="Keywords" content="{keywords}" />
    <meta equiv="content-type" content="text/html; charset=utf-8" />
{stylesheet}\
</head>

<body>
    <footer>
        {copyright}
    </footer>
</body>

</html>
"""


class CancelledError(Exception):
    pass


class RequiredError(Exception):
    pass


@dataclass
class SkeletonInformation:
    name: str
    year: int
    filename: str
    title: str
    description: str | None
    keywords: list[str] | None
    stylesheet: str | None


def get_string(
    message: str,
    name: str = "string",
    default: str | None = None,
    minimum_length: int = 0,
    maximum_length: int = 80,
) -> str | None:
    message += ": " if default is None else " [{0}]: ".format(default)
    while True:
        try:
            line = input(message)
            if not line:
                if default is not None:
                    return default
                if minimum_length == 0:
                    return ""
                else:
                    raise ValueError("{0} may not be empty".format(name))

            if not (minimum_length <= len(line) <= maximum_length):
                raise ValueError(
                    "{name} must have at least "
                    "{minimum_length} and at most "
                    "{maximum_length} characters".format(**locals())
                )

            return line
        except ValueError as err:
            print("ERROR", err)


def get_integer(
    message: str,
    name: str = "integer",
    default: int | None = None,
    minimum: int = 0,
    maximum: int = 100,
    allow_zero: bool = True,
) -> int | None:
    message += ": " if default is None else " [{0}]: ".format(default)
    while True:
        try:
            line = input(message)
            if not line:
                if default is not None:
                    return default
                if allow_zero:
                    return 0
                else:
                    raise ValueError("{0} may not be empty".format(name))

            if not (minimum <= int(line) <= maximum):
                raise ValueError(
                    "{name} must be at least {minimum} and at most {maximum}".format(
                        **locals()
                    )
                )

            return int(line)
        except ValueError as err:
            print("ERROR", err)


def populate_information(information: SkeletonInformation) -> None:
    name = get_string("Enter your name (for copyright)", "name", information.name)
    if not name:
        raise CancelledError()

    year = get_integer(
        "Enter copyright year",
        "year",
        information.year,
        2000,
        2100,
        True,
    )
    assert year is not None

    if year == 0:
        raise CancelledError()
    filename = get_string("Enter filename", "filename")
    if not filename:
        raise CancelledError()
    if not filename.endswith((".htm", ".html")):
        filename += ".html"
    title = get_string("Enter title", "title")
    if not title:
        raise CancelledError()
    description = get_string("Enter description (optional)", "description")
    if not description:
        raise CancelledError()
    keyword = get_string("Enter a keyword (optional)", "keyword")
    keywords: list[str] = []
    while keyword:
        keywords.append(keyword)
        keyword = get_string("Enter a keyword (optional)", "keyword")
    stylesheet = get_string("Enter the stylesheet filename (optional)", "stylesheet")
    if stylesheet and not stylesheet.endswith((".css", ".tss", ".scss", ".sass")):
        stylesheet += ".css"
    information = SkeletonInformation(
        name=name,
        year=year,
        filename=filename,
        title=title,
        description=description,
        keywords=keywords,
        stylesheet=stylesheet,
    )


def make_html_skeleton(info: SkeletonInformation) -> None:
    copyright = COPYRIGHT_TEMPLATE.format(info.year, saxutils.escape(info.name))
    title = saxutils.escape(info.title)
    description = saxutils.escape(info.description) if info.description else ""
    keywords = (
        ",".join([saxutils.escape(k) for k in info.keywords]) if info.keywords else ""
    )
    stylesheet = (
        STYLESHEET_TEMPLATE.format(saxutils.escape(info.stylesheet))
        if info.stylesheet
        else ""
    )

    html = HTML_TEMPLATE.format(
        title=title,
        description=description,
        keywords=keywords,
        stylesheet=stylesheet,
        copyright=copyright,
    )

    fh = None
    try:
        fh = open(info.filename, "w", encoding="utf-8")
        fh.write(html)
    except EnvironmentError as err:
        print("ERROR", err)
    finally:
        if fh is not None:
            fh.close()


def main():
    information = SkeletonInformation(
        name="",
        year=date.today().year,
        title="",
        description="",
        keywords=None,
        stylesheet=None,
        filename="",
    )

    while True:
        try:
            print("\nMake HTML Skeleton\n")
            populate_information(information)
            make_html_skeleton(information)  # type: ignore
        except CancelledError:
            print("Cancelled")
        if (
            x := get_string("\nCreate another (y/n)?", default="y")
        ) and x.lower() not in {"y", "yes"}:
            break


if __name__ == "__main__":
    main()
