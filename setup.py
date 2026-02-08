"""Setup file for MkDocs plugins."""

from setuptools import setup, find_packages

setup(
    name="agentprotocol-mkdocs-plugins",
    version="0.1.0",
    packages=find_packages(where="docs"),
    package_dir={"": "docs"},
    entry_points={
        "mkdocs.plugins": [
            "test-examples = plugins.test_examples:TestExamplesPlugin",
        ]
    },
    install_requires=[
        "mkdocs>=1.4.0",
    ],
)
