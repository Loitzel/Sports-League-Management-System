# test_sigenu.py
import requests
import os
import json
import sys

def sigenu_check(CI: str):
    """Versión original del código para testing"""
    username = os.getenv("USERNAME_SIGENU") 
    if not username:
        username = ""
    password = os.getenv("PASSWORD_SIGENU")
    if not password:
        password = ""
    auth = (username, password)

    # Corregido: eliminar espacios en la URL
    url = f'https://sigenu.uh.cu/sigenu-rest/student/fileStudent/getStudentAllData/{CI}'
    
    try:
        response = requests.get(url, auth=auth, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text[:500]}...")  # Primeros 500 caracteres
        
        if response.text:
            try:
                data = json.loads(response.text)
                print(f"Parsed JSON: {json.dumps(data, indent=2)[:500]}...")
                if data and len(data) > 0:
                    return True
                else:
                    return False
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                return False
        else:
            print("Empty response")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    # Configurar credenciales (ajusta según tus variables de entorno)
    if "USERNAME_SIGENU" not in os.environ:
        os.environ["USERNAME_SIGENU"] = input("Username SIGENU: ")
    if "PASSWORD_SIGENU" not in os.environ:
        import getpass
        os.environ["PASSWORD_SIGENU"] = getpass.getpass("Password SIGENU: ")
    
    CI = "01011166680"
    print(f"Testing CI: {CI}")
    print("-" * 50)
    
    result = sigenu_check(CI)
    print("-" * 50)
    print(f"Result: {result}")