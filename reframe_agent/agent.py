"""
Thin adapter so ADK-CLI can find `root_agent`.
Real pipeline lives in app.agents.root.
"""

from app.agents.root import root_agent  # noqa: F401
