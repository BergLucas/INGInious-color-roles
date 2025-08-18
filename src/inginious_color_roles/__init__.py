from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING, Any, Callable

from docutils.nodes import Node, raw
from docutils.parsers.rst import roles

if TYPE_CHECKING:
    from docutils.parsers.rst.states import Inliner
    from inginious.client.client import Client
    from inginious.frontend.course_factory import CourseFactory
    from inginious.frontend.plugin_manager import PluginManager

__version__ = "0.1.0"


def create_color_role(color: str) -> Callable:
    """Create a reStructuredText role that colors text.

    Args:
        color: The color to apply to the text.

    Returns:
        A callable that implements the role.
    """

    def role(  # noqa: PLR0913
        name: str,
        rawtext: str,
        text: str,
        lineno: int,
        inliner: Inliner,
        options: dict[str, Any] | None = None,
        content: list[str] | None = None,
    ) -> tuple[list[Node], list[Node]]:
        return [
            raw(
                "",
                f'<span style="color:{escape(color)}">{escape(text)}</span>',
                format="html",
            )
        ], []

    return role


def init(
    plugin_manager: PluginManager,
    course_factory: CourseFactory,
    client: Client,
    plugin_config: dict[str, Any],
) -> None:
    """Initialises the color roles plugin.

    Args:
        plugin_manager: The plugin manager instance.
        course_factory: The course factory instance.
        client: The client instance.
        plugin_config: The plugin configuration dictionary.
    """
    colors: dict[str, str] = plugin_config.get("colors", {})

    for role_name, color in colors.items():
        roles.register_local_role(role_name, create_color_role(color))
