from setuptools import setup

setup(
    name="digital-land-frontend",
    version="0.1.0",
    author="Digital land",
    description="Reusable frontend code for digital land services and products",
    license="MIT",
    packages=["digital_land_frontend"],
    package_data={'digital-land-frontend': ['templates/**.*']},
    python_requires=">=3.5",
    install_requires=[
        "jinja2",
    ],
)
