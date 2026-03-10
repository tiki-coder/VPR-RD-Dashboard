import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple
import time
import numpy as np

# ============================================================================
# КОНФИГУРАЦИЯ СТРАНИЦЫ
# ============================================================================

st.set_page_config(
    page_title="Анализ результатов ВПР",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# СТИЛИ CSS
# ============================================================================

st.markdown("""
<style>
    /* Общие стили */
    .main {
        padding-top: 0rem;
    }
    
    /* Убираем отступы сверху */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
    }
    
    /* ЛИПКИЙ ХЕДЕР С ФИЛЬТРАМИ - ИСПРАВЛЕНО */
    .sticky-header {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: #0E1117;
        padding: 1.5rem 0 1.5rem 0;
        margin: -1rem -5rem 2rem -5rem;
        padding-left: 5rem;
        padding-right: 5rem;
        border-bottom: 2px solid rgba(255, 107, 53, 0.3);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
    
    /* Для светлой темы */
    @media (prefers-color-scheme: light) {
        .sticky-header {
            background-color: #FFFFFF;
            border-bottom: 2px solid rgba(255, 107, 53, 0.3);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
    }
    
    /* Карточки метрик */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 33, 39, 0.95) 0%, rgba(30, 33, 39, 0.7) 100%);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: rgba(250, 250, 250, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #FAFAFA;
        margin-bottom: 0.25rem;
    }
    
    .metric-subtitle {
        font-size: 0.875rem;
        color: rgba(250, 250, 250, 0.5);
    }
    
    /* Секции графиков */
    .chart-section {
        background: rgba(30, 33, 39, 0.5);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #FF6B35;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-left: 4px solid #FF6B35;
        padding-left: 1rem;
    }
    
    /* Таблица необъективности */
    .bias-table {
        background: rgba(30, 33, 39, 0.8);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .bias-school-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        transition: background 0.2s ease;
    }
    
    .bias-school-row:hover {
        background: rgba(255, 107, 53, 0.1);
    }
    
    .bias-school-name {
        flex: 1;
        font-size: 0.9rem;
        color: #FAFAFA;
    }
    
    .bias-badge {
        background: #FF6B35;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 1rem;
    }
    
    .bias-subjects {
        font-size: 0.8rem;
        color: rgba(250, 250, 250, 0.6);
        margin-left: 0.5rem;
    }
    
    /* Анимация загрузки */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 60vh;
    }
    
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(255, 107, 53, 0.2);
        border-top: 4px solid #FF6B35;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        margin-top: 1.5rem;
        font-size: 1.1rem;
        color: rgba(250, 250, 250, 0.7);
    }
    
    /* Заголовок приложения */
    .app-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .app-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FAFAFA;
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 0.9rem;
        color: rgba(250, 250, 250, 0.5);
        margin: 0;
    }
    
    /* Адаптация для светлой темы */
    @media (prefers-color-scheme: light) {
        .metric-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(249, 249, 249, 0.9) 100%);
            border: 1px solid rgba(0, 0, 0, 0.08);
        }
        
        .chart-section {
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(0, 0, 0, 0.08);
        }
        
        .metric-label, .metric-subtitle {
            color: rgba(0, 0, 0, 0.6);
        }
        
        .metric-value {
            color: #1a1a1a;
        }
        
        .bias-school-name {
            color: #1a1a1a;
        }
    }
    
    /* Скрыть меню Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Стили для selectbox */
    .stSelectbox > div > div {
        background-color: rgba(30, 33, 39, 0.8);
        border-radius: 8px;
    }
    
    /* Фиксация отступов для липкого хедера */
    div[data-testid="stVerticalBlock"] > div:has(div.sticky-header) {
        position: sticky;
        top: 0;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ФУНКЦИИ ЗАГРУЗКИ И КЭШИРОВАНИЯ ДАННЫХ
# ============================================================================

@st.cache_data(show_spinner=False)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Загружает данные из Excel файлов с оптимизацией для больших объемов.
    Возвращает кортеж из трех DataFrame: marks, scores, bias.
    """
    try:
        # Загрузка с оптимизацией типов данных
        marks = pd.read_excel(
            'marks.xlsx',
            engine='openpyxl',
            dtype={
                'Год': 'int32',
                'Класс': 'int32',
                'Кол-во участников': 'int32'
            }
        )
        
        scores = pd.read_excel(
            'scores.xlsx',
            engine='openpyxl',
            dtype={
                'Год': 'int32',
                'Класс': 'int32',
                'Кол-во участников': 'int32'
            }
        )
        
        bias = pd.read_excel(
            'bias.xlsx',
            engine='openpyxl',
            dtype={
                'Год': 'int32'
            }
        )
        
        # Очистка названий столбцов от лишних пробелов
        marks.columns = marks.columns.str.strip()
        scores.columns = scores.columns.str.strip()
        bias.columns = bias.columns.str.strip()
        
        # Очистка значений от пробелов для текстовых полей
        for col in ['Предмет', 'Муниципалитет', 'Логин', 'ОО']:
            if col in marks.columns:
                marks[col] = marks[col].astype(str).str.strip()
            if col in scores.columns:
                scores[col] = scores[col].astype(str).str.strip()
            if col in bias.columns:
                bias[col] = bias[col].astype(str).str.strip()
        
        return marks, scores, bias
        
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке данных: {str(e)}")
        st.stop()

@st.cache_data(show_spinner=False)
def get_filter_options(marks: pd.DataFrame) -> Dict[str, List]:
    """
    Извлекает уникальные значения для фильтров.
    """
    return {
        'years': sorted(marks['Год'].unique(), reverse=True),
        'classes': sorted(marks['Класс'].unique()),
        'subjects': sorted(marks['Предмет'].unique()),
        'municipalities': ['Все'] + sorted(marks['Муниципалитет'].unique())
    }

# ============================================================================
# ФУНКЦИИ РАСЧЕТА МЕТРИК - ИСПРАВЛЕНО
# ============================================================================

def calculate_metrics(filtered_data: pd.DataFrame) -> Dict[str, float]:
    """
    Рассчитывает метрики: количество ОО, участников, успеваемость и качество.
    ИСПРАВЛЕНО: Правильный расчет взвешенного среднего.
    """
    if filtered_data.empty:
        return {
            'schools': 0,
            'participants': 0,
            'success_rate': 0,
            'quality_rate': 0
        }
    
    # Количество уникальных школ
    schools_count = filtered_data['Логин'].nunique()
    
    # Общее количество участников
    total_participants = int(filtered_data['Кол-во участников'].sum())
    
    # Расчет взвешенного среднего для успеваемости и качества
    total_success = 0
    total_quality = 0
    
    for _, row in filtered_data.iterrows():
        participants = row['Кол-во участников']
        
        # Успеваемость (3 + 4 + 5) для этой школы
        school_success = row['3'] + row['4'] + row['5']
        
        # Качество (4 + 5) для этой школы
        school_quality = row['4'] + row['5']
        
        # Взвешиваем по количеству участников
        total_success += school_success * participants
        total_quality += school_quality * participants
    
    # Вычисляем средние
    success_rate = (total_success / total_participants) if total_participants > 0 else 0
    quality_rate = (total_quality / total_participants) if total_participants > 0 else 0
    
    return {
        'schools': schools_count,
        'participants': total_participants,
        'success_rate': success_rate,
        'quality_rate': quality_rate
    }

def get_marks_distribution(filtered_data: pd.DataFrame) -> pd.DataFrame:
    """
    Получает распределение оценок для построения графика.
    ИСПРАВЛЕНО: Взвешенное среднее по количеству участников.
    """
    if filtered_data.empty:
        return pd.DataFrame()
    
    total_participants = filtered_data['Кол-во участников'].sum()
    
    # Взвешенное среднее для каждой оценки
    marks_weighted = {}
    for mark in ['2', '3', '4', '5']:
        weighted_sum = 0
        for _, row in filtered_data.iterrows():
            weighted_sum += row[mark] * row['Кол-во участников']
        marks_weighted[mark] = weighted_sum / total_participants if total_participants > 0 else 0
    
    result = pd.DataFrame({
        'Оценка': ['2', '3', '4', '5'],
        'Процент': [marks_weighted['2'], marks_weighted['3'], marks_weighted['4'], marks_weighted['5']]
    })
    
    return result

def get_scores_distribution(scores_data: pd.DataFrame, year: int, class_num: int, 
                            subject: str, municipality: str, school: str) -> pd.DataFrame:
    """
    Получает распределение первичных баллов.
    ИСПРАВЛЕНО: Улучшена фильтрация данных.
    """
    # Фильтрация данных
    filtered = scores_data[
        (scores_data['Год'] == year) &
        (scores_data['Класс'] == class_num) &
        (scores_data['Предмет'].str.strip() == subject.strip())
    ].copy()
    
    if municipality != 'Все':
        # Убираем префиксы "город" и "г." для сопоставления
        filtered['Муниципалитет_clean'] = filtered['Муниципалитет'].str.replace('город ', '', regex=False).str.replace('г. ', '', regex=False).str.strip()
        municipality_clean = municipality.replace('город ', '').replace('г. ', '').strip()
        filtered = filtered[filtered['Муниципалитет_clean'] == municipality_clean]
    
    if school != 'Все':
        filtered = filtered[filtered['ОО'].str.strip() == school.strip()]
    
    if filtered.empty:
        return pd.DataFrame()
    
    # Определяем колонки с баллами (все числовые колонки после основных)
    score_columns = []
    for col in filtered.columns:
        try:
            int(col)
            score_columns.append(col)
        except ValueError:
            continue
    
    if not score_columns:
        return pd.DataFrame()
    
    # Взвешенное среднее по количеству участников
    total_participants = filtered['Кол-во участников'].sum()
    
    scores_weighted = {}
    for col in score_columns:
        weighted_sum = 0
        for _, row in filtered.iterrows():
            weighted_sum += row[col] * row['Кол-во участников']
        scores_weighted[int(col)] = weighted_sum / total_participants if total_participants > 0 else 0
    
    result = pd.DataFrame({
        'Балл': list(scores_weighted.keys()),
        'Процент': list(scores_weighted.values())
    })
    
    return result.sort_values('Балл')

def get_bias_data(bias_df: pd.DataFrame, marks_df: pd.DataFrame, year: int, 
                  municipality: str, school: str) -> Dict:
    """
    Получает данные по необъективности для выбранной школы и муниципалитета.
    ИСПРАВЛЕНО: Полностью переработана логика.
    """
    result = {
        'school_markers': 0,
        'school_subjects': [],
        'municipality_stats': [],
        'school_in_bias_3years': False,
        'biased_schools_list': []
    }
    
    # 1. Маркеры конкретной школы
    if school != 'Все':
        school_bias = bias_df[
            (bias_df['Год'] == year) &
            (bias_df['ОО'].str.strip() == school.strip())
        ]
        
        if not school_bias.empty:
            row = school_bias.iloc[0]
            result['school_markers'] = int(row['Количество маркеров']) if pd.notna(row['Количество маркеров']) else 0
            
            # Определяем предметы с маркерами
            subjects_with_markers = []
            
            subject_map = {
                '4 РУ': 'РУ 4',
                '4 МА': 'МА 4',
                '5 РУ': 'РУ 5',
                '5 МА': 'МА 5'
            }
            
            for col, label in subject_map.items():
                if col in row.index and pd.notna(row[col]) and row[col] > 0:
                    subjects_with_markers.append(label)
            
            result['school_subjects'] = subjects_with_markers
        
        # Проверка попадания школы в необъективность за последние 3 года
        school_bias_3years = bias_df[
            (bias_df['Год'].isin([year, year-1, year-2])) &
            (bias_df['ОО'].str.strip() == school.strip())
        ]
        result['school_in_bias_3years'] = len(school_bias_3years) > 0
    
    # 2. Статистика по муниципалитету за 3 года
    for y in [year-2, year-1, year]:
        year_bias = bias_df[bias_df['Год'] == y].copy()
        
        if municipality != 'Все':
            # Очистка названий муниципалитетов
            year_bias['Муниципалитет_clean'] = year_bias['Муниципалитет'].str.replace('город ', '', regex=False).str.replace('г. ', '', regex=False).str.strip()
            municipality_clean = municipality.replace('город ', '').replace('г. ', '').strip()
            year_bias = year_bias[year_bias['Муниципалитет_clean'] == municipality_clean]
        
        # Количество школ с маркерами
        schools_with_bias = year_bias['Логин'].nunique()
        
        # Общее количество школ (из данных по русскому языку 4 класс)
        year_marks = marks_df[
            (marks_df['Год'] == y) &
            (marks_df['Класс'] == 4) &
            (marks_df['Предмет'].str.contains('Русский', case=False, na=False))
        ].copy()
        
        if municipality != 'Все':
            year_marks['Муниципалитет_clean'] = year_marks['Муниципалитет'].str.replace('город ', '', regex=False).str.replace('г. ', '', regex=False).str.strip()
            municipality_clean = municipality.replace('город ', '').replace('г. ', '').strip()
            year_marks = year_marks[year_marks['Муниципалитет_clean'] == municipality_clean]
        
        total_schools = year_marks['Логин'].nunique()
        
        percentage = (schools_with_bias / total_schools * 100) if total_schools > 0 else 0
        
        result['municipality_stats'].append({
            'year': y,
            'biased_schools': schools_with_bias,
            'total_schools': total_schools,
            'percentage': percentage
        })
    
    # 3. Список школ с маркерами в текущем году
    year_bias = bias_df[bias_df['Год'] == year].copy()
    
    if municipality != 'Все':
        year_bias['Муниципалитет_clean'] = year_bias['Муниципалитет'].str.replace('город ', '', regex=False).str.replace('г. ', '', regex=False).str.strip()
        municipality_clean = municipality.replace('город ', '').replace('г. ', '').strip()
        year_bias = year_bias[year_bias['Муниципалитет_clean'] == municipality_clean]
    
    for _, row in year_bias.iterrows():
        subjects = []
        
        subject_map = {
            '4 РУ': 'РУ 4',
            '4 МА': 'МА 4',
            '5 РУ': 'РУ 5',
            '5 МА': 'МА 5'
        }
        
        for col, label in subject_map.items():
            if col in row.index and pd.notna(row[col]) and row[col] > 0:
                count = int(row[col])
                subjects.append(f"{label} ({count})")
        
        markers = int(row['Количество маркеров']) if pd.notna(row['Количество маркеров']) else 0
        
        if markers > 0:
            result['biased_schools_list'].append({
                'name': row['ОО'],
                'markers': markers,
                'subjects': ', '.join(subjects) if subjects else 'Нет данных'
            })
    
    return result

# ============================================================================
# ФУНКЦИИ ПОСТРОЕНИЯ ГРАФИКОВ - ИСПРАВЛЕНО
# ============================================================================

def create_marks_chart(data: pd.DataFrame) -> go.Figure:
    """
    Создает столбчатую диаграмму распределения оценок.
    ИСПРАВЛЕНО: Убраны десятичные дроби из подписей оценок.
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Нет данных для отображения",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    # Цветовая палитра Material Design
    colors = ['#EF5350', '#FFA726', '#66BB6A', '#42A5F5']
    
    fig = go.Figure()
    
    for i, row in data.iterrows():
        fig.add_trace(go.Bar(
            x=[str(int(float(row['Оценка'])))],  # ИСПРАВЛЕНО: форматируем как целое число
            y=[row['Процент']],
            name=str(int(float(row['Оценка']))),
            marker=dict(
                color=colors[i],
                line=dict(color='rgba(0,0,0,0.2)', width=1)
            ),
            text=[f"{row['Процент']:.1f}%"],
            textposition='outside',
            textfont=dict(size=14, color='#FAFAFA'),
            hovertemplate='<b>Оценка %{x}</b><br>Процент: %{y:.2f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title=None,
        xaxis=dict(
            title='Оценка',
            showgrid=False,
            zeroline=False,
            color='#FAFAFA',
            type='category'  # ИСПРАВЛЕНО: категориальная ось
        ),
        yaxis=dict(
            title='Процент учащихся (%)',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False,
            color='#FAFAFA'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=400,
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(family="sans-serif", color='#FAFAFA')
    )
    
    return fig

def create_scores_chart(data: pd.DataFrame) -> go.Figure:
    """
    Создает график распределения первичных баллов.
    ИСПРАВЛЕНО: Правильное отображение оси X с 0 и максимальным баллом.
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Нет данных для отображения",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    # Определяем максимальный балл
    max_score = int(data['Балл'].max())
    min_score = 0  # Всегда начинаем с 0
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data['Балл'].astype(int),
        y=data['Процент'],
        marker=dict(
            color='#42A5F5',
            line=dict(color='rgba(0,0,0,0.2)', width=1)
        ),
        hovertemplate='<b>Балл %{x}</b><br>Процент: %{y:.2f}%<extra></extra>'
    ))
    
    # Создаем список подписей для оси X
    # Показываем все значения, но выделяем 0 и максимум
    all_scores = list(range(min_score, max_score + 1))
    
    fig.update_layout(
        title=None,
        xaxis=dict(
            title='Первичный балл',
            showgrid=False,
            zeroline=False,
            color='#FAFAFA',
            tickmode='linear',
            tick0=0,
            dtick=1,
            range=[-0.5, max_score + 0.5]
        ),
        yaxis=dict(
            title='Процент учащихся (%)',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False,
            color='#FAFAFA'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=400,
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(family="sans-serif", color='#FAFAFA')
    )
    
    return fig

def create_bias_trend_chart(municipality_stats: List[Dict]) -> go.Figure:
    """
    Создает график динамики необъективности за 3 года.
    ИСПРАВЛЕНО: Убраны десятичные дроби из подписей годов.
    """
    if not municipality_stats:
        fig = go.Figure()
        fig.add_annotation(
            text="Нет данных для отображения",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    # Сортируем по годам
    sorted_stats = sorted(municipality_stats, key=lambda x: x['year'])
    
    years = [str(int(s['year'])) for s in sorted_stats]  # ИСПРАВЛЕНО: форматируем как целые числа
    percentages = [s['percentage'] for s in sorted_stats]
    
    # Цвета: последний год - оранжевый, остальные - серые
    colors = ['#B0BEC5'] * (len(years) - 1) + ['#FF6B35']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=percentages,
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.2)', width=1)
        ),
        text=[f"{p:.1f}%" for p in percentages],
        textposition='outside',
        textfont=dict(size=14, color='#FAFAFA'),
        hovertemplate='<b>%{x} год</b><br>Процент: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=None,
        xaxis=dict(
            title='Год',
            showgrid=False,
            zeroline=False,
            color='#FAFAFA',
            type='category'  # ИСПРАВЛЕНО: категориальная ось
        ),
        yaxis=dict(
            title='Процент ОО (%)',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False,
            color='#FAFAFA',
            range=[0, max(percentages) * 1.2 if percentages else 100]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=300,
        margin=dict(l=40, r=40, t=20, b=40),
        font=dict(family="sans-serif", color='#FAFAFA')
    )
    
    return fig

# ============================================================================
# КОМПОНЕНТЫ UI
# ============================================================================

def render_loading_animation():
    """
    Отображает анимацию загрузки данных.
    """
    st.markdown("""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">Загрузка данных...</div>
    </div>
    """, unsafe_allow_html=True)

def render_header():
    """
    Отображает заголовок приложения.
    """
    st.markdown("""
    <div class="app-header">
        <div>
            <h1 class="app-title">📊 АНАЛИЗ РЕЗУЛЬТАТОВ ВПР</h1>
            <p class="app-subtitle">МОНИТОРИНГ ОЦЕНКИ КАЧЕСТВА ОБРАЗОВАНИЯ</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(icon: str, label: str, value: str, subtitle: str):
    """
    Отображает карточку с метрикой.
    """
    st.markdown(f"""
    <div class="metric-card">
        <span class="metric-icon">{icon}</span>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def render_bias_school_card(bias_data: Dict, school_name: str, selected_year: int):
    """
    Отображает карточку с информацией о маркерах конкретной школы.
    """
    markers = bias_data['school_markers']
    subjects = ', '.join(bias_data['school_subjects']) if bias_data['school_subjects'] else 'Нет маркеров'
    in_bias_3y = "✓ Да" if bias_data['school_in_bias_3years'] else "✗ Нет"
    
    marker_text = f"Количество маркеров: {markers}"
    if markers > 0:
        marker_text += f"<br><span class='bias-subjects'>{subjects}</span>"
    
    st.markdown(f"""
    <div class="metric-card">
        <span class="metric-icon">🏫</span>
        <div class="metric-label">АНАЛИЗ ВЫБРАННОЙ ШКОЛЫ ({selected_year})</div>
        <div class="metric-value">{markers}</div>
        <div class="metric-subtitle">{marker_text}</div>
        <div class="metric-subtitle" style="margin-top: 0.5rem;">
            <strong>В списке необъективных за 3 года:</strong> {in_bias_3y}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ОСНОВНОЕ ПРИЛОЖЕНИЕ
# ============================================================================

def main():
    """
    Главная функция приложения.
    """
    
    # Показываем анимацию загрузки
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        render_loading_animation()
    
    # Загружаем данные
    marks_df, scores_df, bias_df = load_data()
    filter_options = get_filter_options(marks_df)
    
    # Убираем анимацию загрузки
    time.sleep(0.5)
    loading_placeholder.empty()
    
    # Заголовок
    render_header()
    
    # ========================================================================
    # ЛИПКИЙ ХЕДЕР С ФИЛЬТРАМИ - ИСПРАВЛЕНО
    # ========================================================================
    
    # Создаем контейнер для липкого хедера
    st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        selected_year = st.selectbox(
            '📅 ГОД',
            options=filter_options['years'],
            key='year_filter',
            format_func=lambda x: str(int(x))  # ИСПРАВЛЕНО: отображаем как целое число
        )
    
    with col2:
        selected_class = st.selectbox(
            '🎓 КЛАСС',
            options=filter_options['classes'],
            key='class_filter',
            format_func=lambda x: str(int(x))  # ИСПРАВЛЕНО: отображаем как целое число
        )
    
    with col3:
        # Фильтруем предметы по выбранному году и классу
        available_subjects = sorted(marks_df[
            (marks_df['Год'] == selected_year) &
            (marks_df['Класс'] == selected_class)
        ]['Предмет'].unique())
        
        selected_subject = st.selectbox(
            '📚 ПРЕДМЕТ',
            options=available_subjects,
            key='subject_filter'
        )
    
    with col4:
        selected_municipality = st.selectbox(
            '🏛️ МУНИЦИПАЛИТЕТ',
            options=filter_options['municipalities'],
            key='municipality_filter'
        )
    
    with col5:
        # Фильтруем школы по выбранному муниципалитету
        if selected_municipality == 'Все':
            available_schools = ['Все'] + sorted(
                marks_df[
                    (marks_df['Год'] == selected_year) &
                    (marks_df['Класс'] == selected_class) &
                    (marks_df['Предмет'] == selected_subject)
                ]['ОО'].unique()
            )
        else:
            available_schools = ['Все'] + sorted(
                marks_df[
                    (marks_df['Год'] == selected_year) &
                    (marks_df['Класс'] == selected_class) &
                    (marks_df['Предмет'] == selected_subject) &
                    (marks_df['Муниципалитет'] == selected_municipality)
                ]['ОО'].unique()
            )
        
        selected_school = st.selectbox(
            '🏫 ОРГАНИЗАЦИЯ (ОО)',
            options=available_schools,
            key='school_filter'
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # ФИЛЬТРАЦИЯ ДАННЫХ
    # ========================================================================
    
    filtered_marks = marks_df[
        (marks_df['Год'] == selected_year) &
        (marks_df['Класс'] == selected_class) &
        (marks_df['Предмет'] == selected_subject)
    ].copy()
    
    if selected_municipality != 'Все':
        filtered_marks = filtered_marks[
            filtered_marks['Муниципалитет'] == selected_municipality
        ]
    
    if selected_school != 'Все':
        filtered_marks = filtered_marks[
            filtered_marks['ОО'] == selected_school
        ]
    
    # ========================================================================
    # КАРТОЧКИ МЕТРИК
    # ========================================================================
    
    metrics = calculate_metrics(filtered_marks)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        schools_text = "Все муниципалитеты" if selected_municipality == 'Все' else selected_municipality
        render_metric_card(
            icon="🏫",
            label="ВЫБРАННЫХ ОО",
            value=f"{metrics['schools']}",
            subtitle=schools_text
        )
    
    with col2:
        render_metric_card(
            icon="👥",
            label="УЧАСТНИКОВ",
            value=f"{metrics['participants']:,}".replace(',', ' '),
            subtitle="Человек приняло участие"
        )
    
    with col3:
        render_metric_card(
            icon="✅",
            label="УСПЕВАЕМОСТЬ",
            value=f"{metrics['success_rate']:.1f}%",
            subtitle="Доля оценок 3, 4 и 5"
        )
    
    with col4:
        render_metric_card(
            icon="📈",
            label="КАЧЕСТВО (4+5)",
            value=f"{metrics['quality_rate']:.1f}%",
            subtitle="Доля оценок 4 и 5"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # ГРАФИКИ РАСПРЕДЕЛЕНИЯ
    # ========================================================================
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Распределение отметок (%)</div>', unsafe_allow_html=True)
        
        marks_dist = get_marks_distribution(filtered_marks)
        marks_chart = create_marks_chart(marks_dist)
        st.plotly_chart(marks_chart, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Распределение первичных баллов (%)</div>', unsafe_allow_html=True)
        
        scores_dist = get_scores_distribution(
            scores_df, selected_year, selected_class, 
            selected_subject, selected_municipality, selected_school
        )
        scores_chart = create_scores_chart(scores_dist)
        st.plotly_chart(scores_chart, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # ПРИЗНАКИ НЕОБЪЕКТИВНОСТИ
    # ========================================================================
    
    st.markdown('<div class="section-title" style="margin-top: 2rem;">⚠️ ПРИЗНАКИ НЕОБЪЕКТИВНОСТИ</div>', unsafe_allow_html=True)
    
    # Получаем данные по необъективности
    bias_data = get_bias_data(bias_df, marks_df, selected_year, selected_municipality, selected_school)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Карточка для конкретной школы
        if selected_school != 'Все':
            render_bias_school_card(bias_data, selected_school, selected_year)
        else:
            st.markdown("""
            <div class="metric-card">
                <span class="metric-icon">ℹ️</span>
                <div class="metric-label">АНАЛИЗ ВЫБРАННОЙ ШКОЛЫ</div>
                <div class="metric-subtitle" style="padding: 2rem 0;">
                    Выберите конкретную школу для детального анализа маркеров необъективности
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Карточка с динамикой по муниципалитету
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<span class="metric-icon">📊</span>', unsafe_allow_html=True)
        
        municipality_text = selected_municipality if selected_municipality != 'Все' else 'по всем муниципалитетам'
        st.markdown(f'<div class="metric-label">ДОЛЯ ОО С ПРИЗНАКАМИ НЕОБЪЕКТИВНОСТИ (%) {municipality_text.upper()}</div>', unsafe_allow_html=True)
        
        bias_chart = create_bias_trend_chart(bias_data['municipality_stats'])
        st.plotly_chart(bias_chart, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # СПИСОК ОО С МАРКЕРАМИ
    # ========================================================================
    
    if bias_data['biased_schools_list']:
        st.markdown(f'<div class="section-title" style="margin-top: 2rem;">📋 СПИСОК ОО РЕГИОНА С МАРКЕРАМИ НЕОБЪЕКТИВНОСТИ ({selected_year})</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        
        # Заголовок таблицы
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; padding: 0.75rem; border-bottom: 2px solid #FF6B35; margin-bottom: 1rem;">
            <div style="flex: 1; font-weight: 600; color: #FF6B35;">НАИМЕНОВАНИЕ ОРГАНИЗАЦИИ</div>
            <div style="width: 120px; text-align: center; font-weight: 600; color: #FF6B35;">МАРКЕРОВ</div>
            <div style="width: 200px; text-align: center; font-weight: 600; color: #FF6B35;">ДИСЦИПЛИНЫ</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Строки таблицы
        for school in sorted(bias_data['biased_schools_list'], key=lambda x: x['markers'], reverse=True):
            st.markdown(f"""
            <div class="bias-school-row">
                <div class="bias-school-name">{school['name']}</div>
                <div style="width: 120px; text-align: center;">
                    <span class="bias-badge">{school['markers']}</span>
                </div>
                <div class="bias-subjects" style="width: 200px; text-align: center;">{school['subjects']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="section-title" style="margin-top: 2rem;">📋 СПИСОК ОО РЕГИОНА С МАРКЕРАМИ НЕОБЪЕКТИВНОСТИ ({selected_year})</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: rgba(250, 250, 250, 0.5);">
            ✓ В выбранном муниципалитете нет школ с признаками необъективности
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: rgba(250, 250, 250, 0.4); font-size: 0.85rem; padding: 2rem 0;">
        Разработано для анализа результатов Всероссийских проверочных работ
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

if __name__ == "__main__":
    main()
