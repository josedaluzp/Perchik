# CCH Axcess OIP — Token Authentication (OAuth 2.0) — implementación completa

Fuentes: KB 000237208 (overview), 000256426 (registro), 000256421 (implementación).
Aplica a cch-axcess-client. Flujo = **authorization_code** (3-legged) + refresh para desatendido.

## Servidores
- **Authorization Server:** `https://login.cchaxcess.com`
- **Resource Server:** `https://api.cchaxcess.com`

## 0. Registro de la app (UNA vez) — KB 000256426
En CCH Axcess Dashboard (cuenta licenciada para OIP + userID con permiso "view firm settings"):
`Dashboard > Application Links > Firm > Developer Tools > Add Application`. Configurar:
- **Application Name** (lo ve el usuario al dar consentimiento), **Type = Authorization Code**
  (recomendado, más seguro que Implicit), **Description**.
- **Access token lifetime** y **Refresh token lifetime** ← *poner el refresh lo más largo posible
  para el cron.*
- **Scopes recomendados:**
  - `CCHAxcess_data_writeaccess` — leer/escribir datos (necesario para el import). 
  - `offline_access` — **necesario para obtener refresh_token** (clave para desatendido).
  - `openid` — sub claims. · `IDInfo` — ID token (logout). · `CCHAxcess_Profile` — email/nombre.
- **Redirect URLs:** una `https://` real. **localhost BLOQUEADO.** (Para el consentimiento manual
  alcanza con una URL https propia y leer el `code` de la barra.)
- Copiar **client_id** y **client_secret** a un store seguro (→ env vars, ver abajo).

## 1. Consentimiento + authorization code (UNA vez, requiere browser)
`GET https://login.cchaxcess.com/ps/auth/v1.0/core/connect/authorize` con query params:
- `response_type=code`
- `client_id=<client_id>`
- `redirect_uri=<redirect registrado>`
- `scope=<lista separada por espacios>` (ej. `CCHAxcess_data_writeaccess offline_access openid IDInfo`)
- (opcional) `acr_values={"AccountNumber":"123456"}` — el account number de 6 dígitos del firm
  (las llaves `{}` son parte del formato).

El usuario entra account number → usuario/contraseña (o ADFS) → MFA → aprueba la app. CCH
redirige a `redirect_uri?code=<authorization_code>`. El code **expira rápido** → usarlo ya.
(Si el usuario ya autorizó antes y no revocó, no se le vuelve a pedir aprobación.)

## 2. Canjear el code por tokens
`POST https://login.cchaxcess.com/ps/auth/v1.0/core/connect/token`
- Header: `Authorization: Basic base64(client_id + ":" + client_secret)`
- Body (form-urlencoded, NO en el header):
  `code=<authorization_code>&redirect_uri=<redirect>&grant_type=authorization_code`
- Si el code trae `%`, URL-decodificarlo antes.
- **Respuesta 200 (JSON):** `id_token` (JWT, para logout/profile), `access_token` (JWT, para las
  APIs), `expires_in` (seg hasta expirar el access), `refresh_token` (string).

## 3. Llamar a las APIs
Header: `Authorization: Bearer <access_token>` contra `https://api.cchaxcess.com/...`
(p.ej. el `POST /taxservices/oiptax/api/v1/ReturnsImportBatch`).

## 4. Refresh (desatendido — el corazón del cron)
`POST https://login.cchaxcess.com/ps/auth/v1.0/core/connect/token`
- Mismo header `Authorization: Basic base64(client_id:client_secret)`.
- Body: `refresh_token=<refresh_token>&redirect_uri=<redirect>&grant_type=refresh_token`
  (el ejemplo de body de la KB usa `grant_type=refresh_token`).
- Devuelve los mismos campos que el paso 2, **y RESETEA la expiración del access Y del refresh**.
- ⇒ Si el cron refresca antes de que expire el refresh token, **renueva para siempre sin humano**.
  Si el refresh expira (PC apagada demasiado tiempo), repetir pasos 1-2 (re-consentir).
- KB dedicada pendiente de leer: *"How do I use OIP token authentication for an unattended
  process?"* — la más relevante para nuestro caso.

## 5. Logout (opcional)
`GET …/connect/endsession?post_logout_redirect_uri=<url>&id_token_hint=<id_token>`. Invalida los
tokens pero NO revoca la autorización (al re-loguear no vuelve a pedir aprobación).

## Seguridad (regla del proyecto)
`client_id`, `client_secret`, `refresh_token` (y el account number) → **variables de entorno /
store seguro, NUNCA en código ni repo**. Ver `.env.example`. Validar al arrancar que existen.

## Arquitectura (a confirmar al implementar)
El cron corre en Claude Desktop, pero el manejo de tokens + los POST HTTP probablemente vivan en
un **componente local** (script / MCP) que cch-axcess-client invoca: guarda el refresh token,
renueva el access token, arma el XML (ver `tax-transfer-format.md`) y postea a la API.
