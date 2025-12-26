import re
import json
import argparse

class FoodParser:
    def __init__(self):
        # Common food keywords found in the synthetic dataset
        self.food_items = ["poha", "khichdi", "biryani", "apple", "coffee", "dal chawal", "salad", "chicken wrap", "yogurt", "berries", "dosa", "chutney", "tea"]
        self.meal_types = ["breakfast", "lunch", "dinner", "snack"]

    def parse(self, text):
        extracted = []
        text_lower = text.lower()
        for food in self.food_items:
            if food in text_lower:
                # Basic quantity/unit extraction logic (e.g., "1 protein shake", "2 cookies")
                qty_match = re.search(r'(\d+)\s+' + food, text_lower)
                quantity = qty_match.group(1) if qty_match else "1"
                
                # Infer meal type if mentioned
                meal = next((m for m in self.meal_types if m in text_lower), "unspecified")
                
                extracted.append({
                    "name": food,
                    "quantity": quantity,
                    "unit": "portion" if not qty_match else "count",
                    "meal": meal
                })
        return extracted

class SymptomParser:
    def __init__(self):
        self.symptom_keywords = ["cramps", "headache", "bloating", "nausea", "anxiety", "migraine", "dizziness", "fatigue", "sore throat"]

    def parse(self, text):
        extracted = []
        text_lower = text.lower()
        for sym in self.symptom_keywords:
            if sym in text_lower:
                # Check for negation (e.g., "no bloating", "no gas")
                negation = False
                if re.search(r'\b(no|nahi|not|none)\b\s+' + sym, text_lower):
                    negation = True
                
                # Extract severity if present (e.g., "8/10")
                severity_match = re.search(r'(\d/10)', text_lower)
                severity = severity_match.group(1) if severity_match else "not specified"

                extracted.append({
                    "name": sym,
                    "severity": severity,
                    "negation": negation,
                    "time_hint": "unspecified" # Heuristics for 'morning'/'night' could be added here
                })
        return extracted

class LightParsePipeline:
    def __init__(self):
        self.food_parser = FoodParser()
        self.symptom_parser = SymptomParser()

    def run(self, entry):
        text = entry.get("text", "")
        return {
            "entry_id": entry.get("entry_id"),
            "foods": self.food_parser.parse(text),
            "symptoms": self.symptom_parser.parse(text)
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_file", required=True)
    parser.add_argument("--out_file", required=True)
    args = parser.parse_args()

    pipeline = LightParsePipeline()

    with open(args.in_file, 'r', encoding='utf-8') as f_in, \
         open(args.out_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            data = json.loads(line)
            result = pipeline.run(data)
            f_out.write(json.dumps(result) + "\n")

if __name__ == "__main__":
    main()
