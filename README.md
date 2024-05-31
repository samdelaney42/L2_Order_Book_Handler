# L2_Order_Book_Handler
This project parses message data form the LOBSTER data set and constructs an order book.

Using the AAPL 50 level sample data message supplied here https://lobsterdata.com/info/DataSamples.php

We read the message file into order_book.py and recreate the order book over the period.

To accurately recreate the LOBSTER L1 order book output, record each event which is in both the 50 and 1 message file.

We then filter our 50 depth order book output using the index recorded - for the 20k messages we test with, there is a 0.3% error rate.

You can find the demonstration of the below in the Lobster_comparison notebok

![LOBSTER Comparison]([https://github.com/samdelaney42/L2_Order_Book_Handler/blob/b8606a64775bd9d5d43931b69a1ef424b90f3d74/data/images/comparison.png])
    
