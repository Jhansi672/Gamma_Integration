# Gamma Integration

This project integrates **Gamma's Public API (v0.2)** to generate AI-powered presentations (PDF or PPTX).

## How to Run
1. Clone the repo  
   `git clone https://github.com/Jhansi672/Gamma_Integration.git`
2. Install dependencies  
   `pip install -r requirements.txt`
3. Create `.env` file  
4. Run Streamlit  
`streamlit run app.py`

## How It Works
- `app.py`: Streamlit frontend for demo and testing.
- `gamma_service.py`: Calls Gamma API to generate presentations.
- Outputs are automatically downloaded as PDF or PPTX files.

## Security
- API key is stored only in `.env` (not in repo).
- HTTPS calls ensure secure data transfer.
