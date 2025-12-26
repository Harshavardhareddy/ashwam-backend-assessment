# Ashwam Backend Engineering Assessment

This repository contains my completed technical assessment for the Backend Engineering Intern position at Ashwam. The solution provides a suite of deterministic, privacy-first tools designed specifically to process sensitive health journaling data.

## 📂 Project Structure

- pii_scrubber.py: Deterministic PII removal with clinical context preservation.
- lang_detect.py: Hybrid script and lexicon-based language detection.
- light_parse.py: Rule-based extraction of symptoms and food items.

---

## 🛠 Technical Approach & Logic

### Exercise A: PII Scrubber
My strategy uses a Longest-Match-First resolution engine. The script identifies all potential matches across various categories like Email, Phone, and Healthcare Providers, then sorts them by character length. 

For conflict resolution, if patterns overlap—for instance, a Clinic Name that happens to contain a Street Name—the system commits to the longest span and discards any sub-matches. This prevents the "partial scrubbing" that often occurs with naive regex implementations. To maintain clinical integrity, I utilized word boundaries and specific anchors to ensure health vitals like "6/10 pain" or "400mg dosage" are never mistaken for sensitive personal data.



### Exercise B: Language Detection
I implemented a hybrid tier detection system. The first tier uses Unicode character ranges to identify Devanagari script. However, because Hinglish and English both use the Latin script, character checks alone are insufficient. 

For the second tier, I developed a Lexical Density Ratio. The detector compares the count of high-frequency Hindi phonetic markers—words like hai, tha, aaj, and yaar—against common English functional words. If the Hindi density exceeds a 20% threshold, the text is accurately labeled as hinglish.



### Exercise C: Light Parsing
This tool uses a modular architecture with separate classes for FoodParser and SymptomParser to maintain a clean separation of concerns. 

A key feature is the negation heuristics. To ensure health tracking remains accurate, the parser looks for negation markers such as no, nahi, or none within a local window of a symptom keyword. This allows the system to correctly distinguish between "I have cramps" and "No cramps." The extraction is entirely deterministic, using regex to anchor quantities to food items and mapping keywords to specific meal types.



---

## ⚖️ Engineering Tradeoffs

I intentionally prioritized privacy over flexibility by choosing local, deterministic rules instead of cloud-based LLMs. This ensures zero data leakage and sub-millisecond latency, which is essential for a private health journaling app. 

Additionally, I balanced precision against recall. The PII patterns are tuned for high precision; I felt it was better to keep generic clinical context un-scrubbed rather than accidentally masking a medication dosage that could be vital for a user's health analysis.

---

## 🚀 How to Run

Make sure you are in the project directory with Python 3.x installed.

### 1. PII Scrubber
python3 pii_scrubber.py --in_file journals.jsonl --out_file scrubbed.jsonl

### 2. Language Detection
python3 lang_detect.py --in_file texts.jsonl --out_file lang.jsonl

### 3. Light Parsing
python3 light_parse.py --in_file entries.jsonl --out_file parsed.jsonl

---
Candidate: Harshavardhan Reddy  
Date: December 26, 2025
