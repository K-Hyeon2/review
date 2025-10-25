import streamlit as st
import pandas as pd
import numpy as np
import os




st.title("큰 제목")

st.header("중간 제목")

st.subheader("작은 제목")

st.write("기본 출력")






name = st.text_input("이름을 입력하세요.")

age = st.number_input("나이를 입력하세요.", min_value=1, max_value=100)

agree = st.checkbox("동의합니다.")

if agree:
    st.write(f"{name}님 환영합니다! {age}살이고 동의해주셨습니다.")




chart_data = pd.DataFrame(np.random.randn(20, 3), 
                          columns = ["A", "B", "C"])

st.line_chart(chart_data)
st.bar_chart(chart_data)






st.set_page_config(page_title="내 로컬 CSV 차트 뷰어", layout="wide")
st.title("📁 로컬 CSV 차트 뷰어 (업로드 없이, os.path 사용)")

# 1) CSV 폴더 경로: main.py와 같은 폴더의 data/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)  # 상대경로 → 절대경로로 안전하게 변환

# 2) data 폴더에서 CSV 목록 읽기
csv_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".csv")]
csv_files.sort()

if not csv_files:
    st.warning(f"`{DATA_DIR}` 폴더에 CSV 파일이 없습니다.\n"
               "예: data/students.csv, data/sales.csv, data/sensor.csv")
    st.stop()

# 3) 파일 선택 (사이드바)
st.sidebar.header("1) 파일 선택")
selected_name = st.sidebar.selectbox("CSV 파일", options=csv_files)
selected_path = os.path.join(DATA_DIR, selected_name)

@st.cache_data(show_spinner=False)
def read_csv_smart(path):
    # 인코딩 자동 대응: 기본 → UTF-8 → CP949 → EUC-KR
    tried = []
    for enc in (None, "utf-8", "cp949", "euc-kr"):
        try:
            if enc is None:
                return pd.read_csv(path)
            else:
                return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            tried.append(enc or "default")
            continue
    # 모두 실패하면 마지막 시도에서 에러가 나도록 기본 호출
    return pd.read_csv(path)  # 실패 시 에러 발생

# 4) CSV 읽기
try:
    df = read_csv_smart(selected_path)
except Exception as e:
    st.error(f"CSV를 읽는 중 오류: {e}")
    st.stop()

st.success(f"불러온 파일: **{selected_name}**")
st.subheader("원본 데이터 미리보기")
st.dataframe(df, use_container_width=True)

# 5) 기본/차트 설정
st.sidebar.header("2) 기본 설정")
all_cols = list(df.columns)
if not all_cols:
    st.warning("열이 없는 CSV입니다.")
    st.stop()

x_col = st.sidebar.selectbox("X축 컬럼", options=all_cols, index=0)

# X축이 날짜일 수 있으면 변환 옵션
parse_date = st.sidebar.checkbox("X축을 날짜(datetime)로 변환 시도", value=("date" in x_col.lower()))
if parse_date:
    df[x_col] = pd.to_datetime(df[x_col], errors="coerce")
    df = df.dropna(subset=[x_col])

# 수치형 컬럼 자동 탐지
numeric_cols = list(df.select_dtypes(include="number").columns)
y_candidates = [c for c in numeric_cols if c != x_col] if x_col in numeric_cols else numeric_cols

st.sidebar.header("3) 차트 설정")
chart_type = st.sidebar.selectbox("차트 타입", ["line", "area", "bar"])
y_cols = st.sidebar.multiselect(
    "Y축(수치형) 컬럼 (복수 선택 가능)",
    options=y_candidates,
    default=y_candidates[:1] if y_candidates else []
)

if not y_cols:
    st.warning("Y축으로 사용할 수치형 컬럼을 최소 1개 선택하세요.")
    st.stop()

# 6) 그리기용 데이터프레임 구성
plot_df = df[[x_col] + y_cols].copy()
plot_df = plot_df.sort_values(by=x_col).set_index(x_col)

st.subheader("차트")
if chart_type == "line":
    st.line_chart(plot_df, use_container_width=True)
elif chart_type == "area":
    st.area_chart(plot_df, use_container_width=True)
else:
    st.bar_chart(plot_df, use_container_width=True)

st.subheader("기본 통계")
st.write(df[y_cols].describe())