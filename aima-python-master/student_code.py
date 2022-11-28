import sys
sys.path.append("aima-python")
from agents import *


class HW1:
    def __init__(self, agents=None, env=None):
        #Do not modify this, it is used for testing! 
        if agents is None:
            (self.reflex_agent, self.model_agent, self.random_agent) = self.get_agents()
        else:
            (self.reflex_agent, self.model_agent, self.random_agent) = agents

        if env is None:
            self.environment = self.get_env()
        else:
            self.environment = env

    def get_agents(self):
        '''
        FILL IN AGENTS HERE
        Return all three agents like: return(reflex_agent, model_agent, random_agent)
        '''
        agent_1 = ReflexVacuumAgent #reflex agent
        agent_2 = ModelBasedVacuumAgent #model based agent
        agent_3 = RandomVacuumAgent #random agent
        return [agent_1, agent_2, agent_3]
    
    def get_env(self):
        '''
        FILL IN ENVIRONMENT HERE
        Return the environment like: return environment
        '''
        env = TrivialVacuumEnvironment #trivial vac environment
        return env

    def run(self, agent, env, times):
        '''
        Run the environment for the given number of times and return the performance of the agent.
        Utilize the helper function to run the environment for the given number of times.
        Make sure the agent is added to the environment before running the environment.
        Return the status of the environment after the run.
        '''
        #step 1: get agent in the env
        #step 2: run the env for the given times
        #step 3: set to status variable
        #step 4: return the status of the env after the run
        status = None
        env.add_thing(thing=agent)
        for i in range(times):
            env.run()
        status = env.status
        return status

    def problem_1(self):
        '''
        Call your run function with the reflex agent and the trivial vac environment and return the result 
        '''
        my_agent = ReflexVacuumAgent()
        my_env = TrivialVacuumEnvironment()
        TraceAgent(my_agent)
        return self.run(my_agent, my_env, 25)

    def problem_2(self):
        '''
        Call your run function with the model based agent and the trivial vac environment and return the result
        '''
        my_agent = ModelBasedVacuumAgent()
        my_env = TrivialVacuumEnvironment()
        TraceAgent(my_agent)
        return self.run(my_agent, my_env, 25)

    def problem_3(self):
        '''
        Call your run function with the random agent and the trivial vac environment and return the result
        '''
        my_agent = RandomVacuumAgent()
        my_env = TrivialVacuumEnvironment()
        TraceAgent(my_agent)
        return self.run(my_agent, my_env, 25)

    def problem_4(self):
        '''
        Compare the performance of the reflex agent, the model based agent, and random agent in the trivial vac environment.
        You will have to pass the agents and the environment to the comparison function, 
        this will require reviewing the documentation because the process is a little different.
        '''
        my_env = TrivialVacuumEnvironment
        agent1 = ReflexVacuumAgent
        agent2 = ModelBasedVacuumAgent
        agent3 = ReflexVacuumAgent
        my_agents = [agent1, agent2, agent3]
        return compare_agents(my_env, my_agents, 25)



def main():
    hw1 = HW1()
    print("Problem 1:", hw1.problem_1())
    print("Problem 2:", hw1.problem_2())
    print("Problem 3:", hw1.problem_3())
    print("Problem 4:", hw1.problem_4())


