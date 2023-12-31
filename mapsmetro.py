import folium, io, json, sys, math, random, os
import psycopg2
from folium.plugins import Draw, MousePosition, MeasureControl
from jinja2 import Template
from branca.element import Element
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.coord_transp=[]
        
        self.resize(600, 600)
        self.conno=0
        main = QWidget()
        self.setCentralWidget(main)
        main.setLayout(QVBoxLayout())
        main.setFocusPolicy(Qt.StrongFocus)

        self.tableWidget = QTableWidget()
        self.tableWidget.doubleClicked.connect(self.table_Click)
        self.rows = []

        self.webView = myWebView()
		
        controls_panel = QHBoxLayout()
        mysplit = QSplitter(Qt.Vertical)
        mysplit.addWidget(self.tableWidget)
        mysplit.addWidget(self.webView)

        main.layout().addLayout(controls_panel)
        main.layout().addWidget(mysplit)

        _label = QLabel('From: ', self)
        _label.setFixedSize(30,20)
        self.from_box = QComboBox() 
        self.from_box.setEditable(True)
        self.from_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.from_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.from_box)

        _label = QLabel('  To: ', self)
        _label.setFixedSize(20,20)
        self.to_box = QComboBox() 
        self.to_box.setEditable(True)
        self.to_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.to_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.to_box)

        _label = QLabel('Hops: ', self)
        _label.setFixedSize(20,20)
        self.hop_box = QComboBox() 
        self.hop_box.addItems( ['1', '2', '3', '4', '5'] )
        self.hop_box.setCurrentIndex( 0 )
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.hop_box)

        self.go_button = QPushButton("Go!")
        self.go_button.clicked.connect(self.button_Go)
        controls_panel.addWidget(self.go_button)
           
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.button_Clear)
        controls_panel.addWidget(self.clear_button)

        self.maptype_box = QComboBox()
        self.maptype_box.addItems(self.webView.maptypes)
        self.maptype_box.currentIndexChanged.connect(self.webView.setMap)
        controls_panel.addWidget(self.maptype_box)
           
        self.connect_DB()

        self.startingpoint = True
                   
        self.show()
        

    def connect_DB(self):
        self.conn = psycopg2.connect(database="l3info_58", user="l3info_58", host="10.11.11.22", password="L3INFO_58")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""SELECT distinct name FROM stations_toulouse ORDER BY name""")
        self.conn.commit()
        rows = self.cursor.fetchall()

        for row in rows : 
            self.from_box.addItem(str(row[0]))
            self.to_box.addItem(str(row[0]))


    def table_Click(self):
        print("Row number double-clicked: ", self.tableWidget.currentRow())
        print(self.coord_transp)
        print(self.coord_transp[0][0][0])
        for i in range(len(self.coord_transp[0])):
                       self.webView.addSegment(self.coord_transp[0][i][0], self.coord_transp[0][i][1],self.coord_transp[0][i][2],self.coord_transp[0][i][3])
                       print(self.coord_transp[0][i][0], self.coord_transp[0][i][1],self.coord_transp[0][i][2],self.coord_transp[0][i][3])
        self.update()


    def button_Go(self):
        self.tableWidget.clearContents()

        _fromstation = str(self.from_box.currentText())
        _tostation = str(self.to_box.currentText())
        _hops = int(self.hop_box.currentText())

        self.rows = []
        self.coord_transp=[]

        if (_hops==1):
        	self.cursor.execute(""f"SELECT DISTINCT m1.nom_long, m2.res_com, m2.nom_long FROM metros as m1, metros as m2 WHERE m1.nom_long='{_fromstation}' AND m2.nom_long='{_tostation}'""")
        	self.conn.commit()
        	self.rows += self.cursor.fetchall()
        	self.cursor.execute(""f"SELECT DISTINCT m1.longitude, m1.latitude,  m2.longitude, m2.latitude FROM metros as m1, metros as m2 WHERE m1.nom_long='{_fromstation}' AND m2.nom_long='{_tostation}'""")
        	self.conn.commit()
        	self.coord_transp.append(self.cursor.fetchall())
        	
        	
        if (_hops == 2) : 
            self.cursor.execute(""f" SELECT distinct A.nom_long, A.res_com, B.nom_long, C.res_com,  D.nom_long FROM metros as A, metros as B, metros as C, metros as D WHERE A.nom_long = $${_fromstation}$$ AND D.nom_long = $${_tostation}$$ AND A.res_com = B.res_com AND B.nom_long = C.nom_long AND C.res_com = D.res_com AND A.res_com <> C.res_com AND A.nom_long <> B.nom_long AND B.nom_long <> D.nom_long""")
            self.conn.commit()
            self.rows += self.cursor.fetchall()
            self.cursor.execute(""f"SELECT distinct A.longitude,A.latitude, B.longitude, B.latitude, D.longitude, D.latitude FROM metros as A, metros as B, metros as C, metros as D WHERE A.nom_long = $${_fromstation}$$ AND D.nom_long = $${_tostation}$$ AND A.res_com = B.res_com AND B.nom_long = C.nom_long AND C.res_com = D.res_com AND A.res_com <> C.res_com AND A.nom_long <> B.nom_long AND B.nom_long <> D.nom_long""")
            self.conn.commit()
            self.coord_transp.append(self.cursor.fetchall())
            print(self.coord_transp)

        if (_hops == 3) : 
            self.cursor.execute(""f" SELECT distinct A.nom_long, A.res_com, B2.nom_long, B2.res_com, C2.nom_long, C2.res_com, D.nom_long FROM metros as A, metros as B1, metros as B2, metros as C1, metros as C2, metros as D WHERE A.nom_long = $${_fromstation}$$ AND A.res_com = B1.res_com AND B1.nom_long = B2.nom_long AND B2.res_com = C1.res_com AND C1.nom_long = C2.nom_long AND C2.res_com = D.res_com AND D.nom_long = $${_tostation}$$ AND A.res_com <> B2.res_com AND B2.res_com <> C2.res_com AND A.res_com <> C2.res_com AND A.nom_long <> B1.nom_long AND B2.nom_long <> C1.nom_long AND C2.nom_long <> D.nom_long""")

            self.cursor.execute(""f" SELECT distinct A.longitude, A.latitude, B2.longitude, B2.latitude, C2.longitude, C2.latitude, D.longitude, D.latitude FROM metros as A, metros as B1, metros as B2, metros as C1, metros as C2, metros as D WHERE A.nom_long = $${_fromstation}$$ AND A.res_com = B1.res_com AND B1.nom_long = B2.nom_long AND B2.res_com = C1.res_com AND C1.nom_long = C2.nom_long AND C2.res_com = D.res_com AND D.nom_long = $${_tostation}$$ AND A.res_com <> B2.res_com AND B2.res_com <> C2.res_com AND A.res_com <> C2.res_com AND A.nom_long <> B1.nom_long AND B2.nom_long <> C1.nom_long AND C2.nom_long <> D.nom_long""")
            self.conn.commit()
            self.coord_transp.append(self.cursor.fetchall())
            

        if len(self.rows) == 0 : 
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return 

        numrows = len(self.rows)
        numcols = len(self.rows[-1])
        self.tableWidget.setRowCount(numrows)
        self.tableWidget.setColumnCount(numcols)

        i = 0
        for row in self.rows : 
            j = 0
            for col in row :
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(col)))
                j = j + 1
            i = i + 1
            print(row)

        header = self.tableWidget.horizontalHeader()
        j = 0
        while j < numcols : 
            header.setSectionResizeMode(j, QHeaderView.ResizeToContents)
            j = j+1
        self.table_Click()
        self.update()	


    def button_Clear(self):
        self.webView.clearMap(self.maptype_box.currentIndex())
        self.startingpoint = True
        self.update()


    def mouseClick(self, lat, lng):
        self.webView.addPoint(lat, lng)

        print(f"Clicked on: latitude {lat}, longitude {lng}")
        self.cursor.execute(""f"SELECT nom_long  FROM metros WHERE sqrt(power(latitude-{lat}, 2) + power(longitude-{lng}, 2))=(SELECT min(sqrt(power(latitude-{lat}, 2) + power(longitude-{lng}, 2))) FROM metros)""")
        self.webView.addPoint(lat, lng)
        self.conn.commit()
        myrows = self.cursor.fetchall()
        print(myrows)
        index = 0
        if (self.conno<=1):
                self.from_box.setCurrentIndex(self.from_box.findText(myrows[index][0], Qt.MatchFixedString))
                self.conno+=2
        else:
                self.to_box.setCurrentIndex(self.to_box.findText(myrows[index][0], Qt.MatchFixedString))
                self.conno=0
        print(self.conno)
class myWebView (QWebEngineView):
    def __init__(self):
        super().__init__()

        self.maptypes = ["OpenStreetMap", "Stamen Terrain", "stamentoner", "cartodbpositron"]
        self.setMap(0)


    def add_customjs(self, map_object):
        my_js = f"""{map_object.get_name()}.on("click",
                 function (e) {{
                    var data = `{{"coordinates": ${{JSON.stringify(e.latlng)}}}}`;
                    console.log(data)}}); """
        e = Element(my_js)
        html = map_object.get_root()
        html.script.get_root().render()
        html.script._children[e.get_name()] = e

        return map_object


    def handleClick(self, msg):
        data = json.loads(msg)
        lat = data['coordinates']['lat']
        lng = data['coordinates']['lng']

        window.mouseClick(lat, lng)


    def addSegment(self, lat1, lng1, lat2, lng2):
        js = Template(
        """
        L.polyline(
            [ [{{latitude1}}, {{longitude1}}], [{{latitude2}}, {{longitude2}}] ], {
                "color": "red",
                "opacity": 1.0,
                "weight": 4,
                "line_cap": "butt"
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude1=lat1, longitude1=lng1, latitude2=lat2, longitude2=lng2 )

        self.page().runJavaScript(js)


    def addMarker(self, lat, lng):
        js = Template(
        """
        L.marker([{{latitude}}, {{longitude}}] ).addTo({{map}});
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": "#3388ff",
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "#3388ff",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def addPoint(self, lat, lng):
        js = Template(
        """
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": 'green',
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": 'green',
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def setMap (self, i):
        self.mymap = folium.Map(location=[48.8619, 2.3519], tiles=self.maptypes[i], zoom_start=12, prefer_canvas=True)

        self.mymap = self.add_customjs(self.mymap)

        page = WebEnginePage(self)
        self.setPage(page)

        data = io.BytesIO()
        self.mymap.save(data, close_file=False)

        self.setHtml(data.getvalue().decode())

    def clearMap(self, index):
        self.setMap(index)



class WebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        #print(msg)
        if 'coordinates' in msg:
            self.parent.handleClick(msg)


       
			
if __name__ == '__main__':
    app = QApplication(sys.argv) 
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
