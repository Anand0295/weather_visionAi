#!/usr/bin/env python3
"""
Weather Project Server Runner
Run this script to start the Django development server
"""
import os
import sys
import subprocess

def main():
    # Change to the Django project directory
    project_dir = os.path.join(os.path.dirname(__file__), 'weatherProject')
    os.chdir(project_dir)
    
    print("Starting Weather Forecast Application...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Run Django development server
        subprocess.run([sys.executable, 'manage.py', 'runserver'], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        print("Make sure you have installed the requirements:")
        print("pip install -r ../requirements.txt")

if __name__ == '__main__':
    main()