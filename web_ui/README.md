# GLM v3.0 - Web UI

Interactive web interface for the GLM Symbolic System ∆∞Ο

## 🚀 Quick Start

### Prerequisites
- API server running on `http://localhost:8000`
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Running the Web UI

```bash
# Option 1: Using Python's built-in server
cd web_ui
python3 -m http.server 8080

# Option 2: Using Node.js http-server
npx http-server web_ui -p 8080

# Option 3: Using any other static server
```

Then open your browser to: **http://localhost:8080**

## 📋 Features

### 1. Domain Selection
- Select source and target domains
- Supported domains:
  - 🔺 **Geometry** (Triangle, Circle, Polygon)
  - 📝 **Text** (Natural Language)
  - 💻 **Code** (Python AST)
  - 🖼️ **Image** (Visual Features)

### 2. Content Transformation
- Enter content in the source domain
- Click "Transform" to convert to target domain
- View results in real-time
- See symbolic representation (∆∞Ο)

### 3. Similarity Analysis
- Compare two contents in the same domain
- Get similarity score (0-1)
- View symbolic metrics for both contents

### 4. Symbolic Visualization
- **∆ (Delta)** - Essence vector visualization
- **∞ (Infinity)** - Process graph with nodes and edges
- **Ο (Omega)** - Completeness vector visualization

### 5. API Status
- Real-time API health check
- Display connected domains
- Show transformation statistics

## 📁 File Structure

```
web_ui/
├── index.html      # Main HTML structure
├── style.css       # Styling and layout
├── app.js          # Application logic
└── README.md       # This file
```

## 🔌 API Integration

The web UI communicates with the GLM API on `http://localhost:8000`

### Required Endpoints

- `GET /health` - Health check
- `GET /domains` - List available domains
- `POST /transform` - Transform content
- `POST /similarity` - Calculate similarity
- `POST /analyze` - Analyze content

### Starting the API

```bash
cd glm_prototype
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## 🎨 Customization

### Colors
Edit `:root` variables in `style.css`:
```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #7c3aed;
    --success-color: #10b981;
    /* ... */
}
```

### API Base URL
Edit `API_BASE_URL` in `app.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Refresh Interval
Edit `REFRESH_INTERVAL` in `app.js`:
```javascript
const REFRESH_INTERVAL = 5000; // milliseconds
```

## 🐛 Troubleshooting

### "API is not online"
- Make sure the API server is running
- Check that it's on `http://localhost:8000`
- Verify CORS is enabled in the API

### CORS Errors
- The API should have CORS enabled
- Check `api.py` for `CORSMiddleware` configuration

### Styling Issues
- Clear browser cache (Ctrl+Shift+Delete)
- Check that `style.css` is loaded
- Verify CSS file path is correct

## 📊 Example Usage

### Transform Code to Text
1. Select "Code" as source domain
2. Select "Text" as target domain
3. Enter Python code:
   ```python
   def hello(name):
       return f"Hello, {name}!"
   ```
4. Click "Transform"
5. See the text description

### Compare Text Similarity
1. Enter first text: "The cat sat on the mat"
2. Enter second text: "A feline rested on the rug"
3. Click "Calculate Similarity"
4. View similarity score

## 🔮 Future Enhancements

- [ ] Drag & drop file upload
- [ ] Real-time collaboration
- [ ] Export results (JSON, PDF)
- [ ] Dark mode toggle
- [ ] Keyboard shortcuts
- [ ] History/undo
- [ ] Advanced visualization (D3.js)
- [ ] Mobile responsive improvements

## 📞 Support

For issues or questions:
- Email: numtemalionel@gmail.com
- GitHub: [GLM Project]
- Documentation: `/glm_prototype/README.md`

## 📄 License

GLM Prototype v3.0 - Nümtema Foundry & Alexander Ngu

---

**Status:** ✅ Operational  
**Version:** 3.0  
**Last Updated:** 2024-11-15
