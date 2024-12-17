import streamlit as st
from atproto import Client, models
from web3 import Web3
import imagehash
from PIL import Image
import json
from datetime import datetime

class BlueskyVerificationSystem:
    def __init__(self):
        # Initialize Bluesky client
        self.client = Client()
        # Store the client in session state
        if 'bluesky_client' not in st.session_state:
            st.session_state.bluesky_client = self.client

    def login_bluesky(self, username, password):
        """Login to Bluesky"""
        try:
            self.client.login(username, password)
            # Store login state
            st.session_state.is_logged_in = True
            st.session_state.bluesky_client = self.client
            return True
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            return False

    def get_post_images(self, post_uri):
        """Fetch images from a Bluesky post"""
        if not st.session_state.get('is_logged_in', False):
            raise Exception("Not logged in. Please login first.")
            
        try:
            post_id = post_uri.split('/')[-1]
            st.write(f"Attempting to fetch post ID: {post_id}")
            
            client = st.session_state.bluesky_client
            
            try:
                # Get the post record
                response = client.com.atproto.repo.get_record({
                    'repo': client.me.did,
                    'collection': 'app.bsky.feed.post',
                    'rkey': post_id
                })
                
                st.write("Post retrieved successfully")
                
                # Access response.value directly
                if not hasattr(response, 'value'):
                    st.error("Response does not contain value attribute")
                    return []
                
                value = response.value
                
                # Access embed directly as an attribute
                if not hasattr(value, 'embed'):
                    st.warning("No embed found in post")
                    return []
                    
                embed = value.embed
                
                # Parse the embed string to extract the blob reference
                embed_str = str(embed)
                import re
                
                # Extract the link using regex
                link_match = re.search(r"link='([^']*)'", embed_str)
                if link_match:
                    cid = link_match.group(1)
                    st.write(f"Found image CID: {cid}")
                    
                    try:
                        # Get the image blob
                        image_data = client.com.atproto.sync.get_blob({
                            'did': client.me.did,
                            'cid': cid
                        })
                        st.write("Successfully retrieved image blob")
                        
                        # Convert blob data to displayable format
                        import io
                        from PIL import Image
                        
                        # Handle different blob data formats
                        if isinstance(image_data, bytes):
                            image = Image.open(io.BytesIO(image_data))
                        elif hasattr(image_data, 'content'):
                            image = Image.open(io.BytesIO(image_data.content))
                        else:
                            st.error("Unexpected image data format")
                            return []
                        
                        # Display the image using the new parameter name
                        st.image(image, caption="Retrieved image from post", use_container_width=True)
                        
                        return [image_data]
                    except Exception as e:
                        st.error(f"Error processing image blob: {str(e)}")
                        return []
                else:
                    st.warning("No image CID found in embed")
                    return []
                    
            except Exception as e:
                st.error(f"Error getting post: {str(e)}")
                return []
                
        except Exception as e:
            raise Exception(f"Error fetching post: {str(e)}")
    
    def compute_image_hash(self, image):
        """Compute perceptual hash of image"""
        return str(imagehash.average_hash(image))

def main():
    st.title("Bluesky Content Verification System")
    
    system = BlueskyVerificationSystem()
    
    # Bluesky Authentication
    with st.sidebar:
        st.header("Bluesky Authentication")
        username = st.text_input("Username", key="bluesky_username")
        password = st.text_input("App Password", type="password", key="bluesky_password")
        if st.button("Login"):
            if system.login_bluesky(username, password):
                st.success("Logged in successfully!")
    
    # Show main content only if logged in
    if st.session_state.get('is_logged_in', False):
        # Rest of your code...
        mode = st.sidebar.selectbox(
            "Select Mode",
            ["Register New Content", "Verify Content", "Check Status"]
        )
        
        if mode == "Verify Content":
            st.header("Verify Content")
            post_uri = st.text_input("Enter Bluesky Post URI")
            
            if st.button("Verify"):
                try:
                    images = system.get_post_images(post_uri)
                    # ... rest of verification code ...
                except Exception as e:
                    st.error(str(e))
    else:
        st.warning("Please login first using the sidebar.")

if __name__ == "__main__":
    main()