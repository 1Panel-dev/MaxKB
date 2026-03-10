# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： init_jinja.py
    @date：2025/12/1 17:16
    @desc:
"""
from typing import Any

from jinja2.sandbox import SandboxedEnvironment
from langchain_core.prompts.string import DEFAULT_FORMATTER_MAPPING, _HAS_JINJA2


def jinja2_formatter(template: str, /, **kwargs: Any) -> str:
    """Format a template using jinja2.

    *Security warning*:
        As of LangChain 0.0.329, this method uses Jinja2's
        SandboxedEnvironment by default. However, this sand-boxing should
        be treated as a best-effort approach rather than a guarantee of security.
        Do not accept jinja2 templates from untrusted sources as they may lead
        to arbitrary Python code execution.

        https://jinja.palletsprojects.com/en/3.1.x/sandbox/

    Args:
        template: The template string.
        **kwargs: The variables to format the template with.

    Returns:
        The formatted string.

    Raises:
        ImportError: If jinja2 is not installed.
    """
    if not _HAS_JINJA2:
        msg = (
            "jinja2 not installed, which is needed to use the jinja2_formatter. "
            "Please install it with `pip install jinja2`."
            "Please be cautious when using jinja2 templates. "
            "Do not expand jinja2 templates using unverified or user-controlled "
            "inputs as that can result in arbitrary Python code execution."
        )
        raise ImportError(msg)

    # Use a restricted sandbox that blocks ALL attribute/method access
    # Only simple variable lookups like {{variable}} are allowed
    # Attribute access like {{variable.attr}} or {{variable.method()}} is blocked
    return SandboxedEnvironment().from_string(template).render(**kwargs)


def run():
    DEFAULT_FORMATTER_MAPPING['jinja2'] = jinja2_formatter
