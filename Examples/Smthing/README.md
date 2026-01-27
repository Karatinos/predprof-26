# OlympDev Web Development Project

This project contains a set of static HTML/CSS templates designed for a web development olympiad. The templates are built using HTML5 and standard CSS. A basic Flask application is included to serve the pages.

## Project Structure

- **app.py**: A Flask application setup to route the templates.
- **static/**: Folder containing static assets (CSS).
  - **style.css**: Centralized stylesheet with CSS variables for theming and semantic classes.
- **templates/**: Folder containing HTML files.
  - **index.html**: Homepage with a static carousel and features section.
  - **login.html**: Simple login page (Username/Password).
  - **register.html**: Comprehensive registration form.
  - **profile.html**: User profile page with avatar, user info, stats, and a comparison table.
  - **catalog.html**: Product catalog with search, filters, and CSS-only modal overlays.
  - **item.html**: Detailed product page with image gallery and reviews.
  - **404.html**: Custom error page.

## How to Run

### Flask Mode (Recommended)
1. Ensure you have Python and Flask installed (`pip install flask`).
2. Run the application:
   ```bash
   python app.py
   ```
3. Visit `http://127.0.0.1:5000/` in your browser.

### Static Mode (File Explorer)
Since the links in the HTML files point to `.html` files (e.g., `catalog.html`), you can often navigate by opening `templates/index.html` in your browser. However, **styles might not load correctly** in static mode because the CSS path is set to `/static/style.css` (absolute path for Flask). To fix this for static viewing, you would need to change the link in the HTML head to `../static/style.css`.

## Editing Templates

### Theming
Colors are defined in `static/style.css` using CSS variables.
- `:root` defines the **Light Mode** colors (Default).
- `.dark` defines the **Dark Mode** colors.
To change the accent color, edit `--accent-color`.

### Header
The navigation header is consistent across all pages inside the `<header>` tag.
- Logo and Navigation links are aligned to the **left**.
- Theme toggle, Profile button, and Account actions are aligned to the **right**.

### Carousel
Located in `index.html` within the `.carousel` class. Slides are simple `div` elements. Change the `background-image` CSS class to update images.

### Modals
In `catalog.html`, modals function using CSS `:target` selectors. Each modal has an ID (e.g., `modal-1`), and clicking a card with `href="#modal-1"` activates it without JavaScript.
