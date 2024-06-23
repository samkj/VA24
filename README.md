# VA24
The repository for Visual Analytics Course SS24.
scripts/: This folder stores Python scripts for data collection, processing, cleaning, and creating visualizations.

requirements.txt: This file contains the required Python packages for the project.

Structure:
+---backend 
|   |   app.py                          # !Start the application here!
|   |   callbacks.py                    
|   |   layout.py
|   +---data                            # holds map data for interactive map
|   +---services
|   |   |   data_service.py   
|  
+---out                                 # holds output csv from sentiment analysis
|
+---scripts
|       BERT_Sentiment.py               # performs BERT sentiment analysis
|       BERT_Sentiment_german.py      # performs BERT in german
|       clean_data.py                   # Data cleaning and preprocessing
|       network.py                      # Generates the html files for the network view
|       preload_model_network.py        # Loads and trains the model for classification for network view
|       Reddit_data.py              
|       test_state.py   
|       VADER_Sentiment.py              # different sentiment analysis
|
+---subreddits_datafiles                # raw data
|   +---all data_sentiment              # cleaned data with sentiment
|   +---processed_datafiles             # cleaned data
|   +---processed_datafiles_sentiment   # clenaed data with sentiment separated by state
|
+---view                                # visual analysis output

How to use:
+ Collect data with praw from reddit
+ Run in order for preprocessing (optional, only necessary for new data):
    - Reddit_data.py
    - clean_data.py
    - BERT_Sentiment.py
    - BERT_Sentimen_german.py
    - VADER_Sentiment.py
    - preload_model_network.py
    - network.py
+ To run broweser view:
    - run "python ./backend/app.py" from main folder
    - click on the link printed in console
