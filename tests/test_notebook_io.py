import os
import json
import threading
import pytest
from nbformat import read, write
from nbformat.v4 import new_notebook, new_code_cell


# Helper function to create a notebook
def create_sample_notebook():
    nb = new_notebook()
    nb.cells.append(new_code_cell("print('Hello World')"))
    return nb


# -----------------------------
# TEST 1: Valid Save and Load
# -----------------------------
def test_valid_save_and_load(tmp_path):
    file_path = tmp_path / "test.ipynb"

    nb = create_sample_notebook()

    # FIXED
    write(nb, file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        loaded_nb = read(f, as_version=4)

    assert loaded_nb.cells[0].source == "print('Hello World')"


# -----------------------------
# TEST 2: Corrupted File Path
# -----------------------------
def test_corrupted_file_path():
    with pytest.raises(Exception):
        with open("fake_file.ipynb", "r") as f:
            read(f, as_version=4)


# -----------------------------
# TEST 3: Read-Only File
# -----------------------------
def test_read_only_file(tmp_path):
    file_path = tmp_path / "readonly.ipynb"

    nb = create_sample_notebook()

    write(nb, file_path)

    os.chmod(file_path, 0o444)

    with pytest.raises(PermissionError):
        with open(file_path, "w") as f:
            write(nb, f)


# -----------------------------
# TEST 4: Crash During Save
# -----------------------------
def test_crash_during_save(tmp_path):
    file_path = tmp_path / "crash.ipynb"

    with open(file_path, "w") as f:
        f.write("{broken json")

    with pytest.raises(Exception):
        with open(file_path, "r") as f:
            json.load(f)


# -----------------------------
# TEST 5: Concurrent Save
# -----------------------------
def test_concurrent_save(tmp_path):
    file_path = tmp_path / "concurrent.ipynb"

    nb1 = create_sample_notebook()
    nb2 = create_sample_notebook()
    nb2.cells[0].source = "print('Thread 2')"

    def save(nb):
        write(nb, file_path)  # FIXED

    t1 = threading.Thread(target=save, args=(nb1,))
    t2 = threading.Thread(target=save, args=(nb2,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    with open(file_path, "r", encoding="utf-8") as f:
        loaded_nb = read(f, as_version=4)

    assert loaded_nb is not None
    # trigger workflow
