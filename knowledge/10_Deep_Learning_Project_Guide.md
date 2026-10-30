# Deep Learning สำหรับโปรเจกต์จบ

## 1. เมื่อไรควรใช้ Deep Learning

เหมาะกับข้อมูลซับซ้อน เช่น ภาพ เสียง ภาษา และข้อมูลจำนวนมาก
แต่ต้องใช้ข้อมูล/ทรัพยากรและการประเมินอย่างรอบคอบ สำหรับข้อมูลตารางขนาดเล็ก
โมเดลแบบดั้งเดิมอาจเหมาะกว่าและอธิบายง่ายกว่า

## 2. องค์ประกอบของ neural network

-   Input: features หรือ tensor
-   Layers: แปลง representation
-   Activation: เพิ่มความไม่เป็นเชิงเส้น
-   Loss: วัดความคลาดเคลื่อน
-   Optimizer: ปรับ weights
-   Epoch: การผ่านข้อมูลฝึกครบหนึ่งรอบ
-   Batch size: จำนวนตัวอย่างต่อการอัปเดตหนึ่งครั้ง

## 3. Training loop ต้องมีอะไร

1.  โหลด batch
2.  forward pass
3.  คำนวณ loss
4.  ล้าง gradient เก่า
5.  backpropagation
6.  optimizer step
7.  วัด validation metrics
8.  บันทึก checkpoint ที่ดีที่สุด

อย่าประเมินโมเดลด้วย training accuracy เพียงอย่างเดียว เพราะอาจ overfit

## 4. แยก train/validation/test

-   Train: ปรับพารามิเตอร์
-   Validation: เลือกโมเดล/ตั้งค่า
-   Test: ประเมินครั้งสุดท้าย ห้ามใช้ test set เป็นข้อมูลปรับโมเดลซ้ำ ๆ หากข้อมูลน้อย
    ให้ใช้ cross-validation ตามความเหมาะสมและอธิบายข้อจำกัด

## 5. ตัวอย่างโมเดลเล็กสำหรับข้อมูลตารางด้วย PyTorch

``` python
import torch
from torch import nn

class SmallClassifier(nn.Module):
    def __init__(self, n_features: int, n_classes: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, n_classes)
        )

    def forward(self, x):
        return self.net(x)

model = SmallClassifier(n_features=4, n_classes=2)
sample = torch.randn(8, 4)  # batch 8, features 4
logits = model(sample)
print(logits.shape)  # torch.Size([8, 2])
```

ตัวอย่างนี้แสดงโครงสร้างและ shape เท่านั้น ยังไม่ได้ฝึกโมเดล ข้อมูลจริงต้องจัด dtype,
labels, loss และ normalization ให้เหมาะสม

## 6. ปัญหาที่พบบ่อย

-   Overfitting: train ดี แต่ validation แย่
-   Underfitting: โมเดลยังเรียนรู้รูปแบบไม่ได้
-   Learning rate สูงเกินไป: loss แกว่งหรือ diverge
-   Class imbalance: โมเดลละเลยคลาสส่วนน้อย
-   Data leakage: ข้อมูลจาก validation/test รั่วเข้า train
-   Reproducibility: seed, dependency หรือ hardware ต่างกันทำให้ผลเปลี่ยน

แนวทาง: ทำ baseline, ดู learning curves, ลดความซับซ้อน, เพิ่มข้อมูลที่มีคุณภาพ, ปรับ
regularization และบันทึก configuration

## 7. ใช้ GPU อย่างมีเหตุผล

ตรวจ `torch.cuda.is_available()` ก่อนใช้ GPU เริ่ม batch size ต่ำบน GPU ที่
VRAM จำกัด และตรวจว่าโมเดลกับ tensor อยู่ device เดียวกัน หากเกิด out-of-memory
ให้ลด batch/image size หรือใช้โมเดลเล็กลง
ไม่จำเป็นต้องฝึกโมเดลใหญ่เพื่อให้โปรเจกต์ดูเป็น AI

## 8. บันทึกและโหลดโมเดล

เก็บ weights พร้อม config ของ preprocessing, class names, model version
และข้อมูลการฝึก หลีกเลี่ยงการโหลดไฟล์ checkpoint จากแหล่งที่ไม่น่าเชื่อถือ เพราะไฟล์
serialization บางรูปแบบอาจมีความเสี่ยงเมื่อโหลด

## 9. โปรเจกต์จบตัวอย่าง

จำแนกสถานะชิ้นงานหรือเสียงมอเตอร์: 1. ตั้ง label และเกณฑ์เก็บข้อมูล 2. สร้าง
baseline แบบง่าย 3. ฝึกโมเดลขนาดเล็ก 4. เปรียบเทียบ metrics บนชุด test 5.
วิเคราะห์ตัวอย่างที่ผิด 6. ทดสอบ inference บนเครื่องจริง 7. ทำหน้า dashboard
และบันทึกข้อจำกัด

## แบบฝึกหัด

1.  อธิบายบทบาทของ loss และ optimizer
2.  วาด training pipeline
3.  ระบุอาการ overfitting จาก learning curves ที่สมมติขึ้น
4.  ออกแบบการทดลองเปรียบเทียบโมเดลเล็กกับโมเดลใหญ่โดยควบคุมตัวแปร
