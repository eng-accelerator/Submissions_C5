import json
import requests
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


def fetch_nvd_cves(keyword: str = "remote code execution", limit: int = 50):
    """Fetch CVEs from NVD API v2 (free)."""
    # Reduce limit for demo purposes
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={keyword}&resultsPerPage={limit}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()["vulnerabilities"]
    except Exception as e:
        print(f"Error fetching CVEs: {e}")
        return []


def build_cve_index(save_path: str = "./faiss_cve_index"):
    """Fetch CVEs and build FAISS index."""
    cves = fetch_nvd_cves()
    docs = []

    if not cves:
        # Fallback to local sample if API fails
        sample_cves = [
            {"id": "CVE-2021-44228", "description": "Apache Log4j2 JNDI RCE"},
            {"id": "CVE-2022-22965", "description": "Spring4Shell RCE"},
        ]
        for cve in sample_cves:
            docs.append(
                Document(
                    page_content=f"{cve['id']}: {cve['description']}",
                    metadata={"cve_id": cve["id"]},
                )
            )
    else:
        for item in cves:
            cve = item["cve"]
            desc = cve.get("descriptions", [{}])[0].get("value", "")
            cve_id = cve["id"]
            metrics = cve.get("metrics", {})
            cvss = metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {})
            docs.append(
                Document(
                    page_content=f"{cve_id}: {desc}",
                    metadata={"cve_id": cve_id, "cvss": cvss.get("baseScore", 0)},
                )
            )

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(save_path)
    print(f"✅ Built FAISS index with {len(docs)} CVE documents")
    return vectorstore


def load_cve_index(path: str = "./faiss_cve_index"):
    """Load an existing FAISS index."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
