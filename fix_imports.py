import os
import glob

def fix_imports(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content.replace('from backend.', 'from ')
                new_content = new_content.replace('import backend.', 'import ')
                
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Fixed imports in {file_path}")

if __name__ == '__main__':
    fix_imports('f:/Hospital-Patient-Records-Management-System/backend')
