import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

# 2. 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)
    
    # '날짜' 열을 YYYYMMDD 형태에서 실제 datetime 날짜 객체로 변환
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    
    # 수치 데이터 형변환
    numeric_cols = ['순위', '일관객', '누적관객', '스크린수', '상영횟수']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

df = load_data()

# 3. 앱 타이틀 및 헤더
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 데이터를 활용하여 시간에 따른 관객수 및 영화 동향을 시각화합니다.")
st.markdown("---")

# 사이드바 데이터 요약
with st.sidebar:
    st.header("📊 데이터 정보")
    st.write(f"- **총 데이터 수**: {len(df):,}건")
    if not df.empty:
        st.write(f"- **조회 기간**: {df['날짜'].min().strftime('%Y-%m-%d')} ~ {df['날짜'].max().strftime('%Y-%m-%d')}")
        st.write(f"- **포함된 영화 수**: {df['영화명'].nunique():,}개")

# ==============================================================================
# [구역 1] 단일 영화 날짜별 일관객 변화
# ==============================================================================
st.subheader("📌 구역 1: 단일 영화 날짜별 일관객 변화")

# 영화 목록 추출 (누적 관객수가 높은 순으로 정렬)
movie_list = df.groupby('영화명')['누적관객'].max().sort_values(ascending=False).index.tolist()

# 드롭다운 영화 선택
selected_movie = st.selectbox(
    "영화를 선택하세요:",
    options=movie_list,
    index=0
)

# 선택된 영화 데이터 필터링 및 날짜순 정렬
movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')

if not movie_df.empty:
    # 플롯리 선 그래프 생성
    fig = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"<b>[{selected_movie}]</b> 날짜별 일관객 수 변화",
        labels={'날짜': '날짜', '일관객': '일관객 수(명)'},
        markers=True
    )
    
    # 마우스 오버 시 날짜, 일관객, 순위, 상영횟수가 보이도록 설정
    fig.update_traces(
        mode='lines+markers',
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<br><b>순위:</b> %{customdata[0]}위<br><b>상영횟수:</b> %{customdata[1]:,}회<extra></extra>",
        customdata=movie_df[['순위', '상영횟수']],
        line=dict(color='#3366CC', width=2.5),
        marker=dict(size=6)
    )
    
    fig.update_layout(
        hovermode="x unified",
        template="plotly_white",
        height=450,
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True, tickformat=","),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    # 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # 문구 입력용 자리
    st.info("💡 **이 그래프로 알 수 있는 것**\n\n*(작성할 문구를 입력하세요)*")
else:
    st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

st.markdown("---")

# ==============================================================================
# [구역 2] 기간 내 일관객 합계 TOP 5 영화의 날짜별 일관객 변화
# ==============================================================================
st.subheader("📌 구역 2: 기간 내 일관객 합계 TOP 5 영화 비교")

# 일관객 합계 기준 TOP 5 영화 추출
top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()

# TOP 5 영화 데이터 필터링
top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')

if not top5_df.empty:
    # 플롯리 선 그래프 생성 (영화별 색상 구분)
    fig2 = px.line(
        top5_df,
        x='날짜',
        y='일관객',
        color='영화명',
        title="<b>기간 내 일관객 합계 TOP 5 영화의 날짜별 일관객 수 비교</b>",
        labels={'날짜': '날짜', '일관객': '일관객 수(명)', '영화명': '영화 제목'},
        markers=True
    )
    
    # 마우스 오버 및 범례 설정
    fig2.update_traces(
        mode='lines+markers',
        hovertemplate="<b>영화:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>",
        marker=dict(size=5)
    )
    
    fig2.update_layout(
        hovermode="x unified",
        template="plotly_white",
        height=500,
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True, tickformat=","),
        legend=dict(
            title="영화를 클릭하여 On/Off",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # 그래프 출력
    st.plotly_chart(fig2, use_container_width=True)

    # 문구 입력용 자리
    st.info("💡 **이 그래프로 알 수 있는 것**\n\n*(작성할 문구를 입력하세요)*")
else:
    st.warning("TOP 5 영화 데이터를 불러올 수 없습니다.")

st.markdown("---")

# ==============================================================================
# [구역 3] 날짜별 10위권 일관객 합계 영역 그래프
# ==============================================================================
st.subheader("📌 구역 3: 날짜별 10위권 일관객 합계 동향")

# 날짜별 일관객 합계 계산
daily_sum = df.groupby('날짜')['일관객'].sum().reset_index().sort_values('날짜')

if not daily_sum.empty:
    # 영역 그래프 생성
    fig3 = px.area(
        daily_sum,
        x='날짜',
        y='일관객',
        title="<b>날짜별 10위권 일관객 합계 변화 및 최다 관객 Top 3일</b>",
        labels={'날짜': '날짜', '일관객': '10위권 총 관객 수(명)'}
    )
    
    # 그래프 스타일링
    fig3.update_traces(
        line=dict(color='#2E86C1', width=2),
        fillcolor='rgba(46, 134, 193, 0.3)',
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>10위권 총 관객:</b> %{y:,}명<extra></extra>"
    )
    
    # 관객 수가 가장 컸던 Top 3일 추출
    top3_days = daily_sum.nlargest(3, '일관객').sort_values('날짜')
    
    # Top 3일 포인트 강조 (마커 추가)
    fig3.add_trace(
        go.Scatter(
            x=top3_days['날짜'],
            y=top3_days['일관객'],
            mode='markers+text',
            name='Top 3일',
            marker=dict(color='#E74C3C', size=10, symbol='diamond'),
            text=[d.strftime('%Y-%m-%d') for d in top3_days['날짜']],
            textposition='top center',
            hovertemplate="<b>🏆 Top 3 날짜:</b> %{x|%Y-%m-%d}<br><b>총 관객:</b> %{y:,}명<extra></extra>",
            showlegend=False
        )
    )
    
    # 주석(Annotations)으로 Top 3 강조 표기
    for _, row in top3_days.iterrows():
        date_str = row['날짜'].strftime('%Y-%m-%d')
        fig3.add_annotation(
            x=row['날짜'],
            y=row['일관객'],
            text=f"<b>{date_str}</b><br>({row['일관객']:,}명)",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor="#E74C3C",
            ax=0,
            ay=-40,
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="#E74C3C",
            borderwidth=1.5,
            borderpad=4,
            font=dict(size=11, color="#900C3F")
        )
    
    fig3.update_layout(
        hovermode="x unified",
        template="plotly_white",
        height=500,
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True, tickformat=","),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # 그래프 출력
    st.plotly_chart(fig3, use_container_width=True)

    # 문구 입력용 자리
    st.info("💡 **이 그래프로 알 수 있는 것**\n\n*(작성할 문구를 입력하세요)*")
else:
    st.warning("데이터를 불러올 수 없습니다.")

st.markdown("---")

# ==============================================================================
# [구역 4] 기간 내 일관객 합계 TOP 10 영화 가로 막대그래프
# ==============================================================================
st.subheader("📌 구역 4: 기간 내 일관객 합계 TOP 10 영화")

# 영화별 일관객 합계 및 10위권 진입 일수(데이터 행 수) 집계
top10_df = (
    df.groupby('영화명')
    .agg(
        총일관객=('일관객', 'sum'),
        진입일수=('날짜', 'nunique')
    )
    .reset_index()
    .nlargest(10, '총일관객')
    .sort_values('총일관객', ascending=True)  # Plotly 가로 막대는 아래서부터 그려지므로 ascending=True로 놓아야 1위가 상단에 위치함
)

if not top10_df.empty:
    # 가로 막대그래프 생성
    fig4 = px.bar(
        top10_df,
        x='총일관객',
        y='영화명',
        orientation='h',
        title="<b>기간 내 일관객 합계 TOP 10 영화 및 10위권 진입 일수</b>",
        labels={'총일관객': '총 일관객 수(명)', '영화명': '영화 제목', '진입일수': '10위권 진입 일수'},
        text='총일관객',
        color='총일관객',
        color_continuous_scale='Blues'
    )
    
    # 막대에 마우스 올렸을 때 보여줄 정보(툴팁) 및 막대 텍스트 설정
    fig4.update_traces(
        texttemplate='%{x:,}명',
        textposition='outside',
        hovertemplate="<b>영화명:</b> %{y}<br><b>총 일관객:</b> %{x:,}명<br><b>10위권 진입 일수:</b> %{customdata[0]}일<extra></extra>",
        customdata=top10_df[['진입일수']]
    )
    
    fig4.update_layout(
        template="plotly_white",
        height=500,
        xaxis=dict(showgrid=True, tickformat=","),
        yaxis=dict(title=""),
        coloraxis_showscale=False,  # 컬러바 숨김
        margin=dict(l=20, r=50, t=60, b=20)
    )
    
    # 그래프 출력
    st.plotly_chart(fig4, use_container_width=True)

    # 문구 입력용 자리
    st.info("💡 **이 그래프로 알 수 있는 것**\n\n*(작성할 문구를 입력하세요)*")
else:
    st.warning("데이터를 불러올 수 없습니다.")

st.markdown("---")

# ==============================================================================
# [구역 5] 그래프 추가 구역 (확장용)
# ==============================================================================
st.subheader("📌 구역 5: (그래프 추가 예정 구역)")
st.caption("향후 시간에 따른 영화 데이터를 시각화하는 그래프가 추가될 위치입니다.")

# 임시 시각화 자리
st.write("*(그래프 들어갈 자리)*")

# 문구 입력용 자리
st.info("💡 **이 그래프로 알 수 있는 것**\n\n*(작성할 문구를 입력하세요)*")
