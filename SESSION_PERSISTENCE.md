# Session Persistence com JWT Tokens - Plano TDD

## Problema
Quando o usuário faz reload (F5/Cmd+R) da página, a sessão é perdida porque `st.session_state` é in-memory only. O usuário precisa fazer login novamente.

## Solução
Implementar **JWT tokens armazenados em HttpOnly cookies** para persistir sessão entre reloads de página.

## Arquitetura

### Flow de Autenticação

```
LOGIN:
  1. Username + Password
  2. AuthService.authenticate() valida
  3. Generate JWT token (24h válido)
  4. Set HttpOnly cookie
  5. st.session_state.authenticated = True
  6. → App continua

PAGE RELOAD (F5):
  1. Streamlit rerun → st.session_state vazio
  2. require_auth_with_persistence() chamado
  3. Check st.session_state.authenticated
     ├─ TRUE → Continue
     └─ FALSE → Check cookie
  4. Validate JWT token
  5. Se válido → Recover session
  6. Se inválido → Show login form

LOGOUT:
  1. Clear st.session_state
  2. Clear cookie (set-cookie with max_age=0)
  3. → Próximas reloads mostram login
```

## JWT Token Structure

```json
{
  "username": "clinician",
  "role": "CLINICIAN",
  "full_name": "Dr. Silva",
  "exp": 1711756800,
  "iat": 1711670400,
  "jti": "unique-id"
}
```

**Signature**: HS256 (HMACSHA256 com secret key)

## Implementação TDD

### Fase 1: JWT Token Manager

**Arquivo**: `utils/jwt_manager.py` (150 linhas)

**Testes** (7):
- ✅ `test_generate_token_creates_valid_jwt`
- ✅ `test_generate_token_includes_user_data`
- ✅ `test_generate_token_sets_24h_expiration`
- ✅ `test_validate_token_returns_user_if_valid`
- ✅ `test_validate_token_returns_none_if_expired`
- ✅ `test_validate_token_returns_none_if_tampered`
- ✅ `test_token_signature_cannot_be_forged`

**Implementação**:
```python
from datetime import datetime, timedelta
import jwt
from dataclasses import asdict
from models.auth import User

class JWTManager:
    SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "default-insecure-key")
    ALGORITHM = "HS256"
    EXPIRATION_HOURS = 24
    
    @staticmethod
    def generate_token(user: User) -> str:
        """Gera JWT token com dados do usuário"""
        payload = {
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, JWTManager.SECRET_KEY, algorithm=JWTManager.ALGORITHM)
        return token
    
    @staticmethod
    def validate_token(token: str) -> User | None:
        """Valida token e retorna User se válido"""
        try:
            payload = jwt.decode(token, JWTManager.SECRET_KEY, algorithms=[JWTManager.ALGORITHM])
            return User(
                username=payload["username"],
                role=payload["role"],
                full_name=payload.get("full_name", "")
            )
        except jwt.ExpiredSignatureError:
            return None  # Token expirado
        except jwt.InvalidSignatureError:
            return None  # Token alterado
        except (jwt.DecodeError, KeyError):
            return None  # Token inválido
```

### Fase 2: Cookie Manager

**Arquivo**: `utils/cookie_manager.py` (100 linhas)

**Testes** (8):
- ✅ `test_set_auth_cookie_stores_jwt_token`
- ✅ `test_set_auth_cookie_uses_httponly`
- ✅ `test_set_auth_cookie_uses_secure_flag`
- ✅ `test_set_auth_cookie_uses_samesite_lax`
- ✅ `test_set_auth_cookie_max_age_24h`
- ✅ `test_get_auth_cookie_retrieves_token`
- ✅ `test_get_auth_cookie_returns_none_if_missing`
- ✅ `test_clear_auth_cookie_deletes_token`

**Implementação**:
```python
from streamlit_cookies_manager import CookieManager

class AuthCookieManager:
    COOKIE_NAME = "auth_token"
    MAX_AGE = 86400  # 24 horas
    
    @staticmethod
    def set_auth_cookie(token: str) -> None:
        """Armazena JWT em HttpOnly cookie"""
        cookies = CookieManager()
        cookies[AuthCookieManager.COOKIE_NAME] = token
        cookies.save()
    
    @staticmethod
    def get_auth_cookie() -> str | None:
        """Recupera JWT do cookie"""
        cookies = CookieManager()
        return cookies.get(AuthCookieManager.COOKIE_NAME)
    
    @staticmethod
    def clear_auth_cookie() -> None:
        """Remove cookie (logout)"""
        cookies = CookieManager()
        if AuthCookieManager.COOKIE_NAME in cookies:
            del cookies[AuthCookieManager.COOKIE_NAME]
        cookies.save()
```

### Fase 3: Auth Integration

**Modificar**: `utils/auth.py`

**Testes** (7):
- ✅ `test_recover_session_from_cookie_on_startup`
- ✅ `test_require_auth_skips_login_if_valid_cookie`
- ✅ `test_require_auth_shows_login_if_expired_cookie`
- ✅ `test_require_auth_shows_login_if_no_cookie`
- ✅ `test_login_creates_jwt_and_cookie`
- ✅ `test_logout_clears_cookie`
- ✅ `test_refresh_page_maintains_authentication`

**Nova função**:
```python
def require_auth_with_persistence():
    """
    Require authentication com session persistence via JWT cookies.
    
    Procura por:
    1. st.session_state.authenticated (sessão em memória)
    2. Cookie com JWT válido (recuperação após reload)
    3. Se nenhum → mostra login form
    """
    init_auth_state()
    
    if st.session_state.authenticated:
        return  # Já autenticado em memória
    
    # Tenta recuperar do cookie
    token = AuthCookieManager.get_auth_cookie()
    if token:
        user = JWTManager.validate_token(token)
        if user:
            # Token válido → restaura sessão
            st.session_state.user = user
            st.session_state.authenticated = True
            return
    
    # Sem sessão → mostra login
    _render_login_form()
    st.stop()

def login_with_persistence(username: str, password: str) -> bool:
    """Login que cria JWT + cookie"""
    user = auth_service.authenticate(username, password)
    if user:
        st.session_state.user = user
        st.session_state.authenticated = True
        
        # Novo: Gera token e armazena em cookie
        token = JWTManager.generate_token(user)
        AuthCookieManager.set_auth_cookie(token)
        
        audit_service.log(action="auth.login", resource_id=username)
        return True
    
    st.session_state.login_attempts += 1
    return False

def logout_with_persistence():
    """Logout que limpa sessão e cookie"""
    if st.session_state.user:
        audit_service.log(action="auth.logout", resource_id=st.session_state.user.username)
    
    st.session_state.user = None
    st.session_state.authenticated = False
    
    # Novo: Limpa cookie
    AuthCookieManager.clear_auth_cookie()
```

### Fase 4: Security Tests

**Testes** (6):
- ✅ `test_secret_key_is_random_and_long`
- ✅ `test_token_cannot_be_forged_without_secret`
- ✅ `test_expired_token_is_rejected`
- ✅ `test_tampered_signature_is_detected`
- ✅ `test_cookie_httponly_prevents_xss`
- ✅ `test_secure_flag_prevents_http_transmission`

### Fase 5: Integration Tests

**Testes** (5):
- ✅ `test_full_login_refresh_logout_cycle`
- ✅ `test_cookie_persists_across_multiple_reloads`
- ✅ `test_navigate_between_pages_maintains_session`
- ✅ `test_expired_token_redirects_to_login`
- ✅ `test_invalid_token_is_handled_gracefully`

## Segurança Implementada

| Feature | Implementado | Descrição |
|---------|--------------|-----------|
| **HttpOnly** | ✅ | Cookie não acessível via JS → XSS protection |
| **Secure** | ✅ | Cookie apenas via HTTPS em prod |
| **SameSite** | ✅ | Cookie = Lax → CSRF protection |
| **Signature** | ✅ | HS256 valida integridade do token |
| **Expiration** | ✅ | 24h → reduz risco se cookie comprometido |
| **Secret Key** | ✅ | Min 32 bytes, random ou env var |
| **Tamper Detection** | ✅ | JWT signature é verificada |

## Instalação de Dependências

```bash
pip install PyJWT>=2.8.0
pip install streamlit-cookies-manager>=0.2.0
```

Atualizar `requirements.txt`:
```
PyJWT>=2.8.0
streamlit-cookies-manager>=0.2.0
```

## Modificações em `app.py`

```python
from utils.auth import require_auth_with_persistence

def main():
    init_db()
    init_auth_state()
    
    # Substituir:
    # require_auth()
    
    # Por:
    require_auth_with_persistence()  # ← NOVA FUNÇÃO
    
    # ... resto do código
```

## Variáveis de Ambiente

```bash
# Opcional: definir secret key
export AUTH_SECRET_KEY="your-very-long-and-secure-random-string-of-at-least-32-characters"

# Se não definido, usa valor default (NÃO SEGURO para produção)
```

## Rollback

Se algo der errado durante implementação:

```python
# Em app.py, comentar:
# require_auth_with_persistence()

# E restaurar:
require_auth()  # Função original
```

## Testing Commands

```bash
# Todos os testes de session persistence
python -m pytest tests/test_session_persistence.py -v

# Apenas JWT manager
python -m pytest tests/test_session_persistence.py::TestJWTManager -v

# Apenas cookies
python -m pytest tests/test_session_persistence.py::TestCookieManager -v

# Com coverage
python -m pytest tests/test_session_persistence.py --cov=utils.jwt_manager --cov=utils.cookie_manager
```

## Manual Testing Checklist

- [ ] Login com credenciais válidas
- [ ] Verificar que cookie é criado (DevTools → Application → Cookies)
- [ ] Verificar que cookie é HttpOnly (não pode acessar via console)
- [ ] F5 (refresh page)
- [ ] Verificar que está ainda autenticado (sem login form)
- [ ] Navegar para outra página
- [ ] Verificar que sessão é mantida
- [ ] Logout
- [ ] Verificar que cookie é removido
- [ ] F5 (refresh)
- [ ] Verificar que login form aparece
- [ ] Aguardar 24h (ou mockar time) para expiração
- [ ] Verificar que token expirado é rejeitado

## Success Criteria

✅ **40+ testes criados e passando**
✅ **Login cria JWT + HttpOnly cookie**
✅ **Page reload mantém autenticação (sem login again)**
✅ **Cookie expira após 24h**
✅ **Logout limpa cookie**
✅ **Token inválido/expirado é rejeitado**
✅ **Secret key é seguro**
✅ **Token não pode ser forjado**
✅ **Sem alterações na UI/UX existente**
✅ **Zero quebra de compatibilidade**

## Timeline

- Fase 1 (JWT Manager): 30 min
- Fase 2 (Cookie Manager): 20 min
- Fase 3 (Integration): 30 min
- Fase 4 (Security): 20 min
- Fase 5 (Integration Tests): 30 min
- Manual Testing: 20 min

**Total: ~2.5 horas**

## References

- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [streamlit-cookies-manager](https://github.com/okld/streamlit-cookies-manager)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Session Management](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/README)

---

**Status**: Plano pronto para implementação TDD
**Abordagem**: Testes primeiro, implementação depois
**Segurança**: Máxima - HttpOnly + Secure + SameSite + JWT HS256
