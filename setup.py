from setuptools import setup


setup(
    name="hydraclient",
    description="A low-level python client for Hydra services",
    packages=["hydraclient", ],
    install_requires=[
        "rdflib",
        "django==1.4.8",
        "requests",
        "httpcache",
        "webob",
        "pyld",
    ]
)
