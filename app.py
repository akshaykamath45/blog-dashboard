import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# API Configuration
API_BASE_URL = 'https://blog-backend-three-psi.vercel.app/api'

# Page Configuration
st.set_page_config(page_title='Blog Dashboard', layout='wide')

# Sidebar Navigation
def sidebar_nav():
    st.sidebar.title('Blog Dashboard')
    return st.sidebar.radio('Navigation', ['Blog List', 'Create Blog', 'Edit Blog'])

# API Functions
def get_all_blogs():
    try:
        response = requests.get(f'{API_BASE_URL}/blogs')
        return response.json()['blogs']
    except Exception as e:
        st.error(f'Error fetching blogs: {str(e)}')
        return []

def get_blog_by_id(blog_id):
    try:
        response = requests.get(f'{API_BASE_URL}/blogs/{blog_id}')
        return response.json()
    except Exception as e:
        st.error(f'Error fetching blog: {str(e)}')
        return None

def create_blog(blog_data):
    try:
        response = requests.post(
            f'{API_BASE_URL}/blogs',
            json=blog_data,
            headers={'Content-Type': 'application/json'}
        )
        return response.json()
    except Exception as e:
        st.error(f'Error creating blog: {str(e)}')
        return None

def update_blog(blog_id, blog_data):
    try:
        response = requests.put(
            f'{API_BASE_URL}/blogs/{blog_id}',
            json=blog_data,
            headers={'Content-Type': 'application/json'}
        )
        return response.json()
    except Exception as e:
        st.error(f'Error updating blog: {str(e)}')
        return None

def delete_blog(blog_id):
    try:
        response = requests.delete(f'{API_BASE_URL}/blogs/{blog_id}')
        return response.json()
    except Exception as e:
        st.error(f'Error deleting blog: {str(e)}')
        return None

# Blog Form
def blog_form(existing_blog=None):
    with st.form('blog_form'):
        # Basic Information
        title = st.text_input('Title*', value=existing_blog.get('title', '') if existing_blog else '')
        category = st.text_input('Category*', value=existing_blog.get('category', '') if existing_blog else '')
        description = st.text_area('Description*', value=existing_blog.get('description', '') if existing_blog else '')
        image = st.text_input('Image URL*', value=existing_blog.get('image', '') if existing_blog else '')
        
        # Content
        st.subheader('Content')
        introduction = st.text_area('Introduction*', value=existing_blog.get('content', {}).get('introduction', '') if existing_blog else '')
        
        # Sections
        st.subheader('Sections')
        num_sections = st.number_input('Number of Sections', min_value=1, value=len(existing_blog.get('content', {}).get('sections', [])) if existing_blog else 1)
        sections = []
        
        for i in range(int(num_sections)):
            st.write(f'Section {i + 1}')
            existing_section = existing_blog.get('content', {}).get('sections', [])[i] if existing_blog and i < len(existing_blog.get('content', {}).get('sections', [])) else None
            section_title = st.text_input(f'Section Title {i + 1}*', value=existing_section.get('title', '') if existing_section else '', key=f'section_title_{i}')
            section_content = st.text_area(f'Section Content {i + 1}*', value=existing_section.get('content', '') if existing_section else '', key=f'section_content_{i}')
            sections.append({'title': section_title, 'content': section_content})
        
        conclusion = st.text_area('Conclusion*', value=existing_blog.get('content', {}).get('conclusion', '') if existing_blog else '')
        
        submitted = st.form_submit_button('Submit')
        
        if submitted:
            if not all([title, category, description, image, introduction, conclusion] + 
                      [s['title'] for s in sections] + [s['content'] for s in sections]):
                st.error('Please fill in all required fields marked with *')
                return None
            
            blog_data = {
                'id': existing_blog.get('id', str(uuid.uuid4())) if existing_blog else str(uuid.uuid4()),
                'title': title,
                'category': category,
                'date': existing_blog.get('date', datetime.now().strftime('%Y-%m-%d')) if existing_blog else datetime.now().strftime('%Y-%m-%d'),
                'image': image,
                'description': description,
                'content': {
                    'introduction': introduction,
                    'sections': sections,
                    'conclusion': conclusion
                }
            }
            return blog_data
        return None

# Blog List View
def show_blog_list():
    st.title('Blog List')
    blogs = get_all_blogs()
    
    # Initialize delete confirmation state if not exists
    if 'delete_confirmation' not in st.session_state:
        st.session_state['delete_confirmation'] = None
    
    for blog in blogs:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"### {blog['title']}")
            st.write(f"Category: {blog['category']}")
            st.write(f"Date: {blog['date']}")
        with col2:
            delete_key = f"delete_{blog['id']}"
            if st.button('Delete', key=delete_key):
                st.session_state['delete_confirmation'] = blog['id']
            
            # Show confirmation dialog if this blog is pending deletion
            if st.session_state.get('delete_confirmation') == blog['id']:
                st.warning('Are you sure you want to delete this blog?')
                col3, col4 = st.columns([1, 1])
                with col3:
                    if st.button('Yes', key=f"yes_{blog['id']}"):
                        if delete_blog(blog['id']):
                            st.success('Blog deleted successfully')
                            st.session_state['delete_confirmation'] = None
                            st.experimental_rerun()
                with col4:
                    if st.button('No', key=f"no_{blog['id']}"):
                        st.session_state['delete_confirmation'] = None
                        st.experimental_rerun()
        st.markdown('---')

# Create Blog View
def show_create_blog():
    st.title('Create New Blog')
    
    # Initialize form data in session state if not exists
    if 'create_blog_data' not in st.session_state:
        st.session_state['create_blog_data'] = None
    
    # Get blog data from form
    if st.session_state.get('create_blog_data') is None:
        blog_data = blog_form()
        if blog_data:
            st.session_state['create_blog_data'] = blog_data
    
    # Show confirmation dialog if we have blog data
    if st.session_state.get('create_blog_data'):
        st.warning('Are you sure you want to submit this blog?')
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button('Yes', key='confirm_create_yes'):
                result = create_blog(st.session_state['create_blog_data'])
                if result:
                    st.success('Blog created successfully')
                    # Clear form data and redirect
                    st.session_state['create_blog_data'] = None
                    st.session_state['page'] = 'Blog List'
                    st.experimental_rerun()
                else:
                    st.error('Failed to create blog. Please try again.')
        with col2:
            if st.button('No', key='confirm_create_no'):
                st.session_state['create_blog_data'] = None
                st.experimental_rerun()

# Edit Blog View
def show_edit_blog():
    st.title('Edit Blog')
    blogs = get_all_blogs()
    
    # Create a dictionary of blog titles and their IDs
    blog_titles = {blog['title']: blog['id'] for blog in blogs}
    
    # Dropdown for blog selection
    selected_title = st.selectbox('Select a blog to edit', options=list(blog_titles.keys()))
    
    if selected_title:
        blog_id = blog_titles[selected_title]
        st.session_state['edit_blog_id'] = blog_id
        
        blog = get_blog_by_id(blog_id)
        if not blog:
            st.error('Blog not found')
            return
    
    blog_data = blog_form(blog)
    if blog_data:
        if update_blog(blog['id'], blog_data):
            st.success('Blog updated successfully')
            st.session_state['page'] = 'Blog List'
            del st.session_state['edit_blog_id']
            st.experimental_rerun()

# Main App
def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Blog List'
    
    page = sidebar_nav()
    st.session_state['page'] = page
    
    if page == 'Blog List':
        show_blog_list()
    elif page == 'Create Blog':
        show_create_blog()
    elif page == 'Edit Blog':
        show_edit_blog()

if __name__ == '__main__':
    main()