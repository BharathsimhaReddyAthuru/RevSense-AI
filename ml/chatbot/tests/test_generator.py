from chatbot.generator import ChatGenerator


def test_build_prompt_includes_context_and_question():
    generator = ChatGenerator(model_name='google/flan-t5-small')
    question = 'What is LTV?'
    context_documents = [
        {'text': 'Customer lifetime value is total revenue per customer.', 'metadata': {'source': 'docs/KPIs.md', 'chunk': 0}},
    ]
    prompt = generator.build_prompt(question, context_documents)
    assert 'Customer lifetime value' in prompt
    assert 'What is LTV?' in prompt
