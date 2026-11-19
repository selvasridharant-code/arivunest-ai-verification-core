# arivunest-ai-verification-core
Automated Document &amp; Academic Credential Verification Pipeline powered by Google Gemini Multimodal AI to extract and validate certificate fields into structured JSON.
# Arivu Nest AI Verification Core (`arivunest-ai-verification-core`)

An automated **Document & Academic Credential Verification Pipeline** developed as part of the **Arivu Nest R&D (Sprint 1)** Software Engineering & AI Research track.

## Overview
This module leverages **Google Gemini Multimodal AI** to ingest academic and internship certificates (Images & PDFs), verify visual authenticity markers (official seals, signatures, formatting), and extract key credential metadata into a strict, validated JSON schema.

## Key Features
- **Multimodal Ingestion:** Supports `.jpg`, `.png`, and `.pdf` credential documents.
- **Structured Extraction:** Uses Gemini Structured Outputs to accurately extract Candidate Name, Certificate ID, Issue Date, Issuing Authority, and Signature presence.
- **Tamper & Quality Checks:** Flags missing signatures, low-resolution scans, or inconsistent credential metadata.

## Tech Stack
- **Language:** Python 3.10+
- **AI Model:** Google Gemini (`google-genai` SDK)
- **Validation:** Pydantic
- **Document Processing:** PyMuPDF (`fitz`), Pillow 
