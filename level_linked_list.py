# this is a doubly linked list class
# when instantiated, each linked list object will reflect a string of orders
# at a given level in the order book
# here we use the Order class as the node itself

from order_obj import Order
import logging

class LinkedList:

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        self.head = None
        self.tail = None

    def addOrder(self, new_order):
        if self.head is None:
            self.head = new_order
            self.tail = new_order
            logging.info("${} limit created, ID: {} is head".format(new_order.price, new_order.id))
            return
        elif self.head.next is None:
            self.head.next = new_order
            self.tail = new_order
            logging.info("${} has {} as head, {} is 2nd in the queue".format(new_order.price, self.head.id, new_order.id))
            return
        else:
            current_node = self.head
            while current_node.next:
                current_node = current_node.next
            current_node.next = new_order
            new_order.prev = current_node
            self.tail = new_order
            logging.info("${} has added ID {} to the back of the queue".format(new_order.price, new_order.id))
            return 
  
    def deleteOrder(self, order_to_delete):
        if self.head is None or order_to_delete is None:
            return
        
        if self.head.id == order_to_delete.id:
            self.head = order_to_delete.next

        if order_to_delete.next is not None:
            order_to_delete.next.prev = order_to_delete.prev

        if order_to_delete.prev is not None:
            order_to_delete.prev.next = order_to_delete.next
        
        logging.info("Order {} deleted from ${} queue".format(order_to_delete.id, order_to_delete.price))