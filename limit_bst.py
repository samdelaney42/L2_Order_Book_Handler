import level_linked_list as ll
from order_obj import Order
import logging

class BinarySearchTree:
    
    def __init__(self, order_price=None):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.limit_price = order_price
        self.num_orders = 0
        self.total_volume = 0
        self.left_child = None
        self.right_child = None
        self.parent = None
        self.order_queue = ll.LinkedList()

### Event handlers

    def handleNewOrder(self, new_order):
        """
        To add an order we need to know:
        - is there an existing limit price at this level?
            - yes --> add to end of queue
            - no --> add a new limit to the tree and set this order at head of the queue
        """
        if self.checkLimit(new_order.price):
            limit_to_add_order = self.getLimit(new_order.price)
            limit_to_add_order.addOrderHelper(new_order)
        else:
            self.addLimit(new_order)

    def handleCancellation(self, order_to_cancel, shares_to_subtract_from_limit_total):
        """
        To cancel shares for a given order:
        - we have reduced in the order object when the event is recieved
        - now we just update the book total
        """
        if self.checkLimit(order_to_cancel.price):
            limit_to_cancel_order = self.getLimit(order_to_cancel.price)
            limit_to_cancel_order.cancelOrderHelper(shares_to_subtract_from_limit_total)
        else:
            logging.debug("Limit {} does not exist".format(order_to_cancel.price))

    def handleDeletion(self, order_to_delete):
        """
        To delete an order
        - get the correct limit price and head of the queue
        - search the queue and remove the order with that ID
        - reduce num orders & total volume
        """
        if self.checkLimit(order_to_delete.price):
            limit_to_delete_order = self.getLimit(order_to_delete.price)
            limit_to_delete_order.deleteOrderHelper(order_to_delete)
            if (limit_to_delete_order.total_volume == 0) & (limit_to_delete_order.num_orders == 0):
                self.deleteLimit(limit_to_delete_order.limit_price)
                logging.info("Limit {} deleted from book".format(limit_to_delete_order.limit_price))
        else:
            logging.debug("Limit {} does not exist".format(order_to_delete.price))

    def handleVisibleExecution(self, order_to_execute, shares_executed):
        """
        To execute shares for a given order:
        - we have reduced in the order object when the event is recieved
        - now we just update the book total
        """
        if self.checkLimit(order_to_execute.price):
            limit_to_execute_order = self.getLimit(order_to_execute.price)
            limit_to_execute_order.executeOrderHelper(shares_executed)
        else:
            logging.debug("Limit {} does not exist".format(order_to_execute.price))

### Helper Functions

    def addOrderHelper(self, new_order):
        self.addOrderToQueue(new_order)
        self.increaseVolumeAtLimit(new_order.shares)
        self.increaseNumOrdersAtLimit()

    def cancelOrderHelper(self, shares_to_cancel):
        self.reduceVolumeAtLimit(shares_to_cancel)

    def deleteOrderHelper(self, order_to_delete):
        self.deleteOrderFromQueue(order_to_delete)
        self.reduceVolumeAtLimit(order_to_delete.shares)
        self.reduceNumOrdersAtLimit()

    def executeOrderHelper(self, shares_to_execute):
        self.reduceVolumeAtLimit(shares_to_execute)

### Attribute change functions

    def addLimit(self, new_order):
        """
        Navigate to the node that will be the parent node
        - Create new limit node as a child and add an order to it 
        """
        if new_order.price < self.limit_price:
            if self.left_child is not None:
                self.left_child.addLimit(new_order)
            else:
                logging.info("Creating new limit")
                self.left_child = BinarySearchTree(new_order.price)
                self.left_child.addOrderHelper(new_order)
                self.left_child.parent = self
                return
        if new_order.price > self.limit_price:
            if self.right_child is not None:
                self.right_child.addLimit(new_order)
            else:
                logging.info("Creating new limit")
                self.right_child = BinarySearchTree(new_order.price)
                self.right_child.addOrderHelper(new_order)
                self.right_child.parent = self
                return
            
    def deleteLimit(self, limit):
        # Find the node in the left subtree if the limit is less than root value
        if limit < self.limit_price:
            self.left_child = self.left_child.deleteLimit(limit)
        # Find the node in the right subtree if the limit is greater than root value
        elif limit > self.limit_price:
            self.right_child = self.right_child.deleteLimit(limit)
        # Delete the node if root.value == limit
        else: 
            # Case 1: Node has no child or only one child
            if not self.right_child:
                return self.left_child
            elif not self.left_child:
                return self.right_child
            # Case 2: Node has two children
            # Find the in-order predecessor (maximum value in the left subtree)
            temp_val = self.right_child
            while temp_val.left_child:
                temp_val = temp_val.left_child
            # Update the current node val with the successor val
            self.limit_price = temp_val.limit_price
            self.num_orders = temp_val.num_orders
            self.total_volume = temp_val.total_volume
            self.order_queue = temp_val.order_queue
            # Delete the in-order predecessor from the left subtree
            self.right_child = self.right_child.deleteLimit(temp_val.limit_price)
        return self

    def addOrderToQueue(self, new_order):
        self.order_queue.addOrder(new_order)
        return
    
    def deleteOrderFromQueue(self, order_to_delete):
        self.order_queue.deleteOrder(order_to_delete)
        return
    
    def reduceVolumeAtLimit(self, shares):
        self.total_volume = self.total_volume - shares
        logging.info("Total vol at {} has been reduced by {}".format(self.limit_price, shares))
    
    def increaseVolumeAtLimit(self, shares):
        self.total_volume = self.total_volume + shares
        logging.info("Total vol at {} has been increased by {}".format(self.limit_price, shares))

    def reduceNumOrdersAtLimit(self):
        self.num_orders = self.num_orders - 1
        logging.info("Num orders at {} has been reduced by 1".format(self.limit_price))

    def increaseNumOrdersAtLimit(self):
        self.num_orders = self.num_orders + 1
        logging.info("Num orders at {} has been increased by 1".format(self.limit_price))

### Misc Functions

    def checkLimit(self, limit):
        if limit == self.limit_price:
            logging.info('limit {} exists'.format(limit))
            return True
        if (limit < self.limit_price) & (self.left_child is not None):
            return self.left_child.checkLimit(limit)
        elif (limit > self.limit_price) & (self.right_child is not None):
            return self.right_child.checkLimit(limit)
        else:
            logging.info('limit {} does not exist'.format(limit))
            return False
        
    def getLimit(self, limit):
        if limit == self.limit_price:
            return self
        if (limit < self.limit_price) & (self.left_child is not None):
            return self.left_child.getLimit(limit)
        elif (limit > self.limit_price) & (self.right_child is not None):
            return self.right_child.getLimit(limit)
        else:
            return False

    def inOrderTraversal(self):
        elements = []
        if self.left_child:
            elements += self.left_child.inOrderTraversal()
        if self.num_orders != 0:
            elements.append(self)
        if self.right_child:
            elements += self.right_child.inOrderTraversal()
        return elements
