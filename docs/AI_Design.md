# AI_DESIGN.md

# Institutional Swing Trading Platform

**Version:** 1.0

---

# Overview

Artificial Intelligence is an auxiliary research component of the Institutional Swing Trading Platform.

The platform is **not AI-driven**.

It is **rule-driven**.

AI exists to improve research, discover hidden statistical relationships, rank opportunities, generate insights, and accelerate strategy evolution.

Production trading decisions always remain under deterministic trading rules defined by the Strategy Engines.

This separation eliminates "black-box trading" while still allowing the platform to benefit from machine learning and data science.

---

# AI Philosophy

The AI subsystem follows five permanent principles.

## Principle 1

AI assists.

Rules decide.

---

## Principle 2

Every AI recommendation must be explainable.

---

## Principle 3

Production trading never depends on a single model.

---

## Principle 4

Research and Production remain isolated.

---

## Principle 5

Every model is version controlled.

---

# AI Architecture

```
Historical Market Data

↓

Trade History

↓

Feature Engineering

↓

Dataset Builder

↓

Feature Store

↓

Model Training

↓

Model Validation

↓

Model Registry

↓

Prediction Service

↓

Research Reports

↓

Dashboard
```

Production trading engines consume AI insights only after deterministic validation.

---

# AI Responsibilities

The AI layer is responsible for:

- Opportunity Ranking
- Pattern Discovery
- Statistical Learning
- Feature Importance
- Performance Prediction
- Regime Classification
- Research Reports
- Explainability

The AI layer is **not** responsible for:

- Executing Orders
- Calculating Risk
- Managing Portfolio
- Bypassing Trading Rules
- Modifying Live Strategy

---

# Data Sources

The AI Engine continuously collects structured datasets.

Sources include:

- Historical Candles
- Watchlists
- Trend Objects
- Consolidation Objects
- Liquidity Grab Objects
- Trade Candidates
- Executed Trades
- Portfolio Metrics
- Analytics Reports
- Market Regimes

Every dataset is versioned.

---

# Feature Engineering

The Feature Engineering pipeline converts raw market data into machine-learning features.

Examples

Trend Features

- EMA50
- EMA200
- EMA Slope
- Relative Strength
- Trend Score

Consolidation Features

- Duration
- Width
- ATR Compression
- Volatility

Liquidity Grab Features

- Recovery Days
- Recovery Strength
- Breakdown Depth
- Volume Ratio
- Wick Length

Trade Features

- Entry Price
- Stop Loss
- RR
- Position Size
- Holding Days

Market Features

- Index Trend
- Sector Strength
- Volatility
- Market Breadth

Portfolio Features

- Portfolio Heat
- Exposure
- Correlation

Only validated features enter the training dataset.

---

# Dataset Builder

The Dataset Builder prepares clean datasets.

Pipeline

```
Raw Data

↓

Cleaning

↓

Validation

↓

Feature Extraction

↓

Normalization

↓

Label Generation

↓

Dataset Versioning

↓

Training Dataset
```

Every dataset receives

- Dataset ID
- Version
- Creation Time
- Feature Count
- Sample Count

---

# Model Training

Supported models may include

- LightGBM
- XGBoost
- Random Forest
- Logistic Regression
- Neural Networks (Future)

Training workflow

```
Dataset

↓

Split

↓

Training

↓

Validation

↓

Evaluation

↓

Model Registry
```

Models never skip validation.

---

# Model Validation

Every trained model is evaluated using

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix

For ranking models

- NDCG
- MAP
- Precision@K

Models failing predefined thresholds are rejected.

---

# Model Registry

Every approved model is stored in a centralized registry.

Stored information

- Model Version
- Dataset Version
- Feature Version
- Training Date
- Metrics
- Hyperparameters
- Status

Only approved models may generate predictions.

---

# Prediction Service

The Prediction Service generates AI insights.

Inputs

- Current Market State
- Engine Outputs
- Historical Features

Outputs

- Opportunity Score
- Confidence Score
- Expected Success Probability
- Feature Importance

Predictions remain advisory.

---

# Explainable AI

Every prediction should explain itself.

Example

```
Prediction Score

91

Confidence

87%

Top Reasons

- Strong Trend
- High Volume Ratio
- Fast Recovery
- Strong Sector
```

No unexplained prediction should appear on the dashboard.

---

# AI Research Pipeline

```
Historical Trades

↓

Feature Engineering

↓

Training

↓

Validation

↓

Prediction

↓

Human Review

↓

Research Report

↓

Possible Strategy Improvement
```

Research does not automatically alter production logic.

---

# Continuous Learning

Every completed trade contributes to future research.

```
Completed Trade

↓

Feature Extraction

↓

Dataset Update

↓

Future Training
```

The platform continuously expands its research dataset.

---

# Model Retraining

Retraining should occur periodically.

Triggers

- Scheduled Retraining
- Dataset Growth
- Model Drift
- New Features
- Strategy Updates

Retraining occurs offline.

---

# Drift Detection

The AI system continuously monitors

- Prediction Accuracy
- Feature Distribution
- Data Distribution
- Model Confidence

If significant drift is detected,

the model enters review.

---

# AI Outputs

The AI Engine produces

- Ranked Opportunities
- Feature Importance
- Pattern Reports
- Market Insights
- Regime Classification
- Research Recommendations

These outputs feed the Dashboard and Analytics.

---

# Human Approval

Every proposed AI improvement follows

```
AI Suggestion

↓

Research Review

↓

Backtesting

↓

Paper Trading

↓

Production Approval
```

AI never deploys itself.

---

# Security

AI models should remain protected.

Requirements

- Version Control
- Access Control
- Dataset Integrity
- Model Integrity
- Audit Logs

Training data must remain immutable after version creation.

---

# Performance Targets

| Component | Target |
|-----------|---------|
| Feature Engineering | <10 min |
| Dataset Build | <15 min |
| Model Training | Offline |
| Prediction | <100 ms |
| Explainability | <200 ms |
| Drift Detection | Daily |

---

# Future AI Expansion

Future capabilities may include

- Regime Detection
- Strategy Discovery
- Hyperparameter Optimization
- Reinforcement Learning (Research Only)
- Natural Language Research Assistant
- Multi-Strategy Ranking
- Portfolio Optimization
- Automated Feature Selection

All future capabilities remain subject to deterministic production governance.

---

# Engineering Decisions

The AI subsystem is intentionally isolated from live trading decisions.

Its purpose is to transform historical market data and completed trading outcomes into actionable research insights through structured datasets, feature engineering, supervised learning, explainable predictions, and continuous model evaluation.

By separating AI research from deterministic execution, the platform gains the benefits of machine learning without sacrificing explainability, auditability, or capital safety. Every model, dataset, prediction, and recommendation remains version-controlled, reproducible, and subject to human validation before influencing future strategy evolution.