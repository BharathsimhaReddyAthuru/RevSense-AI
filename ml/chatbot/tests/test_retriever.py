import pathlib

from chatbot.ingest import build_documents
from chatbot.retriever import build_vector_store, query_vector_store


def test_vector_store_build_and_query(tmp_path):
    docs_dir = tmp_path / 'docs'
    docs_dir.mkdir()
    (docs_dir / 'sample.md').write_text('This is a test document about revenue forecasting and churn prediction.')
    documents = build_documents([str(docs_dir)], chunk_size=50, overlap=10)
    persist_dir = tmp_path / 'index'
    build_vector_store(documents, persist_directory=persist_dir)
    results = query_vector_store('revenue forecasting', persist_directory=persist_dir, top_k=1)
    assert len(results) == 1
    assert 'revenue forecasting' in results[0]['text']
