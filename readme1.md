ESM-2 (Evolutionary Scale Modeling version 2) is a large, transformer-based protein language model from Meta AI, trained on millions of protein sequences (UniRef database) to understand amino acid patterns, similar to how BERT understands language, enabling it to predict protein structure, function, mutations, and design new proteins by learning evolutionary relationships, offering various sizes (e.g., 35M, 650M parameters) for different tasks like structure prediction (ESMFold), property prediction (stability, localization), and sequence design. 


submission.tsv is a text file (tab-separated values) containing predictions your trained models made.
Think of it like:

Model = The teacher (stays on your computer)
submission.tsv = The answer sheet (what the teacher wrote down)
submission.tsv was CREATED BY using:
Test embeddings (test_esm2_embeddings.pkl) 
Trained models (model_MFO_best.pth, model_BPO_best.pth, model_CCO_best.pth)
