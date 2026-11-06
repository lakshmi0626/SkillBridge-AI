# AI engine

The current deterministic production scoring and extraction implementation is in `backend/app/services/ai.py` to keep API execution self-contained. This directory is the planned package boundary for model experimentation and offline evaluation. No hosted LLM or external model service is required by the MVP.
