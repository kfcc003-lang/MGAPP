import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="업무지원 요청 현황 대시보드",
    page_icon="📊",
    layout="wide"
)

st.title("📊 업무지원 요청 현황 대시보드")
st.caption("CSV 파일을 업로드하면 업무지원 요청 데이터를 자동으로 분석하고 시각화합니다.")

# -------------------------------------------------
# CSV 업로드
# -------------------------------------------------
uploaded_file = st.file_uploader(
    "업무지원 요청 CSV 파일을 업로드하세요.",
    type=["csv"]
)

if uploaded_file is None:
    st.info("CSV 파일을 업로드하면 분석 결과가 표시됩니다.")
    st.stop()


# -------------------------------------------------
# CSV 읽기
# -------------------------------------------------
@st.cache_data
def load_data(file):
    try:
        return pd.read_csv(file, encoding="utf-8-sig")
    except UnicodeDecodeError:
        file.seek(0)
        return pd.read_csv(file, encoding="cp949")


try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()


# -------------------------------------------------
# 필수 컬럼 확인
# -------------------------------------------------
required_columns = [
    "request_id",
    "request_date",
    "category",
    "summary",
    "urgency",
    "status",
    "ai_handling"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "필수 컬럼이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.stop()


# -------------------------------------------------
# 데이터 전처리
# -------------------------------------------------
df["request_date"] = pd.to_datetime(
    df["request_date"],
    errors="coerce"
)

# 공백 정리
text_columns = [
    "request_id",
    "category",
    "summary",
    "urgency",
    "status",
    "ai_handling"
]

for col in text_columns:
    df[col] = df[col].astype(str).str.strip()


# -------------------------------------------------
# 사이드바 필터
# -------------------------------------------------
st.sidebar.header("🔎 데이터 필터")

category_options = sorted(df["category"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "업무분류",
    options=category_options,
    default=category_options
)

status_options = sorted(df["status"].dropna().unique())

selected_status = st.sidebar.multiselect(
    "처리상태",
    options=status_options,
    default=status_options
)

urgency_options = sorted(df["urgency"].dropna().unique())

selected_urgency = st.sidebar.multiselect(
    "긴급도",
    options=urgency_options,
    default=urgency_options
)

ai_options = sorted(df["ai_handling"].dropna().unique())

selected_ai = st.sidebar.multiselect(
    "AI 처리 기준",
    options=ai_options,
    default=ai_options
)


# -------------------------------------------------
# 필터 적용
# -------------------------------------------------
filtered_df = df[
    (df["category"].isin(selected_categories)) &
    (df["status"].isin(selected_status)) &
    (df["urgency"].isin(selected_urgency)) &
    (df["ai_handling"].isin(selected_ai))
].copy()


# -------------------------------------------------
# 핵심 지표
# -------------------------------------------------
st.subheader("핵심 지표")

total_count = len(filtered_df)

completed_count = (
    filtered_df["status"] == "완료"
).sum()

unfinished_count = (
    filtered_df["status"] != "완료"
).sum()

urgent_unfinished_count = (
    (filtered_df["urgency"] == "상") &
    (filtered_df["status"] != "완료")
).sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "전체 요청",
    f"{total_count:,}건"
)

col2.metric(
    "완료",
    f"{completed_count:,}건"
)

col3.metric(
    "미완료",
    f"{unfinished_count:,}건"
)

col4.metric(
    "긴급 미완료",
    f"{urgent_unfinished_count:,}건"
)

st.divider()


# -------------------------------------------------
# 차트 1, 2
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:

    st.subheader("업무분류별 요청")

    category_count = (
        filtered_df["category"]
        .value_counts()
        .reset_index()
    )

    category_count.columns = [
        "category",
        "count"
    ]

    fig_category = px.bar(
        category_count,
        x="category",
        y="count",
        text="count",
        labels={
            "category": "업무분류",
            "count": "요청 건수"
        }
    )

    fig_category.update_layout(
        xaxis_title=None,
        yaxis_title="건수"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


with col2:

    st.subheader("처리상태별 요청")

    status_count = (
        filtered_df["status"]
        .value_counts()
        .reset_index()
    )

    status_count.columns = [
        "status",
        "count"
    ]

    fig_status = px.pie(
        status_count,
        names="status",
        values="count",
        hole=0.45
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )


# -------------------------------------------------
# 차트 3, 4
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:

    st.subheader("긴급도별 요청")

    urgency_count = (
        filtered_df["urgency"]
        .value_counts()
        .reset_index()
    )

    urgency_count.columns = [
        "urgency",
        "count"
    ]

    fig_urgency = px.bar(
        urgency_count,
        x="urgency",
        y="count",
        text="count",
        labels={
            "urgency": "긴급도",
            "count": "요청 건수"
        }
    )

    fig_urgency.update_layout(
        xaxis_title=None,
        yaxis_title="건수"
    )

    st.plotly_chart(
        fig_urgency,
        use_container_width=True
    )


with col2:

    st.subheader("AI 처리 기준")

    ai_count = (
        filtered_df["ai_handling"]
        .value_counts()
        .reset_index()
    )

    ai_count.columns = [
        "ai_handling",
        "count"
    ]

    fig_ai = px.pie(
        ai_count,
        names="ai_handling",
        values="count",
        hole=0.45
    )

    st.plotly_chart(
        fig_ai,
        use_container_width=True
    )


# -------------------------------------------------
# 날짜별 요청 추이
# -------------------------------------------------
st.subheader("📈 날짜별 요청 추이")

daily_count = (
    filtered_df
    .dropna(subset=["request_date"])
    .groupby("request_date")
    .size()
    .reset_index(name="count")
)

if not daily_count.empty:

    fig_daily = px.line(
        daily_count,
        x="request_date",
        y="count",
        markers=True,
        labels={
            "request_date": "요청일",
            "count": "요청 건수"
        }
    )

    fig_daily.update_layout(
        xaxis_title="요청일",
        yaxis_title="건수"
    )

    st.plotly_chart(
        fig_daily,
        use_container_width=True
    )

else:

    st.info("표시할 날짜 데이터가 없습니다.")


# -------------------------------------------------
# 긴급 미완료 요청
# -------------------------------------------------
st.subheader("🚨 긴급 미완료 요청")

urgent_df = filtered_df[
    (filtered_df["urgency"] == "상") &
    (filtered_df["status"] != "완료")
].copy()

if len(urgent_df) > 0:

    st.dataframe(
        urgent_df[
            [
                "request_id",
                "request_date",
                "category",
                "summary",
                "urgency",
                "status",
                "ai_handling"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.success("현재 긴급 미완료 요청이 없습니다.")


# -------------------------------------------------
# 전체 데이터
# -------------------------------------------------
st.subheader("📋 요청 목록")

display_df = filtered_df.copy()

display_df = display_df.sort_values(
    "request_date",
    ascending=False
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# -------------------------------------------------
# 요약 보고서
# -------------------------------------------------
with st.expander("📝 요약 보고서 보기"):

    st.markdown(
        f"""
### 업무지원 요청 요약

- 전체 요청: **{total_count:,}건**
- 완료: **{completed_count:,}건**
- 미완료: **{unfinished_count:,}건**
- 긴급 미완료: **{urgent_unfinished_count:,}건**
"""
    )

    st.markdown("#### 업무분류별 건수")

    category_report = (
        filtered_df["category"]
        .value_counts()
        .rename_axis("업무분류")
        .reset_index(name="건수")
    )

    st.dataframe(
        category_report,
        use_container_width=True,
        hide_index=True
    )


# -------------------------------------------------
# CSV 다운로드
# -------------------------------------------------
csv = filtered_df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="⬇️ 현재 조회 데이터 CSV 다운로드",
    data=csv,
    file_name="업무지원요청_조회결과.csv",
    mime="text/csv"
)
