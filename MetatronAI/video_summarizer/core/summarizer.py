"""
Summarizer Module - Functions for summarizing text with progress indicators.
"""

import os
from transformers import pipeline
import openai
from dotenv import load_dotenv
from tqdm import tqdm
import time

# Load environment variables
load_dotenv()

def add_watermark(summary_text):
    """Add watermark to the summary."""
    watermark = "\n\n---\n*Created by Alvin Atillo (TS-PH)*"
    return summary_text + watermark

def summarize_with_transformers(text, length_level=3):
    """
    Summarize text using Hugging Face Transformers with progress indicators.
    
    Args:
        text (str): Text to summarize.
        length_level (int): Summary length level (1-5).
    
    Returns:
        str: Summarized text.
    """
    print("\n🤖 STARTING LOCAL AI SUMMARIZATION")
    print("=" * 50)
    
    # Setup parameters
    max_length = 150 * length_level  # 150, 300, 450, 600, 750
    min_length = 50 * length_level   # 50, 100, 150, 200, 250
    
    print(f"📋 Configuration:")
    print(f"   🎯 Length level: {length_level}/5")
    print(f"   📏 Target length: {min_length}-{max_length} words")
    print(f"   📝 Input text: {len(text):,} characters")
    
    # Load model with progress
    print(f"\n📦 Loading BART summarization model...")
    with tqdm(total=100, desc="Loading model", bar_format="{l_bar}{bar}| {percentage:3.0f}%") as pbar:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        pbar.update(100)
    print("✅ Model loaded successfully")
    
    # Prepare chunks
    chunk_size = 1024
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    print(f"\n🔄 Processing text in {len(chunks)} chunk(s)...")
    
    # Summarize each chunk with progress
    chunk_summaries = []
    for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks", unit="chunk")):
        if len(chunk) > 100:  # Only summarize if there's enough text
            summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
            chunk_summaries.append(summary)
        else:
            chunk_summaries.append(chunk)
    
    # Final summarization if multiple chunks
    if len(chunk_summaries) > 1:
        print(f"\n🔗 Combining {len(chunk_summaries)} chunk summaries...")
        combined_summary = " ".join(chunk_summaries)
        
        with tqdm(total=100, desc="Final summary", bar_format="{l_bar}{bar}| {percentage:3.0f}%") as pbar:
            final_summary = summarizer(combined_summary, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
            pbar.update(100)
    elif len(chunk_summaries) == 1:
        final_summary = chunk_summaries[0]
    else:
        final_summary = ""
    
    # Add watermark and return
    result = add_watermark(final_summary)
    print(f"✅ Summarization complete!")
    print(f"   📄 Output length: {len(result)} characters")
    print(f"   🏷️ Watermark: Added")
    
    return result

def summarize_with_openai(text, length_level=3, include_chapters=True):
    """
    Summarize text using OpenAI's API.
    
    Args:
        text (str): Text to summarize.
        length_level (int): Summary length level (1-5).
        include_chapters (bool): Whether to include chapter summaries.
    
    Returns:
        str: Summarized text.
    """
    openai_api_key = os.getenv('OPENAI_API_KEY')
    openai_endpoint = os.getenv('OPENAI_ENDPOINT')
    
    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    
    # Adjust the prompt based on the length level
    detail_level = ["very brief", "brief", "moderate", "detailed", "very detailed"][length_level - 1]
    
    # Create the system prompt and user prompt based on whether chapter summaries are requested
    if include_chapters:
        system_prompt = f"""You are an assistant that creates structured summaries of educational content.
Your summaries should include:
1. An overall overview of the main topic (about {50 * length_level} words)
2. Chapter breakdowns with headers that identify the main sections/topics
3. A {detail_level} summary of each section with key points and insights

Format your response with clear headers and bullet points where appropriate."""

        user_prompt = f"""Please analyze the following transcript and provide:
1. OVERVIEW: A concise overview of the main topic
2. CHAPTERS: Break the content into logical chapters/sections with clear headers
3. For each chapter, provide a {detail_level} summary of key points

Transcript:
{text}"""
    else:
        system_prompt = f"You are an assistant that creates {detail_level} summaries of transcripts."
        user_prompt = f"Please provide a {detail_level} summary of the following transcript:\n\n{text}"
    
    try:
        # Create client with proper configuration
        print("Initializing OpenAI client...")
        
        # For newer versions of OpenAI library (>=1.0.0)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            if openai_endpoint:
                client.base_url = openai_endpoint
                
            print("Using OpenAI client with base URL:", client.base_url)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4096,
                temperature=0.5
            )
            
            summary = response.choices[0].message.content
            return add_watermark(summary)
            
        # For older versions of OpenAI library
        except (ImportError, AttributeError):
            print("Using legacy OpenAI API")
            import openai
            openai.api_key = openai_api_key
            
            if openai_endpoint:
                openai.api_base = openai_endpoint
                
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4096,
                temperature=0.5
            )
            
            summary = response.choices[0].message.content.strip()
            return add_watermark(summary)
            
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        raise Exception(f"Error with OpenAI API: {str(e)}")

def summarize_text(text, length_level=3, include_chapters=True):
    """
    Summarize text using the best available method.
    
    Args:
        text (str): Text to summarize.
        length_level (int): Summary length level (1-5).
        include_chapters (bool): Whether to include chapter summaries.
    
    Returns:
        str: Summarized text.
    """
    # Check if text is None or empty
    if not text:
        print("Warning: Empty text provided for summarization")
        return add_watermark("No text available to summarize.")
    
    # Primary method: Try to use OpenAI GPT for enhanced summarization
    if os.getenv('OPENAI_API_KEY'):
        try:
            print("🚀 Using OpenAI GPT for enhanced summarization...")
            return summarize_with_openai(text, length_level, include_chapters)
        except Exception as e:
            print(f"⚠️  OpenAI summarization failed: {str(e)}")
            print("🔄 Falling back to local BART model...")
    else:
        print("ℹ️  OpenAI API key not configured. Using local BART model...")
        print("💡 Tip: Add OPENAI_API_KEY to .env for enhanced summarization with chapter support!")
    
    # Fallback method: Use local BART transformer model
    try:
        if include_chapters:
            print("📖 Note: Chapter-based summarization requires OpenAI. Providing standard summary instead.")
        print("🤖 Using local BART model for summarization...")
        return summarize_with_transformers(text, length_level)
    except Exception as e:
        print(f"❌ Local summarization failed: {str(e)}")
        return add_watermark("Summarization failed. Please check the logs for more information.")
