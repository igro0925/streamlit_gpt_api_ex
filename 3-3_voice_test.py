import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ ① AI가 프롬프트 보고 보이스를 골라주는 함수 추가
ALLOWED_VOICES = {"alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"}

def recommend_voice_by_llm(text: str) -> str:
    system_prompt = (
        "너는 텍스트를 읽기 좋은 음성을 골라주는 어시스턴트야.\n"
        "반드시 아래 목록 중 하나만 소문자로 출력해.\n"
        "목록: alloy, ash, coral, echo, fable, onyx, nova, sage, shimmer.\n"
        "설명/공지/안내/매뉴얼/기업 공지 → sage 또는 alloy\n"
        "교육/학습/튜토리얼 → nova\n"
        "아이/이야기/동화/따뜻한 톤 → fable\n"
        "밝고 경쾌 → coral\n"
        "기타는 alloy\n"
        "다른 말 하지 마. 이유도 말하지 마. 하나만."
    )

    resp = client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"이 텍스트에 어울리는 음성을 골라줘:\n{text}"},
        ]
    )

    voice = resp.output[0].content[0].text.strip().lower()
    if voice not in ALLOWED_VOICES:
        voice = "alloy"
    return voice


# ✅ ② TTS 함수
def text_to_voice(user_prompt, selected_option):
    audio_response = client.audio.speech.create(
        model="tts-1",
        voice=selected_option,
        input=user_prompt,
    )
    return audio_response.content


# ✅ ③ 오디오 저장 함수
def save_audio(audio_content, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(audio_content)


# ✅ ④ Streamlit 메인 부분
def main():
    st.title("AI가 알아서 보이스를 골라주는 TTS")

    default_text = "오늘은 생활의 꿀팁을 알아보겠습니다."
    user_prompt = st.text_area("스크립트를 입력하세요", value=default_text, height=200)

    if st.button("🎙️ Generate Audio"):
        with st.spinner("AI가 어울리는 보이스를 고르는 중입니다..."):
            ai_voice = recommend_voice_by_llm(user_prompt)

        st.write(f"🤖 AI가 선택한 보이스: **{ai_voice}**")

        with st.spinner("음성을 생성하는 중입니다..."):
            audio_content = text_to_voice(user_prompt, ai_voice)

        filepath = "audio_output/temp_audio.mp3"
        save_audio(audio_content, filepath)

        st.audio(filepath, format="audio/mp3")
        st.download_button(
            "⬇️ 다운로드",
            data=audio_content,
            file_name="tts_output.mp3",
            mime="audio/mpeg"
        )
        st.success("완료!")

if __name__ == "__main__":
    main()
