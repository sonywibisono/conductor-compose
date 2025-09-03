## Netflix Conductor ##

*Sekilas tentang Netflix Conductor*

Netflix Conductor adalah mesin orkestrasi layanan mikro sumber terbuka yang dikembangkan di Netflix untuk mengelola dan mengoordinasikan alur kerja yang kompleks, terdistribusi, dan asinkron di berbagai layanan . Ia menggunakan bahasa domain spesifik (DSL) berbasis JSON untuk menentukan alur kerja dan memungkinkan pengembang membangun aplikasi yang sangat andal dengan menangani status eksekusi, menyediakan ketahanan dengan percobaan ulang dan fallback, serta menawarkan kemampuan pemantauan dan debugging melalui UI bawaan

*Apa fungsinya*

Conductor memungkinkan Anda menentukan alur kerja sebagai kode, yang menentukan urutan tugas yang perlu dijalankan. Tugas-tugas ini dapat berupa apa saja mulai dari menjalankan layanan mikro, memanggil API eksternal, memproses suatu peristiwa, atau bahkan menjalankan sub-alur kerja lainnya

### REQUIREMENT ###
1. Docker Desktop
2. Docker Command Line
3. Visual Studio Code
4. Node JS + NPM 

### Step ###
1. docker compose up -d
2. sh import.sh
3. Open Browser http://localhost:5001

*Landing page conductor*

![Landing page conductor](/images/landing-page.png)

![Workflow Definition](/images/workflow-definition.png)

![Workflow Editor](/images/workflow-editor.png)
