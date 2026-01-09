# Issue Tracker Frontend

Beautiful and modern React frontend for the Issue Tracker API.

## Features

- ✨ Modern UI with glassmorphism effects
- 📊 Real-time statistics dashboard
- 🔍 Advanced filtering and search
- ✏️ Full CRUD operations
- 📁 CSV import/export
- 🗑️ Bulk operations (update/delete)
- 📱 Responsive design

## Quick Start

```bash
# Install dependencies (if not already installed)
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

## Configuration

The frontend connects to the backend API at `http://localhost:8000`.

To change this, edit `src/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';  // Change this
```

## Building for Production

```bash
npm run build
```

The build will be in the `dist/` folder, ready to deploy.

## Deployment

### Deploy to Render

1. Push code to GitHub
2. Go to Render Dashboard → **"New +"** → **"Static Site"**
3. Connect your repository
4. Configure:
   - **Build Command**: `npm run build`
   - **Publish Directory**: `dist`
5. Add Environment Variable (if needed):
   - **Key**: `VITE_API_URL`
   - **Value**: Your deployed backend URL
6. Deploy!

### Deploy to Vercel/Netlify

Both support Vite out of the box - just connect your repository!

## Tech Stack

- **React** - UI library
- **Vite** - Build tool
- **Vanilla CSS** - Styling with modern effects
- **Fetch API** - HTTP requests

## Project Structure

```
src/
├── api.js          # API client
├── App.jsx         # Main app component
├── index.css       # Global styles
└── main.jsx        # Entry point
```

## License

MIT
