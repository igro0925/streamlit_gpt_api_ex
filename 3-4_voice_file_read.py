import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# .env 로드
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# --------- 1. ipynb -> 텍스트로 변환 ---------
def ipynb_to_text(file_bytes: bytes) -> str:
    nb = json.loads(file_bytes.decode("utf-8"))
    parts = []
    for cell in nb.get("cells", []):
        cell_type = cell.get("cell_type")
        src = "".join(cell.get("source", []))
        if not src.strip():
            continue
        if cell_type == "markdown":
            parts.append(src.strip())
        elif cell_type == "code":
            parts.append("```python\n" + src.strip() + "\n```")
    return "\n\n".join(parts)

# --------- 2. 파일을 “LLM이 읽기 좋은 텍스트”로 만드는 함수 ---------
def file_to_text(uploaded_file) -> str:
    name = uploaded_file.name
    raw_bytes = uploaded_file.read()

    if name.endswith(".py"):
        text = raw_bytes.decode("utf-8")
        return text
    elif name.endswith(".ipynb"):
        return ipynb_to_text(raw_bytes)
    else:
        raise ValueError("지원하는 형식은 .py, .ipynb 입니다.")

# --------- 3. LLM으로 코드 설명 생성 ---------
def explain_code_with_llm(code_text: str) -> str:
    """
    openai 2.6.1 기준: responses.create 에 input=... 사용
    """
    system_prompt = (
        "너는 업로드된 파이썬 코드나 주피터 노트북의 내용을 사람에게 설명해주는 어시스턴트야.\n"
        "아래 형식으로 간단하게 설명해줘.\n"
        "1) 이 코드/노트북이 하는 일 한 줄 요약\n"
        "2) 주요 단계/함수 이름과 하는 일\n"
        "3) 외부에서 설정해야 하는 값/키/환경변수\n"
        "4) 실행 방법이 있으면 적기\n"
        "가능하면 한국어로 답해. 너무 장황하지 않게."
    )

    # 길이 제한: 너무 긴 노트북이면 앞부분만 잘라서 보냄
    MAX_INPUT = 6000
    send_text = code_text[:MAX_INPUT]

    resp = client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 코드를 설명해줘:\n\n{send_text}"},
        ],
    )

    explanation = resp.output[0].content[0].text
    return explanation.strip()

# --------- 4. TTS로 설명 읽어주기 ---------
def tts_from_text(text: str, voice: str = "alloy", model: str = "tts-1") -> bytes:
    audio_response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
    )
    return audio_response.content

# --------- 5. Streamlit UI ---------
def main():
    st.title("📁 코드/노트북 올리면 → 🤖 설명 → 🗣️ 음성으로 듣기")

    uploaded = st.file_uploader("py 또는 ipynb 파일을 업로드하세요", type=["py", "ipynb"])

    # 음성 선택
    voices = ['alloy', 'ash', 'coral', 'echo', 'fable', 'onyx', 'nova', 'sage', 'shimmer']
    selected_voice = st.selectbox("음성(보이스) 선택", voices, index=0)

    # 설명문을 저장해둘 자리
    if "last_explanation" not in st.session_state:
        st.session_state.last_explanation = None

    if uploaded is not None:
        st.success(f"파일을 불러왔습니다: {uploaded.name}")

        # 1) 파일 → 텍스트
        try:
            # 중요: read()는 한 번만 하면 되니까 변수에 담아두고, 텍스트로 만든 뒤
            uploaded.seek(0)  # 혹시 모를 포인터 초기화
            file_bytes = uploaded.read()
            # 다시 텍스트 변환에 쓰기
            if uploaded.name.endswith(".py"):
                code_text = file_bytes.decode("utf-8")
            else:
                code_text = ipynb_to_text(file_bytes)
        except Exception as e:
            st.error(f"파일을 해석하는데 실패했습니다: {e}")
            return

        # 원하면 원본도 보여주기
        with st.expander("원본 코드 보기"):
            st.code(code_text, language="python")

        # 2) LLM으로 설명 생성 버튼
        if st.button("🤖 코드 내용 설명해줘"):
            with st.spinner("AI가 코드를 읽고 설명을 만드는 중..."):
                explanation = explain_code_with_llm(code_text)
            st.session_state.last_explanation = explanation

    # 3) 설명이 있으면 화면에 보여주기 + 음성버튼
    if st.session_state.last_explanation:
        st.subheader("📝 AI가 만든 설명")
        st.markdown(st.session_state.last_explanation)

        if st.button("🗣️ 이 설명을 음성으로 듣기"):
            with st.spinner("음성을 생성하는 중..."):
                audio_bytes = tts_from_text(st.session_state.last_explanation, selected_voice)

            os.makedirs("audio_output", exist_ok=True)
            out_path = "audio_output/ai_explanation.mp3"
            with open(out_path, "wb") as f:
                f.write(audio_bytes)

            st.audio(out_path, format="audio/mp3")
            st.download_button(
                "⬇️ MP3 다운로드",
                data=audio_bytes,
                file_name="ai_explanation.mp3",
                mime="audio/mpeg",
            )

if __name__ == "__main__":
    main()