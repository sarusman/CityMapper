import csv



import csv
import psycopg2


def connect_DB():
	conn = psycopg2.connect(database="l3info_58", user="l3info_58", host="10.11.11.22", password="L3INFO_58")
	cursor = conn.cursor()
	bp=0
	with open("network_nodes.csv", 'r') as f:
		cdv=csv.reader(f)
		for i in cdv:
			if bp>0:
				data=i[0].split(";")
				print(data)
				#cursor.execute("INSERT INTO stations_toulouse ( stop_I, lat, lon, name) VALUES (%s, %s, %s, %s)", (data[0], data[1], data[2], data[3]))
				#conn.commit()
			else:
				bp+=1
	cursor.close()
	conn.close()
connect_DB()
