import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from pdfminer.high_level import extract_text
import docx2txt
import re
import nltk
from PyPDF2 import PdfReader

class ResumeParserApp:
    def __init__(self, master):
        self.master = master
        master.title("Resume Parser App")
        master.geometry("700x800")
        master.configure(bg='#f0f0f0')


        self.style = ttk.Style()
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))


        self.main_frame = ttk.Frame(master, padding="20 20 20 20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Resume Parser App", 
            font=('Arial', 16, 'bold')
        )
        self.title_label.pack(pady=(0, 20))

        # File selection section
        self.file_frame = ttk.Frame(self.main_frame)
        self.file_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(
            self.file_frame, 
            textvariable=self.file_path_var, 
            width=50
        )
        self.file_path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        self.browse_button = ttk.Button(
            self.file_frame, 
            text="Browse", 
            command=self.browse_file
        )
        self.browse_button.pack(side=tk.RIGHT)

        # Skills search section
        self.skills_frame = ttk.Frame(self.main_frame)
        self.skills_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(self.skills_frame, text="Search Skills:").pack(side=tk.LEFT)
        self.skills_search_var = tk.StringVar()
        self.skills_search_entry = ttk.Entry(
            self.skills_frame, 
            textvariable=self.skills_search_var, 
            width=40
        )
        self.skills_search_entry.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)


        # Parse button
        self.parse_button = ttk.Button(
            self.main_frame, 
            text="Parse and Filter Resume", 
            command=self.parse_resume
        )
        self.parse_button.pack(pady=(20, 20))

        
        self.results_notebook = ttk.Notebook(self.main_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs
        self.phone_tab = self.create_tab(self.results_notebook, "Phone Numbers")
        self.email_tab = self.create_tab(self.results_notebook, "Emails")
        self.skills_tab = self.create_tab(self.results_notebook, "Skills")
        self.education_tab = self.create_tab(self.results_notebook, "Education") 
        self.summary_tab = self.create_tab(self.results_notebook, "Summary")

    def create_tab(self, notebook, title):
        """Create a scrollable text tab"""
        frame = ttk.Frame(notebook)
        text_widget = tk.Text(
            frame, 
            wrap=tk.WORD, 
            height=10, 
            font=('Courier', 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.config(state=tk.DISABLED)
        notebook.add(frame, text=title)
        return text_widget

    def browse_file(self):
        """Open file dialog to select resume"""
        filetypes = [
            ('PDF Files', '*.pdf'), 
            ('DOCX Files', '*.docx'), 
            ('All Files', '*.*')
        ]
        filename = filedialog.askopenfilename(
            title="Select Resume File", 
            filetypes=filetypes
        )
        if filename:
            self.file_path_var.set(filename)

    def parse_resume(self):
        """Parse the selected resume with filtering"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file first")
            return

        try:
            # Clear previous results
            for tab in [self.phone_tab, self.email_tab, self.skills_tab, self.education_tab, self.summary_tab]:
                tab.config(state=tk.NORMAL)
                tab.delete('1.0', tk.END)

            # Determine file type and parse
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.pdf':
                resume_text = extract_text(file_path)
            elif ext == '.docx':
                resume_text = docx2txt.process(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file type")
                return

            # Extract information
            phone_numbers = self.extract_phone_numbers(resume_text)
            emails = self.extract_emails(resume_text)
            skills = self.extractskill(resume_text)
            education = self.extract_education(resume_text)

            # Filter skills if search term provided
            search_skills = self.skills_search_var.get().lower().split(',')
            search_skills = [skill.strip() for skill in search_skills if skill.strip()]
            
            if search_skills:
                filtered_skills = set(
                    skill for skill in skills 
                    if any(search_skill in skill.lower() for search_skill in search_skills)
                )
            else:
                filtered_skills = skills

            # Display results
            self.display_results(
                phone_numbers, 
                emails, 
                filtered_skills,
                education,
                resume_text
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_results(self, phone_numbers, emails, skills, education, full_text):
        """Display extracted information in respective tabs"""
        # Phone Numbers
        if phone_numbers:
            self.phone_tab.config(state=tk.NORMAL)
            for number in phone_numbers:
                self.phone_tab.insert(tk.END, f"{number}\n")
            self.phone_tab.config(state=tk.DISABLED)
        
        # Emails
        if emails:
            self.email_tab.config(state=tk.NORMAL)
            for email in emails:
                self.email_tab.insert(tk.END, f"{email}\n")
            self.email_tab.config(state=tk.DISABLED)
        
        # Skills
        if skills:
            self.skills_tab.config(state=tk.NORMAL)
            for skill in skills:
                self.skills_tab.insert(tk.END, f"{skill}\n")
            self.skills_tab.config(state=tk.DISABLED)

        # Education
        if education:
            self.education_tab.config(state=tk.NORMAL)
            for edu in education:
                degree, inst = edu
                entry_text = f"{degree}\n"
                if inst:
                    entry_text += f"Institution: {inst}\n"
                self.education_tab.insert(tk.END, f"{entry_text}\n")
            self.education_tab.config(state=tk.DISABLED)

        # Summary Tab
        self.summary_tab.config(state=tk.NORMAL)
        summary = f"Total Phone Numbers: {len(phone_numbers)}\n"
        summary += f"Total Emails: {len(emails)}\n"
        summary += f"Total Skills Found: {len(skills)}\n"
        summary += f"Educational Qualifications: {len(education)}\n"
        summary += "Quick Preview of Resume Text:\n"
        summary += full_text[:500] + "..."
        self.summary_tab.insert(tk.END, summary)
        self.summary_tab.config(state=tk.DISABLED)

        # Summary Tab
        self.summary_tab.config(state=tk.NORMAL)
        summary = f"Total Phone Numbers: {len(phone_numbers)}\n"
        summary += f"Total Emails: {len(emails)}\n"
        summary += f"Total Skills Found: {len(skills)}\n"
        summary += "Quick Preview of Resume Text:\n"
        summary += full_text[:500] + "..."
        self.summary_tab.insert(tk.END, summary)
        self.summary_tab.config(state=tk.DISABLED)

    def extract_phone_numbers(self, resume_text):
        PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
        return re.findall(PHONE_REG, resume_text)

    def extract_emails(self, resume_text):
        EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
        return re.findall(EMAIL_REG, resume_text)
 
    SKILLS = [
        'BSc', 'teaching', 'maths', 'math', 'mathematics', 
        'english', 'language', 'MSc', 'BEd', 
        'python', 'java', 'c++', 'javascript', 
        'data analysis', 'machine learning', 
        'communication', 'leadership'
    ]

    def extractskill(self, text):
        stop_words = set(nltk.corpus.stopwords.words('english'))
        word_tokens = nltk.tokenize.word_tokenize(text)

        filtered_tokens = [w for w in word_tokens if w.isalpha()]
        bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))

        found_skills = set()

        for token in filtered_tokens:
            if token.lower() in self.SKILLS:
                found_skills.add(token)

        for ngram in bigrams_trigrams:
            if ngram.lower() in self.SKILLS:
                found_skills.add(ngram)
        return found_skills

    RESERVED_WORDS = [
        'college', 'university', 'school', 'education', 'degree',
        'bachelor', 'master', 'phd', 'bs', 'ba', 'ms', 'ma', 
        'high school', 'secondary school'
    ]

    def extract_education(self, text):
        """Extract educational qualifications from resume text"""
        education_info = []
    
        # Define education-related keywords
        degrees = [
            'bachelor', 'bachelors', 'b.a', 'b.s', 'b.sc', 'b.e', 'b.tech', 'b.ed', 'ba', 'bs', 'bsc', 'be', 'btech', 'bed',
            'master', 'masters', 'm.a', 'm.s', 'm.sc', 'm.e', 'm.tech', 'm.ed', 'ma', 'ms', 'msc', 'me', 'mtech', 'med',
            'mba', 'pgdm',
            'doctorate', 'ph.d', 'phd', 'doctor of philosophy',
            'associate', 'diploma', 'certification'
        ]
    
        institutions = ['university', 'college', 'institute', 'school', 'academy']
    
        # Split text into lines for processing
        lines = text.split('\n')
    
        # Check each line for education information
        for i, line in enumerate(lines):
            line_lower = line.lower()
        
            # Check if line contains degree information
            degree_match = None
            for degree in degrees:
                if degree in line_lower:
                    degree_match = degree
                    break
                
            if degree_match:
                # Look for institution in this line or nearby
                institution = None
                for inst in institutions:
                    if inst in line_lower:
                        # Extract full institution name if possible
                        inst_pattern = re.compile(r'([A-Z][A-Za-z\s]+(?:' + '|'.join(institutions) + '))', re.IGNORECASE)
                        inst_match = inst_pattern.search(line)
                        if inst_match:
                            institution = inst_match.group(1).strip()
                        break
            
                # Try to extract full degree name
                degree_pattern = re.compile(r'([A-Za-z\s\.]+(?:' + '|'.join(degrees) + ')[A-Za-z\s\.]*)', re.IGNORECASE)
                degree_full_match = degree_pattern.search(line)
            
                if degree_full_match:
                    degree_name = degree_full_match.group(1).strip()
                else:
                    degree_name = degree_match.capitalize()
            
                # Add to results if not duplicate
                education_info.append((degree_name, institution))
    
        return education_info
    
def main():
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('maxent_ne_chunker', quiet=True)
        nltk.download('words', quiet=True)
    except Exception as e:
        print(f"Error downloading NLTK data: {e}")

    root = tk.Tk()
    app = ResumeParserApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
