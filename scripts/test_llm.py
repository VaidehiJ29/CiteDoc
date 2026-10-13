from llm import generate, LLMError

print(generate("Reply with exactly: front desk works."))

try:
    generate("hello", provider="ollama")
except LLMError as e:
    print("Expected message:", e)