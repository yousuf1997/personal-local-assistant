import os
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch

class DBService:

    def __init__(self):
        self.__uri = f"mongodb+srv://{os.getenv("MONGO_DB_USER")}:{os.getenv("MONGO_DB_PASS")}@local-agent.1elpt96.mongodb.net/"
        self.__client = MongoClient(self.__uri)
        self.__ping()
        self.__db_name = "local-agent"
        self.__embedded_data_collection_name = "embedd-data"
        self.__vectore_store = None 
        

    def __ping(self):
        try:
            self.__client.admin.command("ping")
            print("Connected successfully")
        except Exception as e:
            raise Exception("The following error occurred: ", e)

    def store_embedding(self, embedding_model, split_docs):
        if self.__vectore_store is None:
            self.__vectore_store = MongoDBAtlasVectorSearch.from_documents(split_docs, embedding_model, collection= self.__client[self.__db_name][self.__embedded_data_collection_name])
        else:
            ## batch the given documents to 50 
            batched_split_docs = self.__batch_docs(split_docs)

            for batch in batched_split_docs:
                 self.__vectore_store.add_documents(documents=batch, batch_size=50)

            print("Sucessfully inserted the documents to the db.")     

    def __batch_docs(split_docs):
        batched_docs = []
        current_batch_docs = []        
        document_index = 0

        while document_index < len(split_docs):
            if len(current_batch_docs) < 50: 
                current_batch_docs.append(split_docs)
            else:
                batched_docs.append(current_batch_docs)
                current_batch_docs = []
            document_index = document_index + 1        