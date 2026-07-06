import pathlib

from chatbot.ingest import build_documents, list_text_files


def test_list_text_files_filters_non_text(tmp_path):
    dirs = tmp_path / 'docs'
    dirs.mkdir()
    (dirs / 'notes.md').write_text('# Notes\nHello world')
    (dirs / 'image.png').write_text('binarydata')
    files = list_text_files([str(dirs)])
    assert len(files) == 1
    assert files[0].name == 'notes.md'


def test_build_documents_creates_chunks(tmp_path):
    docs_dir = tmp_path / 'docs'
    docs_dir.mkdir()
    (docs_dir / 'sample.md').write_text(' '.join(['word'] * 400))
    docs = build_documents([str(docs_dir)], chunk_size=100, overlap=10)
    assert len(docs) > 1
    assert all('text' in doc and 'metadata' in doc for doc in docs)
