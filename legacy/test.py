import easyocr

reader = easyocr.Reader(['ja'])

result = reader.readtext("input/2026-06-10233843.png")

for r in result:
    print(r[1])