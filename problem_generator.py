import itertools

class Problem_generator:

    def __init__(self, number_queens):

        self.number_queens = number_queens

    def generate_input(self):

        problem_desc = {}

        # generate all possible permutations from 0 to n (number queens)
        permutations = list(itertools.permutations([queen for queen in range(self.number_queens)]))

        # iterate over each permutation, convert it to string key and calculate it evaluation value
        for perm in permutations:

            key = ''.join([str(p)+'-' for p in perm])

            # in each final position, save the calculated energy of this position
            problem_desc[key[:-1]] = self.calculate_eval_value(key[:-1])

        return problem_desc

    def calculate_eval_value(self, board):

        # value is the final value of the board taking into account the collisions
        value = 0

        # it contains an array of int of the position of each queen
        positions = list(map(int, board.split('-')))

        # iterate over each queen to calculate its value except the last one that cannot be attacked by one other to its right
        for index_position in range(len(positions)-1):

            # if there are two queen or more in the line (right, diagonal top or diagonal bottom, position to the left are not considered and in the same column is not possible to have queens)
            # and extra penalization is applied
            penalty_diag_top = 0
            penalty_diag_bot = 0

            # check the queens (next_index_position queens) on the right that are attacking to the current evaluated queen (index_position queen)
            for index_next_position in range(index_position+1, len(positions)):

                # check if there is in any queen in the right diagonal

                # calculate which is the index position in the diagonal is an attacked position by the current queen
                diagonal_index_diff = index_next_position - index_position

                # check if the current queen is in the same diagonal (top or bottom) than the current queen (it does not matter to have values lower than 0 or greather than the board)
                collision_diag_top = positions[index_position] - diagonal_index_diff
                collision_diag_bot = positions[index_position] + diagonal_index_diff

                # if the current queen is attacked by other queen in the top diagonal
                if positions[index_next_position] == collision_diag_top:

                    value += 1 + penalty_diag_top
                    penalty_diag_top += 1

                # if the current queen is attacked by other queen in the bottom diagonal
                elif positions[index_next_position] == collision_diag_bot:

                    value += 1 + penalty_diag_bot
                    penalty_diag_bot += 1

        return value