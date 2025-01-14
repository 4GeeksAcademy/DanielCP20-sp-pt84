from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean(), nullable=False)

    favorites = db.relationship('FavoriteItem', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User %r>' % self.user_name

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "user_name": self.user_name
        }
    
class Planet(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True)
    diameter = db.Column(db.Integer)
    climate = db.Column(db.String(25))
    population = db.Column(db.Integer)
    terrain = db.Column(db.String(25))
    url = db.Column(db.String(255))

    habitant = db.relationship('People', back_populates='planet')
    favorite_item = db.relationship('FavoriteItem', back_populates='planet', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<El planeta con ID {self.id} es {self.name}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'diameter': self.diameter,
            'climate': self.climate,
            'population': self.population,
            'terrain': self.terrain,
            'url': self.url
        }
    
class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True)
    gender = db.Column(db.Enum('male', 'female', name='gender_enum'))
    height = db.Column(db.Integer)
    mass = db.Column(db.Integer)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    url = db.Column(db.String(255))

    planet = db.relationship(Planet, back_populates='habitant')
    favorite_item = db.relationship('FavoriteItem', back_populates='people', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Personaje con ID {self.id} se llama {self.name}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'height': self.height,
            'mass': self.mass,
            'url': self.url
        }
    
class FavoriteItem(db.Model):
    __tablename__ = 'favorite_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User, back_populates='favorites')

    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    planet = db.relationship(Planet, back_populates='favorite_item')

    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    people = db.relationship(People, back_populates='favorite_item')

    def __repr__(self):
        return f"<Favorito del usuario {self.user_id}: planet_id={self.planet_id} people_id={self.people_id}>"
    
    def serialize(self):
        return {
            'user_id': self.user_id,
            'planet_id': self.planet_id,
            'people_id': self.people_id
        }