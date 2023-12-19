
import os
from importlib.resources import files
from pathlib import Path

from jinja2 import Template

from ..enums import Command
from .constants import CURRENT_REVISION_KEY, LATEST_REVISION_KEY
from .pydantic_models import MirascopeSettings
from .utils import (check_status, find_prompt_path, get_prompt_versions,
                    get_user_mirascope_settings, update_version_text_file,
                    write_prompt_to_template)


def add(args):
    """Adds the given prompt to the specified version directory.

    The contents of the prompt in the users prompts directory are copied to the version directory
    with the next revision number, and the version file is updated with the new revision.

    Typical Usage Example:

        mirascope add <directory_name>

    Args:
        args: The directory name passed to the add command.
    Returns:
        None
    Raises:
        FileNotFoundError: If the file is not found in the specified prompts directory.
    """
    mirascope_settings = get_user_mirascope_settings()
    version_directory_path = mirascope_settings.versions_location
    prompt_directory_path = mirascope_settings.prompts_location
    version_file_name = mirascope_settings.version_file_name
    directory_name: str = args.file
    # Check status before continuing
    used_prompt_path = check_status(mirascope_settings, directory_name)
    if not used_prompt_path:
        print("No changes detected.")
        return
    class_directory = os.path.join(version_directory_path, directory_name)
    version_file_path = os.path.join(class_directory, version_file_name)
    if not os.path.exists(class_directory):
        os.makedirs(class_directory)
    versions = get_prompt_versions(version_file_path)
    # Open user's prompt file
    with open(
        f"{prompt_directory_path}/{directory_name}.py", "r+", encoding="utf-8"
    ) as file:
        # Increment revision id
        if versions.latest_revision is None:
            # first revision
            revision_id = "0001"
        else:
            # default branch with incrementation
            latest_revision_id = versions.latest_revision
            revision_id = f"{int(latest_revision_id)+1:04}"
        # Create revision file
        with open(
            f"{class_directory}/{revision_id}_{directory_name}.py",
            "w+",
            encoding="utf-8",
        ) as file2:
            custom_variables = {
                "prev_revision_id": versions.current_revision,
                "revision_id": revision_id,
            }
            file2.write(write_prompt_to_template(file.read(), Command.ADD, custom_variables))
            keys_to_update = {
                CURRENT_REVISION_KEY: revision_id,
                LATEST_REVISION_KEY: revision_id,
            }
            update_version_text_file(version_file_path, keys_to_update)
    print(f"Adding {version_directory_path}/{revision_id}_{directory_name}.py")


def status(args):
    """
    Checks the status of the current prompt or prompts.

    If a prompt is specified, the status of that prompt is checked. Otherwise, the status of all
    promps are checked. If a prompt has changed, the path to the prompt is printed.

    Typical Usage Example:
            
        mirascope status <directory_name>
        or
        mirascope status

    Args:
        args: The directory name (optional) passed to the status command.
    Returns:
        None
    Raises:
        FileNotFoundError: If the file is not found in the specified prompts directory.

    """
    mirascope_settings = get_user_mirascope_settings()
    version_directory_path = mirascope_settings.versions_location
    directory_name: str = args.file
    # If a prompt is specified, check the status of that prompt
    if directory_name:
        used_prompt_path = check_status(mirascope_settings, directory_name)
        if used_prompt_path:
            print(f"Prompt {used_prompt_path} has changed.")
        else:
            print("No changes detected.")
    else:
        directores_changed: list[str] = []
        # Otherwise, check the status of all prompts
        for _, directories, _ in os.walk(version_directory_path):
            for directory in directories:
                used_prompt_path = check_status(mirascope_settings, directory)
                if used_prompt_path:
                    directores_changed.append(used_prompt_path)
        if len(directores_changed) > 0:
            print("The following prompts have changed:")
            for prompt in directores_changed:
                print(f"\t{prompt}".expandtabs(4))
        else:
            print("No changes detected.")


def use(args):
    """
    Uses the version and prompt specified by the user.

    The contents of the prompt in the version directory are copied to the users prompts directory,
    based on the version specified by the user. The version file is updated with the new revision.

    Typical Usage Example:
    
            mirascope use <prompt_directory> <version>
    Args:
        args: The prompt_directory name and version passed to the use command.
    Returns:
        None
    Raises:
        FileNotFoundError: If the file is not found in the specified prompts directory.
    """
    directory_name = args.prompt_directory
    version = args.version
    mirascope_settings = get_user_mirascope_settings()
    used_prompt_path = check_status(mirascope_settings, directory_name)
    # Check status before continuing
    if used_prompt_path:
        print("Changes detected, please add or delete changes first.")
        print(f"\tmirascope add {directory_name}".expandtabs(4))
        return
    version_directory_path = mirascope_settings.versions_location
    prompt_directory_path = mirascope_settings.prompts_location
    version_file_name = mirascope_settings.version_file_name
    class_directory = os.path.join(version_directory_path, directory_name)
    revision_file_path = find_prompt_path(class_directory, version)
    version_file_path = os.path.join(class_directory, version_file_name)
    # Open versioned prompt file
    with open(revision_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    prompt_file_name = os.path.join(prompt_directory_path, f"{directory_name}.py")
    # Write to user's prompt file
    with open(prompt_file_name, "w+", encoding="utf-8") as file2:
        file2.write(write_prompt_to_template(content, Command.USE))
    # Update version file with new current revision
    keys_to_update = {
        CURRENT_REVISION_KEY: version,
    }
    update_version_text_file(version_file_path, keys_to_update)
    print(f"Using {revision_file_path}")


def init(args):
    """
    Initializes the mirascope project.

    Creates the project structure and files needed for mirascope to work.

    Sample project structure:
    |
    |-- mirascope.ini
    |-- mirascope
    |   |-- prompt_template.j2
    |   |-- versions/
    |   |   |-- <directory_name>/
    |   |   |   |-- version.txt
    |   |   |   |-- <revision_id>_<directory_name>.py
    |-- prompts/

    Typical Usage Example:
        
        mirascope init mirascope

    Args:
        args: The mirascope directory name passed to the init command.
    Returns:
        None
    """
    destination_dir = Path.cwd()
    directory_name = args.directory
    versions_directory = os.path.join(directory_name, "versions")
    os.makedirs(versions_directory, exist_ok=True)
    print(f"Creating {versions_directory}")
    # Create the 'mirascope.ini' file in the current directory with some default values
    ini_settings = MirascopeSettings(
        mirascope_location="mirascope",
        versions_location="versions",
        prompts_location="prompts",
        version_file_name="version.txt",
    )
    # Get templates from the mirascope.cli.generic package
    generic_file_path = files("mirascope.cli.generic")
    ini_path = generic_file_path.joinpath("mirascope.ini.j2")
    with open(ini_path, "r", encoding="utf-8") as file:
        template = Template(file.read())
        rendered_content = template.render(ini_settings.model_dump())
        destination_file_path = destination_dir / "mirascope.ini"
        with open(destination_file_path, "w", encoding="utf-8") as destination_file:
            destination_file.write(rendered_content)
            print(f"Creating {destination_file_path}")
    # Create the 'prompt_template.j2' file in the mirascope directory specified by user
    prompt_template_path = generic_file_path.joinpath("prompt_template.j2")
    with open(prompt_template_path, "r", encoding="utf-8") as file:
        content = file.read()
    template_path = os.path.join(directory_name, "prompt_template.j2")
    with open(template_path, "w", encoding="utf-8") as file:
        file.write(content)
        print(f"Creating {template_path}")

    print("Initialization complete.")
