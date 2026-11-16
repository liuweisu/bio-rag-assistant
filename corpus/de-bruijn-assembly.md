# Genome assembly with de Bruijn graphs

Short-read assemblers such as Velvet, SPAdes and MEGAHIT build a de Bruijn graph instead of comparing every read with every other read.

## How the graph is built

Every read is cut into overlapping substrings of length k (k-mers). Each k-mer becomes an edge between two nodes: its first k-1 bases and its last k-1 bases. Reads from both strands are used, so every k-mer is also added as its reverse complement. A path through the graph that uses each edge once spells out a genome sequence.

## Sequencing errors and the k-mer spectrum

A single sequencing error creates up to k wrong k-mers, and these are usually seen only once or twice. Plotting how many distinct k-mers occur at each multiplicity (the k-mer spectrum) shows a peak of error k-mers at multiplicity 1 to 2 and a second peak of genomic k-mers near the k-mer coverage. Assemblers discard k-mers below the valley between the two peaks. The same spectrum is used by tools like GenomeScope to estimate genome size and heterozygosity.

## Contigs from unitigs

After error removal, maximal non-branching paths (unitigs) are reported as contigs. Branches appear where the genome has repeats longer than k, at heterozygous sites and at remaining errors. A circular chromosome or plasmid without such branches appears as a cycle in the graph.

## Choosing k

A small k tolerates more errors and low coverage but makes more repeats longer than k, so the graph becomes tangled. A large k resolves more repeats but needs more reads that contain an error-free k-mer at every position. SPAdes avoids choosing by combining graphs built with several values of k. Long reads (PacBio HiFi, Oxford Nanopore) span most repeats and are assembled with overlap-based or string-graph assemblers such as hifiasm and Flye.
