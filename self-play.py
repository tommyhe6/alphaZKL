# ==========[ IMPORTS ]==========
from game import Game
from agent import Agent
from mcts import MCTS
from typing import List, Tuple
import numpy as np
from tqdm import tqdm


# ==========[ SELF-PLAY ]==========
class SelfPlay:
    def __init__(self, game: Game, agent: Agent):
        """Runs self-play episodes and learns from them.

        :param game: The game being played
        :type game: Game
        :param agent: The agent playing the game
        :type agent: Agent
        """

        self.game = game
        self.agent = agent
        self.opponent = Agent(game)
        self.all_examples = []

    def run_episode(self) -> List[Tuple[np.ndarray, int, np.ndarray, int]]:
        """
        Runs one episode starting with player one.
        - pi is the MCTS-informed policy vector
        - v is +1 for a win, 0 for a draw, -1 for a loss.

        :return: List of examples of the form (canonical_board, current_player, pi, v)
        :rtype: List[Tuple[np.ndarray, int, np.ndarray, int]]
        """

        # Initialize the game
        board = self.game.initialize_board()
        examples = []
        step = 0
        current_player = 1

        # Step through game
        while True:
            step += 1

            # Compute action probabilities
            canonical_board = self.game.canonicalize(board, current_player)
            pi = self.agent.get_policy(canonical_board)

            # Create example and add symmetries
            symmetries = self.game.get_symmetries(canonical_board, pi)
            for board, player in symmetries:
                examples.append((board, player, pi, None))

            # Take action and step game
            action = np.random.choice(len(pi), p=pi)
            board, current_player = self.game.step(board, current_player, action)

            # Returns the game result for the current player (board, pi, v)
            result = self.game.check_win(board, current_player)
            if result is not None:
                return [(example[0], example[2], result * (-1 if current_player == 1 else 1)) for example in examples]


    def learn(self, num_iterations=1000, num_episodes=100):
        """
        
        :param num_iterations: Number of iterations to run
        :type num_iterations: int, optional
        :param num_episodes: Number of episodes to run per iteration
        :type num_episodes: int, optional
        """

        # Run iterations
        for i in range(num_iterations):
            print(f'[ITERATION {i}]')
            current_examples = []

            # Run episodes
            for j in tqdm(range(num_episodes), desc='Running episodes'):
                current_examples += self.run_episode()
            
            # Get training examples
            self.all_examples += current_examples
            training_examples = np.random.permutation(self.all_examples)

            # Train agent
            self.agent.train(training_examples)
