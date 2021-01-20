import os
import numbers
import validators
from jinja2 import evalcontextfilter, Markup

from .jinja_filters.mappers import OrganisationMapper, GeographyMapper


def get_jinja_template_raw(template_file_path):
    if template_file_path:
        if os.path.exists(template_file_path):
            file = open(template_file_path, "r")
            return file.read()
    return None


@evalcontextfilter
def make_link(eval_ctx, url):
    """
    Converts a url string into an anchor element.

    Requires autoescaping option to be set to True
    """
    if url is not None:
        if validators.url(url):
            anchor = f'<a class="govuk-link" href="{url}">{url}</a>'
            if eval_ctx.autoescape:
                return Markup(anchor)
    return url


def is_valid_uri(uri):
    """
    Checks if a string is valid URI
    """
    if validators.url(uri):
        return True
    return False


def float_to_int(v):
    if v:
        return int(float(v))
    return ""


def commanum(v):
    """
    Makes large numbers readable by adding commas

    E.g. 1000000 -> 1,000,000
    """
    if isinstance(v, numbers.Number):
        return "{:,}".format(v)
    return v


organisation_mapper = OrganisationMapper()


def organisation_id_to_name_filter(id):
    """
    Maps organistion id to the name of the organisation

    E.g. local-authority-eng:HAG -> Harrogate Borough Council
    """
    return organisation_mapper.get_by_key(id)


geography_mapper = GeographyMapper()


def geography_to_name_filter(id):
    """
    Maps geography to name

    E.g. parish:E04001457 -> Aston Clinton
    """
    return geography_mapper.get_name(id)


def geography_to_url_filter(id):
    """
    Maps geograpahy to a link for the relevant geograpahy page

    E.g. parish:E04001457 -> https://digital-land.github.io/parish/E04001465/
    """
    return geography_mapper.get_url(id)


def geography_to_geometry_url_filter(id):
    """
    Maps geograpahy to a link for the relevant geometry geojson file

    E.g. parish:E04001457 -> https://digital-land.github.io/parish/E04001465/geometry.geojson
    """

    return geography_mapper.get_geometry_url(id)


def strip_slug(s):
    parts = s.split("/")
    return parts[-1]
