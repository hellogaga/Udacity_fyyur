#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.exc import SQLAlchemyError
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
#----------------------------------------------------------------------------#
# Models.
db = SQLAlchemy(app)
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(500), default='')
    # in oder to make relationship work, lazy must be 'dynamic'
    shows = db.relationship('Show', backref='Venue', lazy='dynamic') 

    def __repr__(self):
      return f'<Venue {self.id} name: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default=' ')
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy='dynamic')
    
    def __repr__(self):
      return f'<Artist {self.id} name: {self.name}>'

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
      return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # read data from database
  now_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  venues = Venue.query.all()
  
  # adding city and state to 'data', avoing replicates
  data = []
  venue_loc = set()
  for venue in venues:
    venue_loc.add((venue.city, venue.state))
  for loc in venue_loc:
    data.append({
        "city": loc[0],
        "state": loc[1],
        "venues": []
    })

  #loop through venues
  for venue in venues:
    # check upcoming shows, comparing the nowtime and show time.
    print(venue)
    upcoming_shows = venue.shows.filter(Show.time > now_time).all()
    # Iterate through the location info in data and append accordingly.
    for single_loc in data:
      if venue.state == single_loc['state'] and venue.city == single_loc['city']:
        single_loc['venues'].append({
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search = request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike(f'%{search}%'))

  response = {
    "count": result.count(),
    "data": result
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = []
  A_venue = Venue.query.get(venue_id)
  venue_shows = A_venue.shows.all()
  
  past_shows = []
  upcoming_shows = []
  now_time = datetime.now()

  for show in venue_shows:
    data = {
          "artist_id": show.artist_id,
          "artist_name": show.Artist.name,
           "artist_image_link": show.Artist.image_link,
           "start_time": format_datetime(str(show.time))
        }
    if show.time > now_time:
      upcoming_shows.append(data)
    else:
      past_shows.append(data)

  data={
    "id": A_venue.id,
    "name": A_venue.name,
    "genres": A_venue.genres,
    "address": A_venue.address,
    "city": A_venue.city,
    "state": A_venue.state,
    "phone": A_venue.phone,
    "website": A_venue.website,
    "facebook_link": A_venue.facebook_link,
    "seeking_talent": A_venue.seeking_talent,
    "seeking_description":A_venue.description,
    "image_link": A_venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  try:
    form = VenueForm()
    # print(form.seeking_talent.data)
    new_venue = Venue(
      name=request.form['name'],
      genres=request.form.getlist('genres'),
      address=request.form['address'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      facebook_link=request.form['facebook_link'],
      image_link= request.form['image_link'],
      website = request.form['website'],
      seeking_talent = form.seeking_talent.data, 
      description = request.form['seeking_description']
    )
    # insert new venue records into the db
    db.session.add(new_venue)
    db.session.commit()
    # if successful flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except SQLAlchemyError as e:
    print (e)
    # roll back is error
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    # get the venue info
    To_delvenue = Venue.query.get(venue_id)
  
    # delete related shows
    venue_shows = To_delvenue.shows.all()
    print (venue_shows)
    for show in venue_shows:
      print (show)
      db.session.delete(show)
    
    # Delete the venue 
    db.session.delete(To_delvenue)
    
    # Commit the changes
    db.session.commit()
    flash('Venue ' + To_delvenue.name + ' is deleted.')

  except SQLAlchemyError as e:
    print (e)
    db.session.rollback()
    flash('An error occurred. Venue ' + To_delvenue.name + ' could not be deleted.')
  finally:
    db.session.close()
  
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()

  for A_artist in artists:
    data.append({
      "id" : A_artist.id,
      "name" : A_artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search = request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.ilike(f'%{search}%'))

  response = {
    "count": result.count(),
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  data = []
  A_artist = Artist.query.get(artist_id)
  Artist_shows = A_artist.shows.all()
  
  past_shows = []
  upcoming_shows = []
  now_time = datetime.now()

  for show in Artist_shows:
    data = {
           "venue_id": show.venue_id,
           "venue_name": show.Venue.name,
           "venue_image_link": show.Venue.image_link,
           "start_time": format_datetime(str(show.time))
        }
    if show.time > now_time:
      upcoming_shows.append(data)
    else:
      past_shows.append(data)

  data={
    "id": A_artist.id,
    "name": A_artist.name,
    "genres": A_artist.genres,
    "city": A_artist.city,
    "state": A_artist.state,
    "phone": A_artist.phone,
    "facebook_link": A_artist.facebook_link,
    "seeking_venue": A_artist.seeking_venue,
    "image_link": A_artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  print (A_artist.genres)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  A_artist = Artist.query.get(artist_id)
  print (A_artist.seeking_venue)
  print (A_artist.genres)
  
  # the seeking_venue and genres seems cannot pass data to the front end
  # use the following method instead.
  form.seeking_venue.data = A_artist.seeking_venue
  form.genres.data = A_artist.genres

  return render_template('forms/edit_artist.html', form=form, artist=A_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm()
    A_artist = Artist.query.get(artist_id)
    
    A_artist.name=request.form['name']
    A_artist.genres=request.form.getlist('genres')
    A_artist.city=request.form['city']
    A_artist.state= request.form['state']
    A_artist.phone=request.form['phone']
    A_artist.image_link=request.form['image_link']
    A_artist.facebook_link=request.form['facebook_link']
    A_artist.website = request.form['website']
    A_artist.seeking_venue = form.seeking_venue.data
    A_artist.seeking_description = request.form['seeking_description']
  
    db.session.commit()
    # on successful db edit, flash success
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  except SQLAlchemyError as e:
    print (e)
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  
  finally:
    db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  A_venue = Venue.query.get(venue_id)
  print (A_venue.seeking_talent)
  print (A_venue.genres)
  
  # the seeking_venue and genres seems cannot pass data to the front end
  # use the following method instead.
  form.seeking_talent.data = A_venue.seeking_talent
  form.genres.data = A_venue.genres

  return render_template('forms/edit_venue.html', form=form, venue=A_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm()
    A_venue = Venue.query.get(venue_id)
    
    A_venue.name=request.form['name']
    A_venue.city=request.form['city']
    A_venue.state= request.form['state']
    A_venue.address=request.form['address']
    A_venue.phone=request.form['phone']
    A_venue.genres=request.form.getlist('genres')
    A_venue.image_link=request.form['image_link']
    A_venue.facebook_link=request.form['facebook_link']
    A_venue.website = request.form['website']
    A_venue.seeking_talent = form.seeking_talent.data
    A_venue.description = request.form['seeking_description']
  
    db.session.commit()
    # on successful db edit, flash success
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  except SQLAlchemyError as e:
    print (e)
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
  
  finally:
    db.session.close()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    form = ArtistForm()
    new_artist = Artist(
      name=request.form['name'],
      genres=request.form.getlist('genres'),
      city=request.form['city'],
      state= request.form['state'],
      phone=request.form['phone'],
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      website = request.form['website'],
      seeking_venue = form.seeking_venue.data,
      seeking_description = request.form['seeking_description']
      )

    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except SQLAlchemyError as e:
    print (e)
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    # get the venue info
    To_delartist = Artist.query.get(artist_id)
  
    # delete related shows
    Artist_shows = To_delartist.shows.all()
    print(Artist_shows)
    for show in Artist_shows:
      print (show)
      db.session.delete(show)
    
    # Delete the venue 
    db.session.delete(To_delartist)
    
    # Commit the changes
    db.session.commit()
    flash('Artist ' + To_delartist.name + ' is deleted.')

  except SQLAlchemyError as e:
    print (e)
    db.session.rollback()
    flash('An error occurred. Venue ' + To_delartist.name + ' could not be deleted.')
  finally:
    db.session.close()
  
  return redirect(url_for('artists'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.order_by(db.desc(Show.time))

  for A_show in shows:
    data.append({
      "venue_id": A_show.venue_id,
      "venue_name": A_show.Venue.name,
      "artist_id": A_show.artist_id,
      "artist_name": A_show.Artist.name,
      "artist_image_link": A_show.Artist.image_link,
      "start_time": format_datetime(str(A_show.time))
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    new_show = Show(
      artist_id = request.form['artist_id'],
      venue_id = request.form['venue_id'],
      time = request.form['start_time']
    )

    print (request.form['start_time'])

    # commit to database
    db.session.add(new_show)
    db.session.commit()

    # show message
    flash('Show was successfully listed!')
  except SQLAlchemyError as e:
    print (e)
    db.session.rollback()
    flash('An error occurred. Show could not be added.')
  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
