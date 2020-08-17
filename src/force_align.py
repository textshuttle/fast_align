#!/usr/bin/env python3
import subprocess
import sys


# Simplified, non-threadsafe version for force_align.py adapted to work with python3
# Use the version in realtime for development
from typing import TextIO


def read_error_file(file: TextIO):
    T, m = '', ''
    for line in file:
        # expected target length = source length * N 1.37146
        if 'expected target length' in line:
            m = line.split()[-1]
        # final tension: N 10.3627
        elif 'final tension' in line:
            T = line.split()[-1]
    return T, m


class Aligner:
    def __init__(self,
                 fwd_params: str,
                 fwd_err: str,
                 rev_params: str,
                 rev_err: str,
                 heuristic='grow-diag-final-and'):

        fast_align = 'fast_align'
        atools = 'atools'

        with open(fwd_err) as f:
            fwd_T, fwd_m = read_error_file(f)

        with open(rev_err) as f:
            rev_T, rev_m = read_error_file(f)

        fwd_cmd = [fast_align, '-i', '-', '-d', '-T', fwd_T, '-m', fwd_m, '-f', fwd_params]
        rev_cmd = [fast_align, '-i', '-', '-d', '-T', rev_T, '-m', rev_m, '-f', rev_params, '-r']
        tools_cmd = [atools, '-i', '-', '-j', '-', '-c', heuristic]

        self.fwd_align = popen_io(fwd_cmd)
        self.rev_align = popen_io(rev_cmd)
        self.tools = popen_io(tools_cmd)

    def align(self, line: str):
        self.fwd_align.stdin.write(f'{line}\n')
        self.rev_align.stdin.write(f'{line}\n')
        # f words ||| e words ||| links ||| score
        fwd_line = self.fwd_align.stdout.readline().split('|||')[2].strip()
        rev_line = self.rev_align.stdout.readline().split('|||')[2].strip()
        self.tools.stdin.write(f'{fwd_line}\n')
        self.tools.stdin.write(f'{rev_line}\n')
        al_line = self.tools.stdout.readline().strip()
        return al_line

    def close(self):
        self.fwd_align.stdin.close()
        self.fwd_align.wait()
        self.rev_align.stdin.close()
        self.rev_align.wait()
        self.tools.stdin.close()
        self.tools.wait()


def popen_io(cmd):
    p = subprocess.Popen(
        cmd, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.DEVNULL,  # We don't need stderr of the subprocesses.
        text=True,  # Work with strings instead of bytes.
        bufsize=1  # Use line based buffering.
    )
    return p


def main():
    if len(sys.argv[1:]) < 4:
        sys.stderr.write('run:\n')
        sys.stderr.write('  fast_align -i corpus.f-e -d -v -o -p fwd_params >fwd_align 2>fwd_err\n')
        sys.stderr.write('  fast_align -i corpus.f-e -r -d -v -o -p rev_params >rev_align 2>rev_err\n')
        sys.stderr.write('\n')
        sys.stderr.write('then run:\n')
        sys.stderr.write(
            '  {} fwd_params fwd_err rev_params rev_err [heuristic] <in.f-e >out.f-e.gdfa\n'.format(sys.argv[0]))
        sys.stderr.write('\n')
        sys.stderr.write(
            'where heuristic is one of: (intersect union grow-diag grow-diag-final grow-diag-final-and) default=grow-diag-final-and\n')
        sys.exit(2)

    aligner = Aligner(*sys.argv[1:])

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        sys.stdout.write(f'{aligner.align(line.strip())}\n')
        sys.stdout.flush()

    aligner.close()


if __name__ == '__main__':
    main()
