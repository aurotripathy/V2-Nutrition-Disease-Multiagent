import os                     # Provides functions for interacting with the operating system                                                                                                         
import google.genai as genai  # Official Google Generative AI SDK                                                                                                                                    
from google.genai import types  # For creating message Content/Parts                                                                                                                                 
import json
import base64
           

def get_nutriments_from_OCRd_image_file(file_path: str) -> dict:
    """Read and return the content of an image file (jpg/jpeg/webp/png) from the filesystem.
    Uses Gemini to perform OCR and extract text."""
    try:
        # Check file extension to determine file type
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Handle image files (jpg, jpeg, webp, png)
        if file_ext in ['.jpg', '.jpeg', '.webp', '.png']:
            with open(file_path, 'rb') as f:
                image_data = f.read()
            file_size = len(image_data)
            
            # Use Gemini for OCR - extract all text from the image
            ocr_text = None
            max_retries = 3
            retry_count = 0
            
            try:
                client = genai.Client()
                # Read image file
                with open(file_path, 'rb') as img_file:
                    image_bytes = img_file.read()
                
                # Determine MIME type
                mime_type_map = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.webp': 'image/webp',
                    '.png': 'image/png'
                }
                mime_type = mime_type_map.get(file_ext, 'image/jpeg')
                
                # Create image part
                image_part = types.Part(
                    inline_data=types.Blob(
                        data=image_bytes,
                        mime_type=mime_type
                    )
                )
                
                # Loop until we get valid JSON or max retries reached
                while retry_count < max_retries:
                    # Simple prompt - responseMimeType will enforce JSON format
                    prompt_text = "Extract all text from this image and return it in a structured format."
                    
                    # Use responseMimeType to force JSON output
                    # Note: Even with responseMimeType, sometimes markdown wrapping occurs
                    response = client.models.generate_content(
                        model="models/gemini-2.5-flash",
                        contents=[types.Content(
                            parts=[
                                types.Part(text=prompt_text),
                                image_part
                            ]
                        )],
                        config=types.GenerateContentConfig(
                            responseMimeType="application/json"
                        )
                    )
                    
                    # print(f"Raw response:\n {response}")

                    if hasattr(response, 'candidates') and response.candidates:
                        print(f"Response candidates: {len(response.candidates)}")

                    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                        # Get the text from response
                        ocr_text = response.candidates[0].content.parts[0].text.strip()
                        # print(f"OCR text: {ocr_text}")
                        
                        # Remove any markdown code blocks if present (shouldn't be, but just in case)
                        if ocr_text.startswith("```"):
                            # Extract from code block
                            lines = ocr_text.split('\n')
                            if lines[0].startswith("```"):
                                lines = lines[1:]
                            if lines and lines[-1].strip() == "```":
                                lines = lines[:-1]
                            ocr_text = '\n'.join(lines).strip()
                        
                        # Check if response is valid JSON
                        try:
                            parsed_json = json.loads(ocr_text)
                            print(f"Valid JSON received on attempt {retry_count + 1}")
                            # Store as parsed JSON object instead of string for better readability
                            ocr_text = parsed_json
                            break
                        except json.JSONDecodeError as e:
                            # Not valid JSON, print debug info and retry
                            print(f"Attempt {retry_count + 1}: Invalid JSON. Error: {str(e)}")
                            print(f"Response preview: {ocr_text[:500]}...")
                            print(f"Full response: {ocr_text}")
                            retry_count += 1
                            if retry_count >= max_retries:
                                ocr_text = f"Failed to get valid JSON after {max_retries} attempts. Last response: {ocr_text[:500]}"
                    else:
                        retry_count += 1
                        if retry_count >= max_retries:
                            ocr_text = "No text found in image after multiple attempts"
                            
            except Exception as ocr_error:
                ocr_text = f"OCR failed: {str(ocr_error)}"
            
            # Encode image as base64 for text representation
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create structured response
            # If ocr_text is already a parsed JSON object, use it directly; otherwise keep as string
            result = {
                # "file_path": file_path,
                # "file_type": "image",
                # "file_size_bytes": file_size,
                # "base64_data": image_base64,
                "ocr_text": ocr_text if isinstance(ocr_text, dict) else ocr_text
            }
            
            return json.dumps(result, indent=None, ensure_ascii=False)
        
        # Handle invalid image files, error out for now
        else:
            print(f"Error: File '{file_path}' is not a valid image file (.jpg, .jpeg, .webp, .png)")
            return f"Error: File '{file_path}' is not a valid image file (.jpg, .jpeg, .webp, .png)"
            return {}
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except UnicodeDecodeError:
        return f"Error: File '{file_path}' appears to be binary or not a valid text file. Try using an image file (.jpg, .jpeg, .webp, .png) or a text file."
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"
