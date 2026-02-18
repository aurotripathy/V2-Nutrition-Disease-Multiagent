"""
Configuration constants for v3_nutri_agent
"""
# --- Define Model Constants for easier use ---
# More supported models can be referenced here: https://ai.google.dev/gemini-api/docs/models#model-variations
# Note: gemini-3-flash-preview does NOT support function calling (tools)
# Using gemini-1.5-flash which supports function calling/tools
GEMINI_MODEL = "gemini-2.5-flash"  # Supports function calling/tools
GEMINI_OCR_MODEL = "gemini-2.5-flash"
