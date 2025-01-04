# Social Media Simulator

A FastAPI-based simulator to practice safe social media interactions with AI-driven personas. This project aims to help users experience different types of interactions on social media and learn how to handle them safely.

## 🚀 Features
- User registration and login with JWT authentication
- AI-driven personas (e.g., scammer, bully, oversharer)
- MongoDB integration
- Interaction logging
- Educational focus on safe social media practices

## 📚 How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Osquared.git
cd Osquared
```

### 2. Set Up the Environment

Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Set Up MongoDB

Make sure you have MongoDB installed and running. Update the MongoDB connection string in the `config.py` file if necessary.

### 5. Run the Server

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

### 6. Access the Application

Open your browser and go to `http://127.0.0.1:8000` to access the application.

### 7. API Documentation

You can view the API documentation at `http://127.0.0.1:8000/docs` or `http://127.0.0.1:8000/redoc`.
