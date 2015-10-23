from config import SERVER_PORT, DEBUG
from handlers.app import create_app


if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', SERVER_PORT, debug=DEBUG)
