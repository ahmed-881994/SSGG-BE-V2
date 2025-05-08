import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.schema.auth.auth import TokenResponse
from app.service.auth import users
from app.util.auth import compute_s256_challenge, create_access_token, generate_code

auth_codes = {}
clients = {
    "client1": {
        "client_secret": "secret1",
        "redirect_uris": ["http://localhost:8000/docs/oauth2-redirect"],
    }
}

router = APIRouter(prefix="/oauth", tags=["Auth"])


@router.get("/authorize")
async def authorize(request: Request,
                    response_type: str,
                    client_id: str,
                    redirect_uri: str,
                    code_challenge: str,
                    code_challenge_method: str = "S256",
                    state: str = None):
    # Validate client and redirect URI
    client = clients.get(client_id)
    if not client or redirect_uri not in client["redirect_uris"]:
        raise HTTPException(
            status_code=400, detail="Invalid client or redirect URI")

    # If not logged in, show login form
    if "user" not in request.session:
        html = f"""
        <html><body>
          <form action="/authorize" method="post">
            <input type="hidden" name="response_type" value="{response_type}" />
            <input type="hidden" name="client_id" value="{client_id}" />
            <input type="hidden" name="redirect_uri" value="{redirect_uri}" />
            <input type="hidden" name="code_challenge" value="{code_challenge}" />
            <input type="hidden" name="code_challenge_method" value="{code_challenge_method}" />
            <input type="hidden" name="state" value="{state}" />
            Username: <input name="username" /><br />
            Password: <input name="password" type="password" /><br />
            <button type="submit">Login</button>
          </form>
        </body></html>"""
        return HTMLResponse(html)

    # Already logged in: generate code and redirect
    username = request.session["user"]
    code = generate_code()
    expires = datetime.now(
        timezone.utc) + timedelta(seconds=float(os.environ.get("CODE_EXPIRE_SECONDS", "0,0")))
    auth_codes[code] = {
        "username": username,
        "challenge": code_challenge,
        "method": code_challenge_method,
        "redirect_uri": redirect_uri,
        "expires": expires,
        "state": state,
    }
    uri = f"{redirect_uri}?code={code}"
    if state:
        uri += f"&state={state}"
    return RedirectResponse(uri)


@router.post("/authorize")
async def authorize_login(request: Request,
                          response_type: str = Form(...),
                          client_id: str = Form(...),
                          redirect_uri: str = Form(...),
                          code_challenge: str = Form(...),
                          code_challenge_method: str = Form(...),
                          state: str = Form(None),
                          username: str = Form(...),
                          password: str = Form(...)):
    # Validate user
    if users.get_user(username) is None or users.get_user(username).get("password") != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["user"] = username
    # Redirect to GET /authorize to continue
    params = f"response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&code_challenge={code_challenge}&code_challenge_method={code_challenge_method}"
    if state:
        params += f"&state={state}"
    return RedirectResponse(f"/authorize?{params}")


@router.post("/token", response_model=TokenResponse)
async def token(grant_type: str = Form(...),
                code: str = Form(None),
                redirect_uri: str = Form(None),
                client_id: str = Form(...),
                client_secret: str = Form(...),
                code_verifier: str = Form(None)):
    # Only support authorization_code grant
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="Unsupported grant_type")
    # Validate client
    client = clients.get(client_id)
    if not client or client["client_secret"] != client_secret:
        raise HTTPException(
            status_code=401, detail="Invalid client credentials")
    # Validate code
    data = auth_codes.get(code)
    if not data or data["expires"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    if data["redirect_uri"] != redirect_uri:
        raise HTTPException(status_code=400, detail="Redirect URI mismatch")
    # Verify PKCE
    if data["method"] == "S256":
        expected = data["challenge"]
        actual = compute_s256_challenge(code_verifier)
        if actual != expected:
            raise HTTPException(
                status_code=400, detail="PKCE verification failed")
    # All good; create token
    access_token = create_access_token(data["username"])
    # cleanup
    del auth_codes[code]
    return {"access_token": access_token, "token_type": "bearer", "expires_in": float(os.environ.get("ACCESS_TOKEN_EXPIRE_SECONDS","0,0"))}
