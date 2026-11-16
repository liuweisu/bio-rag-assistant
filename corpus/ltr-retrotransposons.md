# LTR retrotransposons

LTR retrotransposons are Class I transposable elements that copy themselves through an RNA intermediate. They make up most of many large plant genomes; in maize they account for roughly three quarters of the genome.

## Structure

A complete element is a few kb to over 20 kb long. Both ends carry a long terminal repeat (LTR), typically a few hundred bases to a few kb. The LTRs usually begin with TG and end with CA. Between them lies the internal region with a primer binding site, a polypurine tract and the genes for GAG and POL (protease, integrase, reverse transcriptase, RNase H). On insertion the element duplicates a short stretch of the target DNA, usually 5 bp, so the element is flanked by a target site duplication (TSD).

## Superfamilies

Copia (Ty1) and Gypsy (Ty3) are the two main superfamilies in plants. They differ in the order of the POL domains: in Copia the integrase comes before reverse transcriptase, in Gypsy it comes after RNase H.

## Insertion age

At the moment of insertion the two LTRs are identical, because both are copied from the same template. Afterwards they accumulate mutations independently. The insertion time T can therefore be estimated as T = K / (2r), where K is the divergence between the two LTRs (corrected for multiple substitutions, for example with the Kimura two-parameter model) and r the substitution rate per site per year. A rate of 1.3 x 10^-8 substitutions per site per year, estimated in rice by Ma and Bennetzen (2004), is widely used for grasses.

## Finding them

Structure-based tools such as LTRharvest and LTR_FINDER search for pairs of long direct repeats at a suitable distance with TG...CA ends and a TSD. LTR_retriever filters their candidates to remove false positives. Solo LTRs, formed by recombination between the two LTRs of one element, are a single LTR flanked by a TSD.
