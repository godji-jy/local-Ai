# Machine Learning และ Data Science สำหรับโปรเจกต์จบ

## เป้าหมาย

เอกสารนี้เน้นกระบวนการทำงานกับข้อมูลตั้งแต่ตั้งโจทย์ ตรวจคุณภาพข้อมูล สร้าง baseline
ประเมินผล และสื่อสารผลลัพธ์ โดยรวม Machine Learning กับ Data Science
ไว้ในไฟล์เดียว

## 1. แปลงปัญหาเป็นโจทย์ข้อมูล

ตัวอย่าง: ทำนายว่ามอเตอร์มีความเสี่ยงผิดปกติหรือไม่ - หน่วยข้อมูลหนึ่งแถว:
ช่วงเวลาการอ่านเซนเซอร์หนึ่งช่วง - Features: อุณหภูมิ, กระแส, RPM, vibration
RMS - Target: สถานะผิดปกติ 0/1 - การใช้งานจริง: ช่วยเตือนให้ตรวจสอบ
ไม่ใช่แทนระบบตัดไฟเพื่อความปลอดภัย

ก่อนเริ่ม ให้ระบุผู้ใช้ปลายทาง การตัดสินใจที่จะใช้ผลทำนาย และต้นทุนของ false
positive/false negative

## 2. สำรวจข้อมูล (EDA)

``` python
import pandas as pd

df = pd.read_csv("sensor_data.csv")
print(df.shape)
print(df.head())
print(df.dtypes)
print(df.isna().sum())
print(df.describe(include="all"))
```

ตรวจสอบ: - จำนวนแถว/คอลัมน์และชนิดข้อมูล - ค่าว่างและค่าซ้ำ - ค่าที่เป็นไปไม่ได้ เช่น
RPM ติดลบในระบบที่วัดรอบทิศทางเดียว - class imbalance เช่น ข้อมูลผิดปกติมีน้อยมาก -
ข้อมูลรั่วไหล (data leakage) เช่น ใช้คอลัมน์ที่ถูกสร้างหลังเกิดเหตุมาเป็น feature

## 3. แยกชุดข้อมูลให้ถูกต้อง

สำหรับข้อมูลตามเวลา ให้แบ่งตามลำดับเวลา ไม่สุ่มทุกแถว เพราะข้อมูลใกล้กันอาจรั่วไหลข้ามชุด
train/test

``` python
df = df.sort_values("timestamp")
cut = int(len(df) * 0.8)
train = df.iloc[:cut]
test = df.iloc[cut:]
```

หากเป็นข้อมูลหลายเครื่อง
ควรพิจารณาแบ่งตามเครื่องเพื่อทดสอบว่าโมเดลใช้กับเครื่องที่ไม่เคยเห็นได้หรือไม่

## 4. สร้าง baseline ก่อน

เริ่มจากกฎง่าย ๆ หรือโมเดลพื้นฐาน แล้วจึงเปรียบเทียบกับโมเดลซับซ้อน เช่น Logistic
Regression, Decision Tree หรือ Random Forest

``` python
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

features = ["temperature", "current", "rpm", "vibration_rms"]
X = df[features]
y = df["fault"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
model = make_pipeline(
    SimpleImputer(strategy="median"),
    RandomForestClassifier(n_estimators=150, random_state=42,
                           class_weight="balanced")
)
model.fit(X_train, y_train)
print(classification_report(y_test, model.predict(X_test), zero_division=0))
```

โค้ดนี้เป็นตัวอย่างสำหรับข้อมูลที่แถวเป็นอิสระต่อกัน หากข้อมูลเป็น time series
ต้องใช้การแบ่งตามเวลาแทน random split

## 5. เข้าใจ metrics

-   Accuracy: สัดส่วนทายถูกทั้งหมด อาจหลอกตาเมื่อคลาสไม่สมดุล
-   Precision: ในสิ่งที่โมเดลแจ้งเตือน มีสัดส่วนเท่าไรที่เป็นจริง
-   Recall: ในเหตุผิดปกติจริง โมเดลตรวจพบได้เท่าไร
-   F1: ค่าเฉลี่ยเชิงสมดุลของ precision และ recall
-   Confusion matrix: แสดง true/false positive/negative

เลือก metric ตามความเสี่ยงของงาน อย่ารายงาน accuracy อย่างเดียว

## 6. Data Science workflow

1.  ตั้งคำถามที่วัดผลได้
2.  เก็บข้อมูลและบันทึกแหล่งที่มา
3.  ตรวจคุณภาพและสิทธิ์การใช้ข้อมูล
4.  ทำ EDA
5.  สร้าง baseline
6.  แบ่งข้อมูลอย่างเหมาะสม
7.  ฝึกและประเมินโมเดล
8.  วิเคราะห์กรณีที่ทายผิด
9.  ทำรายงานหรือ dashboard
10. วางแผนตรวจ drift หลังนำไปใช้

## 7. บันทึกผลทดลอง

เก็บอย่างน้อย: ชื่อโมเดล, เวอร์ชันข้อมูล, features, วิธีแบ่งชุดข้อมูล, random seed,
metrics, วันที่ทดลอง และข้อจำกัด อย่าเลือกโมเดลจากผล test ซ้ำ ๆ จน test
กลายเป็นชุดที่ใช้ปรับโมเดล

## โปรเจกต์จบตัวอย่าง

**ระบบวิเคราะห์แนวโน้มความผิดปกติของมอเตอร์** - เก็บข้อมูลเซนเซอร์พร้อม timestamp -
สร้าง baseline ด้วย threshold - เปรียบเทียบกับ Random Forest -
สร้างกราฟแนวโน้มและ confusion matrix - ให้ผู้ใช้ยืนยันผลแจ้งเตือนเพื่อเก็บ feedback -
เขียนข้อจำกัด: ข้อมูลจำลองไม่เท่ากับข้อมูลจากเครื่องจริง

## แบบฝึกหัด

1.  สร้างกราฟ histogram ของทุก feature
2.  หาค่าว่างและค่าผิดปกติ แล้วอธิบายวิธีจัดการ
3.  เปรียบเทียบ baseline กับ Random Forest
4.  อธิบายว่าทำไมข้อมูลจากอนาคตไม่ควรอยู่ในชุดฝึก
5.  เขียนรายงานผลโมเดลหนึ่งหน้า พร้อมข้อจำกัด
