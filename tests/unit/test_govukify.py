from digital_land_frontend.markdown.govukify import govukify
from digital_land_frontend.markdown.filter import compile_markdown


def test_paragraph_class():
    s = "<p>This is a test string</p>"

    assert govukify(s) == '<p class="govuk-body">This is a test string</p>'


def test_markdown_paragraph():
    s = "This is a paragraph."

    assert compile_markdown(s) == '<p class="govuk-body">This is a paragraph.</p>'


def test_markdown_table():
    s = """| H1 | H2 |
    | ---- | ---- |
    | cell 1.1 | cell 1.2 |
    | cell 2.1 | cell 2.2 |"""

    assert (
        compile_markdown(s)
        == """<table class="govuk-table" >
<thead class="govuk-table__head">
<tr class="govuk-table__row">
<th scope="row" class="govuk-table__header">H1</th>
<th scope="row" class="govuk-table__header">H2</th>
</tr>
</thead>
<tbody class="govuk-table__body">
<tr class="govuk-table__row">
<td class="govuk-table__cell">cell 1.1</td>
<td class="govuk-table__cell">cell 1.2</td>
</tr>
<tr class="govuk-table__row">
<td class="govuk-table__cell">cell 2.1</td>
<td class="govuk-table__cell">cell 2.2</td>
</tr>
</tbody>
</table>"""
    )
