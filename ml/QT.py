from itertools import accumulate
from os import access
import numpy as np 
import pandas as pd
# TODO CHECKOUT cudf

class QLearningTable:
	def __init__(self,actions,learning_rate=0.05,reward_decay=0.9,e_greedy=0.1):

		self.actions=actions
		self.lr=learning_rate
		self.gamma=reward_decay
		self.epsilon=e_greedy
		
		self.q_table=pd.DataFrame(columns=self.actions,dtype=np.float64)

		self.accumulating_episodes = False
		self.episode_memory = []
	
	def choose_action(self,observation):
		self.check_state_exist(observation)
		
		#action selection
		if np.random.uniform()>self.epsilon:
			state_action =self.q_table.loc[observation,:]                 
			action =np.random.choice(state_action[state_action==np.max(state_action)].index)
		else:
			action = np.random.choice(self.actions)
		
		return action

	def store_experience(self, s, a, r, s_):
		if not self.accumulating_episodes:
			self.accumulating_episodes = True
		self.episode_memory.append((s, a, r, s_))

	def learn_from_episode(self):
		self.accumulating_episodes = False
		total_reward = 0
		for (s, a, r, s_) in reversed(self.episode_memory):
			self.check_state_exist(s)
			self.check_state_exist(s_)
			total_reward = r + self.gamma * total_reward
			q_predict = self.q_table.loc[s, a]
			q_target = total_reward
			
			self.q_table.loc[s, a] += self.lr * (q_target - q_predict)

		self.episode_memory.clear()
	
	def learn(self,s,a,r,s_):
		self.check_state_exist(s)
		self.check_state_exist(s_)
		q_predict=self.q_table.loc[s,a]
		if s_!='Game_over' or s_!='Game_pass':
			q_target =r+self.gamma*self.q_table.loc[s_,:].max()
		else:
			q_target=r
		self.q_table.loc[s,a]+=self.lr*(q_target-q_predict)
	
	def check_state_exist(self,state):
		if state not in list(self.q_table.index):
			new_row = pd.Series([0]*len(self.actions), index=self.q_table.columns, name=state)
			self.q_table = pd.concat([self.q_table, pd.DataFrame(new_row).T])