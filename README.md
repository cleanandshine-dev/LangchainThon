# [RAG를 활용한 MVP 프로젝트] 저작권 지킴이 📚
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=OpenAI&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=LangChain&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=Streamlit&logoColor=white)
<br>
<br>


## 🌐 Project Background
### 🖊️ 문제정의
- 일반 사용자들이 저작권법에 접근하기 어렵다는 문제점이 존재
  - **법적 지식 접근의 어려움**
      - 빈번한 개정 - 기술 발전에 따라 새로운 형태의 저작물이 등장하고 사회변화에 따라 법이 지속적으로 개정됨.
      - 복잡한 법률 용어 - 일반인이 이해하기 어려운 복잡한 법률 용어들이 많음.
      - 다양한 권리 유형 - 저작재산권, 저작인격권, 복제권 등 다양한 권리 유형이 존재하여 각 권리의 범위를 이해하기 어려움.
  - **저작권 침해 판단의 어려움**
      - 실질적 유사성: 저작권 침해 여부를 판단할 때 '실질적 유사성'이라는 모호한 기준을 적용하여 판단이 어려움.
      - 공정 이용의 모호성: 교육 목적이나 인용 등 경계가 명확하지 않아 혼란을 줄 수 있음.
<br>

### 🤦🏻‍♀️ 기존방법의 한계
  - 로펌이나 법무법인을 통한 법률 자문은 비용부담이 큼.
  - 한국저작권위원회에서 제공하는 자료를 개별적으로 확인해야 해 시간이 많이 소요됨.
  - 한국저작권위원회에서 여러가지 상담서비스를 제공하고 있으나 사전신청이 필요하고, 제공되는 챗봇서비스의 성능이 떨어져 요구를 충족하지 못함.
<br>

### 🏹 프로젝트 목표
  - 일반 사용자가 저작권 정보를 쉽고 빠르게 찾아볼 수 있도록 RAG를 이용한 챗봇 서비스를 구축
  - 사용자들의 정보 접근성을 높이고 시간과 비용을 절감하는 효과

<br>
<br>


## 💽 Data 
![](image/copyright_reference.png)
<br>
<br>


## 🤖 Structure Overview
![](image/structure_overview.png)
<br>
<br>


## 🔍 Validation
1️⃣ 한국저작권협의회(링크)에 있는 2023저작권상담사례집에 있는 질문을 발췌  
```
📄발췌한 질문리스트
1. CCTV나 블랙박스 영상도 저작물인가요?
2. 시중에 판매되는 학습교재를 이용하여 동영상 강의를 제작하고 유튜브에 게시해도 되나요?
3. 외국도서를 번역한 경우 저의 번역물이 저작물로 보호될 수 있나요?
```
2️⃣ 1️⃣에서 사용한 질문에 추가질문  
3️⃣ 사례에 대한 질문과 해외 저작권법에 대한 질문을 하여 RAG를 통해 검색이 제대로 이루어졌는지 확인  
<br>
<br>
  

## 📺 Demonstration  
- Validation에서 정한 방법을 바탕으로 3분 이내의 영상 제작  
1️⃣ 웹 애플리케이션에 접속    
2️⃣ 메시지창에 자신이 처한 저작권위반 가능성, 침해받은 가능성 외 저작권 관련 궁금한 사항을 작성  
3️⃣ LLM이 DB에 저장된 문서들을 활용하여
  
      ☑️ 법적근거를 제시하여 답변  
      ☑️ 사례를 요구하는 경우 ⇒ 관련 판례를 제시하여 답변 구성  
      ☑️ 해외(미국,일본)의 저작권법에 해당하는 경우 ⇒ 해외 저작권법을 제시하여 답변 구성  
<br>
<br>


## 📡 Developments
- Tavily 등의 웹 서치 LLM과 연결
  - 웹 서치 llm과 연결하여 데이터베이스 뿐 아니라 다른 국가의 법, 사례 정보를 받아 답변의 품질 향상
- 다른 법률에도 확장 가능하게 만들어 다른 법률에 특화된 챗봇도 구현 가능
- 추가적인 기능 탑재
  - 이미지, 글, 영상 등의 자료 입력 시 저작권 위반 위험이 있는 자료인지 검색하는 기능 추가 가능
  - 저작권 법 및 플랫폼별 정책에 위배되지 않는 저작권 자료를 찾는 기능도 추가 가능
- 질문에 대한 답변을 생성할 때 참고하는 자료가 제한적
  ⇒ Agent를 도입하고 추론 과정을 추가하면 원하는 답변을 더 잘 얻을 수 있을 것으로 예상
<br>
<br>


## 💻 Code References
- ![이토록 쉬운 RAG 시스템 구축을 위한 랭체인 실전 가이드](https://www.yes24.com/product/goods/136548871)
- ![Langchain뿌시기](https://www.youtube.com/playlist?list=PLQIgLu3Wf-q_Ne8vv-ZXuJ4mztHJaQb_v)
- ![Langchain-RAG](https://github.com/Kane0002/Langchain-RAG)
<br>
<br>


## 🗨️ Tools
![Canva](https://img.shields.io/badge/Canva-00C4CC?style=flat-square&logo=Canva&logoColor=white)
![Google Drive](https://img.shields.io/badge/GoogleDrive-4285F4?style=flat-square&logo=GoogleDrive&logoColor=white)
![discord](https://img.shields.io/badge/discord-5865F2?style=flat-square&logo=discord&logoColor=white)
