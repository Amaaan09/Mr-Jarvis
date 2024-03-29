from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from PyPDF2 import PdfReader
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from dotenv import load_dotenv

load_dotenv()

LLM = HuggingFaceHub(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
    model_kwargs={"temperature": 0.1, "max_length": 64,"max_new_tokens":512}
)

def extract_pdf_content(pdf_document):
    content = ""
    pdf_reader = PdfReader(pdf_document)
    for page in pdf_reader.pages:
        page_content = page.extract_text()
        if page_content is None:
            page_content = " "
        content += page_content
    return content

def split_content_into_chunks(content):
    content_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
    chunks = content_splitter.split_text(content)
    return chunks

def create_vector_store(content_chunks):
    embeddings = HuggingFaceEmbeddings()    
    vector_store = FAISS.from_texts(texts=content_chunks, embedding=embeddings)
    return vector_store

def queryLLM(llm, vectorstore, question):
    prompt = f"you are a bot called Jarvis made by Amaan and have the personality of the great detective from agatha christie's books HERCULE POIROT. I want you to converse with me in any topic, try to impersonate him as much as possible and answer the following question:\n{question}"
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())
    
    res = qa.invoke(prompt)
    res = res['result']
    res = res.split("Helpful Answer:")[-1]
    return res

def invokeResult(llm, question):
    prompt = f"you are a bot called Jarvis made by Amaan and have the personality of the great detective from agatha christie's books HERCULE POIROT. I want you to converse with me in any topic, try to impersonate him as much as possible and answer the following question:\n{question}"
    res = llm.invoke(prompt)
    res = res.split(question)[-1]
    return res
