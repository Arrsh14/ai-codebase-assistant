from generate import ask

test_questions = [
    "How does this app generate a motivational quote?",   # should work well — core feature
    "What port does the Flask server run on?",             # specific fact — tests precision
    "How does the frontend call the backend?",              # tests cross-file reasoning (JS -> Python)
    "What database does this app use?",                     # trick question — there is no database
]

for question in test_questions:
    print(f"\n{'='*60}")
    ask(question)