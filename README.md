# L2_Order_Book_Handler
This project parses message data form the LOBSTER data set and constructs an order book.

Using the AAPL 50 level sample data message supplied here https://lobsterdata.com/info/DataSamples.php

We read the message file into order_book.py and recreate the order book over the period.

Taking only the BBO from our output, we see that visually, it looks accurate to the lobster L1 order book output.

Our version contains more events, as indicated by the x axis - this is becasue, as we are reading in the 50 level message file and trimming the output just to L1, the numebr of events corresponds to updates to all 50 levels. Whereas, per the lobster documentation, each row of the L1 book file corresponds to to a row of the L1 message file.


![AAPL_BBO_LOBSTER_Comparison](https://github.com/samdelaney42/L2_Order_Book_Handler/assets/45703559/2ac2a8fb-4b50-4d27-81e8-5063dbb0b428)
    
