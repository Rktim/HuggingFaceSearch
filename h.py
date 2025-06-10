import streamlit as st
from huggingface_hub import HfApi, list_models

# Set page config with minimal styling
st.set_page_config(
    page_title="Hugging Face Models",
    page_icon="🤖",
    layout="centered"
)

# Add minimal custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .model-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid #eee;
    }
    .search-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        max-width: 600px;
        margin: 0 auto;
    }
    .stButton > button {
        background-color: #FFD43B;
        color: #000000;
        width: 120px;
        margin: 0 auto;
        padding: 0.25rem 1rem;
        border: none;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #FFE066;
    }
    .sort-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }
    .sort-container .stSelectbox {
        width: 200px;
    }
    .sort-container .stSelectbox > div {
        font-size: 0.9rem;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #666;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
    }
    .logo-container img {
        max-width: 200px;
        height: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Add Hugging Face logo
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("https://huggingface.co/front/assets/huggingface_logo-noborder.svg", width=200)
st.markdown('</div>', unsafe_allow_html=True)

# Clean header
st.title("Hugging Face Models")
st.markdown("Effortlessly search and filter Hugging Face models to find your perfect model.")

# Initialize API
token = st.secrets["hftoken"]
api = HfApi(token=token)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'models' not in st.session_state:
    st.session_state.models = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'sort_by' not in st.session_state:
    st.session_state.sort_by = "name_asc"

# Simple search interface with better layout
with st.container():
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    search_query = st.text_input("Search models", placeholder="Enter model name or keyword", value=st.session_state.search_query)
    search_button = st.button("Search")
    st.markdown('</div>', unsafe_allow_html=True)

# Constants for pagination
RESULTS_PER_PAGE = 10

def perform_search(query):
    with st.spinner("Searching..."):
        models = list(list_models(filter=query))[:100]  # Limit to first 100 results
        st.session_state.models = models
        st.session_state.page = 0
        st.session_state.search_query = query
        return models

def sort_models(models, sort_by):
    if sort_by == "name_asc":
        return sorted(models, key=lambda x: x.id.lower())
    elif sort_by == "name_desc":
        return sorted(models, key=lambda x: x.id.lower(), reverse=True)
    elif sort_by == "size_asc":
        return sorted(models, key=lambda x: getattr(x, 'size', 0) or 0)
    elif sort_by == "size_desc":
        return sorted(models, key=lambda x: getattr(x, 'size', 0) or 0, reverse=True)
    elif sort_by == "downloads_desc":
        return sorted(models, key=lambda x: getattr(x, 'downloads', 0) or 0, reverse=True)
    return models

if search_button:
    if search_query:
        models = perform_search(search_query)
    else:
        st.info("Please enter a search query")
elif st.session_state.models:  # Show results if we have them in session state
    models = st.session_state.models
else:
    models = []

# Display results if we have any
if models:
    st.write(f"Found {len(models)} models")
    
    # Add sorting options
    st.markdown('<div class="sort-container">', unsafe_allow_html=True)
    sort_by = st.selectbox(
        "Sort by",
        options=[
            "name_asc",
            "name_desc",
            "size_asc",
            "size_desc",
            "downloads_desc"
        ],
        format_func=lambda x: {
            "name_asc": "Name (A-Z)",
            "name_desc": "Name (Z-A)",
            "size_asc": "Size (Smallest First)",
            "size_desc": "Size (Largest First)",
            "downloads_desc": "Most Downloaded"
        }[x],
        index=0 if st.session_state.sort_by not in ["name_asc", "name_desc", "size_asc", "size_desc", "downloads_desc"] 
        else ["name_asc", "name_desc", "size_asc", "size_desc", "downloads_desc"].index(st.session_state.sort_by)
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sort models
    if sort_by != st.session_state.sort_by:
        st.session_state.sort_by = sort_by
        st.session_state.page = 0
        st.rerun()
    
    sorted_models = sort_models(models, sort_by)
    
    # Display models with pagination
    start_idx = st.session_state.page * RESULTS_PER_PAGE
    end_idx = start_idx + RESULTS_PER_PAGE
    current_models = sorted_models[start_idx:end_idx]
    
    for model in current_models:
        model_info = f"{model.id}"
        if hasattr(model, 'size'):
            model_info += f" | Size: {model.size:,} bytes"
        if hasattr(model, 'downloads'):
            model_info += f" | Downloads: {model.downloads:,}"
            
        st.markdown(f"""
            <div class="model-item">
                {model_info}
            </div>
        """, unsafe_allow_html=True)
    
    # Pagination controls
    if len(models) > RESULTS_PER_PAGE:
        total_pages = (len(models) - 1) // RESULTS_PER_PAGE + 1
        st.write(f"Page {st.session_state.page + 1} of {total_pages}")
        
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("Previous", disabled=st.session_state.page == 0):
                st.session_state.page -= 1
                st.rerun()
        with col_next:
            if st.button("Next", disabled=st.session_state.page >= total_pages - 1):
                st.session_state.page += 1
                st.rerun()

# Footer with correct markdown syntax
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown("Created by [Raktim](https://github.com/Rktim)")
st.markdown('</div>', unsafe_allow_html=True)