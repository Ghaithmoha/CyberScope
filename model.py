import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# تحميل البيانات المعالجة
try:
    X = pd.read_csv("X_processed.csv")
    y = pd.read_csv("y_processed.csv").squeeze()  # لتحويلها لسلسلة بدل DataFrame
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit(1)

# تأكد من وجود بيانات كافية لكل فئة (عدد العينات أكبر من عدد الفئات)
num_classes = len(y.unique())
num_samples = len(y)

if num_samples < num_classes * 2:
    print("Warning: Dataset might be too small for stratified splitting.")
    stratify_param = None
else:
    stratify_param = y

# تقسيم البيانات مع stratify إذا أمكن
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=stratify_param
)

# بناء نموذج Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# التنبؤ والتقييم
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model accuracy: {accuracy:.4f}")
print("Classification Report:")
print(classification_report(y_test, y_pred))
