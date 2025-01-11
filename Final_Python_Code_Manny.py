#This project was created by E_Stew at Jan 11, 2025.

import tkinter as tk
from tkinter import messagebox, ttk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import tempfile
import webbrowser
import re

class NavySWOTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚓ US Navy Personal & Professional SWOT Analysis ⚓")
        self.root.geometry("900x1200")
        self.root.configure(bg="white")

        self.canvas = tk.Canvas(root, bg="white")
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        tk.Label(self.scrollable_frame, text="US Navy Personal & Professional SWOT Analysis",
                 font=("Helvetica", 24, "bold"), bg="white", fg="navy").pack(pady=20)

        instructions = (
            "Purpose: The SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis helps Sailors assess their "
            "personal and professional development. This tool aligns with the Navy's 'Get Real Get Better' initiative, "
            "promoting self-awareness, accountability, and professional growth.\nInstructions:\n"
            "1. Be honest and thoughtful while answering the questions.\n"
            "2. Reflect on your personal strengths, areas for improvement, and growth opportunities.\n"
            "3. Use this analysis as a foundation for mentorship discussions and goal-setting."
        )
        tk.Label(self.scrollable_frame, text=instructions, font=("Helvetica", 12), bg="white", wraplength=850).pack(pady=10, padx=20)

        self.info_frame = tk.Frame(self.scrollable_frame, bg="white")
        self.info_frame.pack(pady=10, padx=20, fill="x")
        #Personal Information
        self.add_label_and_entry("Sailor's Last Name", "last_name_entry", 0)
        self.add_label_and_entry("Sailor's First Name", "first_name_entry", 1)
        self.add_label_and_entry("Sailor's Middle Initial", "middle_initial_entry", 2)
        #Rank
        tk.Label(self.info_frame, text="Rank:", bg="white").grid(row=3, column=0, sticky="e")
        self.rank_var = tk.StringVar()
        self.rank_menu = ttk.Combobox(self.info_frame, textvariable=self.rank_var, state="readonly",
                                      values=["E-1", "E-2", "E-3", "E-4", "E-5", "E-6", "E-7", "E-8", "E-9", "O-1",
                                              "O-2", "O-3", "O-4", "O-5", "O-6", "O-7", "O-8", "O-9", "O-10"])
        self.rank_menu.grid(row=3, column=1)
        self.rank_menu.bind("<<ComboboxSelected>>", self.update_rate_options)
        #rate
        tk.Label(self.info_frame, text="Rate:", bg="white").grid(row=4, column=0, sticky="e")
        self.rate_var = tk.StringVar()
        self.rate_menu = ttk.Combobox(self.info_frame, textvariable=self.rate_var, state="readonly",
                                      values=["ABH", "ABF", "ABE", "AC", "AD", "AE", "AG", "AM", "AO", "AS", "AT", "AW",
                                              "AZ", "BM", "BU", "CE", "CM", "CS", "CTI", "CTM", "CTN", "CTR", "CTT",
                                              "DC", "EA", "EM", "EN", "EO", "ET", "FC", "FT", "GM", "GSE", "GSM", "HM",
                                              "HT", "IC", "IS", "IT", "LN", "LS", "MA", "MC", "MM", "MR", "MT", "MU",
                                              "NC", "ND", "OS", "PR", "PS", "QM", "RP", "SB", "SH", "SO", "STG", "STS",
                                              "SW", "TM", "UT", "YN"])
        self.rate_menu.grid(row=4, column=1)

        self.add_label_and_entry("Supervisor's Name", "supervisor_name_entry", 5)

        self.swot_frame = tk.Frame(self.scrollable_frame, bg="white")
        self.swot_frame.pack(pady=10, padx=20, fill="x")

        self.create_question_area("🌟 What are your core strengths in your current role?", "Strengths", 500)
        self.create_question_area("📈 What areas need improvement for your professional growth?", "Weaknesses", 500)
        self.create_question_area("🎯 What opportunities exist for career advancement or skill improvement?", "Opportunities", 500)
        self.create_question_area("⚠️ What external challenges could impact your professional growth?", "Threats", 500)
        self.create_question_area("🪞 Reflect on how you plan to use your strengths to overcome threats:", "Self_Reflection", 500)

        # Preview Button
        self.export_button = tk.Button(root, text="Preview PDF", command=self.preview_pdf, bg="navy", fg="black",font=("Helvetica", 12, "bold"))
        self.export_button.pack(pady=20)

    def add_label_and_entry(self, label_text, attr_name, row):
        tk.Label(self.info_frame, text=label_text, bg="white").grid(row=row, column=0, sticky="e")
        entry = tk.Entry(self.info_frame)
        entry.grid(row=row, column=1)
        setattr(self, attr_name, entry)

    def create_question_area(self, question_text, label_text, char_limit):
        frame = tk.Frame(self.swot_frame, bg="white")
        frame.pack(pady=5, padx=5, fill="x")
        tk.Label(frame, text=question_text, bg="white", font=("Helvetica", 14, "bold")).pack(anchor="w")
        text_area = tk.Text(frame, height=6, width=70, wrap="word", font=("Helvetica", 12))
        text_area.pack()
        char_count_label = tk.Label(frame, text=f"0/{char_limit} characters", bg="white")
        char_count_label.pack(anchor="w")

        text_area.bind("<KeyRelease>", lambda event: self.limit_text_length(text_area, char_limit, char_count_label))
        setattr(self, f"{label_text.lower()}_entry", text_area)

    def limit_text_length(self, text_area, char_limit, char_count_label):
        content = text_area.get("1.0", "end-1c")
        word_count = len(content.split())
        char_count_label.config(text=f"{len(content)}/{char_limit} characters, {word_count} words")

        # Check and truncate if character count exceeds the limit
        if len(content) > char_limit:
            text_area.delete("1.0", tk.END)
            text_area.insert("1.0", content[:char_limit])

    def validate_input(self, text):
        if not re.match(r'^[A-Za-z0-9 .,-]+$', text):
            raise ValueError("Invalid characters detected in input fields.")

    def update_rate_options(self, event):
        selected_rank = self.rank_var.get()
        if selected_rank.startswith("O-"):
            self.rate_menu.config(values=["N/A"])
            self.rate_var.set("N/A")
        else:
            self.rate_menu.config(values=["ABH", "ABF", "ABE", "AC", "AD", "AE", "AG", "AM", "AO", "AS",
            "AT", "AW", "AZ", "BM", "BU", "CE", "CM", "CS", "CTI", "CTM",
            "CTN", "CTR", "CTT", "DC", "EA", "EM", "EN", "EO", "ET",
            "FC", "FT", "GM", "GSE", "GSM", "HM", "HT", "IC", "IS", "IT",
            "LN", "LS", "MA", "MC", "MM", "MR", "MT", "MU", "NC", "ND",
            "OS", "PR", "PS", "QM", "RP", "SB", "SH", "SO", "STG", "STS",
            "SW", "TM", "UT", "YN"])
            self.rate_var.set("")

    def preview_pdf(self):
        try:
            # Fetching inputs
            last_name = self.last_name_entry.get().strip().capitalize()
            first_name = self.first_name_entry.get().strip().capitalize()
            middle_initial = self.middle_initial_entry.get().strip().capitalize()
            rank = self.rank_var.get()
            rate = self.rate_var.get()
            supervisor_name = self.supervisor_name_entry.get()

            self.validate_input(last_name)
            self.validate_input(first_name)
            self.validate_input(middle_initial)
            self.validate_input(supervisor_name)

            # Fetching SWOT responses
            strengths = self.strengths_entry.get("1.0", tk.END).strip()
            weaknesses = self.weaknesses_entry.get("1.0", tk.END).strip()
            opportunities = self.opportunities_entry.get("1.0", tk.END).strip()
            threats = self.threats_entry.get("1.0", tk.END).strip()
            self_reflection = self.self_reflection_entry.get("1.0", tk.END).strip()

            # Validate inputs
            if not all([last_name, first_name, middle_initial, rank, rate, strengths, weaknesses, opportunities,
                        threats, self_reflection]):
                messagebox.showerror("Error", "Please fill out all fields before exporting.")
                return

            # Generate PDF with adjusted margins
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            c = canvas.Canvas(temp_file.name, pagesize=letter)
            #Top Margin
            margin = inch
            width, height = letter
            usable_width = width - 2 * margin
            usable_height = height - 2 * margin
            y_position = height - margin

            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(letter[0] / 2, y_position, "US Navy Professional Development SWOT Analysis")
            y_position -= inch / 2
            c.setFont("Helvetica", 12)
            name_and_date = f"Name: {last_name}, {first_name} {middle_initial}." + " " * 80 + f"Date: {datetime.now().strftime('%m-%d-%Y')}"
            c.drawString(margin, y_position, name_and_date)
            y_position -= 20
            c.drawString(margin, y_position, f"Rank: {rank}")  # Fixed here from rank to paygrade
            y_position -= 20
            c.drawString(margin, y_position, f"Rate: {rate}")
            y_position -= 30

            def check_page_overflow(c, y_position):
                if y_position < margin:
                    c.showPage()
                    y_position = height - margin
                    c.setFont("Helvetica", 12)
                return y_position

            # Add SWOT content
            for title, content in [
                ("Strengths", strengths),
                ("Weaknesses", weaknesses),
                ("Opportunities", opportunities),
                ("Threats", threats),
                ("Self-Reflection", self_reflection)
            ]:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(margin, y_position, f"{title}:")
                y_position -= 15
                c.setFont("Helvetica", 10)
                for line in self.wrap_text(content, width=90):
                    y_position -= 12
                    c.drawString(margin, y_position, line)
                    y_position = check_page_overflow(c, y_position)
                y_position -= 20

            # Add Signature Block
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margin, y_position - 20, "Sailor Signature: ______________________")
            c.drawString(margin + 300, y_position - 20, "Date: _________________")
            c.drawString(margin, y_position - 50, f"Supervisor Name: {supervisor_name}")
            c.drawString(margin+ 275, y_position - 50, "Supervisor Signature: ______________________")
            c.save()

            webbrowser.open(f'file://{temp_file.name}')
        except ValueError as e:
            messagebox.showerror ("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    def wrap_text(self, text, width):
        """Wrap text to fit within a specified width for PDF generation."""
        import textwrap
        return textwrap.wrap(text, width)
root = tk.Tk()
app = NavySWOTApp(root)
root.mainloop()
