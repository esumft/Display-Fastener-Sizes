# Display Fastener Sizes (unofficial Autodesk Fusion Add-in)

**Display Fastener Sizes** is an Autodesk Fusion add-in that visually identifies and color-codes fasteners (such as screws and bolts) in your design based on their major diameter. It also generates a color key palette for quick reference.

This is intended to help with design reviews where assessing a products design for assembly efficiency can be enhanced by limiting the variations of and grouping fastener types and sizes.




https://github.com/user-attachments/assets/b4e84483-41ed-423b-988f-620217e4fbb5


---

## Road Map

### Next release
- **Imperial fastener type support**

### Future releases
- **Other fastener types**: Rivets, Washers, Nuts
- **Fastener groups**
- **Tool accessiblity analysis**

---

## Features

- **Color-Coding:** Automatically detects fasteners by name (e.g., "M3", "M4") and overlays a unique color on each size.
- **Color Key Palette:** Displays a palette showing which color corresponds to each fastener size.
- **Opacity Adjustment:** Makes all components semi-transparent to highlight fasteners.
- **UI Integration:** Adds a button to the **Inspect** panel.
- **Reset/Cleanup:** Running the command again removes overlays and restores the original view.

---

## Installation

1. **Download or Clone this Repository:**
2. **Start Autodesk Fusion**
3. **Open the Add-ins dialog under the Utilties tab** (`Utilities` > `Scripts & Add-Ins`).
4. **Select the '+' from the top of the menu** and select "Script or add-in from deivce".
5. **Find the "FastenerVisualiser"** directory and click **Open**.
6. **Find "Display Fastener Sizes" in the list and toggle **"Run"** on. **(Recommended: Check "Run on Startup" so that the Add-In loads when you open Fusion)**

---

## Usage

1. Open your Autodesk design which includes fasteners from the **Fusion fastener library**.
2. Go to the **Inspect** panel.
3. Click the **Display Fastener Sizes** button.
4. Fasteners will be color-coded, and a color key palette will appear on the right.
5. To reset, click the button again.
6. **Recommended Assign a hotkey for frequent use.**
**NOTE: An error will display if there are no fasteners or if the fasteners are not metric (current limitation)**


---

## Supported Fastener Types

- **Metric**

---

## Notes

- Only the fasteners in the top-level component color-coded (Current limitation).
- If no fasteners are detected, a message box will appear.
- The add-in currently only supports metric fastener detection.

---

## Troubleshooting

- If the color overlays or palette do not appear, ensure your fastener components are named with standard size notation (e.g., "M3", "M4").
- To remove overlays and restore the original view, simply run the command again.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

---

## Credits

Developed by [Elliott Griffiths].  
Uses Autodesk Fusion API.

---
