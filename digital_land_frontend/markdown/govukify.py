#!/usr/bin/env python3


def govukify(html):
    """
    A method to add govuk classes to vanilla HTML

    Params
    ------
    html : str
        a string of html
    """
    html = html.replace("<p", '<p class="govuk-body"')
    html = html.replace("<h1", '<h1 class="govuk-heading-xl"')
    html = html.replace("<h2", '<h2 class="govuk-heading-l"')
    html = html.replace("<h3", '<h3 class="govuk-heading-m"')
    html = html.replace("<h4", '<h4 class="govuk-heading-s"')
    html = html.replace("<ul", '<ul class="govuk-list govuk-list--bullet"')
    html = html.replace("<pre>", '<pre class="hljs-container">')
    html = html.replace("<img", '<img class="dl-image" ')
    html = html.replace(
        "<hr",
        '<hr class="govuk-section-break govuk-section-break--m govuk-section-break--visible"',
    )

    # add correct classes for govuk tables. Should test this
    html = html.replace("<table", '<table class="govuk-table" ')
    html = html.replace("<thead>", '<thead class="govuk-table__head">')
    html = html.replace("<tbody>", '<tbody class="govuk-table__body">')
    html = html.replace("<tr>", '<tr class="govuk-table__row">')
    html = html.replace("<th>", '<th scope="row" class="govuk-table__header">')
    html = html.replace("<td>", '<td class="govuk-table__cell">')

    html = html.replace("<code>", '<code class="dl-code">')

    return html
