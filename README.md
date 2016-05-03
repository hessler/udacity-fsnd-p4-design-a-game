# Paper, Rock, Scissors Game API (Full Stack Nanodegree Project 4)

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
2.  Configure and run the app with [GoogleAppEngineLauncher](https://cloud.google.com/appengine/downloads), and ensure it's running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer, unless it is set up on another port.
 
 

## Game Description:
**Rock, Paper, Scissors** is a simple zero-sum game where each player plays a Rock,
Paper, or Scissors object. For this game, the user plays against the computer (AI).
There are four possible outcomes for each game:

1. Rock beats Scissors _(Rock crushes Scissors)_
2. Scissors beats Paper _(Scissors cuts Paper)_
3. Paper beats Rock _(Paper covers Rock)_
4. Tie _(both players play the same object)_

A user's play is sent to the `make_play` endpoint which will reply with updated
game data, including a message reply about the game outcome. Each game can be
retrieved or played by using the path parameter `urlsafe_game_key`.

## Files Included:
 - `api.py`: Contains endpoints and game playing logic.
 - `app.yaml`: App configuration.
 - `cron.yaml`: Cronjob configuration.
 - `main.py`: Handler for taskqueue handler.
 - `models.py`: Entity and message definitions including helper methods.
 - `utils.py`: Helper function for retrieving ndb.Models by urlsafe Key string.

## Endpoints Included:
 - **create_user**
    - Path: `user`
    - Method: `POST`
    - Parameters: `username`, `display_name`, `email`
    - Returns: `UserForm` representation of the new user.
    - Description: Creates a new `User`. `user_name` provided must be unique.
    Will raise a `ConflictException` if a user with specified `username`
    already exists.

 - **get_user**
    - Path: `get_user`
    - Method: `GET`
    - Parameters: `username`
    - Returns: `UserForm` representation of the user with matching username.
    - Description: Returns data about the specified user. Will raise a
    `NotFoundException` is a user with the specified username is not found.

 - **get_users**
    - Path: `get_users`
    - Method: `GET`
    - Parameters: None
    - Returns: `UserForm` objects for each user.
    - Description: Returns data about each user found in the game datastore.
    
 - **new_game**
    - Path: `game`
    - Method: `POST`
    - Parameters: `username`
    - Returns: `GameForm` with initial game state and data.
    - Description: Creates a new `Game`. `username` provided must correspond to an
    existing user. Will raise a `NotFoundException` if user with specified
    `username` is not found.
     
 - **get_game**
    - Path: `game/{urlsafe_game_key}`
    - Method: `GET`
    - Parameters: `urlsafe_game_key`
    - Returns: `GameForm` with game state and data.
    - Description: Returns the current game state and data. Will raise a
    `NotFoundException` if a game is not found based on the specified parameter.

 - **cancel_game**
    - Path: `game/{urlsafe_game_key}/cancel`
    - Method: `POST`
    - Parameters: `urlsafe_game_key`
    - Returns: `GameForm` with updated game state and data.
    - Description: Returns the current game state and data of newly cancelled
    game. Will raise a `ConflictException` if the game has already been marked
    as cancelled, or if the game is already over. Will raise a `NotFoundException`
    if a game is not found based on the specified parameter.
    
 - **make_play**
    - Path: `game/{urlsafe_game_key}`
    - Method: `PUT`
    - Parameters: `urlsafe_game_key`, `play`
    - Returns: `GameForm` with updated game state and data.
    - Description: Accepts a `play` and returns the updated state of the game.
    Will raise a `NotFoundException` if specified game is not found.
    
 - **get_games**
    - Path: `games`
    - Method: `GET`
    - Parameters: None
    - Returns: `GameForms`.
    - Description: Returns all games in the database as `GameForm` objects,
    ordered by most recent game date.

 - **get_user_games**
    - Path: `user_games`
    - Method: `GET`
    - Parameters: `username`
    - Returns: `GameForms`.
    - Description: Returns all active (unfinished) games as `GameForm` objects
    for the specified user.
    
 - **get_user_rankings**
    - Path: `user_rankings`
    - Method: `GET`
    - Parameters: None
    - Returns: `UserRankingForms`. 
    - Description: Returns all users data as `UserRankingForm` objects, ordered
    by winning percentage.
    
 - **get_game_history**
    - Path: `game/{urlsafe_game_key}/history`
    - Method: `GET`
    - Parameters: None
    - Returns: `GameHistoryForm` of specified game.
    - Description: Returns the history of moves for the specified game.
    Will raise a `NotFoundException` if the specified game is not found.


## Models Included:
 - **User**
    - Stores user information: 
       - `username` _(StringProperty)_
       - `display_name` _(StringProperty)_
       - `email` _(StringProperty)_
       - `total_games` _(IntegerProperty)_
       - `wins` _(IntegerProperty)_
       - `win_percentage` _(FloatProperty)_
    
 - **Game**
    - Stores unique game states and data:
       - `play` _(StringProperty)_
       - `ai_play` _(StringProperty)_
       - `game_over` _(BooleanProperty)_
       - `won` _(BooleanProperty)_
       - `user` _(KeyProperty)_
       - `date` _(DateTimeProperty)_
       - `message` _(StringProperty)_
       - `cancelled` _(BooleanProperty)_
       - `moves` _(StructuredProperty)_
    
 - **Move**
    - Stores information about a game's move:
       - `play` _(StringProperty)_
       - `ai_play` _(StringProperty)_
       - `result` _(StringProperty)_

    
## Forms Included:
 - **GameForm**
    - Representation of a Game's state (`urlsafe_key`, `game_over`, `message`,
    `username`, `ai_play`, `play`, `won`, `date`, `cancelled`, `moves`).
 - **GameForms**
    - Multiple GameForm container.
 - **GameHistoryForm**
    - Representation of a Game's history of moves (`moves`).
 - **NewGameForm**
    - Used to create a new game (`username`)
 - **MakePlayForm**
    - Inbound make play form (`play`).
 - **UserForm**
    - Representation of a User (`username`, `display_name`, `email`).
 - **UserForms**
    - Multiple UserForm container.
 - **UserRankingForm**
    - Representation of a User with ranking information (`username`,
    `display_name`, `total_games`, `wins`, `win_percentage`)
 - **UserRankingForms**
    - Multiple UserRankingForm container.
 - **StringMessage**
    - General purpose String container.
