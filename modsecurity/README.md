# Generate self-signed certs
```
mkcert example.com "*.example.com" example.test localhost 127.0.0.1 ::1
mv example.com+5.pem cert.pem
mv example.com+5-key.pem key.pem
```

