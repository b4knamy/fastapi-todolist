import pytest
import os

if __name__ == "__main__":

    os.environ.setdefault("USE_DATABASE_TEST", "1")
    exit_code = pytest.main()
    exit(code=exit_code)
