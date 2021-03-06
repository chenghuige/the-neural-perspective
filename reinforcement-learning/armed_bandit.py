import tensorflow as tf
import numpy as np


class agent(object):

    def __init__(self, num_bandits, num_actions):
        """
        Initialize the agent.
        """

        # Placeholders
        self.state = tf.placeholder(name='state',
            shape=[1], dtype=tf.int32)
        self.action = tf.placeholder(name='action',
            shape=[1], dtype=tf.int32)
        self.reward = tf.placeholder(name='reward',
            shape=[1], dtype=tf.float32)

        # One hot encode the state
        self.state_one_hot = tf.one_hot(indices=self.state, depth=num_bandits)

        # Feed forward net to choose the action
        with tf.variable_scope("net"):
            self.W_input = tf.Variable(tf.ones([num_bandits, num_actions]))
        z1 = tf.matmul(self.state_one_hot, self.W_input)
        self.fc1 = tf.nn.sigmoid(z1)

        self.chosen_weight = tf.slice(tf.reshape(self.fc1, [-1, ]),
            self.action, [1])

        self.loss = -(tf.log(self.chosen_weight) * self.reward)
        self.train_optimizer = tf.train.GradientDescentOptimizer(
            0.001).minimize(self.loss)

    def pull_arm(self, bandit, action):
        """
        Pull the arm of a bandit and get a positive
        or negative result. (+/- 1)
        """

        # get random number from normal dist.
        answer = np.random.randn(1)

        # Get positive reward if bandit is higher than random result
        if bandit[action] > answer:
            return 1
        else:
            return -1

    def step(self, sess, state, action, reward):

        input_feed = {self.state: state,
            self.action: action, self.reward: reward}
        output_feed = [self.W_input, self.train_optimizer]
        outputs = sess.run(output_feed, input_feed)
        return outputs[0], outputs[1]

if __name__ == '__main__':

    # Our options
    bandits = [[-5, -1, 0, 1], [-1, -5, 1, 0], [0, 1, -1, -5]]
    num_bandits = len(bandits)
    num_actions = len(bandits[0])

    # Store all rewards from actions
    rewards = np.zeros([num_bandits, num_actions])

    with tf.Session() as sess:

        model = agent(num_bandits, num_actions)
        sess.run(tf.initialize_all_variables())

        # Simulation
        for i in xrange(1000):

            # Pick a random state
            state = np.random.randint(0, num_bandits)
            print state

            # Determine the action chosen and associated reward
            if np.random.rand(1) < 0.25:
                action = np.random.randint(0, num_actions)
            else:
                action = np.argmax(sess.run(model.fc1, feed_dict={
                    model.state: [state]}))
            reward = model.pull_arm(bandits[state], action)

            # Store the reward
            rewards[state, action] += reward

            # Update weights
            W, _ = model.step(sess, [state], [action], [reward])

            print rewards

        print W








