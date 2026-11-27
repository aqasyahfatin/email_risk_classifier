import re
import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Import NLTK components for the backend preprocessing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Quietly download linguistic resources in the background
@st.cache_resource
def download_nltk_dependencies():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)

download_nltk_dependencies()

# 1. PAGE CONFIGURATION & THEME
st.set_page_config(
    page_title="Email Threat Intelligence Assessor",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for a clean, modern look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .reportview-container .main .block-container{ padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. PREPROCESSING LOGIC (Behind the Scenes)
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', ' url_link ', text, flags=re.MULTILINE)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    
    tokens = word_tokenize(text)
    
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return " ".join(tokens)

# 3. CACHED MODEL LOADING
@st.cache_resource
def load_security_artifacts():
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    model = joblib.load('email_model.pkl')
    return vectorizer, model

try:
    tfidf, security_model = load_security_artifacts()
    artifacts_loaded = True
except FileNotFoundError:
    artifacts_loaded = False

# 4. USER INTERFACE LAYOUT
st.title("🛡️ Email Risk Assessment & Intelligence System")
st.markdown("### WID3002 Natural Language Processing Project Dashboard")
st.write("Paste the raw text content of any suspicious email message below to check its safety rating.")

st.divider()

# Setup two-column layout for inputs and results dashboard
col_input, col_dashboard = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📋 Paste Email Content")
    email_input = st.text_area(
        "Email Body Content:", 
        height=350, 
        placeholder="Paste full text body here... (e.g., 'Dear User, your account has been suspended, click here to verify...')"
    )
    
    analyze_button = st.button("Analyze Email Safety")

with col_dashboard:
    st.subheader("📊 Safety Analysis Results")
    
    if not artifacts_loaded:
        st.error("🚨 **System Error:** Model files missing. Please make sure `email_model.pkl` and `tfidf_vectorizer.pkl` are in the app folder.")
    
    elif analyze_button:
        if email_input.strip() == "":
            st.warning("⚠️ **Input Missing:** Please paste an email body to analyze.")
        else:
            with st.spinner("Analyzing text safety signals..."):
                cleaned_payload = clean_text(email_input)
                vectorized_payload = tfidf.transform([cleaned_payload])
                
                # Get the probability percentages
                probabilities = security_model.predict_proba(vectorized_payload)[0]
                
                ham_prob = probabilities[0] * 100
                spam_prob = probabilities[1] * 100
                phish_prob = probabilities[2] * 100
                
                predicted_class = security_model.predict(vectorized_payload)[0]
                
                # Customize the dashboard theme based on the risk level found
                if predicted_class == 2:
                    severity_label = "Phishing (High Risk)"
                    alert_box = st.error
                    gauge_color = "#D32F2F"
                    advice = "🚨 **CRITICAL WARNING:** This email looks like a dangerous phishing scam. Do NOT click any links, do NOT reply, and never type your password or personal information into pages linked by this email."
                elif predicted_class == 1:
                    severity_label = "Spam (Mid Risk)"
                    alert_box = st.warning
                    gauge_color = "#F57C00"
                    advice = "⚠️ **SPAM ALERT:** This email shows typical junk, advertising, or promotional patterns. Proceed with caution."
                else:
                    severity_label = "Safe / Ham (Low Risk)"
                    alert_box = st.success
                    gauge_color = "#388E3C"
                    advice = "✅ **LOOKS SAFE:** This email appears normal and does not contain obvious scam or phishing threat indicators."

                # Pick the score of the predicted class to display on the gauge meter
                display_score = phish_prob if predicted_class == 2 else (spam_prob if predicted_class == 1 else ham_prob)
                
                # Render the visual user-friendly Risk Meter
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=display_score,
                    number={'suffix': "%", 'font': {'size': 40}},
                    title={'text': f"Result: {severity_label}", 'font': {'size': 18}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': gauge_color},
                        'bgcolor': "white",
                        'steps': [
                            {'range': [0, 35], 'color': "#E8F5E9"},  # Light Green zone
                            {'range': [35, 75], 'color': "#FFF3E0"},  # Light Orange zone
                            {'range': [75, 100], 'color': "#FFEBEE"}  # Light Red zone
                        ],
                    }
                ))
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                # Display the clear advice box
                alert_box(advice)
                
                # Display clear, non-technical probability table
                st.markdown("#### Threat Probability Breakdown")
                prob_matrix = pd.DataFrame({
                    "Risk Level": ["Low Risk (Safe)", "Mid Risk (Spam)", "High Risk (Phishing)"],
                    "System Confidence": [f"{ham_prob:.2f}%", f"{spam_prob:.2f}%", f"{phish_prob:.2f}%"]
                })
                st.table(prob_matrix)
    else:
        st.info("💡 **Ready to scan:** Paste an email on the left side and click 'Analyze Email Safety' to see the security evaluation.")