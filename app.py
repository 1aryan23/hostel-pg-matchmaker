from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Load and clean the CSV file
df = pd.read_csv('data/DATA.csv')

# Remove hidden/invisible characters from column names
df.columns = df.columns.str.replace(r'[\u200e\u200f\u202c]', '', regex=True).str.strip()
df['Contact Number(Whatsapp)'] = df['Contact Number(Whatsapp)'].astype(str).str.strip()

# Function to combine and clean interests
def extract_interests(row):
    interests = str(row['HOBBIES OR INTERESTS']) + ', ' + str(row['ANY OTHER SPECIFIC HOBBIES OR INTERESTS'])
    return set(map(str.strip, interests.lower().split(',')))

# Function to combine and clean top 5 priorities
def extract_priorities(row):
    priorities = []
    for i in range(1, 6):
        col = f'Priority Order/Deal breaker for roomie (Top 5 will be considered) [Priority {i}]'
        priorities.append(str(row.get(col, '')).strip().lower())
    return set(priorities)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/match', methods=['POST'])
def match():
    phone = request.form['phone'].strip()
    phone = str(phone)

    user = df[df['Contact Number(Whatsapp)'] == phone]
    if user.empty:
        return "Phone number not found."

    user_row = user.iloc[0]
    user_pref = str(user_row['PG OR HOSTEL (GHS)']).strip().lower()
    user_interests = extract_interests(user_row)
    user_priorities = extract_priorities(user_row)

    scores = []
    for _, row in df.iterrows():
        if str(row['Contact Number(Whatsapp)']) == phone:
            continue
        if str(row['PG OR HOSTEL (GHS)']).strip().lower() != user_pref:
            continue

        interests = extract_interests(row)
        priorities = extract_priorities(row)
        score = len(user_interests & interests) + len(user_priorities & priorities)

        scores.append({
            'Full Name': row['Full Name'],
            'Contact Number(Whatsapp)': row['Contact Number(Whatsapp)'],
            'Shared Interests': ', '.join(user_interests & interests),
            'score': score
        })

    top_matches = sorted(scores, key=lambda x: x['score'], reverse=True)[:2]
    return render_template('result.html', matches=top_matches)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)


