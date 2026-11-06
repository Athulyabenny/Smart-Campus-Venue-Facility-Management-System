"""
Smart Campus & Student Operations: Master Entry Point
File: run.py

Usage:
    python run.py --web        # Launches the Interactive Web Dashboard (Flask)
    python run.py --cli        # Launches the Terminal CLI Menu (Viva demo)
    python run.py --test       # Executes all unit tests
    python run.py --benchmark  # Runs algorithmic scalability benchmarks
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def launch_web(port=None):
    from web.app import run_server
    if port is None:
        # Check CLI arguments for --port <num> or a trailing port number
        for i, a in enumerate(sys.argv):
            if a in ["--port", "-p"] and i + 1 < len(sys.argv):
                try:
                    port = int(sys.argv[i + 1])
                    break
                except ValueError:
                    pass
            elif a.isdigit() and len(a) >= 4:
                port = int(a)
                break
    run_server(port=port)


def launch_cli():
    from cli.main_cli import main
    main()


def run_tests():
    import unittest
    loader = unittest.TestLoader()
    start_dir = os.path.join(PROJECT_ROOT, "tests")
    suite = loader.discover(start_dir)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


def run_benchmarks():
    from benchmarks.performance_benchmark import run_full_benchmark_suite
    run_full_benchmark_suite()


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--web", "-w"]:
            launch_web()
        elif arg in ["--cli", "-c"]:
            launch_cli()
        elif arg in ["--test", "-t"]:
            run_tests()
        elif arg in ["--benchmark", "-b"]:
            run_benchmarks()
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python run.py [--web | --cli | --test | --benchmark]")
    else:
        print("\n=======================================================")
        print("   SMART CAMPUS & STUDENT OPERATIONS: ALGORITHMIC ENGINE")
        print("=======================================================")
        print("  [1] Launch Interactive Web Dashboard (Browser GUI)")
        print("  [2] Launch Interactive Terminal CLI (Viva Presentation)")
        print("  [3] Run Unit Test Suite (12 Unit Tests)")
        print("  [4] Run Algorithmic Performance Benchmarks")
        print("  [5] Exit")
        print("-------------------------------------------------------")
        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            launch_web()
        elif choice == "2":
            launch_cli()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            run_benchmarks()
        else:
            print("Exiting.")


if __name__ == "__main__":
    main()
