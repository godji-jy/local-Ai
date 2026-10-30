# คณิตศาสตร์พื้นฐานที่จำเป็นสำหรับ Machine Learning และ Deep Learning

**หมวด:** Mathematics / AI / Data Science  
**คำค้น:** vector, matrix, dot product, derivative, gradient, probability, statistics, loss, cosine similarity

## 1. Scalar, Vector และ Matrix

- Scalar คือค่าตัวเลขหนึ่งค่า เช่น อุณหภูมิ 35.2
- Vector คือชุดตัวเลขที่มีลำดับ เช่น `[rpm, temperature, current]`
- Matrix คือข้อมูลสองมิติ เช่น ตารางตัวอย่างหลายแถวและหลาย feature
- Tensor คือโครงสร้างข้อมูลหลายมิติที่ใช้กับ deep learning

หาก dataset มี 1,000 ตัวอย่าง และแต่ละตัวอย่างมี 5 feature จะเขียนเป็น matrix ขนาด 1000 × 5 ได้

## 2. Dot Product

สำหรับเวกเตอร์ `a` และ `b` ที่ยาวเท่ากัน:

`a · b = Σ(a_i b_i)`

ตัวอย่าง `a = [1, 2, 3]`, `b = [4, 5, 6]` ผลคือ `1×4 + 2×5 + 3×6 = 32`

Dot product ใช้ใน linear model, neural network และการคำนวณความคล้ายคลึง หากเวกเตอร์มีค่ามากขึ้นเพราะขนาด ไม่ใช่ทิศทาง ควรพิจารณา normalization หรือ cosine similarity

## 3. Cosine Similarity

`cosine_similarity(a,b) = (a·b) / (||a|| ||b||)`

ค่ามักอยู่ระหว่าง -1 ถึง 1 ในกรณีเวกเตอร์ทั่วไป ค่าที่ใกล้ 1 หมายถึงทิศทางคล้ายกัน ค่าใกล้ 0 หมายถึงตั้งฉาก และใกล้ -1 หมายถึงทิศทางตรงข้าม ใน embedding ของข้อความ ความหมายของคะแนนขึ้นกับโมเดล embedding และการฝึก จึงไม่ควรกำหนด threshold เดียวใช้กับทุก embedding model

## 4. Derivative และ Gradient

Derivative อธิบายว่าฟังก์ชันเปลี่ยนเร็วเพียงใดเมื่อเปลี่ยนตัวแปร ส่วน gradient เป็นเวกเตอร์ของอนุพันธ์ย่อยตามพารามิเตอร์ทุกตัว ใช้บอกทิศทางการเพิ่มขึ้นเร็วที่สุดของฟังก์ชัน

Gradient descent ปรับพารามิเตอร์ในทิศทางตรงข้ามกับ gradient:

`theta_new = theta_old - learning_rate * gradient`

learning rate สูงเกินไปอาจทำให้ loss กระโดดหรือไม่ลู่เข้า ต่ำเกินไปทำให้เรียนรู้ช้า ต้องเลือกจาก validation และพฤติกรรมการฝึก

## 5. Probability และ Bayes

ความน่าจะเป็นอยู่ระหว่าง 0 และ 1 สำหรับเหตุการณ์ A และ B:

`P(A|B) = P(B|A) P(A) / P(B)` เมื่อ `P(B) > 0`

แนวคิดนี้ช่วยปรับความเชื่อเมื่อมีหลักฐานใหม่ แต่ probability ที่โมเดลส่งออกไม่ได้แปลว่า calibrated confidence เสมอไป ควรตรวจ calibration บนข้อมูล validation หากต้องใช้ความน่าจะเป็นเชิงตัดสินใจ

## 6. ค่าเฉลี่ย ความแปรปรวน และส่วนเบี่ยงเบนมาตรฐาน

Mean บอกค่ากลางแบบเฉลี่ย ส่วน variance/standard deviation บอกการกระจาย Standard deviation มีหน่วยเดียวกับข้อมูล จึงตีความได้ง่ายกว่า variance ในหลายกรณี

ข้อมูลที่มี outlier มากอาจทำให้ mean และ standard deviation บิดเบือน ควรดู median, IQR และ histogram เพิ่มเติม

## 7. Normalization และ Standardization

- Min-max scaling: แปลงช่วงข้อมูลให้อยู่ในช่วง เช่น 0–1 โดยอาศัย min/max
- Standardization: `(x - mean) / standard_deviation`
- Robust scaling: ใช้ median และ IQR เพื่อลดผลของ outliers

ค่าพารามิเตอร์ของ scaler ต้อง fit จาก training set เท่านั้น จากนั้นใช้ transform กับ validation/test ด้วยค่าชุดเดิม เพื่อป้องกัน data leakage

## 8. Loss Function

- MAE: เฉลี่ย absolute error ทนต่อ outlier มากกว่า MSE
- MSE: ลงโทษ error ขนาดใหญ่แรงขึ้น
- Cross-entropy: ใช้กับการจำแนกประเภทและความน่าจะเป็นของ class

Loss ที่ใช้ฝึกไม่จำเป็นต้องเป็น metric ที่ใช้รายงานผล ต้องเข้าใจว่าฟังก์ชันวัดอะไรและสอดคล้องกับเป้าหมายหรือไม่

## 9. Sampling และความไม่แน่นอน

ค่าจาก sample เป็นการประมาณประชากร ต้องระบุจำนวนตัวอย่าง วิธีเลือก และความไม่แน่นอน อย่าสรุปว่าความสัมพันธ์เป็นเหตุเป็นผลเพียงเพราะตัวแปรสัมพันธ์กัน

## แหล่งอ้างอิง

- Khan Academy Statistics and Probability: https://www.khanacademy.org/math/statistics-probability
- Google ML Crash Course: https://developers.google.com/machine-learning/crash-course
- PyTorch Autograd: https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html
