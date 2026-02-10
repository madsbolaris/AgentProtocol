"""
Custom MkDocs plugin to render HashiCorp-style cards from simple markdown syntax.

Usage in markdown:
::cards:: cols=4

- title: Quick Start
  eyebrow: START HERE
  description: Get started in 30 minutes with your first agent
  url: quickstart/

- title: Concepts
  eyebrow: LEARN
  description: Understand core concepts and fundamentals
  url: concepts/

::/cards::
"""

import re
import yaml
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class HashiCorpCardsPreprocessor(Preprocessor):
    """Preprocessor to convert ::cards:: blocks to HashiCorp HTML."""

    CARDS_PATTERN = re.compile(
        r'::cards::(?:\s+cols=(\d+))?\s*\n(.*?)\n::/cards::',
        re.DOTALL | re.MULTILINE
    )

    def run(self, lines):
        """Process the markdown lines and replace card blocks."""
        text = '\n'.join(lines)

        def replace_cards(match):
            cols = match.group(1) or '4'  # Default to 4 columns
            cards_yaml = match.group(2)

            try:
                # Parse YAML cards data
                cards = yaml.safe_load(cards_yaml)
                if not cards:
                    return match.group(0)

                # Generate HashiCorp card HTML
                html = self._generate_card_html(cards)
                return html

            except yaml.YAMLError as e:
                print(f"Error parsing cards YAML: {e}")
                return match.group(0)

        text = self.CARDS_PATTERN.sub(replace_cards, text)
        return text.split('\n')

    def _generate_card_html(self, cards):
        """Generate HashiCorp-style card grid HTML."""
        cards_html = []

        for card in cards:
            title = card.get('title', '')
            eyebrow = card.get('eyebrow', '')
            description = card.get('description', '')
            url = card.get('url', '#')

            card_html = f'''    <li>
      <div class="hds-surface-mid card_root__RyqjV card-link_root__xgxTP">
        <a aria-label="{title}" class="card-link_anchor___5xoF" href="{url}">
          <span aria-hidden="true">&nbsp;</span>
        </a>
        <div class="collection-card_root__Q1__Q">
          <div>
            <div class="card-eyebrow_root__ATk89">
              <span class="card-eyebrow_text__qjsGs hds-typography-body-100 hds-font-weight-medium">{eyebrow}</span>
            </div>
            <div>
              <span class="card-title_text__F97Wj hds-typography-body-200 hds-font-weight-semibold">{title}</span>
            </div>
            <div class="card-description_root__uR7I9">
              <span class="truncate-max-lines_root__gjolq card-description_text__9YVkM hds-typography-body-200 hds-font-weight-regular" style="--max-lines: 3;">
                {description}
              </span>
            </div>
          </div>
        </div>
      </div>
    </li>'''

            cards_html.append(card_html)

        # Wrap cards in container
        full_html = f'''<div class="product-landing-blocks_cardsMargin__5Ql2T">
  <ul class="cards-grid-list_listRoot__xMWpJ cards-grid-list_minWidthMode__cPnEx cards-grid-list_allowThreeColumns__tkPIX" style="--grid-gap: 24px;">
{chr(10).join(cards_html)}
  </ul>
</div>'''

        return full_html


class HashiCorpCardsExtension(Extension):
    """Markdown extension for HashiCorp cards."""

    def extendMarkdown(self, md):
        """Register the preprocessor with markdown."""
        md.preprocessors.register(
            HashiCorpCardsPreprocessor(md),
            'hashicorp_cards',
            175  # Priority before other preprocessors
        )


def makeExtension(**kwargs):
    """Required function for markdown extensions."""
    return HashiCorpCardsExtension(**kwargs)
