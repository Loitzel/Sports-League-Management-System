from ldap3 import Server, Connection, ALL, SUBTREE
from config import Config


def authenticate_user(username, password):
    """
    Authenticate user against LDAP server
    
    Args:
        username (str): Username to authenticate
        password (str): Password to authenticate with
    
    Returns:
        bool: True if authentication successful, False otherwise
    """
    try:
        # Create server object
        server = Server(Config.LDAP_SERVER, get_info=ALL)
        
        # Format search filter with username
        search_filter = Config.LDAP_USER_SEARCH_FILTER.format(username=username)
        
        # Establish connection with bind credentials
        conn = Connection(
            server,
            user=Config.LDAP_BIND_DN,
            password=Config.LDAP_BIND_PASSWORD,
            auto_bind=True
        )
        
        # Search for the user
        conn.search(
            search_base=Config.LDAP_BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['dn']
        )
        
        if len(conn.entries) > 0:
            # Get user DN
            user_dn = conn.entries[0].entry_dn
            
            # Try to bind as the user to verify password
            user_conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=False
            )
            
            authenticated = user_conn.bind()
            user_conn.unbind()
            
            conn.unbind()
            
            return authenticated
        else:
            # User not found in LDAP
            conn.unbind()
            return False
            
    except Exception as e:
        print(f"LDAP authentication error: {str(e)}")
        return False


def get_user_info(username):
    """
    Retrieve user information from LDAP server
    
    Args:
        username (str): Username to look up
    
    Returns:
        dict: User information or None if user not found
    """
    try:
        # Create server object
        server = Server(Config.LDAP_SERVER, get_info=ALL)
        
        # Format search filter with username
        search_filter = Config.LDAP_USER_SEARCH_FILTER.format(username=username)
        
        # Establish connection with bind credentials
        conn = Connection(
            server,
            user=Config.LDAP_BIND_DN,
            password=Config.LDAP_BIND_PASSWORD,
            auto_bind=True
        )
        
        # Search for the user with common attributes
        conn.search(
            search_base=Config.LDAP_BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['displayName', 'mail', 'cn', 'givenName', 'sn']
        )
        
        if len(conn.entries) > 0:
            user_entry = conn.entries[0]
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
            conn.unbind()
            return None
            
    except Exception as e:
        print(f"LDAP user info retrieval error: {str(e)}")
        return None