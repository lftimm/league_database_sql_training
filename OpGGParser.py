from datetime import date
import requests
from pathlib import Path
import os
from typing import Optional, List
from bs4 import BeautifulSoup

class OpGGParser:    
    def __init__(self, region: str, page: int) -> None:
            base_url: str = "https://www.op.gg/leaderboards/tier"
            self.region: str = f"?region={region}"
            self.page: str = f"&page={page}"
            self.url: str = f"{base_url}{self.region}{self.page}"

    def request_html_text(self, save: Optional[bool] = True):
        file_name = f"opgg_{self.region.split("=")[-1]}_{self.page.split("&")[-1]}.html"
        file_path = f"html/{file_name}"
        if os.path.exists(file_path):
            return self.__read_html_text_from_file(file_path)
            
        page = requests.get(self.url)
        if(not page.ok):
            raise Exception(f"ERROR REQUESTING:{page}")
        
        parsed_html = BeautifulSoup(page.content, "html.parser")
        if(save):
            with open(file_path,'w', encoding="utf-8") as file:
                file.write(str(parsed_html))

        return parsed_html
    
    def __read_html_text_from_file(self,file_path: str) -> BeautifulSoup:
        print("DEBUG:[Reading From File]")
        with open(file_path,encoding="utf-8") as f:
            return BeautifulSoup(f,"html.parser")

    @staticmethod
    def parse_html(soup: BeautifulSoup):
        return_list = []
        all_players = soup.find_all("tr", class_="css-rmp2x6 e1br5d0")
        all_three_champs = soup.findAll("td", class_="css-624em4 e1br5d8")
        all_matches = soup.findAll("td", class_="css-1ex2x1n e1br5d7")
        all_elos = soup.findAll("td", class_="css-13jn5d5 e1br5d3")        

        check_if_null = lambda x: x if x is not None and x != '' else None

        for i in range(0, len(all_players)):
            player_dict = {}
            incomplete = False
            
            player_name = check_if_null(all_players[i].find("a", class_="summoner-link").find("div").findAll("span")[0].text)
            player_tag = check_if_null(all_players[i].find("a", class_="summoner-link").find("div").findAll("span")[1].text)

            player_wr = check_if_null(all_matches[i].text.split("L")[1].split("%")[0])
            player_w = check_if_null(all_matches[i].text.split("W")[0])
            player_l = check_if_null(all_matches[i].text.split("W")[1].split("L")[0])
            player_elo = check_if_null(all_elos[i].text)
            
            if player_name: 
                player_dict["name"] = player_name
            else:
                incomplete = True

            if player_tag: 
                player_dict["tag"] = player_tag
            else:
                incomplete = True

            if player_w: 
                player_dict["w"] = player_w
            else:
                incomplete = True

            if player_l: 
                player_dict["l"] = player_l
            else:
                incomplete = True

            if player_wr: 
                player_dict["wr"] = player_wr
            else:
                incomplete = True

            if player_elo: 
                player_dict["elo"] = player_elo
            else:
                incomplete = True
        
            try:
                # Safely check if the 'a' tag exists before trying to access its attributes
                player_first_champ = all_three_champs[i].a["href"].split("/")[-2] if all_three_champs[i].a else None
                player_second_champ = all_three_champs[i].a.next_sibling["href"].split("/")[-2] if all_three_champs[i].a and all_three_champs[i].a.next_sibling else None
                player_third_champ = all_three_champs[i].a.next_sibling.next_sibling["href"].split("/")[-2] if all_three_champs[i].a and all_three_champs[i].a.next_sibling and all_three_champs[i].a.next_sibling.next_sibling else None

                # Add these to the player dictionary, and mark incomplete if any are missing
                player_dict["first_champ"] = check_if_null(player_first_champ)
                player_dict["second_champ"] = check_if_null(player_second_champ)
                player_dict["third_champ"] = check_if_null(player_third_champ)

                if not player_first_champ or not player_second_champ or not player_third_champ:
                    incomplete = True  # Mark the player as incomplete if any champ data is missing
            except Exception as e:
                print(f"Error processing champion data for player: {player_name}, {e}")
                incomplete = True  # If any error occurs, mark the player as incomplete

            player_dict["incomplete"] = incomplete

            return_list.append(player_dict)

        return return_list