#!/usr/bin/env python
'''
This tool uses a heuristic to remove highly related individuals, based on a supplied kinship matrix and
a threshold. The output of the pruning procedure is then a list of individuals to keep.

The networkx (v2.1 or newer) Python library must be installed in the environment.

* Find relationships where kinship is above threshold
* Construct a graph, where two individuals are connected if they are highly related
* Find a maximal independent set

A maximal independent set is 

Usage:
    python prune_related.py [kinship matrix] [threshold] [output file] [include]

Input:
    Kinship matrix:     Path to CSV file with kinship coefficients between individuals. The CSV must be comma
                        separated and have no column or row names.
    Threshold:          Pairs of individuals with kinship above this will be considered highly related.
    Output file:        Output will be written to a file with this path.
    Include:            (Optional) Indexes of individuals to attempt to include in minimal set.

Example:
    python prune_related.py kinship_matrix.csv 0.0625 pruned_individuals.txt
    python prune_related.py kinship_matrix.csv 0.0625 pruned_individuals.txt important_probands.txt

Output:
    The indexes of individuals remaining after pruning are written to the specified output file.
'''

from networkx import from_numpy_matrix, maximal_independent_set
#from networkx.algorithms.approximation.independent_set import maximum_independent_set
import numpy as np
import sys

def read_matrix_from_csv(csv_path):
    '''
    Read CSV into memory and convert to NumPy array.

    Input:
    csv_path:       String, path to CSV file.

    Returns:
    Numpy array.
    '''

    kc = []
    with open(csv_path) as fid:
        for i, line in enumerate(fid):
            # Remove newline ("\n") and split by comma(",") to return a list.
              row = line[:-1].split(',')
              # Convert elements from strings to floats.
              # Also strip any whitespace before converting to float.
              row = [float(x.strip()) for x in row]
              kc.append(row)

    kc = np.array(kc)

    return kc

def prune_related(kc, kc_thres, include=None):
    '''
    Find the minimal set of individuals to keep by removing relationships based on
    supplied threshold.

    Input:
    kc:         NumPy array, symmetric. Kinship coefficient matrix.
    kc_thres:   Any positive number. Treshold for which relationships to consider.

    Returns:
    Tuple of two lists of integers, both corresponding to indexes in kc. First list is individuals
    to keep. Second list is a pruned version of the `include` list.
    '''

    assert kc.shape[0] == kc.shape[1], 'Input matrix "kc" must have equal number of columns and rows.'

    # Set diagonal to zero, ignoring kinship with self.
    kc[np.diag_indices_from(kc)] = 0

    # Construct adjacency matrix, specifying which individual pairs have kinship
    # above supplied threshold.
    adj = kc > kc_thres

    # First prune the "include" list.
    if include is not None:
        # Construct graph in NetworkX.
        graph_include = from_numpy_matrix(adj[include,:][:,include])

        # Find approximate maximal independent set.
        mis_include_idx = maximal_independent_set(graph_include)
        mis_include = [include[idx] for idx in mis_include_idx]
    else:
        mis_include = None

    # Construct graph in NetworkX.
    graph = from_numpy_matrix(adj)

    # Find approximate maximal independent set.
    mis = maximal_independent_set(graph, nodes=mis_include)

    return (mis, mis_include)

if __name__ == '__main__':
    assert len(sys.argv) > 2, 'Not enough arguments supplied. See documentation of "prune_related.py".'

    # Path to kinship CSV file.
    csv_path = sys.argv[1]

    # Threshold for high-relatedness.
    kc_thres = float(sys.argv[2])

    out_path = sys.argv[3]

    # Process the "include" list.
    if len(sys.argv) > 4:
        include_file = sys.argv[4]
        with open(include_file) as fid:
            include = fid.read()

        # If the file ends with a newline, remove it.
        if include[-1] == '\n':
            include = include[:-1]

        # Get the include elements into a list.
        include = include.split('\n')
        include = [int(x) for x in include]
    else:
        include = None

    # Read matrix into NumPy array.
    kc = read_matrix_from_csv(csv_path)

    # Prune related individuals.
    mis, mis_include = prune_related(kc, kc_thres, include)

    print('After pruning, %d out of %d individuals are remaining.' %(len(mis), kc.shape[0]+1))
    if include is not None:
        print('In the include list, %d out of %d individuals were removed.' %(len(include) - len(mis_include), len(include)))

    # Write pruned individuals to file.
    with open(out_path, 'w') as fid:
        for ind in mis:
            fid.write(str(ind) +'\n')
