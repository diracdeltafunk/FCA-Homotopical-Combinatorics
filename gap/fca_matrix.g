# Cast bool to int
Boole := function(b)
    if b then
        return 1;
    else
        return 0;
    fi;
end;

# Sort the rows of a binary matrix in DECREASING lex order
# Assumed m is a matrix (i.e. all rows have same length)
# Modifies m in place!
SortRows := function(m)
    local CompareRows;
    if Length(m) = 0 then
        return [];
    fi;
    CompareRows := function(r1, r2)
        local i;
        for i in [1..Length(r1)] do
            if r1[i] > r2[i] then
                return true;
            fi;
        od;
        return false;
    end;
    Sort(m, CompareRows);
end;

# Only works for abelian groups!
FCAMatrixSaturated_Abelian := function(G)
    local subgroups, nontrivial_subgroups, direct_edges, result;
    subgroups := AllSubgroups(G);
    nontrivial_subgroups := Filtered(subgroups, h -> Order(h) > 1);
    direct_edges := Concatenation(List(
        subgroups,
        h -> List(
                Filtered(subgroups, k -> IsSubgroup(k,h) and IsPrimeInt(Index(k,h))),
                x -> [h,x]
            )
    ));
    result := List(direct_edges, e -> List(nontrivial_subgroups,
        h -> Boole((not IsSubgroup(e[2],h)) or IsSubgroup(e[1],h))
    ));
    SortRows(result);
    return result;
end;

# Only works for abelian groups!
FCAMatrix_Abelian := function(G)
    local subgroups, edges, result;
    subgroups := AllSubgroups(G);
    edges := Concatenation(List(
        subgroups,
        h -> List(
                Filtered(subgroups, k -> IsSubgroup(k,h) and not h = k),
                x -> [h,x]
            )
    ));
    result := List(edges, e -> List(edges,
        f -> Boole(
                (not IsSubgroup(e[1],f[1])) or (not IsSubgroup(e[2],f[2])) or IsSubgroup(e[1],f[2])
            )
    ));
    SortRows(result);
    return result;
end;

# Produces the FCA matrix (list of lists of 0's and 1's) for a group G
# Sorted
FCAMatrix := function(G)
    local subgroups, edges, ccedges, result;
    if IsAbelian(G) then
        return FCAMatrix_Abelian(G);
    fi;
    subgroups := AllSubgroups(G);
    edges := Concatenation(List(
        subgroups,
        h -> List(
                Filtered(subgroups, k -> IsSubgroup(k,h) and not h = k),
                x -> [h,x]
            )
    ));
    ccedges := OrbitsDomain(G, edges, OnTuples);
    result := List(ccedges, es -> List(ccedges,
        fs -> Boole(
                ForAll(fs, f -> (not IsSubgroup(es[1][1],f[1])) or (not IsSubgroup(es[1][2],f[2])) or IsSubgroup(es[1][1],f[2]))
            )
    ));
    SortRows(result);
    return result;
end;

# Same as DatToFile but prints to stdout
PrintDat := function(m)
    local i,j;
    for i in [1..Length(m)] do
        for j in [1..Length(m[i])] do
            if m[i][j]=1 then
                Print(j-1);
                Print(" \c");
            fi;
        od;
        Print("\n");
    od;
end;

# Given a matrix of 0's and 1's and a filename, will put the dat in that file
DatToFile := function(m,filename)
    local ostream, i, j;
    ostream := OutputTextFile(filename, false);
    SetPrintFormattingStatus(ostream, false);
    for i in [1..Length(m)] do
        for j in [1..Length(m[i])] do
            if m[i][j]=1 then
                PrintTo(ostream, StringFormatted("{} ", j-1));
            fi;
        od;
        PrintTo(ostream, "\n");
    od;
    CloseStream(ostream);
end;