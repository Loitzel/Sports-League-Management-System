from ldap3 import Server, Connection, ALL, SUBTREE
from config import Config
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def authenticate_user(username, password):
    """
    Authenticate user against LDAP server
    
    Args:
        username (str): Username to authenticate
        password (str): Password to authenticate with
    
    Returns:
        bool: True if authentication successful, False otherwise
    """
    logger.info(f"LDAP authentication attempt started for user: {username}")
    
    try:
        # Create server object
        server = Server(Config.LDAP_SERVER, get_info=ALL)
        logger.info(f"Connected to LDAP server: {Config.LDAP_SERVER}")
        
        # Format search filter with username
        search_filter = Config.LDAP_USER_SEARCH_FILTER.format(username=username)
        logger.debug(f"Search filter: {search_filter} with base DN: {Config.LDAP_BASE_DN}")
        
        # Establish connection with bind credentials
        conn = Connection(
            server,
            user=Config.LDAP_BIND_DN,
            password=Config.LDAP_BIND_PASSWORD,
            auto_bind=True
        )
        logger.info("Successfully bound to LDAP server with service account")
        
        # Search for the user
        conn.search(
            search_base=Config.LDAP_BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['uid']
        )
        
        if len(conn.entries) > 0:
            # Get user DN
            user_dn = conn.entries[0].entry_dn
            logger.info(f"User found in LDAP with DN: {user_dn}")
            
            # Try to bind as the user to verify password
            user_conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=False
            )
            
            authenticated = user_conn.bind()
            logger.info(f"Password verification result for user {username}: {'SUCCESS' if authenticated else 'FAILED'}")
            
            user_conn.unbind()
            conn.unbind()
            
            return authenticated
        else:
            # User not found in LDAP
            logger.warning(f"User '{username}' not found in LDAP directory")
            conn.unbind()
            return False
            
    except Exception as e:
        logger.error(f"LDAP authentication error for user {username}: {str(e)}")
        return False


def get_user_info(username):
    """
    Retrieve user information from LDAP server
    
    Args:
        username (str): Username to look up
    
    Returns:
        dict: User information or None if user not found
    """
    logger.info(f"Retrieving user information from LDAP for user: {username}")
    
    try:
        # Create server object
        server = Server(Config.LDAP_SERVER, get_info=ALL)
        logger.info(f"Connected to LDAP server: {Config.LDAP_SERVER}")
        
        # Format search filter with username
        search_filter = Config.LDAP_USER_SEARCH_FILTER.format(username=username)
        logger.debug(f"Search filter: {search_filter} with base DN: {Config.LDAP_BASE_DN}")
        
        # Establish connection with bind credentials
        conn = Connection(
            server,
            user=Config.LDAP_BIND_DN,
            password=Config.LDAP_BIND_PASSWORD,
            auto_bind=True
        )
        logger.info("Successfully bound to LDAP server with service account")
        
        # Search for the user with common attributes
        conn.search(
            search_base=Config.LDAP_BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['displayName', 'mail', 'cn', 'givenName', 'sn']
        )
        
        if len(conn.entries) > 0:
            user_entry = conn.entries[0]
            logger.info(f"User information retrieved successfully for: {username}")
            user_info = {
                'username': username,
                'display_name': str(user_entry.displayName) if hasattr(user_entry, 'displayName') else username,
                'email': str(user_entry.mail) if hasattr(user_entry, 'mail') else '',
                'first_name': str(user_entry.givenName) if hasattr(user_entry, 'givenName') else '',
                'last_name': str(user_entry.sn) if hasattr(user_entry, 'sn') else ''
            }
            
            conn.unbind()
            return user_info
        else:
            logger.warning(f"No user information found in LDAP for: {username}")
            conn.unbind()
            return None
            
    except Exception as e:
        logger.error(f"LDAP user info retrieval error for user {username}: {str(e)}")
        return None