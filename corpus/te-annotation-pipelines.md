# Annotating transposable elements in a genome

## Classification

Wicker et al. (2007) proposed the hierarchical classification used by most plant genome projects: class (I retrotransposons, II DNA transposons), order (for example LTR, LINE, SINE, TIR, Helitron), superfamily (Copia, Gypsy, hAT, ...) and family. Two elements belong to the same family under the 80-80-80 rule: at least 80% sequence identity over at least 80% of their length, in segments of at least 80 bp.

## Homology-based annotation

RepeatMasker finds copies of known elements by aligning a library of consensus sequences to the genome. Libraries come from Dfam (open, profile HMMs and consensus sequences) or Repbase. For a newly sequenced species, a species-specific library is built first, for example with RepeatModeler2, which combines de novo repeat finding with structural LTR detection.

## Pipelines

EDTA (Extensive de-novo TE Annotator) combines structure-based finders (LTRharvest, LTR_FINDER and LTR_retriever for LTR elements, TIR-Learner for TIR elements, HelitronScanner for Helitrons) with filtering steps that remove false positives and nested elements, then builds a non-redundant library and annotates the whole genome with RepeatMasker. EarlGrey automates a similar process built around RepeatModeler2 and adds consensus extension and defragmentation of fragmented annotations.

## Practical points

Annotations differ strongly between tools, so benchmark against a curated library if one exists. Report TE content per order and superfamily and check that coding genes are not masked as repeats. Soft-masking (lowercase repeats) is the usual input for gene prediction.
