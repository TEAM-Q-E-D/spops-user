import streamlit as st
from dynamo_utils import add_user, is_name_exist

st.title("SpopS 유저 생성 👤")
st.divider()

st.header("사용안내", divider="rainbow")
st.markdown(
    """
    유저 이름은 고유해야 합니다. 이미 생성된 이름이 있다면 다른 이름으로 생성해 주셔야 합니다. \n
    비밀번호는 숫자 4자리로 만드셔야합니다. \n
    이후 기록 확인 페이지에서 자신의 데이터 확인할 때 사용됩니다.
    """,
    unsafe_allow_html=True,
)
st.divider()

st.header("선수 등록", divider="rainbow")

# 사용자 입력 필드 상태 관리
name = st.text_input("이름을 입력하세요", key="name_input")
password = st.text_input("비밀번호 (숫자 4자리)", type="password", key="password_input")

# 사용자 입력 폼
with st.form("user_form"):
    submit_button = st.form_submit_button(label="선수 등록")

# 폼 제출 시 사용자 추가
if submit_button:
    if not name:
        st.error("이름을 입력하세요.")
    elif name == "빈자리":
        st.error("사용자 이름으로 '빈자리'를 사용할 수 없습니다.")
    elif len(password) != 4 or not password.isdigit():
        st.error("비밀번호는 숫자 4자리여야 합니다.")
    elif password.startswith("0"):
        st.error("비밀번호는 '0'으로 시작할 수 없습니다.")
    elif is_name_exist(name):
        st.error("이미 존재하는 이름입니다. 다른 이름을 입력하세요.")
    else:
        if add_user(name, password):
            st.success("성공적으로 선수로 등록되었습니다.")
        else:
            st.error("선수 등록에 오류가 발생했습니다.")
