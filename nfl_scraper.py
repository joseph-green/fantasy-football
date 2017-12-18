from urllib.request import *
from urllib.error import *
import re
import sqlite3


def clean_statline(sl):
	temp = sl
	temp.pop(9)
	temp.pop(6)
	temp.pop(5)
	
	#account for players without listed teams (i.e. played for 2 teams)
	#insert two extra items to accomodate for lost <a> tags
	if sl[6] == '':
		sl.insert(5,'')
		sl.insert(7,'')
	return temp[4::2]

def existing_player(p,l):
	for i in l:
		if p[0] == i[0]:
			return True
	return False

def insert_indexes(a,b,indexes):

	l_orig = len(b[0])

	for r in a:

		in_list = False
		#search through all items in the data entry list
		#insert stats if the names match
		for l in b:
			if r[0] == l[0]:
				for i in indexes:
					l.append(r[i])
				in_list = True

		#if the player is not found, add to the end of the list 
		if not in_list:
			b.append([r[0],r[1],r[3]] + [0 for i in range(0,l_orig-3)])
			for i in indexes:
				b[-1].append(r[i])

	#add null stats for any members of compressed list
	for i in b:
		if len(i) == l_orig:
			i += [0 for i in range(0,len(indexes))]

def compress_de(de):

	temp = []
	
	#insert passing stats
	for r in de[0]:
		temp.append([r[0],r[1],r[3],r[10],r[11],r[13]])

	#insert rushing stats
	insert_indexes(de[1],temp,[7,8,-1])	

	#insert receiving stats
	insert_indexes(de[2],temp,[9,11])

	#insert kicking stats
	insert_indexes(de[3],temp,[17,20])

	#insert defense stats
	insert_indexes(de[4],temp,[17,19,6,13,8])

	return temp

#cleaning function for name
#gets rid of double backslash characters
def clean_name(n):

	temp = []
	chars = list(n)
	for c in chars:
		if not c == "\\":
			temp.append(c)
	return "".join(temp)

#cleaning function for position
#gets rid of double positions and lowercase values
def clean_pos(n):

	if n == "":
		return "NP"
	elif re.match(r"[a-zA-Z]{1,3}",n):
		f_pos = re.search(r"[a-zA-Z]{1,3}",n).group(0)
		return f_pos.upper()
	else:
		return n.upper()

#cleaning function for stats
def clean_stat(n):

	if n == "":
		return 0
	elif type(n) == str:
		return int(n)
	else:
		return n


	
#cleaning function for data row
def clean_de(de):

	temp = de

	for entry in temp:

		#clean name/team
		#append to new list
		entry[0] = clean_name(entry[0])

		entry[2] = clean_pos(entry[2])

		entry[3::] = [clean_stat(i) for i in entry[3::]]

	return temp






urls = ["https://www.pro-football-reference.com/years/2017/passing.htm", "https://www.pro-football-reference.com/years/2017/rushing.htm", "https://www.pro-football-reference.com/years/2017/receiving.htm", "https://www.pro-football-reference.com/years/2017/kicking.htm", "https://www.pro-football-reference.com/years/2017/defense.htm"] 
data_entries = []

for url in urls:

	#get html from pro-football-reference
	src_html = str(urlopen(url).read())

	#get table containing passing stats
	src_table = re.search(r"(?<=<tbody>\\n<tr).+</tbody>",src_html)
	data_rows = re.split(r"</tr>",src_table.group(0))

	#filter out all results that are not player statlines
	data_rows_cl = [clean_statline(re.findall(r">([^\<]*)<",i)) for i in data_rows if re.search(r"data-stat",i) and not re.search(r'<tr class="thead">',i)]

	#push into temporary data entries list
	data_entries.append(data_rows_cl)

#compress and clean data
comp_data_entries = compress_de(data_entries)
data_entries_cl = clean_de(comp_data_entries)

#update data base
conn = sqlite3.connect("player_stats.db")
c = conn.cursor()

#create a new table if it doesn't exist already
c.execute("""CREATE TABLE IF NOT EXISTS player_stats (
	id integer primary key autoincrement, 
	name varchar(255) not null, team varchar(7) not null,
	position varchar(7) not null, pass_yds int default 0,
	pass_tds int default 0, pass_ints int default 0, 
	rush_yds int default 0, rush_tds int default 0, 
	rush_fums int default 0, rec_yds int default 0, 
	rec_tds int default 0, fg_made int default 0, 
	fg_missed int default 0, xp_made int default 0, 
	xp_missed int default 0, def_sacks int default 0, def_safeties int default 0, 
	def_ints int default 0, def_fums int default 0);""")


#update all 
for de in data_entries_cl:
	c.execute("""INSERT OR IGNORE INTO player_stats VALUES(1, "{de[0]}","{de[1]}","{de[2]}","{de[3]}","{de[4]}","{de[5]}","{de[6]}","{de[7]}","{de[8]}","{de[9]}","{de[10]}","{de[11]}","{de[12]}","{de[13]}","{de[14]}","{de[15]}","{de[16]}","{de[17]}","{de[18]}") 
		
		""")
	c.execute("""UPDATE player_stats SET
		pass_yds = "{de[3]}",
		pass_tds = "{de[4]}", 
		pass_ints = "{de[5]}", 
		rush_yds = "{de[6]}", 
		rush_tds = "{de[7]}", 
		rush_fums = "{de[8]}", 
		rec_yds = "{de[9]}", 
		rec_tds = "{de[10]}", 
		fg_made = "{de[11]}", 
		fg_missed = "{de[12]}", 
		xp_made = "{de[13]}", 
		xp_missed = "{de[14]}", 
		def_sacks = "{de[15]}", 
		def_safeties = "{de[16]}", 
		def_ints = "{de[17]}", 
		def_fums = "{de[18]}" """)

conn.commit()
conn.close()