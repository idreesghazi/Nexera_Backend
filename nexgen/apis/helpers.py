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

def get_conversation_history(chat_id) -> str:
    chat_messages = models.ChatMessage.objects.filter(ChatID_id=chat_id).order_by('-ChatMessageID')[:10]
    conversation = ""
    for message in chat_messages:
        conversation += f"{'User: ' if message.HumanFlag else 'System: '}{message.Message}\n"
    return conversation

def get_query_results(query: str, chat_id = None) -> str:

    if chat_id:
        conversation = get_conversation_history(chat_id)
        query = "Chat History:\n"+conversation + "Answer the Question\nUser:" + query

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

    return res.response  

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, model_validator

class TaxGenerator(BaseModel):
    tax_report : str = Field(description="""
            A detailed tax report generated based on the provided user data, including personal and business information, income details, expense and deduction details, and tax payments and compliance. The report will calculate total taxable income, apply Pakistan’s tax slabs to compute the final tax liability, check for any tax refund due, and provide a summary table with total income, total deductions, net taxable income, tax payable or refundable, and filer status & compliance recommendations. The final output will be a well-structured, professional tax report in markdown or PDF format, ready for submission to FBR.
            """
    )
    @model_validator(mode="after")
    @classmethod	
    def validate_types(cls, values: dict) -> dict:
        return values


def tax_report_generation(data):
    system_template = """
    You are an AI Tax Assistant specialized in generating detailed tax reports for individuals and businesses in Pakistan. Your task is to create a well-structured tax report using user-provided financial data, ensuring compliance with the latest FBR tax slabs and withholding tax regulations.

    User-Provided Data:
    1️ Personal & Business Information:

    Full Name: {user_name}
    CNIC or NTN: {cnic}
    Taxpayer Category: {category} (e.g., Individual, Business, Freelancer)
    Business Name (if applicable): {business_name}
    Business Registration Details: {registration_details}
    Filer Status: {active_filer} (Yes/No)
    2️ Income Sources:

    Salary Income: {salary}
    Freelance/Contract Income: {freelance_income}
    Business Revenue: {business_revenue}
    Rental Income: {rental_income}
    Capital Gains (Stocks, Real Estate, Crypto): {capital_gains}
    Foreign Remittances: {foreign_remittances}
    Other Income (Commission, Prizes, etc.): {details_and_amounts}
    3️ Deductions & Tax-Exempt Items:

    Business Expenses (Rent, Salaries, Travel, etc.): {expenses}
    Zakat Paid: {zakat}
    Charitable Donations: {charitable_donations}
    Medical & Education Expenses: {medical_education_expenses}
    Loan Interest Payments: {loan_expense}
    Other Deductible Expenses: {other_expense}
    4️ Withholding Tax & Advance Tax Payments:

    Advance Tax Paid: {advance_tax}
    Withholding Tax on Salary (If any): {withholding_tax}
    Withholding Tax on Business Transactions: {business_withholding_tax}
    Withholding Tax on Property Transactions: {property_withholding_tax}
    Withholding Tax on Banking Transactions & Cash Withdrawals: {banking_withholding_tax}
    Withholding Tax on Utility Bills & Mobile Recharges: {utility_withholding_tax}
    5️ Tax Compliance & FBR Recommendations:

    Previous Tax Filings: {previous_filing} (Yes/No)
    Applicable Tax Slabs (2024 FBR Rates): Applied based on taxable income brackets
    Exemptions & Refund Eligibility: Evaluated from deductions & advance tax
    Instructions for AI:
    1️ Calculate Taxable Income

    Total Taxable Income = Total Income - Deductions
    Apply FBR tax slabs (2024 rates) from the uploaded document.
    2️ Apply Withholding Tax Rules

    Match withholding tax rates to applicable income types (Salary, Business, Banking, Property, etc.).
    Subtract withholding tax paid from the final tax payable.
    3️ Determine Final Tax Payable or Refund

    If Advance Tax Paid > Final Tax Due, calculate refund.
    If Advance Tax Paid < Final Tax Due, calculate outstanding tax liability.
    4️ Generate a Structured Tax Report in Markdown/PDF Format
    Final Report Should Include:

    Taxpayer Information
    Income Breakdown
    Deductions & Withholding Tax Summary
    Tax Calculation (Net Taxable Income, FBR Tax Slabs)
    Final Tax Payable or Refundable
    FBR Compliance Recommendations
    """
    parser = PydanticOutputParser(pydantic_object=TaxGenerator)
    prompt_template = PromptTemplate(
        template=system_template,
        input_variables=[
        "user_name", "cnic", "category", "business_name", "registration_details", "active_filer", "salary", "freelance_income", "business_revenue", "rental_income", "capital_gains", "foreign_remittances", "details_and_amounts", "expenses", "zakat", "charitable_donations", "medical_education_expenses", "loan_expense", "other_expense", "advance_tax", "withholding_tax", "business_withholding_tax", "property_withholding_tax", "banking_withholding_tax", "utility_withholding_tax", "previous_filing"
        ],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt_template | llm

    response = chain.invoke({
        "user_name": data.get("user_name", ""),
        "cnic": data.get("cnic", ""),
        "category": data.get("category", ""),
        "business_name": data.get("business_name", ""),
        "registration_details": data.get("registration_details", ""),
        "active_filer": data.get("active_filer", ""),
        "salary": data.get("salary", 0),
        "freelance_income": data.get("freelance_income", 0),
        "business_revenue": data.get("business_revenue", 0),
        "rental_income": data.get("rental_income", 0),
        "capital_gains": data.get("capital_gains", 0),
        "foreign_remittances": data.get("foreign_remittances", 0),
        "details_and_amounts": data.get("details_and_amounts", ""),
        "expenses": data.get("expenses", 0),
        "zakat": data.get("zakat", 0),
        "charitable_donations": data.get("charitable_donations", 0),
        "medical_education_expenses": data.get("medical_education_expenses", 0),
        "loan_expense": data.get("loan_expense", 0),
        "other_expense": data.get("other_expense", 0),
        "advance_tax": data.get("advance_tax", 0),
        "withholding_tax": data.get("withholding_tax", 0),
        "business_withholding_tax": data.get("business_withholding_tax", 0),
        "property_withholding_tax": data.get("property_withholding_tax", 0),
        "banking_withholding_tax": data.get("banking_withholding_tax", 0),
        "utility_withholding_tax": data.get("utility_withholding_tax", 0),
        "previous_filing": data.get("previous_filing", "")
    })
    return response

def generate_title(message: str) -> str:
    system_template = """
    Generate title for the following coversation: 
    User: {user_message}
    System: {system_message}
    """
    prompt_template = PromptTemplate(template=system_template, input_variables=["user_message", "system_message"])
    system_message = get_query_results(message)

    chain = prompt_template | llm
    response = chain.invoke({
        "user_message": message,
        "system_message": system_message
    })
    return response.content, system_message