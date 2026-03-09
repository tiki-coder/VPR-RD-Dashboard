import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple
import time

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
        padding-top: 2rem;
    }
    
    /* Липкий хедер с фильтрами */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: var(--background-color);
        padding: 1rem 0 2rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid rgba(250, 250, 250, 0.1);
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
    }
    
    /* Скрыть индексы строк в dataframe */
    .dataframe tbody tr th {
        display: none;
    }
    
    /* Стили для selectbox */
    .stSelectbox > div > div {
        background-color: rgba(30, 33, 39, 0.8);
        border-radius: 8px;
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
                'Год': 'int16',
                'Класс': 'int8',
                'Предмет': 'category',
                'Муниципалитет': 'category',
                'Логин': 'category',
                'ОО': 'string',
                'Кол-во участников': 'int32'
            }
        )
        
        scores = pd.read_excel(
            'scores.xlsx',
            engine='openpyxl',
            dtype={
                'Год': 'int16',
                'Класс': 'int8',
                'Предмет': 'category',
                'Муниципалитет': 'category',
                'Логин': 'category',
                'ОО': 'string',
                'Кол-во участников': 'int32'
            }
        )
        
        bias = pd.read_excel(
            'bias.xlsx',
            engine='openpyxl',
            dtype={
                'Год': 'int16',
                'Логин': 'category',
                'Муниципалитет': 'category',
                'ОО': 'string'
            }
        )
        
        # Очистка названий столбцов от лишних пробелов
        marks.columns = marks.columns.str.strip()
        scores.columns = scores.columns.str.strip()
        bias.columns = bias.columns.str.strip()
        
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
# ФУНКЦИИ РАСЧЕТА МЕТРИК
# ============================================================================

def calculate_metrics(filtered_data: pd.DataFrame) -> Dict[str, float]:
    """
    Рассчитывает метрики: количество ОО, участников, успеваемость и качество.
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
    total_participants = filtered_data['Кол-во участников'].sum()
    
    # Расчет успеваемости (доля оценок 3, 4, 5)
    success_rate = (
        filtered_data['3'].sum() + 
        filtered_data['4'].sum() + 
        filtered_data['5'].sum()
    ) / 100  # Делим на 100, т.к. в данных проценты
    
    # Расчет качества (доля оценок 4, 5)
    quality_rate = (
        filtered_data['4'].sum() + 
        filtered_data['5'].sum()
    ) / 100
    
    return {
        'schools': schools_count,
        'participants': total_participants,
        'success_rate': success_rate / len(filtered_data) if len(filtered_data) > 0 else 0,
        'quality_rate': quality_rate / len(filtered_data) if len(filtered_data) > 0 else 0
    }

def get_marks_distribution(filtered_data: pd.DataFrame) -> pd.DataFrame:
    """
    Получает распределение оценок для построения графика.
    """
    if filtered_data.empty:
        return pd.DataFrame()
    
    # Суммируем проценты по всем оценкам
    marks_sum = filtered_data[['2', '3', '4', '5']].sum()
    
    # Нормализуем на количество школ
    marks_avg = marks_sum / len(filtered_data)
    
    result = pd.DataFrame({
        'Оценка': ['2', '3', '4', '5'],
        'Процент': marks_avg.values
    })
    
    return result

def get_scores_distribution(scores_data: pd.DataFrame, year: int, class_num: int, 
                            subject: str, municipality: str, school: str) -> pd.DataFrame:
    """
    Получает распределение первичных баллов.
    """
    # Фильтрация данных
    filtered = scores_data[
        (scores_data['Год'] == year) &
        (scores_data['Класс'] == class_num) &
        (scores_data['Предмет'] == subject)
    ]
    
    if municipality != 'Все':
        filtered = filtered[filtered['Муниципалитет'] == municipality]
    
    if school != 'Все':
        filtered = filtered[filtered['ОО'] == school]
    
    if filtered.empty:
        return pd.DataFrame()
    
    # Определяем колонки с баллами (все числовые колонки после основных)
    score_columns = [col for col in filtered.columns if col.isdigit()]
    
    # Суммируем проценты по каждому баллу
    scores_sum = filtered[score_columns].sum()
    
    # Нормализуем на количество школ
    scores_avg = scores_sum / len(filtered)
    
    result = pd.DataFrame({
        'Балл': [int(col) for col in score_columns],
        'Процент': scores_avg.values
    })
    
    return result.sort_values('Балл')

def get_bias_data(bias_df: pd.DataFrame, year: int, municipality: str, 
                  school: str) -> Dict:
    """
    Получает данные по необъективности для выбранной школы и муниципалитета.
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
            (bias_df['ОО'] == school)
        ]
        
        if not school_bias.empty:
            result['school_markers'] = int(school_bias['Количество маркеров'].iloc[0])
            
            # Определяем предметы с маркерами
            subjects_with_markers = []
            row = school_bias.iloc[0]
            
            if pd.notna(row.get('4 РУ')) and row.get('4 РУ') > 0:
                subjects_with_markers.append('РУ 4')
            if pd.notna(row.get('4 МА')) and row.get('4 МА') > 0:
                subjects_with_markers.append('МА 4')
            if pd.notna(row.get('5 РУ')) and row.get('5 РУ') > 0:
                subjects_with_markers.append('РУ 5')
            if pd.notna(row.get('5 МА')) and row.get('5 МА') > 0:
                subjects_with_markers.append('МА 5')
            
            result['school_subjects'] = subjects_with_markers
        
        # Проверка попадания школы в необъективность за последние 3 года
        school_bias_3years = bias_df[
            (bias_df['Год'].isin([year, year-1, year-2])) &
            (bias_df['ОО'] == school)
        ]
        result['school_in_bias_3years'] = len(school_bias_3years) > 0
    
    # 2. Статистика по муниципалитету за 3 года
    for y in [year, year-1, year-2]:
        year_bias = bias_df[bias_df['Год'] == y]
        
        if municipality != 'Все':
            year_bias = year_bias[year_bias['Муниципалитет'] == municipality]
        
        # Количество школ с маркерами
        schools_with_bias = year_bias['Логин'].nunique()
        
        # Общее количество школ (из данных по русскому языку 4 класс)
        # Эту информацию нужно получить из marks
        result['municipality_stats'].append({
            'year': y,
            'biased_schools': schools_with_bias,
            'total_schools': 0  # Заполнится позже
        })
    
    # 3. Список школ с маркерами в текущем году
    year_bias = bias_df[bias_df['Год'] == year]
    
    if municipality != 'Все':
        year_bias = year_bias[year_bias['Муниципалитет'] == municipality]
    
    for _, row in year_bias.iterrows():
        subjects = []
        if pd.notna(row.get('4 РУ')) and row.get('4 РУ') > 0:
            subjects.append(f"РУ 4 ({int(row['4 РУ'])})")
        if pd.notna(row.get('4 МА')) and row.get('4 МА') > 0:
            subjects.append(f"МА 4 ({int(row['4 МА'])})")
        if pd.notna(row.get('5 РУ')) and row.get('5 РУ') > 0:
            subjects.append(f"РУ 5 ({int(row['5 РУ'])})")
        if pd.notna(row.get('5 МА')) and row.get('5 МА') > 0:
            subjects.append(f"МА 5 ({int(row['5 МА'])})")
        
        result['biased_schools_list'].append({
            'name': row['ОО'],
            'markers': int(row['Количество маркеров']),
            'subjects': ', '.join(subjects)
        })
    
    return result

def fill_total_schools(bias_data: Dict, marks_df: pd.DataFrame, 
                       municipality: str) -> Dict:
    """
    Заполняет информацию об общем количестве школ для расчета процента необъективности.
    """
    for stat in bias_data['municipality_stats']:
        year = stat['year']
        
        # Фильтруем marks по году, 4 классу и русскому языку
        year_marks = marks_df[
            (marks_df['Год'] == year) &
            (marks_df['Класс'] == 4) &
            (marks_df['Предмет'].str.contains('Русский язык', case=False, na=False))
        ]
        
        if municipality != 'Все':
            year_marks = year_marks[year_marks['Муниципалитет'] == municipality]
        
        stat['total_schools'] = year_marks['Логин'].nunique()
        
        # Рассчитываем процент
        if stat['total_schools'] > 0:
            stat['percentage'] = (stat['biased_schools'] / stat['total_schools']) * 100
        else:
            stat['percentage'] = 0
    
    return bias_data

# ============================================================================
# ФУНКЦИИ ПОСТРОЕНИЯ ГРАФИКОВ
# ============================================================================

def create_marks_chart(data: pd.DataFrame) -> go.Figure:
    """
    Создает столбчатую диаграмму распределения оценок с Material Design стилистикой.
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
            x=[row['Оценка']],
            y=[row['Процент']],
            name=row['Оценка'],
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
            color='#FAFAFA'
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
    max_score = data['Балл'].max()
    min_score = data['Балл'].min()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data['Балл'],
        y=data['Процент'],
        marker=dict(
            color='#42A5F5',
            line=dict(color='rgba(0,0,0,0.2)', width=1)
        ),
        hovertemplate='<b>Балл %{x}</b><br>Процент: %{y:.2f}%<extra></extra>'
    ))
    
    # Настройка оси X с обязательным отображением 0 и максимального балла
    tickvals = list(range(min_score, max_score + 1))
    
    # Убедимся, что 0 и max отображаются
    if 0 not in tickvals:
        tickvals = [0] + tickvals
    if max_score not in tickvals:
        tickvals.append(max_score)
    
    fig.update_layout(
        title=None,
        xaxis=dict(
            title='Первичный балл',
            showgrid=False,
            zeroline=False,
            color='#FAFAFA',
            tickmode='array',
            tickvals=tickvals,
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
    
    years = [str(s['year']) for s in sorted_stats]
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
            color='#FAFAFA'
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

def render_bias_school_card(bias_data: Dict, school_name: str):
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
        <div class="metric-label">АНАЛИЗ ВЫБРАННОЙ ШКОЛЫ ({bias_data.get('school_year', '')})</div>
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
    time.sleep(0.5)  # Небольшая задержка для плавности
    loading_placeholder.empty()
    
    # Заголовок
    render_header()
    
    # ========================================================================
    # ЛИПКИЙ ХЕДЕР С ФИЛЬТРАМИ
    # ========================================================================
    
    header_container = st.container()
    with header_container:
        st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            selected_year = st.selectbox(
                '📅 ГОД',
                options=filter_options['years'],
                key='year_filter'
            )
        
        with col2:
            selected_class = st.selectbox(
                '🎓 КЛАСС',
                options=filter_options['classes'],
                key='class_filter'
            )
        
        with col3:
            # Фильтруем предметы по выбранному году и классу
            available_subjects = marks_df[
                (marks_df['Год'] == selected_year) &
                (marks_df['Класс'] == selected_class)
            ]['Предмет'].unique()
            
            selected_subject = st.selectbox(
                '📚 ПРЕДМЕТ',
                options=sorted(available_subjects),
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
    ]
    
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
    bias_data = get_bias_data(bias_df, selected_year, selected_municipality, selected_school)
    bias_data = fill_total_schools(bias_data, marks_df, selected_municipality)
    bias_data['school_year'] = selected_year
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Карточка для конкретной школы
        if selected_school != 'Все':
            render_bias_school_card(bias_data, selected_school)
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
        for school in bias_data['biased_schools_list']:
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
