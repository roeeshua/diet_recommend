import os
import fnmatch

def count_lines_in_project(extensions=['.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.java', '.cpp', '.c', '.h', '.vue']):
    total_lines = 0
    file_counts = {}
    
    for root, dirs, files in os.walk('.'):
        # 忽略一些常见的不需要统计的目录
        ignore_dirs = ['.git', '__pycache__', 'node_modules', 'venv', '.venv', 'env', '.env']
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            filepath = os.path.join(root, file)
            
            # 检查文件扩展名
            for ext in extensions:
                if file.endswith(ext):
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            line_count = len(lines)
                            total_lines += line_count
                            
                            # 按扩展名统计
                            if ext not in file_counts:
                                file_counts[ext] = {'files': 0, 'lines': 0}
                            file_counts[ext]['files'] += 1
                            file_counts[ext]['lines'] += line_count
                            
                            # 打印大文件（超过100行）
                            if line_count > 100:
                                print(f"  {filepath}: {line_count} lines")
                    except Exception as e:
                        print(f"无法读取文件 {filepath}: {e}")
                    break
    
    return total_lines, file_counts

if __name__ == "__main__":
    print("正在统计项目代码行数...\n")
    
    # 主要统计Python文件
    print("Python文件统计:")
    python_lines, python_counts = count_lines_in_project(['.py'])
    print(f"\n总计: {python_counts.get('.py', {}).get('files', 0)} 个Python文件, {python_counts.get('.py', {}).get('lines', 0)} 行代码\n")
    
    # 统计所有代码文件
    print("所有代码文件统计:")
    all_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.java', '.cpp', '.c', '.h', '.json', '.yml', '.yaml', '.md', '.vue']
    total_lines, all_counts = count_lines_in_project(all_extensions)
    
    print(f"\n按文件类型统计:")
    for ext, counts in sorted(all_counts.items()):
        print(f"  {ext}: {counts['files']} 个文件, {counts['lines']} 行")
    
    print(f"\n总计: {sum(c['files'] for c in all_counts.values())} 个文件, {total_lines} 行代码")