#!/usr/bin/env python3
"""
Setup script for CryptoGap+
"""
import os
import sys
import subprocess
import shutil

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def create_env_file():
    """Create .env file from example"""
    if not os.path.exists(".env"):
        if os.path.exists("env_example.txt"):
            shutil.copy("env_example.txt", ".env")
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your API keys")
        else:
            print("⚠️  env_example.txt not found, creating basic .env file")
            with open(".env", "w") as f:
                f.write("# Add your API keys here\n")
                f.write("GROQ_API_KEY=your_groq_api_key_here\n")
    else:
        print("✅ .env file already exists")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up CryptoGap+")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create .env file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: streamlit run app.py")
    print("3. Open your browser to http://localhost:8501")
    print("\nNote: You can run without API keys, but AI analysis requires Groq API key")

if __name__ == "__main__":
    main()
