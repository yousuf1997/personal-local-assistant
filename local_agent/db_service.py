import os
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
import time

class DBService:

    def __init__(self):
        self.__uri = f"mongodb+srv://{os.getenv("MONGO_DB_USER")}:{os.getenv("MONGO_DB_PASS")}@local-agent.1elpt96.mongodb.net/"
        self.__client = MongoClient(self.__uri)
        self.__ping()
        self.__db_name = "local-agent"
        self.__embedded_data_collection_name = "embedd-data"
        self.__vectore_store = None
        self.__vector_search_retriever = None 
        

    def __ping(self):
        try:
            self.__client.admin.command("ping")
            print("Connected successfully")
        except Exception as e:
            raise Exception("The following error occurred: ", e)

    def store_embedding(self, embedding_model, split_docs):
        if len(split_docs) == 0:
            return
        
         ## batch the given documents to 50 
        batched_split_docs = self.__batch_docs(split_docs)

        print(f"Total batch of docs are {len(batched_split_docs)} about to be pushed to db.")

        ## push the first batch
        if self.__vectore_store is None:
            self.__vectore_store = MongoDBAtlasVectorSearch.from_documents(batched_split_docs[0], embedding_model, collection= self.__client[self.__db_name][self.__embedded_data_collection_name])
            print("Inserted the first batch")
            time.sleep(60) ## need this due to free version google rate limiting, 100 request perminute

        for index, batch in enumerate(batched_split_docs):
            if index > 0:
                self.__vectore_store.add_documents(documents=batch, batch_size=50)
                print(f"Inserted the batch of {index}")
                time.sleep(60) ## need this due to free version google rate limiting

        print("Sucessfully inserted the documents to the db.")     

    def vector_search(self, query, embedding_model):
        if self.__vectore_store is None:
            self.__vectore_store = MongoDBAtlasVectorSearch.from_connection_string(
                            self.__uri,
                            self.__db_name + "." + self.__embedded_data_collection_name,
                            embedding_model,
                            index_name="vector_index")

        if self.__vector_search_retriever is None:
            self.__vector_search_retriever = self.__vectore_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 3
                },
            )

        ## retrive the docs 
        return self.__vector_search_retriever.invoke(query)        

    
    def __batch_docs(self, split_docs : list):
        batched_docs = []
        current_batch_docs = []        
        document_index = 0

        while document_index < len(split_docs):
            if len(current_batch_docs) < 50: 
                current_batch_docs.append(split_docs[document_index])
            else:
                batched_docs.append(current_batch_docs)
                current_batch_docs = []
            document_index = document_index + 1

        ## add the left over
        if len(current_batch_docs) > 0:
            batched_docs.append(current_batch_docs)

        return batched_docs   
             