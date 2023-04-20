from src.service import Generator

gen = Generator("polish")
polish_prompt = gen.generate("I want to learn more about various cultures.")
print(polish_prompt)

gen = Generator("free")
free_prompt = gen.generate("What is your favorite tabletop game?")
print(free_prompt)
