"""
AI Job Market Analyzer — Data Generator
Generates: data/job_listings_raw.csv  (~10,200 rows)
Run: python generate_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random, os

random.seed(42)
np.random.seed(42)
os.makedirs("data", exist_ok=True)

# ── JOB TAXONOMY ──────────────────────────────────────────────────────────────
JOB_ROLES = {
    "Data Analyst":              {"skills": ["SQL","Excel","Power BI","Tableau","Python","R","Statistics","Data Visualization","Google Analytics","Looker"],                                        "salary_range": (400000,1200000),  "weight": 0.18},
    "Data Scientist":            {"skills": ["Python","Machine Learning","TensorFlow","PyTorch","SQL","Statistics","NLP","Scikit-learn","Deep Learning","R"],                                       "salary_range": (700000,2200000),  "weight": 0.15},
    "Machine Learning Engineer": {"skills": ["Python","TensorFlow","PyTorch","MLOps","Docker","Kubernetes","AWS","GCP","Feature Engineering","Model Deployment"],                                  "salary_range": (900000,2800000),  "weight": 0.12},
    "AI Engineer":               {"skills": ["Python","LLMs","LangChain","Prompt Engineering","RAG","Vector Databases","FastAPI","OpenAI API","Fine-tuning","NLP"],                                "salary_range": (1000000,3000000), "weight": 0.10},
    "Data Engineer":             {"skills": ["Python","SQL","Apache Spark","Kafka","Airflow","AWS","dbt","Snowflake","BigQuery","ETL Pipelines"],                                                  "salary_range": (800000,2500000),  "weight": 0.13},
    "Business Analyst":          {"skills": ["SQL","Excel","Power BI","Tableau","Requirements Gathering","JIRA","Agile","Stakeholder Management","Process Mapping","Visio"],                       "salary_range": (350000,1100000),  "weight": 0.12},
    "BI Developer":              {"skills": ["Tableau","Power BI","SQL","DAX","Looker","Data Modeling","ETL","SSRS","Excel","Python"],                                                             "salary_range": (500000,1500000),  "weight": 0.07},
    "NLP Engineer":              {"skills": ["Python","NLP","BERT","Transformers","spaCy","NLTK","HuggingFace","TensorFlow","Text Classification","Named Entity Recognition"],                    "salary_range": (900000,2500000),  "weight": 0.05},
    "Computer Vision Engineer":  {"skills": ["Python","OpenCV","YOLO","PyTorch","TensorFlow","CNN","Image Segmentation","Object Detection","NumPy","Deep Learning"],                              "salary_range": (900000,2600000),  "weight": 0.05},
    "MLOps Engineer":            {"skills": ["Python","Docker","Kubernetes","MLflow","Airflow","CI/CD","AWS","GCP","Terraform","Model Monitoring"],                                                "salary_range": (1000000,2800000), "weight": 0.06},
    "Quantitative Analyst":      {"skills": ["Python","R","Statistics","Financial Modeling","SQL","Excel","VBA","Risk Analysis","Monte Carlo Simulation","MATLAB"],                                "salary_range": (800000,3000000),  "weight": 0.04},
    "Research Scientist":        {"skills": ["Python","Deep Learning","Research Papers","PyTorch","TensorFlow","Mathematics","Statistics","NLP","Reinforcement Learning","Publications"],          "salary_range": (1200000,4000000), "weight": 0.03},
}

COMPANIES = {
    "FAANG/Big Tech":  ["Google","Microsoft","Amazon","Meta","Apple","Nvidia","IBM","Oracle","Salesforce","Adobe"],
    "Indian IT":       ["TCS","Infosys","Wipro","HCL Technologies","Tech Mahindra","Cognizant","Capgemini","Accenture India","Mphasis","LTIMindtree"],
    "Startups":        ["Razorpay","CRED","Meesho","Groww","PhonePe","Zepto","Slice","Setu","Juspay","Darwinbox"],
    "Analytics Firms": ["MuSigma","Fractal Analytics","Tiger Analytics","LatentView","Bridgei2i","Sigmoid","Crayon Data","Manthan","Absolutdata","EXL Analytics"],
    "Consulting":      ["Deloitte","McKinsey","BCG","PwC","KPMG","EY","Bain","ZS Associates","Gartner","IDC"],
    "Product":         ["Flipkart","Ola","Swiggy","Zomato","Nykaa","BigBasket","Urban Company","Lenskart","Cars24","Rapido"],
}
COMP_WEIGHTS = [0.15, 0.25, 0.20, 0.15, 0.10, 0.15]

LOCATIONS   = {"Bangalore":0.30,"Hyderabad":0.18,"Mumbai":0.15,"Delhi NCR":0.14,"Pune":0.10,"Chennai":0.07,"Kolkata":0.03,"Remote":0.03}
EXP_LEVELS  = {
    "Entry Level (0-2 yrs)":   {"mult":0.65,"weight":0.30,"lo":0, "hi":2},
    "Mid Level (2-5 yrs)":     {"mult":1.00,"weight":0.40,"lo":2, "hi":5},
    "Senior Level (5-8 yrs)":  {"mult":1.50,"weight":0.20,"lo":5, "hi":8},
    "Lead/Principal (8+ yrs)": {"mult":2.00,"weight":0.10,"lo":8, "hi":15},
}
INDUSTRIES = ["FinTech","E-Commerce","HealthTech","EdTech","SaaS","IT Services","Manufacturing","BFSI","Retail","Telecom","Media & Entertainment","Logistics","Real Estate","Gaming","GovTech"]
EDUCATION  = ["B.Tech/B.E.","M.Tech/M.E.","MCA","BCA","M.Sc (Data Science)","M.Sc (Statistics)","MBA","B.Sc (CS/IT)","PhD","BBA + Certification"]
JOB_TYPES  = ["Full-Time","Full-Time","Full-Time","Contract","Internship"]
SOURCES    = ["LinkedIn","Naukri","Indeed","Company Website","AngelList","Glassdoor","IIMJobs","Instahyre"]

def pick_skills(skills, n_req, n_opt):
    req = random.sample(skills, min(n_req, len(skills)))
    opt = random.sample([s for s in skills if s not in req], min(n_opt, len(skills)-len(req)))
    return "|".join(req), "|".join(opt)

# ── GENERATE ──────────────────────────────────────────────────────────────────
print("Generating job listings...")
role_names   = list(JOB_ROLES.keys())
role_weights = [JOB_ROLES[r]["weight"] for r in role_names]
exp_names    = list(EXP_LEVELS.keys())
exp_weights  = [EXP_LEVELS[e]["weight"] for e in exp_names]
comp_cats    = list(COMPANIES.keys())

rows = []
for i in range(1, 10201):
    role    = random.choices(role_names, weights=role_weights)[0]
    rcfg    = JOB_ROLES[role]
    exp     = random.choices(exp_names, weights=exp_weights)[0]
    ecfg    = EXP_LEVELS[exp]
    company = random.choice(COMPANIES[random.choices(comp_cats, weights=COMP_WEIGHTS)[0]])
    loc     = random.choices(list(LOCATIONS.keys()), weights=list(LOCATIONS.values()))[0]
    salary  = int(random.uniform(*rcfg["salary_range"]) * ecfg["mult"] / 10000) * 10000
    req, opt = pick_skills(rcfg["skills"], random.randint(3,5), random.randint(2,4))
    days_ago = random.randint(0, 365)
    rows.append({
        "JobID":              f"JOB{i:05d}",
        "Title":              role,
        "Company":            company,
        "CompanyCategory":    random.choices(comp_cats, weights=COMP_WEIGHTS)[0],
        "Industry":           random.choice(INDUSTRIES),
        "Location":           loc,
        "ExperienceLevel":    exp,
        "ExperienceYearsMin": ecfg["lo"],
        "ExperienceYearsMax": ecfg["hi"],
        "AnnualSalaryINR":    salary,
        "RequiredSkills":     req,
        "OptionalSkills":     opt,
        "EducationRequired":  random.choice(EDUCATION),
        "JobType":            random.choice(JOB_TYPES),
        "PostingSource":      random.choice(SOURCES),
        "DatePosted":         (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
        "IsRemote":           1 if loc == "Remote" else random.choices([0,1], weights=[0.85,0.15])[0],
        "IsActive":           random.choices([1,0], weights=[0.75,0.25])[0],
    })

df = pd.DataFrame(rows)
df.to_csv("data/job_listings_raw.csv", index=False)
print(f"  ✓ {len(df)} listings → data/job_listings_raw.csv")
print(f"  Roles: {df['Title'].nunique()} | Companies: {df['Company'].nunique()} | Avg Salary: ₹{df['AnnualSalaryINR'].mean():,.0f}")
print("Next → python etl_pipeline.py")
