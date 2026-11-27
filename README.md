# Enterprise Email Risk Assessment & Intelligence System

> An end-to-end NLP threat classification pipeline and interactive Streamlit application that categorizes incoming emails into 3 risk tiers—**Ham (Safe)**, **Spam (Mid Risk)**, and **Phishing (High Risk)**—using calibrated Linear SVM and n-gram feature extraction.

---

## 🚀 Key Results & Performance Summary

| Model Architecture | Hyperparameters | Accuracy | Macro F1 | Security & Business Impact |
| :--- | :--- | :---: | :---: | :--- |
| **Calibrated LinearSVC (Selected)** | **C = 0.1 (Sigmoid)** | **87.55%** | **87.66%** | **99.0% Precision on Ham** (Prevents false positive operational disruption) |
| SGD Classifier | alpha = 0.0001 | 87.45% | 87.52% | Strong linear baseline, slightly higher variance |
| LinearSVC (Uncalibrated) | C = 0.1 | 87.25% | 87.37% | Fast inference, but lacks probability calibration |
| Multinomial Naive Bayes (Baseline) | alpha = 0.01 | 85.71% | 85.71% | Struggles with overlapping Spam/Phishing lexicons |

![Confusion Matrix & Risk Dashboard](docs/assets/confusion_matrix_and_dashboard.png)
*Figure 1: Test Set Confusion Matrix (Left) and Interactive Streamlit Risk Meter (Right).*

---

## 🎯 Business Problem & Context

Binary email filters ("Spam" vs. "Not Spam") fail to address modern phishing attacks, forcing users into binary choices. This system categorizes emails into three risk tiers with **calibrated probability scores** (e.g., *96.1% Phishing / 3.0% Spam / 0.9% Safe*), allowing security teams and end-users to make informed safety decisions.

**Metric Choice**: We prioritized **Precision on Ham (99.0%)** because false positives (flagging critical business communications as threats) disrupt business operations.

---

## 📊 Datasets & Sources Citation

Due to GitHub file size limits (>100 MB per file), raw and cleaned dataset files are excluded from this repository (`.gitignore`) and cited below.

- **Corpus Aggregation**: 131,026 total emails aggregated across four public datasets:
  - 🟢 **Ham (Low Risk)**: 42,805 samples (32.7%)
  - 🟡 **Spam (Mid Risk)**: 45,390 samples (34.6%)
  - 🔴 **Phishing (High Risk)**: 42,831 samples (32.7%)

### External Dataset Sources & Citations
1. **Enron Spam Dataset**: [Kaggle Dataset by Marcel Wiechmann](https://www.kaggle.com/datasets/marcelwiechmann/enron-spam-data)
2. **SpamAssassin Dataset**: [Kaggle Dataset by Ganiyu Olalekan](https://www.kaggle.com/datasets/ganiyuolalekan/spam-assassin-email-classification-dataset)
3. **Phishing Email Dataset**: [Kaggle Dataset by Naser Abdullah Alam](https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset)
4. **Email Spam Classification Dataset**: [Kaggle Dataset by Puru Singhvi](https://www.kaggle.com/datasets/purusinghvi/email-spam-classification-dataset)

### Data Preprocessing & Safeguards
- **Regex URL Safeguard**: Hyperlinks were normalized to a `url_link` placeholder to retain structural phishing cues without domain overfitting.
- **Leakage Controls**: An **80/20 stratified split** (104,820 train / 26,206 test) was applied. The TF-IDF vectorizer was fitted **exclusively on training data**.

---

## ⚙️ Model Architecture & Technical Choices
[Raw Email] ➔ [Regex & 'url_link' Normalization] ➔ [Tokenize & Lemmatize] ➔ [TF-IDF (1-3 N-grams, Max 100k)] ➔ [Calibrated LinearSVC] ➔ [Streamlit UI]

- **Why LinearSVC?** High-dimensional sparse TF-IDF text features benefit from linear margin classification, delivering **sub-millisecond inference speeds**.
- **Probability Calibration**: `CalibratedClassifierCV(method='sigmoid')` converts raw SVM decision distances into interpretable class probabilities.
- **Regularization Tuning**: GridSearch over $C \in \{0.1, 1.0, 10.0\}$ identified $C=0.1$ as optimal, preventing overfitting to training vocabulary.

---

## ⚠️ Failure Analysis ("Where the Model Breaks")

- **Ham Isolation (Success)**: Near-perfect separation of safe emails (99% Precision, 99% Recall, only 127 false positives out of 8,561 test cases).
- **Spam vs. Phishing Confusion (Failure Mode)**:
  - 1,396 Spam emails misclassified as Phishing.
  - 1,641 Phishing emails misclassified as Spam.
- **Root Cause**: Both classes share promotional language, urgency triggers ('verify account'), and `url_link` placeholders. TF-IDF frequency features lack deep contextual semantics needed to separate commercial marketing from malicious intent.

---

## 🛠️ Project Structure & Reproducibility

### Repository Structure
```text
├── Data_Cleaning.ipynb      # Merges & cleans 4 raw CSVs -> cleaned_email_dataset.csv
├── Modelling.ipynb          # Trains TF-IDF + LinearSVC -> exports pkl artifacts
├── app.py                   # Streamlit dashboard using exported models
├── requirements.txt         # Python dependency requirements
├── tfidf_vectorizer.pkl     # Pre-trained TF-IDF vectorizer artifact
└── email_model.pkl          # Pre-trained calibrated LinearSVC model artifact
Quick Start
Bash
# 1. Clone repository & install dependencies
git clone <your-repository-url>
cd email-risk-classifier
pip install -r requirements.txt

# 2. Launch interactive Streamlit Risk Assessment Dashboard
streamlit run app.py
Note: To retrain from scratch, download the 4 raw datasets from Kaggle into the project root and run Data_Cleaning.ipynb followed by Modelling.ipynb.

🛡️ License
Distributed under the MIT License.
