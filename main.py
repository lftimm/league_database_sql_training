from OpGGParser import OpGGParser
from datetime import date
import os
import json

def dataset_to_json(dataset, page, today, file_path):
    json_dict = {
        "dataset_date": today,
        "dataset_page": f"{page}",
        "dataset": dataset
        }

    js = json.dumps(json_dict,indent=4)
    with open(file_path,"w") as f:
        f.write(js)

def clean_html():
    htmls = os.listdir("html")
    for file in htmls:
        os.remove(f"html/{file}")
    
def main(): 
    number_of_entries = 100
    today_date = f"{date.today().month}_{date.today().year}"

    dir_path = f"datasets/{today_date}"
    dir_exists = os.path.isdir(dir_path)
    if (not dir_exists):
        os.makedirs(dir_path)
    datasets_done = os.listdir(dir_path)
    
    for page in range(1,number_of_entries+1):
        file_name = f"opgg_br_page={page}_date={today_date}.json"
        if file_name in datasets_done: continue
        print(f"doing {file_name}")
        op_gg_parser = OpGGParser("br", page)
        html = op_gg_parser.request_html_text()
        dataset = op_gg_parser.parse_html(html)
        dataset_to_json(dataset, page, today_date, f"{dir_path}/{file_name}")
        
    finished = len(os.listdir(f"datasets/{today_date}"))  ==  number_of_entries
    if(finished):
        clean_html()
      
if __name__ == "__main__":
    main()