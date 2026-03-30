"""
Browser token storage using JavaScript localStorage.

localStorage persists across page reloads and is accessible to Streamlit
via st.session_state injection by JavaScript.

This is the only way to persist auth tokens across Streamlit reruns
without relying on external libraries.
"""

import streamlit as st


def inject_token_recovery_script():
    """
    Inject JavaScript to recover JWT token from browser localStorage
    and store it in Streamlit session state.
    
    This script runs on every page load and restores the auth token
    if it exists in localStorage.
    """
    # JavaScript code that runs on every page load
    js_code = """
    <script>
    // Recover token from localStorage and put it in Streamlit session state
    (function() {
        const authToken = localStorage.getItem('cognidata_auth_token');
        if (authToken) {
            // Use Streamlit's WebSocket API to set session state
            // This is a workaround since direct session state access from JS isn't possible
            // Instead, we store it in a data attribute and the Streamlit app reads it
            document.body.setAttribute('data-auth-token', authToken);
            console.log('[CogniData] Auth token recovered from localStorage');
        }
    })();
    </script>
    """
    st.html(js_code)


def store_token_in_browser(token: str):
    """
    Store JWT token in browser's localStorage so it persists across reloads.
    
    Uses JavaScript to write to localStorage.
    
    Args:
        token: JWT token string to store
    """
    js_code = f"""
    <script>
    (function() {{
        localStorage.setItem('cognidata_auth_token', '{token}');
        console.log('[CogniData] Auth token stored in localStorage');
    }})();
    </script>
    """
    st.html(js_code)


def get_token_from_browser() -> str:
    """
    Retrieve JWT token from browser's localStorage.
    
    Since JavaScript can't directly access Streamlit's session state,
    we use a workaround: render a component that reads localStorage
    and returns the token via Streamlit's experimental API.
    
    Returns:
        JWT token string if found in localStorage, None otherwise
    """
    # This is a placeholder - in practice, we need a different approach
    # See: retrieve_token_via_storage_component()
    pass


def clear_token_from_browser():
    """
    Remove JWT token from browser's localStorage.
    Called on logout.
    """
    js_code = """
    <script>
    (function() {
        localStorage.removeItem('cognidata_auth_token');
        console.log('[CogniData] Auth token cleared from localStorage');
    })();
    </script>
    """
    st.html(js_code)


def retrieve_token_via_storage_component():
    """
    Create an invisible component that reads localStorage and returns
    the token value so Streamlit can use it.
    
    This uses st.components.v1.html with a callback mechanism.
    
    Returns:
        JWT token from localStorage or None
    """
    # Use Streamlit's iframe component to bridge JavaScript and Python
    component_code = """
    <script>
    window.parent.postMessage(
        {type: 'COGNIDATA_TOKEN', value: localStorage.getItem('cognidata_auth_token')},
        '*'
    );
    </script>
    """
    # This is tricky because we need bidirectional communication
    # A better approach is using st.session_state directly from a callback
    pass
