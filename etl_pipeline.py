"""
AI Job Market Analyzer — ETL Pipeline
Input:  data/job_listings_raw.csv
Output: data/job_listings_clean.csv
        data/skills_frequency.csv
        data/salary_by_role.csv
        data/skill_gap_analysis.csv
        data/hiring_trends_monthly.csv
        data/location_demand.csv

Run: python etl_pipeline.py
"""

import pandas as pd
import numpy as np
from collections import Counter
import warnings, os
warnings.filterwarnings("ignore")

os.makedirs("data", exist_ok=True)

print("=" * 60)
print("  AI Job Market Analyzer — ETL Pipeline")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# STEP 1: EXTRACT
# ─────────────────────────────────────────────────────────────
print("\n[1/6] Extracting raw data...")
df = pd.read_csv("data/job_listings_raw.csv")
raw_count = len(df)
print(f"  Loaded {raw_count:,} rows × {df.shape[1]} columns")

# ─────────────────────────────────────────────────────────────
# STEP 2: TRANSFORM — Data Cleaning
# ─────────────────────────────────────────────────────────────
print("\n[2/6] Transforming & cleaning...")

# 2a. Date parsing
df["DatePosted"] = pd.to_datetime(df["DatePosted"], errors="coerce")
df["PostingYear"]  = df["DatePosted"].dt.year
df["PostingMonth"] = df["DatePosted"].dt.month
df["PostingMonthName"] = df["DatePosted"].dt.strftime("%b")
df["PostingYearMonth"] = df["DatePosted"].dt.to_period("M").astype(str)
df["DaysOld"] = (pd.Timestamp.today() - df["DatePosted"]).dt.days

# 2b. Drop nulls in critical columns
before = len(df)
df.dropna(subset=["Title","Company","AnnualSalaryINR","RequiredSkills"], inplace=True)
after = len(df)
print(f"  Dropped {before - after} rows with null critical fields")

# 2c. Salary outlier filter (1st–99th percentile)
lo, hi = df["AnnualSalaryINR"].quantile([0.01, 0.99])
df = df[(df["AnnualSalaryINR"] >= lo) & (df["AnnualSalaryINR"] <= hi)]
print(f"  Salary outlier filter: kept {len(df):,} rows (₹{lo:,.0f}–₹{hi:,.0f})")

# 2d. Salary bands
def salary_band(s):
    if s < 500000:   return "₹0–5L"
    elif s < 1000000: return "₹5–10L"
    elif s < 1500000: return "₹10–15L"
    elif s < 2000000: return "₹15–20L"
    elif s < 3000000: return "₹20–30L"
    else:             return "₹30L+"
df["SalaryBand"] = df["AnnualSalaryINR"].apply(salary_band)

# 2e. Experience bracket
def exp_bracket(row):
    lo, hi = row["ExperienceYearsMin"], row["ExperienceYearsMax"]
    mid = (lo + hi) / 2
    if mid <= 1:   return "Fresher (0-1yr)"
    elif mid <= 3: return "Junior (1-3yrs)"
    elif mid <= 6: return "Mid (3-6yrs)"
    elif mid <= 10:return "Senior (6-10yrs)"
    else:          return "Principal (10+yrs)"
df["ExperienceBracket"] = df.apply(exp_bracket, axis=1)

# 2f. Standardise text columns
for col in ["Title","Company","Location","Industry","ExperienceLevel"]:
    df[col] = df[col].str.strip().str.title()

# 2g. Boolean flag cleanup
df["IsRemote"]  = df["IsRemote"].astype(int)
df["IsActive"]  = df["IsActive"].astype(int)

clean_count = len(df)
print(f"  ✓ Clean dataset: {clean_count:,} rows ({clean_count/raw_count*100:.1f}% retained)")

# ─────────────────────────────────────────────────────────────
# STEP 3: SKILLS EXPLOSION
# ─────────────────────────────────────────────────────────────
print("\n[3/6] Exploding & counting skills...")

all_skills = []
for _, row in df.iterrows():
    req = [s.strip() for s in str(row["RequiredSkills"]).split("|") if s.strip()]
    opt = [s.strip() for s in str(row["OptionalSkills"]).split("|")  if s.strip()]
    for s in req:
        all_skills.append({"Skill": s, "Type": "Required", "Role": row["Title"], "Location": row["Location"]})
    for s in opt:
        all_skills.append({"Skill": s, "Type": "Optional", "Role": row["Title"], "Location": row["Location"]})

df_skills = pd.DataFrame(all_skills)

# Skill frequency across all listings
skill_freq = (
    df_skills[df_skills["Type"] == "Required"]
    .groupby("Skill")
    .size()
    .reset_index(name="Frequency")
    .sort_values("Frequency", ascending=False)
)
skill_freq["Rank"] = range(1, len(skill_freq) + 1)
skill_freq["FrequencyPct"] = (skill_freq["Frequency"] / clean_count * 100).round(2)

# Category tag
def skill_category(s):
    cats = {
        "Programming":     ["Python","R","SQL","Java","Scala","Julia","MATLAB","VBA","C++"],
        "ML/DL":           ["Machine Learning","Deep Learning","TensorFlow","PyTorch","Scikit-learn","CNN","YOLO","BERT","Transformers","Reinforcement Learning","Fine-tuning"],
        "Cloud/DevOps":    ["AWS","GCP","Azure","Docker","Kubernetes","Terraform","CI/CD","Airflow","Kafka","MLflow"],
        "Visualization":   ["Tableau","Power BI","Looker","Data Visualization","SSRS","Google Analytics"],
        "Data Platforms":  ["Snowflake","BigQuery","dbt","Apache Spark","ETL Pipelines","ETL","Feature Engineering","Model Deployment","Model Monitoring"],
        "NLP/AI":          ["NLP","LLMs","LangChain","Prompt Engineering","RAG","Vector Databases","OpenAI API","spaCy","NLTK","HuggingFace","Text Classification","Named Entity Recognition"],
        "Analytics Tools": ["Excel","Statistics","Data Modeling","DAX","Requirements Gathering","Process Mapping","Financial Modeling","Risk Analysis","Monte Carlo Simulation"],
        "Vision":          ["OpenCV","Image Segmentation","Object Detection"],
        "Soft/Process":    ["JIRA","Agile","Stakeholder Management","Visio","Research Papers","Publications"],
    }
    for cat, skills in cats.items():
        if s in skills:
            return cat
    return "Other"

skill_freq["Category"] = skill_freq["Skill"].apply(skill_category)
skill_freq.to_csv("data/skills_frequency.csv", index=False)
print(f"  ✓ {len(skill_freq)} unique skills → data/skills_frequency.csv")

# ─────────────────────────────────────────────────────────────
# STEP 4: SALARY ANALYSIS
# ─────────────────────────────────────────────────────────────
print("\n[4/6] Computing salary statistics...")

salary_stats = (
    df.groupby(["Title","ExperienceLevel"])["AnnualSalaryINR"]
    .agg(
        Count="count",
        MedianSalary="median",
        MeanSalary="mean",
        MinSalary="min",
        MaxSalary="max",
        P25="quantile",
        P75=lambda x: x.quantile(0.75),
    )
    .reset_index()
)
salary_stats = salary_stats.round(0)
salary_stats.to_csv("data/salary_by_role.csv", index=False)
print(f"  ✓ {len(salary_stats)} role×level combinations → data/salary_by_role.csv")

# ─────────────────────────────────────────────────────────────
# STEP 5: SKILL GAP ANALYSIS
# ─────────────────────────────────────────────────────────────
print("\n[5/6] Running skill gap analysis...")

# For each role: count required vs optional skill demand
skill_by_role = (
    df_skills.groupby(["Role","Skill","Type"])
    .size()
    .reset_index(name="Count")
)

# Top 5 required skills per role
top_skills_per_role = (
    skill_by_role[skill_by_role["Type"] == "Required"]
    .sort_values(["Role","Count"], ascending=[True, False])
    .groupby("Role")
    .head(5)
)

# Skill gap: skills often in optional but rarely in required (opportunity skills)
req_counts = skill_freq[skill_freq["Type"] == "Required"][["Skill","Frequency"]].rename(columns={"Frequency":"ReqFreq"}) if "Type" in skill_freq.columns else skill_freq[["Skill","Frequency"]].rename(columns={"Frequency":"ReqFreq"})
opt_counts = (
    df_skills[df_skills["Type"] == "Optional"]
    .groupby("Skill").size().reset_index(name="OptFreq")
)
gap_df = req_counts.merge(opt_counts, on="Skill", how="outer").fillna(0)
gap_df["GapScore"] = (gap_df["OptFreq"] - gap_df["ReqFreq"]).clip(lower=0)
gap_df["DemandTier"] = pd.cut(
    gap_df["ReqFreq"],
    bins=[0, 100, 400, 800, 99999],
    labels=["Low","Medium","High","Critical"]
)
gap_df.sort_values("GapScore", ascending=False, inplace=True)
gap_df.to_csv("data/skill_gap_analysis.csv", index=False)
print(f"  ✓ Skill gap computed for {len(gap_df)} skills → data/skill_gap_analysis.csv")

# Per-role skill gap
role_skill_gap = []
for role in df["Title"].unique():
    role_req = set(df_skills[(df_skills["Role"]==role) & (df_skills["Type"]=="Required")]["Skill"].unique())
    role_opt = set(df_skills[(df_skills["Role"]==role) & (df_skills["Type"]=="Optional")]["Skill"].unique())
    gap_skills = role_opt - role_req
    role_skill_gap.append({
        "Role":                role,
        "RequiredSkillCount":  len(role_req),
        "OptionalSkillCount":  len(role_opt),
        "GapSkillCount":       len(gap_skills),
        "TopRequiredSkills":   ", ".join(list(role_req)[:5]),
        "TopGapSkills":        ", ".join(list(gap_skills)[:5]),
    })
pd.DataFrame(role_skill_gap).to_csv("data/role_skill_gap.csv", index=False)
print(f"  ✓ Per-role gap → data/role_skill_gap.csv")

# ─────────────────────────────────────────────────────────────
# STEP 6: HIRING TRENDS & LOCATION
# ─────────────────────────────────────────────────────────────
print("\n[6/6] Computing hiring trends & location demand...")

monthly = (
    df.groupby(["PostingYearMonth","Title"])
    .agg(
        Listings=("JobID","count"),
        AvgSalary=("AnnualSalaryINR","mean"),
        ActiveListings=("IsActive","sum"),
    )
    .reset_index()
)
monthly.to_csv("data/hiring_trends_monthly.csv", index=False)

location = (
    df.groupby(["Location","Title"])
    .agg(
        Listings=("JobID","count"),
        AvgSalary=("AnnualSalaryINR","mean"),
        RemoteCount=("IsRemote","sum"),
    )
    .reset_index()
)
location.to_csv("data/location_demand.csv", index=False)

# Save clean master
df.to_csv("data/job_listings_clean.csv", index=False)

# ─────────────────────────────────────────────────────────────
# SUMMARY REPORT
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  ETL COMPLETE — Output Files")
print("=" * 60)
outputs = [
    ("job_listings_clean.csv",    f"{clean_count:,} rows — master clean dataset"),
    ("skills_frequency.csv",      f"{len(skill_freq)} skills ranked by demand"),
    ("salary_by_role.csv",        f"{len(salary_stats)} role×level salary stats"),
    ("skill_gap_analysis.csv",    f"{len(gap_df)} skills with gap scores"),
    ("role_skill_gap.csv",        f"{len(role_skill_gap)} roles with gap breakdown"),
    ("hiring_trends_monthly.csv", f"{len(monthly)} role×month trend records"),
    ("location_demand.csv",       f"{len(location)} location demand records"),
]
for fname, desc in outputs:
    size = os.path.getsize(f"data/{fname}") // 1024
    print(f"  📄 data/{fname:<35} {desc}  [{size} KB]")

print("\n  Ready for Tableau import ✓")

# ─────────────────────────────────────────────────────────────
# QUICK INSIGHTS PRINT
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  TOP-LINE INSIGHTS")
print("=" * 60)
print(f"\n  Most In-Demand Role    : {df['Title'].value_counts().idxmax()} ({df['Title'].value_counts().iloc[0]:,} listings)")
print(f"  Highest Avg Salary     : {df.groupby('Title')['AnnualSalaryINR'].mean().idxmax()} (₹{df.groupby('Title')['AnnualSalaryINR'].mean().max():,.0f})")
print(f"  Top Location           : {df['Location'].value_counts().idxmax()} ({df['Location'].value_counts().iloc[0]:,} listings)")
print(f"  Top Skill (Required)   : {skill_freq.iloc[0]['Skill']} ({skill_freq.iloc[0]['Frequency']:,} mentions)")
print(f"  Top Industry           : {df['Industry'].value_counts().idxmax()}")
print(f"  Remote Listings        : {df['IsRemote'].sum():,} ({df['IsRemote'].mean()*100:.1f}%)")
print(f"  Active Listings        : {df['IsActive'].sum():,} ({df['IsActive'].mean()*100:.1f}%)")
print()
