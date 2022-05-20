from datetime import datetime

now = datetime.now()

X = now.strftime("%d-%m-%Y")

print(X)