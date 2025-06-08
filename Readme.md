# FCA Tools for Homotopical Cominatorics

This repository contains code to accompany the paper [Formal Concept Analysis and Homotopical Combinatorics] by Scott Balchin and Ben Spitz.

**Contents**

* [Demos](#demos)
* [Subdirectory Info](#subdirectory-info)
  * [pycontext](#pycontext)
  * [pcbo](#pcbo)
  * [dat](#dat)
  * [gap](#gap)
  * [mathematica](#mathematica)

## Demos

> [!NOTE]
> Each demonstration is performed in a macOS or Linux terminal, starting in the root directory of this repository.

### Demonstration 1

**Requirements:** A working GAP4 installation, the `pcbo` binary.

**Goal:** Count the number of $S_5$-transfer systems.

#### Beginner Version

We must first produce the `.dat` file representing the reduced formal context of the lattice $\mathsf{Tr}(\mathsf{Sub}(S_5))$.

To do this, we must run the gap command `PrintDat(FCAMatrix(SymmetricGroup(5)));`, which uses the functions `PrintDat` and `FCAMatrix` defined in the file `gap/fca_matrix.g`. So, we make a file called `generate_S5_dat.g` with the following contents:

```GAP
Read("gap/fca_matrix.g");
PrintDat(FCAMatrix(SymmetricGroup(5)));
```

Now we run this GAP script to produce our desired `.dat` file:

```console
FCA-Homotopical-Combinatorics$ gap -q generate_S5_dat.g > S5.dat
```

Next, we can give this `.dat` file to PCbO to count the number of transfer systems.

```console
FCA-Homotopical-Combinatorics$ pcbo/pcbo S5.dat
WARNING: Too many attributes and/or objects! Integer overflow may occur; program result is not guaranteed correct.
183598202
```

> [!NOTE]
> The warning here indicates that PCbO cannot prove ahead of time that there are not more concepts than the maximum value of a C `unsigned long long`. This isn't really anything to worry about -- an integer overflow can only occur if you manage to count past $2^{64}$. At time of writing, pcbo can generate (on the order of) 1 million concepts per second on a laptop, so unless this command takes a few thousand years to run, you're fine.

The answer is $183598202$, success! This worked, but has a few annoying features:

1. It takes quite a while for PCbO to produce the number 183598202 -- probably a few minutes if you're using a laptop.
2. We are left with a small mess of auxilliary files: `generate_S5_dat.g` and `S5.dat`.

The advanced version of this demonstration addresses these issues.

#### Advanced Version

```console
FCA-Homotopical-Combinatorics$ echo 'Read("gap/fca_matrix.g");PrintDat(FCAMatrix(SymmetricGroup(5)));' | gap -q | pcbo/pcbo -P8 2> /dev/null
183598202
```

Notes:

* The `-P8` flag tells PCbO to use 8 threads; this number should be adjusted based on how many CPU cores you have.
* `2> /dev/null` supresses warnings.
* A `.dat` file for $S_5$ is actually included with this repository, in [dat/S_n/S_5.dat](dat/S_n/S_5.dat). So you could just use `pcbo/pcbo -P8 dat/S_n/S_5.dat 2> /dev/null`.

### Demonstration 2

**Requirements:** A working python3 installation.

**Goal:** Compute the densities and complexities of $\mathsf{Tr}(D_{k})$ for $k = 1, \dots, 10$.

In this example, we'll use the `.dat` files included in this repository. We can then analyse these with the provided python code. We make a file called `script.py` with the contents

```python
from pycontext.context import *

print("n   Density   Complexity")
for i in range(1,11):
  with open(f"dat/D_n/D_{i}.dat", 'r') as file:
    cxt = from_dat_file(file)
    print(f"{i:2d}  {cxt.density():5f}  {cxt.complexity():3d}")
```

Then we can run the script with

```console
FCA-Homotopical-Combinatorics$ python3 script.py
n   Density   Complexity
 1  0.000000    1
 2  0.535714    3
 3  0.433333    2
 4  0.687135    6
 5  0.433333    2
 6  0.739316   10
 7  0.433333    2
 8  0.752101    8
 9  0.602564    4
10  0.739316   10
```

## Subdirectory Info

### pycontext

Python code for processing and manipulating formal contexts. This is provided as a single module [context.py](pycontext/context.py), which you can simply import.

**Dependencies** python >= 3.8, numpy (probably any version is fine?), scipy >= 1.9.0

[context.py](pycontext/context.py) defines a class `FormalContext` which encodes a context matrix. Also provided are some functions which allow you to create instances of `FormalContext`.

#### Ways to create a `FormalContext`

1. The constructor `FormalContext()`, which produces an empty context. Example:

    ```python
    from pycontext.context import *

    cxt = FormalContext()

    print(cxt.matrix_list()) # [[]]
    ```

2. The constructor `FormalContext(l)`, where `l` is a matrix of 0's and 1's (either a list of lists or a numpy array). Example:

    ```python
    from pycontext.context import *

    cxt = FormalContext([[0,1,1],[1,0,1]])

    print(cxt.matrix_list()) # [[0,1,1],[1,0,1]]
    ```

3. The function `from_dat_list(dat)`, where `dat` is a list of lists of non-negative integers (representing a `.dat` file). Example:

    ```python
    from pycontext.context import *

    dat = [[0,1],[0,2]]

    cxt = from_dat_list(dat)

    print(cxt.matrix_list()) # [[1, 1, 0], [1, 0, 1]]
    ```

4. The function `from_dat_file(file)`, where `file` is a `.dat` file (NOT a filename!). Example:

    ```python
    from pycontext.context import *

    with open("dat/S_n/S_3.dat") as file:
      cxt = from_dat_file(file)
      print(cxt.matrix_list()) # [[0, 1, 1, 1, 1], [1, 1, 0, 1, 1], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1], [0, 0, 1, 1, 0]]
    ```

5. The function `from_dat_stdin()`, which reads a `.dat` file from `stdin`. Example:

    ```console
    FCA-Homotopical-Combinatorics$ cat "dat/S_n/S_3.dat" | python3 -c "from pycontext.context import *; print(from_dat_stdin().matrix_list())"
    [[0, 1, 1, 1, 1], [1, 1, 0, 1, 1], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1], [0, 0, 1, 1, 0]]
    ```

#### `FormalContext` Member Functions

* `tikz(inverted=False, PIXEL_SIZE=0.1)`. Returns the source code (as a string) for a tikzpicture representing the formal context. Example:

    ```console
    FCA-Homotopical-Combinatorics$ cat "dat/[n]/[2].dat" | python3 -c "from pycontext.context import *; print(from_dat_stdin().tikz())"
    \begin{tikzpicture}
    \fill[black] (0.0, 0.0) rectangle ++(0.1, 0.1);
    \fill[white] (0.1, 0.0) rectangle ++(0.1, 0.1);
    \fill[white] (0.2, 0.0) rectangle ++(0.1, 0.1);
    \fill[black] (0.0, -0.1) rectangle ++(0.1, 0.1);
    \fill[black] (0.1, -0.1) rectangle ++(0.1, 0.1);
    \fill[white] (0.2, -0.1) rectangle ++(0.1, 0.1);
    \fill[white] (0.0, -0.2) rectangle ++(0.1, 0.1);
    \fill[black] (0.1, -0.2) rectangle ++(0.1, 0.1);
    \fill[black] (0.2, -0.2) rectangle ++(0.1, 0.1);
    \end{tikzpicture}
    ```

    By default, 0's become black pixels and 1's become white pixels. You can invert the colors by setting `inverted=True`, and you can change the size of the pixels by setting `PIXEL_SIZE`.

    > [!WARNING]
    > For large matrices, compiling one of these tikz pictures can easily blow through all of your LaTeX compiler's memory. Tikz is not the right software to use if you want to draw a large image pixel-by-pixel! See the [mathematica](#mathematica) section below for a better way to produce these images.

* `dat_str()`. Returns a string representing the context in `.dat` format. Example:

    ```console
    FCA-Homotopical-Combinatorics$ python3 -c "from pycontext.context import *; print(FormalContext([[1,0,1],[0,1,1]]).dat_str())"
    0 2
    1 2
    ```

* `dat_list()`. Returns a list of lists of non-negative integers representing the context in `.dat` format. Example:

    ```console
    FCA-Homotopical-Combinatorics$ python3 -c "from pycontext.context import *; print(FormalContext([[1,0,1],[0,1,1]]).dat_list())"
    [[0, 2], [1, 2]]
    ```

* `matrix_list()`. Returns the matrix of 0's and 1's as a list of lists. Usage demonstrated in [Ways to Create a `FormalContext`](#ways-to-create-a-formalcontext) above.

* `num_ones()`. Returns the number of 1's in the matrix.

* `num_rows()`. Returns the number of rows in the matrix.

* `num_cols()`. Returns the number of columns in the matrix.

* `density()`. Returns the density of the matrix, i.e. the proportion of entries which are 1's. See [Demonstration 2](#demonstration-2) for an example.

* `complexity()`. Returns the complexity of the context, i.e. the dimension of the largest subcontext which is a contranomial scale. See [Demonstration 2](#demonstration-2) for an example.

    > [!WARNING]
    > Computing the complexity of a context is a #P-hard problem. You should expect this to take ~exponential time in the size of the matrix.

### pcbo

A modified version of PCbO for enumerating formal concepts.

#### Building PCbO

To build, simply run `make` in the pcbo directory. This should produce an executable called `pcbo`.

#### Usage

Full usage instructions are available in [PCbO's readme](pcbo/README.txt). The key points are:

* PCbO will read a `.dat` file from stdin, or you can provide a path to an input file as a command-line argument.
* The flag `-Pn` tells PCbO to use `n` threads. You should probably set `n` to be the number of cores in your CPU. This flag must come *before* the input file (if given).

See [Demonstration 1](#demonstration-1) for an example.

### dat

A collection of `.dat` files representing various lattices of transfer systems. These include:

* [[n]](dat/[n]/): Cyclic $p$-groups. For example, `[4].dat` corresponds to a cyclic group of order $p^4$ where $p$ is a prime.
* [[n]x[m]](dat/[n]x[m]/): Cyclic groups with two prime factors. For example, `[3]x[2].dat` corresponds to a cyclic group of order $p_1^3 p_2^2$ where $p_1, p_2$ are distinct primes.
* [D_n](dat/D_n/): Dihedral groups. For example, `D_4.dat` corresponds to the dihedral group of order $8$.
* [A_n](dat/A_n/): Alternating groups. For example, `A_4.dat` corresponds to the alternating group of order $12$.
* [S_n](dat/S_n/): Symmetric groups. For example, `S_4.dat` corresponds to the symmetric group of order $24$.

### gap

GAP code to generate `.dat` files.

**Dependencies** GAP4

The file `fca_matrix.g` contains two important function definitions:

1. `FCAMatrix(G)`. Given a finite group `G`, produces a matrix of 0's and 1's (the reduced context of $\mathsf{Tr}(\mathsf{Sub}(G))$), with the rows sorted in descending lexicographic order.
2. `PrintDat(m)`. Given a matrix of 0's and 1's, prints a `.dat` representation of the matrix to stdout.

See [Demonstration 1](#demonstration-1) for an example.

### mathematica

Mathematica notebooks and WolframScript code for various combinatorial computations.

**Dependencies** Mathematica

#### DensityCyclic.nb

Contains code to compute the density of $\mathsf{Tr}([n_1] \times [n_k])$.

#### matrix_to_img.wls

A WolframScript script which takes a matrix of 0's and 1's (in Mathematica format) from stdin and a filepath (as a command line argument), and produces an image of the matrix at that path. Example usage:

```console
FCA-Homotopical-Combinatorics$ cat "dat/D_n/D_10.dat" | python3 -c "from pycontext.context import *;print(from_dat_stdin().matrix_list())" | sed -e 's/\[/{/g' -e 's/\]/}/g' | wolframscript -f mathematica/matrix_to_img.wls "D_10.pdf"
```
