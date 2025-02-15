import nest_asyncio
nest_asyncio.apply()
import os
from dotenv import load_dotenv
load_dotenv()

from nexgen import models
from typing import List

import instructor
from fast_graphrag import GraphRAG, QueryParam
from fast_graphrag._llm import OpenAIEmbeddingService, OpenAILLMService
import faiss
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain_community.vectorstores import FAISS
import glob
import PyPDF2

llm = ChatOpenAI(
    model="gpt-4o-mini",
)
embeddings = OpenAIEmbeddings(
    model= "text-embedding-3-small",
)
# index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

def generate_graph():
    
    DOMAIN = "The legal system and laws in Pakistan encompass a wide range of topics including constitutional rights, property disputes, civil and criminal procedures, labor laws, foreign investment regulations, family law, environmental protection, tax laws, intellectual property, consumer protection, cybercrime, inheritance, succession, arbitration, and human rights."
    QUERIES = [
        "What are the fundamental rights guaranteed by the Constitution of Pakistan?",
        "How does the legal system in Pakistan address property disputes?",
        "What are the procedures for filing a civil lawsuit in Pakistan?",
        "What are the key labor laws in Pakistan?",
        "How does the criminal justice system work in Pakistan?",
        "What are the regulations for foreign investment in Pakistan?",
        "How does family law operate in Pakistan?",
        "What are the environmental protection laws in Pakistan?",
        "What are the tax laws applicable to businesses in Pakistan?",
        "How are intellectual property rights protected in Pakistan?",
        "What are the consumer protection laws in Pakistan?",
        "How does the legal system handle cybercrime in Pakistan?",
        "What are the laws regarding inheritance and succession in Pakistan?",
        "What are the procedures for dispute resolution through arbitration in Pakistan?",
        "How does the legal system in Pakistan address human rights violations?"
    ]
    ENTITY_TYPES = [
        "Constitution",
        "Fundamental Rights",
        "Property Disputes",
        "Civil Lawsuit",
        "Labor Laws",
        "Criminal Justice System",
        "Foreign Investment",
        "Family Law",
        "Environmental Protection",
        "Legal Procedures",
        "Judiciary",
        "Legislation",
        "Regulations",
        "Court System",
        "Legal Framework",
        "Tax Laws",
        "Intellectual Property",
        "Consumer Protection",
        "Cybercrime",
        "Inheritance",
        "Succession",
        "Arbitration",
        "Human Rights"
    ]

    models.GraphData.objects.create(DOMAIN=DOMAIN, QUERIES=QUERIES, ENTITY_TYPES=ENTITY_TYPES)

    working_dir = "./myFile"
    grag = GraphRAG(
        working_dir=working_dir,
        domain=DOMAIN,
        example_queries="\n".join(QUERIES),
        entity_types=ENTITY_TYPES,
        config=GraphRAG.Config(
            llm_service=OpenAILLMService(
                api_key=os.getenv("OPENAI_API_KEY"),
            ),
            embedding_service=OpenAIEmbeddingService(
                model="text-embedding-3-small",
                api_key=os.getenv("OPENAI_API_KEY"),
                embedding_dim=1536,
            ),
        ),
    )
    print("Generating Graph")
    data_dir = "./data"
    file_content = ""

    # Read all .txt files
    for txt_file in glob.glob(os.path.join(data_dir, "*.txt")):
        with open(txt_file, 'r', encoding='utf-8') as file:
            file_content = file.read() + "\n"
        grag.insert(file_content)
    # Read all .pdf files
    # for pdf_file in glob.glob(os.path.join(data_dir, "*.pdf")):
    #     print(pdf_file)
    #     with open(pdf_file, 'rb') as file:
    #         reader = PyPDF2.PdfReader(file)
    #         for page_num in range(len(reader.pages)):
    #             page = reader.pages[page_num]
    #             file_content = page.extract_text() + "\n"
    #     grag.insert(file_content)

def get_query_results(query: str) -> str:

    working_dir = "./myFile"
    DOMAIN, QUERIES, ENTITY_TYPES = models.GraphData.objects.all().values_list('DOMAIN', 'QUERIES', 'ENTITY_TYPES')[0]
    grag = GraphRAG(
        working_dir=working_dir,
        domain=DOMAIN,
        example_queries="\n".join(QUERIES),
        entity_types=ENTITY_TYPES,
        config=GraphRAG.Config(
            llm_service=OpenAILLMService(
                api_key=os.getenv("OPENAI_API_KEY"),
            ),
            embedding_service=OpenAIEmbeddingService(
                model="text-embedding-3-small",
                api_key=os.getenv("OPENAI_API_KEY"),
            ),
        ),
    )
    res = grag.query(query, QueryParam(with_references=True))
    print(res)
    return res.response  