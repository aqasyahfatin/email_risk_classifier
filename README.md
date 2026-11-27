# Email Risk Classifier
### WID3002 Natural Language Processing Group Assignment UM

> An end-to-end NLP threat classification pipeline and interactive Streamlit dashboard that categorizes incoming emails into 3 risk tiers—**Ham (Safe)**, **Spam (Mid Risk)**, and **Phishing (High Risk)**—using calibrated linear support vector machines and n-gram feature extraction.

---

## Executive Summary & Headline Benchmarks

Traditional binary spam filters force a rigid "Spam" vs. "Not Spam" decision, leaving non-technical users exposed to sophisticated phishing scams that masquerade as marketing promotions. This project resolves that ambiguity by delivering transparent **threat probability scores** across three distinct risk categories.

### Key Performance Results (Test Set N = 26,206)

| Model Architecture | Hyperparameters | Accuracy | Macro F1 Score | Key Security Advantage |
| :--- | :--- | :---: | :---: | :--- |
| **LinearSVC + CalibratedClassifierCV (Selected)** | **C = 0.1 (Sigmoid)** | **87.55%** | **87.66%** | **99.0% Precision on Ham** (Minimizes false positives) |
| SGD Classifier | alpha = 0.0001 | 87.45% | 87.52% | Strong linear baseline, slightly higher variance |
| LinearSVC (Uncalibrated) | C = 0.1 | 87.25% | 87.37% | Fast inference, but lacks probability calibration |
| Multinomial Naive Bayes (Baseline) | alpha = 0.01 | 85.71% | 85.71% | Weak on overlapping Spam/Phishing lexicons |

---

## Business Problem & Safety Context

Email security requires balancing **user protection** against **operational disruption**:
1. **The Cost of False Positives**: Flagging a critical business communication (Ham) as Phishing disrupts business operations. Our system prioritizes **99% Precision on Ham (Low Risk)**, ensuring only 127 legitimate emails were misclassified out of 8,561 test cases.
2. **Multi-Class Threat Scoring**: Rather than a black-box binary label, the pipeline outputs calibrated confidence percentages (e.g., *96.1% Phishing / 3.0% Spam / 0.9% Safe*), allowing security teams and end-users to make informed decisions on suspicious emails.

---

## Dataset & Leakage Controls

* **Corpus Aggregation**: Built by harmonizing **131,026 emails** across four public corpora (Enron, SpamAssassin, Kaggle Phishing, and Kaggle Spam/Ham datasets).
* **Balanced Class Distribution**:
  * 🟢 **Ham (Low Risk)**: 42,805 samples (32.7%)
  * 🟡 **Spam (Mid Risk)**: 45,390 samples (34.6%)
  * 🔴 **Phishing (High Risk)**: 42,831 samples (32.7%)
* **Strict Stratified Validation**:
  * **80/20 Train/Test Split**: 104,820 training emails vs. 26,206 holdout test emails.
  * **Zero Data Leakage**: The TfidfVectorizer was fitted **exclusively on the training split**; test text was transformed strictly using training-derived vocabulary.
* **Regex URL Normalization**: Punctuation and hidden HTML tags were stripped, but web hyperlinks were systematically normalized to a `url_link` placeholder rather than deleted. This preserved essential structural phishing signals while preventing the model from overfitting to specific domain names.

---

## Model Decisions & Iterations

