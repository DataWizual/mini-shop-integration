#!/usr/bin/env python3
"""
📁 SCRIPT MANAGER - Управление всеми диагностическими скриптами из папки diagnostics
"""

import os
import sys
import glob
import subprocess
from pathlib import Path

class ScriptManager:
    def __init__(self):
        self.diagnostics_dir = Path("diagnostics")
        self.script_categories = {
            'check': '🔍 Скрипты проверки',
            'fix': '🔧 Скрипты исправления', 
            'analyze': '📊 Анализаторы',
            'utility': '🛠️ Утилиты',
            'bash': '🐚 Bash скрипты'
        }
        
        self.scripts = self.scan_diagnostics_scripts()
    
    def scan_diagnostics_scripts(self):
        """Сканирует все скрипты в папке diagnostics"""
        scripts = {}
        
        if not self.diagnostics_dir.exists():
            print(f"❌ Папка {self.diagnostics_dir} не найдена!")
            return scripts
        
        # Ищем все .py и .sh файлы в diagnostics
        for pattern in ["*.py", "*.sh"]:
            for script_file in glob.glob(str(self.diagnostics_dir / pattern)):
                file_path = Path(script_file)
                if file_path.name == '__init__.py':
                    continue
                    
                scripts[file_path.name] = {
                    'path': file_path,
                    'category': self.detect_category(file_path.name),
                    'description': self.get_script_description(file_path.name),
                    'type': 'python' if file_path.suffix == '.py' else 'bash'
                }
        
        return scripts
    
    def detect_category(self, filename):
        """Определяет категорию скрипта по имени"""
        if filename.endswith('.sh'):
            return 'bash'
        elif filename.startswith('check_') or 'check' in filename:
            return 'check'
        elif filename.startswith('fix_') or 'fix' in filename:
            return 'fix'
        elif 'analyzer' in filename or 'analyze' in filename:
            return 'analyze'
        else:
            return 'utility'
    
    def get_script_description(self, filename):
        """Получает описание скрипта"""
        descriptions = {
            # Python скрипты
            'auto_detector.py': 'Авто-определение приложений и проблем',
            'check_panels.py': 'Проверка панелей Grafana',
            'check_grafana.py': 'Диагностика Grafana',
            'check_dashboards.py': 'Проверка дашбордов',
            'fix_loki_logs.py': 'Исправление проблем с Loki',
            'fix_promtail.py': 'Исправление Promtail',
            'fix_dashboards.py': 'Исправление дашбордов',
            'universal_dashboard_fixer.py': 'Универсальное исправление дашбордов',
            'final_fixes.py': 'Финальные исправления',
            'deep_promtail_debug.py': 'Глубокая диагностика Promtail',
            'network_analyzer.py': 'Анализатор сети',
            
            # Bash скрипты
            'control_panel.sh': 'Главная панель управления',
            'quick_check.sh': 'Быстрая проверка системы',
            'quick_ai_check.sh': 'Быстрая AI проверка',
            'metrics_system.sh': 'Метрики системы',
            'metrics_containers.sh': 'Метрики контейнеров'
        }
        
        return descriptions.get(filename, 'Диагностический скрипт')
    
    def list_scripts(self, category=None):
        """Показывает все скрипты"""
        if not self.scripts:
            print("❌ В папке diagnostics не найдены скрипты!")
            return
            
        print("📁 ДИАГНОСТИЧЕСКИЕ СКРИПТЫ:")
        print("=" * 60)
        
        for cat_name, cat_desc in self.script_categories.items():
            if category and category != cat_name:
                continue
                
            print(f"\n{cat_desc}:")
            cat_scripts = {k: v for k, v in self.scripts.items() if v['category'] == cat_name}
            
            if not cat_scripts:
                print("   ⚠️  Нет скриптов")
                continue
                
            for script_name, script_info in cat_scripts.items():
                icon = '🐍' if script_info['type'] == 'python' else '🐚'
                print(f"   • {icon} {script_name:28} - {script_info['description']}")
    
    def show_script_info(self, script_name):
        """Показывает информацию о скрипте"""
        if script_name not in self.scripts:
            print(f"❌ Скрипт {script_name} не найден в папке diagnostics")
            return
        
        script_info = self.scripts[script_name]
        script_type = "Python" if script_info['type'] == 'python' else "Bash"
        
        print(f"📄 ИНФОРМАЦИЯ О СКРИПТЕ: {script_name}")
        print("=" * 50)
        print(f"📂 Категория: {self.script_categories[script_info['category']]}")
        print(f"🔧 Тип: {script_type}")
        print(f"📝 Описание: {script_info['description']}")
        print(f"📁 Путь: {script_info['path']}")
        
        if script_info['type'] == 'python':
            print(f"🚀 Запуск: python3 diagnostics/{script_name}")
        else:
            print(f"🚀 Запуск: ./diagnostics/{script_name}")
    
    def run_script(self, script_name):
        """Запускает скрипт из папки diagnostics"""
        if script_name not in self.scripts:
            print(f"❌ Скрипт {script_name} не найден в папке diagnostics")
            return
        
        script_path = self.scripts[script_name]['path']
        script_type = self.scripts[script_name]['type']
        
        print(f"🚀 ЗАПУСК СКРИПТА: {script_name}")
        print("=" * 50)
        
        try:
            if script_type == 'python':
                # Запускаем Python скрипт
                result = subprocess.run([
                    sys.executable, 
                    str(script_path)
                ], capture_output=False, text=True)
            else:
                # Запускаем Bash скрипт
                # Сначала делаем исполняемым
                script_path.chmod(0o755)
                result = subprocess.run([
                    str(script_path)
                ], capture_output=False, text=True, shell=True)
            
            print(f"✅ Скрипт {script_name} завершен")
            
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
    
    def find_script(self, keyword):
        """Находит скрипты по ключевому слову"""
        print(f"🔍 ПОИСК СКРИПТОВ: '{keyword}'")
        print("=" * 50)
        
        found_scripts = []
        for script_name, script_info in self.scripts.items():
            if (keyword.lower() in script_name.lower() or 
                keyword.lower() in script_info['description'].lower()):
                found_scripts.append((script_name, script_info))
        
        if found_scripts:
            for script_name, script_info in found_scripts:
                icon = '🐍' if script_info['type'] == 'python' else '🐚'
                print(f"   • {icon} {script_name:25} - {script_info['description']}")
        else:
            print("   ⚠️  Скрипты не найдены")

def main():
    manager = ScriptManager()
    
    if len(sys.argv) == 1:
        # Показываем все скрипты
        manager.list_scripts()
        print(f"\n🚀 ИСПОЛЬЗОВАНИЕ:")
        print("  python3 script_manager.py list          - Все скрипты")
        print("  python3 script_manager.py info <скрипт> - Информация о скрипте")  
        print("  python3 script_manager.py run <скрипт>  - Запуск скрипта")
        print("  python3 script_manager.py find <слово>  - Поиск скриптов")
        print("  python3 script_manager.py check         - Только проверки")
        print("  python3 script_manager.py fix           - Только исправления")
        print("  python3 script_manager.py bash          - Только bash скрипты")
        return
    
    command = sys.argv[1]
    
    if command == 'list':
        manager.list_scripts()
    elif command == 'info' and len(sys.argv) > 2:
        manager.show_script_info(sys.argv[2])
    elif command == 'run' and len(sys.argv) > 2:
        manager.run_script(sys.argv[2])
    elif command == 'find' and len(sys.argv) > 2:
        manager.find_script(sys.argv[2])
    elif command in ['check', 'fix', 'analyze', 'utility', 'bash']:
        manager.list_scripts(command)
    else:
        print("❌ Неизвестная команда")
        print("🚀 Используйте: python3 script_manager.py list")

if __name__ == "__main__":
    main()
