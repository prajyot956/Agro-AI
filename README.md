# 🌱 Agro-AI: The Intelligent Farming Assistant

**Agro-AI** is a cutting-edge, multimodal web application designed to empower farmers and agricultural enthusiasts through Artificial Intelligence. Built efficiently in Python using Streamlit, it leverages state-of-the-art Large Language Models (like Llama 4 Scout Vision via Groq API) to deliver real-time, actionable insights directly to farmers in their native languages. 

Whether you need a quick crop disease diagnosis from a photo, estimated market trends tailored to your local district, or simplified summaries of complex government agricultural schemes, Agro-AI acts as your free, intelligent, 24/7 personal consultant.

---

## ✨ Key Features

- 🔐 **Secure Role-Based Access:** Private login gateways tailored for administrators and verified farmers to keep analytical sessions secure.
- 🍃 **Instant Crop Health Diagnostics:** Upload an image of your crop and receive an immediate evaluation of plant health, disease identification, and treatment advice utilizing powerful Image-to-Text vision models.
- 📈 **Market Price Insights:** Stay ahead of the curve. Request specific crop market trends in your state/district to receive expert historical estimates and harvesting advice to maximize profits.
- 🏛️ **Government Scheme Summarizer:** Say goodbye to complex bureaucratic jargon! Enter any agricultural scheme name and instantly get a simplified, three-sentence summary of your eligibility and core benefits.
- 💬 **Contextual Follow-Up Chat:** It doesn't stop following the initial report! Seamlessly ask continuous follow-up questions within each module to dig deeper into your diagnosis or market report.
- 🌍 **Deep Multilingual Support:** AI-powered on-the-fly translation bridging the language gap. Instantly translate your interfaces and expert advice into Hindi, Gujarati, Marathi, Tamil, Telugu, Bengali, and English.

---

## 🚀 Quick Setup (Local Development)

It's incredibly easy to get Agro-AI running on your own machine.

### Prerequisites

Ensure you have Python 3.8+ installed on your system.

1. **Clone the project:**
   ```bash
   git clone https://github.com/your-username/Agro-AI.git
   cd Agro-AI
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API Keys:**
   Create a hidden Streamlit secrets file to store your API configuration safely. 
   Create `.streamlit/secrets.toml` at the root of your project and insert your free API key obtained from [Groq Console](https://console.groq.com):
   ```toml
   GROQ_API_KEY = "your-actual-api-key-here"
   ```

4. **Launch the Application:**
   ```bash
   python -m streamlit run app.py
   ```
   Navigate to `localhost:8501` to use the application! (Default accounts include `admin`/`admin` and `farmer`/`farmer`).

---

## ☁️ Deployment

Agro-AI is structured perfectly for instant cloud deployment. 

1. Ensure your codebase (excluding the `.streamlit` hidden folder) is pushed to a public or private GitHub repository. 
2. Go to [Streamlit Community Cloud](https://share.streamlit.io).
3. Connect your repository and select `app.py` as your main file path.
4. **Crucial:** Click on *Advanced Settings* before deploying and paste the contents of your `secrets.toml` inside the Secrets box to securely pass your API Key to the cloud.

---

### Built With:
* [Streamlit](https://streamlit.io/)
* [Groq](https://groq.com/) (Llama 3.3 70B & Llama 4 Scout Vision)
* [Python 3](https://python.org)
