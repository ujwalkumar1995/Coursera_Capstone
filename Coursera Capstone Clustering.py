#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
website_url = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text


# In[2]:


from bs4 import BeautifulSoup
soup = BeautifulSoup(website_url,'lxml')
print(soup.prettify())


# In[3]:


My_table = soup.find('table',{'class':'wikitable sortable'})


# In[4]:


content = My_table.findAll('td')  


# In[5]:


list1 = []
list2 = []
list3 = []
for i in range(0,len(content)):
    if((i+1) % 3 == 0):
        list3.append(content[i].getText('Title'));
    elif((i) % 3 == 0):
        list1.append(content[i].getText('Title'));
    else:
        list2.append(content[i].getText('Title'));    


# In[6]:


newList1 = []
newList2 = []
newList3 = []
for i in range(0, len(list2)):
    if(list2[i] != 'Not assigned'):
        newList1.append(list1[i])
        newList2.append(list2[i])
        temp = list3[i].replace('\n','')
        newList3.append(temp)

for i in range(0, len(newList3)):
    if(newList3[i] == 'Not assigned'):
        newList3[i] = newList2[i]     


# In[7]:


import pandas as pd


# In[8]:


df = pd.DataFrame(newList1, columns =['PostalCode'])
df['Borough'] = newList2
df['Neighbourhood'] = newList3


# In[11]:


df


# In[12]:


df.shape


# In[ ]:




