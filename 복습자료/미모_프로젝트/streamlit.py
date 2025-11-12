import streamlit as st
import pandas as pd
import bcrypt
from pathlib import Path


USERS_FILE = Path(".users_demo.csv")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def _user_dir(user_id: str) -> Path:
    d = DATA_DIR / f"user_{user_id}"
    d.mkdir(exist_ok=True)
    return d

# ---------- 즐겨찾기 ----------
def fav_path(user_id: str) -> Path:
    return _user_dir(user_id) / "favorites.csv"

def load_favs(user_id: str) -> pd.DataFrame:
    p = fav_path(user_id)
    if p.exists():
        return pd.read_csv(p)
    # 최초 생성: 비어있는 형식
    return pd.DataFrame(columns=["title_id", "title", "poster"])

def save_favs(user_id: str, df: pd.DataFrame):
    df.to_csv(fav_path(user_id), index=False)

def remove_fav(user_id: str, title_id: int):
    df = load_favs(user_id)
    df = df[df["title_id"] != title_id]
    save_favs(user_id, df)

# ---------- 리뷰 ----------
def rev_path(user_id: str) -> Path:
    return _user_dir(user_id) / "reviews.csv"

def load_revs(user_id: str) -> pd.DataFrame:
    p = rev_path(user_id)
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame(columns=["title", "review", "created_at"])

def save_revs(user_id: str, df: pd.DataFrame):
    df.to_csv(rev_path(user_id), index=False)


def _load_users_df() -> pd.DataFrame:
    if USERS_FILE.exists():
        return pd.read_csv(USERS_FILE)
    return pd.DataFrame(columns=["user_id","pw_hash","email","nickname","joined"])

def _save_users_df(df: pd.DataFrame):
    df.to_csv(USERS_FILE, index=False)

def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def check_pw(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

def update_nickname(user_id: str, new_nick: str) -> tuple[bool, str]:
    df = _load_users_df()
    m = df["user_id"] == user_id
    if not m.any():
        return False, "사용자를 찾을 수 없습니다."
    if not new_nick.strip():
        return False, "닉네임을 입력해주세요."
    df.loc[m, "nickname"] = new_nick.strip()
    _save_users_df(df)
    return True, "닉네임이 변경되었습니다."

def change_password(user_id: str, cur_pw: str, new_pw: str) -> tuple[bool, str]:
    df = _load_users_df()
    m = df["user_id"] == user_id
    if not m.any():
        return False, "사용자를 찾을 수 없습니다."
    row = df[m].iloc[0]
    if not check_pw(cur_pw, row["pw_hash"]):
        return False, "현재 비밀번호가 일치하지 않습니다."
    if len(new_pw) < 8:
        return False, "새 비밀번호는 8자 이상 권장!"
    df.loc[m, "pw_hash"] = hash_pw(new_pw)
    _save_users_df(df)
    return True, "비밀번호가 변경되었습니다."


def get_user_profile(uid: str):
    """CSV(신규 가입자) → 없으면 데모 USERS 순으로 프로필만 반환"""
    df = _load_users_df()
    row = df[df["user_id"] == uid]
    if not row.empty:
        r = row.iloc[0]
        return {
            "user_id": uid,
            "nickname": r["nickname"],
            "email": r["email"],
            "joined": r["joined"],
        }
    # 데모 USERS fallback
    u = USERS.get(uid)
    if u:
        return {
            "user_id": uid,
            "nickname": u["nickname"],
            "email": u["email"],
            "joined": u["joined"],
        }
    return None




USERS = {
    "guest": {
        "password": "12341234",           # 데모용 평문! (다음 단계에서 해시/DB)
        "nickname": "게스트",
        "email": "guest@example.com",
        "joined": "2025-01-01",
    },
    "neo": {
        "password": "matrix1234",
        "nickname": "네오",
        "email": "neo@zion.ai",
        "joined": "2024-10-10",
    },
}


def auth_login(uid: str, pw: str):
    # 1) CSV(신규 가입자) 우선
    df = _load_users_df()
    row = df[df["user_id"] == uid]
    if not row.empty:
        r = row.iloc[0]
        if check_pw(pw, r["pw_hash"]):
            return {
                "nickname": r["nickname"],
                "email": r["email"],
                "joined": r["joined"],
            }
        else:
            return None

    # 2) 없으면 하드코딩 USERS(이전 단계 계정)도 허용
    u = USERS.get(uid)
    if not u:
        return None




st.set_page_config(page_title="OTT Demo", layout="wide")

# 1) 세션에 현재 페이지 값 준비 (최초 실행 시 기본 '홈')
if "page" not in st.session_state:
    st.session_state.page = "홈"

# 2) 헤더 영역 (로고 + 우측 버튼)
left, right = st.columns([6, 1])
with left:
    st.markdown("### 로고")
with right:
    if "user" in st.session_state:
        # 로그인 상태 → 로그아웃 버튼
        if st.button("로그아웃", use_container_width=True):
            st.session_state.pop("user")
            st.session_state.page = "홈"
            st.rerun()
    else:
        # 비로그인 상태 → 로그인으로 이동
        if st.button("로그인", use_container_width=True):
            st.session_state.page = "로그인"

st.divider()


def validate_user_id(uid: str) -> str | None:
    if not uid.strip():
        return "아이디를 입력하세요."
    if " " in uid:
        return "아이디에 공백은 안 돼요."
    if len(uid) < 3:
        return "아이디는 3자 이상 권장!"
    return None

def validate_password(pw: str) -> str | None:
    if not pw:
        return "비밀번호를 입력하세요."
    if len(pw) < 8:
        return "비밀번호는 8자 이상 권장!"
    return None



# 3) 사이드바 메뉴 (페이지 변경만 수행)
with st.sidebar:
    if st.button("홈", use_container_width=True):
        st.session_state.page = "홈"
    if st.button("회원가입", use_container_width=True):
        st.session_state.page = "회원가입"
    if st.button("마이페이지", use_container_width=True):
        st.session_state.page = "마이페이지"


# 4) 페이지별 렌더 함수 (내용은 비워두고 자리만 잡자)
def page_home():
    st.header("홈")
    st.write("여기는 홈입니다. (다음 단계에서 기능 채울 예정)")

def page_login():
    st.header("로그인")

    with st.form("login-form", clear_on_submit=False):
        uid = st.text_input("아이디")
        pw  = st.text_input("비밀번호", type="password")
        keep = st.checkbox("로그인 유지", value=False)
        submitted = st.form_submit_button("로그인")

    if submitted:
        e1 = validate_user_id(uid)
        e2 = validate_password(pw)

        if e1: st.error(e1)
        if e2: st.error(e2)

        if not (e1 or e2):
            user = auth_login(uid, pw)
            if user is None:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
            else:
                # ✅ 세션에 로그인 사용자 정보 저장
                st.session_state.user = {
                    "user_id": uid,
                    "nickname": user["nickname"],
                    "email": user["email"],
                    "joined": user["joined"],
                    "keep": keep,
                }
                st.success("로그인 성공! 마이페이지로 이동합니다.")
                st.session_state.page = "마이페이지"
                st.rerun()

    # 보조 이동
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("회원가입으로 이동"):
            st.session_state.page = "회원가입"
    with c2:
        st.button("ID 찾기", disabled=True)
    with c3:
        st.button("PW 찾기", disabled=True)



def sign_up(user_id: str, password: str, email: str, nickname: str):
    df = _load_users_df()
    if user_id in set(df["user_id"]):
        return False, "이미 존재하는 아이디입니다."
    if email in set(df["email"]):
        return False, "이미 등록된 이메일입니다."

    row = {
        "user_id": user_id,
        "pw_hash": hash_pw(password),       # 해시 저장 (평문 금지)
        "email": email,
        "nickname": nickname,
        "joined": pd.Timestamp.today().date().isoformat(),
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _save_users_df(df)
    return True, "가입 완료"




def page_signup():
    st.header("회원가입 / ID/PW 찾기")

    tab_signup, tab_find_id, tab_find_pw = st.tabs(["회원가입", "ID 찾기", "PW 찾기"])

    # --- 회원가입 탭 ---
    with tab_signup:
        with st.form("signup-form", clear_on_submit=False):
            uid = st.text_input("아이디")
            pw  = st.text_input("비밀번호", type="password")
            pw2 = st.text_input("비밀번호 확인", type="password")
            nick= st.text_input("닉네임")
            email = st.text_input("이메일")
            ok = st.form_submit_button("가입하기")

        if ok:
            e_uid = validate_user_id(uid)
            e_pw  = validate_password(pw)
            if e_uid: st.error(e_uid)
            if e_pw:  st.error(e_pw)
            if pw != pw2:
                st.error("비밀번호 확인이 일치하지 않습니다.")

            if not any([e_uid, e_pw]) and pw == pw2:
                ok2, msg = sign_up(uid, pw, email, nick)
                if not ok2:
                    st.error(msg)
                else:
                    st.success(msg)
                    # 자동 로그인
                    prof = get_user_profile(uid)
                    if prof:
                        st.session_state.user = {**prof, "keep": False}
                        st.session_state.page = "마이페이지"
                        st.rerun()

    # --- ID 찾기 탭 ---
    with tab_find_id:
        st.caption("가입할 때 쓴 이메일로 아이디를 찾아요.")
        with st.form("find-id-form", clear_on_submit=True):
            em = st.text_input("가입 이메일")
            ok_find = st.form_submit_button("아이디 찾기")
        if ok_find:
            df = _load_users_df()
            row = df[df["email"] == em]
            if row.empty:
                st.error("해당 이메일로 가입된 계정이 없습니다.")
            else:
                uid_found = row.iloc[0]["user_id"]
                st.success(f"아이디: **{uid_found}**")

    # --- PW 찾기 탭 ---
    with tab_find_pw:
        st.caption("아이디와 가입 이메일을 확인해요. (MVP: 메일 발송 대신 임시 안내)")
        with st.form("find-pw-form", clear_on_submit=True):
            uid2 = st.text_input("아이디")
            em2  = st.text_input("가입 이메일")
            ok_pw = st.form_submit_button("비밀번호 재설정 요청")
        if ok_pw:
            df = _load_users_df()
            row = df[(df["user_id"] == uid2) & (df["email"] == em2)]
            if row.empty:
                st.error("아이디/이메일이 일치하지 않습니다.")
            else:
                st.success("재설정 링크가 발송되었습니다. (MVP 데모 메시지)")
                # 실제 구현은: 토큰 발급 → 메일 발송 → 토큰 검증 페이지

def page_mypage():
    st.header("마이페이지")

    # 로그인 보호
    if "user" not in st.session_state:
        st.warning("마이페이지는 로그인 후 이용 가능합니다.")
        if st.button("로그인하러 가기"):
            st.session_state.page = "로그인"
        return
    u = st.session_state.user
    uid = u["user_id"]

    # -------- 내 정보 --------
    st.subheader("내 정보")
    c1, c2, c3, c4 = st.columns([2,3,3,2])
    with c1: st.metric("닉네임", u["nickname"])
    with c2: st.metric("이메일", u["email"])
    with c3: st.metric("가입일", u["joined"])
    with c4: st.caption("비밀번호 변경은 추후 단계")


        # -------- 프로필 수정: 닉네임 --------
    with st.expander("프로필 수정 (닉네임)", expanded=False):
        with st.form("form-edit-nick", clear_on_submit=False):
            new_nick = st.text_input("새 닉네임", value=u["nickname"])
            ok_nick = st.form_submit_button("닉네임 저장")
        if ok_nick:
            ok, msg = update_nickname(uid, new_nick)
            if ok:
                # 세션에도 즉시 반영
                st.session_state.user["nickname"] = new_nick.strip()
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    # -------- 보안: 비밀번호 변경 --------
    with st.expander("비밀번호 변경", expanded=False):
        with st.form("form-change-pw", clear_on_submit=True):
            cur = st.text_input("현재 비밀번호", type="password")
            new = st.text_input("새 비밀번호 (8자 이상)", type="password")
            chk = st.text_input("새 비밀번호 확인", type="password")
            ok_pw = st.form_submit_button("비밀번호 변경")
        if ok_pw:
            if new != chk:
                st.error("새 비밀번호 확인이 일치하지 않습니다.")
            else:
                ok, msg = change_password(uid, cur, new)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    st.markdown("---")

    # -------- 즐겨찾기 목록 --------
    st.subheader("내 즐겨찾기")
    fav_df = load_favs(uid)

    # 최초 체험용 더미(비었으면 샘플 10개 넣어줌)
    if fav_df.empty:
        sample = [{"title_id": i, "title": f"영화 제목 {i}", "poster": "🎬"} for i in range(1, 11)]
        fav_df = pd.DataFrame(sample)
        save_favs(uid, fav_df)

    # 페이지네이션 상태
    PAGE_SIZE = 8
    if "fav_page" not in st.session_state: st.session_state.fav_page = 1
    page = st.session_state.fav_page
    total = len(fav_df)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE

    # 슬라이스
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_df = fav_df.iloc[start:end]

    # 카드 그리드(4x2)
    rows, cols = 2, 4
    for r in range(rows):
        col_objs = st.columns(cols)
        for c in range(cols):
            idx = r*cols + c
            if idx >= len(page_df): 
                with col_objs[c]: st.empty()
                continue
            row = page_df.iloc[idx]
            with col_objs[c]:
                st.markdown(f"<div style='text-align:center;font-size:48px'>{row['poster']}</div>", unsafe_allow_html=True)
                st.markdown(f"**{row['title']}**")
                # 삭제 버튼
                if st.button("삭제", key=f"fav_del_{int(row['title_id'])}"):
                    remove_fav(uid, int(row["title_id"]))
                    st.rerun()

    # 페이지네이션 컨트롤
    pc = st.columns([1,6,1])
    with pc[0]:
        if st.button("◀ 이전", disabled=(page <= 1)):
            st.session_state.fav_page = max(1, page-1); st.rerun()
    with pc[1]:
        st.markdown(f"<div style='text-align:center'>페이지 {page} / {max(total_pages,1)}</div>", unsafe_allow_html=True)
    with pc[2]:
        if st.button("다음 ▶", disabled=(page >= total_pages)):
            st.session_state.fav_page = min(total_pages, page+1); st.rerun()

    st.markdown("---")

    # -------- 내 리뷰 --------
    # -------- 내 리뷰 --------
    st.subheader("내가 작성한 리뷰")

    # 작성 폼 (간단)
    with st.form("add-review-form", clear_on_submit=True):
        t = st.text_input("영화 제목")
        r = st.text_area("리뷰 내용", height=100, placeholder="한 줄 감상도 좋아요!")
        ok = st.form_submit_button("리뷰 저장")
    if ok:
        if not t.strip():
            st.error("영화 제목을 입력해주세요.")
        elif not r.strip():
            st.error("리뷰 내용을 입력해주세요.")
        else:
            df = load_revs(uid)
            new_row = {"title": t.strip(), "review": r.strip(),
                       "created_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_revs(uid, df)
            st.success("리뷰가 저장되었습니다.")
            st.rerun()

    # 테이블 표시
    rev_df = load_revs(uid)
    if rev_df.empty:
        st.info("아직 작성한 리뷰가 없습니다.")
    else:
        # 열 순서/표시명 통일
        rev_df = rev_df[["title","review","created_at"]].rename(columns={
            "title":"영화제목","review":"리뷰","created_at":"작성일"
        })
        st.dataframe(rev_df, use_container_width=True, height=280)

 
# 5) ‘현재 페이지’ 값에 따라 해당 함수 호출
page = st.session_state.page
if page == "홈":
    page_home()
elif page == "로그인":
    page_login()
elif page == "회원가입":
    page_signup()
elif page == "마이페이지":
    page_mypage()