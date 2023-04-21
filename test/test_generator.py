from src.service import ContextGenerator

gen = ContextGenerator("polish")
polish_prompt = gen.generate("I want to learn more about various cultures.")
print(polish_prompt)

gen = ContextGenerator("free")
free_prompt = gen.generate("What is your favorite tabletop game?")
print(free_prompt)
