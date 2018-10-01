#!/usr/bin/env python

import numpy as np
from prune_related import prune_related

if __name__ == '__main__':
    # Set random seed so the same result is produced every time.
    np.random.seed(0)

    # Construct a random 10 x 10 matrix according to a [0, 1] uniform distribution.
    n = 10
    A = np.random.rand(n, n)
    A = (A + A.transpose()) / 2  # Make symmetric.
    A[np.diag_indices(n)] = 0.5  # Set diagonal to 0.5.

    # Call method.
    mis = prune_related(A, 0.5)

    # The expected result.
    mis_correct = set([0, 9, 4, 6])

    # Compare result with expected result. Raise error if there is a difference.
    assert mis == mis_correct, "Unit test failed. Method 'prune_related' did not return expected result."

    print("Unit test successful.")

