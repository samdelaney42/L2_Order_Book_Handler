import copy

class Order:
	"""
	Represents an order in the limit order book.

	Attributes:
		entryTime (object): The time when the order was entered.
		type (object): The type of the order.
		id (object): The unique identifier of the order.
		shares (object): The number of shares in the order.
		price (object): The price of the order.
		direction (object): The direction of the order.
		next (Order): Reference to the next order in the linked list.
		prev (Order): Reference to the previous order in the linked list.
	"""
	def __init__(self, data):
		"""
		Initializes a new instance of Order.

		Args:
			data (list): A list containing order data.
		"""
		self.entryTime = copy.copy(data.time)
		self.type = copy.copy(data.type)
		self.id = copy.copy(data.order_id)
		self.shares = copy.copy(data.shares)
		self.price = copy.copy(data.price)
		self.direction = copy.copy(data.direction)
		self.next = None
		self.prev = None

	def getOrder(self):
		"""
		Retrieves order details.

		Returns:
			list: A list containing order ID, price, and shares.
		"""
		return [self.id, self.price, self.shares]

	def getDirection(self):
		"""
		Retrieves the direction of the order.

		Returns:
			str: The direction of the order ('buy' or 'sell').
		"""
		if self.direction == 1:
			return 'buy'
		else:
			return 'sell'