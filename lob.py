import sys
import angellist
import json

class Lob(object) :

#TODO: validation, separate class? 

#TODO: list properties here?
#TODO: separate ranking class?

  def __init__(self, token) :
    self.access_token = token
    #TODO: json field?

  #TODO: get json file path for candidate attributes
  def get_input(self):

    # response = raw_input("Please enter your name : ")
    # ss = raw_input("Please enter your social security : ") 
    # print response, ss
    #loop til we open json file with no error
    pass 

  def angel_list(self) :
    pass

  #get id's and skill information of each company
  #returns a dict of each company name and its id (or should I do the opposite?)
  def filter_companies(self, data):
    comp_data = {}
    startup = data["jobs"] #array of startup objects
    for e in startup:
      comp = e["startup"]
      if comp["name"] not in comp_data:
        comp_data[comp["name"]] = (comp["id"], e["tags"])

    return comp_data

  #dict that counts occurences of skills
  def count_skills(self, data):
    data = json.load(data)
    sk_count = {}
    for key, value in data.iteritems() :
      info = value[1] #non-id list
      # print info
      for tag in info : #skill is each object
        if tag["tag_type"] == "SkillTag" :
          if tag["name"] not in sk_count :
            sk_count[tag["name"]] = 1
          else :
            sk_count[tag["name"]] += 1
        else :
          continue
    return sk_count

if __name__ == '__main__':
  #TODO: use a db to hide credentials?
  #i might just hash it

  al = angellist.AngelList()
  al.client_id = 'fe4a1fb11ab1a4e0a9595b9c31e7f366af494f1bc0de05e7'
  al.access_token = '94ece8695020668b807e8b19d2028be7f1a7bbe43546f9dd'
  al.client_secret = '3021d52bd5941d2de685c96a03ce056f0b002dcd9ffff9c2'
  # auth_url = al.getAuthorizeURL()

  # job = al.getJobByTag(al.access_token, '14766')

  lobsta = Lob(al.access_token)
  #cache the json
  #TODO: more pages? it seems my file is only one page
  #apparently there are page and per_page parameters
  with open('jobtag.json') as data_file:    
      data = json.load(data_file)
      # json.dumps(lobsta.filter_companies(data))
  with open('comp.json') as skill_file:
      print json.dumps(lobsta.count_skills(skill_file))
