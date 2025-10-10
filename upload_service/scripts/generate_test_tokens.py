"""
Script para generar tokens JWT de prueba para los usuarios de prueba
"""
import jwt
import os
from datetime import datetime, timedelta

# Configuración JWT (debe coincidir con .env)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def generate_token(user_id: int, email: str, expiration_days: int = 30) -> str:
    """
    Genera un token JWT para un usuario
    """
    payload = {
        "sub": user_id,  # Subject (user_id)
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=expiration_days),
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def main():
    # Usuarios de prueba
    test_users = [
        {"id": 1, "email": "test1@example.com", "nombre": "Juan Pérez"},
        {"id": 2, "email": "test2@example.com", "nombre": "María González"},
        {"id": 3, "email": "test3@example.com", "nombre": "Carlos Rodríguez"},
        {"id": 4, "email": "admin@example.com", "nombre": "Admin Sistema"},
    ]

    print("\n" + "="*80)
    print("TOKENS JWT DE PRUEBA")
    print("="*80)
    print(f"\nSecretKey: {SECRET_KEY}")
    print(f"Algorithm: {ALGORITHM}")
    print(f"Expiración: 30 días\n")
    print("="*80)

    for user in test_users:
        token = generate_token(user["id"], user["email"])
        print(f"\nUsuario: {user['nombre']} ({user['email']})")
        print(f"User ID: {user['id']}")
        print(f"Token:")
        print(f"{token}")
        print("-"*80)

    print("\n" + "="*80)
    print("USO:")
    print("="*80)
    print("\nPara usar estos tokens en tus requests, agrega el header:")
    print("Authorization: Bearer <token>")
    print("\nEjemplo con curl:")
    print("curl -X POST 'http://localhost:8000/api/v1/transacciones/upload?banco_codigo=BANCOLOMBIA' \\")
    print("  -H 'Authorization: Bearer <token>' \\")
    print("  -F 'archivos=@archivo.xlsx'")
    print("\nEjemplo para verificar el token:")
    print("curl -X GET 'http://localhost:8000/api/v1/test/user-id' \\")
    print("  -H 'Authorization: Bearer <token>'")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
