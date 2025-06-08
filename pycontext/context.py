import numpy as np
import scipy.optimize as opt
from sys import stdin


# A class called FormalContext which contains a single numpy matrix of 0s and 1s
class FormalContext:
    """A class representing a formal context with a binary matrix of 0s and 1s."""

    def __init__(self, matrix=None):
        """Initialize the formal context with a binary matrix.

        Args:
            matrix: A numpy array of 0s and 1s, or None to create empty context
        """
        if matrix is not None:
            self.matrix = np.array(matrix, dtype=int)
        else:
            self.matrix = np.array([[]], dtype=int)

    def __str__(self):
        """String representation of the formal context."""
        return f"FormalContext of size {self.matrix.shape}\n{self.matrix}"

    def __repr__(self):
        """Developer representation of the formal context."""
        return f"FormalContext(matrix={self.matrix.tolist()})"

    def tikz(self, inverted=False, PIXEL_SIZE=0.1):
        """Generate a TikZ representation of the formal context.

        If inverted is False, 0s are represented as black squares and 1s as white squares.
        If inverted is True, 0s are represented as white squares and 1s as black squares.
        """
        tikz_str = "\\begin{tikzpicture}\n"
        for i in range(self.matrix.shape[0]):
            for j in range(self.matrix.shape[1]):
                color = "white" if (self.matrix[i, j] == 1) != inverted else "black"
                tikz_str += f"\\fill[{color}] ({round(j * PIXEL_SIZE,2)}, {round(-i * PIXEL_SIZE,2)}) rectangle ++({round(PIXEL_SIZE,2)}, {round(PIXEL_SIZE,2)});\n"
        tikz_str += "\\end{tikzpicture}"
        return tikz_str

    def dat_str(self):
        """Generate a string .dat representation of the formal context."""
        dat_str = ""
        for i in range(self.matrix.shape[0]):
            row = [str(j) for j in np.where(self.matrix[i] == 1)[0]]
            dat_str += " ".join(row) + "\n"
        return dat_str.strip()

    def dat_list(self):
        """Generate a list of lists .dat representation of the formal context."""
        dat_list = []
        for i in range(self.matrix.shape[0]):
            row = [int(j) for j in np.where(self.matrix[i] == 1)[0]]
            dat_list.append(row)
        return dat_list

    def matrix_list(self):
        """Return the matrix as a list of lists."""
        return self.matrix.tolist()

    def num_ones(self):
        """Return the number of 1's in the matrix."""
        return np.sum(self.matrix)

    def num_rows(self):
        """Return the number of rows in the context matrix."""
        return self.matrix.shape[0]

    def num_cols(self):
        """Return the number of columns in the context matrix."""
        return self.matrix.shape[1]

    def density(self):
        """Return the density of the context, defined as the number of 1's divided by the total number of entries."""
        total_entries = self.matrix.size
        if total_entries == 0:
            raise ValueError("The context is empty, density undefined.")
        return self.num_ones() / total_entries

    def complexity(self):
        """Calculate the complexity of a formal context.

        This uses an integer linear programming approach, where we equivalently search for a max
        induced matching in the bipartite graph represented by the inverted context matrix.

        Returns:
            The complexity.
        """
        inverted_context_matrix = (
            np.ones_like(self.matrix) - self.matrix
        )  # Invert the matrix to count 1's as 0's and vice versa
        num_rows = inverted_context_matrix.shape[0]
        num_cols = inverted_context_matrix.shape[1]
        N = max(num_rows, num_cols)
        # Variables
        # x_1, ..., x_n, one for each row of matrix
        # y_1, ..., y_k, one for each column of matrix
        A = np.zeros((2 * (num_rows + num_cols), num_rows + num_cols))
        # The first num_rows rows of A have the following form:
        # e_i CONCAT -row_i
        # where e_i is the i-th unit vector (row vector)
        # and row_i is the i-th row of `matrix`
        for i in range(num_rows):
            A[i, i] = 1
            A[i, num_rows : num_rows + num_cols] = -inverted_context_matrix[i, :]
        # The next num_cols rows of A have the following form:
        # -col_j CONCAT e_j
        for j in range(num_cols):
            A[num_rows + j, num_rows + j] = 1
            A[num_rows + j, :num_rows] = -inverted_context_matrix[:, j]
        # The next num_rows rows of A have the following form:
        # (N-1) * e_i CONCAT row_i
        for i in range(num_rows):
            A[num_rows + num_cols + i, i] = N - 1
            A[num_rows + num_cols + i, num_rows : num_rows + num_cols] = (
                inverted_context_matrix[i, :]
            )
        # The next num_cols rows of A have the following form:
        # col_j CONCAT (N-1) * e_j
        for j in range(num_cols):
            A[num_rows + num_cols + num_rows + j, num_rows + j] = N - 1
            A[num_rows + num_cols + num_rows + j, :num_rows] = inverted_context_matrix[
                :, j
            ]
        # Bounds
        b_u = np.zeros(2 * (num_rows + num_cols))
        for j in range(num_rows + num_cols):
            b_u[num_rows + num_cols + j] = N
        # Constants
        c = np.zeros(num_rows + num_cols)
        for i in range(num_rows):
            c[i] = -1
        integrality = np.ones_like(c)
        bounds = opt.Bounds(np.zeros_like(c), np.ones_like(c))
        constraints = opt.LinearConstraint(A, -np.inf, b_u)
        res = opt.milp(
            c=c, constraints=constraints, integrality=integrality, bounds=bounds
        )
        return -round(res.fun)


def from_dat_list(dat):
    """Create a FormalContext instance from a list of lists representing a .dat file.

    Args:
        dat: A list of lists of ints.

    Returns:
        FormalContext
    """

    if not dat:
        return FormalContext()

    max_attr = max(max(row) if row else 0 for row in dat)

    result = np.zeros((len(dat), max_attr + 1), dtype=int)

    for i in range(len(dat)):
        for k in dat[i]:
            result[i, k] = 1

    return FormalContext(result)


def from_dat_stdin():
    """Create a FormalContext instance from stdin input, in .dat form.

    Reads lines from stdin where each line contains space-separated integers
    representing attribute indices. Creates a binary matrix where entry (i,j)
    is 1 if attribute j is present in object i.

    Returns:
        FormalContext
    """

    dat = []

    # Loop over lines in stdin until EOF
    for line in stdin:
        nums = line.split()
        dat.append([int(x) for x in nums])

    return from_dat_list(dat)


def from_dat_file(file):
    """Create a FormalContext instance from a file containing .dat format.

    Args:
        file: A file object to read from, where each line contains space-separated integers. *NOT A FILENAME!*

    Returns:
        FormalContext
    """
    dat = []

    # Loop over lines in the file
    for line in file:
        nums = line.split()
        dat.append([int(x) for x in nums])

    return from_dat_list(dat)


# Not needed -- .cxt files are not used in this project.
# def from_cxt_stdin():
#     """Create a FormalContext instance from stdin input, in .cxt form.

#     Returns:
#         FormalContext
#     """
#     # Skip 'B' and blank line
#     stdin.readline()
#     stdin.readline()
#     # Read the first two lines to get m and n
#     m = int(stdin.readline().strip())
#     n = int(stdin.readline().strip())

#     # Skip the next n+m+1 lines
#     for _ in range(n + m + 1):
#         stdin.readline()

#     # Read the matrix
#     matrix = []
#     for _ in range(m):
#         line = stdin.readline().strip()
#         row = [1 if char == 'X' else 0 for char in line]
#         matrix.append(row)

#     return FormalContext(matrix)
