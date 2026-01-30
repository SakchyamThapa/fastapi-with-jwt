import streamlit as st
import requests
from typing import Optional
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

def make_request(endpoint: str, method: str = "GET", data: dict = None, auth_required: bool = True):
    """Make HTTP request to FastAPI backend"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if auth_required and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def login_page():
    """Login page"""
    st.title("🔐 Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="user@example.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                response = make_request(
                    "/auth/login",
                    method="POST",
                    data={"email": email, "password": password},
                    auth_required=False
                )
                
                if response and response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data['access_token']
                    st.session_state.user = data['user']
                    st.session_state.page = 'dashboard'
                    st.success("Login successful!")
                    st.rerun()
                else:
                    error_msg = response.json().get('detail', 'Login failed') if response else 'Connection failed'
                    st.error(error_msg)

def logout():
    """Logout user"""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.page = 'login'
    st.rerun()

def user_dashboard():
    """User dashboard page"""
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {user['full_name']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Role:** {user['role']}")
        st.write(f"**Status:** {'✅ Active' if user['is_active'] else '❌ Inactive'}")
        st.divider()
        
        if user['role'] == 'admin':
            if st.button("👥 Admin Panel", use_container_width=True):
                st.session_state.page = 'admin'
                st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()
    
    # Main content
    st.title("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Your Role", user['role'].upper())
    with col2:
        st.metric("Account Status", "Active" if user['is_active'] else "Inactive")
    with col3:
        st.metric("Account Type", "Admin" if user['role'] == 'admin' else "User")
    
    st.divider()
    
    # Profile information
    st.subheader("👤 Profile Information")
    with st.expander("View Profile Details", expanded=True):
        response = make_request("/users/me")
        if response and response.status_code == 200:
            profile_data = response.json()
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Full Name:**", profile_data['full_name'])
                st.write("**Email:**", profile_data['email'])
            with col2:
                st.write("**Role:**", profile_data['role'])
                st.write("**Account Status:**", "Active" if profile_data['is_active'] else "Inactive")
            st.write("**User ID:**", profile_data['id'])
            st.write("**Created At:**", profile_data['created_at'])
        else:
            st.error("Failed to load profile information")
    
    # Update profile section
    st.divider()
    st.subheader("✏️ Update Profile")
    with st.form("update_profile"):
        new_name = st.text_input("Full Name", value=user['full_name'])
        new_password = st.text_input("New Password (leave blank to keep current)", type="password")
        submit = st.form_submit_button("Update Profile", use_container_width=True)
        
        if submit:
            update_data = {"full_name": new_name}
            if new_password:
                update_data["password"] = new_password
            
            response = make_request("/users/me", method="PUT", data=update_data)
            if response and response.status_code == 200:
                st.success("Profile updated successfully!")
                updated_user = response.json()
                st.session_state.user = updated_user
                st.rerun()
            else:
                error_msg = response.json().get('detail', 'Update failed') if response else 'Connection failed'
                st.error(error_msg)

def admin_panel():
    """Admin panel page"""
    user = st.session_state.user
    
    # Check if user is admin
    if user['role'] != 'admin':
        st.error("Access denied. Admin privileges required.")
        return
    
    # Sidebar
    with st.sidebar:
        st.title("Admin Panel")
        st.write(f"**Logged in as:** {user['full_name']}")
        st.divider()
        
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()
    
    # Main content
    st.title("👥 User Management")
    
    # Statistics
    response = make_request("/admin/users/stats")
    if response and response.status_code == 200:
        stats = response.json()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", stats['total_users'])
        with col2:
            st.metric("Active Users", stats['active_users'])
        with col3:
            st.metric("Admins", stats['admin_users'])
        with col4:
            st.metric("Regular Users", stats['regular_users'])
    
    st.divider()
    
    # Create new user
    with st.expander("➕ Create New User"):
        with st.form("create_user"):
            col1, col2 = st.columns(2)
            with col1:
                new_email = st.text_input("Email*")
                new_name = st.text_input("Full Name*")
            with col2:
                new_password = st.text_input("Password*", type="password")
                new_role = st.selectbox("Role*", ["user", "admin"])
            
            new_active = st.checkbox("Active", value=True)
            submit = st.form_submit_button("Create User", use_container_width=True)
            
            if submit:
                if not new_email or not new_name or not new_password:
                    st.error("Please fill in all required fields")
                else:
                    create_data = {
                        "email": new_email,
                        "password": new_password,
                        "full_name": new_name,
                        "role": new_role,
                        "is_active": new_active
                    }
                    
                    response = make_request("/admin/users", method="POST", data=create_data)
                    if response and response.status_code == 200:
                        st.success(f"User {new_email} created successfully!")
                        st.rerun()
                    else:
                        error_msg = response.json().get('detail', 'Creation failed') if response else 'Connection failed'
                        st.error(error_msg)
    
    st.divider()
    
    # List all users
    st.subheader("📋 All Users")
    response = make_request("/admin/users")
    
    if response and response.status_code == 200:
        users = response.json()
        
        if not users:
            st.info("No users found")
        else:
            for user_item in users:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.write(f"**{user_item['full_name']}**")
                        st.caption(user_item['email'])
                    
                    with col2:
                        status = "🟢 Active" if user_item['is_active'] else "🔴 Inactive"
                        st.write(status)
                    
                    with col3:
                        role_emoji = "👑" if user_item['role'] == 'admin' else "👤"
                        st.write(f"{role_emoji} {user_item['role'].upper()}")
                    
                    with col4:
                        edit_key = f"edit_{user_item['id']}"
                        if st.button("✏️ Edit", key=edit_key):
                            st.session_state.edit_user_id = user_item['id']
                    
                    # Edit user form (expanded when edit button clicked)
                    if hasattr(st.session_state, 'edit_user_id') and st.session_state.edit_user_id == user_item['id']:
                        with st.expander("Edit User", expanded=True):
                            with st.form(f"edit_form_{user_item['id']}"):
                                edit_name = st.text_input("Full Name", value=user_item['full_name'])
                                edit_role = st.selectbox("Role", ["user", "admin"], 
                                                        index=0 if user_item['role'] == 'user' else 1)
                                edit_active = st.checkbox("Active", value=user_item['is_active'])
                                edit_password = st.text_input("New Password (leave blank to keep current)", 
                                                             type="password")
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    update_submit = st.form_submit_button("💾 Update", use_container_width=True)
                                with col_b:
                                    delete_submit = st.form_submit_button("🗑️ Delete", use_container_width=True, 
                                                                          type="secondary")
                                
                                if update_submit:
                                    update_data = {
                                        "full_name": edit_name,
                                        "role": edit_role,
                                        "is_active": edit_active
                                    }
                                    if edit_password:
                                        update_data["password"] = edit_password
                                    
                                    response = make_request(f"/admin/users/{user_item['id']}", 
                                                          method="PUT", data=update_data)
                                    if response and response.status_code == 200:
                                        st.success("User updated successfully!")
                                        del st.session_state.edit_user_id
                                        st.rerun()
                                    else:
                                        error_msg = response.json().get('detail', 'Update failed') if response else 'Connection failed'
                                        st.error(error_msg)
                                
                                if delete_submit:
                                    response = make_request(f"/admin/users/{user_item['id']}", method="DELETE")
                                    if response and response.status_code == 200:
                                        st.success("User deleted successfully!")
                                        del st.session_state.edit_user_id
                                        st.rerun()
                                    else:
                                        error_msg = response.json().get('detail', 'Deletion failed') if response else 'Connection failed'
                                        st.error(error_msg)
                    
                    st.divider()
    else:
        st.error("Failed to load users")

def main():
    """Main application"""
    st.set_page_config(
        page_title="User Management System",
        page_icon="👥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Route to appropriate page
    if st.session_state.token is None:
        login_page()
    elif st.session_state.page == 'admin':
        admin_panel()
    else:
        user_dashboard()

if __name__ == "__main__":
    main()