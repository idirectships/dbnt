"""Adapters for different AI systems."""

from dbnt.adapters.base import BaseAdapter
from dbnt.adapters.claude_code import ClaudeCodeAdapter
from dbnt.adapters.generic import GenericAdapter

__all__ = ["BaseAdapter", "ClaudeCodeAdapter", "GenericAdapter"]
