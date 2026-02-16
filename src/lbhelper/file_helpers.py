from pathlib import Path
import tempfile
import jinja2
import requests

from lbhelper.defaults import DEFAULT_LOGGER


def render_template_to_file(template_path: Path, target_path: Path = None, **kwargs) -> Path:
    """
    Render template to a temp file and returns path of it. Generally used with ``pathlib.Path`` fields
    in :class:`Targets`.

    :param pathlib.Path template_path: Template path.
    :param pathlib.Path,Optional target_path: Target path. If not given, then writing to a temporary file.
    :param kwargs: Additional kwargs for template.
    :return: Path of rendered file.
    :rtype: pathlib.Path
    """

    DEFAULT_LOGGER.info(f"Rendering template {template_path} to {target_path} ...")

    rendered_template = render_template_to_string(template_path, **kwargs)
    written_file_path = target_path

    if target_path is None:
        DEFAULT_LOGGER.info(f"Rendering template to {target_path} ...")

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write(rendered_template)
            written_file_path = Path(tmp.name)
    else:
        DEFAULT_LOGGER.info(f"Ensuring parent directory of {target_path} ...")
        target_path.parent.mkdir(parents=True, exist_ok=True)

        DEFAULT_LOGGER.info(f"Rendering template to {target_path} ...")
        with target_path.open(mode="w+", encoding="utf-8") as f:
            f.write(render_template_to_string(template_path, **kwargs))

    DEFAULT_LOGGER.info(f"Template {template_path} rendered to {target_path}.")

    return written_file_path

def render_template_to_string(template_path: Path, **kwargs) -> str:
    """
    Render template to string. Generally used as input as other templates. For example, when defining a
    :class:`HooKScript` to write a config file, the config file itself can be defined in another template
    and passed to the :class:`HookScript`, which decouples the :class:`HookScript` and the config file.

    :param pathlib.Path template_path: Template path.
    :param kwargs: Additional kwargs for template.
    :return: Rendered string.
    :rtype: str
    """
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path.parent), undefined=jinja2.StrictUndefined)
    template = env.get_template(template_path.name)
    return template.render(**kwargs)


def escape_string_for_shell_script(s: str) -> str:
    """
    Escape "\" and "$". Useful when writing string to file via shell scripts. For instance, when writing strings
    via:
    ```
    cat > file<<EOL
    $SOME_STRING
    EOL
    ```
    The "\" and "$" of  $SOME_STRING need to be escaped. Otherwise, they'll be treated as special characters from
    source script and cause unexpected results.

    :param str s: String to escape.
    :return: Escaped string.
    :rtype: str
    """
    patterns_dict = {
        "\\": "\\\\",
        "$": "\\$",
    }

    for pattern, alter in patterns_dict.items():
        s = s.replace(pattern, alter)

    return s


def download_file(url: str) -> Path:
    """
    Download file from url as temporary file and return path of it. Generally used with ``pathlib.Path`` fields
    in :class:`Targets`.

    :param str url: URL to download.
    :return: Path of downloaded file.
    :rtype: pathlib.Path
    """
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
            for chunk in r.iter_content(chunk_size=8192):
                tmp.write(chunk)
    return Path(tmp.name)
