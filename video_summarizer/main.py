#!/usr/bin/env python
"""
Video Summarizer - A CLI tool that transcribes videos and creates summaries.
"""

import argparse
import os
import sys
import time
from dotenv import load_dotenv

# Add parent directory to path to allow imports from core package
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Load local modules
from core.video_handler import download_video, extract_audio
from core.transcriber import transcribe_audio
from core.summarizer import summarize_text

# Load environment variables from .env file (for API keys)
load_dotenv()

def validate_args(args):
    """Validate command line arguments."""
    if args.file and not os.path.exists(args.file):
        print(f"Error: The file '{args.file}' does not exist.")
        return False
    
    if args.url and not (args.url.startswith('http://') or args.url.startswith('https://')):
        print(f"Error: The URL '{args.url}' is not valid.")
        return False
    
    return True

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Transcribe and summarize video content.')
    
    # Input source options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-f', '--file', help='Path to a local video file or transcript text file')
    input_group.add_argument('-u', '--url', help='URL to a video (YouTube, etc.)')
    
    # Optional arguments
    parser.add_argument('-o', '--output', help='Output directory for files (default: current directory)', default='.')
    parser.add_argument('-l', '--language', help='Language of the video (default: auto-detect)', default='auto')
    parser.add_argument('--keep-temp', action='store_true', help='Keep temporary files (audio, transcript)')
    parser.add_argument('--summary-length', type=int, default=3, help='Summary length (1-5, with 5 being the longest)')
    parser.add_argument('--chapters', action='store_true', help='Include chapter summaries in the output')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with detailed logging')
    
    args = parser.parse_args()
    
    if not validate_args(args):
        sys.exit(1)
    
    # Enable debug logging if requested
    if hasattr(args, 'debug') and args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG, 
                           format='%(asctime)s - %(levelname)s - %(message)s')
        logging.debug("Debug mode enabled")
    
    try:
        print("🎬 MetatronAI Video Summarizer")
        print("=" * 50)
        print("🤖 AI-powered video transcription and summarization")
        print("=" * 50)
        
        # Initialize variables
        audio_path = None
        transcript_path = None
        summary_path = None
        start_time = time.time()  # Track total processing time
        
        # Overall progress tracking
        total_steps = 5  # Video validation, audio extraction, transcription, summary, cleanup
        current_step = 0
        
        def show_step_progress(step_name):
            nonlocal current_step
            current_step += 1
            print(f"\n📋 STEP {current_step}/{total_steps}: {step_name}")
            print("-" * 30)
        
        # Check if input is a text file
        is_text_file = False
        if args.file and args.file.lower().endswith('.txt'):
            is_text_file = True
            show_step_progress("READING TEXT FILE")
            print(f"📄 Text file detected: {args.file}")
            transcript_path = args.file
            video_path = args.file  # Set video_path to the text file for naming the output
            
            # Read the transcript directly
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript = f.read()
            
            print(f"✅ Transcript loaded: {len(transcript):,} characters")
            
        # Regular video processing flow
        else:
            # Step 1: Get the video (download or use local file)
            if args.url:
                show_step_progress("DOWNLOADING VIDEO")
                video_path = download_video(args.url, args.output)
            else:
                show_step_progress("VALIDATING LOCAL VIDEO")
                video_path = args.file
                print(f"📁 Using local video file: {video_path}")
                
                # Validate file exists and get info
                if not os.path.exists(video_path):
                    raise FileNotFoundError(f"Video file not found: {video_path}")
                
                file_size = os.path.getsize(video_path) / (1024 * 1024)
                print(f"✅ Video file validated ({file_size:.1f} MB)")
            
            # Step 2: Extract audio from video
            show_step_progress("EXTRACTING AUDIO")
            audio_path = extract_audio(video_path, args.output)
            
            # Step 3: Transcribe audio
            show_step_progress("TRANSCRIBING AUDIO")
            print(f"🎙️ Language setting: {args.language}")
            transcript = transcribe_audio(audio_path, args.language)
            
            if not transcript:
                print("Warning: Transcription returned empty result.")
                transcript = "No transcription available."
            
            print(f"Transcription complete. Length: {len(transcript)} characters")
            
            # Save transcript to file
            if video_path:
                transcript_path = os.path.join(args.output, os.path.splitext(os.path.basename(video_path))[0] + '.txt')
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)
        
        # Step 4: Summarize transcript
        show_step_progress("GENERATING SUMMARY")
        print(f"📝 Generating summary using:")
        print(f"  ├─ Length level: {args.summary_length}")
        print(f"  └─ Chapter mode: {'enabled' if args.chapters else 'disabled'}")
        summary = summarize_text(transcript, args.summary_length, args.chapters)
        
        if not summary:
            print("⚠️ Warning: Summarization returned empty result.")
            summary = "No summary available."
        else:
            print(f"✅ Summary generated: {len(summary):,} characters")
        
        # Step 5: Save outputs
        show_step_progress("SAVING FILES")
        
        # Generate base name for output files
        if video_path:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            summary_path = os.path.join(args.output, base_name + '_summary.txt')
            transcript_path = os.path.join(args.output, base_name + '.txt') if not is_text_file else video_path
            
            # Save summary to file
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"📄 Summary saved to: {summary_path}")
        else:
            summary_path = None
            transcript_path = None
        
        # Step 5: Cleanup temporary files
        show_step_progress("CLEANING UP")
        
        # Clean up temporary files if not keeping them
        if not args.keep_temp and not args.file and not is_text_file and video_path:  # Don't delete the input file if it was provided
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
                    print(f"🗑️ Deleted temporary video file: {video_path}")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete temporary video file: {str(e)}")
                
        if not args.keep_temp and not is_text_file and audio_path:
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    print(f"🗑️ Deleted temporary audio file: {audio_path}")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete temporary audio file: {str(e)}")
        
        # Final completion message
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\n🎉 PROCESSING COMPLETE! ⏱️ Total time: {total_time:.1f} seconds")
        print("=" * 60)
        print(summary)
        if transcript_path:
            print(f"\n📄 Full transcript saved to: {transcript_path}")
        if summary_path:
            print(f"📝 Summary saved to: {summary_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Add debug flag handling
    if "--debug" in sys.argv:
        import logging
        logging.basicConfig(level=logging.DEBUG, 
                           format='%(asctime)s - %(levelname)s - %(message)s')
        logging.debug("Debug mode enabled via command line")
        
    main()
