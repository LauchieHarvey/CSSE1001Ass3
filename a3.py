# Assignment 3. Pokemon, Got 2 Find Them All!
import random
import tkinter as tk
import tkinter.messagebox
import time

# Constants you may wish to change:
GRID_SIZE = 10
NUMBER_OF_POKEMONS = 7
WINDOW_SIZE = 600
# CONSTANTS you don't want to change:
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

# ^^^^ CONSTANTS ^^^^


class PokemonGame:
	""" 
		Controller class for the pokemon game.
		instantiated like: PokemonGame(master, grid size=10, num pokemon=15, task=TASK_ONE)
	"""
	
	def __init__(self, master, grid_size, number_of_pokemons, task = TASK_TWO):
		""" Constructor method for the PokemonGame class"""
		self._master = master
		self._game_board = BoardModel(grid_size, number_of_pokemons)

		# Instantiate the canvas && position it in the master window.
		self._canvas = BoardView(self._master, grid_size, WINDOW_SIZE)
		self._canvas.pack(expand = True, fill = "both")

		if task == TASK_TWO:
			self._status_bar = StatusBar(master)
			self._status_bar.pack(fill = 'x', side = tk.BOTTOM)

		# Resize root window to fit all widgets.
		master.geometry("")

		self.set_canvas_binds()



	def set_canvas_binds(self):
		""" Set event bindings for the canvas."""
		self._canvas.bind("<Button-1>", self.left_click)
		self._canvas.bind("<Button-2>", self.right_click)
		self._canvas.bind("<Button-3>", self.right_click)




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
				PokemonGame.end_game_message(False)

		if self._game_board.check_win():
			PokemonGame.end_game_message(True)

		self._canvas.draw_board(self._game_board.get_game())


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

		if self._game_board.check_win():
			# They have won so display win messagebox
			PokemonGame.end_game_message(True)

		self._canvas.draw_board(self._game_board.get_game())



	def end_game_message(has_won):
		""" Shows the user the messagebox displaying either a win or a loss

				Parameters:
					won (bool): Whether the user won or lost (True if the user did win)
		"""
		if not has_won:
			tk.messagebox.showerror(title="Ooopsie ;(", message = "Oh no! You scared away all the pokemons!")
		else:
			tk.messagebox.showinfo(title = "Congratulations!", message = "Congratulations, you won!!")


	def create_new_game():
		"""Event handler for "New Game" button click"""
		pass

	def restart_game():
		"""Event handler for "Restart Game" button click"""
		pass



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

		self._pokemon_locations = self.generate_pokemons()


	def get_game(self):
		"""Getter method for game 'private' variable"""
		return self._game

	def get_pokemon_locations(self):
		"""Getter method for pokemon_locations 'private' variable"""
		return self._pokemon_locations

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

		        Parameters:
		            game (str): The game string.
		            index (int): The index in the game string where a flag is placed.
	    """
	    if self._game[index] == FLAG:
	        self.replace_character_at_index(index, UNEXPOSED)

	    elif self._game[index] == UNEXPOSED:
	        self.replace_character_at_index(index, FLAG)


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
		"""Returns most important variables for debugging purposes"""
		representation = {
		 f"grid_size = {self._grid_size}\n",
		 f"number_of_pokemons = {self._number_of_pokemons}\n",
		 f"game string = {self._game}\n",
		 f"pokemon_locations = {self._pokemon_locations}\n"
		}
		# Returning instead of printing to follow convention.
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
		super().__init__(self._master, bg = "green", width = board_width,
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

		center_pixel = (top_left_pixel[0] + rect_width / 2, top_left_pixel[1] + rect_height / 2)

		return center_pixel



class StatusBar(tk.Frame):
	""" Subclass of tk.Frame that holds the status bar of the PokemonGame"""

	def __init__(self, master, *args, **kwargs):
		"""Constructor for the status bar frame

				Parameters:
					master (tk object): The root window.
					args and kwargs: accepted so the caller can define any 
					tk.Frame attributes when instantiating a StatusBar object.

		"""
		super().__init__(master, *args, **kwargs)

		self._new_game_button = tk.Button(self, text = "New Game", command = PokemonGame.create_new_game)
		self._new_game_button.pack(anchor = tk.E, side = tk.TOP)

		self._restart_game_button = tk.Button(self, text = "Restart Game", command = PokemonGame.restart_game)
		self._restart_game_button.pack(anchor = tk.E, side = tk.BOTTOM)
		
		# Instantiate timer
		self._start_time = time.time()
		self._time_label = tk.Label(self, text = "0m 0s")
		self._time_label.pack()
		self.update_label_time()


	def update_label_time(self):
		current_time = time.time()
		elapsed_time = current_time - self._start_time
		minutes = round(elapsed_time // 60)
		seconds = round(elapsed_time % 60)
		# Assign the calculated time to the label
		self._time_label['text'] = f"{minutes}m {seconds}s"
		self.after(1000, self.update_label_time)





def main():
	""" 
		Main function used to interact with the classes and
		determine the flow of the programme.
	"""

	root = tk.Tk()
	root.title("Pokemon: Got 2 Find Them All!")
	root.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}")
	# Window label heading
	label = tk.Label(root, text = "Pokemon: Got 2 Find Them All!", bg = "pink")
	label.pack(side = tk.TOP, fill = "x")

	game_gui = PokemonGame(root, GRID_SIZE, NUMBER_OF_POKEMONS)
	root.mainloop()


if __name__ == "__main__":
	main()