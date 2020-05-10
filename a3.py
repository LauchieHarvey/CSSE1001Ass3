# Assignment 3. Pokemon, Got 2 Find Them All!
import random

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
INVALID = "That ain't a valid action buddy."
HELP_TEXT = """h - Help.
<Uppercase Letter><number> - Selecting a cell (e.g. 'A1')
f <Uppercase Letter><number> - Placing flag at cell (e.g. 'f A1')
:) - Restart game.
q - Quit.
"""
# ^^^^ CONSTANTS ^^^^


class PokemonGame:
	""" Controller class for the pokemon game."""
	
	def __init__(self):
		""" Constructor method for the PokemonGame class"""
		pass


class BoardModel:
	""" Model class that represents the board/game state as an object"""

	def __init__(self, grid_size = 6, number_of_pokemons = 5):
		"""Constructor method for the BooardModel class"""
		self._grid_size = grid_size
		self._number_of_pokemons = number_of_pokemons
		self._game = UNEXPOSED * grid_size ** 2

		# Might need to make generate_pokemons static for it to work in the constructor class.
		self._pokemon_locations = self.generate_pokemons()



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

	def parse_position(self, action):
	    """resolve the action into its corresponding position.

			    Parameters:
			        action (str): The string containing the row (Cap) and column.

			    Returns:
			        (tuple<int, int>) : The row, column position of a cell in the game.

			        None if the action is invalid.
	    """
	    if len(action) < 2:
	        return None

	    row, column = action[0], action[1:]

	    if not column.isdigit():
	        return None

	    x = ALPHA.find(row)
	    y = int(column) - 1
	    
	    if x == -1 or not 0 <= y < self._grid_size:
	        return None

	    return x, y


	def position_to_index(self, position):
		""" Converts a tuple type postion coordinate to the index of the same cell
		in the game str
		
				Parameters: 
					position (tuple<int1, int2>): Tabular location of a given cell.
					grid_size (int): The number of cells along each side of the grid.

				Returns:
					index (int): The corresponding index of the position 
					in the game string.
		"""
		return position[0] * self._grid_size + position[1]


	def replace_character_at_index(self, index, character):
	    """A specified index in the game string at the specified index is replaced by
	    a new character.

		    Parameters:
		        game (str): The game string.
		        index (int): The index in the game string where the character is replaced.
		        character (str): The new character that will be replacing the old character.

		    Returns:
		        (str): The updated game string.
	    """
	    return self._game[:index] + character + self._game[index + 1:]


	def flag_cell(self, index):
	    """Toggle Flag on or off at selected index. If the selected index is already
	        revealed, the game would return with no changes.

		        Parameters:
		            game (str): The game string.
		            index (int): The index in the game string where a flag is placed.
		        Returns
		            (str): The updated game string.
	    """
	    if self._game[index] == FLAG:
	        self._game = replace_character_at_index(self._game, index, UNEXPOSED)

	    elif self._game[index] == UNEXPOSED:
	        self._game = replace_character_at_index(self._game, index, FLAG)

	    return self._game


	def index_in_direction(self, index, direction):
	    """The index in the game string is updated by determining the
	    adjacent cell given the direction.
	    The index of the adjacent cell in the game is then calculated and returned.

		    Parameters:
		        index (int): The index in the game string.
		        grid_size (int): The grid size of the game.
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
	    return position_to_index((row, col), self._grid_size)


	def big_fun_search(self, game, pokemon_locations, index):
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

	 	if game[index] == FLAG:
	 		return queue

	 	number = number_at_cell(game, self._pokemon_locations, self._grid_size, index)
	 	if number != 0:
	 		return queue

	 	while queue:
	 		node = queue.pop()
	 		for neighbour in neighbour_directions(node, self._grid_size):
	 			if neighbour in discovered or neighbour is None:
	 				continue

	 			discovered.append(neighbour)
	 			if game[neighbour] != FLAG:
	 				number = number_at_cell(self._game, self._pokemon_locations, 
	 					self._grid_size, neighbour)
	 				if number == 0:
	 					queue.append(neighbour)
	 			visible.append(neighbour)
	 	return visible


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
			neighbour = index_in_direction(index, self._grid_size, direction)
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
		return sum(1 for neighbour in neighbour_directions(index, self._grid_size) \
			if neighbour in self._pokemon_locations)


	def check_win(self):
	    """ Checking if the player has won the game.

			    Returns:
			        (bool): True if the player has won the game, false if not.
	    """
	    return UNEXPOSED not in self._game and self._game.count(FLAG) == len(self._pokemon_locations)


	def __repr__(self):
		"""Print most important variables to console for debugging"""
		return f"grid_size = {self._grid_size}\nnumber_of_pokemons = {self._number_of_pokemons}\ngame string = \
		{self._game}\npokemon_locations = {self._pokemon_locations}"


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





class BoardView:
	""" View class that handles the graphical user interface for the programme."""

	def __init__():
		"""Constructor method for the BoardView class"""
		pass





def main():
	GRID_SIZE = 6
	NUMBER_OF_POKEMONS = 7
	
	game_board = BoardModel(GRID_SIZE, NUMBER_OF_POKEMONS)
	print(str(game_board))


if __name__ == "__main__":
	main()