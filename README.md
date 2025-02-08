# MediAI - Medical Report Analysis & Prediction System

## Live Demo (frontend)
[HealthVault](https://healthhackverse.netlify.app)

## Overview
MediAI is an advanced medical analysis system that combines machine learning, natural language processing, and data analytics to provide medical report analysis and disease/medicine predictions. The system uses ensemble learning methods and Claude AI for comprehensive medical insights.

## Features

### Medical Report Analysis
- PDF medical report upload and processing
- Natural language processing using Claude AI
- Detailed report analysis including:
  - Layman terms summary
  - Key medical findings with emoji indicators
  - Medical terminology explanations
  - Personalized recommendations

### Disease & Medicine Prediction
- Dual prediction system:
  - Advanced predictor using Gradient Boosting
  - Basic predictor using Random Forest
- Features include:
  - Disease prediction with confidence scores
  - Medicine recommendations
  - Model accuracy metrics
  - Multi-label classification

### Data Management
- Excel file upload functionality
- Automated data cleaning and validation
- JSON database integration
- Training data management

## Technical Stack

### Backend
- FastAPI framework
- Python 3.9+
- Scikit-learn for ML models
- PyPDF2 for PDF processing
- Pandas for data manipulation
- Claude AI integration

### Machine Learning
- Ensemble Methods:
  - Gradient Boosting Classifier
  - Random Forest Classifier
- Feature Engineering:
  - Label Encoding
  - Multi-label Binarization
- Model Evaluation:
  - Train-Test Split
  - Accuracy Metrics
  - Confidence Scoring

### Data Processing
- PDF text extraction
- Excel data processing
- JSON data management
- Data validation and cleaning

## API Endpoints

### Medical Analysis
- `/upload` - PDF medical report upload and analysis
- `/predict-medical` - Disease and medicine prediction
- `/upload-excel` - Training data upload

## System Requirements
- Python 3.9+
- FastAPI
- Scikit-learn
- PyPDF2
- Pandas
- Claude AI API access
- Latest nodejs installed

## Installation and running
### For Backend
```bash
cd backend
python -m venv venv # do pip install venv if venv not installed
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
- After doing this go into config.js in backend directory and replace the cookie with your claude api cookie
### For Frontend
```bash
cd frontend
npm i
npm run dev
```

## Performance Metrics
- Disease Prediction Accuracy: 64.71%
- Medicine Prediction Accuracy: 74.51%

## Security
- CORS middleware implementation
- File upload validation
- Error handling and logging
- Secure API endpoints

## Logging
- Comprehensive logging system
- Debug level logging
- Error tracking and reporting

## Data Storage
- Local file system for uploads
- JSON database for training data
- Structured data validation

## Future Enhancements
- Enhanced ML model accuracy
- Additional file format support
- Real-time prediction updates
- Advanced data visualization
- API rate limiting
- Cloud storage integration

