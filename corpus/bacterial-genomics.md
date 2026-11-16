# Bacterial genome analysis: origin of replication, genes and insertion sequences

## Origin of replication

Most bacteria have a circular chromosome that is replicated in both directions from a single origin (oriC) to the terminus (ter). Because of mutational bias during replication, the leading strand is enriched in G over C. GC skew, (G - C) / (G + C) in a sliding window, therefore changes sign at the origin and the terminus. The cumulative GC skew reaches its minimum near oriC and its maximum near ter (Lobry 1996). In E. coli the origin carries several DnaA boxes, binding sites of the initiator protein DnaA with the consensus TTATCCACA, so clusters of DnaA boxes near the skew minimum support the prediction.

## Gene prediction

Bacterial genomes are gene-dense: about 85 to 90% of the sequence is coding. Open reading frames are easy to find, but random sequence also contains long ORFs. Prodigal improves on simple ORF calling by learning the genome's codon usage, start codon preferences and ribosome binding site motifs. Annotation pipelines such as Bakta and PGAP then assign functions.

## Insertion sequences

Insertion sequence (IS) elements are the simplest bacterial transposable elements: short (typically 0.7 to 2.5 kb) DNA elements that encode only a transposase and are bounded by inverted repeats. IS elements can disrupt genes, activate neighbouring genes with outward-facing promoters, and mobilise antibiotic resistance genes when two copies flank them as a composite transposon. ISfinder is the reference database.
