class Order:
	def __init__(self, data):

		self.entryTime = data[0].copy()
		self.type = data[1].copy()
		self.id = data[2].copy()
		self.shares = data[3].copy()
		self.price = data[4].copy()
		self.direction = data[5].copy()
		self.next = None
		self.prev = None

	def getOrder(self):
		return [self.id, self.price, self.shares]

	def getDirection(self):
		if self.direction == 1:
			return 'buy'
		else:
			return 'sell'