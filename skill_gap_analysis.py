"""
AI Job Market Analyzer — Skill Gap Analysis
Input:  data/job_listings_clean.csv
Output: Printed report + data/skill_gap_report.csv

Run AFTER etl_pipeline.py:
    python skill_gap_analysis.py
    python skill_gap_analysis.py --role "Data Analyst"
    python skill_gap_analysis.py --role "Data Scientist" --top 10
"""

import pandas as pd
import numpy as np
import argparse
import os

def load_data():
    df = pd.read_csv("data/job_listings_clean.csv")
    df["DatePosted"] = pd.to_datetime(df["DatePosted"], errors="coerce")
    return df

def explode_skills(df):
    rows = []
    for _, row in df.iterrows():
        for stype, col in [("Required","RequiredSkills"), ("Optional","OptionalSkills")]:
            for skill in str(row[col]).split("|"):
                skill = skill.strip()
                if skill:
                    rows.append({"Role": row["Title"], "Skill": skill, "Type": stype,
                                 "Location": row["Location"], "Salary": row["AnnualSalaryINR"]})
    return pd.DataFrame(rows)

def skill_gap_report(df_skills, role=None, top_n=15):
    if role:
        df_skills = df_skills[df_skills["Role"].str.lower() == role.lower()]
        if df_skills.empty:
            print(f"  No data found for role: '{role}'")
            return pd.DataFrame()

    req = df_skills[df_skills["Type"]=="Required"].groupby("Skill").size().reset_index(name="RequiredCount")
    opt = df_skills[df_skills["Type"]=="Optional"].groupby("Skill").size().reset_index(name="OptionalCount")
    merged = req.merge(opt, on="Skill", how="outer").fillna(0)
    merged["TotalMentions"] = merged["RequiredCount"] + merged["OptionalCount"]
    merged["RequiredPct"]   = (merged["RequiredCount"] / merged["TotalMentions"] * 100).round(1)
    merged["GapScore"]      = (merged["OptionalCount"] - merged["RequiredCount"]).clip(lower=0)

    # Demand tier
    merged["DemandTier"] = pd.cut(
        merged["RequiredCount"],
        bins=[-1, 50, 200, 500, 99999],
        labels=["Niche","Growing","High Demand","Critical"]
    )

    merged.sort_values("RequiredCount", ascending=False, inplace=True)
    return merged.head(top_n)

def print_report(df_skills, role=None, top_n=15):
    title = f"Role: {role}" if role else "All Roles Combined"
    print("\n" + "=" * 70)
    print(f"  SKILL GAP ANALYSIS — {title}")
    print("=" * 70)

    gap = skill_gap_report(df_skills, role=role, top_n=top_n)
    if gap.empty:
        return gap

    # Top required skills
    print(f"\n  📌 TOP {top_n} IN-DEMAND SKILLS (by Required Frequency)\n")
    print(f"  {'Rank':<5} {'Skill':<30} {'Required':>10} {'Optional':>10} {'Demand':>12}")
    print("  " + "-" * 67)
    for i, row in gap.iterrows():
        print(f"  {gap.index.get_loc(i)+1:<5} {row['Skill']:<30} {int(row['RequiredCount']):>10,} {int(row['OptionalCount']):>10,} {str(row['DemandTier']):>12}")

    # Emerging/gap skills
    gap_skills = gap[gap["GapScore"] > 0].sort_values("GapScore", ascending=False).head(5)
    if not gap_skills.empty:
        print(f"\n  🔼 TOP EMERGING SKILLS (high optional, rising to required)\n")
        for _, row in gap_skills.iterrows():
            print(f"  • {row['Skill']:<28}  Gap Score: {row['GapScore']:.0f}")

    # Critical must-haves
    critical = gap[gap["DemandTier"] == "Critical"]
    if not critical.empty:
        print(f"\n  🔴 CRITICAL SKILLS (appear in most listings)\n")
        for _, row in critical.iterrows():
            print(f"  • {row['Skill']:<28}  Required in {row['RequiredPct']:.0f}% of mentions")

    return gap

def salary_by_skill(df_skills_raw, df_clean, top_skills):
    """Average salary for listings that require each top skill"""
    results = []
    for skill in top_skills:
        mask = df_clean["RequiredSkills"].str.contains(skill, na=False, case=False)
        avg_sal = df_clean[mask]["AnnualSalaryINR"].mean()
        count   = mask.sum()
        results.append({"Skill": skill, "AvgSalary": round(avg_sal), "ListingCount": count})
    return pd.DataFrame(results).sort_values("AvgSalary", ascending=False)

def role_comparison(df_skills):
    """Side-by-side skill overlap across roles"""
    role_skills = df_skills[df_skills["Type"]=="Required"].groupby("Role")["Skill"].apply(set)
    roles = role_skills.index.tolist()
    print("\n" + "=" * 70)
    print("  CROSS-ROLE SKILL OVERLAP")
    print("=" * 70)
    print(f"\n  {'Role A':<28} {'Role B':<28} {'Shared Skills'}")
    print("  " + "-" * 70)
    pairs = [(roles[i], roles[j]) for i in range(len(roles)) for j in range(i+1, len(roles))]
    pairs_overlap = [(a, b, role_skills[a] & role_skills[b]) for a, b in pairs]
    pairs_overlap.sort(key=lambda x: len(x[2]), reverse=True)
    for a, b, shared in pairs_overlap[:10]:
        print(f"  {a:<28} {b:<28} {', '.join(list(shared)[:4])}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Skill Gap Analysis")
    parser.add_argument("--role", type=str, default=None, help="Filter by job role (e.g. 'Data Analyst')")
    parser.add_argument("--top",  type=int, default=15,   help="Number of top skills to show")
    args = parser.parse_args()

    df       = load_data()
    df_skills = explode_skills(df)

    # Full report
    gap = print_report(df_skills, role=args.role, top_n=args.top)

    # Salary-by-skill
    if not gap.empty:
        top_skill_names = gap["Skill"].tolist()[:10]
        sal = salary_by_skill(df_skills, df, top_skill_names)
        print("\n  💰 AVERAGE SALARY BY REQUIRED SKILL\n")
        print(f"  {'Skill':<30} {'Avg Salary (INR)':>18} {'# Listings':>12}")
        print("  " + "-" * 62)
        for _, row in sal.iterrows():
            print(f"  {row['Skill']:<30} ₹{int(row['AvgSalary']):>16,} {int(row['ListingCount']):>12,}")

    # Cross-role overlap (only when no role filter)
    if not args.role:
        role_comparison(df_skills)

    # Save
    if not gap.empty:
        out = f"data/skill_gap_{'_'.join(args.role.lower().split()) if args.role else 'all'}.csv"
        gap.to_csv(out, index=False)
        print(f"\n  ✓ Saved → {out}\n")
