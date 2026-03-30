# 🚆 London Crime & Public Transport Analytics
### *An End-to-End Data Science Pipeline: Extraction, Prediction, and Geospatial Animation*

## 📌 Project Overview
This repository contains a comprehensive Python-based pipeline designed to analyse crime patterns across London. The project spans three critical phases: 
1.  **Data Engineering:** Automating the cleanup of complex, non-standard Excel reports from the Greater London Authority (GLA).
2.  **Predictive Modelling:** Using regression techniques to forecast crime trends.
3.  **Advanced Visualisation:** Generating interactive choropleth maps and time-lapse animations to visualise "crime hotspots" geographically.

---

## 🛠️ Technical Workflow

### 1. Data Cleaning & Transformation (`Part 1`)
Raw data often comes in "Financial Year" blocks, which are difficult to analyse. 
* **What I did:** Built a custom parser in `pandas` to convert multi-header Excel sheets into a clean "long-format" time-series dataset.
* **Result:** A unified dataset containing transport modes (Bus, LU, DLR), crime categories, and temporal data ready for modelling.

### 2. Exploratory Data Analysis & Regression (`Part 2`)
* **What I did:** Conducted EDA to find correlations between transport volume and crime rates. Implemented **Polynomial Regression** via `scikit-learn` to capture non-linear trends in the data.
* **Result:** Predictive models that help estimate future crime volumes based on historical monthly patterns.

### 3. Geospatial Animation & Mapping (`Part 3`)
* **What I did:** Integrated `GeoPandas` with London borough shapefiles. Developed a script that allows users to select a specific crime type (e.g., "Violence" or "Burglary") and see its evolution over time.

---

## 📂 Repository Structure

| File | Purpose |
| :--- | :--- |
| `gla-data-science-project-part1.ipynb` | Data extraction and "Long-Format" conversion. |
| `gla-data-science-project-part2.ipynb` | Regression modelling and performance evaluation. |
| `part3_step01.py` | Geospatial engine for generating PNGs and MP4s. |
| `test_part3.py` | Unit tests for the visualization and filtering logic. |

---

## 🚀 Getting Started

### Prerequisites
```bash
pip install pandas matplotlib seaborn scikit-learn geopandas openpyxl pytest
