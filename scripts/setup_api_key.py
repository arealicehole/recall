#!/usr/bin/env python3
"""
Setup script for Recall API key configuration
"""

import os
import json
import getpass

def setup_api_key():
    print("=" * 50)
    print("Recall API Key Setup")
    print("=" * 50)
    
    print("\nThis script will help you configure your AssemblyAI API key for Recall.")
    print("You can get a free API key at: https://www.assemblyai.com/")
    
    # Get API key from user
    print("\nPlease enter your AssemblyAI API key:")
    api_key = getpass.getpass("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return False
    
    # Validate API key format (basic check)
    if len(api_key) < 20 or not api_key.replace('-', '').replace('_', '').isalnum():
        print("❌ API key format appears invalid. Please check your key.")
        return False
    
    # Method 1: Save to user config directory
    config_dir = os.path.expanduser("~/.recall")
    config_file = os.path.join(config_dir, "config.json")
    
    try:
        os.makedirs(config_dir, exist_ok=True)
        
        # Load existing config or create new
        config_data = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
            except:
                pass
        
        # Update API key
        config_data['api_key'] = api_key
        
        # Save config
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ API key saved to: {config_file}")
        
    except Exception as e:
        print(f"❌ Failed to save to config file: {e}")
        
    # Method 2: Create .env file
    env_file = ".env"
    try:
        with open(env_file, 'w') as f:
            f.write(f"ASSEMBLYAI_API_KEY={api_key}\n")
        print(f"✅ API key saved to: {env_file}")
        
    except Exception as e:
        print(f"❌ Failed to save to .env file: {e}")
    
    # Method 3: Environment variable instruction
    print("\n" + "=" * 50)
    print("API Key Configuration Complete!")
    print("=" * 50)
    
    print("\nYour API key has been configured. You can now:")
    print("1. Run the web interface: python run_web.py")
    print("2. Run the desktop GUI: python run.py")
    print("3. Test the configuration: python debug_transcription.py")
    
    print(f"\nIf you need to change your API key later, you can:")
    print(f"- Edit the config file: {config_file}")
    print(f"- Edit the .env file: {env_file}")
    print(f"- Set environment variable: set ASSEMBLYAI_API_KEY={api_key}")
    
    return True

if __name__ == "__main__":
    setup_api_key() 