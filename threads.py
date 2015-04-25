"""
Computer Systems Architecture Course
Assignment 1 - Cluster Activity Simulation
March 2015

Name: Zapuc Ileana-Alexandra
"""
from threading import Thread

class MyThread(Thread):
	"""
	Class that represents a thread of a node.
	"""
	def __init__(self, nr, node):
		"""
		Constructor.
		
		@type node: Integer
		@param node_id: the unique id of the owner of this thread;
						between 0 and N-1

		@type nr: Integer
		@param data: the unique id of this thread
		"""
		Thread.__init__(self)
		self.id = nr
		self.node = node
	
	
	def run(self):
		"""
			Thread pops a task from queue(taskpool); gather data
		from other nodes; run computations; scatter data to 
		other nodes.
		"""
		while(1):
			item = self.node.queue.get()
			task = item[0]
			if task == -1:
				break
			inlist = item[1]
			outlist = item[2]
			data = []
			for tuplu in inlist:
				nodeGather = tuplu[0]
				dataGather = self.node.nodes[nodeGather].gatherData\
			(tuplu[1], tuplu[2])
				data.extend(dataGather)
			result_data = task.run(data)
			
			begin = 0
			for tuplu in outlist:
				nodeScatter = tuplu[0]
				length = tuplu[2] - tuplu[1]
				end = begin + length
				self.node.nodes[nodeScatter].scatterData\
			(result_data[begin:end], tuplu[1], tuplu[2])
				begin = end
				
			self.node.queue.task_done()