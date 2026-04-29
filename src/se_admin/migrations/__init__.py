"""se_admin migrations - composed action sequences, named recipes."""

from se_admin.migrations.python_package_profile import run_python_package_profile
from se_admin.migrations.python_tooling_profile import run_python_tooling_profile
from se_admin.migrations.python_version import run_python_version
from se_admin.migrations.replace_mkdocs_with_zensical import (
    run_replace_mkdocs_with_zensical,
)
from se_admin.migrations.workflow_names import run_workflow_names

__all__ = [
    "run_replace_mkdocs_with_zensical",
    "run_python_package_profile",
    "run_python_tooling_profile",
    "run_python_version",
    "run_workflow_names",
]
