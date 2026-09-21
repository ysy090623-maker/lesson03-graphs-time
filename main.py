"""
영화 데이터 그래프 도감 1 - 시간

- 데이터 출처: https://github.com/greatsong/modudata
  (KOBIS 일별 박스오피스 10위권, 1년치)
- 앞으로 그래프를 계속 추가할 예정이라, 구역(section)을 나누어 둔다.
  새 그래프를 추가할 때는 "## 구역 2" 같은 새 구역을 아래에 이어서 쓰면 된다.
"""

# ── 1. 필요한 도구(라이브러리) 불러오기 ────────────────────────────────
import pandas as pd                # 표(테이블)를 다루는 도구
import plotly.express as px        # 마우스를 올리면 값이 보이는 그래프를 그리는 도구
import streamlit as st             # 화면(웹 앱)을 만드는 도구


# ── 2. 고정값 ──────────────────────────────────────────────────────────
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/"
    "kobis_daily.csv"
)


# ── 3. 자료 불러오기 ───────────────────────────────────────────────────
# @st.cache_data 를 붙이면, 앱을 새로고침해도 인터넷에서 자료를 매번
# 다시 받지 않고 저장해 둔 걸 그대로 쓴다. (자료가 자주 안 바뀌니 효율적이다.)
@st.cache_data(show_spinner="영화 자료를 불러오는 중입니다...")
def load_data() -> pd.DataFrame:
    """CSV를 읽어서, 날짜 열을 진짜 날짜 형식으로 바꿔 돌려준다."""
    df = pd.read_csv(DATA_URL)

    # 날짜 열은 "20250901"처럼 하이픈 없는 여덟 자리 숫자로 되어 있다.
    # format="%Y%m%d" 로 알려 주면 진짜 날짜(datetime) 형식으로 바뀐다.
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")

    return df


# ── 4. 화면 그리기 ─────────────────────────────────────────────────────
st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", page_icon="📈", layout="wide")

st.title("📈 영화 데이터 그래프 도감 1 - 시간")
st.caption("자료 출처: KOBIS 일별 박스오피스 10위권 (1년치) · github.com/greatsong/modudata")

df = load_data()

st.divider()

# ══════════════════════════════════════════════════════════════════════
# 구역 1. 영화 한 편의 시간에 따른 일관객 변화
# ══════════════════════════════════════════════════════════════════════
st.header("구역 1 · 영화 한 편의 관객수 변화")

# 드롭다운에 넣을 영화 이름 목록 (가나다순으로 정렬해서 찾기 쉽게)
movie_names = sorted(df["영화명"].unique())

selected_movie = st.selectbox("영화를 골라 보세요", movie_names)

# 고른 영화의 기록만 뽑아서 날짜 순서로 정렬
movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

# 플롯리 선 그래프: x축은 날짜, y축은 일관객.
fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,  # 각 날짜에 점을 찍어서 더 잘 보이게
    labels={"날짜": "날짜", "일관객": "일일 관객수"},
    title=f"{selected_movie} · 날짜별 일일 관객수",
)
# 마우스를 올리면 날짜와 관객수가 보이도록 hover 내용을 직접 지정
fig.update_traces(hovertemplate="날짜: %{x|%Y-%m-%d}<br>관객수: %{y:,}명<extra></extra>")
fig.update_layout(yaxis_tickformat=",")  # y축 눈금도 1,000 단위 쉼표로

st.plotly_chart(fig, use_container_width=True)

# 그래프 아래 "이 그래프로 알 수 있는 것" 한 문장을 적을 자리.
# 지금은 빈 자리이고, 나중에 영화별로 직접 채워 넣으면 된다.
st.info("**이 그래프로 알 수 있는 것:** _(여기에 한 문장을 적어 주세요)_")

st.divider()

# ══════════════════════════════════════════════════════════════════════
# 구역 2. 일관객 합계 상위 5편 비교
# ══════════════════════════════════════════════════════════════════════
st.header("구역 2 · 관객수 상위 5편 비교")

# 영화명으로 묶어서 일관객을 다 더한 뒤, 가장 큰 5편을 고른다.
total_by_movie = df.groupby("영화명")["일관객"].sum().sort_values(ascending=False)
top5_names = total_by_movie.head(5).index.tolist()

# 상위 5편의 기록만 뽑아서 날짜 순서로 정렬
top5_df = df[df["영화명"].isin(top5_names)].sort_values("날짜")

# color="영화명" 을 주면 영화마다 다른 색 선이 그려지고,
# 범례(legend)를 클릭해서 특정 영화를 켜고 끌 수 있다 (플롯리 기본 기능).
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    labels={"날짜": "날짜", "일관객": "일일 관객수", "영화명": "영화"},
    title="일관객 합계 상위 5편 · 날짜별 일일 관객수 비교",
    category_orders={"영화명": top5_names},  # 범례 순서를 합계 큰 순서로 고정
)
fig2.update_traces(hovertemplate="%{fullData.name}<br>날짜: %{x|%Y-%m-%d}<br>관객수: %{y:,}명<extra></extra>")
fig2.update_layout(yaxis_tickformat=",", legend_title_text="영화 (클릭해서 켜고 끄기)")

st.plotly_chart(fig2, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** _(여기에 한 문장을 적어 주세요)_")

st.divider()

# ══════════════════════════════════════════════════════════════════════
# 구역 3. (다음 그래프를 위한 자리)
# ══════════════════════════════════════════════════════════════════════
# 다음 그래프를 추가할 때는 아래에 st.header("구역 3 · ...") 부터
# 시작해서 구역 1, 2와 같은 모양으로 이어서 쓰면 된다.
