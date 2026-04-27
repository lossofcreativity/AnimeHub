# 🎌 AnimeHub - Your Ultimate Anime & Manga Platform

Welcome to **AnimeHub**, a stunning web application built with Python Flask that allows you to discover, track, and manage your favorite anime and manga!

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🎬 Anime & Manga Management
- **Browse Anime** - Explore thousands of anime titles with detailed information
- **Browse Manga** - Discover manga series with comprehensive details
- **Search Functionality** - Powerful search to find your favorite titles
- **Advanced Details** - View ratings, episodes, genres, studios, and more

### 📚 Personal Collections
- **Watchlist** - Track anime you want to watch with status updates
- **Reading List** - Manage manga you're reading or planning to read
- **Progress Tracking** - Monitor episodes watched and chapters read
- **Status Management** - Mark items as Planning, Watching/Reading, or Completed

### 👥 User System
- **Secure Authentication** - Sign up and login with encrypted passwords
- **Personal Profile** - Access your watchlist and reading list anytime
- **Database Storage** - All your data safely stored in SQLite database

### 🎨 Design Features
- **HiAnime Inspired UI** - Modern, dark-themed interface with stunning animations
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile devices
- **Smooth Animations** - Beautiful transitions and hover effects
- **Dark Mode** - Easy on the eyes with cyberpunk aesthetic
- **Fast Loading** - Optimized performance with lazy loading images

### 🔗 API Integration
- **Jikan API** - Access to comprehensive anime/manga data
- **AniList API** - Additional data source for anime information
- **Real-time Data** - Always get the latest information

## 📋 Routes

```
Authentication:
  /login                 - Login page
  /signup                - Sign up page
  /logout                - Logout

Main Pages:
  /home                  - Home page with top anime & manga
  /anime                 - Search anime
  /anime/<id>            - Anime details
  /manga                 - Search manga
  /manga/<id>            - Manga details
  /author/<id>           - Author information
  /as/<id>               - Animation studio details

Collections:
  /watchlist             - Your anime watchlist
  /readinglist           - Your manga reading list

API Endpoints:
  /api/watchlist/add     - Add anime to watchlist (POST)
  /api/watchlist/remove/<id> - Remove from watchlist (DELETE)
  /api/readinglist/add   - Add manga to reading list (POST)
  /api/readinglist/remove/<id> - Remove from reading list (DELETE)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the project directory:**
```bash
cd "c:\Users\Avaya Shrestha\Documents\CodeSpace\Test Website"
```

2. **Create a virtual environment (optional but recommended):**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux
```

3. **Install required packages:**
```bash
pip install -r requirements.txt
```

### Running the Application

1. **Start the Flask development server:**
```bash
python app.py
```

2. **Open your browser and visit:**
```
http://localhost:5000
```

3. **Create an account or login to get started!**

## 📁 Project Structure

```
Test Website/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── users.db               # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet with hianime design
│   └── js/
│       └── main.js        # Interactive JavaScript
└── templates/
    ├── base.html          # Base template with navbar
    ├── login.html         # Login page
    ├── signup.html        # Sign up page
    ├── home.html          # Home page with top anime/manga
    ├── anime.html         # Anime detail page
    ├── manga.html         # Manga detail page
    ├── anime_search.html  # Anime search results
    ├── manga_search.html  # Manga search results
    ├── author.html        # Author details
    ├── studio.html        # Studio details
    ├── watchlist.html     # Watchlist page
    ├── readinglist.html   # Reading list page
    ├── 404.html           # 404 error page
    └── 500.html           # 500 error page
```

## 🎨 Design Highlights

### Color Scheme
- **Primary Color**: Cyan (#00d4ff)
- **Secondary Color**: Magenta (#ff006e)
- **Accent Color**: Yellow (#ffd60a)
- **Background**: Dark Navy (#0a0e27)
- **Text**: White & Light Gray

### Key Design Features
- Gradient backgrounds and text
- Glowing effects on hover
- Smooth transitions and animations
- Card-based layout
- Modern glassmorphism effects
- Responsive grid layouts

## 🔐 Security Features

- **Password Hashing**: Passwords are securely hashed using Werkzeug
- **Session Management**: Secure session handling with Flask
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injections
- **CSRF Protection Ready**: Easy to add CSRF tokens

## ⚡ Performance Optimizations

- **Lazy Loading**: Images load only when visible
- **Caching**: API responses can be cached
- **Debouncing**: Search and scroll events are debounced
- **Throttling**: Smooth performance on rapid interactions
- **Intersection Observer**: Efficient animation triggering

## 🔄 Data Flow

```
User Registration/Login
        ↓
User Account Created (users.db)
        ↓
Browse Anime/Manga (Jikan API)
        ↓
View Details
        ↓
Add to Watchlist/Reading List
        ↓
Store in Database
        ↓
View Collections & Track Progress
```

## 🎯 Future Enhancements

- [ ] User ratings and reviews
- [ ] Social features (follow users, share lists)
- [ ] Anime news integration
- [ ] Community forums
- [ ] Advanced filtering and sorting
- [ ] Email notifications
- [ ] Dark/Light theme toggle
- [ ] API rate limiting
- [ ] Admin dashboard
- [ ] Mobile app

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change the port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Database Issues
```bash
# Delete users.db and restart the app
rm users.db
python app.py
```

### API Connection Issues
- Check your internet connection
- Verify Jikan API is accessible at https://api.jikan.moe/v4
- Try restarting the application

## 📝 Configuration

### Change Secret Key
In `app.py`, update:
```python
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
```
Use a strong, random secret key for production.

### Database
Default: SQLite (users.db)
To use PostgreSQL or MySQL:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/animehub'
```

## 🌐 API Documentation

### Jikan API
- **Base URL**: https://api.jikan.moe/v4
- **Anime**: `/anime/{id}`
- **Manga**: `/manga/{id}`
- **Search**: `/anime?query=search_term`
- **Top**: `/top/anime`, `/top/manga`
- **People**: `/people/{id}`
- **Studios**: `/studios/{id}`

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 👨‍💻 Author

Created with ❤️ for anime fans everywhere!

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the documentation
- Review the code comments

---

**Happy Watching & Reading! 🎌✨**

Visit AnimeHub today and start tracking your favorite anime and manga!
