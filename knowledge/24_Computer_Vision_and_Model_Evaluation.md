# Computer Vision และการประเมินโมเดลภาพ

**หมวด:** Computer Vision / Deep Learning  
**คำค้น:** image preprocessing, convolution, classification, object detection, segmentation, augmentation, IoU, mAP, confusion matrix

## 1. งาน Computer Vision ต่างกันอย่างไร

- Image classification: ตอบว่าภาพมี class ใด
- Object detection: ระบุตำแหน่งกล่องและ class ของวัตถุ
- Semantic segmentation: กำหนด class ให้ทุก pixel
- Instance segmentation: แยกวัตถุแต่ละ instance
- OCR: อ่านข้อความจากภาพ
- Image similarity: เปรียบเทียบความคล้ายของภาพ

เลือก task ให้ตรงกับ output ที่ต้องการ อย่าใช้ classification หากต้องรู้ตำแหน่งวัตถุ

## 2. Image preprocessing

ขั้นตอนอาจรวม resize, crop, color conversion, normalization และ conversion เป็น tensor ต้องใช้ preprocessing ที่ตรงกับโมเดลที่ฝึกหรือใช้งาน หาก train กับ RGB แต่ inference ป้อน BGR จะทำให้ผลผิดได้

เก็บ image dimensions, color space, normalization mean/std และ interpolation method ใน configuration

## 3. Convolution

Convolution filter/kernel เลื่อนผ่านภาพเพื่อคำนวณ feature map ชั้นต้นอาจตอบสนองต่อ edge/texture และชั้นลึกเรียนรู้ pattern ที่ซับซ้อนขึ้น ขนาด kernel, stride, padding และ channel ส่งผลต่อขนาด output และ receptive field

## 4. Data augmentation

Augmentation เพิ่มความหลากหลาย เช่น flip, crop, rotate, brightness/contrast jitter แต่ต้องไม่เปลี่ยน label semantics เช่น ภาพตัวอักษรหรือป้ายที่การกลับด้านทำให้ความหมายเปลี่ยน การ augmentation ทำเฉพาะ training set ไม่ใช้กับ test set แบบสุ่ม

## 5. Class imbalance

ถ้าบาง class มีตัวอย่างน้อยมาก accuracy อาจหลอกตา ตรวจ per-class precision/recall, confusion matrix และ macro/weighted metrics พิจารณา class weighting, resampling หรือเก็บข้อมูลเพิ่มโดยไม่ทำให้ test leakage

## 6. Object detection metrics

IoU (Intersection over Union) วัดการทับซ้อนของ predicted box กับ ground-truth box:

`IoU = area(intersection) / area(union)`

Precision/recall ใช้กับการตรวจจับตาม confidence threshold และ IoU threshold ส่วน mAP สรุป average precision ตาม class และเงื่อนไขการประเมินที่กำหนด ต้องรายงาน protocol ให้ชัด เช่น IoU threshold และ dataset split

## 7. Dataset split และ leakage

ภาพจากวิดีโอหรือสถานการณ์เดียวกันที่คล้ายกันมากไม่ควรกระจาย train/test แบบสุ่มโดยไม่คิด เพราะโมเดลอาจจำฉากเดิมได้ ควรแบ่งตาม session, subject, machine, location หรือเวลาเมื่อเหมาะสม

## 8. ตรวจ error ด้วยภาพจริง

ดู false positive และ false negative แยกตาม lighting, angle, blur, occlusion, distance และ background อย่าดูเฉพาะภาพที่โมเดลทำได้ดี ควรสร้างชุด edge cases และทดสอบกับกล้อง/สภาพแวดล้อมจริง

## 9. Deployment considerations

วัด latency, memory, throughput, input resolution และ hardware target โมเดลที่แม่นบน workstation อาจช้าเกินไปบน edge device การ quantization อาจลด memory และเพิ่มความเร็ว แต่ต้องวัดผล accuracy หลัง quantize

## แหล่งอ้างอิง

- PyTorch tutorials: https://docs.pytorch.org/tutorials/
- PyTorch optimization loop: https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- Google ML Crash Course: https://developers.google.com/machine-learning/crash-course
