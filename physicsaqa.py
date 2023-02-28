import requests 
import re
from bs4 import BeautifulSoup
class PhysicsAQA:
    def __init__(self) -> None:
                
        self.url = "https://www.savemyexams.co.uk/a-level/physics/aqa/-/pages/topic-questions-pdf/"

        response= requests.get(self.url).text
        self.soup = BeautifulSoup(response,features='lxml')#
        
    def collectdata(self):
        physicsaqa = {}
        slice_indexes = []
        data = []
        data = self.soup.find_all(["td"])[2:]
        for ind,td in  enumerate(data):
            if "." in td.text or "Section" in td.text:
                #print(td.text,ind)
                slice_indexes.append(ind)

        #print(len(slice_indexes))
        for ind in range(len(slice_indexes)+1):
            if ind == len(slice_indexes) -1:
                break
            
            sliceone = slice_indexes[ind]
            slicetwo = slice_indexes[ind + 1]
            chapterdata = data[sliceone:slicetwo]
            chapternum = data[sliceone:slicetwo][0].text.replace('\n','').replace('\xa0','')
            #print(sliceone,slicetwo)
            #print(data[sliceone:slicetwo])
            physicsaqa[chapternum] = {}
            for chapter in chapterdata:
                #print(chapter)
                if chapter.find("a",href=True) != None:
                    #print(chapter)
                    physicsaqa[chapternum][chapter.find("a",href=True).text.replace('\xa0','').replace('\n','').replace("\u200b","")] = chapter.find("a",href=True)["href"]
        return physicsaqa
if __name__ == "__main__":
   data =  PhysicsAQA().collectdata()

   print(data)

