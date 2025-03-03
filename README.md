# Recommendation-Agent

---

# Personalized Recommendation App

This repository contains a microservice-based application that provides personalized recommendations. It consists of two components:

1. **FastAPI Server (main.py):**  
   Provides API endpoints for user management and recommendation retrieval.

2. **Streamlit Client (streamlit_app.py):**  
   A simple front-end for adding users and fetching recommendations.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
  - [Starting the FastAPI Server](#starting-the-fastapi-server)
  - [Launching the Streamlit App](#launching-the-streamlit-app)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [License](#license)

## Features

- **User Management:** Create new users by providing their interests, preferences, and demographics.
- **Personalized Recommendations:** Retrieve job and news recommendations based on user profiles.
- **Two-Component Architecture:** FastAPI serves as the backend API, while Streamlit provides a user-friendly front-end.

## Prerequisites

- Python 3.8 or higher
- [pip](https://pip.pypa.io/en/stable/)
- MongoDB 

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Harshwardhanpjadhav/Recommendation-Agent.git
   cd Recommendation-Agent
   ```

2. **Create and activate a virtual environment (optional but recommended):**

   ```bash
   python3 -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** Make sure your `requirements.txt` includes libraries such as:
   > - fastapi
   > - uvicorn
   > - streamlit
   > - pymongo
   > - newsapi-python
   > - requests

## Running the Application

### Starting the FastAPI Server

1. **Run the FastAPI server:**

   From the project root directory, run:

   ```bash
   uvicorn main:app --reload
   ```

   This will start the API server on [http://127.0.0.1:8000](http://127.0.0.1:8000). The `--reload` flag enables auto-reloading on code changes.

2. **API Endpoints:**

   - **POST** `/user/user-details`  
     Submit new user details (JSON payload).

   - **GET** `/recommendation/recommendations/?user_id=...`  
     Retrieve recommendations for a user.

### Launching the Streamlit App

1. **Run the Streamlit front-end:**

   In a separate terminal window (with the virtual environment activated), run:

   ```bash
   streamlit run streamlit_app.py
   ```

   This will open the Streamlit app in your default web browser, typically at [http://localhost:8501](http://localhost:8501).

2. **Using the App:**

   - **Add New User:**  
     Fill out the form with user ID, interests, preferences, and demographics.
   - **Get Recommendation:**  
     Enter the user ID and fetch recommendations.


## Project Structure

```
personalized-recommendation-app/
|--- app/
├── main.py                # FastAPI server file
├── streamlit_app.py       # Streamlit front-end file
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── test/
    └── test_api.py        # API test cases using pytest and FastAPI TestClient
```

## Data Input it takes
```
{
    "user_id": "1",
    "interests": [
      "technology"
    ],
    "preferences": {
      "language": "es",
      "max_recommendations": 10
    },
    "demographics": {
      "age": 30,
      "gender": "male",
      "occupation": "Software Engineer"
    }
  }
```
- It takes only this format input has schema defined in backend which allows only this structure format

## License

This project is licensed under the [MIT License](LICENSE).

---