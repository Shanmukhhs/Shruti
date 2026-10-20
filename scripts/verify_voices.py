"""
SAPI5 Voice Verification Script
Checks available voices on Windows and verifies Hindi voice presence.
Run this before Phase 2 to ensure TTS support is available.
"""

import sys


def main():
    try:
        import pyttsx3
    except ImportError:
        print("ERROR: pyttsx3 is not installed.")
        print("Install it with: pip install pyttsx3")
        sys.exit(1)

    print("=" * 60)
    print("SAPI5 Voice Verification for Shruti")
    print("=" * 60)
    print()

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')

        if not voices:
            print("ERROR: No voices found on this system.")
            print("Please install at least one SAPI5 voice.")
            sys.exit(1)

        print(f"Found {len(voices)} voice(s):\n")

        hindi_found = False
        for i, voice in enumerate(voices, 1):
            voice_id = voice.id
            voice_name = voice.name
            voice_lang = getattr(voice, 'languages', ['Unknown'])
            print(f"Voice {i}:")
            print(f"  Name: {voice_name}")
            print(f"  ID: {voice_id}")
            print(f"  Languages: {voice_lang}")
            print()

            # Check for Hindi voice
            voice_name_lower = voice_name.lower()
            if 'hindi' in voice_name_lower or 'hi-' in str(voice_lang).lower():
                hindi_found = True
                print("  *** THIS IS A HINDI VOICE ***")
                print()

        print("=" * 60)
        if hindi_found:
            print("SUCCESS: Hindi voice found!")
            print("Shruti can generate Hindi audio.")
        else:
            print("WARNING: No Hindi voice found.")
            print("Hindi/mixed PDF uploads will be blocked.")
            print()
            print("To add Hindi voice:")
            print("Go to Windows Settings, then Time & Language, then Speech, then Add Hindi")
        print("=" * 60)

    except Exception as e:
        print(f"ERROR: Failed to initialize pyttsx3: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
