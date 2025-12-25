import os
import glob
import re

def has_chinese(text):
    return re.search(r'[\u4e00-\u9fff]', text) is not None

bat_files = glob.glob('**/*.bat', recursive=True)
bat_files = [f for f in bat_files if 'venv' not in f] # Exclude venv files

for file_path in bat_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if has_chinese(content):
                print(f"FOUND_CHINESE: {file_path}")
                # Print a snippet
                for line in content.splitlines():
                    if has_chinese(line):
                        print(f"  Snippet: {line.strip()[:50]}...")
    except UnicodeDecodeError:
        # Try GBK just in case, though usually utf-8 for this user based on 'start_frontend.bat' earlier
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
                if has_chinese(content):
                    print(f"FOUND_CHINESE (GBK): {file_path}")
        except:
            print(f"ERROR: Could not read {file_path}")
    except Exception as e:
        print(f"ERROR: {file_path} - {e}")
