# AI-Based Multilingual Government Scheme & Job Assistant

An end-to-end AI/ML and FastAPI platform designed to help Indian citizens understand government schemes, notices, and benefits in simple language and regional languages (Hindi & English), as well as discover recent government job recruitments matching their exact educational qualifications.

---

## 🌟 Key Features

1. **Multilingual Scheme & Job RAG Search**:
   - Semantic cross-lingual retrieval powered by `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` and **ChromaDB**.
   - Accepts queries in Hindi or English (e.g., *"गरीब किसानों को 6000 रुपये मिलने वाली योजना"*, *"bank po jobs for graduates"*).
2. **Deep Neural Network Eligibility Matcher**:
   - PyTorch Deep Neural Network (`EligibilityNeuralNet`) trained on GPU with 98.56% validation accuracy.
   - Matches a citizen's age, qualification ladder (10th, 12th, Graduate, etc.), income, caste category, and state against all schemes and active job vacancies.
3. **Document OCR & Plain Language Explainer**:
   - Extracts text from uploaded government circulars, notice images, and PDFs via **EasyOCR** and **PyPDF**.
   - Simplifies dense bureaucratic language into plain, everyday language and finds matching scheme/job portals.
4. **Recent Job Notification Alerts**:
   - Categorized by qualification: 10th Pass (SSC GD, Postal GDS), 12th Pass (SSC CHSL, Police), Graduate (IBPS PO, UPSC Civil Services).
   - Provides direct official application links and deadlines.
5. **Interactive Multilingual Frontend**:
   - Streamlit citizen portal supporting instant language toggling between Hindi and English.

---

## 🚀 How to Run

### 1. Launch FastAPI Backend Server
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger API docs will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Launch Streamlit Frontend Portal
```powershell
.\.venv\Scripts\streamlit.exe run frontend_app.py
```
Open browser at: [http://localhost:8501](http://localhost:8501)

### 3. Run Automated End-to-End Tests
```powershell
.\.venv\Scripts\python.exe scripts\test_api_endpoints.py
```
