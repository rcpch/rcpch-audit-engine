#!/bin/bash
# Script to update JavaScript libraries used in the Epilepsy12 application
# This script downloads the latest versions of the libraries and places them in the correct directories

set -e

echo "Updating JavaScript libraries for Epilepsy12..."

# Define versions
HTMX_VERSION="2.0.7"
SWEETALERT2_VERSION="11.26.18"
PLOTLY_VERSION="2.38.1"  # Latest v2 (matches Python plotly package structure)
HYPERSCRIPT_VERSION="0.9.12"  # No newer releases found
POPPER_VERSION="2.11.8"  # Latest v2

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

cd "$TEMP_DIR"

# Download htmx
echo "Downloading htmx ${HTMX_VERSION}..."
wget -q "https://unpkg.com/htmx.org@${HTMX_VERSION}/dist/htmx.min.js" -O htmx.min.js

# Download SweetAlert2
echo "Downloading SweetAlert2 ${SWEETALERT2_VERSION}..."
wget -q "https://cdn.jsdelivr.net/npm/sweetalert2@${SWEETALERT2_VERSION}/dist/sweetalert2.all.min.js" -O sweetalert2.all.min.js

# Download Plotly
echo "Downloading Plotly ${PLOTLY_VERSION}..."
wget -q "https://cdn.plot.ly/plotly-${PLOTLY_VERSION}.min.js" -O plotly.min.js

# Download _hyperscript (if newer version exists, update version number)
echo "Downloading _hyperscript ${HYPERSCRIPT_VERSION}..."
wget -q "https://unpkg.com/hyperscript.org@${HYPERSCRIPT_VERSION}/dist/_hyperscript.min.js" -O hyperscript.min.js

# Download Popper.js (for bootstrap compatibility)
echo "Downloading Popper.js ${POPPER_VERSION}..."
wget -q "https://cdn.jsdelivr.net/npm/@popperjs/core@${POPPER_VERSION}/dist/umd/popper.min.js" -O popper.min.js

# Get back to project root
cd -

# Create new library directories
echo "Creating new library directories..."
mkdir -p "static/htmx_${HTMX_VERSION}"
mkdir -p "static/sweetalert2_${SWEETALERT2_VERSION}"
mkdir -p "static/plotly_${PLOTLY_VERSION}"
mkdir -p "static/popper_${POPPER_VERSION}"

# Copy files to static directories
echo "Copying files to static directories..."
cp "$TEMP_DIR/htmx.min.js" "static/htmx_${HTMX_VERSION}/"
cp "$TEMP_DIR/sweetalert2.all.min.js" "static/sweetalert2_${SWEETALERT2_VERSION}/"
cp "$TEMP_DIR/plotly.min.js" "static/plotly_${PLOTLY_VERSION}/"
cp "$TEMP_DIR/popper.min.js" "static/popper_${POPPER_VERSION}/"

# Clean up
rm -rf "$TEMP_DIR"

echo ""
echo "✓ JavaScript libraries downloaded successfully!"
echo ""
echo "Next steps:"
echo "1. Update templates/base.html to reference new library versions:"
echo "   - htmx_1.8.4 → htmx_${HTMX_VERSION}"
echo "   - hyperscript_0.9.12 → hyperscript_${HYPERSCRIPT_VERSION} (no update needed)"
echo "   - sweetalert2_11.11.0 → sweetalert2_${SWEETALERT2_VERSION}"
echo "   - plotly_1.58.5 → plotly_${PLOTLY_VERSION}"
echo ""
echo "2. Update templates/rest_framework/api.html:"
echo "   - Replace CDN popper.js reference with: {% static 'popper_${POPPER_VERSION}/popper.min.js' %}"
echo ""
echo "3. Update templates/epilepsy12/partials/registration/registration_dates.html:"
echo "   - Replace CDN sweetalert2 reference with: {% static 'sweetalert2_${SWEETALERT2_VERSION}/sweetalert2.all.min.js' %}"
echo ""
echo "4. Test the application thoroughly"
echo "5. Remove old library directories after confirming everything works"
echo ""
