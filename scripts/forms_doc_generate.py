#!/usr/bin/env python3
#
# Copyright (c) 2024 YunoHost Contributors
#
# This file is part of YunoHost (see https://yunohost.org)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import ast
import datetime
import subprocess
from pathlib import Path

from jinja2 import Template


TEMPLATE_FILE = Path(__file__).resolve().parent / "forms_doc_template.md.j2"

def get_current_commit(docdir: Path) -> str:
    p = subprocess.Popen(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=docdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout, stderr = p.communicate()

    current_commit = stdout.strip().decode("utf-8")
    return current_commit


def get_changelog_version(srcdir: Path) -> str:
    changelog_file = srcdir / "debian" / "changelog"
    version = changelog_file.open("r").readline().split()[1].strip("()")
    return version


##############################################################################


def dict_key_first(dict: dict, key) -> dict:
    value = dict.pop(key)
    return {key: value, **dict}


def list_config_panel(srcdir: Path) -> dict[str, str]:
    configpanel_file = srcdir / "src" / "utils" / "configpanel.py"

    # NB: This magic is because we want to be able to run this script outside of a YunoHost context,
    # in which we cant really 'import' the file because it will trigger a bunch of moulinette/yunohost imports...
    tree = ast.parse(configpanel_file.read_text())

    classes: dict[str, str] = {}

    for cl in reversed(tree.body):
        if isinstance(cl, ast.ClassDef):
            if cl.name in ["SectionModel", "PanelModel", "ConfigPanelModel"]:
                docstring = ast.get_docstring(cl)
                assert isinstance(docstring, str)
                classes[cl.name.replace("Model", "")] = docstring

    return classes


def list_form_options(srcdir: Path) -> dict[str, str]:
    configpanel_file = srcdir / "src" / "utils" / "form.py"

    # NB: This magic is because we want to be able to run this script outside of a YunoHost context,
    # in which we cant really 'import' the file because it will trigger a bunch of moulinette/yunohost imports...
    tree = ast.parse(configpanel_file.read_text())

    options: dict[str, str] = {}

    for cl in tree.body:
        if not isinstance(cl, ast.ClassDef):
            continue
        if not cl.name.endswith("Option"):
            continue
        if not isinstance(cl.body[0], ast.Expr):
            continue

        assert isinstance(cl.body[1], ast.AnnAssign)
        assert isinstance(cl.body[1].target, ast.Name)
        assert isinstance(cl.bases[0], ast.Name)

        # Determine the title of the section
        if cl.name == "BaseOption":
            name = "Common properties"

        elif cl.name == "BaseInputOption":
            name = "Common inputs properties"

        else:
            assert cl.body[1].target.id == "type"
            assert isinstance(cl.body[1].value, ast.Attribute)
            option_type = cl.body[1].value.attr

            if option_type == "display_text":
                # display_text is kind of legacy x_x
                continue

            name = f"`{option_type}`"

            if cl.bases:
                base_type = cl.bases[0].id.replace("Option", "")
                base_type = base_type.replace("Base", "").lower()
                name += f" ({base_type})"

        docstring = ast.get_docstring(cl)
        if docstring:
            options[name] = docstring

    # Dirty hack to have "Common properties" as first and "Common inputs properties" as 2nd in list
    options = dict_key_first(options, "Common inputs properties")
    options = dict_key_first(options, "Common properties")
    return options


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", type=Path, required=True, help="Input yunohost source directory")
    parser.add_argument("--output", "-o", type=Path, required=True)
    args = parser.parse_args()

    template_data = {
        "configpanel": list_config_panel(args.input),
        "options": list_form_options(args.input),
        "date": datetime.datetime.now().strftime("%d/%m/%Y"),
        "version": get_changelog_version(args.input),
        "doc_commit": get_current_commit(Path(__file__).parent),
        "src_commit": get_current_commit(args.input),
    }

    template = Template(TEMPLATE_FILE.read_text())
    result = template.render(**template_data)
    args.output.write_text(result)


if __name__ == "__main__":
    main()
