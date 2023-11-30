from langchain import OpenAI

from llama_index import SimpleDirectoryReader, ServiceContext, VectorStoreIndex
from llama_index import set_global_service_context
from llama_index.response.pprint_utils import pprint_response
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.query_engine import SubQuestionQueryEngine

import json
import streamlit as st
import os
import requests


# Page configuration
st.set_page_config(page_title="SemaPDF", page_icon="📚", layout="wide",)

#set Open-AI key
os.environ["Public_Url"] = st.secrets["Public_Url"]

llm = OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=-1)

service_context = ServiceContext.from_defaults(llm=llm)
set_global_service_context(service_context=service_context)



# Sema Translator
def translate(userinput, target_lang, source_lang=None):
    if source_lang:
       url = "Public_Url/translate_enter/"
       data = {
           "userinput": userinput,
           "source_lang": source_lang,
           "target_lang": target_lang,
        }
       response = requests.post(url, json=data)
       result = response.json()
       print(type(result))
       source_lange = source_lang
       translation = result['translated_text']
       return source_lange, translation
    else:
      url = "Public_Url/translate_detect/"
      data = {
        "userinput": userinput,
        "target_lang": target_lang,
      }

      response = requests.post(url, json=data)
      result = response.json()
      source_lange = result['source_language']
      translation = result['translated_text']
      return source_lange, translation


def main():
        st.title("💬 SemaNaPDF")
        # upload file
        pdf = st.file_uploader("Upload a Pdf Document and ask it questions", type="pdf")

        # extract the text
        if pdf is not None:
          reader = PdfReader(pdf)
          lyft_docs = SimpleDirectoryReader(input_files=["../pdf.pdf"]).load_data()
          print(f'Loaded lyft 10-K with {len(lyft_docs)} pages')

          # Save 
          lyft_index = VectorStoreIndex.from_documents(lyft_docs)
          lyft_engine = lyft_index.as_query_engine(similarity_top_k=3)

          #user_question = st.text_input("Ask your document anything ...")
          query_engine_tools = [
          QueryEngineTool(
              query_engine=lyft_engine, 
              metadata=ToolMetadata(name='lyft_10k', description='Provides information about your document')
          )
          ]

          s_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=query_engine_tools)

          # show user input
          if "messages" not in st.session_state:
              st.session_state.messages = []

          for message in st.session_state.messages:
              with st.chat_message(message["role"]):
                st.markdown(message["content"])

          if user_question := st.chat_input("Ask your document anything ......?"):
            with st.chat_message("user"):
                st.markdown(user_question)
            user_langd, Queryd = translate(user_question, 'eng_Latn')
            st.session_state.messages.append({"role": "user", "content": user_question})
            response = await s_engine.aquery(Queryd')
            output = translate(response, user_langd, 'eng_Latn')[1]
            with st.chat_message("assistant"):
                st.markdown(output)
                st.session_state.messages.append({"role": "assistant", "content": output})


if __name__ == '__main__':
    main()
