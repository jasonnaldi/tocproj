#!/usr/bin/python3

import sys
import subprocess


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: specify the file name + something to produce image')
        sys.exit()

    # Read input file
    f = open(sys.argv[1])
    lines = f.readlines()
    f.close()

    header = lines[0].split()
    k = int(header[0]) # Size of clique
    n = int(header[1]) # Number of nodes in graph

    adjMatrix = [[False for x in range(n)] for y in range(n)]

    for i in range(1, len(lines)):
        split = lines[i].split()
        node1 = int(split[0])
        node2 = int(split[1])
        adjMatrix[node1][node2] = True
        adjMatrix[node2][node1] = True

    # Apply reduction
    variables = []
    clauses = []

    # We create clauses for each of the nodes that can belong to k (that is, k nodes)
    for i in range(1, k + 1):
        clause = ""

        for v in range(0, n):
            variables.append([i, v])
            clause += ("" if v == 0 else " ") + str(len(variables)) # Condition: each vertex in clique is unique

        clause += " 0"
        clauses.append(clause)

    for v1 in range(0, len(variables)):
        i = variables[v1][0]
        v = variables[v1][1]

        for v2 in range(0, len(variables)):
            if v1 == v2:
                continue

            j = variables[v2][0]
            w = variables[v2][1]

            clause = "-" + str(v1 + 1) + " -" + str(v2 + 1) + " 0"

            # Condition: if two nodes are not connected by an edge, they cannot be in the clique
            if not adjMatrix[v][w] and v != w:
                if clause not in clauses:
                    clauses.append(clause)

            # Condition: each vertex in the clique is unique
            if (v == w and i != j) or (v != w and i == j):
                if clause not in clauses:
                    clauses.append(clause)

    # Prepare dimacs output to be fed to minisat
    output = "p cnf " + str(len(variables)) + " " + str(len(clauses))

    for clause in clauses:
        output += "\n" + clause

    # Python and minisat junk to get right output (SAT/UNSAT + assignments when appropriate)
    tempfile = 'temp.temp'

    f = open(tempfile, "w")
    f.write(output)
    f.close()

    cmd = 'CMD="./minisat ' + tempfile + ' >(cat) > /dev/null"; /bin/bash -c "$CMD"'
    lines = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode().split()
    issat = lines[0] == "SAT"

    if len(sys.argv) <= 2 and not issat:
        print("UNSAT")
    else:
    # Output data as graphviz graph
        gviz = "graph {\n"
        thenodes = []

        if issat:
            # If SAT (k-clique exists), draw clique
            clique = []

            for i in range(1, len(lines)):
                if (int(lines[i]) > 0):
                    clique.append(i % k)

            for i in range(0, len(clique)):
                for j in range(i + 1, len(clique)):
                    if adjMatrix[i][j]:
                        if i not in thenodes:
                            thenodes.append(i)
                        if j not in thenodes:
                            thenodes.append(j)

                        if len(sys.argv) > 2:
                            gviz += "  " + str(i) + " -- " + str(j) + "[color=red, penwidth=3.0];\n"
                            adjMatrix[i][j] = False # Do this so in printing we don't need to check again whether edge is in clique

        for i in range(0, n):
            for j in range(i, n):
                if adjMatrix[i][j]:
                    gviz += "  " + str(i) + " -- " + str(j) + ";\n";

        gviz += "}\n"

        for i in range(0, len(thenodes)):
            print(thenodes[i])

        # More junk to get the output graph as an image whose name is the input file name with ".png" extension
        cmd = 'dot -Tpng -o ./public/img/graph.png 2> /dev/null'
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        pipe.communicate(input=str.encode(gviz))

    subprocess.Popen('rm ' + tempfile, shell=True)
