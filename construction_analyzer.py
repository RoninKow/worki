import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import pandas as pd
import os

class ConstructionDelayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ отставания строительства")
        self.root.geometry("900x600")
        
        self.dataframe = None
        self.results = []
        
        # Создаем элементы интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Button(top_frame, text="📂 Загрузить Excel", command=self.load_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="💾 Сохранить отчет", command=self.save_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="❌ Очистить", command=self.clear_data).pack(side=tk.LEFT, padx=5)
        
        # Статус
        self.status_label = ttk.Label(top_frame, text="Файл не загружен", foreground="gray")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Таблица результатов
        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('task', 'plan_start', 'plan_end', 'fact_end', 'delay_days', 'status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        self.tree.heading('task', text='Задача')
        self.tree.heading('plan_start', text='План начало')
        self.tree.heading('plan_end', text='План окончание')
        self.tree.heading('fact_end', text='Факт окончание')
        self.tree.heading('delay_days', text='Отставание (дней)')
        self.tree.heading('status', text='Статус')
        
        self.tree.column('task', width=200)
        self.tree.column('plan_start', width=100)
        self.tree.column('plan_end', width=100)
        self.tree.column('fact_end', width=100)
        self.tree.column('delay_days', width=100)
        self.tree.column('status', width=150)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Итоговая статистика
        stats_frame = ttk.LabelFrame(self.root, text="Общая статистика", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="Загрузите файл для анализа", font=("Arial", 10))
        self.stats_label.pack()
        
    def parse_date(self, date_str):
        """Парсинг даты из разных форматов"""
        if pd.isna(date_str) or str(date_str).strip() == '':
            return None
        
        date_formats = [
            '%d.%m.%Y',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y.%m.%d'
        ]
        
        date_str = str(date_str).strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Попытка использовать pandas
        try:
            return pd.to_datetime(date_str).to_pydatetime()
        except:
            return None
    
    def get_delay_status(self, days):
        """Определение статуса отставания"""
        if days <= 0:
            return "✅ В срок", "green"
        elif days <= 7:
            return "⚠️ Небольшое (до 7 дней)", "orange"
        elif days <= 30:
            return "🔴 Серьезное (до 30 дней)", "red"
        elif days <= 90:
            return "🚨 Критическое (до 90 дней)", "darkred"
        else:
            return "💥 Катастрофическое (>90 дней)", "purple"
    
    def load_excel(self):
        """Загрузка Excel файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите Excel файл",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.dataframe = pd.read_excel(file_path)
            
            # Проверка необходимых колонок
            required_cols = ['Наименование задачи', 'Плановая дата окончания']
            missing_cols = [col for col in required_cols if col not in self.dataframe.columns]
            
            if missing_cols:
                messagebox.showerror("Ошибка", f"В файле отсутствуют колонки: {', '.join(missing_cols)}")
                return
            
            self.analyze_data()
            self.status_label.config(text=f"Загружен: {os.path.basename(file_path)}", foreground="green")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def analyze_data(self):
        """Анализ данных из таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.results = []
        total_delay = 0
        critical_tasks = 0
        
        today = datetime.now()
        
        for index, row in self.dataframe.iterrows():
            task_name = str(row.get('Наименование задачи', f'Задача {index+1}'))
            plan_start = self.parse_date(row.get('Плановая дата начала', ''))
            plan_end = self.parse_date(row.get('Плановая дата окончания', ''))
            fact_end = self.parse_date(row.get('Фактическая дата окончания', ''))
            
            # Если фактическая дата не указана, используем текущую дату для расчета
            if fact_end is None and plan_end is not None:
                if plan_end < today:
                    fact_end = today  # Считаем, что задача еще не выполнена
                else:
                    fact_end = None  # Задача в будущем
            
            delay_days = 0
            status_text = "✅ В плане"
            status_color = "black"
            
            if plan_end and fact_end:
                delay = (fact_end - plan_end).days
                if delay > 0:
                    delay_days = delay
                    status_text, status_color = self.get_delay_status(delay_days)
                    total_delay += delay_days
                    if delay_days > 30:
                        critical_tasks += 1
                elif delay <= 0 and fact_end <= today:
                    status_text = "✅ Выполнено в срок"
                    status_color = "green"
            elif plan_end and today > plan_end and fact_end is None:
                # Задача просрочена, но факт не указан
                delay = (today - plan_end).days
                delay_days = delay
                status_text, status_color = self.get_delay_status(delay_days)
                total_delay += delay_days
                if delay_days > 30:
                    critical_tasks += 1
            
            # Форматируем даты для отображения
            plan_start_str = plan_start.strftime('%d.%m.%Y') if plan_start else "-"
            plan_end_str = plan_end.strftime('%d.%m.%Y') if plan_end else "-"
            fact_end_str = fact_end.strftime('%d.%m.%Y') if fact_end else "-"
            
            self.tree.insert('', tk.END, values=(
                task_name,
                plan_start_str,
                plan_end_str,
                fact_end_str,
                delay_days,
                status_text
            ))
            
            self.results.append({
                'task': task_name,
                'plan_start': plan_start_str,
                'plan_end': plan_end_str,
                'fact_end': fact_end_str,
                'delay_days': delay_days,
                'status': status_text
            })
        
        # Обновление статистики
        tasks_count = len(self.dataframe)
        avg_delay = total_delay / tasks_count if tasks_count > 0 else 0
        
        stats_text = (
            f"Всего задач: {tasks_count} | "
            f"Общее отставание: {total_delay} дн. | "
            f"Среднее отставание: {avg_delay:.1f} дн. | "
            f"Критических задач: {critical_tasks}"
        )
        self.stats_label.config(text=stats_text)
    
    def save_report(self):
        """Сохранение отчета в Excel"""
        if not self.results:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные для анализа")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить отчет",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if not file_path:
            return
        
        try:
            df_report = pd.DataFrame(self.results)
            df_report.to_excel(file_path, index=False)
            messagebox.showinfo("Успех", f"Отчет сохранен:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчет:\n{str(e)}")
    
    def clear_data(self):
        """Очистка данных"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.results = []
        self.dataframe = None
        self.status_label.config(text="Файл не загружен", foreground="gray")
        self.stats_label.config(text="Загрузите файл для анализа")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConstructionDelayApp(root)
    root.mainloop()