import os
import time
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories.streamlit import StreamlitChatMessageHistory
from langchain.retrievers import SelfQueryRetriever, MultiQueryRetriever
from langchain_community.document_transformers import LongContextReorder
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers import EnsembleRetriever
from langchain_community.document_loaders import TextLoader
from langchain import hub

import chromadb
chromadb.api.client.SharedSystemClient.clear_system_cache()

#오픈AI API 키 설정    
os.environ["OPENAI_API_KEY"] = YOUR_OPEN_API_KEY

@st.cache_resource
def get_vector_store():
    persist_directory = './semantic_chunk_text_based_just_laws_large' 
    if os.path.exists(persist_directory):
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=OpenAIEmbeddings(model='text-embedding-3-large')
        )
    else:
        return

@st.cache_resource
def initialize_components(selected_model):
    vectorstore = get_vector_store()
    llm = ChatOpenAI(model=selected_model, streaming=True)

    # Self Query Retriever 설정
    metadata_field_info = [
        AttributeInfo(
            name="source",
            description="""
                Source of the document. 
                Contains information about the law and the laws of a certain country. 
                If there's no name of country in source, consider it as Korean.
            """,
            type="string",
        )
    ]

    self_query_retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=vectorstore,
        document_contents='Laws',
        metadata_field_info=metadata_field_info
    )

    # Multi Query Retriever 설정
    base_retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 5,
            'score_threshold': 0.25
        }
    )
    
    multi_query_retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm
    )

    # # Long Context Reorder 추가
    # compressor = DocumentCompressorPipeline(
    #     transformers=[LongContextReorder()]
    # )

    # SelfQueryRetriever와 MultiQueryRetriever의 앙상블 설정

    ensemble_retriever = EnsembleRetriever(
        retrievers=[self_query_retriever, multi_query_retriever],
        weights=[0.8, 0.2]
    )

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

    qa_system_prompt = """You are an expert consultant on copyright law. 
    When answering questions, please refer to the retrieved context from relevant documents and reflect it in your response.
    Specify which law, article, and clause the answer pertains to, and if there are related court rulings, include the case number as supporting evidence.
    If no such information exists, it's okay not to provide any basis. 
    If you don't know the answer, please be honest and avoid making false claims. 
    Respond in Korean using polite language.
    
    {context}"""
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ('system', qa_system_prompt),
            MessagesPlaceholder('chat_history'),
            ('human', '{input}')
        ]
    )

    history_aware_retriever = create_history_aware_retriever(llm, ensemble_retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain

st.title('저작권지킴이')

if 'messages' not in st.session_state:
    st.session_state['messages'] = [{'role': 'assistant', 'content': '저작권에 대해 궁금하신가요? 무엇이든 물어보세요!'}]

for msg in st.session_state['messages']:
    st.chat_message(msg['role']).write(msg['content'])

rag_chain = initialize_components('gpt-4o-mini')
chat_history = StreamlitChatMessageHistory(key='chat_messages')

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    lambda session_id: chat_history,
    input_messages_key='input',
    history_messages_key='chat_history',
    output_messages_key='answer'
)

if prompt_message := st.chat_input('Your question'):
    st.session_state['messages'].append({'role': 'human', 'content': prompt_message})
    st.chat_message('human').write(prompt_message)
    
    with st.chat_message('ai'):
      with st.spinner('Thinking...'):
        response_parts = []
        answer_placeholder = st.empty()

        response = conversational_rag_chain.invoke(
            {'input': prompt_message},
            {'configurable': {'session_id': 'any'}}
        )

        for part in response['answer']:
            response_parts.append(part)
            answer_placeholder.markdown(''.join(response_parts))
            time.sleep(0.01)  # Add a delay to make the response appear gradually

        # Once complete, store the final answer
        st.session_state['messages'].append({'role': 'assistant', 'content': ''.join(response_parts)})
        
        # Show the reference documents properly
        with st.expander('참고 문서 확인'):
            if 'context' in response and response['context'][:5]:
                for doc in response['context']:
                    st.markdown(doc.metadata['source'].split('\\')[-1].split('.txt')[0], help=doc.page_content)
                # st.markdown(TextLoader(response['context'][0].metadata['source'], encoding='utf-8').load())
            else:
                st.write("참고 문서가 없습니다.")
