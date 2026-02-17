"""MkDocs custom plugins and extensions."""

from .test_snippets import TestSnippetsPlugin
from .hashicorp_tabs import HashiCorpTabsExtension, makeExtension

__all__ = ['TestSnippetsPlugin', 'HashiCorpTabsExtension', 'makeExtension']
