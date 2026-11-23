from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from db_service import DBService

class RAGService:

    def __init__(self, db_service : DBService):
        self.__db_service = db_service
        self.__text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150)
        self.__embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

    def embedd_docs(self, docs_file_path):
        loader = PyPDFLoader(docs_file_path)
        pages = loader.load()

        good_pages = []

        ## we want pages that has at least more than 20 words
        for page in pages:
            if len(page.page_content.split(" ")) > 20:
                good_pages.append(page)

        ## split it
        split_docs =  self.__text_splitter.split_documents(good_pages)

        ## now put them in the db
        self.__db_service.store_embedding(embedding_model=self.__embedding_model, split_docs=split_docs)

    def query(self, query):
        matched_docs = self.__db_service.vector_search(query, self.__embedding_model)
        page_contents = []
        
        for doc in matched_docs:
            splited_docs = doc.page_content.split(" ")
            cleaned_words = []
        
            ## remove \n
            for word in splited_docs:
                cleaned_words.append(word.replace("\n", ""))

            ## joined all cleaned words into single string 
            page_contents.append(" ".join(cleaned_words))

        return page_contents       

