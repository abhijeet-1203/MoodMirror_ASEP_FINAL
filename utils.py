import pandas as pd
import os

DATA_PATH = "data/journal_entries.csv"

def load_entries():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=['Date', 'Entry', 'Sentiment', 'Score', 'Keywords'])

def save_entry(date, entry, sentiment, score, keywords):
    df = load_entries()
    new_entry = pd.DataFrame({
        'Date': [date],
        'Entry': [entry],
        'Sentiment': [sentiment],
        'Score': [score],
        'Keywords': [', '.join(keywords)]
    })
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_PATH, index=False) 
# pdf export
def export_to_pdf(df):
    """Export journal entries to PDF with emoji and bold support"""
    from fpdf import FPDF
    import pandas as pd
    import os

    pdf = FPDF()
    pdf.add_page()

    # Add both regular and bold fonts
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)

    # Title (bold)
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, "Your MoodMirror Journal Entries", 0, 1, 'C')
    pdf.ln(5)

    # ✅ Handle case when DataFrame is empty
    if df.empty:
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 10, "No journal entries available.", 0, 1)
    else:
        for _, row in df.iterrows():
            pdf.set_font('DejaVu', 'B', 10)
            pdf.cell(0, 6, f"Date: {row['Date']}", 0, 1)

            pdf.set_font('DejaVu', '', 10)
            mood = str(row['Sentiment'])
            score = f"{row['Score']:.2f}"
            entry_text = str(row['Entry']).replace('\n', ' ') if pd.notna(row['Entry']) else "No entry available"

            pdf.cell(0, 6, f"- Mood: {mood} (Score: {score})", 0, 1)
            pdf.multi_cell(0, 6, f"- Entry: {entry_text}")
            pdf.ln(4)

    return bytes(pdf.output(dest='S'))

