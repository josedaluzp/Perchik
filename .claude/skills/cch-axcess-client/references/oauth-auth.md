# CCH Axcess OIP — Token Authentication (OAuth 2.0)

Fuente: KB 000237208 (Wolters Kluwer, 08/2023). Aplica a cch-axcess-client.

## Servidores
- **Authorization Server:** `login.cchaxcess.com` (maneja tokens OAuth2).
- **Resource Server:** `api.cchaxcess.com` (responde las APIs — Tax Services, etc.).

## Flujo: authorization_code (3-legged) + refresh para desatendido
NO es `client_credentials`. Requiere consentimiento humano **una sola vez**, y luego renovación
silenciosa vía refresh token:

```
1. (UNA vez) Registrar la app OIP  → client_id + client_secret.
   "Should be completed by the company that licenses an integration kit." Registro = una sola vez.
2. (UNA vez) Consentimiento del usuario: el authz server pide account number → usuario/contraseña
   (o Federated/ADFS) → MFA → el usuario concede acceso a la app.
   → la app recibe access_token + REFRESH_TOKEN.
3. (cada corrida) usar el refresh_token para obtener un nuevo access_token y llamar a las APIs.
   La KB confirma: "applications may securely store tokens and renew them for scheduled or
   unattended processing." → calza con el cron en la PC dedicada (consentir 1 vez, renovar solo).
```

El access token va en `Authorization: Bearer <token>` contra `api.cchaxcess.com`. Identifica
qué usuario/licencia usa la API y que la app fue autorizada por ese usuario.

## Revocación
El usuario puede quitar el acceso a la app desde CCH Axcess → invalida los tokens y la app deja de
renovar hasta un nuevo consentimiento. (Tener esto en cuenta: si alguien revoca, el cron falla y
hay que re-consentir en la PC.)

## Implicación de seguridad (regla del proyecto)
`client_id`, `client_secret` y `refresh_token` → **variables de entorno / store seguro, NUNCA en
el código ni en el repo**. Documentar nombres en un `.env.example`.

## Implicación de arquitectura
El cron corre en Claude Desktop, pero las llamadas HTTP OAuth + import probablemente requieran un
**componente local** (script / pequeño MCP) que cch-axcess-client invoque: ese componente
mantiene el refresh token, renueva el access token y hace los POST a la API. A confirmar al
implementar.

## Pendiente (las 2 sub-KB que faltan leer)
1. **"How do I register my OIP application … to get an Oauth2 client ID and client secret?"**
   → el registro (paso 1). De dónde salen client_id/secret, redirect URI, etc.
2. **"How do I implement Oauth2 token authentication in my OIP application?"**
   → los endpoints concretos: authorize URL, token URL, cómo se pide el refresh, scopes, sandbox.
3. (info) "What CCH Axcess login options are compatible with Token Authentication for OIP?"
