import streamlit as st

st.title("Welcome to SpopS 👋")
st.divider()
st.header("사용안내", divider="rainbow")


st.markdown(
    """
    스폽스(SpopS)는 측정과 기록을 통해 \n
    당신의 동기부여를 유도하고 스포츠 퍼포먼스를 향상 시키기 위한 앱입니다.
    """
)

st.divider()

st.markdown(
    """
    \n
    등록된 코트의 현재 대기 인원을 파악할 수 있고 \n
    각종 경기 데이터를 확인할 수 있습니다. \n
    
    _~~오늘의 0점자에 적히지 않으려면 열심히 해야겠죠..~~_
    """
)

st.divider()
st.markdown(
    """
        왼쪽 사이드바에서 여러 페이지에 접근할 수 있습니다. \n
        우선 선수 등록 이후에
        코트 앞에 비치된 디바이스(아이패드 등)에서 대기열에 이름을 추가할 수 있습니다.
    """
)
