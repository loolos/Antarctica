import os

files_to_fix = [
    r'frontend\node_modules\spdy\lib\spdy\agent.js',
    r'frontend\node_modules\spdy\lib\spdy\server.js',
    r'frontend\node_modules\spdy-transport\lib\spdy-transport\utils.js'
]

replacement = 'Object.assign'
target = 'util._extend'

for file_path in files_to_fix:
    full_path = os.path.join(os.getcwd(), file_path)
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if target in content:
                new_content = content.replace(target, replacement)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed {file_path}")
            else:
                print(f"Target not found in {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    else:
        print(f"File not found: {full_path}")
