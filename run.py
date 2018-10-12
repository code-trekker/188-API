from wmapp import app
import os

if __name__ == '__main__':
    # app.run(host='localhost', port=8000, debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)