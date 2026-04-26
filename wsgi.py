from app import app

# if __name__ == "__main__":
#     reports_dir = "reports"
#     if not os.path.exists(reports_dir):
#         os.makedirs(reports_dir)
#     app.run(host="0.0.0.0", port=443, ssl_context=("certs/cert.pem", "certs/key.pem"))

if __name__ == "__main__":
    app.run()
    