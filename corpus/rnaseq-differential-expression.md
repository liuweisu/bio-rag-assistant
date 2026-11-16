# Differential expression analysis of RNA-seq counts

## Counts and normalisation

After reads are mapped or pseudo-aligned, each gene gets a count per sample. Raw counts cannot be compared directly because libraries differ in sequencing depth and composition. DESeq2 uses median-of-ratios normalisation: for each gene the geometric mean across samples serves as a pseudo-reference, each sample's size factor is the median of its ratios to that reference over all genes.

## The model

DESeq2 models counts with a negative binomial distribution, which allows the variance to exceed the mean (overdispersion). Because most experiments have few replicates, gene-wise dispersion estimates are shrunk towards a trend fitted across all genes. A generalised linear model with the experimental design (for example ~ condition) is fitted per gene and coefficients are tested with a Wald test, or with a likelihood ratio test for more complex designs.

## Multiple testing

Testing thousands of genes produces many small p-values by chance. The Benjamini-Hochberg procedure controls the false discovery rate (FDR); DESeq2 reports these as adjusted p-values (padj). Independent filtering removes genes with very low counts, which have little power, before adjustment. Log2 fold changes of low-count genes are noisy; shrinkage estimators such as apeglm give more useful effect sizes for ranking.

## Quality control

Before testing, check library sizes, the number of detected genes and a PCA of variance-stabilised counts. A sample with very low depth or one that clusters away from its group can drive false results.
