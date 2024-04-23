# L2_Order_Book_Handler
This project parses message data form the LOBSTER data set and constructs an order book.

Using the AAPL 50 level sample data supplied here https://lobsterdata.com/info/DataSamples.php

We are able to to construct what looks like a relativley accurate version of the BBO:
![AAPL_BBO_LOBSTER_Comparison](https://github.com/samdelaney42/L2_Order_Book_Handler/assets/45703559/2ac2a8fb-4b50-4d27-81e8-5063dbb0b428)

To do: 

    - We currently output the current state of the book after every event message is handled
    
    - This means, there may be duplicate rows in the order book output (top 5 levels)
    
    - As we can see based on the graphical comparison, our x axis is significantly larger
    
