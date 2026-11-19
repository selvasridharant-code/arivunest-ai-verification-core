import os
import json
import fitz  # PyMuPDF
from PIL import Image
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# 1. Define Structured Output Schema
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
    """Loads an image or converts the first page of a PDF into a PIL Image."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        doc = fitz.open(file_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=200)
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
        return Image.open(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def verify_certificate(file_path: str) -> dict:
    """Extracts and verifies certificate metadata using Gemini Multimodal API."""
    client = genai.Client()  # Reads GEMINI_API_KEY from environment
    image = load_document_as_image(file_path)

    prompt = (
        "Analyze this academic or internship certificate carefully. "
        "Extract all key details accurately, check for visual authenticity markers "
        "such as official seals, logos, and authorized signatures, and return the result "
        "strictly matching the required JSON schema."
    )

    # Try primary model first, fallback if temporarily overloaded (503)
    for model_name in ["gemini-3.8-flash", "gemini-3.8-flash-lite", "gemini-2.5-pro"]:
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
            if "503" in str(e) or "404" in str(e):
                print(f"Model {model_name} unavailable, switching model...")
                continue
            raise e
    raise RuntimeError("All configured Gemini models are temporarily unavailable.")

if __name__ == "__main__":
    sample_file = "sample_certificate.pdf"  # Replace with your test certificate path
    if os.path.exists(sample_file):
        result = verify_certificate(sample_file)
        print(json.dumps(result, indent=2))
    else:
        print(f"Place a test certificate at '{sample_file}' and set GEMINI_API_KEY to run.")