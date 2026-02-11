# Credit Card Fraud Detection Using Transaction Behavior Analysis

## 🏗️ Data Engineering Workflow

This project implements an **end-to-end data engineering pipeline** that transforms raw transactional data into **analytics-ready tables**, with **data quality validation enforced before loading into the data warehouse**.

---

## Pipeline Overview

```
Source Data
   ↓
Raw Layer
   ↓
Transformation (pandas)
   ↓
Data Quality Validation (Great Expectations)
   ↓
Data Warehouse (Serving Layer)
   ↓
Analytics & BI
```

---

## 1. Data Ingestion (Raw Layer)

### Objective
Ingest data from source systems and store it in its **original, unmodified format**.

### Process
- Extract raw transactional data from the source system  
- Store data without transformation  
- Preserve schema as-is  

### Output Structure
```
data/raw/
└── transaction_raw.csv
```

### Design Rationale
- Preserve original data for **audit and reprocessing**
- No schema enforcement at this stage
- Clear separation between **source** and **transformed** data

---

## 2. Data Transformation (Processed Layer — pandas)

### Objective
Clean, standardize, and transform raw data into **analytics-ready datasets**.

### Process
Transformation is implemented using **pandas**, including:
- Data type casting  
- Handling missing values  
- Duplicate removal  
- Business rule validation  
- Feature standardization  
- Modeling into analytical tables (e.g., fact tables)

### Output Structure
```
data/processed/
└── fact_transaction.csv
```

### Why pandas?
- Dataset size fits in memory
- Faster iteration for analytical workflows
- Readable and maintainable transformation logic
- Well suited for batch ETL and portfolio-scale projects

---

## 3. Data Quality Validation (Great Expectations)

### Objective
Ensure processed data meets **predefined quality rules** before loading into the warehouse.

### Process
- Validation runs after transformation  
- Great Expectations executes expectation suites  
- Validation triggered via **Checkpoint**
- Pipeline fails if validation does not pass  

### Example Expectations
- Primary key is **not null** and **unique**
- Mandatory fields are not null
- Numeric values fall within valid ranges
- Boolean fields contain only valid values

### Decision Gate
```
If validation fails  → Pipeline stops
If validation passes → Data is eligible for loading
```

### Why Validate After Transformation?
- Schema and business logic already finalized
- Expectations reflect downstream consumption needs
- Prevents invalid data from entering the warehouse

---

## 4. Load to Data Warehouse (Serving Layer)

### Objective
Load validated datasets into the data warehouse for analytics and reporting.

### Process
- Only validated datasets are loaded
- Fact tables stored in warehouse schema
- Data becomes accessible for BI and downstream analysis

### Output
```
Data Warehouse
└── fact_transaction
```

---

## 5. Orchestration (Apache Airflow)

### Objective
Automate, schedule, and monitor the pipeline execution.

### DAG Flow
```
python_extract
      ↓
python_transform
      ↓
python_validate
      ↓
python_load_to_data_warehouse
```

### Airflow Responsibilities
- Task scheduling  
- Dependency management  
- Retry and failure handling  
- Centralized logging  

---

## 6. Data Quality Documentation

### Objective
Provide transparency and observability for data validation.

### Process
- Validation results recorded by Great Expectations
- Data Docs generated after each checkpoint execution
- Enables inspection of:
  - Failed expectations
  - Historical validation runs

---

## 🧰 Technology Stack

| Layer          | Tools                      |
|----------------|----------------------------|
| Ingestion      | Python                     |
| Transformation | pandas                     |
| Data Quality   | Great Expectations         |
| Orchestration  | Apache Airflow             |
| Storage        | CSV / Data Warehouse       |
| Documentation  | Great Expectations Data Docs |

---

## 🎯 Key Design Principles

- Clear separation between **raw** and **processed** layers  
- Data quality as a **mandatory gate**, not just reporting  
- Fail fast when invalid data is detected  
- Maintain simple, readable transformations  
- Designed for scalability (can migrate to Spark if required)

## 📊 Data Analytics Project Overview

This project leverages **behavioral analytics** and **rule-based detection** to identify fraudulent credit card transaction patterns early, reducing financial losses and protecting legitimate transactions. By analyzing 1.29M+ transactions across 983 users, we uncover subtle fraud signals that traditional methods often miss.

### 1. Business Objective

**Detect early fraud signals before financial losses escalate** by analyzing statistical interdependencies and behavioral anomalies within transactional ecosystems.

### 2. Key Results

| Metric | Value |
|--------|-------|
| **Transactions Analyzed** | 1,296,675 |
| **Total Transaction Value** | $91.2 Million |
| **Users Analyzed** | 983 |
| **Fraud Rate** | 0.58% |
| **Best Rule-Based Uplift** | 24.84% |
| **Fraud Coverage** | ~51% (time-based) |

---

## 3. Problem Statement

### 1. The Challenge

Transaction data is inherently **complex and noisy**. Fraudulent signals are so subtle that they easily get lost, making early detection nearly impossible without systematic behavioral profiling.

### 2. Key Problems Identified

1. **Unusual Spending Patterns**: Users exhibit transaction behaviors that deviate significantly from their historical norms
2. **Merchant Anomalies**: Certain merchants show disproportionately high fraud rates
3. **Transaction Time Anomalies**: Fraud concentrates during specific time windows (10 PM - 12 AM)
4. **Delayed Detection Risks**: Late fraud detection leads to escalating financial losses

---

## 4. Data Analytics Approach

### 1. Exploratory Data Analysis (EDA)

We conducted comprehensive EDA to answer five critical questions:

#### **Question 1: Does fraud occur at the user level or transaction level?**

**Finding:**
- **77.52%** of users are involved in fraud (762 out of 983)
- Only **0.58%** of transactions are fraudulent (7,520 out of 1,296,675)

**Insight:** Fraud occurrence is highly concentrated at the **user level**, suggesting repeated behavior rather than isolated incidents. This strong class imbalance requires precision-focused detection strategies.

---

#### **Question 2: Is fraud a repeated behavior or isolated incidents?**

**Statistical Analysis:**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Mean Fraud Count** | 9.85 | Average fraudulent user commits ~10 frauds |
| **Median** | 10 | Central tendency confirms habitual behavior |
| **IQR (25%-75%)** | 8-12 | 50% of fraud users commit 8-12 frauds |
| **Range** | 2-19 | All fraudulent users show repeated behavior |
| **Coefficient of Variation** | ~30.1% | Relatively consistent fraud frequency |

**Insight:** Fraud is **habitual, not a one-time event**. All fraudulent users exhibit repeated fraud behavior (minimum 2 occurrences, up to 19). This indicates detection should focus on user-level patterns.

---

#### **Question 3: Does higher transaction amount indicate fraud?**

**Comparative Analysis:**

| Metric | Non-Fraud | Fraud | Ratio |
|--------|-----------|-------|-------|
| **Median** | $47.28 | $396.51 | **8.4×** |
| **Mean** | $67.67 | $531.32 | **7.8×** |
| **P90** | $134.21 | $1,024.60 | **7.6×** |
| **Maximum** | $28,948.90 | $1,376.04 | Fraud capped |

**Insight:** 
- Fraud transactions are consistently **7-8× higher** in value
- However, fraudulent amounts are **more tightly bounded** (max $1,376 vs. $28,949 for legitimate)
- This suggests **calculated evasion** — fraudsters avoid extremely large amounts that trigger automatic blocking

---

#### **Question 4: Are underage users more prone to fraud?**

**Age-Based Fraud Rate Analysis:**

| Age Group | Transactions | Frauds | Fraud Rate |
|-----------|-------------|--------|------------|
| **Underage (≤18)** | 21,065 | 137 | 0.65% |
| **19-25** | 123,539 | 758 | 0.61% |
| **26-35** | 299,697 | 1,417 | **0.47%** ⬇️ |
| **36-50** | 412,476 | 1,927 | **0.47%** ⬇️ |
| **50+** | 439,898 | 3,267 | **0.74%** ⬆️ |

**Key Findings:**
- **Prime-age groups (26-50)** have the **lowest fraud rates** (~0.47%), indicating more stable transaction behavior
- **Underage users** show moderate risk (0.65%), similar to 19-25 age group
- **50+ segment records the highest fraud rate** (0.74%), suggesting increased vulnerability due to:
  - Social engineering attacks
  - Lower digital literacy
  - Scam susceptibility

---

#### **Question 5: At what time of day is fraud rate highest?**

**Temporal Pattern Analysis:**

| Time Window | Fraud Cases | % of Total Fraud |
|-------------|-------------|------------------|
| **22:00-22:59** | 1,616 | ~21.5% |
| **23:00-23:59** | **1,904** | **~25.4%** 🔴 |
| **00:00-00:59** | 315 | ~4.2% |
| **10 PM - 12 AM Combined** | **~3,835** | **~51%** |

**Insight:** 
- Fraud activity is **strongly time-dependent**
- **Late-night hours (10 PM - 12 AM)** account for ~51% of all fraud
- Elevated risk during periods when transaction monitoring and user oversight may be reduced

---

## 5. Behavioral Fraud Signals

Based on our analysis, we identified four key behavioral signals:

### 1. **Habitual, Not a One-Time Event**
- Fraud cases are driven by **repeated user behavior**, not isolated incidents
- Detection should focus on user-level patterns rather than single transactions

### 2. **Calculated Evasion**
- Fraud transactions are usually **higher in value**, but avoid extremely large amounts
- Reflects deliberate, risk-aware behavior to avoid triggering automated detection

### 3. **The Late-Night Window**
- Fraud risk is **strongly time-dependent**
- Large share of fraudulent activity occurs during late-night hours

### 4. **Operational Prioritization**
- Demographic factors (age) help translate behavioral signals into **practical rule-based controls**
- Enables targeting under limited validation capacity

---

## 6. Rule-Based Fraud Detection Strategy

### Approach

To detect and mitigate fraud efficiently, we implemented a **rule-based fraud detection strategy** that triggers OTP verification for selected age segments.

**Constraint:** OTP delivery incurs a cost, so the company allocates a fixed budget for OTP usage (assumed at **20% of transactions**).

### Detection Workflow

```
Incoming Transactions → Age Segmentation → Apply Rules → OTP Verification → Fraud Prevention
```

### Rule Performance Comparison

**Baseline Fraud Rate:** 0.5789% (before any validation rules)

| Rule | Target | Coverage | Fraud Rate After | Fraud Reduction | **Fraud Uplift** |
|------|--------|----------|------------------|-----------------|------------------|
| **Rule 1** | Youngest (13-30) | ~20.84% | 0.4582% | 0.1207 | **20.85%** |
| **Rule 2** ✅ | Oldest (61-95) | ~19.65% | 0.4350% | 0.1438 | **24.84%** |
| **Rule 3** | 10% Young + 10% Old | ~20.25% | 0.4466% | 0.1322 | **22.85%** |

### Recommended Strategy: Rule 2 (Oldest Users)

**Why?**
- Delivers the **highest fraud uplift (24.84%)**
- Covers ~19.65% of transactions (within 20% OTP budget)
- Optimizes fraud prevention impact per OTP sent

**Implementation:**
```python
if user_age >= 61 and user_age <= 95:
    trigger_otp_verification()
```

---

## 7. Statistical Analysis Techniques

### 1. **Descriptive Statistics**
- Mean, median, mode, standard deviation
- Percentile analysis (P25, P50, P75, P90)
- Coefficient of variation for consistency measurement

### 2. **Comparative Analysis**
- Fraud vs. non-fraud transaction amounts
- Age-based fraud rate comparison
- Time-based fraud concentration

### 3. **Distribution Analysis**
- Transaction amount distribution (fraud vs. non-fraud)
- Fraud count distribution across users
- Temporal fraud pattern distribution

### 4. **Correlation Analysis**
- User demographics vs. fraud propensity
- Transaction timing vs. fraud likelihood
- Transaction amount vs. fraud probability

---

## 8. Next Steps & Recommendations

### ACCESS Framework
**A**ssess → **C**lassify → **C**ombine → **E**valuate → **S**cale → **S**afeguard

### Immediate Actions (Rule-Based Enhancement)

#### 1. **Time-Based Rule Enhancement**
**Proposed Control:**
- Implement additional OTP verification during 10:00 PM - 12:00 AM window

**Expected Impact:**
- Capture ~51% of total fraud
- Transaction coverage: ~10%

**Implementation:**
```python
from datetime import datetime

def should_trigger_time_based_otp(transaction_timestamp):
    hour = transaction_timestamp.hour
    return 22 <= hour <= 23  # 10 PM - 11:59 PM
```

#### 2. **Multi-Signal Rule Framework**
**Action:** Combine age-based and time-based rules

**Example:**
```python
def should_trigger_otp(user_age, transaction_timestamp):
    age_risk = user_age >= 61
    time_risk = 22 <= transaction_timestamp.hour <= 23
    
    # High risk: Both conditions met
    if age_risk and time_risk:
        return True, "HIGH_RISK"
    
    # Medium risk: One condition met
    elif age_risk or time_risk:
        return True, "MEDIUM_RISK"
    
    # Low risk: No conditions met
    else:
        return False, "LOW_RISK"
```

### Long-Term Strategy (Machine Learning)

#### 3. **Machine Learning Model Development**

**Approach:**
- Use rule-based features (age, time, frequency, amount) as ML training features
- Learn non-linear patterns that rules cannot capture

**Feature Engineering:**
```python
features = [
    'user_age',
    'transaction_hour',
    'transaction_amount',
    'user_fraud_count_historical',
    'avg_transaction_amount_last_30_days',
    'transaction_count_last_7_days',
    'merchant_fraud_rate',
    'time_since_last_transaction_minutes'
]
```

**Model Candidates:**
- Random Forest (interpretable, handles non-linearity)
- XGBoost (high performance on imbalanced data)
- Logistic Regression with engineered features (baseline)

**Evaluation Metrics:**
- Precision (minimize false positives)
- Recall (maximize fraud capture)
- F1-Score (balance precision-recall)
- ROC-AUC (overall discrimination)
- Fraud Uplift % (business metric)

---

## 9. Methodology Summary

### Data Collection
- **Source:** Kaggle credit card transactions dataset
- **Period:** 2019-2020 fiscal year
- **Volume:** 1,296,675 transactions

### Data Processing
1. **ETL Pipeline:** Extract → Transform → Validate → Load
2. **Data Quality:** Great Expectations validation (NOT NULL, UNIQUE, TYPE checks)
3. **Feature Engineering:** Date dimensions, age calculations, merchant deduplication

### Analytical Techniques
1. **Univariate Analysis:** Distribution analysis for key variables
2. **Bivariate Analysis:** Fraud vs. non-fraud comparisons
3. **Temporal Analysis:** Hour-of-day, day-of-week patterns
4. **Segmentation Analysis:** Age-based, merchant-based, amount-based

### Visualization Tools
- **Python Libraries:** Matplotlib, Seaborn
- **BI Tools:** Looker Studio (interactive dashboards)

---

## 10. Key Learnings

### 1. **Class Imbalance is Critical**
- Fraud represents only 0.58% of transactions
- Requires precision-focused metrics, not just accuracy
- Rule-based approaches work well for highly imbalanced data

### 2. **User-Level Patterns > Transaction-Level**
- 77.52% of users involved in fraud show repeated behavior
- Focus detection on user behavior profiles, not isolated transactions

### 3. **Fraud is Calculated, Not Random**
- Fraudsters deliberately stay below detection thresholds
- Transaction amounts are "risk-aware" (high but not extreme)

### 4. **Temporal Patterns are Exploitable**
- 51% of fraud occurs in 2-hour window (10 PM - 12 AM)
- Suggests fraudsters target low-monitoring periods

### 5. **Age is a Proxy for Vulnerability**
- 50+ segment shows highest fraud rate (0.74%)
- Indicates need for age-specific protection measures

---

## 🔗 Resources

### Documentation
- [GitHub Repository](https://github.com/dhiasrenaldy01-ai/final-project-coda013)
- [Interactive Dashboard](https://lookerstudio.google.com/...)

---

## 🤝 Contributing

This project is part of the **CODA RMT 013** data engineering and analytics portfolio. For questions or collaboration:

- **Author:** Arief Bagus Nugraha, Paulus Marpaung, Dhias Renaldy, Nabilah Astiarini, Sinta Ahwalisa
- **LinkedIn:**: [linkedin.com/in/ariefbn13](https://www.linkedin.com/in/ariefbn13/)
- **LinkedIn:**: [linkedin.com/in/withpaulusmarpaung](https://www.linkedin.com/in/withpaulusmarpaung/)
- **LinkedIn:**:  [linkedin.com/in/dhiasrenaldy](https://www.linkedin.com/in/dhias-renaldy/))
- **LinkedIn:** [linkedin.com/in/sintaahwalisa](https://linkedin.com/in/sintaahwalisa)
- **LinkedIn:** [linkedin.com/in/nabilahastiarini](https://www.linkedin.com/in/nabilahastiarini/)

---

## 📄 License

This project is for educational and portfolio purposes. Dataset source attribution follows Kaggle's terms of use.

---

## Acknowledgments

- **Dataset:** Kaggle Credit Card Fraud Detection Dataset
- **Tools:** Python (Pandas, PySpark), Apache Airflow, PostgreSQL (Neon), Great Expectations, Looker Studio
- **Inspiration:** Financial fraud detection challenges and sustainable development goals (SDG 8)

---

