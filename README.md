# doomn

**doomn** is an open-source tool for **image translation**, providing both automatic text detection + translation and an **online editor for translated text layers**. It supports **any source and target languages**, making it perfect for comics, posters, signs, UI screenshots, and more.

## ✨ Features

- 🖼️ Automatic text detection (OCR)
- 🌐 Translate between **any** languages
- 🎨 Online WYSIWYG editing of translated text layers
- 🛠️ Web frontend + Python backend
- 📦 Easily deployable demo and build scripts
- 📬 Commercial use requires author contact

---

## 🔧 Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Yarn or npm
- Recommended OS: macOS/Linux

### Backend (Python FastAPI)

```bash
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
````

### Frontend (React + Vite)

```bash
cd web
npm install -g yarn
yarn
yarn start
```

This will launch the web editor at:
👉 [http://localhost:3000](http://localhost:3000)

> Make sure the backend is running on port `8000`.

## 🖥️ Editor Preview

Here is a screenshot of the in-browser editor interface:
![editor.png](uploads%2Feditor.png)

---


## 🖼️ Demo Cases

Below are a few sample image translation cases:

| Original Image                                            | Translated Image                                               |
| --------------------------------------------------------- | -------------------------------------------------------------- |
|![fc278336-6ddf-4249-9efe-2e26f43f8c2d.jpg](uploads%2F0d7aacc6-5075-4b45-917e-aef3b364e0c1%2Ffc278336-6ddf-4249-9efe-2e26f43f8c2d.jpg)|![fc278336-6ddf-4249-9efe-2e26f43f8c2d_pic_trans.jpg](uploads%2F0d7aacc6-5075-4b45-917e-aef3b364e0c1%2Ffc278336-6ddf-4249-9efe-2e26f43f8c2d_pic_trans.jpg)|
|![1752997279457-O1CN01WgLcMj1z9pFtnLEqY_!!2865066672-913.png](uploads%2F02e74150-c574-45bd-9913-705a1c24645b%2F1752997279457-O1CN01WgLcMj1z9pFtnLEqY_%21%212865066672-913.png)|![1752997279457-O1CN01WgLcMj1z9pFtnLEqY_!!2865066672-913_pic_trans.png](uploads%2F02e74150-c574-45bd-9913-705a1c24645b%2F1752997279457-O1CN01WgLcMj1z9pFtnLEqY_%21%212865066672-913_pic_trans.png)|
|![2e8c5d9be0874ee9ab362716ba3d4f40.png](uploads%2F4cb8be016941401a97ae450868b73544%2F2e8c5d9be0874ee9ab362716ba3d4f40.png)|![2e8c5d9be0874ee9ab362716ba3d4f40_pic_trans.png](uploads%2F4cb8be016941401a97ae450868b73544%2F2e8c5d9be0874ee9ab362716ba3d4f40_pic_trans.png)|
|![009.png](uploads%2F009.png)|![009_pic_trans.png](uploads%2F009_pic_trans.png) |


```
doomn/
├── fabric_render/          # Python render fabric json to pic
├── server/                 # Python FastAPI server for OCR + translation
├── web/                    # React-based editor interface
├── uploads/                # Example images (original and translated)
└── README.md
```

---

## 📌 Roadmap
* [ ] AI-enhanced text placement

---

## 🙏 Thanks to These Projects

doomn is built on the shoulders of giants. We gratefully acknowledge the following open-source tools and frameworks:

* [Fabritor-web](https://github.com/sleepy-zone/fabritor-web) – Online Editor


## 📝 License & Commercial Use

This project is open-sourced under the [MIT License](LICENSE).

For **commercial use**, please contact the author via email:

📧 `bounty.wang@gmail.com`

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

