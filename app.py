import streamlit as st
import os

# Set page config
st.set_page_config(
    page_title="Alpha Arena - AI Prediction Market",
    page_icon="◐",
    layout="wide"
)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'public'  # 'public' or 'admin'

def check_password(password: str) -> bool:
    """Check if provided password matches admin password."""
    admin_password = os.environ.get('ADMIN_PASSWORD', '')
    if not admin_password:
        return False
    return password == admin_password

def show_login():
    """Display login interface."""
    st.markdown("""
    <style>
    .login-container {
        max-width: 450px;
        margin: 80px auto;
        padding: 3rem 2.5rem;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        border-radius: 20px;
        border: 1px solid rgba(139, 92, 246, 0.3);
        box-shadow: 0 20px 60px rgba(139, 92, 246, 0.15);
    }
    .login-title {
        text-align: center;
        color: #8B5CF6;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .login-subtitle {
        text-align: center;
        color: #94A3B8;
        margin-bottom: 2rem;
    }
    </style>
    
    <div class="login-container">
        <div class="login-title">🔐 Admin Access</div>
        <div class="login-subtitle">Enter password to control the competition</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Admin Password", type="password", key="admin_password", label_visibility="collapsed", placeholder="Enter admin password...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔓 Login", use_container_width=True, type="primary"):
                if check_password(password):
                    st.session_state.authenticated = True
                    st.session_state.view_mode = 'admin'
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
        
        with col_btn2:
            if st.button("👁️ Public View", use_container_width=True):
                st.session_state.view_mode = 'public'
                st.rerun()

# Main routing logic
if st.session_state.view_mode == 'public':
    # Public dashboard - no authentication required
    # Execute public_dashboard.py code
    with open('public_dashboard.py', 'r') as f:
        exec(f.read())
    
elif st.session_state.view_mode == 'admin':
    if not st.session_state.authenticated:
        # Show login page
        show_login()
    else:
        # Show admin panel
        # Add logout/view switch buttons in sidebar
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 Admin Controls")
            
            if st.button("👁️ Switch to Public View", use_container_width=True):
                st.session_state.view_mode = 'public'
                st.rerun()
            
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                st.session_state.authenticated = False
                st.session_state.view_mode = 'public'
                st.rerun()
        
        # Load admin interface - execute app_admin.py code
        with open('app_admin.py', 'r') as f:
            exec(f.read())
