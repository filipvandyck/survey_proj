#!/usr/bin/env python3
#
# mod_map.py

#requires geopandas 
#requires rtree

import sys
import os
import glob
import pandas as pd
import numpy as np

import geopandas
import folium
import webbrowser


from branca.element import Element

import myoutput as out

TEST1     = os.path.dirname(os.path.realpath(__file__)) + '/map/test1.csv'
TEST2     = os.path.dirname(os.path.realpath(__file__)) + '/map/test2.csv'
TEST3     = os.path.dirname(os.path.realpath(__file__)) + '/map/test3.csv'
TEST_BLOK = os.path.dirname(os.path.realpath(__file__)) + '/map/test_blok_pr.csv'

GEOJSONFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/map/geojson/' 
GMLFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/map/gml/' 
MAPFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/map/' 
HTMLFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/map/html/'
 


def remove_first_quote(s):
    if len(s) > 0:
        if s[:1] == "'":
            s = s[1:len(s)]
        return(s)
    else:
        return('')
   
       

def convert_gml():
    
    gmlfiles = [f for f in glob.glob(GMLFOLDER + "*.gml")]
    for gmlfile in gmlfiles:
        out.info_file('convert gmlfile to geojson', gmlfile)


        df = geopandas.read_file(gmlfile)
        df = df.to_crs(epsg=4326)
        
        geojsonfile = GEOJSONFOLDER + os.path.splitext(os.path.basename(gmlfile))[0] + '.geojson'
        poly = df.to_file(geojsonfile, driver='GeoJSON')


        out.info_file('output geojsonfile', geojsonfile)


def add_javascript(m, javascript):


    map_id = m.get_name()

    my_js = javascript.format(map_id)

    e = Element(my_js)
    
    
    html = m.get_root()
    html.script.get_root().render()
    html.script._children[e.get_name()] = e

    return(m)



def draw_coordinates(f, geojsonfiles='', tiles='openstreetmap', allow_change = True, option='all'):
    
    out.info_file('draw coordinates on map', f)



    survey = pd.read_csv(f, delimiter=';',encoding = "ISO-8859-1", keep_default_na=False)
    
    survey = survey.applymap(str)
    survey = survey.applymap(remove_first_quote)

    if 'Street' in survey.columns:
        survey['adres_map'] = survey['Street'] + ' ' + survey['Nr'] + ' ' + survey['Suffix'] 
    if 'Straat' in survey.columns:
        survey['adres_map'] = survey['Straat'] + ' ' + survey['Huisnummer'] + ' ' + survey['Huisnummer Toevoeging']

    if 'Blok' not in survey.columns:
        survey['Blok'] = ''


    if 'Nature' in survey.columns:
        df_lu = survey[survey['Nature'] == 'LU'].groupby(['LAM MK']).size().reset_index(name='LU')
        df_bu = survey[survey['Nature'] == 'BU'].groupby(['LAM MK']).size().reset_index(name='BU')
        df_su = survey[survey['Nature'] == 'SU'].groupby(['LAM MK']).size().reset_index(name='SU')
        df_totaal = survey[survey['Nature'] != ''].groupby(['LAM MK']).size().reset_index(name='TOTAAL')
 
        survey = df_lu.merge(survey, how='right')
        out.columnToInt(survey,'LU')

        survey = df_bu.merge(survey, how='right')
        out.columnToInt(survey,'BU')

        survey = df_su.merge(survey, how='right')
        out.columnToInt(survey,'SU')

        survey = df_totaal.merge(survey, how='right')
        out.columnToInt(survey,'TOTAAL')
        
 
        survey['BT'] = np.where( survey.BU + survey.LU > 1, 'MDU','SDU')
    
    
        survey = survey.drop_duplicates(subset='planrrr_bid', keep='first')


    survey['xPos'] = survey['xPos'].str.replace(',','.').astype(float)
    survey['yPos'] = survey['yPos'].str.replace(',','.').astype(float)


    gdf_survey = geopandas.GeoDataFrame(survey, geometry=geopandas.points_from_xy(survey.xPos, survey.yPos))
    gdf_survey.crs = {'init' :'epsg:31370'}
    gdf_survey = gdf_survey.to_crs(epsg=4326)
    survey['lat'] = gdf_survey['geometry'].x
    survey['lon'] = gdf_survey['geometry'].y
    
    lat_start = 51.26
    lon_start = 4.4
    if survey['lat'][0] > 0:
        lat_start = survey['lat'][0]
    if survey['lon'][0] > 0:
        lon_start = survey['lon'][0]




    feature_group_nb        = folium.map.FeatureGroup(name='New Builings')
    feature_group_mon       = folium.map.FeatureGroup(name='Monuments')
    feature_group_all       = folium.map.FeatureGroup(name='Street Survey')
    feature_group_quadrants = folium.map.FeatureGroup(name='Site Survey')
    
    
    for index, row in survey.iterrows():
        icon_color = 'orange'
        marker_icon = 'home'
        if 'Wall Mount' in survey.columns:
            if row['Wall Mount'] == 'N':
                icon_color = 'red'
            if row['Wall Mount'] == 'Y':
                icon_color = 'green'
    
        lu_info = ''
        image_url = ''
        buildingtype = ''
        if 'LU' in survey.columns:
            lu_info = 'LU&emsp;&emsp;' + str(row['LU']) + '<br>\
                    BU&emsp;&emsp;' + str(row['BU']) + '<br>\
                    SU&emsp;&emsp;' + str(row['SU']) + '<br><br>\
                    Floors&nbsp;&nbsp;'         + str(row['Number Floors']) + '<br>\
                    BT&emsp;&emsp;' + row['BT'] + '<br>'
            
            if row['Blok'] != '':
                    lu_info = lu_info + '<br>Blok&nbsp;&nbsp;&nbsp;&nbsp;' + str(row['Blok']) + '<br><br>'

            if row['VC Method']:
                    lu_info = lu_info + 'Quadr&nbsp;&nbsp;' + str(row['VC Method']) + '<br>'
                    
                    if row['VC Method'][:1] == 'D':
                        image_url = 'map/D.png'
                    if row['VC Method'][:1] == 'C':
                        image_url = 'map/C.png'
                    if row['VC Method'][:1] == 'A':
                        image_url = 'map/A.png'
                    if row['VC Method'][:1] == 'X':
                        image_url = 'map/X.png'
                    if row['VC Method'] == 'XA':
                        image_url = 'map/XA.png'
                    if row['VC Method'] == 'XC':
                        image_url = 'map/XC.png'
                        
            buildingtype = row['BT']               
            if buildingtype == 'MDU':
                marker_icon = 'building'


            if int(row['Number Floors']) > 5:
                marker_icon = 'hotel'


        marker_text = "<b>" + str(row['adres_map']) + "</b><br><br>" + lu_info  + "<br>\
                   <a target='_blank' href='https://www.google.be/maps/place/" + row['adres_map'] + "/@" + str(row['lat']) + "," + str(row['lon']) + "'>Google Maps</a>"
        
       
        if 'SS Reason' in survey.columns:
            if row['SS Reason'] == 'MON':
                marker_icon = 'landmark'
                popup_mon = folium.Popup(marker_text, max_width=330)
                feature_group_mon.add_child(folium.Marker([row['lon'], row['lat']], popup=popup_mon, icon=folium.Icon(color=icon_color, icon = marker_icon, prefix='fa')))
      
        if buildingtype == 'MDU':
            popup_mdu = folium.Popup(marker_text, max_width=330)
            feature_group_quadrants.add_child(folium.CircleMarker([row['lon']+0.00000, row['lat']], radius= 11, color=icon_color, fill_color=icon_color, popup=popup_mdu))
        if buildingtype == 'SDU':
            popup_sdu = folium.Popup(marker_text, max_width=330)
            feature_group_quadrants.add_child(folium.CircleMarker([row['lon']+0.00000, row['lat']], radius= 4, color=icon_color, fill_color=icon_color, popup=popup_sdu))

        if image_url:
            icon = folium.features.CustomIcon(icon_image=image_url ,icon_size=13)
            feature_group_quadrants.add_child(folium.Marker([row['lon']+0.00000, row['lat']], icon=icon))



        check_column = ''
        if 'planrrr_bid' in survey.columns:
            check_column = 'planrrr_bid'
         
        if 'Opdrachtnummer' in survey.columns:
            check_column = 'Opdrachtnummer'
       
        if check_column:
            if row[check_column][:2] == 'NB':
                marker_icon = 'simplybuilt'
                
                if allow_change == True:
                    marker_text  = marker_text + "<br><br><a href='#' onclick='setMarkerAdres(" + '"' + row['adres_map'] + '","' + row[check_column] + '"' + ");'>Change Coords</a>"

  #              popup = folium.Popup(marker_text, max_width=300)
                feature_group_nb.add_child(folium.Marker([row['lon'], row['lat']], popup=marker_text, icon=folium.Icon(color=icon_color, icon = marker_icon, prefix='fa')))
                
        
          
       # marker_icon = 'building'
        popup_all = folium.Popup(marker_text, max_width=330)
        feature_group_all.add_child(folium.Marker([row['lon'], row['lat']], popup=popup_all, icon=folium.Icon(color=icon_color, icon = marker_icon, prefix='fa')))
        
    thefile = open(f, "r")
    str_f = thefile.read()
    str_f = str_f.replace('\n','\\n')
    str_filename = os.path.basename(f)
    
    javascript = """

    //    http://zoologie.umons.ac.be/tc/algorithms.aspx#c2

        function convertBelgianDatum(Lat,Lng){{
		var Haut = 0;      
		var LatBel; var LngBel;
		var DLat; var DLng;
		var Rm; var Rn; 
		var LWb; var LWe2;
		var SinLat; var SinLng;
		var CoSinLat; var CoSinLng;
		var Adb;

		var dx = 125.8;
		var dy = -79.9;
		var dz = 100.5;
		var da = 251.0;
		var df = 0.000014192702;

		var LWf = 1 / 297;
		var LWa = 6378388;
		LWb = (1 - LWf) * LWa;
		LWe2 = (2 * LWf) - (LWf * LWf);
		Adb = 1 / (1 - LWf);

		Lat = (Math.PI / 180) * Lat;
		Lng = (Math.PI / 180) * Lng;

		SinLat = Math.sin(Lat);
		SinLng = Math.sin(Lng);
		CoSinLat = Math.cos(Lat);
		CoSinLng = Math.cos(Lng);

	 
		Rn = LWa / Math.sqrt(1 - LWe2 * SinLat * SinLat);
		Rm = LWa * (1 - LWe2) / (1 - LWe2 * Lat * Lat) ^ 1.5;
		 
		DLat = -dx * SinLat * CoSinLng - dy * SinLat * SinLng + dz * CoSinLat;
		DLat = DLat + da * (Rn * LWe2 * SinLat * CoSinLat) / LWa;
		DLat = DLat + df * (Rm * Adb + Rn / Adb) * SinLat * CoSinLat;
		DLat = DLat / (Rm + Haut);
		 
		DLng = (-dx * SinLng + dy * CoSinLng) / ((Rn + Haut) * CoSinLat);

		 
		LatBel = ((Lat + DLat) * 180) / Math.PI;
		LngBel = ((Lng + DLng) * 180) / Math.PI;

		return Array(LatBel, LngBel);
	}}

	

        function convertxy(lat,lng){{
		dat = convertBelgianDatum(lat,lng);
		lat = dat[0]; 
		lng = dat[1];

		var LongRef = 0.076042943;


		var bLamb = 6378388 * (1 - (1 / 297));
   		var aCarre = Math.pow(6378388,2);
   		var eCarre = (aCarre - Math.pow(bLamb,2)) / aCarre;
   		var KLamb = 11565915.812935;
		var nLamb = 0.7716421928;
 
   		var eLamb = Math.sqrt(eCarre);
   		var eSur2 = eLamb / 2;
 
		lat = (Math.PI / 180) * lat;
   		lng = (Math.PI / 180) * lng;

		
 
   		var eSinLatitude = eLamb * Math.sin(lat);
   		var TanZDemi = ( Math.tan((Math.PI / 4) - (lat / 2)) ) * ( Math.pow( ((1 + eSinLatitude) / (1 - eSinLatitude)), eSur2) );


   		var RLamb = KLamb * (Math.pow(TanZDemi, nLamb));
 
   		var Teta = nLamb * (lng - LongRef);
		 
   		 
		var CX = 150000 + 0.01256 + RLamb * Math.sin(Teta - 0.000142043);
   		var CY = 5400000 + 88.4378 - RLamb * Math.cos(Teta - 0.000142043);            
                
                CX = CX.toFixed(4);
                CY = CY.toFixed(4);

            	return Array(CX, CY);

        }};

        var mapid = document.getElementsByClassName('folium-map')[0].id;
        var g_adres = '';
        var g_key = '';
        var g_file = ' """ + f + """ ';
        var g_str_file = ' """ + str_f + """ ';
        var g_str_filename = ' """ + str_filename + """ ';
        
        function setMarkerAdres(adres, key){{
            alert("Set marker on new location for\\n\\n" + key + "\\n" + adres);
            g_adres = adres;
            g_key = key;
        }};
        
        
        
        function saveData(data, fileName) {{
//            alert(data);
            var a = document.createElement('a');
            document.body.appendChild(a);
            a.style = 'display: none';

            var json = JSON.stringify(data),
            blob = new Blob([data], {{type: 'text/plain;charset=utf-8'}}),

            url = window.URL.createObjectURL(blob);
            a.href = url;

            a.download = fileName;

            a.click();

            window.URL.revokeObjectURL(url);

        }}


        function addToCsv(x,y){{
            if(g_adres !== ''){{
                                
                x = x.toString().replace('.',',');
                y = y.toString().replace('.',',');
                
                row = g_str_file.split('\\n');

                console.log(row);

                header = row[0].split(';');
                var index_of_xPos = 0;
                var index_of_yPos = 0;

                for (index = 0; index < header.length; index++) {{
                    if (header[index] == 'xPos'){{
                        index_of_xPos = index;
                    }}
                    if (header[index] == 'yPos'){{
                        index_of_yPos = index;
                    }}
                }} 
                console.log('index of xPos:' + index_of_xPos);
                console.log('index of yPos:' + index_of_yPos);
                
                var index_of_key = 0

                for (index = 0; index < row.length; index++) {{
                    if (row[index].includes(g_key)){{
                        index_of_key = index;
                    }}
                }} 
                console.log('index of key:' + index_of_key);
                console.log(row[index_of_key]);

                row_to_change = row[index_of_key].split(';');
                row_to_change[index_of_xPos] = x;
                row_to_change[index_of_yPos] = y;
                
                row_changed = '';
                for (index = 0; index < row_to_change.length; index++) {{
                    row_changed = row_changed + row_to_change[index] + ';';
                }} 
                row_changed = row_changed.slice(0,-1);
                
                console.log('new row:' + row_changed);
                
                row[index_of_key] = row_changed;
                
                var csvdata = '';
                for (index = 0; index < row.length; index++) {{
                    csvdata = csvdata + row[index] + '\\n'
                }} 
                

                alert('Change xy for : ' + g_key + '\\
                   \\n' + g_adres + ' \\
                   \\n\\nx: ' + x + '\\ny: ' + y + '\\
                   \\n\\n' + row_changed 
                   );
                


           //     saveData(csvdata,g_str_filename);                
                g_str_file = csvdata;

            }}else{{
                alert('no key found!!');
            }}
        }};
 
        function saveToCsv(){{
            alert('data to write: \\n' + g_str_file);        
            saveData(g_str_file,g_str_filename);                
           
        }};

        function newMarker(e){{
            
	    var new_mark = L.marker().setLatLng(e.latlng).addTo(window[mapid]);
	    new_mark.on('dblclick', function(e){{ window[mapid].removeLayer(e.target)}})

            var lat = e.latlng.lat.toFixed(4);
            var lng = e.latlng.lng.toFixed(4);
            var xy = [];
            xy = convertxy(lat, lng);
            
            var adres = g_adres;

            new_mark.bindPopup("<b>"+ adres + "</b><br> \\
                    <u>" + g_key + "</u><BR><BR> \\
                    <i>lat, lng:</i> :: " + lat + ", " + lng + "<BR><BR> \\
                    <i>x, y:</i> :: " + xy[0] + ", " + xy[1] + "<BR><BR> \\
                    <a target='_blank' href='https://www.google.be/maps/place/" + g_adres + "/@" + lat + "," + lng + "'>Google Maps</a><hr> \\
                    <a href='#' onclick='addToCsv(" + '"' + xy[0] + '","' + xy[1] + '"' + ");'>Change</a>&nbsp;&nbsp \\
                    <a href='#' onclick='saveToCsv();'>Save to csv</a> \\
                    ");
              }};
        
        window[mapid].on('click', newMarker);
        
                 """
    
    javascript_add_css = """
        function addCss(fileName) {{

            var head = document.head;
            var link = document.createElement('link');

            link.type = 'text/css';
            link.rel = 'stylesheet';
            link.href = fileName;

            head.appendChild(link);
        }}
        addCss('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/all.min.css');
        addCss('https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css');
                        """
    
    m = folium.Map(location=[lon_start, lat_start], tiles=tiles, zoom_start=15)


    if geojsonfiles == '':
        geojsonfiles = [f for f in glob.glob(GEOJSONFOLDER + "*.geojson")]
    
    for geojsonfile in geojsonfiles:
        layername = os.path.splitext(os.path.basename(geojsonfile))[0]
        folium.GeoJson(geojsonfile,name=layername).add_to(m)
    

    out.info_file('Draw polyglons on map', geojsonfiles)

   

    if allow_change == True:
        out.info_file('Add javascript for coordinate adjustment', f)
        add_javascript(m,javascript)

    add_javascript(m,javascript_add_css)

    
    
    if option == 'all':
        m.add_child(feature_group_nb)
    #    m.add_child(feature_group_mon)
        m.add_child(feature_group_all)
        m.add_child(feature_group_quadrants)

    if option == 'sts':
        m.add_child(feature_group_nb)
        m.add_child(feature_group_all)

    if option == 'ssv':
        m.add_child(feature_group_nb)
        m.add_child(feature_group_mon)
        m.add_child(feature_group_quadrants)


    m.add_child(folium.map.LayerControl())


    html = HTMLFOLDER + os.path.splitext(os.path.basename(f))[0] + "_" + option + '.html'



    out.info_file('Save html file', html)

     
    m.save(html)


    webbrowser.open('file://' + os.path.realpath(html))


#draw_coordinates(TEST1)
#draw_coordinates(TEST2, allow_change=False)
#draw_coordinates(TEST2, allow_change=False,option='sts')
#draw_coordinates(TEST2, allow_change=False,option='ssv')
#draw_coordinates(TEST_BLOK, allow_change=False,option='ssv')
#draw_coordinates(TEST3, allow_change=False,option='ssv')

