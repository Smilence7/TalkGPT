import os.path

import playsound

save_path = os.path.join(os.path.normpath("../saved/record"), "rec-20230423-230008-reply.mp3")
print(os.path.normpath(os.path.abspath(save_path)))
print(save_path)

playsound.playsound(os.path.normpath(os.path.abspath(save_path)))