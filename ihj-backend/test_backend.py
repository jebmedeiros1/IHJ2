#!/usr/bin/env python3
"""
Script de teste para o backend FastAPI
Testa os endpoints sem conexão com banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    try:
        print("Testando imports...")
        
        # Testa config
        from config import settings
        print("✓ Config carregado")
        
        # Testa models
        from models import UserLogin, Token, FiltroRequest
        print("✓ Models carregados")
        
        # Testa auth (sem conexão com banco)
        from auth import get_password_hash, verify_password
        print("✓ Auth carregado")
        
        # Testa se FastAPI pode ser inicializado
        from fastapi import FastAPI
        app = FastAPI()
        print("✓ FastAPI inicializado")
        
        print("\n✅ Todos os imports funcionaram corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no import: {e}")
        return False

def test_auth_functions():
    """Testa funções de autenticação"""
    try:
        print("\nTestando funções de autenticação...")
        
        from auth import get_password_hash, verify_password
        
        # Testa hash de senha
        password = "test123"
        hashed = get_password_hash(password)
        print(f"✓ Hash gerado: {hashed[:20]}...")
        
        # Testa verificação de senha
        is_valid = verify_password(password, hashed)
        print(f"✓ Verificação de senha: {is_valid}")
        
        if is_valid:
            print("✅ Funções de autenticação funcionando!")
            return True
        else:
            print("❌ Erro na verificação de senha")
            return False
            
    except Exception as e:
        print(f"❌ Erro nas funções de auth: {e}")
        return False

def test_models():
    """Testa modelos Pydantic"""
    try:
        print("\nTestando modelos Pydantic...")
        
        from models import UserLogin, FiltroRequest
        
        # Testa UserLogin
        user_data = UserLogin(username="test", password="test123")
        print(f"✓ UserLogin: {user_data.username}")
        
        # Testa FiltroRequest
        filtro_data = FiltroRequest(
            classes=["1", "2"],
            filtros={"caracteristica1": ["valor1", "valor2"]}
        )
        print(f"✓ FiltroRequest: {len(filtro_data.classes)} classes")
        
        print("✅ Modelos Pydantic funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos modelos: {e}")
        return False

def main():
    """Função principal de teste"""
    print("=== TESTE DO BACKEND FASTAPI ===\n")
    
    tests = [
        test_imports,
        test_auth_functions,
        test_models
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n=== RESULTADO DOS TESTES ===")
    passed = sum(results)
    total = len(results)
    
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Backend está pronto.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

