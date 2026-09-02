# Machine Learning Virtual Lab

Auto ML Problem Detector - Identifies whether a dataset is suited for Classification or Regression.

## Project Structure

```
Machine-Learning-Virtual-Lab/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI server
│   └── detector.py      # Dataset analysis logic
├── requirements.txt
├── LICENSE
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Run Server

```bash
python -m backend.main
```

Server starts at `http://localhost:8000`

## API Endpoints

### POST `/api/analyze`

Analyzes a UCI dataset and detects problem type.

**Request:**
```json
{
  "code": "from ucimlrepo import fetch_ucirepo\n\nheart_disease = fetch_ucirepo(id=45)\nX = heart_disease.data.features\ny = heart_disease.data.targets"
}
```

**Response:**
```json
{
  "dataset_id": 45,
  "target_column": "num",
  "target_dtype": "int64",
  "unique_target_values": 5,
  "problem_type": "Classification",
  "reason": "Numeric target has relatively few unique values.",
  "num_features": 13,
  "num_samples": 303
}
```

### GET `/api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```
