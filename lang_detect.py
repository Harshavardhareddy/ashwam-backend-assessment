import re
import json
import argparse

class AshwamLangDetector:
    def __init__(self):
        # Lexicon of common Hindi words in Roman script (Hinglish)
        self.hi_lexicon = {
            "aaj", "aj", "kal", "hai", "tha", "thi", "the", "ho", "raha", "rahi", "rahe",
            "yaar", "mujhe", "muje", "mera", "meri", "mere", "nahi", "nhi", "na", "ab", 
            "thoda", "bahut", "bhot", "bohot", "ko", "ki", "ka", "ke", "ne", "se", "aur", 
            "mein", "me", "bhi", "raat", "subah", "gaya", "gya", "khana", "rathi"
        }
        # English stopword markers
        self.en_lexicon = {"the", "and", "with", "for", "was", "were", "been", "feeling", "today", "to", "at"}

    def get_metrics(self, text):
        # Script ratios
        total_chars = len(re.sub(r'\s+', '', text))
        if total_chars == 0: return 0, 0, 0
        
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        deva_chars = len(re.findall(r'[\u0900-\u097F]', text))
        
        return latin_chars/total_chars, deva_chars/total_chars, total_chars

    def detect(self, text):
        latin_ratio, deva_ratio, n_chars = self.get_metrics(text)
        tokens = re.findall(r'\b\w+\b', text.lower())
        n_tokens = len(tokens)

        # 1. Handle "Unknown" (Short/Noise)
        if n_tokens < 2 or (latin_ratio == 0 and deva_ratio == 0):
            return "unknown", "other", 0.0, {"reason": "insufficient_signal"}

        # 2. Determine Script
        if latin_ratio > 0 and deva_ratio > 0:
            script = "mixed"
        elif deva_ratio > 0.5:
            script = "devanagari"
        elif latin_ratio > 0.5:
            script = "latin"
        else:
            script = "other"

        # 3. Determine Language
        hi_hits = sum(1 for t in tokens if t in self.hi_lexicon)
        en_hits = sum(1 for t in tokens if t in self.en_lexicon)
        
        # Logic for Primary Language
        if script == "devanagari":
            lang = "hi"
            conf = 0.95
        elif script == "mixed":
            lang = "mixed"
            conf = 0.90
        else: # Latin script
            if hi_hits > en_hits:
                lang = "hinglish"
                conf = min(0.6 + (hi_hits/n_tokens), 0.98)
            elif hi_hits > 0 and en_hits > 0:
                lang = "mixed"
                conf = 0.85
            else:
                lang = "en"
                conf = min(0.7 + (en_hits/n_tokens), 0.99)

        evidence = {
            "latin_ratio": round(latin_ratio, 2),
            "devanagari_ratio": round(deva_ratio, 2),
            "hi_lexicon_hits": hi_hits,
            "en_stopword_hits": en_hits,
            "n_tokens": n_tokens
        }

        return lang, script, round(conf, 2), evidence

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_file", required=True)
    parser.add_argument("--out_file", required=True)
    args = parser.parse_args()

    detector = AshwamLangDetector()

    with open(args.in_file, 'r', encoding='utf-8') as f_in, \
         open(args.out_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            data = json.loads(line)
            lang, script, conf, evidence = detector.detect(data['text'])
            
            res = {
                "id": data['id'],
                "primary_language": lang,
                "script": script,
                "confidence": conf,
                "evidence": evidence
            }
            f_out.write(json.dumps(res) + "\n")

if __name__ == "__main__":
    main()
