#!/usr/bin/env python

import numpy as np
import pandas as pd
from prune_related import prune_related
import subprocess

test_dir = 'test_data'

def test_method(A, thres, mis_correct):

    # Call method.
    mis = prune_related(A, thres)

    # Compare result with expected result.
    return mis == mis_correct

def test_cmdline(filename, thres, mis_correct, colnames='false', rownames='false'):
    outtemp = test_dir + '/pruned_idx_temp.txt'
    subprocess.call('python prune_related.py %s %f %s %s %s > /dev/null' %(filename, thres, outtemp, colnames, rownames), shell=True)

    mis = []
    with open(outtemp) as fid:
        for line in fid:
            mis.append(int(line[:-1]))

    mis = set(mis)

    return mis == mis_correct


if __name__ == '__main__':
    # Set random seed so the same result is produced every time.
    np.random.seed(0)

    # Construct a random 10 x 10 matrix according to a [0, 1] uniform distribution.
    thres = 0.5
    n = 10
    A = np.random.rand(n, n)
    A = (A + A.transpose()) / 2  # Make symmetric.
    A[np.diag_indices(n)] = 0.5  # Set diagonal to 0.5.

    # The expected result.
    mis_correct = set([0, 9, 4, 6])

    # Test calling the method directly.
    result1 = test_method(A, thres, mis_correct)

    # Test calling the python script from the shell.
    filename = test_dir + "/test_matrix.csv"
    A_df = pd.DataFrame(data=A)
    A_df.to_csv(filename, index=False, header=False)

    result2 = test_cmdline(filename, thres, mis_correct)

    # Same, but with column and row indexes.
    filename = test_dir + "/test_matrix_idx.csv"
    A_df.to_csv(filename, index=True, header=True)

    result3 = test_cmdline(filename, thres, mis_correct, colnames='true', rownames='true')

    errors = ''
    if not result1:
        errors += "Method 'prune_related' did not return expected result.\n"
    if not result2:
        errors += "Shell call to 'prune_related.py' did not return expected result.\n"
    if not result3:
        errors += "Shell call to 'prune_related.py' with matrix indexes did not return expected result.\n"

    assert result1 and result2, 'Errors have occurred:\n%s' % errors

    print("Unit test successful.")

