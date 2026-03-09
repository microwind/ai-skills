#!/usr/bin/env python3
import cProfile
import pstats
import sys
from io import StringIO

def run_profiler(code_snippet):
    '''Run profiler on code snippet'''
    pr = cProfile.Profile()
    pr.enable()

    try:
        exec(code_snippet)
    except Exception as e:
        return f"Error: {e}"

    pr.disable()

    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)

    return s.getvalue()

if __name__ == '__main__':
    code = sys.stdin.read()
    report = run_profiler(code)
    print(report)
