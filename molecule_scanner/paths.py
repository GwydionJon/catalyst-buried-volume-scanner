import os
import sys
import glob
from tempfile import mkdtemp
from tkinter.filedialog import askdirectory

_data_dir = None


def set_data_directory(directory=None, create_dir=False):
    """Set a custom root directory to locate data files
    :param directory:
        The name of the custom data directory.
    :type directory: str
    :param create_dir:
        Whether adaptivefiltering should create the directory if it does
        not already exist.
    :type created_dir: bool
    """
    if directory is None:
        directory = askdirectory()
    # Check existence of the given data directory
    elif not os.path.exists(directory):
        if create_dir:
            os.makedirs(directory, exist_ok=True)
        else:
            raise FileNotFoundError(
                f"The given data directory '{directory}' does not exist (Use create_dir=True to automatically create it)!"
            )

    # Update the module variable
    global _data_dir
    _data_dir = directory


def get_temporary_workspace():
    """Return a temporary directory that persists across the session
    This should be used as the working directory of any filter workflows
    or other operations that might produce spurious file outputs.
    """
    global _tmp_dir
    if _tmp_dir is None:
        _tmp_dir = mkdtemp()

    return _tmp_dir.name


def load_executable():

    sambvcax_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "executables"
    )
    if sys.platform == "win32":
        sambvca21_path = os.path.join(sambvcax_dir, "sambvca21.exe")
    else:
        sambvca21_path = os.path.join(sambvcax_dir, "sambvca21.x")

    return sambvca21_path


def locate_file(filename):
    """Locate a file on the filesystem
    This function abstracts the resolution of paths given by the user.
    It should be used whenever data is loaded from user-provided locations.
    The priority list for path resolution is the following:
    * If the given path is absolute, it is used as is.
    * If a path was set with :any:`set_data_directory` check whether
      the given relative path exists with respect to that directory
    * Check whether the given relative path exists with respect to
      the current working directory
    * Check whether the given relative path exists with respect to
      the specified XDG data directory (e.g. through the environment
      variable :code:`XDG_DATA_DIR`) - Linux/MacOS only.
    * Check whether the given relative path exists with respect to
      the package installation directory. This can be used to write
      examples that use package-provided data.
    :param filename: The (relative) filename to resolve
    :type filename: str
    :raises FileNotFoundError: Thrown if all resolution methods fail.
    :returns: The resolved, absolute filename
    """
    # If the path is absolute, do not change it
    if os.path.isabs(filename):
        return filename

    # Gather a list of candidate paths for relative path
    candidates = []

    # If set_data_directory was called, its result should take precedence
    if _data_dir is not None:
        candidates.append(os.path.join(_data_dir, filename))

    # search in example files
    candidates.append(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "example_data", "mad25_p.xyz"
        )
    )

    # Use the current working directory
    candidates.append(os.path.join(os.getcwd(), filename))

    # Iterate through the list to check for file existence
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    raise FileNotFoundError(
        f"Cannot locate file {filename}, maybe use set_data_directory to point to the correct location. Tried the following: {', '.join(candidates)}"
    )
