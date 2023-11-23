import streamlit as st
import pandas as pd
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

#load_dotenv()


save_file_name = f'batch.txt'
uploaded_file = None
button_clicked = False
st.set_page_config(layout="wide")
st.title("log check")

# 좌우 영역 구분
left_column, right_column = st.columns([2, 3])

executive_summary = None


client = OpenAI(
)


def make_prompt(data):
    system_prompt = '''다음의 내용은 보안 이슈에 대한 설명입니다.  시스템에 대한 로그 데이터를 전달하겠습니다.  \n
    로그 데이터에서 보안 취약성이 확인된 시스템만을 찾아서 아래의 항목에 맞춰 간단히 답변하세요. \n
    보안 취약성이 없는 시스템의 정보는 답변에서 제외하세요. \n
컴퓨터이름 : \n
문제 원인 : \m
이슈번호 : \n
### \n '''

    system_prompt += '''###'''
    system_prompt += str(executive_summary)
    system_prompt += '''###'''

    promptQuery = []
    promptQuery.append({"role": "system", "content": system_prompt})
    promptQuery.append({"role": "user", "content": data})

    print("############################ promptQuery start")
    print(promptQuery)
    print("############################ promptQuery end")
    #st.write(promptQuery)
    return promptQuery




def init_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)



def save_batch(batch_lines, batch_count, save_file_name):
    #file_name = f'batch.txt'
    file_name = save_file_name
    with open(file_name, 'a', newline='', encoding='utf-8') as batch_file:
        batch_file.write(str(batch_count)+ '\n')
        for line in batch_lines:
            batch_file.write(','.join(line) + '\n')




def set_Left_Column(left_column):
    global executive_summary
    left_column.markdown("## 입력 영역")
    executive_summary =left_column.text_area('텍스트를 입력해 주세요.', height=400)
    uploaded_file = left_column.file_uploader("CSV 파일을 업로드하세요.", type=["csv"])
    if uploaded_file is not None:
        return uploaded_file




def set_Right_Column(right_column):
    right_column.markdown("## 결과 영역")
    #if right_column.button("버튼을 클릭하세요"):
    #    button_clicked = True

def process_and_call_api(upload_file):
    init_file(save_file_name)
    df = pd.read_csv(upload_file)

    file_part = []
    for i, row in enumerate(df.iterrows(), start=0):
        if 20 >  (sys.getsizeof(file_part) / 1024 ):
            #st.write(f"{i}:{len(str(row))}: {row}")
            file_part += row
            print("##### file part ######")
            print(file_part)
            #print(f" len => "+str(sys.getsizeof(file_part)))
        else:
            call_API(file_part, right_column)
            file_part = row
    call_API(file_part, right_column)


def call_API(data, right_column):

    global button_clicked
    if button_clicked:
        st.write("버튼이 클릭되었습니다!")
        # 버튼 클릭 후 상태를 재설정
        button_clicked = False
        #st.write("Calling API with data:", data)


    with right_column:
        promptQuery = make_prompt(str(data))
        #st.write(promptQuery)

        response = client.chat.completions.create(
            messages=promptQuery,
            model="gpt-3.5-turbo",
            temperature=1.0
        )
        st.text(response.choices[0].message.content.strip())

        print("Generated Text:", response)

    with left_column:
        st.write(promptQuery)




def main():

    # 초기화
    save_file_name = f'batch.txt'

    uploaded_file = set_Left_Column(left_column)
    set_Right_Column(right_column)

    if uploaded_file is not None:
        process_and_call_api(uploaded_file)

if __name__ == "__main__":
    main()
