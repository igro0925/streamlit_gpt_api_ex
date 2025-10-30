####### lib 설치 ##########
# pip install openai
# pip install streamlit
# pip install python-dotenv
###########################
# 실행 : streamlit run 3-2.voice_func.py
###########################
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일 경로 지정 
load_dotenv(override=True)

# Open AI API 키 설정하기
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenAI Key 값 셋팅
client = OpenAI(api_key = OPENAI_API_KEY)

# 음성 변환 함수
def text_to_voice(user_prompt, selected_option):
    # 텍스트로부터 음성을 생성.
    audio_response = client.audio.speech.create(
        model="tts-1",
        voice=selected_option,
        input=user_prompt,
    )

    # 음성을 mp3 파일로 저장. 코드가 있는 경로에 파일이 생성된다.
    return audio_response.content

# audio 저장하기
def save_audio(audio_content):
    with open("audio_output/temp_audio.mp3", "wb") as audio_file:
        audio_file.write(audio_content)

# 메인 처리 로직
def main():
    st.title("OpenAI's Text-to-Audio Response")

    # 달리가 생성한 이미지를 사용. prompt: 귀여운 인공지능 성우 로봇 그려줘
    st.image("https://wikidocs.net/images/page/215361/%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5%EC%84%B1%EC%9A%B0.jpg", width=200)

    # 인공지능 성우 선택 박스를 생성.
    # 공식 문서 참고: https://platform.openai.com/docs/guides/text-to-speech
    options = ['alloy', 'ash', 'coral', 'echo', 'fable', 'onyx', 'nova', 'sage', 'shimmer']
    selected_option = st.selectbox("성우를 선택하세요:", options)

    # 인공지능 성우에게 프롬프트 전달
    default_text = '오늘은 생활의 꿀팁을 알아보겠습니다.'
    user_prompt = st.text_area("인공지능 성우가 읽을 스크립트를 입력해주세요.", value=default_text, height=200)

    # Generate Audio 버튼을 클릭하면 True가 되면서 if문 실행.
    if st.button("Generate Audio"):
        # text를 음성으로 변환
        audio_content = text_to_voice(user_prompt, selected_option)

        # 음성변환 정보를 파일로 저장
        save_audio(audio_content)

        # mp3 파일 재생 컨트롤러 표시
        st.audio("temp_audio.mp3", format="audio/mp3")

# 메인 실행
if __name__ == "__main__":
    main()