import os
import uuid
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories.streamlit import StreamlitChatMessageHistory


import chromadb
chromadb.api.client.SharedSystemClient.clear_system_cache()

#오픈AI API 키 설정
os.environ["OPENAI_API_KEY"] = YOUR_OPEN_API_KEY


@st.cache_resource
def load_and_split_pdf(file_path):
  loader = PyPDFLoader(file_path)
  return loader.load_and_split()


@st.cache_resource
def create_vector_store(_docs):
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
  split_docs = text_splitter.split_documents(_docs)
  persist_directory = "./chroma_db_test_project"
  vectorstore = Chroma.from_documents(split_docs, 
                                      OpenAIEmbeddings(model='text-embedding-3-large'),
                                      persist_directory=persist_directory)
  return vectorstore

@st.cache_resource
def get_vector_store():
  persist_directory = './vectordb/large_recursive_500_0'
  if os.path.exists(persist_directory):
    return Chroma(
      persist_directory=persist_directory,
      embedding_function=OpenAIEmbeddings(model='text-embedding-3-large')
    )
  else:
    return
  
@st.cache_resource
def initialize_components(selected_model):
  # loader_directory = DirectoryLoader(r"../data/", glob="*.pdf", loader_kwargs={"mode": "paged"} )
  # _docs = loader_directory.load()
  vectorstore = get_vector_store()
  retriever = vectorstore.as_retriever()

  contextualize_q_system_prompt = '''Given a chat history and the latest user question \
  which might reference context in the chat history, formulate a standalone question \
  which can be understood without the chat history. Do NOT answer the question, \
  just reformulate it if needed and otherwise return it as is.'''
  contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
      ('system', contextualize_q_system_prompt),
      MessagesPlaceholder('chat_history'),
      ('human', '{input}')
    ]
  )

  qa_system_prompt = """You are an assistant for question-answering tasks. \
  Use the following pieces of retrieved context to answer the question. \
  If you don't know the answer, just say that you don't know. \
  Keep the answer perfect. please use imogi with the answer.\
  너의 자료에는 판례가 있어. 최대한 판례를 참고하여 대답을 작성해주고, 그 예시를 들어서 너의 판단을 설명해줘.\
  대답은 한국어로 하고, 존댓말을 써줘. \
  
  {context}"""
  qa_prompt = ChatPromptTemplate.from_messages(
    [
      ('system', qa_system_prompt),
      MessagesPlaceholder('chat_history'),
      ('human', '{input}')
    ]
  )

  llm = ChatOpenAI(model=selected_model, streaming=True)
  history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
  question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
  rag_chain = create = create_retrieval_chain(history_aware_retriever, question_answer_chain)
  return rag_chain

st.header('저작권 지킴이')
if 'messages' not in st.session_state:
  st.session_state['messages'] = [{'role':'assistant', 'content':'저작권법에 대해 물어보세요!'}]
with st.sidebar:
  rag_chain = initialize_components('gpt-4o-mini')
chat_history = StreamlitChatMessageHistory(key='chat_messages')

conversational_rag_chain = RunnableWithMessageHistory(
  rag_chain,
  lambda session_id: chat_history,
  input_messages_key='input',
  history_messages_key='chat_history',
  output_messages_key='answer'
)

for msg in chat_history.messages:
  st.chat_message(msg.type).write(msg.content)

if prompt_message := st.chat_input('Your question'):
  st.chat_message('human').write(prompt_message)
  with st.chat_message('ai'):
    with st.spinner('Thinking...'):
      config = {'configurable':{'session_id':'any'}}
      response = conversational_rag_chain.invoke(
        {'input': prompt_message},
        config,
      )

      answer = response['answer']
      st.write(answer)
      with st.expander('참고 문서 확인'):
        for doc in response['context']:
          st.markdown(doc.metadata['source'], help=doc.page_content)