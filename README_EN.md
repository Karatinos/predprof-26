<<<<<<< HEAD
# OlympDev Web Development Project

This project contains a set of static HTML/CSS templates designed for a web development olympiad. The templates are built using HTML5 and Tailwind CSS (via CDN). A basic Flask application is included to serve the pages.

## Project Structure

- **index.html**: Homepage with a static carousel and features section.
- **login.html**: Simple login page (Username/Password).
- **register.html**: Comprehensive registration form with various input types.
- **profile.html**: User profile page with avatar, user info, stats, and a comparison table.
- **catalog.html**: Product catalog with search, filters, and CSS-only modal overlays.
- **item.html**: Detailed product page with image gallery and reviews.
- **404.html**: Custom error page.
- **style.css**: Centralized stylesheet with CSS variables for theming.
- **app.py**: A Flask application setup to route these templates.

## How to Run

### Flask Mode (Recommended)
1. Ensure you have Python and Flask installed (`pip install flask`).
2. Keep all files in the same directory.
3. Run the application:
   ```bash
   python app.py
   ```
4. Visit `http://127.0.0.1:5000/` in your browser.

*Note: The `app.py` is configured to look for templates in the current directory (`.`), so you do not need a separate `templates` folder.*

### Static Mode
Simply open `index.html` in any modern web browser. You can navigate through the site using the links provided in the navigation bar.

## Editing Templates

### Theming
Colors are defined in `style.css` using CSS variables.
- `:root` defines the **Light Mode** colors (Default).
- `.dark` defines the **Dark Mode** colors.
To change the accent color, edit `--accent-color` in `style.css`.

### Header
The navigation header is consistent across all pages inside the `<header>` tag.
- Logo and Navigation links are aligned to the **left**.
- Theme toggle and Account actions are aligned to the **right**.
To update the menu, you must edit the HTML in each file.

### Carousel
Located in `index.html` within the `.carousel` class. Slides are simple `div` elements. Change the `background-image` inline style to update images.

### Modals
In `catalog.html`, modals function using CSS `:target` selectors. Each modal has an ID (e.g., `modal-1`), and clicking a card with `href="#modal-1"` activates it without JavaScript.
=======
# predprof-26
Проект для тренировочного хакатона перед предпрофом 2025-26
>>>>>>> 75df1d8305f67094a8094a31633a54bad33e6927
