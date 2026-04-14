# AI Job Market Analyzer — Tableau Dashboard Procedure

## Prerequisites
- Tableau Desktop or Tableau Public (free) — tableau.com/products/public
- Python 3.8+ with pandas, numpy
- All scripts from this repo

---

## STEP 1 — Generate & Process Data

```bash
pip install pandas numpy
python generate_data.py        # → data/job_listings_raw.csv
python etl_pipeline.py         # → 7 clean output CSVs
python skill_gap_analysis.py   # → printed report + data/skill_gap_all.csv
```

---

## STEP 2 — Connect Data Sources in Tableau

Open Tableau → **Connect → Text File**. Load each file:

| File | Purpose |
|---|---|
| `job_listings_clean.csv` | Primary fact table |
| `skills_frequency.csv` | Skills dimension |
| `salary_by_role.csv` | Pre-aggregated salary stats |
| `hiring_trends_monthly.csv` | Time series |
| `location_demand.csv` | Geographic dimension |
| `skill_gap_analysis.csv` | Skill gap scores |

### Relationships (Data Source tab)
- `hiring_trends_monthly` → join on `Title` to `job_listings_clean`
- `location_demand` → join on `Location` + `Title`
- `skill_gap_analysis` → standalone (used in its own sheet)

---

## STEP 3 — Calculated Fields

Create these calculated fields in Tableau (**Analysis → Create Calculated Field**):

```
// Salary in Lakhs (more readable)
Salary (Lakhs)
[AnnualSalaryINR] / 100000

// Active Listing Flag
Is Active Label
IF [IsActive] = 1 THEN "Active" ELSE "Closed" END

// Remote Label
Work Mode
IF [IsRemote] = 1 THEN "Remote" ELSE "On-Site" END

// Experience Mid Point
Exp Midpoint
([ExperienceYearsMin] + [ExperienceYearsMax]) / 2

// Posting Recency bucket
Recency
IF [DaysOld] <= 7   THEN "Last 7 Days"
ELSEIF [DaysOld] <= 30  THEN "Last 30 Days"
ELSEIF [DaysOld] <= 90  THEN "Last 90 Days"
ELSE "Older"
END
```

---

## STEP 4 — Dashboard Pages (5 sheets + 1 dashboard each)

---

### SHEET 1 — Market Overview (Executive Summary)

**KPI Banners** (use Text marks, no axis):
| Metric | Formula |
|---|---|
| Total Listings | COUNT([JobID]) |
| Active Listings | SUM([IsActive]) |
| Avg Salary | AVG([AnnualSalaryINR]) |
| Unique Companies | COUNTD([Company]) |
| Remote % | SUM([IsRemote]) / COUNT([JobID]) |

**Visual 1 — Listings by Role (Horizontal Bar)**
- Rows: Title
- Columns: COUNT(JobID)
- Color: ExperienceLevel
- Sort: Descending by count

**Visual 2 — Monthly Hiring Trend (Line Chart)**
- Columns: PostingYearMonth (discrete)
- Rows: COUNT(JobID)
- Color: Title (filter to top 5 roles)

**Visual 3 — Industry Distribution (Treemap)**
- Color + Size: COUNT(JobID)
- Label: Industry
- Detail: AVG(Salary Lakhs)

**Filters to add:** DatePosted range, ExperienceLevel, IsActive

---

### SHEET 2 — Skills Intelligence

**Visual 1 — Top 30 Skills Bar Chart**
- Data source: `skills_frequency.csv`
- Rows: Skill (top 30 by Frequency)
- Columns: Frequency
- Color: Category
- Sort: Descending

**Visual 2 — Skills Heatmap by Role**
- Rows: Skill (top 20)
- Columns: Role
- Color: COUNT — use `job_listings_clean.csv`, filter RequiredSkills contains [Skill]
  
  *Tableau tip: Use a cross-join or data blend. Simplest approach:*
  - Use `skills_frequency.csv` directly
  - Rows: Skill, Columns: Role, Color: Frequency

**Visual 3 — Skill Category Donut**
- Rows/Cols: 0, 0 (manual donut setup)
- Angle: COUNT(Skill)
- Color: Category
- Label: Category + Frequency

**Visual 4 — Skill Demand Tier Bubble Chart**
- Columns: FrequencyPct
- Rows: GapScore
- Size: Frequency
- Color: DemandTier
- Label: Skill

---

### SHEET 3 — Salary Analysis

**Visual 1 — Salary Box Plot by Role**
- Columns: Title
- Rows: AnnualSalaryINR
- Mark type: Circle
- Add reference line: Median

**Visual 2 — Salary Heatmap (Role × Experience)**
- Data: `salary_by_role.csv`
- Rows: Title
- Columns: ExperienceLevel
- Color: MedianSalary (continuous, green scale)
- Label: MedianSalary (formatted as ₹##,##L)

**Visual 3 — Salary Band Distribution**
- Rows: SalaryBand
- Columns: COUNT(JobID)
- Color: Title

**Visual 4 — Salary vs Experience Scatter**
- Columns: Exp Midpoint (calculated field)
- Rows: Salary (Lakhs)
- Color: Title
- Size: COUNT(JobID)

---

### SHEET 4 — Geographic Demand

**Visual 1 — Map (Symbol Map)**
- Marks: Circle
- Size + Color: COUNT(JobID)
- Tooltip: Location, Count, AvgSalary, Top Role
- Assign geo roles to Location column (City → State if needed)

*Note: Tableau may not geocode all Indian cities. Manual lat/long option:*

| City | Latitude | Longitude |
|---|---|---|
| Bangalore | 12.9716 | 77.5946 |
| Hyderabad | 17.3850 | 78.4867 |
| Mumbai | 19.0760 | 72.8777 |
| Delhi NCR | 28.7041 | 77.1025 |
| Pune | 18.5204 | 73.8567 |
| Chennai | 13.0827 | 80.2707 |
| Kolkata | 22.5726 | 88.3639 |

Add a custom geocoding CSV with these values if needed.

**Visual 2 — Location vs Role Heatmap**
- Rows: Location
- Columns: Title
- Color: COUNT(JobID)

**Visual 3 — Remote vs On-Site Bar**
- Rows: Work Mode
- Columns: COUNT(JobID)
- Color: Title

---

### SHEET 5 — Skill Gap & Career Intelligence

**Data source: `skill_gap_analysis.csv`**

**Visual 1 — Skill Gap Quadrant**
- Columns: RequiredCount
- Rows: GapScore
- Size: TotalMentions
- Color: DemandTier
- Label: Skill
- Add reference lines at median X and median Y → creates 4 quadrants:
  - High Required + Low Gap = Core skills (must have)
  - Low Required + High Gap = Emerging skills (invest now)
  - High Required + High Gap = Transition skills
  - Low Required + Low Gap = Niche skills

**Visual 2 — Top Gap Skills Bar**
- Rows: Skill (top 15 by GapScore)
- Columns: GapScore
- Color: DemandTier

**Visual 3 — Role Skill Count Comparison**
- Data: `role_skill_gap.csv`
- Rows: Role
- Columns: RequiredSkillCount + GapSkillCount (dual axis)

---

## STEP 5 — Build Dashboards

### Dashboard 1 — Market Overview
Size: 1400×900px. Layout:
```
┌─────────────────────────────────────────────────┐
│  KPI Banner (Total, Active, Avg Salary, Remote)  │
├──────────────────────────┬──────────────────────┤
│  Listings by Role (bar)  │  Industry Treemap     │
├──────────────────────────┴──────────────────────┤
│            Monthly Hiring Trend (line)           │
├──────────────────────────────────────────────────┤
│  Filters: Date | Experience Level | Job Type     │
└──────────────────────────────────────────────────┘
```

### Dashboard 2 — Skills Intelligence
```
┌────────────────┬────────────────────────────────┐
│  Top 30 Skills │  Skill Demand Bubble Chart      │
│  (bar)         │                                 │
├────────────────┴────────────────────────────────┤
│         Skills Heatmap (Role × Skill)            │
├─────────────────────────────────────────────────┤
│  Skill Category Donut  │  Filters: Role, Tier   │
└─────────────────────────────────────────────────┘
```

### Dashboard 3 — Salary Analysis
```
┌──────────────────────────────────────────────────┐
│  Salary Heatmap (Role × Experience Level)         │
├───────────────────┬──────────────────────────────┤
│  Box Plot (Role)  │  Salary Band Distribution    │
├───────────────────┴──────────────────────────────┤
│         Salary vs Experience Scatter              │
└──────────────────────────────────────────────────┘
```

### Dashboard 4 — Geographic Demand
```
┌──────────────────────────────────────────────────┐
│              Map (Symbol Map)                     │
├───────────────────┬──────────────────────────────┤
│  Location Heatmap │  Remote vs On-Site Bar       │
└───────────────────┴──────────────────────────────┘
```

### Dashboard 5 — Skill Gap Intelligence
```
┌──────────────────────────────────────────────────┐
│         Skill Gap Quadrant (scatter)              │
├────────────────────┬─────────────────────────────┤
│  Top Gap Skills    │  Role Skill Count Comparison │
└────────────────────┴─────────────────────────────┘
```

---

## STEP 6 — Formatting

### Color Palette (set in Tableau Preferences)
```
Primary:   #1a3a5c  (dark navy)
Accent:    #2d9cdb  (blue)
Positive:  #27ae60  (green)
Warning:   #f2994a  (orange)
Negative:  #eb5757  (red)
Neutral:   #bdbdbd  (gray)
```

### Checklist
- [ ] All salary values formatted as ₹##,##,### or ##.#L
- [ ] Consistent font: Tableau Book / Gill Sans
- [ ] Dashboard background: #f4f6f9
- [ ] Add navigation buttons across dashboards (Dashboard → Objects → Button)
- [ ] Add title and subtitle to every sheet
- [ ] Tooltips customized (add avg salary, top skills to every tooltip)
- [ ] Add "Last Updated" parameter text box

---

## STEP 7 — Publish

**Tableau Public (free):**
1. File → Save to Tableau Public
2. Sign in with free account
3. Set visibility → Public
4. Copy embed URL for portfolio

**For portfolio:**
- Screenshot each dashboard
- Record 2-min walkthrough using Loom
- Add Tableau Public link to resume and GitHub

---

## STEP 8 — CLI Usage Reference

```bash
# Generate fresh data
python generate_data.py

# Run full ETL
python etl_pipeline.py

# Skill gap — all roles
python skill_gap_analysis.py

# Skill gap — specific role
python skill_gap_analysis.py --role "Data Analyst"
python skill_gap_analysis.py --role "Machine Learning Engineer" --top 10
python skill_gap_analysis.py --role "AI Engineer"
```

---

## Folder Structure
```
ai-job-market-analyzer/
├── generate_data.py
├── etl_pipeline.py
├── skill_gap_analysis.py
├── tableau_procedure.md         ← this file
├── README.md
├── data/
│   ├── job_listings_raw.csv
│   ├── job_listings_clean.csv
│   ├── skills_frequency.csv
│   ├── salary_by_role.csv
│   ├── skill_gap_analysis.csv
│   ├── role_skill_gap.csv
│   ├── hiring_trends_monthly.csv
│   └── location_demand.csv
└── dashboard/
    └── AI_Job_Market_Analyzer.twbx   ← your saved Tableau file
```
