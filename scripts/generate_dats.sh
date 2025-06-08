for i in {3..7}; do
    echo "Creating data for Symmetric group S_$i"
    echo "Read(\"gap/fca_matrix.g\");PrintDat(FCAMatrix(SymmetricGroup($i)));" | gap -q > "dat/S_n/S_$i.dat"
done;

for i in {4..7}; do
    echo "Creating data for Alternating group A_$i"
    echo "Read(\"gap/fca_matrix.g\");PrintDat(FCAMatrix(AlternatingGroup($i)));" | gap -q > "dat/A_n/A_$i.dat"
done;

for i in {1..20}; do
    echo "Creating data for Dihedral group D_$i"
    echo "Read(\"gap/fca_matrix.g\");PrintDat(FCAMatrix(DihedralGroup(2*$i)));" | gap -q > "dat/D_n/D_$i.dat"
done;

for i in {1..30}; do
    echo "Creating data for [$i]"
    echo "Read(\"gap/fca_matrix.g\");PrintDat(FCAMatrix(CyclicGroup(2^$i)));" | gap -q > "dat/[n]/[$i].dat"
done;

for i in {1..7}; do
    for j in $(seq 1 $i); do
        echo "Creating data for [$i] x [$j]"
        echo "Read(\"gap/fca_matrix.g\");PrintDat(FCAMatrix(CyclicGroup(2^$i*3^$j)));" | gap -q > "dat/[n]x[m]/[$i]x[$j].dat"
    done;
done;