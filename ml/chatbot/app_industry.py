import argparse
import pathlib
import sys
from typing import List

ROOT_PATH = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from chatbot.ingest import build_documents
from chatbot.logger import configure_logger
from chatbot.safety import is_safe_input
from chatbot.langchain_agent import IndustryChatbot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='RevSense-AI industry-grade chatbot runner')
    parser.add_argument('--build-index', action='store_true', help='Build the LangChain vector store from source documents')
    parser.add_argument('--sources', nargs='+', default=['docs', 'sql', 'revsense_dbt/models'], help='Source directories to index')
    parser.add_argument('--query', type=str, help='Query to ask the chatbot')
    parser.add_argument('--top-k', type=int, default=4, help='Number of retrieved documents to use')
    parser.add_argument('--model', type=str, help='Optional model name for the generator')
    parser.add_argument('--embedding-model', type=str, help='Optional embedding model name')
    return parser.parse_args()


def main() -> int:
    logger = configure_logger()
    args = parse_args()
    chatbot = IndustryChatbot(
        model_name=args.model,
        embedding_model_name=args.embedding_model,
    )

    if not chatbot.available:
        logger.error('Industry chatbot dependencies are missing.')
        print(chatbot.get_dependency_message())
        return 1

    if args.build_index:
        logger.info('Building document index from sources: %s', args.sources)
        documents = build_documents(args.sources)
        if not documents:
            logger.error('No documents were discovered during ingestion.')
            print('No documents found to index. Verify source paths and file types.')
            return 1
        chatbot.build_vector_store(documents)
        logger.info('Successfully built industry-grade vector store with %d documents.', len(documents))
        print(f'Industry-grade index built with {len(documents)} document chunks.')
        return 0

    if not args.query:
        print('Query is required unless --build-index is used.')
        return 1

    safe, reason = is_safe_input(args.query)
    if not safe:
        logger.warning('Rejected unsafe input: %s', reason)
        print(f'Unsafe input: {reason}')
        return 1

    response = chatbot.query(args.query, top_k=args.top_k)

    print('\n=== Answer ===\n')
    print(response['answer'])
    print('\n=== Sources ===\n')
    for doc in response['source_documents']:
        print(doc.metadata.get('source', 'unknown'))

    logger.info(
        'Industry query executed: %s | Answer length: %d | Sources: %s',
        args.query,
        len(response['answer']),
        [doc.metadata.get('source', '') for doc in response['source_documents']],
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
