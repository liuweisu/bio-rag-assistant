# Bottom-up proteomics and protein identification

## Digestion

In bottom-up (shotgun) proteomics, proteins are digested into peptides before mass spectrometry. Trypsin is the standard enzyme: it cleaves C-terminal to lysine (K) and arginine (R), but not when the next residue is proline (P). Search engines allow a small number of missed cleavages. Cysteines are usually reduced and alkylated with iodoacetamide, which adds a fixed carbamidomethyl modification of 57.021 Da.

## Peptide mass fingerprinting

In peptide mass fingerprinting (PMF) the masses of the intact peptides of one purified protein, typically measured by MALDI-TOF as singly protonated ions [M+H]+, are compared with an in silico digest of every protein in a database. The protein whose theoretical peptides explain the most observed peaks within the mass tolerance (often 10 to 50 ppm) is reported. Scores such as MOWSE correct for large proteins having more peptides that can match by chance. PMF works for single proteins, not for complex mixtures.

## Tandem mass spectrometry

For complex samples, LC-MS/MS fragments each peptide and the fragment spectrum is matched to theoretical spectra (Mascot, MaxQuant/Andromeda, MSFragger). The false discovery rate of peptide-spectrum matches is estimated with the target-decoy approach: the search is repeated against reversed or shuffled protein sequences, and the number of decoy hits above a score threshold estimates the number of false target hits.

## Useful protein properties

Monoisotopic masses use the most abundant isotope of each element and are used for accurate peptide masses; average masses are used for intact proteins. The isoelectric point is the pH at which the net charge is zero. The GRAVY score, the mean Kyte-Doolittle hydropathy, is positive for hydrophobic proteins such as many membrane proteins.
