# Python imports

# 3rd Party imports

# E12 Imports
from epilepsy12.constants.colors import *

class ChartHTML:
    """Simple container class to hold chart HTML content.

    Useful to avoid lots of rendered html if trying to print a view's context.
    """

    def __init__(self, chart_html: str, name: str):
        self.chart_html = chart_html
        self.name = name

    def get_html(self) -> str:
        return self.chart_html

    def get_name(self) -> str:
        return self.name

    def __str__(self):
        return f"<{self.get_name()} ChartHTML object>"

    def __repr__(self):
        return f"<{self.get_name()} ChartHTML object>"




