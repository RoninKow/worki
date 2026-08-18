# -*- coding: utf-8 -*-
"""
Программа для расчета отставания по срокам строительства
"""

from datetime import datetime, date
import sys


def get_date_input(prompt):
    """Запрашивает у пользователя дату в формате ДД.ММ.ГГГГ"""
    while True:
        user_input = input(prompt).strip()
        try:
            day, month, year = map(int, user_input.split('.'))
            return date(year, month, day)
        except ValueError:
            print("❌ Ошибка! Используйте формат ДД.ММ.ГГГГ (например, 25.12.2024)")


def calculate_delay(plan_date, actual_date):
    """
    Рассчитывает отставание в днях
    Возвращает положительное число если есть отставание,
    отрицательное если опережение, 0 если вовремя
    """
    delta = (actual_date - plan_date).days
    return delta


def get_delay_status(days):
    """Определяет статус отставания"""
    if days <= 0:
        return "✅ В срок или с опережением"
    elif days <= 7:
        return "⚠️ Небольшое отставание (до недели)"
    elif days <= 30:
        return "🔴 Серьезное отставание (до месяца)"
    elif days <= 90:
        return "🚨 Критическое отставание (до 3 месяцев)"
    else:
        return "💥 Катастрофическое отставание (более 3 месяцев)"


def main():
    print("=" * 60)
    print("🏗️  ПРОГРАММА РАСЧЕТА ОТСТАВАНИЯ ПО СРОКАМ СТРОИТЕЛЬСТВА")
    print("=" * 60)
    print()
    
    # Запрос плановой даты
    print("📅 Введите плановую дату завершения строительства:")
    plan_date = get_date_input("   Плановая дата (ДД.ММ.ГГГГ): ")
    
    print()
    
    # Запрос фактической даты
    print("📅 Введите фактическую/прогнозируемую дату завершения:")
    print("   (оставьте пустым для использования текущей даты)")
    actual_input = input("   Фактическая дата (ДД.ММ.ГГГГ): ").strip()
    
    if actual_input:
        actual_date = get_date_input("   Фактическая дата (ДД.ММ.ГГГГ): ")
    else:
        actual_date = date.today()
        print(f"   Используется текущая дата: {actual_date.strftime('%d.%m.%Y')}")
    
    print()
    print("=" * 60)
    
    # Расчет отставания
    delay_days = calculate_delay(plan_date, actual_date)
    
    # Вывод результатов
    print("📊 РЕЗУЛЬТАТЫ РАСЧЕТА:")
    print("-" * 60)
    print(f"Плановая дата завершения:     {plan_date.strftime('%d.%m.%Y')}")
    print(f"Фактическая дата завершения:  {actual_date.strftime('%d.%m.%Y')}")
    print("-" * 60)
    
    if delay_days > 0:
        print(f"⏰ ОТСТАВАНИЕ: {delay_days} дн.")
        print(f"Статус: {get_delay_status(delay_days)}")
        
        # Дополнительные расчеты
        weeks = delay_days // 7
        months = delay_days // 30
        print()
        print("Дополнительная информация:")
        print(f"  • Недель отставания: ~{weeks}")
        print(f"  • Месяцев отставания: ~{months}")
        
    elif delay_days < 0:
        print(f"🚀 ОПЕРЕЖЕНИЕ: {abs(delay_days)} дн.")
        print(f"Статус: {get_delay_status(delay_days)}")
    else:
        print("✅ Строительство завершено точно в срок!")
        print(f"Статус: {get_delay_status(delay_days)}")
    
    print("=" * 60)
    print()
    input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
