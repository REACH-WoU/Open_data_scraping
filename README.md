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
Script is taking news from https://tripoli.land/ua with pictures for each.
After running it you will have the output with folder with images and excel file with columns:
- ID - unique id of each news;
- Title;
- Publication Date;
- Text;
- Image File - the name of image file (the same number as ID);
- Link.

For using you should:

- Name te image folder (into image_folder)
- Select news category name from list and put into category (if you need take all news change to the second base link):
Зерно - zerno, 
Сільгосптехніка - selhoztehnika,
Елеватори - elevatory,
Тваринництво - zhivotnovodstvo,
Компанії - kompanii,
Агрономія - agronomiya,
Транспорт - transport,
Світ - mir,
Загальні - ukraina
- Indicate the number of the last page with news into last_page,
- Name the output file (file_name)

# data_isuo.py

Script taking data for education facilities for hromada from https://isuo.org/.
As a result of running script you will have excel file with max 5 sheets:
- Sheet 1 - general information about education department of hromada;
- Schools;
- Kindergartens;
- Out of school intitutions;
- Inclusive centers.

For using you should:
- Find you hromada on ISUO;
- Put the name of oblast level education department into oblast (like ДОН Дніпропетровської ОДА);
- Put tne name of hromada level education department into hromada (like Царичанська СТГ)
- Name your output file (file_name)
