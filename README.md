# Resume Parser and Job Matcher

A Python-based tool for parsing resumes and matching candidate skills with job requirements using regex patterns and keyword extraction.

## Features

- Resume text parsing and skill extraction
- Contact information detection
- Education and experience analysis
- Job matching algorithm with scoring
- GUI interface built with Tkinter
- Export results to JSON/CSV formats

## Tech Stack

- **Python** - Core programming language
- **Pandas** - Data manipulation and CSV export
- **Regex** - Pattern matching for skill extraction
- **Tkinter** - GUI framework

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Upload a resume file (text format)
3. Click "Find Matching Jobs" to analyze
4. View detailed job matches and scores
5. Export results if needed

## Algorithm

The matching algorithm evaluates:
- Required skills match (40% weight)
- Preferred skills match (20% weight)  
- Experience level (30% weight)
- Education requirements (10% weight)
