"""
Module with miscellaneous functions. 
"""
import inspect
from IPython.display import display, HTML


def _get_info(obj: object) -> str:
    info = None
    if obj.__doc__ is not None:
        info = inspect.getdoc(obj)
    if callable(obj) and not inspect.isclass(obj):
        signature = inspect.signature(obj)
        if signature.parameters:
            info += (
                "\n\n"
                "Parameter Types & Defaults\n"
                "--------------------------\n"
            )
            n = len(signature.parameters)
            for i, param in enumerate(signature.parameters.values()):
                if param.name != 'self':
                    param_str = str(param)
                    if len(param_str) > 80:
                        param_str = param_str[:80] + '...'
                    info += param_str
                    if i < (n - 1):
                        info += '\n'
    return info


def styled_message(
    message: str,
    style: str = "info",
    title: str = None,
    collapsible: bool = False
) -> None:
    """
    Displays the message inside a styled HTML message box.

    Parameters
    ----------
    message:
        Message text to display.
    style: {"info", "warning", "success", "error", "note"}
        Determines the visual style of the message box.
    title: optional
        Overrides the default title of the styled message box.
    collapsible: optional, default False
        Indicates whether the message box should be collapsible or not.

    Returns
    -------
    None
    """
    styles = {
        "info": {
            "bg": "#e7f3fe",
            "color": "#084298",
            "border": "#2196F3",
            "icon": "ℹ️",
            "title": "Info"
        },
        "warning": {
            "bg": "#fff3cd",
            "color": "#664d03",
            "border": "#ffcc00",
            "icon": "⚠️",
            "title": "Warning"
        },
        "success": {
            "bg": "#d1e7dd",
            "color": "#0f5132",
            "border": "#28a745",
            "icon": "✅",
            "title": "Success"
        },
        "error": {
            "bg": "#f8d7da",
            "color": "#842029",
            "border": "#dc3545",
            "icon": "❌",
            "title": "Error"
        },
        "note": {
            "bg": "#fefefe",
            "color": "#333333",
            "border": "#999999",
            "icon": "📝",
            "title": "Note"
        }
    }

    s = styles.get(style, styles["info"])
    icon = s["icon"]
    title_text = title if title else s["title"]
    content_html = f"""
    <strong>{icon} {title_text}</strong><pre style="background-color:{s['bg']}; color:{s['color']};">{message}</pre>
    """
    if collapsible:
        html = f"""
        <details style="background-color:{s['bg']}; color:{s['color']}; padding:10px;
                        border-left:5px solid {s['border']}; border-radius:4px; margin-top:5px;">
            <summary style="cursor:pointer; font-weight:bold;">{icon} {title_text}</summary>
            <div style="margin-top:10px;"><pre style="background-color:{s['bg']}; color:{s['color']};">{message}</pre></div>
        </details>
        """
    else:
        html = f"""
        <div style="background-color:{s['bg']}; color:{s['color']}; padding:10px;
                    border-left:5px solid {s['border']}; border-radius:4px; margin-top:5px;">
            {content_html}
        </div>
        """
    display(HTML(html))


def show_docs(obj: object, stylish: bool = False) -> None:
    """
    Prints the docstring of `obj` to screen.

    Inside a Jupyter notebook the option `stylish` can be set to True to display
    the docstring in a collapsible info box.
    """
    info = _get_info(obj)
    if not stylish:
        print(info)
    styled_message(info, collapsible=True)


__all__ = [
    "styled_message",
    "show_docs"
]
