from website import create_app
from replit import web

app, api = create_app()

if __name__ == '__main__':
    web.run(app)