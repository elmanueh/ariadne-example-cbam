from __future__ import annotations

import os
import sys
from pathlib import Path

CONFIG_PATH = Path("ariadne.yml")
DEFAULT_ARTIFACTS_DIR = "dist/artifacts"


def main() -> int:
    if not CONFIG_PATH.is_file():
        print("::error::ariadne.yml must exist in the repository root.")
        return 1

    artifacts_dir = DEFAULT_ARTIFACTS_DIR
    graph_output = ""
    inside_outputs = False

    for raw_line in CONFIG_PATH.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indentation = len(raw_line) - len(raw_line.lstrip())
        line = raw_line.strip()

        if indentation == 0:
            inside_outputs = line == "outputs:"
            continue

        if inside_outputs and line.startswith("artifacts_dir:"):
            value = _yaml_scalar(line.split(":", maxsplit=1)[1])
            if value:
                artifacts_dir = value

        if inside_outputs and line.startswith("graph_file:"):
            graph_output = _yaml_scalar(line.split(":", maxsplit=1)[1])

    if not _is_repo_relative(artifacts_dir):
        print(
            "::error::outputs.artifacts_dir must be repository-relative and cannot contain '..'."
        )
        return 1

    if graph_output and not _is_repo_relative(graph_output):
        print(
            "::error::outputs.graph_file must be repository-relative and cannot contain '..'."
        )
        return 1

    output_path = os.environ.get("GITHUB_OUTPUT")
    lines = [
        f"artifacts-dir={artifacts_dir}",
        f"graph-output-path={graph_output}",
    ]
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as output:
            output.write("\n".join(lines))
            output.write("\n")
    else:
        print("\n".join(lines))

    return 0


def _yaml_scalar(raw_value: str) -> str:
    value = raw_value.strip()
    if not value:
        return ""

    if value[0] in {"'", '"'}:
        quote = value[0]
        end = value.find(quote, 1)
        if end != -1:
            return value[1:end]

    return value.split("#", maxsplit=1)[0].strip()


def _is_repo_relative(path_value: str) -> bool:
    path = Path(path_value)
    return not path.is_absolute() and ".." not in path.parts


if __name__ == "__main__":
    sys.exit(main())
