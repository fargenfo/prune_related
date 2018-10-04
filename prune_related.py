#!/usr/bin/env python
'''
This tool uses a heuristic to remove highly related individuals, based on a supplied kinship matrix and
a threshold. The output of the pruning procedure is then a list of individuals to keep.

The networkx (v2.1 or newer) Python library must be installed in the environment.

* Find relationships where kinship is above threshold
* Construct a graph, where two individuals are connected if they are highly related
* Find an approximate maximum independent set

A maximum independent set is a set of nodes of a graph such that no two nodes are connected in the graph. We
find an approximation to the maximum independent set using a NetworkX implementation of an algorithm
described in the following paper:

Boppana, R., & Halldorsson, M. M. (1990). Approximating maximum independent sets by excluding subgraphs. In Lecture Notes in Computer Science (including subseries Lecture Notes in Artificial Intelligence and Lecture Notes in Bioinformatics). https://doi.org/10.1007/3-540-52846-6_74

Usage:
    python prune_related.py [kinship matrix] [threshold] [output file] [column names] [row names]

Input:
    Kinship matrix:     Path to CSV file with kinship coefficients between individuals. The CSV must be comma
                        separated and have no column or row names.
    Threshold:          Pairs of individuals with kinship above this will be considered highly related.
    Output file:        Output will be written to a file with this path.
    Column names:       "true"/"false", whether or not the CSV file contains column names.
    Row names:          "true"/"false", whether or not the CSV file contains row names.

Example:
    python prune_related.py kinship_matrix.csv 0.0625 pruned_individuals.txt

Output:
    The indexes of individuals remaining after pruning are written to the specified output file.
'''

from networkx import from_numpy_matrix
from networkx.algorithms.approximation.independent_set import maximum_independent_set
import numpy as np
import pandas as pd
import sys


def prune_related(kc, kc_thres):
    '''
    Find the minimal set of individuals to keep by removing relationships based on
    supplied threshold.

    Input:
    kc:         NumPy array, symmetric. Kinship coefficient matrix.
    kc_thres:   Any positive number. Treshold for which relationships to consider.

    Returns:
    List of indexes corresponding to individuals in kc matrix.
    '''

    assert kc.shape[0] == kc.shape[1], 'Input matrix "kc" must have equal number of columns and rows.'

    # Set diagonal to zero, ignoring kinship with self.
    kc[np.diag_indices_from(kc)] = 0

    # Construct adjacency matrix, specifying which individual pairs have kinship
    # above supplied threshold.
    adj = kc > kc_thres

    # Construct graph in NetworkX.
    graph = from_numpy_matrix(adj)

    # Find approximate maximal independent set.
    mis = maximum_independent_set(graph)

    return mis

if __name__ == '__main__':
    assert len(sys.argv) > 2, 'Not enough arguments supplied. See documentation of "prune_related.py".'

    # Path to kinship CSV file.
    csv_path = sys.argv[1]

    # Threshold for high-relatedness.
    kc_thres = float(sys.argv[2])

    out_path = sys.argv[3]

    # Parse arguments "colnames" and "rownames", if provided.
    if len(sys.argv) > 4:
        colnames = sys.argv[4]

        if colnames == 'true':
            colnames == True
        elif colnames == 'false':
            colnames = False
        else:
            raise ValueError('Argument "colnames" must be either "true" or "false".')
    else:
        colnames = False

    if len(sys.argv) > 5:
        rownames = sys.argv[5]
        if rownames == 'true':
            rownames == True
        elif rownames == 'false':
            rownames = False
        else:
            raise ValueError('Argument "rownames" must be either "true" or "false".')
    else:
        rownames = False

    # Read matrix into NumPy array.
    header = 0 if colnames else None
    index_col = 0 if rownames else None
    kc = pd.read_csv(csv_path, header=header, index_col=index_col)
    kc = np.array(kc)

    # Prune related individuals.
    mis = prune_related(kc, kc_thres)

    print('After pruning, %d out of %d individuals are remaining.' %(len(mis), kc.shape[0]+1))

    # Write pruned individuals to file.
    with open(out_path, 'w') as fid:
        for ind in mis:
            fid.write(str(ind) +'\n')
