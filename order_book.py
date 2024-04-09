import limit_bst as tree
from  order_obj import Order
import logging

class Book:

	def __init__(self):
		logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

		self.buy = tree.BinarySearchTree(-9999999999)
		self.sell = tree.BinarySearchTree(9999999999)
		self.best_bid = self.buy
		self.best_offer = self.sell
		self.orders = {}

	def  handleEvent(self, event, i):
		if event.type == 1:
			logging.info('{} New Order Submission'.format(i))
			self.newLimitOrderSubmission(event)
		elif event.type == 2:
			logging.info('{} Order Cancelation'.format(i))
			self.cancelationOfExistingLimitOrder(event)
		elif event.type == 3:
			logging.info('{} Order Deleteion'.format(i))
			self.deletionOfExistingLimitOrder(event)
		elif event.type == 4:
			logging.info('{} Visible Order Execution'.format(i))
			self.orderExecution(event)
		elif event.type == 5:
			logging.info('{} Hidden Order Execution'.format(i))
		logging.info(self.getAllLevels())


	def newLimitOrderSubmission(self, event):
		# turn event into order object 
		new_order = Order(event)
		# add to order dict keyd on id
		self.orders[new_order.id] = new_order
		logging.info("Adding ID {} at {}, vol {}, in {} tree".format(new_order.id, new_order.price, new_order.shares, new_order.getDirection()))
		# check if buy or sell then add to approporiate tree
		if event.direction == 1:
			self.buy.handleNewOrder(new_order)
		elif event.direction == -1:
			self.sell.handleNewOrder(new_order)
		# update NBBO
		self.updateNbbo(new_order)

	def cancelationOfExistingLimitOrder(self, event):
		# get the ID of the order to partially cancel and get the order from the dict
		order_to_cancel = self.orders.get(event.order_id)
		shares_to_subtract_from_limit_total = event.shares
		if (order_to_cancel is not None) & (order_to_cancel.shares != 0):
			logging.info("Canceling {} shares for ID {} at {} in {} tree".format(shares_to_subtract_from_limit_total, order_to_cancel.id, order_to_cancel.price, order_to_cancel.getDirection()))
			if order_to_cancel.direction == 1:
				self.buy.handleCancellation(order_to_cancel, shares_to_subtract_from_limit_total)
			elif order_to_cancel.direction == -1:
				self.sell.handleCancellation(order_to_cancel, shares_to_subtract_from_limit_total)
			# reduce the number of shares at this order by those in the event 
			order_to_cancel.shares = order_to_cancel.shares - shares_to_subtract_from_limit_total
			# update the order in the dict
			self.orders[order_to_cancel.id] = order_to_cancel
			# edit the number of total shares at that level in the book
			logging.info("ID {} has {} shares remaining".format(order_to_cancel.id, order_to_cancel.shares))
		else:
			logging.info("ID {} does not exist".format(event.order_id))

	def deletionOfExistingLimitOrder(self, event):
		# get the ID of the order to delete and get the order from the dict
		order_to_delete = self.orders.get(event.order_id)
		# check if order exists
		if order_to_delete is not None:
			# pass order to book to delete from relevant queue
			logging.info("Deleting ID {} at {} from queue in {} tree".format(order_to_delete.id, order_to_delete.price, order_to_delete.getDirection()))
			if order_to_delete.direction == 1:
				self.buy.handleDeletion(order_to_delete)
			elif order_to_delete.direction == -1:
				self.sell.handleDeletion(order_to_delete)
		else:
			logging.info("ID {} does not exist".format(event.order_id))

	def orderExecution(self, event):
		# get id of order to execute and num shares to execute
		order_to_execute = self.orders.get(event.order_id)
		shares_traded = event.shares
		if order_to_execute is not None:
			logging.info("Executing {} shares for ID {} at {} in {} tree".format(shares_traded, order_to_execute.id, order_to_execute.price, order_to_execute.getDirection()))
			if order_to_execute.direction == 1:
				self.buy.handleVisibleExecution(order_to_execute, shares_traded)
			elif order_to_execute.direction == -1:
				self.sell.handleVisibleExecution(order_to_execute, shares_traded)
			# get number of shares executed
			# reduce shares at ID
			order_to_execute.shares = order_to_execute.shares - shares_traded
			# update order in dict
			self.orders[order_to_execute.id] = order_to_execute
			logging.info("ID {} has {} shares remaining".format(order_to_execute.id, order_to_execute.shares))
			if order_to_execute.shares == 0:
				self.deletionOfExistingLimitOrder(event)
		else:
			logging.info("ID {} does not exist".format(event.order_id))
		
	def getNbbo(self):
		return self.best_offer.limit_price, self.best_bid.limit_price
	
	def updateNbbo(self, order):

		if order.direction == 1:
			if order.price > self.best_bid.limit_price:
				self.best_bid = self.buy.inOrderTraversal()[-1]
		else:
			if order.price < self.best_offer.limit_price:
				self.best_offer = self.sell.inOrderTraversal()[0]

	def getXLevels(self, x):
		b = self.buy.inOrderTraversal()[-x:]
		o = self.sell.inOrderTraversal()[:x]

		b = [[i.limit_price, i.total_volume, i.num_orders] for i in b]
		o = [[i.limit_price, i.total_volume, i.num_orders] for i in o]
		return [b, o]
	
	def getAllLevels(self):
		b = self.buy.inOrderTraversal()
		o = self.sell.inOrderTraversal()

		b = [[i.limit_price, i.total_volume, i.num_orders] for i in b]
		o = [[i.limit_price, i.total_volume, i.num_orders] for i in o]
		return [b, o]
	
	def fillLevels(self):
		
		pass