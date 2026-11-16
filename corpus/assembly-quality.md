# Measuring assembly quality: N50, NG50 and BUSCO

## Contiguity

N50 is the contig length L such that contigs of length L or longer contain at least half of the assembly. L50 is the number of contigs needed to reach that half. A higher N50 means a less fragmented assembly.

N50 can be inflated by removing short contigs, because it is computed relative to the assembly size. NG50 uses the expected genome size instead, so assemblies of different total size can be compared fairly. QUAST reports N50, NG50, L50, the number of contigs and, when a reference is available, misassemblies.

## Completeness

BUSCO (Benchmarking Universal Single-Copy Orthologs) searches an assembly for genes that are expected to be present in a single copy in nearly all species of a lineage, for example embryophyta for land plants. It reports the percentage of these genes found complete and single-copy, complete and duplicated, fragmented, and missing. A high duplicated fraction can indicate that both haplotypes of a heterozygous region were kept, or a recent whole-genome duplication.

## Correctness

Contiguity and completeness do not prove that an assembly is correct. Read mapping back to the assembly, k-mer based tools such as Merqury (which compares assembly k-mers with read k-mers to estimate base accuracy as a QV score), and Hi-C contact maps are used to find errors and misjoins.
