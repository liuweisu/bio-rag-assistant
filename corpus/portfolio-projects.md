# Portfolio projects by liuweisu

## bioseq-toolkit

A dependency-free Python package for genome assembly (de Bruijn graph, N50/NG50), transposable element discovery (LTR retrotransposons with insertion dating, TIR transposons, repeat masking, family classification), bacterial genomics (origin of replication from cumulative GC skew, ORFs), detection of TE insertions in a patient gene, and proteomics (digestion, pI, peptide mass fingerprinting). Every method is tested on simulated data with a known answer; LTR finding reaches precision 1.00 and recall 0.93 on simulated plant fragments, TIR finding is harder (precision 0.74, recall 0.61). It runs in the browser through Pyodide.

## genomics-biobank-sql

A normalised relational database for a genomics biobank and TE annotations: species, assemblies, chromosomes, genes, a TE classification tree, TE copies, individuals, phenotypes, samples, sequencing runs and genotype calls, with foreign keys, CHECK constraints, triggers, indexes and views. Twelve SQL queries use joins, CTEs, recursive CTEs and window functions. A browser SQL playground runs SQLite in WebAssembly.

## plant-cell-image-analysis

Classical image analysis: leaf segmentation with the excess green index and Otsu's threshold, disease severity from CIELAB colour with recovery of lesions on the leaf margin (severity error below 1 percentage point on light backgrounds), leaf shape traits, and nucleus counting with a distance-transform watershed (F1 0.98 versus 0.61 without the watershed on synthetic images).

## leaf-inpainting

Restoring damaged leaves in images with harmonic, biharmonic, Telea, Navier-Stokes and exemplar-based (Criminisi) inpainting, evaluated with a leaf-shape metric besides PSNR and SSIM. Exemplar inpainting restores bitten leaf margins best (shape IoU 0.89 versus 0.60 to 0.72 for diffusion methods).

## rnaseq-agent

An LLM agent that answers questions about a bulk RNA-seq dataset by calling real analysis tools (DESeq2 through pydeseq2) on a local open-weight model, with an evaluation set that includes trap questions designed to tempt the model into making things up.

## bio-rag-assistant

This assistant: retrieval-augmented question answering over bioinformatics method notes, with BM25 retrieval written from scratch, answers with citations from Claude, an offline extractive mode, a retrieval and answer evaluation set, and a FastAPI service.
