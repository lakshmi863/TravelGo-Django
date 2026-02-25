import os

def extract_files_and_content(root_folder, output_file):
    ignore_dirs = {'node_modules', 'venv', 'logs'}
    ignore_files = {'package-lock.json'}

    with open(output_file, 'w', encoding='utf-8') as out_file:
        for root, dirs, files in os.walk(root_folder):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for file in files:
                if file in ignore_files:
                    continue  # Skip ignored files

                file_path = os.path.join(root, file)
                out_file.write(f"\n{'='*80}\n")
                out_file.write(f"File: {file_path}\n")
                out_file.write(f"{'='*80}\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        out_file.write(f.read())
                except Exception as e:
                    out_file.write(f"[Error reading file: {e}]\n")

# Usage
root_folder_path = r"C:\Users\Lenovo\Desktop\Dgango Travel Backend"
output_text_file = "interviewcommunity.txt"

extract_files_and_content(root_folder_path, output_text_file)