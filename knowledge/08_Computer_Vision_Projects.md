# Computer Vision สำหรับโปรเจกต์จบ

## 1. เลือกโจทย์ให้เหมาะกับข้อมูล

โจทย์หลัก: - Classification: จัดประเภทภาพ เช่น ชิ้นงานปกติ/มีตำหนิ - Object
detection: ระบุตำแหน่งวัตถุด้วย bounding box - Segmentation:
แยกพื้นที่ของวัตถุเป็นระดับพิกเซล - OCR: อ่านตัวอักษรจากภาพ - Tracking:
ติดตามวัตถุข้ามเฟรม

อย่าเลือกโมเดลก่อนกำหนดนิยามคลาส แหล่งข้อมูล และวิธีประเมินผล

## 2. เตรียม dataset

1.  ขออนุญาตและตรวจสิทธิ์การใช้ภาพ
2.  กำหนด label guide พร้อมตัวอย่าง
3.  แยก train/validation/test โดยหลีกเลี่ยงภาพซ้ำหรือภาพจากวิดีโอเดียวกันข้ามชุด
4.  บันทึกที่มาของข้อมูลและเวอร์ชัน annotation
5.  ตรวจ class imbalance และความหลากหลายของแสง/มุม/พื้นหลัง

หากภาพทดสอบเกือบเหมือนภาพฝึก ผลประเมินจะสูงเกินจริง

## 3. ตัวอย่าง classification ด้วย transfer learning

ตัวอย่างแนวทาง PyTorch (ต้องติดตั้ง PyTorch และ torchvision ให้ตรงกับเครื่อง):

``` python
import torch
from torch import nn
from torchvision import models

num_classes = 2
weights = models.ResNet18_Weights.DEFAULT
model = models.resnet18(weights=weights)
model.fc = nn.Linear(model.fc.in_features, num_classes)

for name, param in model.named_parameters():
    param.requires_grad = name.startswith("fc.")

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print("Training device:", device)
```

โค้ดนี้เตรียมโมเดล ไม่ใช่ training loop ที่สมบูรณ์ การใช้ pretrained weights
ต้องดาวน์โหลดไว้ก่อนหากต้องทำงาน offline และต้องตรวจ license/เงื่อนไขของ weights

## 4. การประเมินผล

-   Classification: precision, recall, F1, confusion matrix
-   Detection: mAP และ IoU
-   Segmentation: IoU หรือ Dice score
-   OCR: character/word error rate

ตรวจภาพที่ทายผิดเป็นกลุ่ม เช่น แสงน้อย มุมเอียง หรือวัตถุถูกบัง
เพื่อหาแนวทางเพิ่มข้อมูลหรือปรับ pipeline

## 5. การประมวลผลภาพก่อนโมเดล

งานอาจต้อง resize, normalize, crop หรือปรับ contrast แต่ต้องใช้ preprocessing
แบบเดียวกันระหว่าง train และ inference หลีกเลี่ยงการปรับภาพที่ทำให้ข้อมูลสำคัญหายไป

## 6. ทำงานบนเครื่องที่ VRAM จำกัด

-   เริ่มจากภาพขนาดเล็กและ batch size ต่ำ
-   ใช้ transfer learning แทนฝึกโมเดลใหญ่จากศูนย์
-   ปิด gradient ใน inference ด้วย `torch.inference_mode()`
-   ทดสอบ CPU fallback
-   บันทึกเวลา inference และหน่วยความจำ ไม่ดูแต่ accuracy

## 7. เชื่อมต่อ dashboard

Pipeline ตัวอย่าง: กล้อง/ไฟล์ภาพ → ตรวจ input → preprocess → inference →
ผลลัพธ์พร้อม confidence → บันทึกผล → dashboard

แสดง confidence และข้อความว่าโมเดลอาจผิดพลาดได้ อย่าใช้ผล CV
เพียงอย่างเดียวตัดสินเรื่องความปลอดภัยที่มีผลร้ายแรงโดยไม่มีระบบสำรอง

## โปรเจกต์จบตัวอย่าง

**ตรวจตำหนิชิ้นงานในห้องปฏิบัติการ** - สร้างชุดภาพที่ได้รับอนุญาต - ทำ baseline ด้วย
feature/โมเดลเบื้องต้น - เปรียบเทียบกับ transfer learning - รายงาน F1 และเวลา
inference - วิเคราะห์ผลผิดพลาดตามสภาพแสง - สร้างหน้าสรุปผลและข้อจำกัด

## แบบฝึกหัด

1.  อธิบายความต่าง classification กับ detection
2.  ออกแบบ label guide สำหรับชิ้นงาน 3 คลาส
3.  วางแผนแยก dataset ที่มาจากวิดีโอ
4.  วิเคราะห์ผลเสียของการใช้ test set ปรับโมเดลซ้ำ ๆ
