from app import app, db
from app.models import User, Itinerary, Activity

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Itinerary': Itinerary, 'Activity': Activity}

if __name__ == "__main__":
    app.run(debug=True)
