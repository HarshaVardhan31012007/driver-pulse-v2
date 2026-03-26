# Driver Pulse – Simple Deployment Guide

## Requirements

Make sure your system has:

* Python **3.8 or higher**
* **Git**
* **pip**
* Internet connection

(Optional)

* Docker (only if you want container deployment)

---

# 1. Run Locally (Recommended)

### Step 1 – Download the Project

```bash
git clone <your-repository-url>
cd driver-pulse
```

Or download the ZIP from GitHub and extract it.

---

### Step 2 – Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

---

### Step 3 – Install Required Libraries

```bash
pip install -r requirements.txt
```

---

### Step 4 – Generate Sample Data

Run:

```bash
python main.py --generate-sample-data
```

This will create the dataset required for the dashboard.

---

### Step 5 – Start the Dashboard

```bash
streamlit run dashboard/app.py
```

---

### Step 6 – Open the App

Open your browser and go to:

```
http://localhost:8501
```

Your **Driver Pulse Dashboard** will appear.

---

# 2. Stop the Application

Press:

```
CTRL + C
```

in the terminal.

---

# 3. Deploy Online (Streamlit Cloud – Easy)

### Step 1 – Push Code to GitHub

```bash
git init
git add .
git commit -m "Driver Pulse Project"
git remote add origin <your-github-repo>
git push -u origin main
```

---

### Step 2 – Deploy

1. Go to
   https://share.streamlit.io

2. Click **New App**

3. Select your GitHub repository

4. Set main file:

```
dashboard/app.py
```

5. Click **Deploy**

Your app will be live in **2 minutes**.

---

# 4. Common Problems

### Port already in use

Run with different port:

```bash
streamlit run dashboard/app.py --server.port 8502
```

---

### Missing libraries

Run:

```bash
pip install -r requirements.txt
```

---

### Python version error

Check:

```bash
python --version
```

Must be **3.8+**

---

# 5. Project Structure

```
driver-pulse
│
├── dashboard
│   ├── app.py
│   └── pages
│
├── data
├── outputs
├── utils
├── main.py
├── requirements.txt
```

---

# 6. Quick Run (Only 3 Commands)

```bash
pip install -r requirements.txt
python main.py --generate-sample-data
streamlit run dashboard/app.py
```

---

# Team

**Team Velocity**

Driver Pulse – AI Driver Safety & Earnings Analytics
