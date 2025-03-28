# Open_data_scraping
This repository contains scripts for collecting data from open sources of information
Lower will be gemeral information about each one.

# scrapper_opendata_ubki.py
Script, firstly, takes data about enterprices from https://opendatabot.ua/ for hromada level (but you can easily change it), then, search adderss for each enterprice and saving everything into excel file with columns:
- name - name of enterprice;
- edrpou_code - code of Unified State Register of Enterprises and Organizations of Ukraine;
- activity - main activity of the company (Classifier of types of economic activity);
- income_2024 ;
- number_of_employees;
- address;
- ADM4_name - name of settlement.

For using you should:
- link to the first page of hromada from opendatabot.ua into link_hromada (https://opendatabot.ua/c/UA12020030000073022);
- offeset maximun number into offset_max (you can take it at the end of last page link - https://opendatabot.ua/c/UA12020030000073022?offset=48);
- put the name of your excel file into enterprices_file.


# elevators_news_bs4.py
