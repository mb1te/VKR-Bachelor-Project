import pandas as pd

from AnswerModel import AnswerModel

df = pd.read_csv('quiz.csv')

model = AnswerModel()

correct1, false1 = 0, 0
correct2, false2 = 0, 0

n_samples = 500

cur = 1
for index, row in df.head(n=n_samples).iterrows():
    question = row[1]
    choices = list(row[2:])

    try:
        print(f"Вопрос: {question}")
        ans = model.answer_question(question, choices)
        print(f"Ответ модели 1: {ans[0]}")
        print(f"Ответ модели 2: {ans[1]}")
        print(f"Правильный ответ: {choices[0]}")

        if ans[0] == row[2]:
            correct1 += 1
        else:
            false1 += 1

        if ans[1] == row[2]:
            correct2 += 1
        else:
            false2 += 1
    except Exception as e:
        print(e)

    print(f"{cur}/{n_samples}")
    cur += 1

print(f"Score1 = {correct1 / (correct1 + false1)}")
print(f"Score2 = {correct2 / (correct2 + false2)}")