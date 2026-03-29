# Modal Alert System - CogniData

## Overview

The CogniData application uses a **professional modal alert system** to provide consistent, modern notifications throughout the interface. All user-facing alerts display as styled modal dialogs instead of inline Streamlit notifications.

**Implemented in**: `utils/alerts.py`  
**Exported from**: `utils/__init__.py`  
**Commit**: 463d520

---

## Alert Types

### Modal Alerts (Blocking Dialogs)

Modal alerts display in a centered modal dialog that must be acknowledged before the user can continue. Use these for important notifications that require user attention.

#### `modal_success(message, title=None)`
- **Purpose**: Confirm successful completion of an action
- **Color**: Green (#26A69A)
- **Icon**: ✅ (recommended in title)
- **Usage**: After creating/updating/deleting records

```python
from utils import modal_success

modal_success(
    "Protocol created successfully!",
    title="✅ Protocolo Creado"
)
```

#### `modal_error(message, title=None)`
- **Purpose**: Display error messages
- **Color**: Red (#EF5350)
- **Icon**: ❌ (recommended in title)
- **Usage**: When operations fail (database errors, validation errors, etc.)

```python
from utils import modal_error

modal_error(
    "Failed to save patient: Database connection error",
    title="❌ Error al Guardar"
)
```

#### `modal_warning(message, title=None)`
- **Purpose**: Alert user to important consequences
- **Color**: Orange (#FFA726)
- **Icon**: ⚠️ (recommended in title)
- **Usage**: Before destructive actions, when re-confirmation is needed

```python
from utils import modal_warning

modal_warning(
    "This action cannot be undone. All associated tests will be deleted.",
    title="⚠️ Advertencia"
)
```

#### `modal_info(message, title=None)`
- **Purpose**: Provide informational messages
- **Color**: Blue (#29B6F6)
- **Icon**: ℹ️ (recommended in title)
- **Usage**: Status updates, processing notifications, neutral information

```python
from utils import modal_info

modal_info(
    "Processing your request. This may take a few moments...",
    title="ℹ️ Por favor espere"
)
```

### Toast Alerts (Non-blocking Inline Notifications)

Toast alerts display inline using Streamlit's standard notification system. Use these for secondary notifications that don't require explicit dismissal.

#### `toast_success(message)`
- **Purpose**: Brief success confirmations
- **Behavior**: Fades away after a few seconds

#### `toast_error(message)`
- **Purpose**: Brief error notifications
- **Behavior**: Fades away after a few seconds

#### `toast_warning(message)`
- **Purpose**: Brief warnings
- **Behavior**: Fades away after a few seconds

#### `toast_info(message)`
- **Purpose**: Brief informational messages
- **Behavior**: Fades away after a few seconds

```python
from utils import toast_success, toast_error

toast_success("Test completed")
toast_error("Connection timeout")
```

---

## Visual Design

### Modal Styling

Each modal dialog includes:

| Element | Value |
|---------|-------|
| **Width** | 600px (responsive) |
| **Left Border** | 4px solid (alert-specific color) |
| **Background** | Color with 20% opacity |
| **Padding** | 16px (comfortable spacing) |
| **Border Radius** | 6px (modern appearance) |
| **Font Size** | 16px (readable) |
| **Text Color** | Dark (#212121) |
| **Close Button** | Centered below message |

### Color Palette

The modal system uses colors from the centralized palette (`utils/colors.py`):

| Alert Type | Background | Border | Hex Code |
|-----------|-----------|--------|----------|
| **Success** | Green | Green | #26A69A |
| **Error** | Red | Red | #EF5350 |
| **Warning** | Orange | Orange | #FFA726 |
| **Info** | Blue | Blue | #29B6F6 |

---

## Implementation Details

### Module Structure

```python
# utils/alerts.py (95 lines)

def modal_success(message: str, title: str = None) -> None:
    """Display a success modal dialog."""
    # Implemented using st.dialog()
    # Displays message with green styling
    # User must click close button to dismiss

def modal_error(message: str, title: str = None) -> None:
    """Display an error modal dialog."""
    # Implemented using st.dialog()
    # Displays message with red styling
    # User must click close button to dismiss

def modal_warning(message: str, title: str = None) -> None:
    """Display a warning modal dialog."""
    # Implemented using st.dialog()
    # Displays message with orange styling
    # User must click close button to dismiss

def modal_info(message: str, title: str = None) -> None:
    """Display an info modal dialog."""
    # Implemented using st.dialog()
    # Displays message with blue styling
    # User must click close button to dismiss

# Toast functions for non-blocking notifications
def toast_success(message: str) -> None:
def toast_error(message: str) -> None:
def toast_warning(message: str) -> None:
def toast_info(message: str) -> None:
```

### Streamlit Version Requirement

This system requires **Streamlit 1.55.0 or higher** for `st.dialog()` support.

To check your version:
```bash
pip show streamlit
```

To upgrade:
```bash
pip install --upgrade streamlit
```

---

## Usage Patterns

### Pattern 1: Success After Save Operation

```python
from utils import modal_success

# After successfully creating a protocol
protocol_id = service.create_protocol(name, description)
if protocol_id:
    modal_success(
        "Protocol created successfully!",
        title="✅ Protocolo Creado"
    )
```

### Pattern 2: Error Handling

```python
from utils import modal_error

try:
    result = database_operation()
except Exception as e:
    modal_error(
        f"Operation failed: {str(e)}",
        title="❌ Error"
    )
```

### Pattern 3: Destructive Action Warning

```python
from utils import modal_warning

if user_clicks_delete:
    modal_warning(
        "This action will permanently delete the protocol and all associated test data.",
        title="⚠️ Advertencia"
    )
    # Proceed with deletion only after user acknowledges
```

### Pattern 4: Long-Running Operation Status

```python
from utils import modal_info

modal_info(
    "Generating PDF report... This may take 30-60 seconds.",
    title="ℹ️ Por favor espere"
)
# Perform long operation
# Modal will auto-close when operation completes
```

### Pattern 5: Combined Success + Next Action

```python
from utils import modal_success, toast_info

modal_success("Test results saved successfully!")
# User acknowledges modal
toast_info("Redirecting to dashboard...")
# Non-blocking toast appears while redirecting
```

---

## Migration Guide

### Replacing Streamlit Alerts

When updating existing code, replace inline alerts with modals:

#### OLD CODE (Inline Alert)
```python
st.success("✅ Protocolo creado")
```

#### NEW CODE (Modal Alert)
```python
from utils import modal_success

modal_success("Protocolo creado", title="✅ Éxito")
```

---

#### OLD CODE (Inline Alert)
```python
st.error(f"❌ Error: {error_message}")
```

#### NEW CODE (Modal Alert)
```python
from utils import modal_error

modal_error(f"Error: {error_message}", title="❌ Error")
```

---

#### OLD CODE (Inline Alert)
```python
st.warning("Esta acción no se puede deshacer")
```

#### NEW CODE (Modal Alert)
```python
from utils import modal_warning

modal_warning(
    "Esta acción no se puede deshacer",
    title="⚠️ Advertencia"
)
```

---

## Files Using Modal Alerts

### Currently Implemented

- **app_pages/protocols.py** - Protocol CRUD operations
  - Protocol creation success
  - Protocol deletion confirmation
  - Validation errors

### Ready for Implementation

The following pages have existing alerts that should be migrated:

- **app_pages/config.py** - Configuration changes (~25 alerts)
- **app_pages/tests.py** - Test data entry and scoring (~20 alerts)
- **app_pages/patients.py** - Patient management (~10 alerts)
- **app_pages/dashboard.py** - Dashboard operations (~5 alerts)
- **utils/auth.py** - Login and authentication (~5 alerts)

Total: ~75 alerts available for migration

---

## Best Practices

### ✅ DO:
- Use **modal_success** to confirm important operations completed
- Use **modal_error** for all exception handling
- Use **modal_warning** before destructive actions
- Use **modal_info** for processing status
- Include emoji icons in titles for visual clarity
- Write messages in the user's language (Spanish/English as needed)
- Keep messages clear and actionable

### ❌ DON'T:
- Use modals for every minor notification (that's what toasts are for)
- Show multiple modals in sequence (can feel overwhelming)
- Use overly technical error messages (translate to user-friendly language)
- Leave modals open without a close button
- Use wrong alert type (error modal for non-errors, etc.)

---

## Spanish Translation Examples

Common alert messages with Spanish translations:

| English | Spanish |
|---------|---------|
| Success | Éxito ✅ |
| Error | Error ❌ |
| Warning | Advertencia ⚠️ |
| Information | Información ℹ️ |
| Created successfully | Creado exitosamente |
| Deleted successfully | Eliminado exitosamente |
| Updated successfully | Actualizado exitosamente |
| This action cannot be undone | Esta acción no se puede deshacer |
| Processing... | Procesando... |
| Please wait | Por favor espere |

---

## Testing Modal Alerts

To test the modal alert system in development:

```python
# Create a simple test page
import streamlit as st
from utils import modal_success, modal_error, modal_warning, modal_info

st.title("Modal Alert Tests")

col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Success Modal"):
        modal_success("This is a success message!")
    
    if st.button("❌ Error Modal"):
        modal_error("This is an error message!")

with col2:
    if st.button("⚠️ Warning Modal"):
        modal_warning("This is a warning message!")
    
    if st.button("ℹ️ Info Modal"):
        modal_info("This is an info message!")
```

Run with:
```bash
streamlit run test_modals.py
```

---

## Troubleshooting

### Modal not appearing?
1. Verify Streamlit version is 1.55.0 or higher
2. Check that `st.dialog()` is being called correctly
3. Ensure the modal function is imported correctly
4. Check browser console for JavaScript errors

### Modal text not visible?
1. Verify the message string is not empty
2. Check that the title (if provided) is not excessively long
3. Ensure the message fits within the modal width

### Multiple modals appearing?
1. Check that you're not calling multiple modal functions in the same code block
2. Verify that Streamlit reruns aren't triggering duplicate calls
3. Use session state to track modal display

---

## Future Enhancements

Potential improvements for the modal system:

- [ ] Add timeout parameter (auto-close after N seconds)
- [ ] Add action buttons (Yes/No, OK/Cancel)
- [ ] Add progress indicators for long-running operations
- [ ] Add custom icon support
- [ ] Add animation options
- [ ] Add sound/notification support for important alerts

---

## References

- **Implementation**: `/Users/grumbler/devel/cognidata/utils/alerts.py`
- **Exports**: `/Users/grumbler/devel/cognidata/utils/__init__.py`
- **Color Palette**: `/Users/grumbler/devel/cognidata/utils/colors.py`
- **Streamlit Docs**: https://docs.streamlit.io/develop/api-reference/dialogs/st.dialog

---

## Summary

The modal alert system provides a professional, consistent way to display notifications throughout CogniData. By using this centralized system instead of ad-hoc Streamlit alerts, the application maintains a cohesive UX and makes it easy to update alert styling application-wide.

**Quick Import**:
```python
from utils import modal_success, modal_error, modal_warning, modal_info
```

**That's it!** You now have professional modals ready to use anywhere in the application.
