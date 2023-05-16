from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

class Sighting:

    def __init__(self, data) -> None:
        self.id = data['id']
        self.location = data['location']
        self.what_happened = data['what_happened']
        self.date_of_siting = data['date_of_siting']
        self.num_of_sasquatches = data['num_of_sasquatches']
        self.created_at = data['created_at']
        self.updated_at = data['update_at']
        self.user_id = data['user_id']
        self.creator = None
        self.skeptics = []


    @classmethod
    def get_one(cls, data):
        query = 'SELECT * from sightings WHERE id = %(id)s'

        results = connectToMySQL('sasquatch').query_db(query, data)
        r = cls(results[0])
        owner = user.User.get_one({'id':r.user_id})
        r.creator = owner
        return r
    
    @classmethod
    def get_all(cls):
        query = 'SELECT * FROM sightings;'

        results = connectToMySQL('sasquatch').query_db(query)

        sightings = [cls(sighting) for sighting in results]

        return sightings
    
    @classmethod
    def add_sighting(cls, data):
        query = '''INSERT INTO sightings(location, what_happened, date_of_siting, num_of_sasquatches, created_at, update_at, user_id) 
        VALUES(%(location)s, %(what_happened)s, %(date_of_siting)s, %(num_of_sasquatches)s, NOW(), NOW(), %(user_id)s);'''
        
        result = connectToMySQL('sasquatch').query_db(query, data)
        print(result)
        return result


    @classmethod
    def edit(cls, data):
        query = '''UPDATE sightings SET location=%(location)s, what_happened=%(what_happened)s, date_of_siting=%(date_of_siting)s, num_of_sasquatches=%(num_of_sasquatches)s, update_at=NOW() WHERE id=%(id)s;'''

        return connectToMySQL('sasquatch').query_db(query, data)
    
    @classmethod
    def delete(cls, data):
        query = 'DELETE FROM sightings WHERE id=%(id)s;'

        return connectToMySQL('sasquatch').query_db(query, data)
    
    @classmethod
    def get_all_sightings_with_creator(cls):
        # Get all sightings, and their one associated User that created it
        query = "SELECT * FROM sightings JOIN users ON sightings.user_id = users.id;"
        results = connectToMySQL('sasquatch').query_db(query)
        all_sightings = []
        for row in results:
            # Create a sighting class instance from the information from each db row
            one_row = cls(row)
            # Prepare to make a User class instance, looking at the class in models/user.py
            one_sighting_creator_info = {
                # Any fields that are used in BOTH tables will have their name changed, which depends on the order you put them in the JOIN query, use a print statement in your classmethod to show this.
                "id": row['users.id'], 
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "created_at": row['users.created_at'],
                "updated_at": row['updated_at']
            }
            # Create the User class instance that's in the user.py model file
            owner = user.User(one_sighting_creator_info)
            # Associate the sighting class instance with the User class instance by filling in the empty sighting_creator attribute in the sighting class
            one_row.creator = owner
            # Append the sighting containing the associated User to your list of sightings
            all_sightings.append(one_row)
            
        return all_sightings
    
    @classmethod
    def add_skeptic(cls, data):
        sql = 'INSERT INTO skeptics(user_id, sighting_id) VALUES(%(user_id)s, %(sighting_id)s);'

        results = connectToMySQL('sasquatch').query_db(sql, data)

        return results
    
    @classmethod
    def delete_skeptic(cls, data):
        sql = 'DELETE FROM skeptics WHERE user_id=%(user_id)s and sighting_id=%(sighting_id)s;'

        return connectToMySQL('sasquatch').query_db(sql, data)

    @classmethod
    def get_users_with_sightings(cls, data):
        sql = '''SELECT * FROM sightings LEFT JOIN skeptics ON 
        skeptics.sighting_id = sightings.id LEFT JOIN users ON 
        skeptics.user_id = users.id WHERE sightings.id = %(id)s;'''

        results = connectToMySQL('sasquatch').query_db(sql, data)
        sight = cls(results[0])
        owner = user.User.get_one({'id':sight.user_id})
        sight.creator = owner
        for row in results:
            user_data = {
                "id": row['users.id'], 
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "created_at": row['users.created_at'],
                "updated_at": row['updated_at']
            }
            sight.skeptics.append( user.User(user_data))
        
        return sight

    @staticmethod
    def validate_sighting(sighting):
        print(sighting)
        is_valid = True
        if len(sighting['location']) < 1:
            flash('entire form must be filled out', 'creation_error')
            is_valid = False
        if len(sighting['what_happened']) < 1:
            flash('entire form must be filled out', 'creation_error')
            is_valid = False
        if not sighting['date_of_siting']:
            flash('date of sighting must be entered', 'creation_error')
            is_valid = False
        if int(sighting['num_of_sasquatches']) < 1:
            flash('Minimum of 1 sasquatch is required to be a sighting', 'creation_error')
            is_valid = False

        return is_valid