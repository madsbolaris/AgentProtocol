"""Setup for custom MkDocs plugins."""

from setuptools import setup, find_packages

setup(
    name='mkdocs-test-snippets',
    version='1.0.0',
    description='Extract code snippets directly from test files',
    author='Agent Protocol Contributors',
    packages=find_packages(),
    install_requires=[
        'mkdocs>=1.5.0',
    ],
    entry_points={
        'mkdocs.plugins': [
            'test_snippets = mkdocs_plugins.test_snippets:TestSnippetsPlugin',
        ]
    }
)
