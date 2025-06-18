import pandas as pd
from sklearn.preprocessing import LabelEncoder

# تحميل البيانات - تأكد من وجود الملف في نفس مجلد المشروع
file_path = "synthetic_logs.csv"

try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
    exit(1)

# ترميز الأعمدة النصية إلى أرقام
level_encoder = LabelEncoder()
df["level_encoded"] = level_encoder.fit_transform(df["level"])

message_encoder = LabelEncoder()
df["message_encoded"] = message_encoder.fit_transform(df["message"])

# حفظ البيانات المعالجة في ملفات منفصلة
X = df[["message_encoded"]]
y = df["level_encoded"]

X.to_csv("X_processed.csv", index=False)
y.to_csv("y_processed.csv", index=False)

print("✅ Data preprocessing completed and saved.")
