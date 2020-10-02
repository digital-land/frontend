# Data item

Use the data item component when you want to display a number from some data.

{{ designSystemExample({
"iframe": {
    "title": "An example of the data item component",
    "url": "example.html",
    "size": "s"
},
"partial": [
    {
    "type": "html",
    "name": 'digital-land-frontend/components/data-item/example.html'
    },
    {
    "type": "jinja",
    "path": 'digital-land-frontend/components/data-item/example.html'
    }
]
}) }}

### When not to use

This component shouldn't be used for any number on a page, it is intended to be used to display a significant piece of data or information.

### Inline example

Add a `.data-item--inline` class if you need the data item to display inline.

{{ designSystemExample({
"iframe": {
    "title": "An example of the inline variation of the data item component",
    "url": "example-inline.html",
    "size": "s"
},
"partial": [
    {
    "type": "html",
    "name": 'digital-land-frontend/components/data-item/example-inline.html'
    },
    {
    "type": "jinja",
    "path": 'digital-land-frontend/components/data-item/example-inline.html'
    }
]
}) }}
