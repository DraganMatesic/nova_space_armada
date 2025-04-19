from random import randrange
from string import printable


password = []
chars = printable.strip()
for i in range(32):
    idx = randrange(0, 64)
    password.append(chars[idx])

password_str = ''.join(password)
print(password_str)