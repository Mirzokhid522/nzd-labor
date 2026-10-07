from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_unemployment_data():
    csv_path = os.path.join(os.path.dirname(__file__), 'unemployment.csv')
    
    if not os.path.exists(csv_path):
        return jsonify({"error": "unemployment.csv not found"}), 404

    try:
        records = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        # Locate data rows starting with year/quarter (e.g., "2024Q1", "2024Q2")
        for line in lines:
            parts = [p.strip().strip('"') for p in line.split(',')]
            if len(parts) > 0 and any(q in parts[0] for q in ['Q1', 'Q2', 'Q3', 'Q4']):
                period = parts[0]
                try:
                    # Filter for 2024 onwards to keep the macro charts sharp
                    year_val = int(period[:4])
                    if year_val >= 2024:
                        def safe_float(idx):
                            try:
                                val = parts[idx]
                                return float(val) if val not in ['', '..', 'NaN'] else None
                            except (IndexError, ValueError):
                                return None

                        records.append({
                            "period": period,
                            # Male metrics (Indices 5: Partic, 6: Unemp, 7: Employ)
                            "male_partic": safe_float(5),
                            "male_unemp": safe_float(6),
                            "male_employ": safe_float(7),
                            # Female metrics (Indices 13: Partic, 14: Unemp, 15: Employ)
                            "female_partic": safe_float(13),
                            "female_unemp": safe_float(14),
                            "female_employ": safe_float(15),
                            # Total metrics (Indices 21: Partic, 22: Unemp, 23: Employ)
                            "total_partic": safe_float(21),
                            "total_unemp": safe_float(22),
                            "total_employ": safe_float(23)
                        })
                except ValueError:
                    continue
                    
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)