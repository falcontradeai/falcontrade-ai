# FalconTrade API

## Frontend logout instructions

Send a `POST` request to `/auth/logout` with the current access token in the `Authorization` header:

```javascript
fetch("/auth/logout", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`
  }
});
```

After a successful request, remove the stored token from the browser (e.g. localStorage, sessionStorage or cookies):

```javascript
localStorage.removeItem("token");
```

Once logged out, the token is revoked on the server and can no longer be used for authenticated requests.

