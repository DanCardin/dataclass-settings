import contextlib
from unittest.mock import mock_open, patch


@contextlib.contextmanager
def env_setup(env={}, files={}):
    def exists(path):
        return path in files

    def choose_file(path, *_, **__):
        if "pdbrc" in path:
            return mock_open(read_data="")(path)
        return mock_open(read_data=files[path])(path)

    env_patch = patch("os.environ", new=env)
    files_patch = patch("builtins.open", new=choose_file)
    exists_patch = patch("os.path.exists", new=exists)

    with env_patch, files_patch, exists_patch:
        yield
