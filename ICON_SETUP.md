# Bayonne Hockey Club - Icon Setup Instructions

## iPhone Home Screen Icon Setup

To create the proper icon files for iPhone home screen bookmarks, you need to create the following files in the `app/static/` directory:

### Required Icon Files:

1. **favicon.ico** - 16x16, 32x32, 48x48 (multi-size ICO file)
2. **apple-touch-icon.png** - 180x180 pixels (for iPhone home screen)
3. **favicon-32x32.png** - 32x32 pixels
4. **favicon-16x16.png** - 16x16 pixels

### How to Create These Files:

#### Option 1: Using Online Favicon Generators
1. Go to https://realfavicongenerator.net/
2. Upload your Bayonne Hockey Club logo
3. Configure the settings:
   - Apple Touch Icon: 180x180
   - Favicon: 16x16, 32x32, 48x48
4. Download the generated files
5. Place them in the `app/static/` directory

#### Option 2: Using Design Software
1. Create a square logo (preferably 512x512 or higher)
2. Export as PNG in the following sizes:
   - 180x180 for apple-touch-icon.png
   - 32x32 for favicon-32x32.png
   - 16x16 for favicon-16x16.png
3. Create favicon.ico using an online converter or icon software

#### Option 3: Using the SVG Template
The `favicon.svg` file has been created as a template. You can:
1. Edit the SVG to match your exact logo
2. Use online SVG to PNG converters to generate the required sizes
3. Use online SVG to ICO converters for the favicon.ico

### Current Setup:
- ✅ SVG favicon created (fallback)
- ✅ Web manifest created
- ✅ Meta tags added to base template
- ⏳ Icon files need to be created and uploaded

### Testing:
1. After adding the icon files, test on iPhone:
   - Open the website in Safari
   - Tap the Share button
   - Tap "Add to Home Screen"
   - The custom icon should appear

### Notes:
- The Apple Touch Icon should be 180x180 pixels
- No rounded corners needed (iOS adds them automatically)
- Use a solid background color for best results
- The theme color is set to #2d0000 (dark red) to match the site design
