import streamlit as st 
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#DONE
#NEEDS TESTING

# Set page config
st.set_page_config(
    page_title="Movie Database Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown(
    """
    <style>
        /* Base responsive settings */
        .stApp {
            max-width: 100%;
            padding: 1rem;
            margin: 0 auto;
            box-sizing: border-box;
        }
        
        /* Responsive container adjustments */
        .element-container {
            padding: 0.5rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            width: 100%;
        }
        
        /* Responsive grid layout */
        .row-widget.stHorizontal {
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        /* Responsive images */
        img {
            max-width: 100%;
            height: auto;
        }
        
        /* Responsive text sizes */
        @media screen and (max-width: 768px) {
            h1 {
                font-size: 1.5rem !important;
            }
            h2 {
                font-size: 1.25rem !important;
            }
            h3 {
                font-size: 1.1rem !important;
            }
            p {
                font-size: 0.9rem !important;
            }
            .stButton > button {
                width: 100%;
                margin: 0.25rem 0;
            }
        }
        
        /* Responsive movie grid */
        @media screen and (max-width: 640px) {
            .movie-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 1rem;
            }
        }
        
        @media screen and (min-width: 641px) and (max-width: 1024px) {
            .movie-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media screen and (min-width: 1025px) {
            .movie-grid {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        
        /* Responsive form elements */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            max-width: 100%;
            box-sizing: border-box;
        }
        
        /* Responsive charts */
        .js-plotly-plot {
            width: 100% !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Load environment variables
load_dotenv()



# Load the secrets.toml file


# Access variables
tmdb_access_token = st.secrets["general"]["TMDB_ACCESS_TOKEN"]
neo4j_uri = st.secrets["general"]["NEO4J_URI"]
neo4j_user = st.secrets["general"]["NEO4J_USER"]
neo4j_password = st.secrets["general"]["NEO4J_PASSWORD"]
email_user = st.secrets["general"]["EMAIL_USER"]
email_password = st.secrets["general"]["EMAIL_PASSWORD"]
email_receiver = st.secrets["general"]["EMAIL_RECEIVER"]

# neo4j_uri = os.getenv('NEO4J_URI2')
# neo4j_user = os.getenv('NEO4J_USER2')
# neo4j_password = os.getenv('NEO4J_PASSWORD2')
# email_password = os.getenv('EMAIL_PASSWORD')
# email_user = os.getenv('EMAIL_USER')
# email_receiver = os.getenv('EMAIL_RECEIVER')




# Initialize Neo4j connection
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))


# st.markdown(
#     """
#     <style>
#         .stApp {
#             background-color: #FFA421;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

def run_query(query, params=None):
    with driver.session() as session:
        result = session.run(query, params)
        return [dict(record) for record in result]

def send_feedback_email(user_name, user_email, feedback_text, satisfaction):
    print("Starting email send process...")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_receiver
        msg['Subject'] = f"✨ New User Feedback from {user_name} ✨"
        
        # Create a professionally formatted HTML email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
                <h2 style="color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    New Feedback Received
                </h2>
                
                <div style="background-color: white; padding: 20px; border-radius: 5px; margin-top: 20px;">
                    <h3 style="color: #2c3e50; margin-bottom: 15px;">User Information</h3>
                    <p><strong>Name:</strong> {user_name}</p>
                    <p><strong>Email:</strong> {user_email}</p>
                    <p><strong>Satisfaction Rating:</strong> {satisfaction}</p>
                    
                    <h3 style="color: #2c3e50; margin-top: 25px; margin-bottom: 15px;">Feedback Message</h3>
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; border-radius: 4px;">
                        {feedback_text}
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #666;">
                    <p>This feedback was submitted through the Movie Database Explorer application.</p>
                    <p>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html_body, 'html'))
        
        print("Connecting to SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("Attempting login...")
        server.login(email_user, email_password)
        
        print("Sending email...")
        server.sendmail(email_user, email_receiver, msg.as_string())
        server.quit()
        
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

# # Set page config
# st.set_page_config(
#     page_title="Movie Database Explorer",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Title and sidebar
st.title("🎬 Movie Database Explorer")

# Initialize session states if they don't exist
if 'feedback_sent' not in st.session_state:
    st.session_state.feedback_sent = False

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Choose a page", 
    ["Movie Search", "Movie Recommendations", "Analytics Dashboard"]
)

if page == "Movie Search":
    main_col, search_col = st.columns([2, 1])
    
    with search_col:
        search_open = st.button("🔍 Advanced Search", key="open_search")
        
        if search_open:
            search_term = st.text_input("Movie title", "")
            
            sort_options = [
                "Release Date (Newest)",
                "Release Date (Oldest)",
                "Rating (Highest)",
                "Rating (Lowest)"
            ]
            selected_sort = st.selectbox("Sort by", sort_options)
            
            with st.expander("Rating & Year Filters"):
                min_rating = st.slider("Minimum Rating", 0.0, 10.0, 0.0, 0.1)
                year_range = st.slider(
                    "Release Year Range",
                    2000, 2024, (2000, 2024)
                )
        else:
            search_term = st.text_input("Quick search", placeholder="Enter movie title")
            selected_sort = "Rating (Highest)"
            min_rating = 0.0
            year_range = (2000, 2024)
        
        with st.form("feedback_form", clear_on_submit=True):
            st.write("### Share Your Feedback")
            col1, col2 = st.columns(2)
            
            with col1:
                user_name = st.text_input("Name")
            with col2:
                user_email = st.text_input("Email")
                
            feedback_text = st.text_area(
                "Your thoughts",
                placeholder="How can we improve your experience?"
            )
            satisfaction = st.select_slider(
                "How was your experience?",
                options=["😞", "😐", "🙂", "😊", "🤩"],
                value="🙂"
            )
            
            submit_button = st.form_submit_button("Submit Feedback")
            
            if submit_button:
                if user_name and feedback_text and user_email:
                    # Basic email validation
                    if "@" in user_email and "." in user_email:
                        with st.spinner('Sending feedback...'):
                            if send_feedback_email(user_name, user_email, feedback_text, satisfaction):
                                st.success("Thank you for your feedback! We appreciate your input.")
                                st.session_state.feedback_sent = True
                            else:
                                st.error("Failed to send feedback. Please try again.")
                    else:
                        st.error("Please enter a valid email address.")
                else:
                    st.warning("Please fill in all fields (name, email, and feedback).")

    with main_col:
        # Construct the query based on filters and sorting
        sort_clause = {
            "Release Date (Newest)": "ORDER BY m.release_date DESC",
            "Release Date (Oldest)": "ORDER BY m.release_date ASC",
            "Rating (Highest)": "ORDER BY m.vote_average DESC",
            "Rating (Lowest)": "ORDER BY m.vote_average ASC"
        }[selected_sort]
        
        if not search_term:
            query = f"""
            MATCH (m:Movie)
            WHERE m.vote_average >= $min_rating
            AND toInteger(substring(m.release_date, 0, 4)) >= $start_year
            AND toInteger(substring(m.release_date, 0, 4)) <= $end_year
            RETURN m.title as title, 
                   m.release_date as release_date,
                   m.vote_average as rating,
                   m.overview as overview,
                   m.poster_path as poster,
                   m.vote_count as vote_count
            {sort_clause}
            LIMIT 15
            """
            results = run_query(query, {
                "min_rating": min_rating,
                "start_year": year_range[0],
                "end_year": year_range[1]
            })
        else:
            query = f"""
            MATCH (m:Movie)
            WHERE m.title CONTAINS $search_term
            AND m.vote_average >= $min_rating
            AND toInteger(substring(m.release_date, 0, 4)) >= $start_year
            AND toInteger(substring(m.release_date, 0, 4)) <= $end_year
            RETURN m.title as title, 
                   m.release_date as release_date,
                   m.vote_average as rating,
                   m.overview as overview,
                   m.poster_path as poster,
                   m.vote_count as vote_count
            {sort_clause}
            LIMIT 15
            """
            results = run_query(query, {
                "search_term": search_term,
                "min_rating": min_rating,
                "start_year": year_range[0],
                "end_year": year_range[1]
            })
        
        # Display movies in a grid
        if results:
            for i in range(0, len(results), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(results):
                        movie = results[i + j]
                        with cols[j]:
                            if movie['poster']:
                                poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster']}"
                                st.image(poster_url, use_container_width=True)
                            else:
                                st.image("https://via.placeholder.com/300x450?text=No+Poster", use_container_width=True)
                            
                            st.subheader(movie['title'])
                            st.write(f"⭐ {movie['rating']:.1f}/10")
                            st.write(f"📅 {movie['release_date']}")
                            st.write(f"👥 {movie['vote_count']} votes")
                            
                            with st.expander("Overview"):
                                st.write(movie['overview'])
        else:
            if search_term:
                st.info("No movies found matching your criteria.")
            else:
                st.write("Explore movies using the search options")

# elif page == "Movie Recommendations":
#     st.header("🎯 Movie Recommendations")
    
#     query = """
#     MATCH (m:Movie)
#     RETURN m.title as title
#     ORDER BY m.title
#     """
#     movies = run_query(query)
#     movie_titles = [m['title'] for m in movies]
    
#     selected_movie = st.selectbox("Select a movie you like", movie_titles)
    
#     if selected_movie:
#         query = """
#         MATCH (source:Movie {title: $title})
#         MATCH (m:Movie)
#         WHERE m <> source
#         OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)-[:ACTED_IN]->(source)
#         OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)-[:DIRECTED]->(source)
#         WITH m, source,
#              count(DISTINCT a) AS common_actors,
#              count(DISTINCT d) AS common_directors,
#              abs(source.vote_average - m.vote_average) AS rating_diff
#         WITH m, 
#              (common_actors * 3) + 
#              (common_directors * 5) + 
#              (10 - rating_diff) AS recommendation_score,
#              common_actors,
#              common_directors
#         WHERE recommendation_score > 0
#         RETURN m.title AS title,
#                m.vote_average AS rating,
#                m.overview AS overview,
#                m.poster_path AS poster,
#                m.release_date AS release_date,
#                recommendation_score,
#                common_actors,
#                common_directors
#         ORDER BY recommendation_score DESC
#         LIMIT 5
#         """
#         recommendations = run_query(query, {"title": selected_movie})
        
#         if recommendations:
#             st.subheader("Recommended Movies")
#             for movie in recommendations:
#                 cols = st.columns([1, 2])
                
#                 with cols[0]:
#                     if movie['poster']:
#                         poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster']}"
#                         st.image(poster_url, width=200)
#                     else:
#                         st.image("https://via.placeholder.com/300x450?text=No+Poster", width=200)
                
#                 with cols[1]:
#                     st.subheader(movie['title'])
#                     st.write(f"⭐ Rating: {movie['rating']:.1f}/10")
#                     st.write(f"📅 Release Date: {movie['release_date']}")
#                     st.write(f"🎯 Recommendation Score: {movie['recommendation_score']:.1f}")
#                     st.write(f"👥 Common Actors: {movie['common_actors']}")
#                     st.write(f"🎬 Common Directors: {movie['common_directors']}")
                    
#                     with st.expander("Overview"):
#                         st.write(movie['overview'])
                
#                 st.divider()

elif page == "Movie Recommendations":
    st.header("🎯 Movie Recommendations")
    
    # Initialize session states for popups
    if 'show_cast_popup' not in st.session_state:
        st.session_state.show_cast_popup = False
        st.session_state.cast_popup_data = None
        st.session_state.cast_popup_type = None
        st.session_state.button_clicked = False
    
    query = """
    MATCH (m:Movie)
    RETURN m.title as title
    ORDER BY m.title
    """
    movies = run_query(query)
    movie_titles = [m['title'] for m in movies]
    
    selected_movie = st.selectbox("Select a movie you like", movie_titles)
    
    def show_cast_popup(data, popup_type):
        st.session_state.show_cast_popup = True
        st.session_state.cast_popup_data = data
        st.session_state.cast_popup_type = popup_type
        st.session_state.button_clicked = True
    
    def close_popup():
        st.session_state.show_cast_popup = False
        st.session_state.cast_popup_data = None
        st.session_state.cast_popup_type = None
        st.session_state.button_clicked = False
    
    if selected_movie:
        # Updated query
        query="""
                MATCH (source:Movie {title: $title})
                MATCH (m:Movie)
                WHERE m <> source

                // Find common actors
                OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)-[:ACTED_IN]->(source)
                WITH m, source, collect(DISTINCT {
                    name: a.name,
                    profile_path: a.profile_path,
                    id: CASE WHEN a IS NOT NULL THEN elementId(a) ELSE NULL END
                }) AS common_actors

                // Find common directors
                OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)-[:DIRECTED]->(source)
                WITH m, source, common_actors, collect(DISTINCT {
                    name: d.name,
                    profile_path: d.profile_path,
                    id: CASE WHEN d IS NOT NULL THEN elementId(d) ELSE NULL END
                }) AS common_directors

                // Find common genres
                OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(source)
                WITH m, source, common_actors, common_directors, collect(DISTINCT g.name) AS common_genres

                // Find common keywords
                OPTIONAL MATCH (m)-[:HAS_KEYWORD]->(k:Keyword)<-[:HAS_KEYWORD]-(source)
                WITH m, common_actors, common_directors, common_genres, collect(DISTINCT k.name) AS common_keywords

                // Filter out nulls from the lists
                WITH m, 
                    [x IN common_actors WHERE x.id IS NOT NULL] AS common_actors,
                    [x IN common_directors WHERE x.id IS NOT NULL] AS common_directors,
                    common_genres,
                    common_keywords

                // Calculate weights for different factors
                WITH m, 
                    common_actors,
                    common_directors,
                    common_genres,
                    common_keywords,
                    size(common_actors) AS actor_count,
                    size(common_directors) AS director_count,
                    size(common_genres) AS genre_count,
                    size(common_keywords) AS keyword_count,
                    m.vote_average AS vote_average,
                    m.vote_count AS vote_count,
                    m.popularity AS popularity

                // Calculate normalized scores (0-1 range)
                WITH m, common_actors, common_directors, common_genres, common_keywords,
                    actor_count, director_count, genre_count, keyword_count,
                    CASE WHEN vote_count > 1000 THEN vote_average / 10 ELSE (vote_average * sqrt(vote_count/1000)) / 10 END AS normalized_rating,
                    popularity / 1000 AS normalized_popularity

                // Calculate final recommendation score with weighted components
                WITH m, common_actors, common_directors, common_genres, common_keywords,
                    actor_count, director_count, genre_count, keyword_count,
                    (actor_count * 3 +              // Weight for common actors
                    director_count * 5 +           // Weight for common directors
                    genre_count * 2 +             // Weight for common genres
                    keyword_count * 1 +           // Weight for common keywords
                    normalized_rating * 4 +        // Weight for rating
                    normalized_popularity * 2      // Weight for popularity
                    ) AS recommendation_score

                // Filter out movies with insufficient connections
                WHERE (actor_count > 0 OR director_count > 0 OR genre_count > 0 OR keyword_count > 0)

                // Return results
                RETURN m.title AS title,
                    m.vote_average AS rating,
                    m.vote_count AS vote_count,
                    m.overview AS overview,
                    m.poster_path AS poster,
                    m.release_date AS release_date,
                    recommendation_score,
                    common_actors,
                    common_directors,
                    common_genres,
                    common_keywords,
                    actor_count,
                    director_count,
                    genre_count,
                    keyword_count
                ORDER BY recommendation_score DESC
                LIMIT 10

                """
        # query = """
        #     MATCH (source:Movie {title: $title})
        #     MATCH (m:Movie)
        #     WHERE m <> source

        #     // Find common actors
        #     OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)-[:ACTED_IN]->(source)
        #     WITH m, source, collect(DISTINCT {
        #         name: a.name,
        #         profile_path: a.profile_path,
        #         id: CASE WHEN a IS NOT NULL THEN id(a) ELSE NULL END
        #     }) AS common_actors

        #     // Find common directors
        #     OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)-[:DIRECTED]->(source)
        #     WITH m, common_actors, collect(DISTINCT {
        #         name: d.name,
        #         profile_path: d.profile_path,
        #         id: CASE WHEN d IS NOT NULL THEN id(d) ELSE NULL END
        #     }) AS common_directors

        #     // Filter out nulls from the lists
        #     WITH m, 
        #         [x IN common_actors WHERE x.id IS NOT NULL] AS common_actors,
        #         [x IN common_directors WHERE x.id IS NOT NULL] AS common_directors

        #     // Calculate recommendation score
        #     WITH m, 
        #         common_actors,
        #         common_directors,
        #         size(common_actors) AS actor_count,
        #         size(common_directors) AS director_count,
        #         (size(common_actors) * 3) + (size(common_directors) * 5) AS recommendation_score

        #     // Filter out movies with no common actors or directors
        #     WHERE (actor_count > 0 OR director_count > 0)
        #     RETURN m.title AS title,
        #         m.vote_average AS rating,
        #         m.overview AS overview,
        #         m.poster_path AS poster,
        #         m.release_date AS release_date,
        #         recommendation_score,
        #         common_actors,
        #         common_directors,
        #         actor_count,
        #         director_count
        #     ORDER BY recommendation_score DESC, rating ASC
        #     LIMIT 4;

        #     """
        # Pass the selected_movie as the title parameter
        recommendations = run_query(query, {"title": selected_movie})
        
        # Display popup if active
        if st.session_state.show_cast_popup and st.session_state.cast_popup_data and st.session_state.button_clicked:
            popup_data = st.session_state.cast_popup_data
            popup_type = st.session_state.cast_popup_type
            
            with st.sidebar:
                st.header(f"Common {popup_type.title()}s")
                if st.button("Close", key="close_popup"):
                    close_popup()
                    st.rerun()
                
                for person in popup_data:
                    st.write("---")
                    if person['profile_path']:
                        st.image(f"https://image.tmdb.org/t/p/w185{person['profile_path']}")
                    else:
                        st.image("https://via.placeholder.com/185x278?text=No+Photo", width=185)
                    
                    st.subheader(person['name'])
                    
                    # Fetch filmography
                    filmography_query = """
                        MATCH (p:Person)
                    WHERE elementId(p) = $person_id
                    MATCH (p)-[r:ACTED_IN|DIRECTED]->(m:Movie)
                    RETURN m.title as title,
                           m.release_date as release_date,
                           m.vote_average as rating
                    ORDER BY m.release_date DESC

                    """
                    # MATCH (p:Person)-[:{popup_type.upper()}_IN]->(m:Movie)
                    # WHERE id(p) = $person_id
                    # RETURN m.title as title,
                    #        m.release_date as release_date,
                    #        m.vote_average as rating
                    # ORDER BY m.release_date DESC
                    
                    filmography = run_query(filmography_query, {"person_id": person['id']})
                    
                    if filmography:
                        st.write("Filmography:")
                        df = pd.DataFrame(filmography)
                        df.columns = ['Movie', 'Release Date', 'Rating']
                        st.dataframe(df, hide_index=True)
        
        if recommendations:
            st.subheader("Recommended Movies")
            
            for idx, movie in enumerate(recommendations):
                with st.container():
                    cols = st.columns([1, 2])
                    
                    with cols[0]:
                        if movie['poster']:
                            poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster']}"
                            st.image(poster_url, width=200)
                        else:
                            st.image("https://via.placeholder.com/300x450?text=No+Photo", width=200)
                    
                    with cols[1]:
                        st.subheader(movie['title'])
                        st.write(f"⭐ Rating: {movie['rating']:.1f}/10")
                        st.write(f"😎 Popularity votes: {movie['vote_count']}")
                        st.write(f"📅 Release Date: {movie['release_date']}")
                        
                        # Inline recommendation score and cast/crew buttons
                        actors_col, directors_col = st.columns(2)
                        
                        # with score_col:
                        #     st.write(f"🎯 Recommendation Score: {movie['recommendation_score']:.1f}")
                        
                        # Only show actor button if there are common actors
                        if movie['actor_count'] > 0:
                            with actors_col:
                                if st.button(f"👥 {movie['actor_count']} Common Actors", key=f"actors_{idx}"):
                                    show_cast_popup(movie['common_actors'], "acted")
                                    st.rerun()
                        
                        
                        # Only show director button if there are common directors
                        if movie['director_count']>0:
                            with directors_col:
                                if st.button(f"🎬 {movie['director_count']} Common Directors", key=f"directors_{idx}"):
                                    show_cast_popup(movie['common_directors'], "direct")
                                    st.rerun()
                        
                        
                        with st.expander("Overview"):
                            st.write(movie['overview'])
                
                st.divider()

elif page == "Analytics Dashboard":
    st.header("📊 Analytics Dashboard")
    tab1, tab2, tab3 = st.tabs(["Top Rated", "Most Popular", "Actor Analysis"])

    # Get screen width using Streamlit's layout features
    use_container_width = True

    # Helper function to create responsive plots
    def create_responsive_bar(df, x_col, y_col, title, x_label, y_label, color_col=None):
        # Determine orientation based on data length and column width
        orientation = 'h' if len(df) > 8 else 'v'
        
        if orientation == 'h':
            fig = px.bar(
                df,
                y=x_col,  # Swap x and y for horizontal
                x=y_col,
                title=title,
                labels={x_col: x_label, y_col: y_label},
                color=color_col if color_col else y_col,
                color_continuous_scale='viridis',
                orientation='h'
            )
        else:
            fig = px.bar(
                df,
                x=x_col,
                y=y_col,
                title=title,
                labels={x_col: x_label, y_col: y_label},
                color=color_col if color_col else y_col,
                color_continuous_scale='viridis'
            )
        
        # Update layout for better readability
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_tickangle=-45 if orientation == 'v' else 0,
            height=500
        )
        return fig

    with tab1:
        query = """
        MATCH (m:Movie)
        WHERE m.vote_count > 100
        RETURN m.title as title, m.vote_average as rating, m.vote_count as votes
        ORDER BY m.vote_average DESC
        LIMIT 10
        """
        top_rated = pd.DataFrame(run_query(query))
        st.subheader("Top Rated Movies")
        fig = create_responsive_bar(
            top_rated,
            'title',
            'rating',
            "Top Rated Movies",
            'Movie Title',
            'Rating',
            'votes'
        )
        st.plotly_chart(fig, use_container_width=use_container_width)

    with tab2:
        query = """
        MATCH (m:Movie)
        RETURN m.title as title, m.popularity as popularity, m.vote_count as votes
        ORDER BY m.popularity DESC
        LIMIT 10
        """
        popular = pd.DataFrame(run_query(query))
        st.subheader("Most Popular Movies")
        fig = create_responsive_bar(
            popular,
            'title',
            'popularity',
            "Most Popular Movies",
            'Movie Title',
            'Popularity Score',
            'votes'
        )
        st.plotly_chart(fig, use_container_width=use_container_width)

    with tab3:
        query = """
        MATCH (a:Person)-[r:ACTED_IN]->(m:Movie)
        RETURN a.name as actor, count(m) as movie_count, avg(m.vote_average) as avg_rating
        ORDER BY movie_count DESC
        LIMIT 10
        """
        prolific_actors = pd.DataFrame(run_query(query))
        st.subheader("Most Prolific Actors")
        fig = create_responsive_bar(
            prolific_actors,
            'actor',
            'movie_count',
            "Actors with Most Movies",
            'Actor Name',
            'Number of Movies',
            'avg_rating'
        )
        st.plotly_chart(fig, use_container_width=use_container_width)


# Cleanup
driver.close()