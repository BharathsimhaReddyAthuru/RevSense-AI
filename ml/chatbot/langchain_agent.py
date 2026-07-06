import os
import pathlib
from typing import Dict, List, Optional

DEFAULT_LLM_MODEL = os.getenv('CHAT_MODEL_NAME', 'google/flan-t5-small')
DEFAULT_EMBEDDING_MODEL = os.getenv('CHAT_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
DEFAULT_MAX_LENGTH = 256
DEFAULT_TEMPERATURE = 0.0
DEFAULT_PROMPT_TEMPLATE = (
    '{system}\n\n'
    'Context:\n{context}\n\n'
    'User question: {question}\n\n'
    'Answer:'
)

SYSTEM_PROMPT = (
    'You are a domain expert for an ecommerce revenue intelligence system called RevSense-AI. '
    'Answer user questions using only the provided context. '
    'If the answer is not contained in the context, respond with a brief and honest statement that you do not have enough information. '
    'Do not hallucinate or invent facts.'
)


import importlib
import importlib.util

# Avoid importing heavy submodules at import time. Use spec checks instead.
HuggingFaceEmbeddings = None
HuggingFacePipeline = None
Chroma = None
FAISS = None
Document = None

def _spec_exists(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


class IndustryChatbot:
    def __init__(
        self,
        model_name: Optional[str] = None,
        embedding_model_name: Optional[str] = None,
        persist_directory: Optional[pathlib.Path] = None,
    ):
        self.model_name = model_name or DEFAULT_LLM_MODEL
        self.embedding_model_name = embedding_model_name or DEFAULT_EMBEDDING_MODEL
        self.persist_directory = (
            pathlib.Path(persist_directory)
            if persist_directory is not None
            else pathlib.Path(__file__).resolve().parent / 'index' / 'langchain'
        )
        self.index = None
        self.llm = None
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        # Require core packages to be present via spec checks. This avoids
        # triggering heavy import-time errors inside langchain submodules.
        required = ['langchain', 'transformers', 'sentence_transformers']
        vector_providers = ['chromadb', 'faiss']
        for pkg in required:
            if not _spec_exists(pkg):
                return False
        if not any(_spec_exists(p) for p in vector_providers):
            return False
        return True

    def get_dependency_message(self) -> str:
        return (
            'Industry mode requires optional packages: langchain, transformers, sentence-transformers, '
            'and either chromadb or faiss-cpu. Install them in a compatible Python environment.'
        )

    def _build_embeddings(self):
        if not self.available or HuggingFaceEmbeddings is None:
            raise RuntimeError(self.get_dependency_message())
        return HuggingFaceEmbeddings(model_name=self.embedding_model_name)

    def _build_llm(self):
        if self.llm is not None:
            return self.llm

        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
        except ImportError:
            return None

        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            transformer_pipeline = pipeline(
                'text2text-generation',
                model=model,
                tokenizer=tokenizer,
                device=-1,
            )
            self.llm = HuggingFacePipeline(pipeline=transformer_pipeline)
            return self.llm
        except Exception:
            return None

    def _document_objects(self, documents: List[Dict[str, str]]):
        if Document is None:
            raise RuntimeError(self.get_dependency_message())
        return [Document(page_content=doc['text'], metadata=doc['metadata']) for doc in documents]

    def build_vector_store(self, documents: List[Dict[str, str]]) -> None:
        if not self.available:
            raise RuntimeError(self.get_dependency_message())

        docs = self._document_objects(documents)
        embeddings = self._build_embeddings()

        try:
            self.index = Chroma.from_documents(
                documents=docs,
                embedding=embeddings,
                persist_directory=str(self.persist_directory),
            )
        except Exception:
            self.index = FAISS.from_documents(documents=docs, embedding=embeddings)
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self.index.save_local(str(self.persist_directory))

    def _load_vector_store(self):
        if not self.available:
            raise RuntimeError(self.get_dependency_message())

        if self.index is not None:
            return self.index

        embeddings = self._build_embeddings()
        try:
            self.index = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=embeddings,
            )
        except Exception:
            self.index = FAISS.load_local(str(self.persist_directory), embeddings)

        return self.index

    def _build_prompt(self, question: str, documents: List[Document]) -> str:
        context = '\n\n'.join(
            f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
            for doc in documents
        )
        return DEFAULT_PROMPT_TEMPLATE.format(
            system=SYSTEM_PROMPT,
            context=context,
            question=question,
        )

    def _fallback_answer(self, documents: List[Document]) -> str:
        if not documents:
            return 'No relevant documents were available to answer the question.'

        return (
            'Unable to generate with the configured local model. Returning the most relevant retrieved content instead:\n\n'
            + '\n\n'.join(
                f"Source {idx + 1} ({doc.metadata.get('source', 'unknown')}): {doc.page_content}"
                for idx, doc in enumerate(documents)
            )
        )

    def query(self, query_text: str, top_k: int = 4) -> Dict[str, str]:
        index = self._load_vector_store()
        retriever = index.as_retriever(search_kwargs={'k': top_k})
        documents = retriever.get_relevant_documents(query_text)

        llm = self._build_llm()
        if llm is None:
            return {'answer': self._fallback_answer(documents), 'source_documents': documents}

        prompt = self._build_prompt(query_text, documents)
        output = llm(prompt, max_length=DEFAULT_MAX_LENGTH, temperature=DEFAULT_TEMPERATURE, do_sample=False)

        if isinstance(output, str):
            answer = output.strip()
        elif isinstance(output, list) and output:
            answer = output[0].get('generated_text', '').strip() or output[0].get('text', '').strip()
        else:
            answer = ''

        if not answer:
            answer = self._fallback_answer(documents)

        return {'answer': answer, 'source_documents': documents}
