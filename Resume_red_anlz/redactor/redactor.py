import os.path
from fileinput import filename
import spacy
import fitz
import re

from pygments.lexer import words
from rapidfuzz import fuzz




nlp = spacy.load("en_core_web_sm")

whitelist_terms = [
    "civil engineering", "mechanical engineering", "electrical engineering",
    "chemical engineering", "b.tech", "m.tech", "ph.d", "engineering",
    "production", "mining", "metallurgical"
]

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = " "
    for page in doc:
        text+=page.get_text()
    return text

def redact_pii_keywords(text):

    # for detecting named entities using spacy
    doc = nlp(text)
    keywords = set()


    #redacted names, orgs, etc

    for ent in doc.ents:
        ent_text_lower = ent.text.lower()
        if ent.label_ in ["PERSON","ORG", "GPE"] and not any(kw in ent_text_lower for kw in whitelist_terms):
            keywords.add(ent.text.strip())

        #REDACTED MAILS
        keywords.update(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))

        #redacted contact number
        phone_regex = r"(?:(?:\+91|0091|91)?[-\s]?)?\(?\d{3,5}\)?[-\s]?\d{3,5}[-\s]?\d{3,5}"
        keywords.update(re.findall(phone_regex, text))
        #redacted urls
        keywords.update(re.findall(r"http[s]?://\S+", text))

        return  list(keywords)

def redact_pdf(input_pdf_path, output_pdf_path, pii_keywords, fuzz_threshold=70):
    doc = fitz.open(input_pdf_path)

    for page in doc:
        words = page.get_text("words") # will cover the list of words on the page with positions
        for keyword in pii_keywords:
            if not keyword.strip():
                continue
            for w in words:
                word_text = w[4]
                if fuzz.partial_ratio(keyword.lower(), word_text.lower()) >= fuzz_threshold:
                    areas = page.search_for(keyword)
                    for area in areas:
                        page.add_redact_annot(area, fill=(0, 0, 0))  # Black box redaction
        page.apply_redactions()

    doc.save(output_pdf_path)
    doc.close()
    print(f"[+] Redacted PDF saved to: {output_pdf_path}")


def redact_resume_pdf(input_pdf_path, output_dir="redacted"):
    text= extract_text_from_pdf(input_pdf_path)
    pii_keywords = redact_pii_keywords(text)

    #first extract the basename
    filename = os.path.splitext(os.path.basename(input_pdf_path))[0]
    #now create the output path
    output_path = os.path.join(output_dir, f"{filename}_redacted.pdf")
    #check whether the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    redact_pdf(input_pdf_path, output_path, pii_keywords)

    print(f"Redacted file saved at: {output_path}")
    return  output_path

##

#if __name__=="__main__":
 #   file_path = "Resume_red_anlz/data/ashusinghresume.pdf"  # Put your resume here
  #  text = extract_text_from_pdf(file_path)
   # redacted = redact_pii_keywords(text)
   # save_redacted_pdf(redacted,file_path)



