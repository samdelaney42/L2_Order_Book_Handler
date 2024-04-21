import limit_bst as tree
from  order_obj import Order
import numpy as np
import pandas as pd
import log

class Book:
	"""
    Represents a limit order book.

    Attributes:
        buy (BinarySearchTree): A binary search tree representing buy orders.
        sell (BinarySearchTree): A binary search tree representing sell orders.
        best_bid (Order): The best bid order in the book.
        best_offer (Order): The best offer order in the book.
        orders (dict): All orders keyed by their IDs.
		trades [list]: All visible executions 
		event_times [list]: Event times used later to index the formatted orderbook
		book_snapshot [list]: in order traversal of the book after each event
		hidden_trades [list]: All hidden executions
    """
	
	def __init__(self):
		"""
        Initializes a new instance of Book.

        Sets up logging configuration and initializes necessary attributes.
        """
		self.logger = log.get_logger('Order Book')

		self.buy = tree.BinarySearchTree(-9999999999)
		self.sell = tree.BinarySearchTree(9999999999)
		self.best_bid = self.buy
		self.best_offer = self.sell
		self.orders = {}
		self.trades = []
		self.hidden_trades = []
		self.event_times = []
		self.book_snapshot = []

	def  handleEvent(self, event, i):
		"""
        Handles incoming events and takes appropriate actions.

        Args:
            event (Event): The event object to be processed.
            i (int): Identifier for the event.

        Raises:
            ValueError: If the event type is not recognized.
        """

		if event.type == 1:
			self.logger.info('{} New Order Submission'.format(i))
			self.newLimitOrderSubmission(event)
		elif event.type == 2:
			self.logger.info('{} Order Cancelation'.format(i))
			self.cancelationOfExistingLimitOrder(event)
		elif event.type == 3:
			self.logger.info('{} Order Deleteion'.format(i))
			self.deletionOfExistingLimitOrder(event)
		elif event.type == 4:
			self.logger.info('{} Visible Order Execution'.format(i))
			self.orderExecution(event)
		elif event.type == 5:
			self.logger.info('{} Hidden Order Execution'.format(i))
			self.hiddentExecution(event)
		# aggregate info for use later
		self.event_times.append(event.time)
		self.book_snapshot.append([self.getAllLevels(), event.time])


	def newLimitOrderSubmission(self, event):
		"""
        Processes a new limit order submission event.

        Args:
            event (Event): The event object representing the new order submission.
        """
		# turn event into order object 
		new_order = Order(event)
		# add to order dict keyd on id
		self.orders[new_order.id] = new_order
		self.logger.info("Adding ID {} at {}, vol {}, in {} tree".format(new_order.id, new_order.price, new_order.shares, new_order.getDirection()))
		# check if buy or sell then add to approporiate tree
		if event.direction == 1:
			self.buy.handleNewOrder(new_order)
		elif event.direction == -1:
			self.sell.handleNewOrder(new_order)
		# update NBBO
		self.updateNbbo(new_order)

	def cancelationOfExistingLimitOrder(self, event):
		"""
        Cancels an existing limit order.

        Args:
            event (Event): The event object representing the order cancellation.
        """
		# get the ID of the order to partially cancel and get the order from the dict
		order_to_cancel = self.orders.get(event.order_id)
		shares_to_subtract_from_limit_total = event.shares
		if (order_to_cancel is not None):
			if (order_to_cancel.shares != 0):
				self.logger.info("Canceling {} shares for ID {} at {} in {} tree".format(shares_to_subtract_from_limit_total, order_to_cancel.id, order_to_cancel.price, order_to_cancel.getDirection()))
				if order_to_cancel.direction == 1:
					self.buy.handleCancellation(order_to_cancel, shares_to_subtract_from_limit_total)
				elif order_to_cancel.direction == -1:
					self.sell.handleCancellation(order_to_cancel, shares_to_subtract_from_limit_total)
				# reduce the number of shares at this order by those in the event 
				order_to_cancel.shares = order_to_cancel.shares - shares_to_subtract_from_limit_total
				# update the order in the dict
				self.orders[order_to_cancel.id] = order_to_cancel
				# edit the number of total shares at that level in the book
				self.logger.info("ID {} has {} shares remaining".format(order_to_cancel.id, order_to_cancel.shares))
		else:
			self.logger.info("ID {} does not exist".format(event.order_id))

	def deletionOfExistingLimitOrder(self, event):
		"""
        Deletes an existing limit order.

        Args:
            event (Event): The event object representing the order deletion.
        """
		# get the ID of the order to delete and get the order from the dict
		order_to_delete = self.orders.get(event.order_id)
		# check if order exists
		if order_to_delete is not None:
			# pass order to book to delete from relevant queue
			self.logger.info("Deleting ID {} at {} from queue in {} tree".format(order_to_delete.id, order_to_delete.price, order_to_delete.getDirection()))
			if order_to_delete.direction == 1:
				self.buy.handleDeletion(order_to_delete)
			elif order_to_delete.direction == -1:
				self.sell.handleDeletion(order_to_delete)
		else:
			self.logger.info("ID {} does not exist".format(event.order_id))

	def orderExecution(self, event):
		"""
        Executes an order.

        Args:
            event (Event): The event object representing the order execution.
        """
		# get id of order to execute and num shares to execute
		order_to_execute = self.orders.get(event.order_id)
		shares_traded = event.shares
		if order_to_execute is not None:
			# determine the direction we are executing and send to respective buy or sell tree
			self.logger.info("Executing {} shares for ID {} at {} in {} tree".format(shares_traded, order_to_execute.id, order_to_execute.price, order_to_execute.getDirection()))
			if order_to_execute.direction == 1:
				self.buy.handleVisibleExecution(order_to_execute, shares_traded)
			elif order_to_execute.direction == -1:
				self.sell.handleVisibleExecution(order_to_execute, shares_traded)
			# get number of shares executed and remove it from the amount we we have saved in the executable order object
			# reduce shares at ID
			if order_to_execute.shares > 0:
				order_to_execute.shares = order_to_execute.shares - shares_traded
			else:
				self.logger.info("ID {} has 0 shares remaining".format(order_to_execute.id))
			# update the order in dict with new vlaues
			self.orders[order_to_execute.id] = order_to_execute
			self.logger.info("ID {} has {} shares remaining".format(order_to_execute.id, order_to_execute.shares))
			# Add to trades list
			self.trades.append([event.time, order_to_execute.price, shares_traded, order_to_execute.direction])
			# if there are 0 shares for this ID then remove the order from the queue
			if order_to_execute.shares == 0:
				self.deletionOfExistingLimitOrder(event)
		else:
			self.logger.info("ID {} does not exist".format(event.order_id))

	def hiddentExecution(self, event):
		self.hidden_trades.append([event.time, event.price, event.shares, event.direction])
		
	def getNbbo(self):
		"""
        Retrieves the National Best Bid and Offer (NBBO).

        Returns:
            tuple: A tuple containing the best offer price and best bid price.
        """
		return self.best_offer.limit_price, self.best_bid.limit_price
	
	def updateNbbo(self, order):
		"""
        Updates the BBO based on the given order.

        Args:
            order (Order): The order object used to update NBBO.
        """
		if order.direction == 1:
			if order.price > self.best_bid.limit_price:
				self.best_bid = self.buy.inOrderTraversal()[-1]
		else:
			if order.price < self.best_offer.limit_price:
				self.best_offer = self.sell.inOrderTraversal()[0]

	def getXLevels(self, x):
		"""
        Retrieves the top X levels from buy and sell trees.

        Args:
            x (int): The number of levels to retrieve.

        Returns:
            list: A list containing top X buy levels and top X sell levels.
        """
		b = self.buy.inOrderTraversal()[-x:]
		o = self.sell.inOrderTraversal()[:x]

		b = [[i.limit_price, i.total_volume, i.num_orders] for i in b]
		o = [[i.limit_price, i.total_volume, i.num_orders] for i in o]
		return [b, o]
	
	def getAllLevels(self):
		"""
        Retrieves all levels from buy and sell trees.

        Returns:
            list: A list containing all buy levels and all sell levels.
        """
		b = self.buy.inOrderTraversal()
		o = self.sell.inOrderTraversal()

		b = [[i.limit_price, i.total_volume, i.num_orders] for i in b]
		o = [[i.limit_price, i.total_volume, i.num_orders] for i in o]
		return [b, o]
	
	def getOrdersatlevel(self, level):
		"""
		Gets all the orders in the queue from a specified level

		Returns:
			list: A list containing all the orders at a given level, index 0 being first in queue
		"""
		if self.buy.checkLimit(level) == True:
			limit_to_get_queue = self.buy.getLimit(level)
		elif self.sell.checkLimit(level) == True:
			limit_to_get_queue = self.sell.getLimit(level)
		else:
			self.logger.info("Limit {} does not exist".format(level))
		
		return limit_to_get_queue.order_queue.getOrderqueue(limit_to_get_queue.order_queue.head)

		
		

class Format:
	"""
	This class takes the order book output and formats it to a symetrical, 5 level data frame

	Attributes:
		data: this is the order book output that we will manipuate
	"""

	def __init__(self, data):
		self.data = data
	
	def formatBook(self):
		self.book, self.time = self.stripTime(self.data)
		self.data = self.symetricBook(self.book, self.time)
		self.data = self.outputBook(self.data)
		return self.data
	
	def  stripTime(self, book_and_time):
		book = []
		time = []
		for i in range(len(book_and_time)):
			book.append(book_and_time[i][0])
			time.append(book_and_time[i][1])
		return book, time

	def symetricBook(self, book_snapshot, time_list):

		symetric_book = []
		count = 0
		for x in book_snapshot:
			bid = x[0]
			ask = x[1]

			if len(bid) <= 5:
				bid = bid[::-1]
				for y in range((5-len(bid))):
					bid.append([0, 0, 0])
			elif len(bid) > 5:
				bid = bid[::-1]
				bid = bid[:5]
			
			if len(ask) <= 5:
				for z in range((5-len(ask))):
					ask.append([0, 0, 0])
			elif len(ask) > 5:
				ask = ask[:5]
			time = time_list[count]

			symetric_book.append([time, ask, bid])
			count += 1
		
		return symetric_book
	
	def outputBook(self, symetric_book):
		
		colnames = ['Ask_1','Ask_1_Vol', 'Bid_1', 'Bid_1_Vol','Ask_2','Ask_2_Vol', 'Bid_2', 'Bid_2_Vol','Ask_3','Ask_3_Vol', 'Bid_3', 'Bid_3_Vol','Ask_4','Ask_4_Vol', 'Bid_4', 'Bid_4_Vol','Ask_5','Ask_5_Vol', 'Bid_5', 'Bid_5_Vol']
		df_rows = []
		idx = []
		for snap_shot in symetric_book:
			idx.append(snap_shot[0])
			ask = snap_shot[1]
			bid = snap_shot[2]
			df_row = []
			for level in range(len(ask)):
				df_row.append(ask[level][:2])
				df_row.append(bid[level][:2])
			a = np.array(df_row)
			a = a.flatten()
			a = list(a)
			df_rows.append(a)

		my_output = pd.DataFrame(df_rows, columns = colnames, index = idx)
		return my_output