Predict biological functions of proteins from their amino-acid sequences using machine learning. Functions are defined as Gene Ontology (GO) terms, which describe:

1.Molecular Function (MF)

2.Biological Process (BP)

3.Cellular Component (CC)

The challenge is a multi-label classification problem where each protein may be associated with multiple GO terms.


The datasets is mainly in FASTA Format:
       -a simple, widely-used text-based file format for storing DNA, RNA, or protein sequences, characterized by a header line starting with a > (greater-than) symbol, followed by one or more lines of sequence data using single-letter codes (e.g., A, T, G, C for DNA; amino acid codes for proteins). It's a near-universal standard in bioinformatics due to its ease of use with text editors and scripting languages, often using extensions like .fasta, .fa, or .fna. 


GO Term Ontology File-
This file defines the Gene Ontology hierarchy:
GO terms and their relationships (parent/child structure)
-Information needed to interpret GO labels consistently
-This is a standard file format used in GO datasets.

| Column Name                | Description                                           |
| -------------------------- | ----------------------------------------------------- |
| `protein_id`               | Unique protein identifier                             |
| `sequence`                 | Amino acid sequence string                            |
| `go_term` / `GO_ID`        | Gene Ontology term label (for training)               |
| `evidence` (optional)      | How the annotation was determined (experimental etc.) |
| `probability` (submission) | Predicted likelihood of the GO term                   |



Loading GO ontology graph...
 Loaded 40122 GO terms
  - MFO terms: 10131
  - BPO terms: 25950
  - CCO terms: 4041

================================================================================
EXAMPLE 1: Get term information
================================================================================
Term: GO:0003674
Name: molecular_function
Namespace: molecular_function

================================================================================
EXAMPLE 2: Get ancestors of a term
================================================================================
Term: GO:0016791
Number of ancestors: 168
First 5 ancestors: ['GO:0042392', 'GO:0052830', 'GO:0004725', 'GO:0004438', 'GO:0004346']

================================================================================
EXAMPLE 3: Propagate terms (add all ancestors)
================================================================================
Original terms: 2
After propagation: 260
Added 258 ancestor terms
 Saved GO parser to go_parser.pkl

================================================================================
GO PARSER READY!
You can now use this parser in your modeling pipeline
================================================================================
