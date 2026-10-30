# Machine Learning Evaluation: การวัดผล ความน่าเชื่อถือ และ Data Leakage

**หมวด:** Machine Learning / Data Science  
**คำค้น:** train validation test, cross validation, precision, recall, F1, ROC AUC, overfitting, leakage, baseline

## 1. แยก Train, Validation และ Test

- **Training set:** ใช้เรียนรู้พารามิเตอร์ของโมเดล
- **Validation set:** ใช้เลือกโมเดล ปรับ hyperparameters และ threshold
- **Test set:** ใช้ประเมินขั้นสุดท้ายเพียงหลังตัดสินใจเรื่องโมเดลแล้ว

ห้ามใช้ test set เป็นข้อมูลช่วยปรับโมเดลซ้ำ ๆ เพราะจะทำให้ test set ไม่เป็นตัวแทนข้อมูลใหม่อีกต่อไป

## 2. Data leakage คืออะไร

Data leakage เกิดเมื่อขั้นตอนสร้างโมเดลใช้ข้อมูลที่ไม่ควรทราบ ณ เวลาทำนาย เช่น คำนวณค่าเฉลี่ยเพื่อ standardize จากทั้งชุดข้อมูลก่อนแบ่ง train/test หรือใช้ข้อมูลอนาคตเป็น feature ของการทำนายในอดีต ผลคือคะแนนทดสอบดูดีเกินจริง แต่เมื่อนำไปใช้กับข้อมูลใหม่กลับแย่

วิธีป้องกัน:

1. แบ่ง train/test ก่อน fit preprocessing
2. ใช้ `Pipeline` ให้ preprocessing ถูก fit ภายในแต่ละ fold
3. แบ่งตามเวลาเมื่อข้อมูลมีลำดับเวลา
4. ข้อมูลจากบุคคล เครื่องจักร หรือกลุ่มเดียวกันไม่ควรกระจายข้าม train/test หากทำให้เกิดการจำข้อมูลเดิม

## 3. Confusion Matrix

สำหรับ binary classification:

- TP: ทำนาย positive และเป็น positive จริง
- TN: ทำนาย negative และเป็น negative จริง
- FP: ทำนาย positive แต่จริงเป็น negative
- FN: ทำนาย negative แต่จริงเป็น positive

สูตรสำคัญ:

- Accuracy = (TP + TN) / (TP + TN + FP + FN)
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = 2 × Precision × Recall / (Precision + Recall)

Accuracy อาจทำให้เข้าใจผิดเมื่อข้อมูลไม่สมดุล เช่น งานตรวจจับความผิดปกติที่ปกติมี 99% หากทำนายว่าปกติทุกกรณีก็ได้ accuracy 99% แต่ตรวจจับความผิดปกติไม่ได้เลย

## 4. เลือก metric ให้ตรงต้นทุนความผิดพลาด

- ต้องการลด false alarm: พิจารณา precision
- ต้องการไม่พลาดเหตุการณ์สำคัญ: พิจารณา recall
- ต้องการสมดุล precision/recall: พิจารณา F1
- ต้องการดูพฤติกรรมหลาย threshold: ใช้ precision-recall curve หรือ ROC curve ตามลักษณะข้อมูล
- งาน regression: MAE, MSE/RMSE และ R² มีความหมายต่างกัน ต้องเลือกตามต้นทุนของ error

อย่าเลือก metric เพราะเป็นค่าที่สูงที่สุด แต่เลือกตามผลกระทบจริงของความผิดพลาด

## 5. Cross-validation

K-fold cross-validation แบ่งข้อมูลเป็น K ส่วน สลับใช้หนึ่งส่วนเป็น validation และส่วนที่เหลือเป็น training แล้วเฉลี่ยคะแนน ช่วยให้ผลไม่ขึ้นกับการแบ่งครั้งเดียว แต่ต้องเลือกวิธีแบ่งให้เหมาะกับข้อมูล:

- `StratifiedKFold` สำหรับ classification ที่ต้องรักษาสัดส่วน class
- `GroupKFold` เมื่อมีข้อมูลจากกลุ่มเดียวกัน
- `TimeSeriesSplit` เมื่อข้อมูลมีลำดับเวลาและไม่ควร train ด้วยอนาคตเพื่อทำนายอดีต

## 6. Baseline และการเปรียบเทียบ

ก่อนใช้โมเดลซับซ้อน ให้ทำ baseline เช่น majority class, mean predictor หรือกฎง่าย ๆ แล้วเปรียบเทียบด้วย split และ metric เดียวกัน หากโมเดลซับซ้อนไม่ชนะ baseline อย่างสม่ำเสมอ ควรตรวจข้อมูลและ feature ก่อนเพิ่มขนาดโมเดล

## 7. Overfitting และ Underfitting

- Overfitting: คะแนน train ดีมาก แต่ validation/test แย่ มักเกิดจากโมเดลจำรายละเอียดหรือ noise
- Underfitting: คะแนน train และ validation แย่ อาจเกิดจาก feature ไม่พอ โมเดลเรียบง่ายเกินไป หรือฝึกไม่เหมาะสม

ควรดู learning curve, train/validation gap และ error analysis แทนการดู accuracy ตัวเดียว

## 8. Error analysis

สุ่มตรวจกรณีที่โมเดลผิด แบ่งประเภทความผิด เช่น ข้อมูลผิดป้ายกำกับ, class ซ้อนทับ, sensor noise, feature ไม่มีข้อมูลสำคัญ, distribution shift แล้วเลือกแก้ที่สาเหตุ อย่าปรับ threshold เพื่อซ่อนปัญหาข้อมูล

## 9. รายงานผลอย่างโปร่งใส

รายงาน dataset version, จำนวนตัวอย่าง, วิธี split, random seed, preprocessing, model version, hyperparameters, metric และข้อจำกัด อย่ารายงานเพียงคะแนนเดียวโดยไม่บอกวิธีประเมิน

## แหล่งอ้างอิง

- scikit-learn: Common pitfalls and data leakage: https://scikit-learn.org/stable/common_pitfalls.html
- scikit-learn: Model evaluation: https://scikit-learn.org/stable/modules/model_evaluation.html
- Google ML Crash Course: Classification metrics: https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
