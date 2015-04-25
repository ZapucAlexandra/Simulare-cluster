"""
This module represents a cluster's computational node.

Computer Systems Architecture Course
Assignment 1 - Cluster Activity Simulation
March 2015
"""
from Queue import Queue
from threads import MyThread
from threading import Lock
from barrier import ReusableBarrierCond

class Node:
	"""
	Class that represents a cluster node with computation and storage
	functionalities.
	"""
	

	def __init__(self, node_id, data):
		"""
		Constructor.

		@type node_id: Integer
		@param node_id: the unique id of this node; between 0 and N-1

		@type data: List of Integer
		@param data: a list containing this node's data
		"""
		self.node_id = node_id
		self.data = data
		self.bufData = data[:]
		self.nodes = None
		self.queue = Queue()
		self.dataLock = Lock()
		self.threads = []
		self.num_Threads = 16
		self.create_threads()
		self.barrier = None
		
		
	def create_threads(self):
		""" Creates num_Threads"""
		for i in xrange(self.num_Threads):
			t = MyThread(i, self)
			t.start()
			self.threads.append(t)
	
	def __str__(self):
		"""
		Pretty prints this node.

		@rtype: String
		@return: a string containing this node's id
		"""
		return "Node %d" % self.node_id
	
	
	def set_cluster_info(self,  nodes):
		"""
		Informs the current node about the supervisor and about the other
		nodes in the cluster.
		Guaranteed to be called before the first call to 'schedule_task'.

		@type nodes: List of Node
		@param nodes: a list containing all the nodes in the cluster
		"""
		"""
			Sets the owner of reusable barrier. 
		"""
		self.nodes = nodes
		if self.node_id == self.nodes[0].node_id:
			self.barrier = ReusableBarrierCond(len(self.nodes))
		else:
			self.barrier = self.nodes[0].barrier
	
	def schedule_task(self, task, in_slices, out_slices):
		"""
		Schedule task to execute on the node.

		@type task: Task
		@param task: the task object to execute

		@type in_slices: List of (Integer, Integer, Integer)
		@param in_slices: a list of the slices of data that need to be
			gathered for the task; each tuple specifies the id of a node
			together with the starting and ending indexes of the slice; the
			ending index is exclusive

		@type out_slices: List of (Integer, Integer, Integer)
		@param out_slices: a list of slices where the data produced by the
			task needs to be scattered; each tuple specifies the id of a node
			together with the starting and ending indexes of the slice; the
			ending index is exclusive"""
			
		"""
		Creates a tuple with task, in_slices ans out_slices.
		Puts the tuple in queue.
		"""
		mytask = (task, in_slices, out_slices)
		self.queue.put(mytask)
	
	def sync_results(self):
		"""
		Wait for scheduled tasks to finish.
		Wait for all nodes to finish their jobs.
		Update the buffer for gather data with the result 
		from scatter.
		"""
		self.queue.join()
		self.nodes[0].barrier.wait()

		self.bufData = self.data[:]
		self.nodes[0].barrier.wait()

	def gatherData(self, begin, end):
		"""
		Returns the data needed for gather.
		Called by the node who needs this data.
		"""
		return self.bufData[begin:end]
	
	def scatterData(self, mydata, begin, end):
		"""
		Lock acquire to prevent scatte from other threads.
		Scatter the data of the thead that called this function.
		Lock release to allow other threads to scatter their data.
		"""
		self.dataLock.acquire()
		index = 0
		for i in range(begin, end):
			self.data[i] = self.data[i] + mydata[index]
			index += 1
		self.dataLock.release()
	
	def get_data(self):
		"""
		Return a copy of this node's data.
		"""
		return self.data


	def shutdown(self):
		"""
		Instructs the node to shutdown (terminate all threads). This method
		is invoked by the tester. This method must block until all the threads
		started by this node terminate.
		"""
		for i in range(self.num_Threads):
			self.queue.put((-1,[],[]))
		for i in xrange(self.num_Threads):
			self.threads[i].join()
		