import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import re
import os
from datetime import datetime
import json
from collections import Counter
import threading

class ResumeParser:
    def __init__(self):
        self.skills_patterns = {
            'programming': r'\b(?:python|java|javascript|c\+\+|c#|php|ruby|go|rust|swift|kotlin|scala|r|matlab|sql|html|css|react|angular|vue|node\.?js|django|flask|spring|laravel|rails|express)\b',
            'databases': r'\b(?:mysql|postgresql|mongodb|redis|sqlite|oracle|sql server|cassandra|dynamodb|elasticsearch)\b',
            'cloud': r'\b(?:aws|azure|gcp|google cloud|docker|kubernetes|jenkins|terraform|ansible|chef|puppet)\b',
            'frameworks': r'\b(?:tensorflow|pytorch|scikit-learn|pandas|numpy|matplotlib|seaborn|opencv|nltk|spacy|keras|hadoop|spark|kafka|airflow)\b',
            'tools': r'\b(?:git|github|gitlab|jira|confluence|slack|trello|figma|sketch|photoshop|illustrator|excel|powerpoint|tableau|power bi)\b',
            'soft_skills': r'\b(?:leadership|communication|teamwork|problem solving|analytical|creative|adaptable|organized|detail oriented|time management)\b'
        }
        
        self.education_patterns = {
            'degree': r'\b(?:bachelor|master|phd|doctorate|diploma|certificate|b\.?tech|m\.?tech|b\.?sc|m\.?sc|b\.?com|m\.?com|mba|bba)\b',
            'field': r'\b(?:computer science|information technology|software engineering|data science|artificial intelligence|machine learning|electrical|mechanical|civil|chemical|business|management|finance|marketing)\b'
        }
        
        self.experience_patterns = {
            'years': r'(\d+)[\+\-\s]*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            'positions': r'\b(?:software engineer|developer|programmer|analyst|manager|lead|senior|junior|intern|consultant|architect|designer|scientist|researcher)\b'
        }

    def extract_text_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    def extract_contact_info(self, text):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        phones = re.findall(phone_pattern, text)
        
        return {
            'emails': emails,
            'phones': phones
        }

    def extract_skills(self, text):
        text_lower = text.lower()
        all_skills = {}
        
        for category, pattern in self.skills_patterns.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            all_skills[category] = list(set(matches))
        
        return all_skills

    def extract_education(self, text):
        text_lower = text.lower()
        education = {}
        
        for category, pattern in self.education_patterns.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            education[category] = list(set(matches))
        
        return education

    def extract_experience(self, text):
        text_lower = text.lower()
        experience = {}
        
        years_match = re.search(self.experience_patterns['years'], text_lower, re.IGNORECASE)
        if years_match:
            experience['years'] = int(years_match.group(1))
        else:
            experience['years'] = 0
        
        positions = re.findall(self.experience_patterns['positions'], text_lower, re.IGNORECASE)
        experience['positions'] = list(set(positions))
        
        return experience

    def parse_resume(self, file_path):
        text = self.extract_text_from_file(file_path)
        
        parsed_data = {
            'file_name': os.path.basename(file_path),
            'contact_info': self.extract_contact_info(text),
            'skills': self.extract_skills(text),
            'education': self.extract_education(text),
            'experience': self.extract_experience(text),
            'raw_text': text[:500] + '...' if len(text) > 500 else text
        }
        
        return parsed_data

class JobMatcher:
    def __init__(self):
        self.job_database = self.load_sample_jobs()

    def load_sample_jobs(self):
        return [
            {
                'id': 1,
                'title': 'Senior Python Developer',
                'company': 'TechCorp Inc',
                'location': 'San Francisco, CA',
                'required_skills': ['python', 'django', 'postgresql', 'aws', 'git'],
                'preferred_skills': ['docker', 'kubernetes', 'redis', 'react'],
                'experience_required': 5,
                'education_required': ['bachelor', 'computer science'],
                'description': 'Looking for experienced Python developer to join our backend team.'
            },
            {
                'id': 2,
                'title': 'Data Scientist',
                'company': 'DataTech Solutions',
                'location': 'New York, NY',
                'required_skills': ['python', 'pandas', 'scikit-learn', 'sql', 'matplotlib'],
                'preferred_skills': ['tensorflow', 'pytorch', 'aws', 'tableau'],
                'experience_required': 3,
                'education_required': ['master', 'data science'],
                'description': 'Seeking data scientist for machine learning projects.'
            },
            {
                'id': 3,
                'title': 'Full Stack Developer',
                'company': 'WebSolutions Ltd',
                'location': 'Austin, TX',
                'required_skills': ['javascript', 'react', 'node.js', 'mongodb', 'html', 'css'],
                'preferred_skills': ['typescript', 'aws', 'docker', 'git'],
                'experience_required': 2,
                'education_required': ['bachelor', 'computer science'],
                'description': 'Full stack developer for modern web applications.'
            },
            {
                'id': 4,
                'title': 'Machine Learning Engineer',
                'company': 'AI Innovations',
                'location': 'Seattle, WA',
                'required_skills': ['python', 'tensorflow', 'pytorch', 'pandas', 'numpy'],
                'preferred_skills': ['kubernetes', 'mlflow', 'aws', 'spark'],
                'experience_required': 4,
                'education_required': ['master', 'artificial intelligence'],
                'description': 'ML engineer for production AI systems.'
            },
            {
                'id': 5,
                'title': 'Junior Software Developer',
                'company': 'StartupXYZ',
                'location': 'Remote',
                'required_skills': ['python', 'git', 'sql'],
                'preferred_skills': ['django', 'react', 'postgresql'],
                'experience_required': 1,
                'education_required': ['bachelor', 'computer science'],
                'description': 'Entry level position for new graduates.'
            }
        ]

    def calculate_skill_match(self, resume_skills, job_skills):
        resume_all_skills = []
        for category_skills in resume_skills.values():
            resume_all_skills.extend(category_skills)
        
        resume_skills_set = set(skill.lower() for skill in resume_all_skills)
        job_skills_set = set(skill.lower() for skill in job_skills)
        
        if not job_skills_set:
            return 0
        
        matched_skills = resume_skills_set.intersection(job_skills_set)
        return len(matched_skills) / len(job_skills_set) * 100

    def calculate_experience_match(self, resume_experience, required_experience):
        resume_years = resume_experience.get('years', 0)
        if resume_years >= required_experience:
            return 100
        elif resume_years == 0:
            return 0
        else:
            return (resume_years / required_experience) * 100

    def calculate_education_match(self, resume_education, required_education):
        resume_degrees = [deg.lower() for deg in resume_education.get('degree', [])]
        resume_fields = [field.lower() for field in resume_education.get('field', [])]
        
        required_degrees = [deg.lower() for deg in required_education if deg in ['bachelor', 'master', 'phd']]
        required_fields = [field.lower() for field in required_education if field not in ['bachelor', 'master', 'phd']]
        
        degree_match = any(deg in resume_degrees for deg in required_degrees) if required_degrees else True
        field_match = any(field in resume_fields for field in required_fields) if required_fields else True
        
        if degree_match and field_match:
            return 100
        elif degree_match or field_match:
            return 50
        else:
            return 0

    def match_jobs(self, parsed_resume):
        matches = []
        
        for job in self.job_database:
            required_skill_match = self.calculate_skill_match(
                parsed_resume['skills'], 
                job['required_skills']
            )
            
            preferred_skill_match = self.calculate_skill_match(
                parsed_resume['skills'], 
                job['preferred_skills']
            )
            
            experience_match = self.calculate_experience_match(
                parsed_resume['experience'], 
                job['experience_required']
            )
            
            education_match = self.calculate_education_match(
                parsed_resume['education'], 
                job['education_required']
            )
            
            overall_score = (
                required_skill_match * 0.4 +
                preferred_skill_match * 0.2 +
                experience_match * 0.3 +
                education_match * 0.1
            )
            
            match_data = {
                'job': job,
                'scores': {
                    'required_skills': round(required_skill_match, 2),
                    'preferred_skills': round(preferred_skill_match, 2),
                    'experience': round(experience_match, 2),
                    'education': round(education_match, 2),
                    'overall': round(overall_score, 2)
                }
            }
            
            matches.append(match_data)
        
        return sorted(matches, key=lambda x: x['scores']['overall'], reverse=True)

class ResumeParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Parser & Job Matcher - Anushka Jha")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        self.parser = ResumeParser()
        self.matcher = JobMatcher()
        self.current_resume_data = None
        
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        title_label = ttk.Label(main_frame, text="Resume Parser & Job Matcher", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(control_frame, text="Upload Resume", 
                  command=self.upload_resume).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(control_frame, text="Find Matching Jobs", 
                  command=self.find_matches, state='disabled').grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(control_frame, text="Export Results", 
                  command=self.export_results, state='disabled').grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(control_frame, text="Clear All", 
                  command=self.clear_all).grid(row=0, column=3)
        
        self.match_button = control_frame.winfo_children()[1]
        self.export_button = control_frame.winfo_children()[2]
        
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        self.setup_resume_panel(content_frame)
        self.setup_jobs_panel(content_frame)

    def setup_resume_panel(self, parent):
        resume_frame = ttk.LabelFrame(parent, text="Resume Analysis", padding="10")
        resume_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        resume_frame.columnconfigure(0, weight=1)
        resume_frame.rowconfigure(0, weight=1)
        
        self.resume_text = scrolledtext.ScrolledText(resume_frame, height=20, width=50)
        self.resume_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def setup_jobs_panel(self, parent):
        jobs_frame = ttk.LabelFrame(parent, text="Job Matches", padding="10")
        jobs_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        jobs_frame.columnconfigure(0, weight=1)
        jobs_frame.rowconfigure(0, weight=1)
        
        self.jobs_tree = ttk.Treeview(jobs_frame, columns=('Company', 'Location', 'Score'), show='tree headings')
        self.jobs_tree.heading('#0', text='Job Title')
        self.jobs_tree.heading('Company', text='Company')
        self.jobs_tree.heading('Location', text='Location')
        self.jobs_tree.heading('Score', text='Match %')
        
        self.jobs_tree.column('#0', width=200)
        self.jobs_tree.column('Company', width=150)
        self.jobs_tree.column('Location', width=120)
        self.jobs_tree.column('Score', width=80)
        
        scrollbar = ttk.Scrollbar(jobs_frame, orient=tk.VERTICAL, command=self.jobs_tree.yview)
        self.jobs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.jobs_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.jobs_tree.bind('<Double-1>', self.show_job_details)

    def upload_resume(self):
        file_path = filedialog.askopenfilename(
            title="Select Resume File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_resume_data = self.parser.parse_resume(file_path)
                self.display_resume_analysis()
                self.match_button.configure(state='normal')
                messagebox.showinfo("Success", "Resume uploaded and parsed successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse resume: {str(e)}")

    def display_resume_analysis(self):
        if not self.current_resume_data:
            return
        
        self.resume_text.delete(1.0, tk.END)
        
        analysis = f"FILE: {self.current_resume_data['file_name']}\n"
        analysis += "=" * 50 + "\n\n"
        
        contact = self.current_resume_data['contact_info']
        if contact['emails'] or contact['phones']:
            analysis += "CONTACT INFORMATION:\n"
            if contact['emails']:
                analysis += f"Emails: {', '.join(contact['emails'])}\n"
            if contact['phones']:
                analysis += f"Phones: {', '.join(contact['phones'])}\n"
            analysis += "\n"
        
        skills = self.current_resume_data['skills']
        analysis += "SKILLS FOUND:\n"
        for category, skill_list in skills.items():
            if skill_list:
                analysis += f"{category.title()}: {', '.join(skill_list)}\n"
        analysis += "\n"
        
        education = self.current_resume_data['education']
        if any(education.values()):
            analysis += "EDUCATION:\n"
            for category, items in education.items():
                if items:
                    analysis += f"{category.title()}: {', '.join(items)}\n"
            analysis += "\n"
        
        experience = self.current_resume_data['experience']
        analysis += "EXPERIENCE:\n"
        analysis += f"Years: {experience['years']}\n"
        if experience['positions']:
            analysis += f"Positions: {', '.join(experience['positions'])}\n"
        analysis += "\n"
        
        analysis += "RESUME PREVIEW:\n"
        analysis += "-" * 30 + "\n"
        analysis += self.current_resume_data['raw_text']
        
        self.resume_text.insert(1.0, analysis)

    def find_matches(self):
        if not self.current_resume_data:
            messagebox.showwarning("Warning", "Please upload a resume first!")
            return
        
        def process_matching():
            try:
                matches = self.matcher.match_jobs(self.current_resume_data)
                self.root.after(0, lambda: self.display_job_matches(matches))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Matching failed: {str(e)}"))
        
        threading.Thread(target=process_matching, daemon=True).start()
        messagebox.showinfo("Processing", "Finding job matches... Please wait.")

    def display_job_matches(self, matches):
        for item in self.jobs_tree.get_children():
            self.jobs_tree.delete(item)
        
        self.job_matches = matches
        
        for match in matches:
            job = match['job']
            score = match['scores']['overall']
            
            self.jobs_tree.insert('', 'end', 
                                text=job['title'],
                                values=(job['company'], job['location'], f"{score:.1f}%"))
        
        self.export_button.configure(state='normal')
        messagebox.showinfo("Complete", f"Found {len(matches)} job matches!")

    def show_job_details(self, event):
        selection = self.jobs_tree.selection()
        if not selection:
            return
        
        item = self.jobs_tree.item(selection[0])
        job_title = item['text']
        
        match = next((m for m in self.job_matches if m['job']['title'] == job_title), None)
        if not match:
            return
        
        job = match['job']
        scores = match['scores']
        
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Job Details - {job['title']}")
        details_window.geometry("600x500")
        details_window.configure(bg='#f0f0f0')
        
        frame = ttk.Frame(details_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        details_text = scrolledtext.ScrolledText(frame, height=25, width=70)
        details_text.pack(fill=tk.BOTH, expand=True)
        
        details = f"{job['title']}\n"
        details += f"{job['company']} - {job['location']}\n"
        details += "=" * 50 + "\n\n"
        
        details += "MATCH SCORES:\n"
        details += f"Overall Match: {scores['overall']:.1f}%\n"
        details += f"Required Skills: {scores['required_skills']:.1f}%\n"
        details += f"Preferred Skills: {scores['preferred_skills']:.1f}%\n"
        details += f"Experience: {scores['experience']:.1f}%\n"
        details += f"Education: {scores['education']:.1f}%\n\n"
        
        details += "JOB REQUIREMENTS:\n"
        details += f"Required Skills: {', '.join(job['required_skills'])}\n"
        details += f"Preferred Skills: {', '.join(job['preferred_skills'])}\n"
        details += f"Experience Required: {job['experience_required']} years\n"
        details += f"Education Required: {', '.join(job['education_required'])}\n\n"
        
        details += "DESCRIPTION:\n"
        details += job['description']
        
        details_text.insert(1.0, details)
        details_text.configure(state='disabled')

    def export_results(self):
        if not hasattr(self, 'job_matches'):
            messagebox.showwarning("Warning", "No job matches to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.export_to_csv(file_path)
                else:
                    self.export_to_json(file_path)
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

    def export_to_json(self, file_path):
        export_data = {
            'resume_analysis': self.current_resume_data,
            'job_matches': self.job_matches,
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def export_to_csv(self, file_path):
        rows = []
        for match in self.job_matches:
            job = match['job']
            scores = match['scores']
            rows.append({
                'Job Title': job['title'],
                'Company': job['company'],
                'Location': job['location'],
                'Overall Score': scores['overall'],
                'Required Skills Score': scores['required_skills'],
                'Preferred Skills Score': scores['preferred_skills'],
                'Experience Score': scores['experience'],
                'Education Score': scores['education'],
                'Required Skills': ', '.join(job['required_skills']),
                'Preferred Skills': ', '.join(job['preferred_skills']),
                'Experience Required': job['experience_required'],
                'Education Required': ', '.join(job['education_required'])
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(file_path, index=False)

    def clear_all(self):
        self.current_resume_data = None
        self.resume_text.delete(1.0, tk.END)
        
        for item in self.jobs_tree.get_children():
            self.jobs_tree.delete(item)
        
        self.match_button.configure(state='disabled')
        self.export_button.configure(state='disabled')
        
        if hasattr(self, 'job_matches'):
            delattr(self, 'job_matches')

def main():
    root = tk.Tk()
    app = ResumeParserGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()