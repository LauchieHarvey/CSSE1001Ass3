# Assignment 3. Pokemon, Got 2 Find Them All!
import random
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import csv
import os.path
from PIL import ImageTk, Image


# CONSTANTS
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
DIRECTIONS = (UP, DOWN, LEFT, RIGHT,
              f"{UP}-{LEFT}", f"{UP}-{RIGHT}",
              f"{DOWN}-{LEFT}", f"{DOWN}-{RIGHT}")
WALL_VERTICAL = "|"
WALL_HORIZONTAL = "-"
POKEMON = "☺"
FLAG = "♥"
UNEXPOSED = "~"
EXPOSED = "0"


TASK_ONE = "task_one"
TASK_TWO = "task_two"


IMAGES = {
	'0' : "images/zero_adjacent.gif",
	'1' : "images/one_adjacent.gif",
	'2' : "images/two_adjacent.gif",
	'3' : "images/three_adjacent.gif",
	'4' : "images/four_adjacent.gif",
	'5' : "images/five_adjacent.gif",
	'6' : "images/six_adjacent.gif",
	'7' : "images/seven_adjacent.gif",
	'8' : "images/eight_adjacent.gif",
	UNEXPOSED : "images/unrevealed.gif",
	FLAG : "images/pokeball.gif",
}

POKEMON_IMAGES = {
	0 : "images/pokemon_sprites/charizard.gif", 
	1 :	"images/pokemon_sprites/cyndaquil.gif",
	2 : "images/pokemon_sprites/pikachu.gif",
	3 :	"images/pokemon_sprites/psyduck.gif",
	4 :	"images/pokemon_sprites/togepi.gif",
	5 :	"images/pokemon_sprites/umbreon.gif"
}

# ^^^^ CONSTANTS ^^^^






class PokemonGame:
	""" 
		Controller class for the pokemon game.
		instantiated like: PokemonGame(master, grid size=10, num pokemon=15, task=TASK_ONE)
	"""

	def __init__(self, master, grid_size = 6, number_of_pokemons = 7, task = TASK_TWO, board_width = 400):
		""" Constructor method for the PokemonGame class"""
		self._master = master
		self._task = task
		self._game_board = BoardModel(grid_size, number_of_pokemons)


		if task == TASK_TWO:
			# Instantiate the Status Bar.
			self._status_bar = StatusBar(master, number_of_pokemons, self.create_new_game, self.restart_game)
			self._status_bar.pack(fill = 'x', side = tk.BOTTOM)
			# Instantiate the canvas && position it in the master window.
			self._canvas = ImageBoardView(self._master, grid_size, board_width)
			# Instantiate the file menu
			self._file_menu = FileMenu(self._master, self)

		else:
			# Instantiate the canvas && position it in the master window.
			self._canvas = BoardView(self._master, grid_size, board_width)
		
		self._canvas.pack(anchor = tk.CENTER,)

		# Resize root window to fit all widgets.
		master.geometry("")

		self.set_canvas_binds()



	def set_canvas_binds(self):
		""" Set event bindings for the canvas."""
		self._canvas.bind("<Button-1>", self.left_click)
		self._canvas.bind("<Button-2>", self.right_click)
		self._canvas.bind("<Button-3>", self.right_click)


	def handle_game_win(self):
		"""Does everything required when the game has been won"""
		if self._task == TASK_TWO:
			# Stop the timer from updating
			self._status_bar.set_time_running(False)
			# Display the end game messagebox
			self.end_game_message(True)



	def verify_quit():
		"""Prompts the user to verify that they want to quit, if so, quits"""
		answer = tk.messagebox.askquestion(title = "Quit? ;(", message = "Are you sure you want to quit?")
		if answer == "yes":
			exit()


	def left_click(self, event):
		""" Event handler for a left click on the canvas

				Parameters:
					event (obj): Instance containing information about the 
					tkinter event, importantly the event.x and event.y variables
					which are the coordinates of the mouse.
		"""
		# Convert mouse pixel position to rectangle position
		rect_clicked_position = self._canvas.pixel_to_position(event.x, event.y)
		# Convert the rectangle to the corresponding index in the game board.
		clicked_index = self._game_board.position_to_index(rect_clicked_position)
		
		game_string = self._game_board.get_game()
		pokemon_locations = self._game_board.get_pokemon_locations()

		if game_string[clicked_index] not in [FLAG, range(9)]:
			if clicked_index not in pokemon_locations:
				self._game_board.reveal_cells(clicked_index)
			elif clicked_index in pokemon_locations:
				#User clicked on a pokemon, reveal all pokemon locations.
				for pokemon_index in pokemon_locations:
					self._game_board.replace_character_at_index(pokemon_index, POKEMON)

				# Update the GUI before the end game message
				self._canvas.draw_board(self._game_board.get_game())

				if self._task == TASK_TWO:
					self._status_bar.set_time_running(False)
					self.end_game_message(False)

		self._canvas.draw_board(self._game_board.get_game())

		if self._game_board.check_win():
			self.handle_game_win()



	def right_click(self, event):
		""" Event handler for a right click on the canvas

				Parameters:
					event (obj): Instance containing information about the 
					tkinter event, importantly the event.x and event.y variables
					which are the coordinates of the mouse.
		"""
		# Convert mouse pixel position to rectangle position
		rect_clicked_position = self._canvas.pixel_to_position(event.x, event.y)
		# Convert the rectangle to the corresponding index in the game board.
		clicked_index = self._game_board.position_to_index(rect_clicked_position)

		self._game_board.flag_cell(clicked_index)

		# Update the attempted catches status bar variable
		if self._task == TASK_TWO:
			self._status_bar.set_pokeball_labels(self._game_board.get_attempted_catches(),
				self._game_board.get_number_of_pokemons())

		self._canvas.draw_board(self._game_board.get_game())

		if self._game_board.check_win():
			self.handle_game_win()

		



	def end_game_message(self, has_won):
		""" Shows the user the messagebox displaying either a win or a loss

				Parameters:
					won (bool): Whether the user won or lost (True if the user did win)
		"""
		end_game_string = "Congratulations, you won!!" if has_won else "You lose!"
		ask_play_again = "Would you like to play again?"
		play_again = tk.messagebox.askquestion(title="Game Over!", 
			message = f"{end_game_string} {ask_play_again}")

		if play_again == "yes":
			self.create_new_game()
		else:
			exit(0)



	def create_new_game(self):
		"""Event handler for "New Game" button click"""
		grid_size = self._game_board.get_grid_size()
		number_of_pokemons = self._game_board.get_number_of_pokemons()
		# Reset the state of the game
		self._game_board = BoardModel(grid_size, number_of_pokemons)
		self._canvas.draw_board(self._game_board.get_game())

		# Reset status bar variables
		self._status_bar.reset_time()
		if not self._status_bar.get_time_running():
			self._status_bar.set_time_running(True)
		self._status_bar.set_pokeball_labels(self._game_board.get_attempted_catches(),
			self._game_board.get_number_of_pokemons())


	def restart_game(self):
		"""Event handler for "Restart Game" button click"""
		# Cache the current pokemon locations
		pokemon_locations = self._game_board.get_pokemon_locations()
		# Reset the game state
		self.create_new_game()
		# Set the pokemon locations back to the cached state.
		self._game_board.set_pokemon_locations(pokemon_locations)


	def save_game(self):
		""" Saves the current instance of the PokemonGame class as a .csv file
		
		.csv file is saved in the order below:
			game_board_string, grid_size, number_of_pokemons, pokemon_locations 
		for example, a .csv might look like:
			101♥~~101,3,3,"(3,4,5)"
		"""
		# Get key values from BoardModel class as a list
		game_variables = [self._game_board.get_game(), self._game_board.get_grid_size(),
		self._game_board.get_number_of_pokemons(), self._game_board.get_attempted_catches(),
		self._game_board.get_pokemon_locations()]

		# While loop used to determine the name of the file :)
		i = 0
		while os.path.isfile(f"saved_game{i}.csv"):
			i += 1
		else:
			file_name = f"saved_game{i}.csv"

		
		# Open a .csv with an appropriate name in write mode
		with open(file_name, mode='w') as file:
			writer = csv.writer(file, delimiter = ',')
			# Write the key values to the .csv file.
			writer.writerow(game_variables)


	def load_game(self):
		"""Loads a .csv file into the game. The file is assumed to be in the format give above"""

		# Get the user to pick which file to load
		file_name = tk.filedialog.askopenfilename(title = "Select a File",
		 		filetypes = (("CSV files", "*.csv"),))

		# If they picked a file type other than .csv then show error message and skip
		if file_name is None:
			tk.messagebox.showerror(title="Ooopsie ;(", message = "Please select a .csv file!!!")
			return None

		# Get values from the file
		with open(file_name, mode = 'r') as file:
			reader = csv.reader(file, delimiter = ',')
			try:
				variables = [row for row in reader][0]
				game_string = variables[0]
				grid_size = int(variables[1])
				num_of_pokemon = int(variables[2])
				attempted_catches = int(variables[3])
				pokemon_locations = variables[4][1:-1].split(',')
				pokemon_locations = [int(i) for i in pokemon_locations]
			except:
				tk.messagebox.showerror(title="Ooopsie ;(", message = "There appears to be something \
					wrong with the file!!!")
				return None

		# Update the game to reflect the loaded file
		self._game_board = BoardModel(grid_size, num_of_pokemon)
		self._game_board.set_game_string(game_string)
		self._game_board.set_pokemon_locations(pokemon_locations)
		self._game_board.set_attempted_catches(attempted_catches)
		self._status_bar.set_pokeball_labels(attempted_catches, num_of_pokemon)
		self._canvas.set_grid_size(grid_size)
		self._canvas.draw_board(self._game_board.get_game())
		self._status_bar.reset_time()
		if not self._status_bar.get_time_running():
			self._status_bar.set_time_running(True)




class BoardModel:
	""" Model class that represents the board/game state as an object"""

	def __init__(self, grid_size = 6, number_of_pokemons = 5):
		"""Constructor method for the BooardModel class
			
				Parameters:
					grid_size (int): The width of the game board.
					number_of_pokemons (int): How many pokemon are hidden 
					in the long and eerie grass.
		"""
		self._grid_size = grid_size
		self._number_of_pokemons = number_of_pokemons
		self._game = UNEXPOSED * grid_size ** 2
		self._attempted_catches = 0

		self._pokemon_locations = self.generate_pokemons()


	def get_game(self):
		"""Getter method for game 'private' variable"""
		return self._game

	def get_grid_size(self):
		"""Getter method for grid size private variable"""
		return self._grid_size

	def get_number_of_pokemons(self):
		"""Getter method for number of pokemons variabel"""
		return self._number_of_pokemons

	def get_pokemon_locations(self):
		"""Getter method for pokemon_locations 'private' variable"""
		return self._pokemon_locations

	def set_pokemon_locations(self, pokemon_locations):
		"""Setter method for pokemon_locations, used when restarting game

				Parameters:
					pokemon_locations(list(int)): list of pokemon indexes.
		"""
		self._pokemon_locations = pokemon_locations

	def set_game_string(self, game_string):
		"""Setter method for the game string"""
		self._game = game_string


	def get_attempted_catches(self):
		"""Getter method for the number of attempted catches (flagged cells)"""
		return self._attempted_catches


	def set_attempted_catches(self, attempted_catches):
		"""Setter method for the attempted catches varaible (flagged cells)"""
		self._attempted_catches = attempted_catches

	def generate_pokemons(self):
	    """Pokemons will be generated and given a random index within the game.

			    Parameters:
			        grid_size (int): The grid size of the game.
			        number_of_pokemons (int): The number of pokemons that the game will have.

			    Returns:
			        (tuple<int>): A tuple containing  indexes where the pokemons are
			        created for the game string.
	    """
	    cell_count = self._grid_size ** 2
	    pokemon_locations = ()

	    for _ in range(self._number_of_pokemons):
	        if len(pokemon_locations) >= cell_count:
	            break
	        index = random.randint(0, cell_count-1)

	        while index in pokemon_locations:
	            index = random.randint(0, cell_count-1)

	        pokemon_locations += (index,)

	    return pokemon_locations



	def position_to_index(self, position):
		""" Converts a tuple type postion coordinate to the index of the same cell
		in the game str
		
				Parameters: 
					position (tuple<int1, int2>): Tabular location of a given cell.

				Returns:
					index (int): The corresponding index of the position 
					in the object's game string.
		"""
		return position[0] * self._grid_size + position[1]


	def replace_character_at_index(self, index, character):
	    """A specified index in the game string at the specified index is replaced by
	    a new character.

		    Parameters:
		        game (str): The game string.
		        index (int): The index in the game string where the character is replaced.
		        character (str): The new character that will be replacing the old character.
	    """
	    self._game = self._game[:index] + character + self._game[index + 1:]


	def flag_cell(self, index):
	    """Toggle Flag on or off at selected index. If the selected index is already
	        revealed, the game would return with no changes.
	        Updates the number of attempted catches.

		        Parameters:
		            game (str): The game string.
		            index (int): The index in the game string where a flag is placed.
	    """
	    # If the user has run out of catch attempts, don't let them place another
	    if  (
	    		self._attempted_catches == self._number_of_pokemons and
	    		self._game[index] == UNEXPOSED
	    	):
	    	return None

	    if self._game[index] == FLAG:
	        self.replace_character_at_index(index, UNEXPOSED)
	        self._attempted_catches -= 1

	    elif self._game[index] == UNEXPOSED:
	        self.replace_character_at_index(index, FLAG)
	        self._attempted_catches += 1


	def index_in_direction(self, index, direction):
	    """The index in the game string is updated by determining the
	    adjacent cell given the direction.
	    The index of the adjacent cell in the game is then calculated and returned.

		    Parameters:
		        index (int): The index in the game string.
		        direction (str): The direction of the adjacent cell.

		    Returns:
		        (int): The index in the game string corresponding to the new cell position
		        in the game.
		        None: When given an invalid direction.
	    """
	    # convert index to row, col coordinate
	    col = index % self._grid_size
	    row = index // self._grid_size
	    if RIGHT in direction:
	        col += 1
	    elif LEFT in direction:
	        col -= 1
	    # Notice the use of if, not elif here
	    if UP in direction:
	        row -= 1
	    elif DOWN in direction:
	        row += 1
	    if not (0 <= col < self._grid_size and 0 <= row < self._grid_size):
	        return None
	    return self.position_to_index((row, col))


	def big_fun_search(self, index):
	 	"""Searching adjacent cells to see if there are any Pokemon"s present.
	 	Find all cells which should be revealed when a cell is selected.
	 	For cells which have a zero value (i.e. no neighbouring pokemons) all the cell"s
	 	neighbours are revealed. If one of the neighbouring cells is also zero then
	 	all of that cell"s neighbours are also revealed. This repeats until no
	 	zero value neighbours exist.
	 	For cells which have a non-zero value (i.e. cells with neightbour pokemons), only
	 	the cell itself is revealed.
		 	Parameters:
		 		index (int): Index of the currently selected cell

		 	Returns:
		 		(list<int>): List of cells to turn visible.
	 	"""
	 	queue = [index]
	 	discovered = [index]
	 	visible = [index]

	 	if self._game[index] == FLAG:
	 		return queue

	 	number = self.number_at_cell(index)
	 	if number != 0:
	 		return queue

	 	while queue:
	 		node = queue.pop()
	 		for neighbour in self.neighbour_directions(node):
	 			if neighbour in discovered or neighbour is None:
	 				continue

	 			discovered.append(neighbour)
	 			if self._game[neighbour] != FLAG:
	 				number = self.number_at_cell(neighbour)
	 				if number == 0:
	 					queue.append(neighbour)
	 			visible.append(neighbour)
	 	return visible


	def reveal_cells(self, index):
	    """
	    Reveals all neighbouring cells at index and repeats for all
	    cells that had a 0.
	    Does not reveal flagged cells or cells with Pokemon.

		    Parameters:
		        index (int): Index of the currently selected cell
	    """
	    number = self.number_at_cell(index)
	    self.replace_character_at_index(index, str(number))
	    clear = self.big_fun_search(index)
	    for i in clear:
	        if self._game[i] != FLAG:
	            number = self.number_at_cell(i)
	            self.replace_character_at_index(i, str(number))



	def neighbour_directions(self, index):
		""" This function returns a list of indexes that are a neighbour of the specified cell.

				Parameters:
					index (int): The index of the specified cell in the game str

				Returns:
					([int, ...]): Array of integers corresponding to game indexes that contain
					neighbouring cells.
		"""
		neighbours = []

		for direction in DIRECTIONS:
			neighbour = self.index_in_direction(index, direction)
			if neighbour != None: neighbours += [neighbour,]

		return neighbours


	def number_at_cell(self, index):
		""" This function returns the number of Pokemon in neighbouring cells.

				Parameters:
					index (int): The index of the specified cell in the game str

				Returns:
					(int): number of pokemon in the neighboring cells
		"""
		# Adds one for every neighbouring cell if the neighbouring cell is a pokemon, returns the total.
		return sum(1 for neighbour in self.neighbour_directions(index) \
			if neighbour in self._pokemon_locations)


	def check_win(self):
	    """ Checking if the player has won the game.

			    Returns:
			        (bool): True if the player has won the game, false if not.
	    """
	    return UNEXPOSED not in self._game and self._game.count(FLAG) == len(self._pokemon_locations)


	def __repr__(self):
		"""Returns most important variables for debugging purposes and saving state"""
		representation = [
		 f"grid_size = {self._grid_size}\n",
		 f"number_of_pokemons = {self._number_of_pokemons}\n",
		 f"game string = {self._game}\n",
		 f"pokemon_locations = {self._pokemon_locations}\n"
		]

		return ''.join(representation)


	def __str__(self):
		"""Returns game_board as a string (display_game from a1.py)"""
		row_separator = '\n' + WALL_HORIZONTAL * (self._grid_size + 1) * 4

		# column headings
		first_row = f"  {WALL_VERTICAL}"
		for i in range(1, self._grid_size + 1):
		# python magic: string format alignment
			first_row += f" {i:<2}{WALL_VERTICAL}"

		game_board = first_row + row_separator

	    # Game Grid
		for i in range(self._grid_size):
			row = f"{ALPHA[i]} "
			for j in range(self._grid_size):
				char = self._game[self.position_to_index((i, j))]
				row += f"{WALL_VERTICAL} {char} "

			game_board += "\n" + row + WALL_VERTICAL
			game_board += row_separator

		# Returning instead of printing because str() is a typically a type cast method.
		return game_board



class BoardView(tk.Canvas):
	""" 
		View class that handles the graphical user interface for the programme.
		Instantiated like: BoardView(master, grid size, board width=600, *args, **kwargs)
	"""

	def __init__(self, master, grid_size, board_width = 600, *args, **kwargs):
		""" Constructor method for the BoardView class

				Parameters:
					master (tk object): The root window.
					grid_size (int): The width of the game board.
					board_width (int): The pixel size of the tk window.
					args and kwargs: accepted so the caller can define any 
					tk.Canvas attributes when calling this class.
		"""
		self._master = master
		self._grid_size = grid_size
		self._board_width = board_width

		# Instantiate a canvas widget using the superclass
		super().__init__(self._master, width = board_width,
		 height = board_width, *args, **kwargs)

		self.draw_board(UNEXPOSED * grid_size ** 2)


	def draw_board(self, board):
		""" Draws relevant shapes to the canvas based on representation of the game board.
			First erases the canvas!
	
				Parameters:
					board: A string representation of the game. 
					e.g. "10~♥1~☺~~" for a 3x3 grid.
		"""
		# Clear canvas
		self.delete("all")
		
		rectangle_width, rectangle_height = self.get_rect_dimensions() 

		# Draw the rectangles to the canvas.
		for row in range(self._grid_size):
			for col in range(self._grid_size):
				index = self._grid_size * row + col

				if board[index] == UNEXPOSED:
					self.create_rectangle(col * rectangle_width, row * rectangle_height,
						(col + 1) * rectangle_width, (row + 1) * rectangle_height)
				elif board[index] == FLAG:
					self.create_rectangle(col * rectangle_width, row * rectangle_height,
						(col + 1) * rectangle_width, (row + 1) * rectangle_height, fill = "red")
				elif board[index].isdigit():
					self.create_rectangle(col * rectangle_width, row * rectangle_height,
						(col + 1) * rectangle_width, (row + 1) * rectangle_height, fill = "lawn green")
					# create label of board[index] number at center pixel of rectangle
					self.create_text(self.position_to_pixel((row, col)), text = str(board[index]))
				elif board[index] == POKEMON:
					self.create_rectangle(col * rectangle_width, row * rectangle_height,
						(col + 1) * rectangle_width, (row + 1) * rectangle_height, fill = "yellow")


	def get_rect_dimensions(self):
		"""Calculates and returns the dynamic width and height of each rectangle on the canvas
			
				Returns:
					tuple<int, int>: Dynamic width, height of each rectangle on the canvas.
		"""
		# Left like this so that it can easily be adjusted in future to support non-square boards
		return (self._board_width // self._grid_size, self._board_width // self._grid_size)



	def pixel_to_position(self, pixel_x, pixel_y):
		""" Converts a pixel tuple to the position of the rectangle that it is in

				Parameters:
					pixel (tuple<int, int>): The coordinate of the pixel on the canvas

				Returns:
					position (tuple<int, int>): The coordinate of the rectangle that 
					the pixel is inside. In format: (row, col)
		"""
		rectangle_width, rectangle_height = self.get_rect_dimensions() 
		return (pixel_y // rectangle_height, pixel_x // rectangle_width)


	def position_to_pixel(self, position):
		""" Returns the center pixel coordinate of the given rectangle position.

				Parameter:
					position (tuple<int, int>): location of the rectangle on the game
					board in the format (row, column)
		"""
		rect_width, rect_height = self.get_rect_dimensions()
		# X coordinate determined by column (position[1]):
		top_left_pixel = (rect_width * position[1], rect_height * position[0])

		center_pixel = (top_left_pixel[0] + rect_width // 2, top_left_pixel[1] + rect_height // 2)

		return center_pixel



class ImageBoardView(BoardView):
	"""Subclass of BoardView, the image canvas for task two"""

	def __init__(self, master, grid_size, board_width = 600, *args, **kwargs):
		""" Constructor method for the ImageBoardView class

				Parameters:
					master (tk object): The root window.
					grid_size (int): The width of the game board.
					board_width (int): The pixel size of the tk window.
					args and kwargs: accepted so the caller can define any 
					tk.Canvas attributes when calling this class.
		"""
		self._rendered_images = {}
		self._rendered_pokemon_images = {}
		super().__init__(master, grid_size, board_width, *args, **kwargs)


	def set_grid_size(self, grid_size):
		"""Setter method for grid_size, used when loading a file of a different grid size"""
		self._grid_size = grid_size
		# Whenever the grid_size is reset, the images need to be resized, so we clear
		# the cached image dictionaries. (benefits of encapsulation huh :))
		self._rendered_images = {}
		self._rendered_pokemon_images = {}

	def instantiate_image(self, image_code):
		"""Images need to be instantiated as a tkinter PhotoImage object before
			they can be displayed on the window. This method does that and puts
			the images into a dictionary for fast access.

				Parameter:
					image_path(str): The dictionary key corresponding to the image file path

				Returns:
					(PhotoImage obj): The tkinter photo image object corresponding to 
					the image_path that	has been resized to fit the board_width.
		"""
		# Memoize the process so that we don't have to render the same image hundreds of times
		if image_code == POKEMON:
			random_pokemon = random.randint(0, 5)
			rendered_image = self._rendered_pokemon_images.get(random_pokemon, None)
			if rendered_image is not None:
				return rendered_image
		else:
			rendered_image = self._rendered_images.get(image_code, None)
			if rendered_image is not None:
				return rendered_image

		# If the grid has a pokemon then we need to randomize the image
		if image_code == POKEMON:
			image_location = POKEMON_IMAGES.get(random_pokemon)
		else:
			image_location = IMAGES.get(image_code)

		# Image needs to be resized to fit the board_width and converted to PhotoImage object
		image = Image.open(image_location)
		image = image.resize(self.get_rect_dimensions())
		tk_rendered_image = ImageTk.PhotoImage(image)

		# Store rendered image in hash for memoization (and because tkinter 
		# does not display images unless they're stored to memory for some reason)
		if image_code != POKEMON:
			self._rendered_images[image_code] = tk_rendered_image
		else:
			self._rendered_pokemon_images[random_pokemon] = tk_rendered_image
		
		return tk_rendered_image


	def draw_board(self, board):
		""" Draws relevant shapes to the canvas based on representation of the game board.
			First erases the canvas!
	
				Parameters:
					board: A string representation of the game. 
					e.g. "10~♥1~☺~~" for a 3x3 grid.
		"""
		# Clear canvas
		self.delete("all")

		# Draw the images to the canvas.
		for row in range(self._grid_size):
			for col in range(self._grid_size):
				index = self._grid_size * row + col
				x, y = self.position_to_pixel((row, col))

				if board[index] == POKEMON:
					image = self.instantiate_image(POKEMON)
					self.create_image(x, y, image = image)
				else:
					image = self.instantiate_image(board[index])
					self.create_image(x, y, image = image)



class StatusBar(tk.Frame):
	""" Subclass of tk.Frame that holds the status bar of the PokemonGame"""

	def __init__(self, master, num_of_pokemons, create_new_game, restart_game, *args, **kwargs):
		"""Constructor for the status bar frame

				Parameters:
					master (tk object): The root window.
					numb_of_pokemons(int): the number of hidden pokemons in the grass
					create_new_game(method pointer): Method pointer of the 
					PokemonGame.create_game() method
					restart_game(method pointer): Method pointer to the 
					PokemonGame.restart_game() method
					args and kwargs: accepted so the caller can define any 
					tk.Frame attributes when instantiating a StatusBar object.

		"""
		super().__init__(master, *args, **kwargs)
		self._time_running = True

		# New game button
		self._new_game_button = tk.Button(self, text = "New Game", 
			command = create_new_game)
		self._new_game_button.grid(row = 0, column = 4, padx = 40, sticky = tk.E)

		# Restart button
		self._restart_game_button = tk.Button(self, text = "Restart Game", 
			command = restart_game)
		self._restart_game_button.grid(row = 1, column = 4, padx = 40, sticky = tk.E)
		
		# Alarm clock image label
		clock_image = tk.PhotoImage(file = "images/clock.gif")
		alarm_clock_label = tk.Label(self, image = clock_image)
		alarm_clock_label.image = clock_image
		alarm_clock_label.grid(row = 0, column = 2, rowspan = 2, padx = 15)

		# Time elapsed lable
		time_elapsed_label = tk.Label(self, text = "Time elapsed")
		time_elapsed_label.grid(row = 0, column = 3)

		# Time taken display label
		self._time_label = tk.Label(self, text = "0m 0s")
		self._time_label.grid(row = 1, column = 3)

		# Pokeball image label
		pokeball_image = tk.PhotoImage(file = "images/full_pokeball.gif")
		pokeball_label = tk.Label(self, image = pokeball_image)
		pokeball_label.image = pokeball_image
		pokeball_label.grid(row = 0, column = 0, rowspan = 2, padx = 15)


		# Attempted catches lable
		self._attempted_catches_label = tk.Label(self, text = "0 attempted catches")
		self._attempted_catches_label.grid(row = 0, column = 1, sticky = tk.W)

		# Pokeballs left label
		self._pokeballs_left_label = tk.Label(self,\
				text = f"{num_of_pokemons} pokeballs left")
		self._pokeballs_left_label.grid(row = 1, column = 1, sticky = tk.W)

		# Set time to auto update in the status bar.
		self._time_elapsed = 0
		self.update_label_time()


	def get_time_running(self):
		"""Getter method for the time_running variable"""
		return self._time_running


	def set_time_running(self, time_running):
		"""Setter method for whether the timer is counting up or not"""
		self._time_running = time_running
		self.update_label_time()


	def update_label_time(self):
		""" Updates the time and displays it in the status bar
	
				Parameter:
					time_running(bool): When true the time will be updated every second.
		"""
		self._time_elapsed += 1
		minutes = round(self._time_elapsed // 60)
		seconds = round(self._time_elapsed % 60)

		# Assign the calculated time to the label
		self._time_label['text'] = f"{minutes}m {seconds}s"

		if self._time_running:
			# Call this function after 1 second to update the time again.
			self.after(1000, self.update_label_time)


	def set_pokeball_labels(self, attempted_catches, num_of_pokemons):
		"""Updates the "attempted catches" and "pokeballs left" labels
				Parameters:
					attempted_catches (int): the number of flags on the game board
		"""
		self._attempted_catches_label['text'] = f"{attempted_catches} attempted catches"
		self._pokeballs_left_label['text'] = \
			f"{num_of_pokemons - attempted_catches} pokeballs left"

	def reset_time(self):
		""" Setter method for the time elapsed variable"""
		self._time_elapsed = 0



class FileMenu(tk.Menu):
	"""Inherits from tkinter Menu class, makes the file menu for the game"""

	def __init__(self, master, game):
		""" Constructor method for the FileMenu class

				Parameters:
					master (tk object): The root window.
					game (PokemonGame obj): An instance of the Pokemon Game class
					so that the menu commands can be directed back to a method of
					the PokemonGame class
		"""
		super().__init__(master)

		file_menu = tk.Menu(self)
		self.add_cascade(label = "File", menu = file_menu)

		file_menu.add_command(label="Save Game", command = game.save_game)
		file_menu.add_command(label="Load Game", command = game.load_game)
		file_menu.add_command(label="Restart", command = game.restart_game)
		file_menu.add_command(label="New Game", command = game.create_new_game)
		file_menu.add_command(label="Quit ;(", command = PokemonGame.verify_quit)

		master.config(menu = self)



def main():
	""" 
		Main function used to interact with the classes and
		determine the flow of the programme.
	"""

	root = tk.Tk()

	root.title("Pokemon: Got 2 Find Them All!")
	# If you want to change the canvas size, please see the constants at the top of the file.
	root.geometry(f"{400}x{400}")
	# Window label heading
	label = tk.Label(root, text = "Pokemon: Got 2 Find Them All!", bg = "OrangeRed3",
		font = ('', 22), fg = 'white')
	label.pack(side = tk.TOP, fill = "x")


	game_gui = PokemonGame(root)
	root.mainloop()


if __name__ == "__main__":
	main()