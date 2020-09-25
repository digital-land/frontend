from setuptools import setup

setup(
    name="digital-land-frontend",
    version="0.1.1",
    author="Digital land",
    description="Reusable frontend code for digital land services and products",
    license="MIT",
    packages=["digital_land_frontend"],
    package_data={'digital-land-frontend': ['templates/**.*']},
    python_requires=">=3.5",
    install_requires=[
        "jinja2",
        "govuk-jinja-components @ git+https://github.com/digital-land/govuk-jinja-components.git@base-template",
    ],
)
