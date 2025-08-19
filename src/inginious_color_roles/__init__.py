from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Callable

from docutils.nodes import Node, inline, system_message
from docutils.parsers.rst import roles
from flask import Response
from inginious.frontend.pages.utils import INGIniousPage

if TYPE_CHECKING:
    from docutils.parsers.rst.states import Inliner
    from inginious.client.client import Client
    from inginious.frontend.course_factory import CourseFactory
    from inginious.frontend.plugin_manager import PluginManager

__version__ = "0.1.0"


class ColorsGenerator(INGIniousPage):
    """Serve color roles for reStructuredText."""

    def __init__(self, colors: dict[str, str | None]) -> None:
        """Initialize the color roles generator."""
        self.colors = colors

    def GET(self) -> Response:  # noqa: N802
        """Serve color roles for reStructuredText.

        Returns:
            The color roles.
        """
        return Response(
            response="\n".join(
                f".{name} {{color: {color}}}"
                for name, color in self.colors.items()
                if color is not None
            ),
            status=200,
            mimetype="text/css",
        )


def create_role(role_name: str) -> Callable:
    """Create a reStructuredText role.

    Args:
        role_name: The name of the role.

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
    ) -> tuple[list[Node], list[system_message]]:
        parsed_nodes, messages = inliner.parse(
            text,
            lineno,
            SimpleNamespace(
                reporter=inliner.reporter,
                document=inliner.document,
                language=inliner.language,
            ),
            inliner.parent,
        )

        return [inline("", "", *parsed_nodes, classes=[role_name])], messages

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
    colors: dict[str, str | None] = plugin_config.get("colors", {})

    for role_name in colors:
        roles.register_local_role(role_name, create_role(role_name))

    plugin_manager.add_page(
        "/plugins/color_roles/generated/css/colors.css",
        ColorsGenerator.as_view("color_roles_generated", colors=colors),
    )
    plugin_manager.add_hook(
        "css",
        lambda: "/plugins/color_roles/generated/css/colors.css",
    )
