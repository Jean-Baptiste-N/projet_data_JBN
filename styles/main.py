def load_css():
    return """
    <style>
    .main { padding: 0rem 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #abc4f7;
        border-radius: 4px 4px 0px 0px;
        color: black;
    }
    .error-message {
        color: red;
        padding: 1rem;
        border: 1px solid red;
        border-radius: 4px;
    }
    .nav-button {
        background-color: #abc4f7;
        color: black;
        padding: 10px 20px;
        border-radius: 4px;
        text-decoration: none;
        margin: 5px;
        cursor: pointer;
        border: none;
    }
    .nav-button:hover {
        background-color: #8ba8e0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .back-to-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999;
        background-color: #abc4f7;
        color: black;
        padding: 10px;
        border-radius: 50%;
        text-decoration: none;
        display: none;
    }
    </style>
    """
