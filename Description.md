# CAFA 6 Protein Function Prediction

> **Note — read first.** This is a conceptual / design write-up of the *intended*
> end-to-end pipeline. The embedding-extraction, model-training, and prediction
> stages are **not yet implemented** in this repository, and every performance
> figure below (F1, F-max, training times, "Expected Performance" tables) is an
> **illustrative target, not a measured result**. See [README.md](README.md) for
> the actual implemented status and verified numbers.

## 🧬 Project Overview

This project implements a deep learning pipeline for predicting protein functions using the **CAFA 6 (Critical Assessment of Protein Function Annotation)** dataset. The goal is to predict Gene Ontology (GO) terms for proteins based on their amino acid sequences.

### **What is Protein Function Prediction?**

Proteins are the workhorses of biology - they perform almost every function in living organisms. Understanding what a protein does (its "function") is crucial for:
- Drug discovery and development
- Understanding diseases
- Biotechnology applications
- Evolutionary biology

However, experimentally determining protein function is expensive and time-consuming. **Machine learning can predict function from sequence**, saving years of lab work.

---

## 🎯 The Problem

### **Input:**
- **Protein sequences:** Strings of amino acids (e.g., "MKTAYIAKQRQISFVKSHFSRQLE...")
- Each protein is identified by a UniProt ID (e.g., `sp|P12345|PROT_HUMAN`)

### **Output:**
- **GO Terms:** Standardized labels describing protein function
- Each protein can have **multiple functions** (multi-label classification)
- GO terms are organized in a **hierarchy** (graph structure)

### **Three Types of Functions (Ontologies):**
1. **MFO (Molecular Function):** What the protein DOES at molecular level
   - Example: "kinase activity", "DNA binding"
   
2. **BPO (Biological Process):** What biological processes it participates in
   - Example: "cell division", "immune response"
   
3. **CCO (Cellular Component):** WHERE in the cell it's located
   - Example: "nucleus", "cell membrane"

---

## 🏗️ System Architecture

```
Raw Data (Protein Sequences)
    ↓
[1] Feature Extraction (ESM2)
    ↓
High-Dimensional Embeddings (1280 dimensions)
    ↓
[2] Label Preparation
    ↓
Binary Label Matrices (proteins × GO terms)
    ↓
[3] Neural Network Training
    ↓
Trained Models (MFO, BPO, CCO)
    ↓
[4] Prediction + Hierarchy Enforcement
    ↓
Final Submission (submission.tsv)
```

---

## 📂 Project Structure

```
CAFA-6-Project/
├── data/                              # Raw dataset files
│   ├── train_sequences.fasta          # Training protein sequences (82,404 proteins)
│   ├── testsuperset.fasta             # Test protein sequences
│   ├── train_terms.tsv                # Training labels (537K annotations)
│   ├── go-basic.obo                   # Gene Ontology structure (40K terms)
│   └── sample_submission.tsv          # Submission format example
│
├── scripts/                           # Python scripts
│   ├── data_exploration.py            # Step 1: Analyze dataset
│   ├── extract_embeddings.py          # Step 2: Generate ESM2 embeddings
│   ├── prepare_labels.py              # Step 3: Create label matrices
│   ├── train_models.py                # Step 4: Train neural networks
│   ├── make_prediction.py             # Step 5: Generate predictions
│   └── ontologyparser.py              # GO hierarchy utilities
│
├── embeddings/                        # Protein embeddings (large files)
│   ├── train_esm2_embeddings.pkl      # Training embeddings (1280-dim)
│   └── test_esm2_embeddings.pkl       # Test embeddings (1280-dim)
│
├── processed_data/                    # Preprocessed data
│   ├── train_labels_MFO.npy           # MFO labels (82404 × 500)
│   ├── train_labels_BPO.npy           # BPO labels (82404 × 800)
│   ├── train_labels_CCO.npy           # CCO labels (82404 × 400)
│   ├── train_protein_ids.pkl          # Protein ID list
│   └── selected_terms.pkl             # GO term mappings
│
├── models/                            # Trained models
│   ├── model_MFO_best.pth             # Best MFO model
│   ├── model_BPO_best.pth             # Best BPO model
│   └── model_CCO_best.pth             # Best CCO model
│
├── submissions/                       # Kaggle submissions
│   └── submission.tsv                 # Final predictions
│
├── go_parser.pkl                      # GO graph parser object
└── README.md                          # This file
```

---

## 🔬 Technical Deep Dive

### **Step 1: Data Exploration**

**What we did:**
- Loaded 82,404 training protein sequences
- Analyzed 537,027 GO term annotations
- Examined GO term distribution across ontologies
- Identified data statistics and patterns

**Key Findings:**
- Average protein length: ~400 amino acids
- MFO: 1,529 frequent GO terms
- BPO: 5,333 frequent GO terms  
- CCO: 1,011 frequent GO terms
- Highly imbalanced dataset (some terms appear 30K+ times, others <10 times)

---

### **Step 2: Feature Extraction with ESM2**

**What is ESM2?**
- **ESM2 (Evolutionary Scale Modeling 2)** is a state-of-the-art protein language model
- Developed by Facebook AI Research (Meta)
- Pre-trained on 250 million protein sequences
- Similar to BERT/GPT but for proteins instead of text

**How it works:**
1. Takes amino acid sequence as input
2. Processes it through transformer layers
3. Outputs a 1280-dimensional vector (embedding) per protein
4. This embedding captures evolutionary and structural information

**Why ESM2?**
- ✅ Captures evolutionary patterns learned from millions of proteins
- ✅ Understands amino acid context and interactions
- ✅ Transfer learning: Pre-trained knowledge helps with limited training data
- ✅ State-of-the-art performance on protein tasks

**Our Implementation:**
```python
Model: facebook/esm2_t33_650M_UR50D
- Parameters: 650 million
- Embedding dimension: 1280
- Batch processing with GPU acceleration
- Time: ~40 minutes for 82K proteins (with RTX 4050)
```

**Result:**
- Each protein → 1280 numbers capturing its biological properties
- Train: 82,404 proteins → (82404, 1280) matrix
- Test: Similar size for test proteins

---

### **Step 3: Label Preparation**

**The Challenge:**
- 26,125 unique GO terms in training data
- Can't predict all (too many, too rare)
- Need to select most important terms

**Our Approach:**

**3.1 Term Selection:**
- Selected top N most frequent terms per ontology:
  - **MFO:** 500 terms (min 30 proteins per term)
  - **BPO:** 800 terms (min 57 proteins per term)
  - **CCO:** 400 terms (min 37 proteins per term)
- Total: 1,700 GO terms to predict

**3.2 Hierarchy Propagation:**
- GO terms form a directed acyclic graph (DAG)
- If protein has term X, it must have ALL parent terms
- Example: "kinase activity" → "phosphorylation" → "catalytic activity" → "molecular function"
- We propagate labels UP the hierarchy for consistency

**3.3 Label Matrices:**
Created binary matrices:
- MFO: (82,404 proteins × 500 terms)
- BPO: (82,404 proteins × 800 terms)
- CCO: (82,404 proteins × 400 terms)
- Value = 1 if protein has that function, 0 otherwise

**Result:**
- 49,751 proteins have MFO labels (avg: 54.2 labels per protein)
- 44,382 proteins have BPO labels (avg: 6.6 labels per protein)
- 58,505 proteins have CCO labels (avg: 36.5 labels per protein)

---

### **Step 4: Neural Network Training**

**Architecture:**

We trained **3 separate neural networks** (one per ontology):

```
Input Layer (1280 neurons - ESM2 embedding)
    ↓
Hidden Layer 1 (512 neurons)
    ↓ ReLU activation
    ↓ Batch Normalization
    ↓ Dropout (30%)
    ↓
Hidden Layer 2 (256 neurons)
    ↓ ReLU activation
    ↓ Batch Normalization
    ↓ Dropout (30%)
    ↓
Output Layer (N neurons - one per GO term)
    ↓ Sigmoid activation (multi-label)
    ↓
Predictions (probability for each GO term)
```

**Training Details:**

| Parameter | Value | Why? |
|-----------|-------|------|
| Loss Function | Binary Cross-Entropy | Multi-label classification |
| Optimizer | Adam | Adaptive learning rates |
| Learning Rate | 0.001 | Standard for Adam |
| Batch Size | 32 | Fits in 6GB GPU memory |
| Epochs | 20 | Balance speed vs accuracy |
| Train/Val Split | 80/20 | Standard practice |
| Device | CUDA (RTX 4050) | GPU acceleration |

**Training Process:**
1. Load ESM2 embeddings + labels
2. Split into training (65,923) and validation (16,481) sets
3. Train for 20 epochs
4. Monitor validation F1 score
5. Save best model (highest validation F1)

**Training Time:**
- MFO model: ~30 minutes (500 output neurons)
- BPO model: ~45 minutes (800 output neurons)
- CCO model: ~25 minutes (400 output neurons)
- **Total:** ~90 minutes on RTX 4050

**Validation Performance:**
After 20 epochs, our models achieved:
- MFO: F1 ~0.40-0.50
- BPO: F1 ~0.30-0.40
- CCO: F1 ~0.45-0.55

---

### **Step 5: Prediction & Submission**

**5.1 Load Test Data:**
- Load test protein embeddings
- Load trained models (best checkpoints)

**5.2 Generate Raw Predictions:**
```python
For each test protein:
    embedding = ESM2(sequence)  # 1280 dimensions
    
    For each ontology:
        logits = neural_network(embedding)
        probabilities = sigmoid(logits)  # Convert to [0, 1]
        # Output: probability for each GO term
```

**5.3 Hierarchy Enforcement:**
Critical step! Ensures predictions follow GO graph rules.

```python
For each protein prediction:
    For each GO term with probability > 0:
        Find all ancestor terms in GO graph
        For each ancestor:
            ancestor_prob = max(ancestor_prob, child_prob)
```

**Why this matters:**
- If we predict "kinase activity" (0.8), we must also predict "catalytic activity"
- Child term probability should never exceed parent
- Enforces biological consistency

**5.4 Create Submission File:**

Format: `EntryID \t term \t confidence`

```
EntryID          term        confidence
sp|P12345|       GO:0003674  0.856234
sp|P12345|       GO:0005515  0.742891
sp|P12345|       GO:0008150  0.691345
...
```

**Filtering:**
- Only include predictions with confidence > 0.01 (1%)
- Reduces file size and improves precision
- Typical submission: 100K-500K predictions

---

## 🧮 What the Models Learned

### **The Training Process:**

1. **Input:** Protein embedding (1280 numbers representing the protein)
2. **Hidden Layers:** Learn patterns and combinations
   - Layer 1: Basic feature combinations
   - Layer 2: Complex patterns (e.g., "proteins with features A+B+C often have function X")
3. **Output:** Probability for each GO term

### **What Patterns Were Learned:**

**MFO Model (Molecular Function):**
- Learns biochemical activity patterns
- Example: "High values in dimensions 45, 123, 891 → likely a kinase"
- Captures enzyme families, binding domains, catalytic sites

**BPO Model (Biological Process):**
- Learns process participation patterns
- Example: "Certain embedding patterns → involved in cell cycle"
- Harder to learn (more abstract, context-dependent)

**CCO Model (Cellular Component):**
- Learns localization signals
- Example: "Specific amino acid patterns → membrane protein"
- Often easiest to predict (clearer sequence signals)

### **Key Insight:**
The models don't "understand" biology like humans. Instead, they learn:
- **Statistical correlations** between embedding patterns and GO terms
- **Evolutionary signals** captured by ESM2 pre-training
- **Co-occurrence patterns** (terms that appear together)

---

## 📊 Evaluation & Performance

### **How CAFA Evaluates:**

**Metric: F-max (Maximum F1 Score)**

```
For each confidence threshold (0.01 to 0.99):
    predictions = apply_threshold(probabilities, threshold)
    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)
    F1 = 2 × (precision × recall) / (precision + recall)

F-max = maximum F1 across all thresholds
```

**Why F-max?**
- Different thresholds give different precision/recall trade-offs
- F-max finds the optimal threshold automatically
- Weighted by Information Accretion (rare terms worth more)

### **Expected Performance:**

| Metric | Expected Score | Interpretation |
|--------|---------------|----------------|
| MFO F-max | 0.35 - 0.45 | Good - captures enzyme functions |
| BPO F-max | 0.25 - 0.35 | Moderate - processes are harder |
| CCO F-max | 0.40 - 0.50 | Good - localization is clearer |
| **Overall** | **0.35 - 0.45** | **Competitive baseline** ⭐ |

### **Benchmark Comparison:**

| Approach | Expected F-max | Description |
|----------|---------------|-------------|
| Random | ~0.10 | Baseline |
| BLAST (sequence similarity) | 0.25 - 0.35 | Traditional method |
| **Our Model** | **0.35 - 0.45** | **ESM2 + Neural Net** ⭐ |
| State-of-the-art | 0.55 - 0.65 | Ensemble + fine-tuning |
| Human experts | ~0.70 | Upper bound |

---

## 🚀 How to Run

### **Prerequisites:**

```bash
# Python 3.8+
pip install torch transformers biopython pandas numpy scikit-learn tqdm obonet networkx
```

### **Hardware Requirements:**
- **CPU:** Any modern CPU
- **RAM:** 16GB+ recommended
- **GPU:** 6GB+ VRAM (RTX 3060, 4050, or better) for training
- **Storage:** 20GB free space

### **Step-by-Step Execution:**

```bash
# Step 1: Explore data
python scripts/data_exploration.py

# Step 2: Extract embeddings (2-4 hours with GPU)
python scripts/extract_embeddings.py --batch_size 2

# Step 3: Prepare labels
python scripts/prepare_labels.py --features "embeddings/train_esm2_embeddings.pkl"

# Step 4: Train models (~90 minutes with RTX 4050)
python scripts/train_models.py --embeddings "embeddings/train_esm2_embeddings.pkl" --epochs 20

# Step 5: Generate predictions
python scripts/make_prediction.py --test_embeddings "embeddings/test_esm2_embeddings.pkl" --enforce_hierarchy

# Submit submissions/submission.tsv to Kaggle!
```

---

## 💡 Key Innovations

1. **Transfer Learning with ESM2**
   - Leverages pre-trained knowledge from 250M proteins
   - No need to train embeddings from scratch
   - Significantly improves performance

2. **Hierarchy Enforcement**
   - Ensures predictions follow GO graph structure
   - Biologically consistent results
   - Improves F-max score

3. **Multi-Label Neural Networks**
   - Separate models per ontology
   - Handles class imbalance with BCE loss
   - Dropout for regularization

4. **Efficient Pipeline**
   - GPU-accelerated at every step
   - Batch processing
   - Modular design for experimentation

---

## 🔮 Potential Improvements

### **Quick Wins (1-2 days):**
1. Train for more epochs (50-100)
2. Hyperparameter tuning (learning rate, dropout, architecture)
3. Ensemble multiple models
4. Optimize confidence thresholds per ontology

### **Advanced (1-2 weeks):**
5. Fine-tune ESM2 on CAFA data (end-to-end training)
6. Add graph neural network for GO hierarchy
7. Use protein-protein interaction networks
8. Multi-task learning (share layers between ontologies)
9. Data augmentation with homologous proteins
10. Attention mechanisms to focus on important sequence regions

### **Research-Level (1+ months):**
11. Pre-train custom protein language model
12. Incorporate 3D structure predictions (AlphaFold)
13. Use evolutionary conservation scores
14. Active learning to select informative training examples

---

## 📈 Results & Insights

### **What Worked Well:**
✅ ESM2 embeddings capture rich protein information  
✅ Neural networks learn complex function patterns  
✅ Hierarchy enforcement improves biological validity  
✅ GPU acceleration makes training practical  
✅ Modular pipeline allows easy experimentation  

### **Challenges Faced:**
⚠️ Class imbalance (some terms very rare)  
⚠️ Limited training epochs (could improve with more time)  
⚠️ BPO predictions harder than MFO/CCO  
⚠️ Large file sizes (embeddings ~5-10GB)  
⚠️ Test set might have novel protein families  

### **Key Learnings:**
💡 Pre-trained models are powerful for biology  
💡 Domain knowledge (GO hierarchy) helps ML  
💡 Multi-label classification needs careful handling  
💡 Validation metrics guide model improvement  
💡 Protein function prediction is an open problem  

---

## 🎓 Educational Value

This project demonstrates:

1. **Deep Learning Fundamentals:**
   - Neural network architecture design
   - Training loops and optimization
   - Evaluation metrics and validation

2. **Transfer Learning:**
   - Using pre-trained models (ESM2)
   - Feature extraction vs fine-tuning
   - Domain adaptation

3. **Bioinformatics:**
   - Protein sequence analysis
   - Gene Ontology structure
   - FASTA file formats

4. **Software Engineering:**
   - Modular code design
   - Data pipeline construction
   - GPU programming with PyTorch

5. **Machine Learning Best Practices:**
   - Train/val/test splits
   - Handling imbalanced data
   - Batch processing
   - Model checkpointing

---


---

## 📚 References

### **Key Papers:**
1. **ESM2:** Evolutionary-scale prediction of atomic-level protein structure with a language model (Lin et al., 2023)
2. **CAFA:** The CAFA challenge reports (2011-2024)
3. **GO:** The Gene Ontology resource (Ashburner et al., 2000)


