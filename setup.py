import glob
import os

from setuptools import setup, find_packages

components = []
directories_html = glob.glob("digital_land_frontend/**/**/*.html", recursive=True)
directories_jinja = glob.glob("digital_land_frontend/**/**/*.jinja", recursive=True)

for directory in directories_html:
    components.append(
        os.path.relpath(os.path.dirname(directory), "digital_land_frontend") + "/*.html"
    )

for directory in directories_jinja:
    components.append(
        os.path.relpath(os.path.dirname(directory), "digital_land_frontend")
        + "/*.jinja"
    )

setup(
    name="digital-land-frontend",
    version="0.46",
    author="Digital land",
    description="Reusable frontend code for digital land services and products",
    license="MIT",
    packages=find_packages(),
    package_data={"digital-land-frontend": components},
    python_requires=">=3.5",
    install_requires=[
        "CacheControl",
        # issue with frames ..
        "jinja2==2.11.3",
        "lockfile",
        "validators",
        "requests",
        "shapely",
        "govuk_jinja_components @ git+https://github.com/digital-land/govuk-jinja-components.git#egg=govuk_jinja_components",
        "markdown",
    ],
    include_package_data=True,
)
