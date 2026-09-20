# collectstatic_debug.py
import subprocess, sys, re, os, pathlib

def run_collectstatic():
    proc = subprocess.run(
        ["python", "manage.py", "collectstatic", "--noinput", "-v", "2"],
        cwd=r"c:\Users\chide\OneDrive\Desktop\mamas_mart-main\mamas_mart-main",
        capture_output=True,
        text=True,
    )
    return proc

def main():
    result = run_collectstatic()
    if result.returncode == 0:
        print("collectstatic succeeded")
        sys.exit(0)

    # Print full traceback for debugging
    print("collectstatic failed")
    print(result.stdout)
    print(result.stderr)

    # Look for a file path in the traceback – Windows paths usually contain a drive letter
    # Example pattern: C:\... or /c/... (unlikely on Windows)
    path_match = re.search(r"([A-Za-z]:\\\\[^\\n\\r]+)", result.stderr)
    if not path_match:
        path_match = re.search(r"(/[^\s]+)", result.stderr)  # fallback
    if not path_match:
        print("Could not auto-detect offending file.")
        sys.exit(1)

    bad_path = pathlib.Path(path_match.group(1))
    print(f"Detected problematic path: {bad_path}")

    # If it exists, rename it (add .broken) so we can restore later if needed
    if bad_path.is_file():
        backup = bad_path.with_suffix(bad_path.suffix + ".broken")
        bad_path.rename(backup)
        print(f"Renamed file to {backup}")
    elif bad_path.is_dir():
        backup = bad_path.with_name(bad_path.name + "_broken")
        bad_path.rename(backup)
        print(f"Renamed directory to {backup}")
    else:
        print("Path does not exist – maybe a broken symlink?")
        # Remove the symlink if it exists
        try:
            bad_path.unlink()
            print("Removed broken symlink")
        except Exception as e:
            print(f"Failed to remove: {e}")

    # Retry collectstatic
    print("\nRe-running collectstatic after fix …")
    retry = run_collectstatic()
    print(retry.stdout)
    print(retry.stderr)
    if retry.returncode == 0:
        print("collectstatic now succeeds!")
    else:
        print("Still failing – manual inspection may be required.")

if __name__ == "__main__":
    main()
