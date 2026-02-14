import sys


def check_venv() -> int:
    """Check if virtual environment is active.

    Returns:
        0 if venv is active, 1 otherwise
    """
    is_venv_active = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if not is_venv_active:
        print("ERROR: Virtual environment not active!")
        print("Please activate your venv: .venv\\Scripts\\Activate")
        return 1

    print("Virtual environment is active")
    return 0


if __name__ == "__main__":
    sys.exit(check_venv())
