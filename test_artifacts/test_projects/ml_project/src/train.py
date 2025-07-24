"""
Customer Churn Prediction Model Training
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
import mlflow
import mlflow.sklearn
import joblib
import argparse
import os

def load_and_preprocess_data(data_path):
    """Load and preprocess the churn dataset"""
    df = pd.read_csv(data_path)
    
    # Handle missing values
    df = df.dropna()
    
    # Encode categorical variables
    le = LabelEncoder()
    categorical_columns = df.select_dtypes(include=['object']).columns
    
    for col in categorical_columns:
        if col != 'churn':  # Assuming 'churn' is the target
            df[col] = le.fit_transform(df[col])
    
    # Separate features and target
    X = df.drop('churn', axis=1)
    y = df['churn']
    
    # Encode target if it's categorical
    if y.dtype == 'object':
        y = le.fit_transform(y)
    
    return X, y

def train_model(X_train, X_test, y_train, y_test, model_type='rf'):
    """Train and evaluate a model"""
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Initialize model
    if model_type == 'rf':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    elif model_type == 'lr':
        model = LogisticRegression(random_state=42)
    elif model_type == 'xgb':
        model = xgb.XGBClassifier(random_state=42)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Train model
    model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred)
    }
    
    return model, scaler, metrics

def main():
    parser = argparse.ArgumentParser(description='Train churn prediction model')
    parser.add_argument('--data', default='data/customer_churn.csv', help='Path to training data')
    parser.add_argument('--model', default='rf', choices=['rf', 'lr', 'xgb'], help='Model type')
    parser.add_argument('--output', default='models/', help='Output directory for model')
    
    args = parser.parse_args()
    
    # Start MLflow run
    with mlflow.start_run():
        # Load and preprocess data
        X, y = load_and_preprocess_data(args.data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        model, scaler, metrics = train_model(X_train, X_test, y_train, y_test, args.model)
        
        # Log metrics
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(metric_name, metric_value)
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Save model and scaler
        os.makedirs(args.output, exist_ok=True)
        joblib.dump(model, f"{args.output}/model_{args.model}.pkl")
        joblib.dump(scaler, f"{args.output}/scaler_{args.model}.pkl")
        
        print(f"Model trained successfully!")
        print(f"Metrics: {metrics}")

if __name__ == "__main__":
    main()