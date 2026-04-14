# 🧠 AI Job Market Analyzer

![Tableau](https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=tableau&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-27ae60?style=for-the-badge)

> An end-to-end job market intelligence pipeline — from raw listings to a 5-dashboard Tableau analytics suite — covering 10,000+ job postings across 12 data roles, 15 industries, and 7 cities.

---

## 📌 Overview

This project simulates a production-grade job market analytics system. It scrapes structure from messy job listing data, processes it through a modular ETL pipeline, and surfaces insights across hiring trends, skill demand, salary benchmarks, geographic distribution, and career gap analysis.

**Key questions answered:**
- Which data roles are hiring the most right now?
- What are the highest-paying skills in 2024?
- Which cities dominate AI/ML hiring in India?
- What skills are emerging (optional today → required tomorrow)?
- What's the salary range for each role × experience level?

---

## 📊 Dashboard Preview

| Dashboard | Focus |
|---|---|
| **Market Overview** | Listings by role, monthly trend, industry treemap, KPI summary |
| **Skills Intelligence** | Top 30 skills, role×skill heatmap, category donut, demand bubbles |
| **Salary Analysis** | Box plots, role×experience heatmap, salary bands, scatter |
| **Geographic Demand** | Symbol map, city heatmap, remote vs on-site breakdown |
| **Skill Gap Intelligence** | Gap quadrant, emerging skills, role-level gap comparison |

> 🔗 **[View Live Dashboard on Tableau Public](#)** ← replace with your link after publishing

---

## 🗂️ Repository Structure

```
ai-job-market-analyzer/
│
├── generate_data.py            # Synthetic data generator (10,200 listings)
├── etl_pipeline.py             # Full ETL: clean → transform → output 7 CSVs
├── skill_gap_analysis.py       # Deep-dive CLI skill gap tool
├── tableau_procedure.md        # Step-by-step Tableau build guide (5 dashboards)
├── README.md
│
├── data/
│   ├── job_listings_raw.csv        # Raw generated data (10,200 rows)
│   ├── job_listings_clean.csv      # ETL output — master clean table (10,003 rows)
│   ├── skills_frequency.csv        # 74 skills ranked by demand
│   ├── salary_by_role.csv          # Salary stats per role × experience level
│   ├── skill_gap_analysis.csv      # Skill gap scores and demand tiers
│   ├── role_skill_gap.csv          # Per-role gap breakdown
│   ├── hiring_trends_monthly.csv   # Monthly listing volume by role
│   └── location_demand.csv         # Listings and salary by city + role
│
└── dashboard/
    └── AI_Job_Market_Analyzer.twbx  # Tableau packaged workbook
```

---

## 📁 Dataset

### job_listings_clean.csv — 10,003 rows

| Column | Type | Description |
|---|---|---|
| JobID | String | Unique identifier (JOB00001+) |
| Title | String | One of 12 data roles |
| Company | String | 60 real Indian/global companies |
| CompanyCategory | String | FAANG / Indian IT / Startups / Analytics / Consulting / Product |
| Industry | String | 15 industries (FinTech, BFSI, EdTech...) |
| Location | String | 7 Indian cities + Remote |
| ExperienceLevel | String | Entry / Mid / Senior / Lead |
| AnnualSalaryINR | Integer | Realistic INR salary |
| SalaryBand | String | ₹0-5L / ₹5-10L / ₹10-15L ... ₹30L+ |
| RequiredSkills | String | Pipe-separated required skills |
| OptionalSkills | String | Pipe-separated nice-to-have skills |
| EducationRequired | String | Degree requirement |
| JobType | String | Full-Time / Contract / Internship |
| PostingSource | String | LinkedIn / Naukri / Indeed etc. |
| DatePosted | Date | Last 365 days |
| IsRemote | Boolean | 1 = Remote eligible |
| IsActive | Boolean | 1 = Listing still open |

**Dataset stats:**
- 10,003 listings · 12 job roles · 60 companies · 15 industries
- Avg salary: ₹15.8L · Range: ₹3L – ₹49.6L
- Active listings: 74.8% · Remote-eligible: 17.8%

---

## 🧮 ETL Pipeline

`etl_pipeline.py` runs 6 transformation stages:

```
[1] Extract        → Load raw CSV (10,200 rows)
[2] Transform      → Type casting, null removal, outlier filter, salary bands, experience brackets
[3] Skills Explode → Pipe-split skills → individual rows, frequency count, category tagging
[4] Salary Stats   → Median/mean/P25/P75 grouped by role × experience
[5] Skill Gap      → Required vs Optional frequency, GapScore, DemandTier labeling
[6] Aggregates     → Monthly hiring trends, location demand tables
```

**Outputs (7 files, all Tableau-ready):**

| File | Rows | Description |
|---|---|---|
| `job_listings_clean.csv` | 10,003 | Master fact table |
| `skills_frequency.csv` | 74 | Skills ranked by demand frequency |
| `salary_by_role.csv` | 48 | Role × level salary statistics |
| `skill_gap_analysis.csv` | 74 | Gap scores per skill |
| `role_skill_gap.csv` | 12 | Per-role gap breakdown |
| `hiring_trends_monthly.csv` | 156 | Monthly volume by role |
| `location_demand.csv` | 96 | Demand + salary by city |

---

## 🔍 Skill Gap Analysis

`skill_gap_analysis.py` provides a CLI tool for deep skill intelligence.

```bash
# All roles
python skill_gap_analysis.py

# Specific role
python skill_gap_analysis.py --role "Data Analyst"
python skill_gap_analysis.py --role "Machine Learning Engineer" --top 10

# All supported roles
# Data Analyst | Data Scientist | Machine Learning Engineer | AI Engineer
# Data Engineer | Business Analyst | BI Developer | NLP Engineer
# Computer Vision Engineer | MLOps Engineer | Quantitative Analyst | Research Scientist
```

**Sample output — Skill Gap Quadrant logic:**

```
 HIGH GAP │ Emerging Skills        │ Transition Skills
          │ (invest now)           │ (gap to bridge)
──────────┼────────────────────────┼──────────────────
  LOW GAP │ Niche / Specialised    │ Core Must-Haves
          │                        │ (Python, SQL...)
          └────────────────────────┴──────────────────
               LOW REQUIRED             HIGH REQUIRED
```

**Key findings from the dataset:**

- Python appears in **36%** of all job listings as a required skill
- NLP-related roles command the highest average salaries (~₹18.6L)
- Bangalore accounts for **30%** of all AI/Data listings
- LLMs, RAG, and Vector Databases are the fastest-emerging skills (high optional → rising required)
- Cross-role overlap is highest between BI Developer ↔ Data Analyst (SQL, Tableau, Power BI, Python)

---

## 🛠️ Tech Stack

| Tool | Role |
|---|---|
| **Python 3.8+** | Data generation, ETL orchestration |
| **Pandas** | Data cleaning, transformation, aggregation |
| **NumPy** | Vectorised operations, statistical simulation |
| **Tableau Desktop / Public** | 5-dashboard interactive analytics suite |
| **Power Query (M)** | Secondary data prep within Tableau data source |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/your-username/ai-job-market-analyzer.git
cd ai-job-market-analyzer

# 2. Install dependencies
pip install pandas numpy

# 3. Generate raw data
python generate_data.py

# 4. Run ETL pipeline
python etl_pipeline.py

# 5. Run skill gap analysis (optional)
python skill_gap_analysis.py --role "Data Analyst"

# 6. Open Tableau → connect data/job_listings_clean.csv
# Follow tableau_procedure.md for full dashboard build
```

---

## 📈 Sample Insights

```
Most In-Demand Role     : Data Analyst      (1,592 listings)
Highest Avg Salary      : Research Scientist (₹24.5L avg)
Top Location            : Bangalore          (3,035 listings, 30%)
Top Required Skill      : Python             (3,609 mentions, 36%)
Fastest-Emerging Skills : LLMs, RAG, LangChain, Vector Databases
Highest Salary Skill    : NLP / TensorFlow / PyTorch (~₹18-19L avg)
Remote % by Role        : AI Engineer (22%) > MLOps (21%) > Data Scientist (19%)
Cross-Role Overlap      : BI Dev ↔ Data Analyst share SQL, Tableau, Power BI, Python
```

---

## 📄 License

MIT License — free to use, adapt, and extend for learning or portfolio purposes.

---

## 👤 Author

**Jeeva**  
M.Sc. Data Science · VIT Vellore

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/your-username)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/your-profile)
[![Tableau Public](https://img.shields.io/badge/Tableau_Public-E97627?style=flat&logo=tableau&logoColor=white)](#)
