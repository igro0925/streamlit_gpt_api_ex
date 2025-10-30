from dotenv import load_dotenv
import os

# .env 파일에 저장된 환경변수 로드
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


from openai import OpenAI

# openai api 인증 및 openai 객체 생성
client = OpenAI(api_key=OPENAI_API_KEY)

# chat completion 실행
completion = client.chat.completions.create(
    model="gpt-3.5-turbo", # 테스트는 싼거로
    messages=[
        # System 프롬프트
        {
            "role": "system",
            "content": "너는 IT 전문가야. 초등학생도 이해할 수 있도록 답변 부탁해."
        },
        # User 프롬프트
        {
            "role": "user",
            "content": "클라우드와 플랫폼의 차이를 설명해줘"
        }
    ]
)

print(completion.choices[0].message)