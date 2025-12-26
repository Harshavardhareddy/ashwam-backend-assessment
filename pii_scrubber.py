import re
import json
import argparse

class PII_Scrubber:
    def __init__(self):
        # Specific patterns to catch required Ashwam PII types
        self.patterns = {
            "EMAIL": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "PHONE": r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
            "DOB": r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
            "APPT_ID": r'\b(APPT|BKG|INV|REF|BUPA)-[A-Z0-9-]+\b',
            "GOV_ID": r'\b\d{3,4}[\s-]\d{2,5}[\s-]\d{1,4}\b',  # Medicare, SSN, Aadhaar
            "ADDRESS": r'\d+\s[A-Za-z\s]+(Street|St|Rd|Road|Lane|Ln|Ave|VIC|Pune|Carlton)\s?\d*',
            "PROVIDER": r'(Monash Women’s Health Clinic|Sunrise IVF|City Pathology Labs|Lotus Fertility)',
            "NAME": r'(Dr\.\s|Partner\s|Patient:\s)([A-Z][a-z]+(\s[A-Z][a-z]+)?)'
        }

    def process_text(self, text):
        matches = []
        for p_type, pattern in self.patterns.items():
            for m in re.finditer(pattern, text):
                matches.append({
                    "type": p_type,
                    "start": m.start(),
                    "end": m.end(),
                    "value": m.group()
                })

        # Resolve Overlaps: Sort by length descending, keep only non-overlapping spans
        matches.sort(key=lambda x: (x['end'] - x['start']), reverse=True)
        final_spans = []
        occupied_indices = set()

        for m in matches:
            span_range = set(range(m['start'], m['end']))
            if not (span_range & occupied_indices):
                final_spans.append(m)
                occupied_indices.update(span_range)

        # Sort spans by start position for replacement
        final_spans.sort(key=lambda x: x['start'])
        
        # Build scrubbed text
        scrubbed_text = text
        offset = 0
        for m in final_spans:
            placeholder = f"[{m['type']}]"
            start = m['start'] + offset
            end = m['end'] + offset
            scrubbed_text = scrubbed_text[:start] + placeholder + scrubbed_text[end:]
            offset += len(placeholder) - (m['end'] - m['start'])

        return scrubbed_text, final_spans

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_file", required=True)
    parser.add_argument("--out_file", required=True)
    args = parser.parse_args()

    scrubber = PII_Scrubber()

    with open(args.in_file, 'r') as f_in, open(args.out_file, 'w') as f_out:
        for line in f_in:
            data = json.loads(line)
            scrubbed_text, spans = scrubber.process_text(data['text'])
            
            output = {
                "entry_id": data['entry_id'],
                "scrubbed_text": scrubbed_text,
                "detected_spans": [{"type": s['type'], "start": s['start'], "end": s['end']} for s in spans],
                "types_found": list(set(s['type'] for s in spans)),
                "scrubber_version": "v1"
            }
            f_out.write(json.dumps(output) + "\n")

if __name__ == "__main__":
    main()
