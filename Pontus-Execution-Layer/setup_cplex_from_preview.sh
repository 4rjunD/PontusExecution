#!/bin/bash
# Setup CPLEX from Preview folder

echo "🔍 Looking for Preview folder with CPLEX..."
echo ""

# Check common locations
PREVIEW_PATHS=(
    "/Users/arjundixit/Downloads/PontusRouting/Preview"
    "/Users/arjundixit/Desktop/Preview"
    "/Users/arjundixit/Downloads/Preview"
)

FOUND=0

for PREVIEW in "${PREVIEW_PATHS[@]}"; do
    if [ -d "$PREVIEW" ]; then
        echo "✅ Found Preview folder: $PREVIEW"
        FOUND=1
        
        # Check for zip files
        ZIP_COUNT=$(find "$PREVIEW" -maxdepth 1 -name "*.zip" | wc -l | tr -d ' ')
        if [ "$ZIP_COUNT" -gt 0 ]; then
            echo "   📦 Found $ZIP_COUNT zip file(s) - extracting..."
            cd "$PREVIEW"
            for ZIP in *.zip; do
                if [[ "$ZIP" == *"osx-arm64"* ]] || [[ "$ZIP" == *"arm64"* ]]; then
                    echo "   Extracting: $ZIP"
                    unzip -q "$ZIP" -d . 2>/dev/null || echo "   ⚠️  Extraction may have failed"
                fi
            done
        fi
        
        # Find CPLEX Python directory
        echo ""
        echo "   🔍 Searching for CPLEX Python installation directory..."
        CPLEX_PYTHON=$(find "$PREVIEW" -name "setup.py" -path "*/cplex/python/*" -type f 2>/dev/null | head -1)
        
        if [ -n "$CPLEX_PYTHON" ]; then
            CPLEX_DIR=$(dirname "$CPLEX_PYTHON")
            echo "   ✅ Found CPLEX Python directory: $CPLEX_DIR"
            
            # Check platform
            if [[ "$CPLEX_DIR" == *"arm64_osx"* ]]; then
                echo "   🎯 Platform: arm64_osx (correct for your Mac)"
            elif [[ "$CPLEX_DIR" == *"x86-64_osx"* ]]; then
                echo "   🎯 Platform: x86-64_osx (Intel Mac - may work)"
            else
                echo "   ⚠️  Platform: $(basename $(dirname "$CPLEX_DIR"))"
            fi
            
            echo ""
            echo "   📦 Installing CPLEX Python bindings..."
            cd "$CPLEX_DIR"
            python3 setup.py install
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "   ✅ Installation complete!"
                echo ""
                echo "   🧪 Testing installation..."
                python3 -c "import cplex; print('CPLEX version:', cplex.__version__)" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo "   ✅ CPLEX is ready to use!"
                else
                    echo "   ⚠️  Installation completed but import test failed"
                    echo "   Try: python3 -c 'import cplex'"
                fi
            else
                echo "   ❌ Installation failed"
            fi
        else
            echo "   ❌ Could not find CPLEX Python setup.py"
            echo ""
            echo "   Looking for CPLEX directories..."
            find "$PREVIEW" -type d -iname "*cplex*" -o -iname "*ilog*" 2>/dev/null | head -5
        fi
        
        break
    fi
done

if [ $FOUND -eq 0 ]; then
    echo "❌ Preview folder not found in common locations:"
    for path in "${PREVIEW_PATHS[@]}"; do
        echo "   - $path"
    done
    echo ""
    echo "Please tell me the exact path to your Preview folder."
fi

