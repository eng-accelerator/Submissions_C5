from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


class CVERetriever:
    def __init__(self, index_path: str = "./faiss_cve_index"):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        try:
            self.vectorstore = FAISS.load_local(
                index_path, self.embeddings, allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            self.vectorstore = None

    def search(self, query: str, k: int = 5):
        if not self.vectorstore:
            return []
        results = self.vectorstore.similarity_search(query, k=k)
        return results

    def get_context(self, query: str):
        results = self.search(query)
        context = "\n\n".join([doc.page_content for doc in results])
        return context
