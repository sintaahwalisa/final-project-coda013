# 🏗️ Data Engineering Workflow

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
