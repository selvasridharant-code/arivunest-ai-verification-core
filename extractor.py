import os
import json
import time
import fitz  # PyMuPDF
from PIL import Image
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # Loads GEMINI_API_KEY from .env file

class CertificateVerification(BaseModel):
    candidate_name: str = Field(description="Full name of the candidate on the certificate")
    certificate_id: str = Field(description="Unique certificate or reference ID, or 'N/A' if not found")
    issue_date: str = Field(description="Date of issue in YYYY-MM-DD or original text format")
    issuing_authority: str = Field(description="Organization or institution issuing the certificate")
    course_or_role: str = Field(description="Course name, internship role, or achievement title")
    signatures_detected: bool = Field(description="True if official signature(s) or seal are visually present")
    verification_status: str = Field(description="VALID if key fields and signatures exist, else FLAGGED")
    remarks: str = Field(description="Brief notes on visual quality, missing fields, or anomalies")

def load_document_as_image(file_path: str) -> Image.Image:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        doc = fitz.open(file_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
        return Image.open(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def verify_certificate(file_path: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env or environment variables.")

    client = genai.Client(api_key=api_key)
    image = load_document_as_image(file_path)

    prompt = (
        "Analyze this academic or internship certificate carefully. "
        "Extract all key details accurately, check for visual authenticity markers "
        "such as official seals, logos, and authorized signatures, and return the result "
        "strictly matching the required JSON schema."
    )

    models_to_try = [

        "gemini-4-hydrogen",
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
    ]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[image, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CertificateVerification,
                    temperature=0.1,
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            err_msg = str(e)
            if "503" in err_msg or "429" in err_msg or "404" in err_msg:
                print(f"{model_name} unavailable/busy, switching to next model...")
                time.sleep(1)
                continue
            raise e
    raise RuntimeError("All configured Gemini models are temporarily busy. Please retry in a few seconds.")

if __name__ == "__main__":
    sample_file = "sample_certificate.pdf"
    if os.path.exists(sample_file):
        result = verify_certificate(sample_file)
        print(json.dumps(result, indent=2))
    else:
        print(f"Place a test certificate at '{sample_file}' and set GEMINI_API_KEY to run.")